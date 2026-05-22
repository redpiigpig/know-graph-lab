"""Export theologians from /translation-glossary DB → ebook-translate glossary.md.

Replaces the block between
    <!-- AUTO-GLOSSARY:theologians:START -->
    <!-- AUTO-GLOSSARY:theologians:END -->
with a fresh markdown table organized by era. Also rewrites the high-frequency
person list in translate_ebook_to_zh.py's PROMPT_TMPL between
    # AUTO-PROMPT-PEOPLE:START
    # AUTO-PROMPT-PEOPLE:END

Re-run anytime to sync (after editing ★ in the UI / DB).
"""
from __future__ import annotations
import os, sys, io, re, requests
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from dotenv import load_dotenv
load_dotenv(".env")

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

GLOSSARY_MD = Path(".claude/skills/ebook-translate/glossary.md")
TRANSLATE_PY = Path("scripts/translate_ebook_to_zh.py")

# ---------- era buckets matching effectiveYear ----------
ERAS = [
    ("使徒教父與護教士（1-2c）",      lambda y: y < 200),
    ("尼西亞前教父（3c）",            lambda y: 200 <= y < 300),
    ("尼西亞 + 4c 教父",              lambda y: 300 <= y < 400),
    ("5c 教父",                       lambda y: 400 <= y < 500),
    ("6-8c 過渡期",                   lambda y: 500 <= y < 800),
    ("9-12c 中世紀早期",              lambda y: 800 <= y < 1200),
    ("13-15c 經院與後期",             lambda y: 1200 <= y < 1500),
    ("16-17c 宗改與正統時代",          lambda y: 1500 <= y < 1700),
    ("18c 啟蒙與敬虔",                lambda y: 1700 <= y < 1800),
    ("19c",                          lambda y: 1800 <= y < 1900),
    ("20c",                          lambda y: 1900 <= y < 2000),
    ("21c 當代",                      lambda y: y >= 2000),
]


def effective_year(r: dict) -> int:
    if r.get("died_year") is not None:
        return r["died_year"]
    if r.get("born_year") is not None:
        return r["born_year"] + 40
    m = re.match(r"^(\d+)(?:-(\d+))?c", r.get("century") or "", re.I)
    if m:
        a = int(m.group(1))
        b = int(m.group(2)) if m.group(2) else a
        return (a + b - 1) * 50
    return 9999


def fetch_all() -> list[dict]:
    rows = []
    offset = 0
    while True:
        r = requests.get(
            f"{URL}/rest/v1/theologians?select=*",
            headers={**H, "Range-Unit": "items", "Range": f"{offset}-{offset+999}"},
            timeout=30,
        )
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        rows.extend(batch)
        if len(batch) < 1000:
            break
        offset += 1000
    return rows


def fmt_years(r: dict) -> str:
    b, d = r.get("born_year"), r.get("died_year")
    if b is None and d is None:
        return r.get("century", "—") or "—"
    fmt = lambda y: "" if y is None else (f"{-y} BC" if y < 0 else f"{y}")
    return f"{fmt(b)}–{fmt(d)}"


def alt_variants(r: dict) -> str:
    """各傳統不同於 ★建議 的變體（簡短）。"""
    rec = (r.get("name_recommended") or "").strip()
    seen = {rec} if rec else set()
    out = []
    for tag, key in [("新教", "name_protestant"), ("思高", "name_catholic_sgs"),
                     ("東正", "name_orthodox"), ("中國", "name_china_academic")]:
        v = (r.get(key) or "").strip()
        if not v:
            continue
        first = v.split("；")[0].strip()
        if first and first not in seen:
            out.append(f"{tag}={first}")
            seen.add(first)
    return " · ".join(out) if out else ""


def gen_theologians_block(rows: list[dict]) -> str:
    rows_sorted = sorted(rows, key=effective_year)
    lines = [
        "<!-- AUTO-GLOSSARY:theologians:START -->",
        "<!-- 自動從 /translation-glossary DB 同步 — 不要手動編輯這段，改了會被 export_glossary_from_db.py 覆寫。",
        "     要改譯名請去 /translation-glossary 編輯模式 → 重跑 `python scripts/export_glossary_from_db.py`。 -->",
        "",
        f"_共 {len(rows_sorted)} 位 — 按卒年由古至今排（卒年未知按生年；生年未知按世紀）_",
        "",
    ]
    for label, pred in ERAS:
        bucket = [r for r in rows_sorted if pred(effective_year(r))]
        if not bucket:
            continue
        lines.append(f"### {label}  （{len(bucket)} 位）")
        lines.append("")
        lines.append("| 英文／拉丁 | 原文 | 年代 | ★ 建議譯名 | 其他傳統變體 |")
        lines.append("|---|---|---|---|---|")
        for r in bucket:
            name_en = r.get("name_english", "")
            orig = (r.get("name_original") or "").strip() or "—"
            yrs = fmt_years(r)
            rec = (r.get("name_recommended") or "").strip() or "—"
            alts = alt_variants(r) or "—"
            lines.append(f"| {name_en} | {orig} | {yrs} | **{rec}** | {alts} |")
        lines.append("")
    lines.append("<!-- AUTO-GLOSSARY:theologians:END -->")
    return "\n".join(lines)


def patch_glossary_md(block: str):
    text = GLOSSARY_MD.read_text(encoding="utf-8")
    start_marker = "<!-- AUTO-GLOSSARY:theologians:START -->"
    end_marker = "<!-- AUTO-GLOSSARY:theologians:END -->"
    if start_marker in text:
        text = re.sub(
            rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}",
            lambda m: block,
            text, count=1, flags=re.DOTALL,
        )
    else:
        # First-time: replace the legacy hand-written sections
        # Find from "## 教父人名（按地區" through "## 神學術語" (exclusive)
        m = re.search(
            r"## 教父人名（按地區.*?\n(?=## 神學術語)",
            text, flags=re.DOTALL,
        )
        if not m:
            # Fallback: insert before "## 神學術語"
            m = re.search(r"## 神學術語", text)
            if not m:
                raise RuntimeError("Could not find insertion point in glossary.md")
            text = text[:m.start()] + "## 教父人名（自動同步自 translation-glossary DB）\n\n" + block + "\n\n---\n\n" + text[m.start():]
        else:
            text = text[:m.start()] + "## 教父人名（自動同步自 translation-glossary DB）\n\n" + block + "\n\n---\n\n" + text[m.end():]
    GLOSSARY_MD.write_text(text, encoding="utf-8")


def gen_prompt_block(rows: list[dict]) -> str:
    """High-frequency people for translate_ebook_to_zh.py PROMPT_TMPL.
    Limit to pre-1500 (which is what Schaff ANF/NPNF/ACCS covers)."""
    rows_sorted = sorted(rows, key=effective_year)
    cap = [r for r in rows_sorted if effective_year(r) < 1500]
    lines = [
        "# AUTO-PROMPT-PEOPLE:START — 自動從 /translation-glossary DB 同步（教父全集翻譯用）",
        "AUTO_PROMPT_PEOPLE = '''",
    ]
    for r in cap:
        rec = (r.get("name_recommended") or "").strip()
        if not rec:
            continue
        lines.append(f"   - {r['name_english']} → {rec}")
    lines.append("'''")
    lines.append("# AUTO-PROMPT-PEOPLE:END")
    return "\n".join(lines)


def patch_translate_py(block: str):
    text = TRANSLATE_PY.read_text(encoding="utf-8")
    start_marker = "# AUTO-PROMPT-PEOPLE:START"
    end_marker = "# AUTO-PROMPT-PEOPLE:END"
    if start_marker in text:
        text = re.sub(
            rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}",
            lambda m: block,
            text, count=1, flags=re.DOTALL,
        )
    else:
        # Insert just before PROMPT_TMPL definition
        m = re.search(r'^PROMPT_TMPL = """', text, flags=re.M)
        if not m:
            raise RuntimeError("Could not find PROMPT_TMPL in translate_ebook_to_zh.py")
        text = text[:m.start()] + block + "\n\n" + text[m.start():]
        # Also append {AUTO_PROMPT_PEOPLE} placeholder reference into PROMPT_TMPL's intro
        # Find the "2. **教父/教會傳統術語對齊以下標準譯法**" line
        text = text.replace(
            "2. **教父/教會傳統術語對齊以下標準譯法**：\n",
            "2. **教父/教會傳統術語對齊以下標準譯法**（更完整對照表見 ebook-translate/glossary.md 自動同步段）：\n"
            "{AUTO_PROMPT_PEOPLE}\n",
            1,
        )
    TRANSLATE_PY.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    rows = fetch_all()
    print(f"Fetched {len(rows)} theologians from DB")

    theo_block = gen_theologians_block(rows)
    patch_glossary_md(theo_block)
    print(f"✓ Wrote {GLOSSARY_MD}")

    prompt_block = gen_prompt_block(rows)
    patch_translate_py(prompt_block)
    print(f"✓ Wrote {TRANSLATE_PY}")

    # Stats
    by_era = {}
    for r in rows:
        ey = effective_year(r)
        for label, pred in ERAS:
            if pred(ey):
                by_era[label] = by_era.get(label, 0) + 1
                break
    print("\nEra distribution:")
    for label, _ in ERAS:
        if label in by_era:
            print(f"  {label}: {by_era[label]}")
