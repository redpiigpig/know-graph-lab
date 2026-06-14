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
import os, sys, io, re, json, argparse, time
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
# Engine meta-commentary / refusal / note markers that leaked into ZH content.
# Anchored near the START of the section (leaks lead the output) to stay precise.
_META_LEAD = re.compile(
    r"^[\s「『（(]*("
    r"我(?:已)?準備好(?:接收|進行|翻譯|為您)|我注意到您|"
    r"我(?:無法|不能|沒辦法)(?:完成|識別|確定|判斷|提供(?:翻譯|準確)|翻譯這|處理這|"
    r"直接(?:轉|翻)譯|為您翻譯)|"
    r"無法(?:識別|確定|判斷)(?:這(?:個|段)|您|此|原文|出)|"
    r"我(?:必須|需要)坦誠(?:告知)?|我感謝您的(?:信任|請求)|"
    r"作為(?:一個|一名)?(?:AI|人工智慧|語言模型)|很抱歉(?:，|,)?我|"
    r"請(?:您)?提供(?:要|您要|完整|您想|需要)|您提供的(?:英文|文本|文段|內容|片段|文字)|"
    r"你提供的(?:英文|文本|文段|內容|片段|文字)|這(?:個|段)文(?:本|字)(?:並非|不是|看起來)|"
    r"根據(?:著作權|版權)|基於(?:著作權|版權)|"
    r"以下(?:是|為).{0,15}(?:翻譯|譯文)|這是.{0,12}的(?:繁體中文)?翻譯|"
    r"此處「.{0,20}」(?:應譯|建議)|建議(?:保留|譯為|使用「)|"
    r"\*\*原文|\*\*翻譯|原文：|翻譯：|逐字翻譯[：:]|繁體中文翻譯："
    r")")
# Word-by-word English gloss leak: COMMON ENGLISH FUNCTION WORDS bracketed inline
# (e.g. "我（I）是（am）那（the）光（Light）"). Must NOT match legitimate scholarly
# transliteration annotations like （gnosis）（batos）（syzygy）（mythos）（ruha）.
_WORD_GLOSS = re.compile(
    r"（(?:the|is|am|are|and|of|to|in|that|which|a|an|he|she|it|was|were|be|"
    r"for|with|i|you|they|we|his|her|this|these|those|from|by|on|at|as|but|"
    r"or|not|all|out|into)）", re.I)


def latin_ratio(s: str) -> float:
    if not s:
        return 0.0
    return len(re.sub(r"[^A-Za-z]", "", s)) / len(s)


def classify(en: str, zh: str) -> str | None:
    """Return a failure-mode tag if the ZH section is bad, else None."""
    en, zh = (en or "").strip(), (zh or "").strip()
    if not zh:
        return "empty"
    if _META_LEAD.match(zh):
        return "meta_leak"
    if len(_WORD_GLOSS.findall(zh)) >= 3:
        return "word_gloss"
    if len(zh) > 40 and latin_ratio(zh) > 0.5:
        return "untranslated"
    # short EN heading blown up into a long Chinese essay (hallucination)
    if 0 < len(en) < 70 and len(zh) >= 2.5 * len(en) and latin_ratio(zh) <= 0.5:
        return "halluc_heading"
    return None


def fetch_pairs(doc: str | None):
    where = f"AND e.doc_slug='{doc}'" if doc else ""
    rows = mgmt(f"""
        SELECT e.doc_slug, e.order_index, e.section_label,
               e.text AS en, z.text AS zh
        FROM gnostic_sections e
        JOIN gnostic_sections z
          ON z.doc_slug=e.doc_slug AND z.order_index=e.order_index
         AND z.version_code='zh'
        WHERE e.version_code='gnosis_en' {where}
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
    ap.add_argument("--limit", type=int, default=None, help="cap sections to fix this run")
    ap.add_argument("--doc", default=None, help="restrict to one doc_slug")
    ap.add_argument("--pace", type=float, default=0.0, help="sleep between calls (s)")
    args = ap.parse_args()

    pairs = fetch_pairs(args.doc)
    flagged = []
    by_tag: dict[str, int] = {}
    for p in pairs:
        tag = classify(p["en"], p["zh"])
        if tag:
            p["tag"] = tag
            flagged.append(p)
            by_tag[tag] = by_tag.get(tag, 0) + 1

    print(f"scanned {len(pairs)} EN↔ZH pairs · flagged {len(flagged)}", flush=True)
    for tag, n in sorted(by_tag.items(), key=lambda x: -x[1]):
        print(f"   {tag:16} {n}", flush=True)
    docs = {}
    for f in flagged:
        docs[f["doc_slug"]] = docs.get(f["doc_slug"], 0) + 1
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

    todo = flagged[:args.limit] if args.limit else flagged
    print(f"\nre-translating {len(todo)} sections via --engine {args.engine}\n", flush=True)
    fixed = failed = 0
    for i, f in enumerate(todo, 1):
        en = (f["en"] or "").strip()
        slug, oi, tag = f["doc_slug"], f["order_index"], f["tag"]
        # trivial sources (page/citation markers, pure numbers) → keep verbatim
        if ig.is_trivial_source(en):
            upsert_zh(slug, oi, en)
            print(f"  {i}/{len(todo)} {slug}#{oi} [{tag}] trivial→kept", flush=True)
            fixed += 1
            continue
        try:
            pieces = te.split_oversized(en)
            zh = "\n\n".join(engine_fn(piece) for piece in pieces).strip()
            if not zh or classify(en, zh):
                # Re-translation still bad. For SHORT sources this is a structural
                # marker (scripture ref "Phil. ii. 6–8.", "Sections:", roman numeral
                # "XXX.", citation header) that the engine refuses or hallucinates a
                # verse/essay for. Keep the source verbatim — a citation/label is
                # language-neutral and strictly better than a fabrication.
                if len(en) <= 80:
                    upsert_zh(slug, oi, en)
                    print(f"  {i}/{len(todo)} {slug}#{oi} [{tag}] kept-verbatim "
                          f"(structural marker)", flush=True)
                    fixed += 1
                else:
                    print(f"  {i}/{len(todo)} {slug}#{oi} [{tag}] ⚠ still bad after retry "
                          f"→ {zh[:50]!r}", flush=True)
                    failed += 1
                continue
            upsert_zh(slug, oi, zh)
            print(f"  {i}/{len(todo)} {slug}#{oi} [{tag}] {len(en)}→{len(zh)} ✓", flush=True)
            fixed += 1
        except Exception as e:  # noqa: BLE001
            print(f"  {i}/{len(todo)} {slug}#{oi} [{tag}] ERROR {str(e)[:120]}", flush=True)
            failed += 1
        if args.pace:
            time.sleep(args.pace)

    print(f"\nDONE — fixed {fixed} · failed/skipped {failed}", flush=True)


if __name__ == "__main__":
    main()
