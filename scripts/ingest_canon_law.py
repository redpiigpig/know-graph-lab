"""Ingest 教會法規 → canon_law_{documents,versions,sections}.

DB-backed, mirrors scripts/ingest_gnostic.py. la↔en↔zh align by order_index
(= 條號/段號). See .claude/skills/scripture-canon/SKILL.md §3.

Pure parse/slug/align logic lives in scripts/canon_law.py (tested). This driver
does I/O: fetch vatican.va, split, stamp book labels, upsert.

Sources:
  - CIC en/la : vatican.va/archive/cod-iuris-canonici/{eng,lat}/  (clean HTML)
  - CIC zh    : vatican.va/chinese/cic/  (PDF w/ broken font → Gemini Vision OCR,
                separate batch — see ingest_canon_law_zh_ocr in SKILL)

Examples:
  python -X utf8 scripts/ingest_canon_law.py --seed-docs
  python -X utf8 scripts/ingest_canon_law.py --doc cic-1983 --lang en
  python -X utf8 scripts/ingest_canon_law.py --doc cic-1983 --lang la
"""
from __future__ import annotations
import os, sys, json, re, argparse, time
from pathlib import Path

import requests
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))
import canon_law as cl  # noqa: E402

load_dotenv()
SUPABASE_URL = os.environ["SUPABASE_URL"]
SERVICE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_REST = {"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}",
          "Content-Type": "application/json", "Prefer": "return=minimal"}

UA = {"User-Agent": "Mozilla/5.0 (KGL canon-law ingest)"}

# vatican.va archive bases for the Latin / English Code of Canon Law.
#   en = many per-canon-range pages (…cic_lib4-cann834-878_en.html), links carry
#        #fragment anchors → strip them; la = one page per book (cic_liberIV_la.html).
CIC_INDEX = {
    "en": "https://www.vatican.va/archive/cod-iuris-canonici/cic_index_en.html",
    "la": "https://www.vatican.va/archive/cod-iuris-canonici/cic_index_la.html",
}
# Capture the FULL relative href (incl. eng/documents/ or latin/documents/),
# tolerating a trailing #fragment anchor.
CIC_PAGE_RE = {
    "en": re.compile(r'href="([^"]*?cic_lib\d+-cann[\d-]+_en\.html)(?:#[^"]*)?"', re.I),
    "la": re.compile(r'href="([^"]*?cic_liber[IVXLC]+_la\.html)(?:#[^"]*)?"', re.I),
}

# Footer / chrome lines that ride after the last canon on a vatican.va page.
_BOILER = re.compile(r"^(©|copyright|concordat|\*{2,}|back to|index|top$)", re.I)


def fetch(url: str, retries: int = 4) -> str:
    last = None
    for i in range(retries):
        try:
            r = requests.get(url, timeout=60, headers=UA)
            r.raise_for_status()
            r.encoding = r.apparent_encoding or "utf-8"
            return r.text
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"fetch failed {url}: {last}")


def html_to_lines(html: str) -> list[str]:
    """vatican.va archive page → text lines (one per block), boilerplate dropped."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    for bad in soup(["script", "style"]):
        bad.decompose()
    body = soup.body or soup
    text = body.get_text("\n")
    out = []
    for raw in text.split("\n"):
        s = " ".join(raw.split())
        if not s or _BOILER.match(s):
            continue
        out.append(s)
    return out


# ── Upsert helpers (mirror ingest_gnostic) ───────────────────────────────────
def upsert_document(meta: dict) -> None:
    requests.post(f"{SUPABASE_URL}/rest/v1/canon_law_documents",
                  headers={**H_REST, "Prefer": "resolution=merge-duplicates"},
                  data=json.dumps([meta]), timeout=60).raise_for_status()


def replace_sections(slug: str, version: str, rows: list[dict]) -> int:
    requests.delete(
        f"{SUPABASE_URL}/rest/v1/canon_law_sections?doc_slug=eq.{slug}&version_code=eq.{version}",
        headers=H_REST, timeout=60)
    BATCH = 200
    for i in range(0, len(rows), BATCH):
        batch = rows[i:i + BATCH]
        for attempt in range(3):
            r = requests.post(f"{SUPABASE_URL}/rest/v1/canon_law_sections",
                              headers=H_REST, data=json.dumps(batch), timeout=180)
            if r.status_code in (200, 201, 204):
                break
            if r.status_code >= 500 and attempt < 2:
                time.sleep(2 * (attempt + 1)); continue
            print(f"  ERROR batch {i}: {r.status_code} {r.text[:300]}"); r.raise_for_status()
    return len(rows)


# ── Document seeding ─────────────────────────────────────────────────────────
def seed_documents() -> None:
    for c in cl.CORPORA:
        upsert_document({
            "slug": c["slug"], "title_zh": c["title_zh"], "title_zh_short": c.get("title_zh_short"),
            "title_en": c["title_en"], "title_lat": c.get("title_lat") or None,
            "tradition": c["tradition"], "corpus": c["corpus"],
            "structure_note": c.get("structure_note"), "promulgated_year": c.get("promulgated_year"),
            "display_order": c["display_order"],
        })
        print(f"  ✓ doc {c['slug']}  ({c['title_zh']})", flush=True)


# ── CIC en/la ingest ─────────────────────────────────────────────────────────
def discover_cic_pages(lang: str) -> list[str]:
    idx = fetch(CIC_INDEX[lang])
    seen, out = set(), []
    for href in CIC_PAGE_RE[lang].findall(idx):
        url = requests.compat.urljoin(CIC_INDEX[lang], href)
        if url not in seen:
            seen.add(url); out.append(url)
    return out


def ingest_cic(lang: str, *, limit_pages: int | None = None, dry_run: bool = False) -> None:
    assert lang in ("en", "la")
    version = lang  # version codes: 'en' / 'la'
    pages = discover_cic_pages(lang)
    if limit_pages:
        pages = pages[:limit_pages]
    print(f"CIC {lang}: {len(pages)} pages", flush=True)
    all_lines: list[str] = []
    for i, url in enumerate(pages):
        try:
            all_lines.extend(html_to_lines(fetch(url)))
            print(f"  · page {i + 1}/{len(pages)} ({url.rsplit('/', 1)[-1]})", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"  ✗ page {url}: {e}", flush=True)
        time.sleep(0.2)
    secs = cl.split_into_sections(all_lines, lang)
    # dedupe stray same-canon rows (a body line starting with another canon's
    # cross-reference) — keep the longest text per order_index.
    best: dict[int, dict] = {}
    for s in secs:
        cur = best.get(s["order_index"])
        if cur is None or len(s["text"]) > len(cur["text"]):
            best[s["order_index"]] = s
    secs = [best[k] for k in sorted(best)]
    # stamp clean Chinese 卷 labels by canon number (overrides any parsed heading)
    for s in secs:
        s["book_label"] = cl.cic_book_for(s["order_index"]) or s.get("book_label")
    print(f"  parsed {len(secs)} canons (order {secs[0]['order_index']}..{secs[-1]['order_index']})" if secs else "  no canons", flush=True)
    if dry_run:
        for s in secs[:3]:
            print(f"    [{s['order_index']}] {s['label']} | {s['book_label']} | {s['text'][:60]}…")
        return
    rows = [{"doc_slug": "cic-1983", "version_code": version, "order_index": s["order_index"],
             "section_label": s["label"], "book_label": s["book_label"],
             "chapter_label": s["chapter_label"], "is_heading": False,
             "text": s["text"], "char_count": len(s["text"])} for s in secs]
    n = replace_sections("cic-1983", version, rows)
    print(f"  ✓ upserted {n} {version} canon rows", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-docs", action="store_true", help="upsert canon_law_documents from CORPORA")
    ap.add_argument("--doc", help="document slug, e.g. cic-1983")
    ap.add_argument("--lang", help="version code: en / la / zh")
    ap.add_argument("--limit-pages", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.seed_docs:
        print("Seeding documents…", flush=True)
        seed_documents()

    if args.doc and args.lang:
        if args.doc == "cic-1983" and args.lang in ("en", "la"):
            ingest_cic(args.lang, limit_pages=args.limit_pages, dry_run=args.dry_run)
        elif args.lang == "zh":
            sys.exit("zh ingest = Gemini Vision OCR batch (vatican.va PDFs have broken font); not yet wired here")
        else:
            sys.exit(f"no ingest path for doc={args.doc} lang={args.lang} yet")

    if not args.seed_docs and not args.doc:
        ap.print_help()


if __name__ == "__main__":
    main()
