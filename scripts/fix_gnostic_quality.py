"""Repair low-quality gnostic_sections ZH translations in place.

The 2026-06-06 bulk run left a recurring failure mode (user: 「翻譯不太好」):
short EN headings/labels were *hallucinated* into long fabricated Chinese
essays, others were left untranslated (English/Latin remained), and some
leaked engine meta-commentary / refusals / word-by-word glosses.

This script is **section-level and surgical**: it detects the bad ZH sections
with a high-precision multi-signal detector, then RE-TRANSLATES each one from
its English source (gnosis_en) with the hardened GNOSTIC_PROMPT_TMPL (which now
forbids expansion / commentary / refusal). A heading → a short heading, so the
hallucinated body disappears. Good sections are left untouched.

  python -X utf8 scripts/fix_gnostic_quality.py --dry              # report only
  python -X utf8 scripts/fix_gnostic_quality.py --dry --show 40    # + samples
  python -X utf8 scripts/fix_gnostic_quality.py --engine gemini --limit 20
  python -X utf8 scripts/fix_gnostic_quality.py --engine haiku     # all flagged
  python -X utf8 scripts/fix_gnostic_quality.py --doc catechism    # one doc
"""
from __future__ import annotations
import os, sys, io, json, argparse, time
from pathlib import Path

import requests
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
load_dotenv(".env")

SUPABASE_URL = os.environ["SUPABASE_URL"]
PROJECT_REF = SUPABASE_URL.split("//")[1].split(".")[0]
ACCESS_TOKEN = os.environ["SUPABASE_ACCESS_TOKEN"]
SERVICE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
MGMT_QUERY = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
H_MGMT = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
H_REST = {"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}",
          "Content-Type": "application/json", "Prefer": "return=minimal"}


def mgmt(sql: str):
    r = requests.post(MGMT_QUERY, headers=H_MGMT, json={"query": sql}, timeout=120)
    r.raise_for_status()
    return r.json()


# ── Detector ──────────────────────────────────────────────────────────────────
# The quality gate lives in gnostic_library.py (pure + tested) so this repair
# tool and the inline ingest gate share ONE definition (no drift).
import gnostic_library as gl  # noqa: E402

classify = gl.classify_translation


def fetch_pairs(doc: str | None = None, category: str | None = None,
                exclude_apocrypha: bool = False, exclude_category: str | None = None):
    conds = ["e.version_code='gnosis_en'"]
    if doc:
        conds.append(f"e.doc_slug='{doc}'")
    if category:
        conds.append(f"d.category='{category}'")
    if exclude_category:
        conds.append(f"d.category<>'{exclude_category}'")
    if exclude_apocrypha:               # task #2: 23 篇等黃根春回填，不可精修
        conds.append("d.apocrypha_slug IS NULL")
    rows = mgmt(f"""
        SELECT e.doc_slug, e.order_index, e.section_label,
               e.text AS en, z.text AS zh
        FROM gnostic_sections e
        JOIN gnostic_documents d ON d.slug=e.doc_slug
        JOIN gnostic_sections z
          ON z.doc_slug=e.doc_slug AND z.order_index=e.order_index
         AND z.version_code='zh'
        WHERE {' AND '.join(conds)}
        ORDER BY e.doc_slug, e.order_index""")
    return rows


def upsert_zh(slug: str, order_index: int, text: str):
    url = (f"{SUPABASE_URL}/rest/v1/gnostic_sections"
           f"?on_conflict=doc_slug,version_code,order_index")
    body = [{"doc_slug": slug, "version_code": "zh", "order_index": order_index,
             "text": text, "char_count": len(text)}]
    r = requests.post(url, headers={**H_REST, "Prefer": "resolution=merge-duplicates"},
                      data=json.dumps(body), timeout=120)
    if r.status_code not in (200, 201, 204):
        raise RuntimeError(f"upsert {slug}#{order_index}: {r.status_code} {r.text[:200]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default="gemini",
                    choices=["gemini", "nvidia", "sonnet", "haiku"])
    ap.add_argument("--dry", action="store_true", help="detect + report, translate nothing")
    ap.add_argument("--show", type=int, default=0, help="print N flagged samples")
    ap.add_argument("--limit", type=int, default=None, help="cap sections this run")
    ap.add_argument("--doc", default=None, help="restrict to one doc_slug")
    ap.add_argument("--category", default=None, help="restrict to one category key")
    ap.add_argument("--retranslate", action="store_true",
                    help="精修: re-translate EVERY section in scope (not just flagged), "
                         "forcing fresh quality through the gate")
    ap.add_argument("--exclude-apocrypha", action="store_true",
                    help="skip docs with apocrypha_slug (task #2: 等黃根春回填，不可動)")
    ap.add_argument("--exclude-category", default=None, help="skip this category key")
    ap.add_argument("--resume", action="store_true",
                    help="ledger-resume: skip sections already done this campaign "
                         "(c:/tmp/gnostic_refine.done); survives death/quota walls")
    ap.add_argument("--pace", type=float, default=0.0, help="sleep between calls (s)")
    args = ap.parse_args()

    pairs = fetch_pairs(args.doc, args.category, args.exclude_apocrypha,
                        args.exclude_category)
    flagged = []
    by_tag: dict[str, int] = {}
    for p in pairs:
        tag = classify(p["en"], p["zh"])
        if tag:
            p["tag"] = tag
            flagged.append(p)
            by_tag[tag] = by_tag.get(tag, 0) + 1

    scope = args.category or args.doc or "ALL"
    print(f"scope={scope} · scanned {len(pairs)} EN↔ZH pairs · flagged {len(flagged)}",
          flush=True)
    for tag, n in sorted(by_tag.items(), key=lambda x: -x[1]):
        print(f"   {tag:16} {n}", flush=True)
    docs = {f["doc_slug"] for f in flagged}
    print(f"   across {len(docs)} docs", flush=True)

    if args.show:
        print("\n── samples ──")
        for f in flagged[:args.show]:
            print(f"\n[{f['tag']}] {f['doc_slug']}#{f['order_index']}")
            print(f"  EN: {f['en'][:90]!r}")
            print(f"  ZH: {f['zh'][:120]!r}")

    if args.dry:
        return

    # ── translate ──
    import translate_ebook_to_zh as te
    import ingest_gnostic as ig
    te.PROMPT_TMPL = ig.GNOSTIC_PROMPT_TMPL
    engine_fn = {
        "gemini": te.gemini_with_nvidia_fallback,
        "nvidia": te.nvidia_translate,
        "sonnet": te.sonnet_translate,
        "haiku": te.haiku_translate,
    }[args.engine]

    # --retranslate (精修): every section in scope. Default: only flagged ones.
    work = pairs if args.retranslate else flagged
    for p in work:
        p.setdefault("tag", "retranslate")

    # ledger-resume: skip sections already done this campaign (survives a death /
    # quota wall mid-run without restarting an ~18k-section job from zero).
    LEDGER = Path("c:/tmp/gnostic_refine.done")
    done: set[str] = set()
    if args.resume and LEDGER.exists():
        done = {ln.strip() for ln in LEDGER.read_text(encoding="utf-8").splitlines() if ln.strip()}
        before = len(work)
        work = [p for p in work if f"{p['doc_slug']}#{p['order_index']}" not in done]
        print(f"resume: ledger has {len(done)} done · skipping {before - len(work)} · "
              f"{len(work)} left", flush=True)
    ledger_fh = LEDGER.open("a", encoding="utf-8") if args.resume else None

    todo = work[:args.limit] if args.limit else work
    mode = "精修 re-translating" if args.retranslate else "fixing"
    print(f"\n{mode} {len(todo)} sections via --engine {args.engine}\n", flush=True)
    fixed = verbatim = failed = 0

    def mark_done(slug: str, oi: int):
        if ledger_fh:
            ledger_fh.write(f"{slug}#{oi}\n")
            ledger_fh.flush()

    for i, f in enumerate(todo, 1):
        en = (f["en"] or "").strip()
        slug, oi, tag = f["doc_slug"], f["order_index"], f["tag"]
        # trivial sources (page/citation markers, pure numbers) → keep verbatim
        if ig.is_trivial_source(en):
            upsert_zh(slug, oi, en)
            mark_done(slug, oi)
            print(f"  {i}/{len(todo)} {slug}#{oi} [{tag}] trivial→kept", flush=True)
            verbatim += 1
            continue
        try:
            # shared gated translator: retry on gate failure, verbatim fallback
            # for short structural markers (ONE definition with the ingest path).
            zh, status = ig.translate_one(en, te, engine_fn)
            upsert_zh(slug, oi, zh)
            mark_done(slug, oi)
            if status and "verbatim" in status:
                print(f"  {i}/{len(todo)} {slug}#{oi} [{tag}] kept-verbatim ({status})",
                      flush=True)
                verbatim += 1
            elif status:
                print(f"  {i}/{len(todo)} {slug}#{oi} [{tag}] ⚠ {status} (best effort) "
                      f"{len(en)}→{len(zh)}", flush=True)
                failed += 1
            else:
                print(f"  {i}/{len(todo)} {slug}#{oi} [{tag}] {len(en)}→{len(zh)} ✓",
                      flush=True)
                fixed += 1
        except Exception as e:  # noqa: BLE001
            print(f"  {i}/{len(todo)} {slug}#{oi} [{tag}] ERROR {str(e)[:120]}", flush=True)
            failed += 1
        if args.pace:
            time.sleep(args.pace)

    if ledger_fh:
        ledger_fh.close()
    print(f"\nDONE — clean {fixed} · verbatim {verbatim} · best-effort/err {failed}",
          flush=True)


if __name__ == "__main__":
    main()
