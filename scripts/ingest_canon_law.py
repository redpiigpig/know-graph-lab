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


# ── CIC zh: Gemini Vision OCR (vatican.va /chinese/cic/ PDFs have broken font) ─
ZH_CACHE = Path("c:/tmp/canon_law_zh")
CIC_ZH_PROMPT = """這是《天主教法典》(Codex Iuris Canonici, 1983) 官方繁體中文版的一頁掃描。

請抽出**純正文**，整理為單欄繁體中文純文字輸出。規則：
1. 逐條保留條號，格式統一為「第 N 條」（N 用阿拉伯數字），各自獨立成行。
2. 卷／編／題／章標題保留原樣（如「第一卷 總則」「第二編 教會聖統制」「第一章 …」），獨立成行。
3. 條文內的分項「§ 1.」「§ 2.」「1°」「2°」保留。
4. 移除頁首頁尾、頁碼、書名 running header、拉丁對照欄（只要中文）。
5. 斷行的句子接回同一段；不同條之間換行分開。
6. 直接輸出繁體中文純文字，**不要** markdown、不要 ``` 包裝、不要任何說明。

若整頁無正文（封面／空白／純拉丁），輸出單行：# NO_TEXT
"""


def _gemini_ocr_pdf(path: Path, prompt: str, sleep: float = 1.2) -> str:
    """OCR every page of a PDF with Gemini Vision → joined text.

    Page-level cache: each resolved page is written to
    c:/tmp/canon_law_zh/pages/{stem}/p{NNN}.txt immediately, so a multi-page PDF
    accumulates progress across retries even under heavy quota contention.
    Resume skips any page whose cache file already exists. Raises on 2 consecutive
    all-key-429 pages (per OCR 2-strike rule) — partial pages stay cached.
    """
    import fitz
    from google import genai
    from google.genai import types
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ocr_with_gemini import _find_gemini_keys  # type: ignore
    keys = _find_gemini_keys()
    if not keys:
        raise RuntimeError("no GEMINI_API_KEY")
    clients = [genai.Client(api_key=k) for k in keys]  # build once, reuse (avoid "client closed")
    pagedir = ZH_CACHE / "pages" / path.stem
    pagedir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(path))
    n = doc.page_count
    strikes = 0
    for pi in range(n):
        pagefile = pagedir / f"p{pi:03d}.txt"
        if pagefile.exists():  # already resolved on a previous attempt (empty = NO_TEXT)
            continue
        page = doc.load_page(pi)
        longest = max(page.rect.width, page.rect.height)
        pix = page.get_pixmap(matrix=fitz.Matrix(1800 / longest, 1800 / longest), alpha=False)
        png = pix.tobytes("png")
        text, ok, all_429 = "", False, True
        for client in clients:  # rotate keys; a single depleted key (429) just falls through
            try:
                resp = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[types.Part.from_bytes(data=png, mime_type="image/png"), prompt],
                    config=types.GenerateContentConfig(temperature=0.1))
                text = (resp.text or "").strip()
                ok = True; all_429 = False
                break
            except Exception as e:  # noqa: BLE001
                if any(s in str(e) for s in ("429", "RESOURCE_EXHAUSTED", "quota")):
                    continue  # try next key
                all_429 = False
                time.sleep(3)
        # strike only when EVERY key 429'd for this page; 2 consecutive → abort (per OCR rule)
        strikes = strikes + 1 if (not ok and all_429) else 0
        if strikes >= 2:
            doc.close()
            raise RuntimeError("連 2 頁全 key 429 quota，依規範退出")
        if ok:
            clean = "" if text == "# NO_TEXT" else text
            clean = re.sub(r"^```[a-z]*\n", "", clean); clean = re.sub(r"\n```$", "", clean)
            pagefile.write_text(clean.strip(), encoding="utf-8")  # persist immediately
        print(f"    page {pi + 1}/{n}  {len(text)} chars", flush=True)
        time.sleep(sleep)
    doc.close()
    # all pages resolved → assemble from the page cache in order
    parts = [(pagedir / f"p{pi:03d}.txt").read_text(encoding="utf-8") for pi in range(n)]
    return "\n".join(p for p in parts if p)


def ingest_cic_zh(*, resume: bool = True, limit_pdfs: int | None = None) -> None:
    ZH_CACHE.mkdir(parents=True, exist_ok=True)
    pdfs = cl.CIC_ZH_PDFS[:limit_pdfs] if limit_pdfs else cl.CIC_ZH_PDFS
    all_lines: list[str] = []
    for i, base in enumerate(pdfs):
        txt_path = ZH_CACHE / (base.replace(".pdf", ".txt"))
        if resume and txt_path.exists() and txt_path.stat().st_size > 0:
            print(f"  [{i + 1}/{len(pdfs)}] cached {base}", flush=True)
            all_lines.extend(txt_path.read_text(encoding="utf-8").splitlines())
            continue
        pdf_path = ZH_CACHE / base
        if not pdf_path.exists():
            r = requests.get(cl.cic_zh_url(base), headers=UA, timeout=120); r.raise_for_status()
            pdf_path.write_bytes(r.content)
        print(f"  [{i + 1}/{len(pdfs)}] OCR {base} …", flush=True)
        text = _gemini_ocr_pdf(pdf_path, CIC_ZH_PROMPT)
        txt_path.write_text(text, encoding="utf-8")
        all_lines.extend(text.splitlines())
    secs = cl.split_into_sections(all_lines, "zh")
    best: dict[int, dict] = {}
    for s in secs:
        cur = best.get(s["order_index"])
        if cur is None or len(s["text"]) > len(cur["text"]):
            best[s["order_index"]] = s
    secs = [best[k] for k in sorted(best)]
    for s in secs:
        s["book_label"] = cl.cic_book_for(s["order_index"]) or s.get("book_label")
    print(f"  parsed {len(secs)} zh canons" + (f" (order {secs[0]['order_index']}..{secs[-1]['order_index']})" if secs else ""), flush=True)
    rows = [{"doc_slug": "cic-1983", "version_code": "zh", "order_index": s["order_index"],
             "section_label": s["label"], "book_label": s["book_label"],
             "chapter_label": s["chapter_label"], "is_heading": False,
             "text": s["text"], "char_count": len(s["text"])} for s in secs]
    n = replace_sections("cic-1983", "zh", rows)
    print(f"  ✓ upserted {n} zh canon rows", flush=True)


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
        elif args.doc == "cic-1983" and args.lang == "zh":
            ingest_cic_zh(resume=True, limit_pdfs=args.limit_pages)
        else:
            sys.exit(f"no ingest path for doc={args.doc} lang={args.lang} yet")

    if not args.seed_docs and not args.doc:
        ap.print_help()


if __name__ == "__main__":
    main()
