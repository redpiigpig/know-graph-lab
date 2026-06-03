"""Ingest a 研究回顧 (literature review) → writing_projects + lit_review_{entries,sections}.

Two stages (see .claude/skills/research-review/SKILL.md):

  --seed            parse the綜述 markdown → upsert a kind='paper' writing_project
                    + upsert every bibliography entry (metadata + abstract).
  --fetch-fulltext  for openly-available NON-Chinese entries, fetch the full text
                    (PDF via PyMuPDF / HTML), segment into paragraphs, translate
                    each into 繁中 (ebook-translate engine), assert 1:1 alignment,
                    upsert 原文(orig)/中譯(zh) sections. Overnight, --resume-able.

Chinese-language entries get NO sections (中譯欄等同原文，書目層即可). Copyright-only
works (no open full text) are marked fulltext_status='unavailable'.

Examples:
  # seed the八敬法 review under a new 'bajingfa' paper project (paper c1)
  python -X utf8 scripts/ingest_lit_review.py --seed \
      --report scripts/data/lit_review_eight_garudhammas.md \
      --project bajingfa --paper-ref c1 \
      --title "昭慧法師的戒律學思想與實踐：以性別議題為核心" \
      --subtitle "改寫為期刊論文 · 八敬法研究回顧"

  # overnight: fetch + translate every fetchable full text, resume-able
  python -X utf8 scripts/ingest_lit_review.py --fetch-fulltext --project bajingfa --resume --engine gemini

  # pilot one entry, capped at 6 paragraphs
  python -X utf8 scripts/ingest_lit_review.py --fetch-fulltext --project bajingfa \
      --only analayo-2015 --limit-paras 6 --engine gemini
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lit_review as lr  # noqa: E402

load_dotenv()
SUPABASE_URL = os.environ["SUPABASE_URL"]
SERVICE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_REST = {"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}",
          "Content-Type": "application/json"}

UA = {"User-Agent": "Mozilla/5.0 (KGL lit-review ingest)"}

# Academic translator prompt — overrides the ebook-translate default per paragraph.
LR_PROMPT_TMPL = """你是佛教學／宗教學學術論文的專業譯者。
把以下學術文字**逐字**翻成**繁體中文**（台灣學術用語、中間點用「‧」）。

要求：
1. 忠實、精確、學術；保留論證結構與術語。
2. 專有名詞用通行中譯，首次出現可括註原文（例：八敬法（aṭṭhagarudhammā）、比丘尼（bhikkhunī）、大愛道（Mahāpajāpatī Gotamī）、《小品》（Cullavagga））。巴利／梵文術語保留原拼寫於括註內。
3. 引用的經典名、人名依學界慣例；不確定者保留原文。
4. 只輸出這一段的繁體中文翻譯，不要前言、編號或說明。

{source}"""

# Entries with no openly-available machine-readable full text (copyright books /
# paywalled journals): seeded as 'unavailable' so the UI is honest and the fetch
# stage skips them. Matched by ref_key prefix.
UNAVAILABLE_PREFIXES = (
    "karma-lekshe-tsomo-1988",          # Snow Lion book (copyright)
    "thea-mohr-jampa-tsedroen",         # Wisdom Publications book (copyright)
    "ann-heirman-tzu-lung-chiu",        # Buddhist Studies Review (paywalled)
)
MIN_FULLTEXT_PARAS = 6   # fewer than this ⇒ likely a homepage/paywall, not the article
CONSEC_FAIL_ABORT = 4


# ── REST helpers ──────────────────────────────────────────────────────────────
def rest_upsert(table: str, rows: list[dict], on_conflict: str) -> None:
    if not rows:
        return
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}?on_conflict={on_conflict}",
        headers={**H_REST, "Prefer": "resolution=merge-duplicates,return=minimal"},
        data=json.dumps(rows), timeout=120)
    if r.status_code not in (200, 201, 204):
        print(f"  ERROR upsert {table}: {r.status_code} {r.text[:300]}")
        r.raise_for_status()


def rest_get(table: str, params: str) -> list[dict]:
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{table}?{params}", headers=H_REST, timeout=60)
    r.raise_for_status()
    return r.json()


def rest_patch(table: str, params: str, body: dict) -> None:
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/{table}?{params}",
                       headers={**H_REST, "Prefer": "return=minimal"},
                       data=json.dumps(body), timeout=60)
    if r.status_code not in (200, 204):
        print(f"  ERROR patch {table}: {r.status_code} {r.text[:300]}")
        r.raise_for_status()


# ── Seed ──────────────────────────────────────────────────────────────────────
def seed(report_path: str, project_slug: str, paper_ref: str | None,
         title: str, subtitle: str | None, description: str | None) -> None:
    md = Path(report_path).read_text(encoding="utf-8")
    parsed = lr.parse_review_report(md)
    entries = parsed["entries"]
    print(f"parsed {len(entries)} entries, {len(parsed['gaps'])} gaps", flush=True)

    # 1) writing_projects (kind='paper')
    rest_upsert("writing_projects", [{
        "slug": project_slug,
        "title": title,
        "subtitle": subtitle,
        "description": description or parsed["summary"],
        "emoji": "📄",
        "color": "teal",
        "status": "改寫為期刊論文中",
        "kind": "paper",
        "paper_ref": paper_ref,
    }], on_conflict="slug")
    print(f"✓ project '{project_slug}' (kind=paper, paper_ref={paper_ref})", flush=True)

    # 2) lit_review_entries
    rows = []
    for i, e in enumerate(entries):
        status = "pending"
        if e["language"] == "zh":
            status = "unavailable"   # zh 文獻不建逐段中譯（書目層即可）
        elif any(e["ref_key"].startswith(p) for p in UNAVAILABLE_PREFIXES):
            status = "unavailable"
        url = e["fulltext_url"]
        if url and ("......" in url or "…" in url):
            url = None
        rows.append({
            "project_slug": project_slug,
            "ref_key": e["ref_key"],
            "authors": e["authors"],
            "year": e["year"],
            "title": e["title"],
            "venue": e["venue"] or None,
            "language": e["language"],
            "theme": e["theme"],
            "dimension": e["dimension"],
            "stance": e["stance"],
            "abstract_zh": e["abstract"] or None,
            "fulltext_url": url,
            "fulltext_status": status,
            "display_order": i,
        })
    rest_upsert("lit_review_entries", rows, on_conflict="project_slug,ref_key")
    print(f"✓ upserted {len(rows)} entries "
          f"({sum(1 for r in rows if r['fulltext_status'] == 'pending')} pending full text)", flush=True)


# ── Fetch + translate full text ───────────────────────────────────────────────
def make_engine(engine: str):
    import translate_ebook_to_zh as te
    te.PROMPT_TMPL = LR_PROMPT_TMPL
    fn = {
        "gemini": te.gemini_with_nvidia_fallback,
        "nvidia": te.nvidia_translate,
        "sonnet": te.sonnet_translate,
    }[engine]
    return te, fn


def fetch_url(url: str) -> tuple[str, str]:
    """→ ('pdf'|'html', text). PDF parsed with PyMuPDF (page text joined by blank lines)."""
    r = requests.get(url, timeout=120, headers=UA)
    r.raise_for_status()
    ctype = r.headers.get("content-type", "").lower()
    if "pdf" in ctype or url.lower().split("?")[0].endswith(".pdf"):
        import fitz  # PyMuPDF
        doc = fitz.open(stream=r.content, filetype="pdf")
        text = "\n\n".join(page.get_text() for page in doc)
        doc.close()
        return "pdf", text
    r.encoding = r.apparent_encoding or "utf-8"
    return "html", r.text


def translate_paragraphs(paras: list[str], te, fn, limit: int | None, pace: float) -> list[str]:
    todo = paras[:limit] if limit else paras
    out: list[str] = []
    for i, p in enumerate(todo):
        if pace and i > 0:
            time.sleep(pace)
        pieces = te.split_oversized(p)
        zh = "\n\n".join(fn(piece) for piece in pieces)
        out.append(zh.strip())
        print(f"      · para {i + 1}/{len(todo)} ({len(p)}→{len(zh)})", flush=True)
    return out


def upsert_sections(entry_id: int, orig: list[str], zh: list[str]) -> None:
    requests.delete(f"{SUPABASE_URL}/rest/v1/lit_review_sections?entry_id=eq.{entry_id}",
                    headers=H_REST, timeout=60)
    rows = []
    for i, (o, z) in enumerate(zip(orig, zh)):
        rows.append({"entry_id": entry_id, "version_code": "orig", "order_index": i, "text": o, "char_count": len(o)})
        rows.append({"entry_id": entry_id, "version_code": "zh", "order_index": i, "text": z, "char_count": len(z)})
    BATCH = 100
    for i in range(0, len(rows), BATCH):
        rest_upsert("lit_review_sections", rows[i:i + BATCH], on_conflict="entry_id,version_code,order_index")


def fetch_fulltext(project_slug: str, engine: str, resume: bool,
                   only: str | None, limit_paras: int | None,
                   limit_entries: int | None, pace: float, dry_run: bool) -> None:
    sel = "id,ref_key,title,language,fulltext_url,fulltext_status"
    entries = rest_get("lit_review_entries",
                       f"project_slug=eq.{project_slug}&select={sel}&order=display_order")
    todo = []
    for e in entries:
        if only and only not in e["ref_key"]:
            continue
        if e["language"] == "zh":
            continue
        if e["fulltext_status"] == "unavailable":
            continue
        if not e["fulltext_url"]:
            print(f"  ⏭ no URL: {e['ref_key']}", flush=True)
            continue
        # Skip bare-domain / homepage URLs — fetching those would translate site
        # chrome, not the article. Keep them as reference links; resolve the real
        # article URL (WebSearch) before they become fetchable.
        from urllib.parse import urlparse
        path = urlparse(e["fulltext_url"]).path.strip("/")
        if not path:
            print(f"  ⏭ homepage URL (resolve article first): {e['ref_key']}", flush=True)
            continue
        if resume and e["fulltext_status"] == "translated":
            continue
        todo.append(e)
    if limit_entries:
        todo = todo[:limit_entries]
    print(f"fetch-fulltext: {len(todo)} entries to process", flush=True)

    te, fn = (None, None) if dry_run else make_engine(engine)
    consec_fail = 0
    for e in todo:
        print(f"  → {e['ref_key']}  ({e['fulltext_url']})", flush=True)
        try:
            kind, text = fetch_url(e["fulltext_url"])
            paras = (lr.extract_paragraphs_from_text(text) if kind == "pdf"
                     else lr.extract_paragraphs_from_html(text))
            print(f"    {kind}: {len(paras)} paragraphs", flush=True)
            if len(paras) < MIN_FULLTEXT_PARAS:
                print("    ⚠ too few paragraphs (homepage/paywall?) — leave pending, fix URL", flush=True)
                consec_fail = 0
                continue
            if dry_run:
                continue
            orig = paras[:limit_paras] if limit_paras else paras
            zh = translate_paragraphs(orig, te, fn, limit_paras, pace)
            lr.assert_aligned(orig, zh)
            upsert_sections(e["id"], orig, zh)
            rest_patch("lit_review_entries", f"id=eq.{e['id']}", {"fulltext_status": "translated"})
            print(f"    ✓ {len(zh)} paras × 2 versions upserted", flush=True)
            consec_fail = 0
        except Exception as exc:  # noqa: BLE001
            consec_fail += 1
            print(f"    ✗ FAIL: {exc}  (consec={consec_fail})", flush=True)
            if consec_fail >= CONSEC_FAIL_ABORT:
                raise SystemExit(f"aborting: {CONSEC_FAIL_ABORT} consecutive failures "
                                 "(quota/network) — re-run with --resume later")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", action="store_true")
    ap.add_argument("--fetch-fulltext", action="store_true")
    ap.add_argument("--report")
    ap.add_argument("--project", required=True)
    ap.add_argument("--paper-ref", default=None)
    ap.add_argument("--title", default="")
    ap.add_argument("--subtitle", default=None)
    ap.add_argument("--description", default=None)
    ap.add_argument("--engine", default="gemini", choices=["gemini", "nvidia", "sonnet"])
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--only", default=None, help="ref_key substring filter (fetch one)")
    ap.add_argument("--limit-paras", type=int, default=None)
    ap.add_argument("--limit-entries", type=int, default=None)
    ap.add_argument("--pace", type=float, default=0.0)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.seed:
        if not args.report or not args.title:
            sys.exit("--seed needs --report and --title")
        seed(args.report, args.project, args.paper_ref, args.title, args.subtitle, args.description)
    if args.fetch_fulltext:
        fetch_fulltext(args.project, args.engine, args.resume, args.only,
                       args.limit_paras, args.limit_entries, args.pace, args.dry_run)
    if not args.seed and not args.fetch_fulltext:
        sys.exit("need --seed and/or --fetch-fulltext")


if __name__ == "__main__":
    main()
