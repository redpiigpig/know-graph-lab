"""Ingest The Gnostic Society Library (gnosis.org) → gnostic_{documents,sections}.

Pipeline (see .claude/skills/gnostic-library/SKILL.md):
  fetch category index → parse_category_index → (dedup) → fetch each doc →
  parse_document → translate each EN paragraph → assert_aligned → upsert.

gnosis.org's HTTPS cert is expired, so we fetch with verify=False (insecure).
English is public-domain (Mead etc.); Chinese is our per-paragraph translation.
EN↔ZH align by order_index (one ZH paragraph per EN paragraph — the gate).

Examples:
  # one document
  python -X utf8 scripts/ingest_gnostic.py --category nag_hammadi \
      --url http://gnosis.org/naghamm/gosthom.html --title "The Gospel of Thomas" --engine gemini
  # whole category (lists docs; --limit-docs to cap; dedup auto for polemics/cac/dss)
  python -X utf8 scripts/ingest_gnostic.py --category hermetica --limit-docs 3 --engine gemini
  # just list a category's docs, translate nothing
  python -X utf8 scripts/ingest_gnostic.py --category nag_hammadi --list
"""
from __future__ import annotations
import os, sys, json, re, argparse, time
from pathlib import Path

import requests
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gnostic_library as gl  # noqa: E402

load_dotenv()
SUPABASE_URL = os.environ["SUPABASE_URL"]
PROJECT_REF = SUPABASE_URL.split("//")[1].split(".")[0]
ACCESS_TOKEN = os.environ["SUPABASE_ACCESS_TOKEN"]
SERVICE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

MGMT_QUERY = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
H_MGMT = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
H_REST = {"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}",
          "Content-Type": "application/json", "Prefer": "return=minimal"}

GNOSTIC_PROMPT_TMPL = """你是諾斯底主義、赫密士、摩尼教等古典宗教文獻的專業譯者。
把以下英文**逐字**翻成**繁體中文**（台灣用語、中間點用「‧」）。

要求：
1. 忠實、典雅、可讀；保留原文語氣與神聖文體。
2. 專有名詞用通行中譯，首次出現可括註英文（例：智慧（Sophia）、造物主（Demiurge）、圓滿境界（Pleroma）、艾翁（Aeon））。
3. 只輸出這一段的繁體中文翻譯，不要前言、編號或說明。

{source}"""


# ── Fetch (insecure — gnosis.org cert expired) ───────────────────────────────
def fetch(url: str, retries: int = 3) -> str:
    last = None
    for i in range(retries):
        try:
            r = requests.get(url, timeout=60, verify=False,
                             headers={"User-Agent": "Mozilla/5.0 (KGL gnostic ingest)"})
            r.raise_for_status()
            r.encoding = r.apparent_encoding or "utf-8"
            return r.text
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"fetch failed {url}: {last}")


# ── Dedup: existing English titles already on the site ───────────────────────
def existing_en_titles() -> list[str]:
    """apocrypha_documents.title_en + gnostic_documents.title_en — the corpus we
    don't want to re-transcribe (per user: skip polemics/cac/dss overlaps)."""
    titles: list[str] = []
    for tbl in ("apocrypha_documents", "gnostic_documents"):
        r = requests.post(MGMT_QUERY, headers=H_MGMT,
                          json={"query": f"SELECT title_en FROM {tbl}"})
        if r.ok:
            titles += [row["title_en"] for row in r.json() if row.get("title_en")]
    return titles


# ── Translate (one call per paragraph → guaranteed 1:1 alignment) ────────────
def make_engine(engine: str):
    import translate_ebook_to_zh as te
    te.PROMPT_TMPL = GNOSTIC_PROMPT_TMPL
    # Haiku 全面停用 (2026-06-03): default chain = Gemini → NVIDIA fallback.
    fn = {
        "gemini": te.gemini_with_nvidia_fallback,
        "nvidia": te.nvidia_translate,
        "sonnet": te.sonnet_translate,
        "haiku": te.gemini_with_nvidia_fallback,  # redirected
    }[engine]
    return te, fn


def translate_paragraphs(paragraphs: list[str], te, engine_fn, limit: int | None = None) -> list[str]:
    todo = paragraphs[:limit] if limit else paragraphs
    out: list[str] = []
    for i, p in enumerate(todo):
        pieces = te.split_oversized(p)
        zh = "\n\n".join(engine_fn(piece) for piece in pieces)
        out.append(zh.strip())
        print(f"    · para {i + 1}/{len(todo)} ({len(p)}→{len(zh)} chars)", flush=True)
    return out


# ── Upsert ───────────────────────────────────────────────────────────────────
def upsert_document(meta: dict) -> None:
    requests.post(f"{SUPABASE_URL}/rest/v1/gnostic_documents",
                  headers={**H_REST, "Prefer": "resolution=merge-duplicates"},
                  data=json.dumps([meta]), timeout=60).raise_for_status()


def replace_sections(slug: str, rows: list[dict]) -> int:
    requests.delete(f"{SUPABASE_URL}/rest/v1/gnostic_sections?doc_slug=eq.{slug}",
                    headers=H_REST, timeout=60)
    BATCH = 100
    for i in range(0, len(rows), BATCH):
        batch = rows[i:i + BATCH]
        for attempt in range(3):
            r = requests.post(f"{SUPABASE_URL}/rest/v1/gnostic_sections",
                              headers=H_REST, data=json.dumps(batch), timeout=180)
            if r.status_code in (200, 201, 204):
                break
            if r.status_code >= 500 and attempt < 2:
                time.sleep(2 * (attempt + 1)); continue
            print(f"  ERROR batch {i}: {r.status_code} {r.text[:300]}"); r.raise_for_status()
    return len(rows)


def ingest_doc(category: str, title: str, url: str, te, engine_fn, *,
               display_order: int = 0, limit_paras: int | None = None,
               dry_run: bool = False) -> dict | None:
    print(f"  → {title}  ({url})", flush=True)
    parsed = gl.parse_document(fetch(url))
    en = parsed["sections"]
    if not en:
        print("    ⚠ no sections parsed — skip"); return None
    title = title or parsed["title"] or "Untitled"
    slug = gl.make_slug(title)
    print(f"    slug={slug}  EN paras={len(en)}", flush=True)
    if dry_run:
        return {"slug": slug, "title_en": title, "en_paras": len(en)}

    zh = translate_paragraphs(en, te, engine_fn, limit=limit_paras)
    en_used = en[:len(zh)]
    gl.assert_aligned(en_used, zh)

    upsert_document({
        "slug": slug, "title_zh": title, "title_en": title, "category": category,
        "source_url": url, "display_order": display_order,
    })
    rows = []
    for i, (e, c) in enumerate(zip(en_used, zh)):
        rows.append({"doc_slug": slug, "version_code": "gnosis_en", "order_index": i, "text": e, "char_count": len(e)})
        rows.append({"doc_slug": slug, "version_code": "zh", "order_index": i, "text": c, "char_count": len(c)})
    n = replace_sections(slug, rows)
    print(f"    ✓ upserted {n} section rows ({len(zh)} paras × 2 versions)", flush=True)
    return {"slug": slug, "title_en": title, "paras": len(zh)}


# Overnight order: public-domain-clean categories first (Mead/Hermetica),
# then core Gnostic, then related religions, then dedup/peripheral last.
ALL_ORDER = ["hermetica", "mead", "gnostic_scriptures", "nag_hammadi", "valentinus",
             "manichaean", "mandaean", "cathar", "alchemical", "modern",
             "polemics", "christian_apocrypha", "dead_sea"]
CONSEC_FAIL_ABORT = 4  # stop the whole run after this many docs fail in a row (quota dead)


def done_slugs() -> set[str]:
    """Doc slugs that already have ZH sections (for --resume skip)."""
    r = requests.post(MGMT_QUERY, headers=H_MGMT, json={
        "query": "SELECT DISTINCT doc_slug FROM gnostic_sections WHERE version_code = 'zh'"})
    return {row["doc_slug"] for row in r.json()} if r.ok else set()


def process_category(key: str, te, engine_fn, *, resume: bool, done: set[str],
                     state: dict, limit_docs=None, limit_paras=None, dry_run=False) -> None:
    cat = gl.CATEGORY_BY_KEY[key]
    docs = gl.parse_category_index(fetch(gl.GNOSIS_ROOT + cat["index_path"]),
                                   base_path=cat["index_path"])
    if cat["dedup_against_existing"]:
        existing = existing_en_titles()
        before = len(docs)
        docs = [d for d in docs if not gl.is_duplicate(d["title"], existing)]
        print(f"[{key}] dedup: {before} → {len(docs)}", flush=True)
    if limit_docs:
        docs = docs[:limit_docs]
    print(f"=== {cat['label_zh']} ({key}): {len(docs)} docs ===", flush=True)
    for i, d in enumerate(docs):
        slug = gl.make_slug(d["title"])
        if resume and slug in done:
            print(f"  ⏭ skip (done): {d['title']}", flush=True)
            continue
        try:
            res = ingest_doc(key, d["title"], d["url"], te, engine_fn,
                             display_order=cat["display_order"] * 100 + i,
                             limit_paras=limit_paras, dry_run=dry_run)
            if res:
                done.add(res["slug"])
            state["consec_fail"] = 0
        except Exception as e:  # noqa: BLE001
            state["consec_fail"] += 1
            print(f"  ✗ FAIL {d['title']}: {e}  (consec={state['consec_fail']})", flush=True)
            if state["consec_fail"] >= CONSEC_FAIL_ABORT:
                raise SystemExit(f"aborting: {CONSEC_FAIL_ABORT} consecutive failures "
                                 "(quota likely exhausted) — re-run with --resume later")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--category", help="CATEGORIES key, e.g. nag_hammadi")
    ap.add_argument("--all", action="store_true", help="iterate every category (overnight)")
    ap.add_argument("--url", help="single document URL")
    ap.add_argument("--title", default="", help="document title (overrides parsed)")
    ap.add_argument("--list", action="store_true", help="list category docs and exit")
    ap.add_argument("--engine", default="gemini", choices=["gemini", "nvidia", "sonnet", "haiku"])
    ap.add_argument("--resume", action="store_true", help="skip docs already in DB")
    ap.add_argument("--limit-docs", type=int, default=None)
    ap.add_argument("--limit-paras", type=int, default=None, help="cap paragraphs per doc (pilot)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    # ── Overnight: every category ────────────────────────────────────────────
    if args.all:
        te, engine_fn = make_engine(args.engine)
        done = done_slugs() if args.resume else set()
        state = {"consec_fail": 0}
        print(f"OVERNIGHT run · resume={args.resume} · {len(done)} docs already done", flush=True)
        for key in ALL_ORDER:
            try:
                process_category(key, te, engine_fn, resume=args.resume, done=done,
                                 state=state, limit_docs=args.limit_docs,
                                 limit_paras=args.limit_paras, dry_run=args.dry_run)
            except SystemExit as e:
                print(str(e), flush=True); break
        print(f"OVERNIGHT done · {len(done)} docs total in DB", flush=True)
        return

    if not args.category:
        sys.exit("need --category KEY or --all")
    cat = gl.CATEGORY_BY_KEY.get(args.category)
    if not cat:
        sys.exit(f"unknown category {args.category}; valid: {list(gl.CATEGORY_BY_KEY)}")

    # List / whole-category mode → resolve doc links from the index page.
    if args.list or not args.url:
        if args.list:
            docs = gl.parse_category_index(fetch(gl.GNOSIS_ROOT + cat["index_path"]),
                                           base_path=cat["index_path"])
            if cat["dedup_against_existing"]:
                existing = existing_en_titles()
                docs = [d for d in docs if not gl.is_duplicate(d["title"], existing)]
            print(f"{cat['label_zh']} ({args.category}): {len(docs)} docs")
            for d in docs:
                print(f"  - {d['title']}  {d['url']}")
            return
        te, engine_fn = make_engine(args.engine)
        done = done_slugs() if args.resume else set()
        process_category(args.category, te, engine_fn, resume=args.resume, done=done,
                         state={"consec_fail": 0}, limit_docs=args.limit_docs,
                         limit_paras=args.limit_paras, dry_run=args.dry_run)
        return

    # Single-document mode
    te, engine_fn = make_engine(args.engine) if not args.dry_run else (None, None)
    ingest_doc(args.category, args.title, args.url, te, engine_fn,
               display_order=cat["display_order"] * 100,
               limit_paras=args.limit_paras, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
