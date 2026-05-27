"""Rule-based sweep over a translated book JSONL to fix the LLM-quality
bugs the structural pipeline can't catch.

Pairs with `scan_translated_book.py`:
  - scan reports T1 (heading bleed) and T2 (h3 vs volume drift).
  - sweep applies in-place fixes plus T3 (quote chars) and T8 (term
    consistency from the per-book TERM_FIXES table).

T1 fix — heading bleed: split heading at the body-marker position, prepend
the trailing portion onto the next paragraph. Example:

  Before:
    #### 第一章—書信寫作的契機既然我看到你
    ，最為卓越的狄奧格尼圖，極其渴慕要學習...

  After:
    #### 第一章—書信寫作的契機

    既然我看到你，最為卓越的狄奧格尼圖，極其渴慕要學習...

T2 fix — first-h3 letter-title drift: when the chunk has a `volume` set
and its first h3 (### ...) doesn't match the volume, replace the h3 text
with the volume name (since the volume is what the sidebar / breadcrumb
shows; the LLM's literal H3 wording shouldn't override that). The fix is
SKIPPED when the chunk has multiple h3s — those are EPUB-packaging cross-
work bleed cases (next letter's intro got pulled into prev chunk) and
need a careful split that this sweep doesn't attempt.

T3 fix — straight quotes → CJK corner brackets. Toggle each chunk's
straight " between 「 and 」 (alternating), and ' between 『 and 』, so
all Chinese quote chars use the proper full-width CJK form. Chunks with
odd quote-count get reported but not changed (heuristically broken).
Only the `content` (Chinese) is swept; `source_text` (English original)
is left untouched.

T8 fix — term consistency. TERM_FIXES is the per-book table of
{ wrong_term: standard_term } pairs, applied longest-first so prefix
collisions don't bite. For ANF Vol 1 the table is built into the script;
other books override by editing TERM_FIXES_BY_BOOK below.

Usage:
    python scripts/sweep_book_quality.py <ebook_id> --dry-run
    python scripts/sweep_book_quality.py <ebook_id>
    python scripts/sweep_book_quality.py <ebook_id> --no-push
    python scripts/sweep_book_quality.py <ebook_id> --only-t1   # T1 only
    python scripts/sweep_book_quality.py <ebook_id> --only-t2   # T2 only
    python scripts/sweep_book_quality.py <ebook_id> --only-t3   # quotes only
    python scripts/sweep_book_quality.py <ebook_id> --only-t8   # terms only
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "scripts"))
import standardize_ebook as se  # noqa: E402

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR")
                  or r"G:\我的雲端硬碟\資料\電子書\_chunks")

# Reuse scan's body-marker set — keep in sync.
BODY_MARKERS = [
    "既然", "誠然", "親愛的", "讓我們", "誠如",
    "若你", "若我", "蓋此", "蓋我", "蓋經上", "蓋誠",
    "雖然", "但關於", "但是我", "然而我",
    "因此我", "正如我", "我先前", "我所說", "只要前一",
    "亞伯拉罕被", "本書信", "在已過去", "從一開始",
]
TITLE_CLOSE_PUNCT = re.compile(r"[。！？」）]\s*$")
EM_DASH_SPLIT_RE = re.compile(r"^(第[一二三四五六七八九十百千零0-9]+章\s*[—\-－]+\s*)(.+)$")

# Per-book term consistency fixes — { wrong_term: standard_term }. The
# standards match the volume / NCX-derived names in consolidate_by_ncx.
# Longest patterns first to avoid prefix collision (科林斯 must be tried
# before 科林).
TERM_FIXES_ANF_VOL_1 = {
    # Corinth — volume name uses 哥林多 (Protestant)
    "科林多人": "哥林多人",
    "科林斯人": "哥林多人",
    "科林多教會": "哥林多教會",
    "科林斯教會": "哥林多教會",
    "科林多": "哥林多",
    "科林斯": "哥林多",
    "科林妥": "哥林多",
    "格林多前書": "哥林多前書",
    "格林多後書": "哥林多後書",
    "格林多": "哥林多",
    # Diognetus — addressee of Mathetes' letter. Volume = 致丟格那妥書.
    "狄奧格尼圖斯": "丟格那妥",
    "狄奧格尼特斯": "丟格那妥",
    "狄奧格尼圖": "丟格那妥",
    "狄奧格尼特": "丟格那妥",
    "狄奧格尼": "丟格那妥",
    # Paul — book uses 保羅 (Protestant)
    "聖保祿": "聖保羅",
    "保祿": "保羅",
    # Philippi — volume name uses 腓立比 (Protestant)
    "斐理伯人書": "腓立比人書",
    "斐理伯人": "腓立比人",
    "斐理伯": "腓立比",
    # Cephas / 磯法 — Catholic 革法 → Protestant 磯法
    "革法": "磯法",
    # Smyrna — volume uses 士每拿
    "士麥那": "士每拿",
    # Tarsus — volume uses 他爾索, but body shows variants
    "他爾蘇城": "他爾索",
    "他爾蘇": "他爾索",
    "塔爾蘇": "他爾索",
    # Aristion — Papias references this disciple of John
    "亞里斯頓": "亞里斯鐸",
    # Jupiter — sweep both ways could happen; prefer 朱庇特 (more common
    # in Latin transliteration tradition). Body uses both.
    "木星": "朱庇特",
    # Typos
    "平安安": "平安",
}

# ── ANF Vol 2 — Fathers of the Second Century ───────────────────────────
# Hermas / Tatian / Athenagoras / Theophilus / Clement of Alexandria
TERM_FIXES_ANF_VOL_2 = {
    # Corinth — Protestant 哥林多
    "科林多人": "哥林多人",
    "科林斯人": "哥林多人",
    "科林多": "哥林多",
    "科林斯": "哥林多",
    "科林妥": "哥林多",
    "格林多前書": "哥林多前書",
    "格林多後書": "哥林多後書",
    "格林多": "哥林多",
    # Paul — Protestant 保羅
    "聖保祿": "聖保羅",
    "保祿": "保羅",
    # Philippi — Protestant 腓立比
    "斐理伯人書": "腓立比人書",
    "斐理伯人": "腓立比人",
    "斐理伯": "腓立比",
    # Cephas — Protestant 磯法
    "革法": "磯法",
    "克法": "磯法",
    # Antioch
    "安條克": "安提阿",
    # Smyrna — Vol 1 standard 士每拿
    "士麥那": "士每拿",
    # Clement of Alexandria — volume uses 革利免 (亞歷山卓)
    # 革利免 是希臘文 Κλήμης (Klemēs) 的音譯，思高/和合本/教會傳統都用此譯名；
    # 不要被 LLM 校對誤導改成英文音譯「克雷門」。
    "克萊門": "革利免",
    "克雷門": "革利免",
    # Valentinus — Vol 1 standard 瓦倫廷
    "瓦倫提努": "瓦倫廷",
    "華倫提奴": "瓦倫廷",
    "華倫提努": "瓦倫廷",
    # Heraclitus
    "赫拉克里特": "赫拉克利特",
    # Thales — Protestant Greek philosophy convention
    "泰勒斯": "泰利斯",
    # Democritus
    "德謨克里特": "德謨克利特",
    # Protagoras
    "普羅泰哥拉": "普羅泰戈拉",
    # Caius (proper name in Hermas + Clement)
    "蓋猶": "該猶",
    # Epicurus
    "伊比鳩魯": "伊壁鳩魯",
    # Hera (Greek goddess) — 赫拉 is standard; 赫剌 is rare variant
    "赫剌": "赫拉",
    # Jupiter (Vol 1 convention)
    "木星": "朱庇特",
    # Aristion (Vol 1 convention from Papias)
    "亞里斯頓": "亞里斯鐸",
    # Typos seen — 違揹 (carry-on-back) is wrong for 違背 (violate)
    "違揹": "違背",
    "平安安": "平安",
    # Autolycus — addressee of Theophilus's letter; normalize to 奧托呂庫
    "奧託呂庫": "奧托呂庫",
    "歐多呂庫": "奧托呂庫",
    "奧多利古": "奧托呂庫",
    "歐多魯克": "奧托呂庫",
    # Cassian — proper transliteration is 卡西安 (Protestant); 格西安 is wrong
    "若望‧格西安": "卡西安",
    "格西安": "卡西安",
    # Sicyon — Greek city; standardize to 西錫翁
    "錫錫翁": "西錫翁",
}

# ── ANF Vol 3 — Tertullian (Apologetic + Anti-Marcion + Ethical) ────────
TERM_FIXES_ANF_VOL_3 = {
    # Corinth
    "科林多人": "哥林多人",
    "科林斯人": "哥林多人",
    "科林多": "哥林多",
    "科林斯": "哥林多",
    "格林多前書": "哥林多前書",
    "格林多後書": "哥林多後書",
    "格林多": "哥林多",
    # Paul — Protestant 保羅
    "聖保祿": "聖保羅",
    "保祿": "保羅",
    # Peter — Protestant 彼得 (Tertullian text leans Catholic 伯多祿 due to
    # Latin sources; standardize to Protestant for cross-volume consistency)
    "伯多祿": "彼得",
    # Philippi
    "斐理伯人書": "腓立比人書",
    "斐理伯人": "腓立比人",
    "斐理伯": "腓立比",
    # Cephas
    "革法": "磯法",
    "克法": "磯法",
    # Valentinus — Vol 1 standard 瓦倫廷
    "瓦倫提努": "瓦倫廷",
    "華倫提奴": "瓦倫廷",
    "華倫提努": "瓦倫廷",
    # Hermogenes — Tertullian's adversary in《駁黑摩根》; unify to 黑摩根
    "黑爾摩根尼斯": "黑摩根",
    "赫莫根尼斯": "黑摩根",
    "黑摩根尼斯": "黑摩根",
    "赫摩根": "黑摩根",
    "赫莫根": "黑摩根",
    "黑爾摩根": "黑摩根",
    # Thales / Democritus / Protagoras
    "泰勒斯": "泰利斯",
    "塔勒斯": "泰利斯",
    "德謨克里特": "德謨克利特",
    "普羅泰哥拉": "普羅泰戈拉",
    # Pliny
    "普林尼": "普利尼",
    # Heracles → 海格力斯 (Vol 1 latinate convention)
    "赫拉克勒斯": "海格力斯",
    # Jupiter (Vol 1 convention)
    "木星": "朱庇特",
    # Typo
    "違揹": "違背",
    "對峙巖": "對峙岩",
    # Perpetua/Felicitas — Vol 3 glossary 統一為 佩爾佩圖亞 / 費莉西塔斯
    "永卓": "佩爾佩圖亞",
    "費利西塔斯": "費莉西塔斯",  # 利 vs 莉
    "費利西塔": "費莉西塔斯",
    "菲莉西妲": "費莉西塔斯",
    # Saturus / Saturninus 是兩個不同人物，不要互相替換：
    # - Saturus (殉道者，跟 Perpetua 一起死於 203 AD) → 薩圖魯
    # - Saturninus (羅馬農業神 Saturnus，或 Toulouse 的殉道者) → 薩圖爾努斯
    # 早期版本曾把兩者合併為「薩圖爾努斯」是 bug，必須保持兩名分離
    # Jupiter — Vol 1 標準 朱庇特
    "奧林匹亞宙斯": "奧林匹斯的朱庇特",
    "盧米娜神": "魯米娜神",
}

TERM_FIXES_BY_BOOK: dict[str, dict[str, str]] = {
    "c98d358d-7066-4691-a896-b7232707b0db": TERM_FIXES_ANF_VOL_1,  # ANF Vol 1
    "4e3d16fc-ef4f-420f-a3ec-56e2e92d659f": TERM_FIXES_ANF_VOL_2,  # ANF Vol 2
    "364dac2e-410f-4906-be63-8bb86b4865ee": TERM_FIXES_ANF_VOL_3,  # ANF Vol 3
}


def find_bleed_split(heading_text: str) -> tuple[str, str] | None:
    """If heading is a bleed, return (title_proper, body_bleed); else None.

    `heading_text` is the text AFTER the leading `#### ` markers. We:
      1. Skip if heading already closes with 「。！？」」 — that's a clean
         descriptive title with body-marker-like words used legitimately.
      2. Split at「第X章—」boundary if present; inspect the tail.
      3. Find the EARLIEST body marker in the tail at position > 1; split
         the heading there.
    """
    if TITLE_CLOSE_PUNCT.search(heading_text):
        return None
    m = EM_DASH_SPLIT_RE.match(heading_text)
    if not m:
        return None
    prefix, tail = m.group(1), m.group(2)
    best_pos = None
    best_marker = None
    for marker in BODY_MARKERS:
        pos = tail.find(marker)
        if pos >= 2 and (best_pos is None or pos < best_pos):
            best_pos = pos
            best_marker = marker
    if best_pos is None:
        return None
    title_proper = prefix + tail[:best_pos].rstrip()
    body_bleed = tail[best_pos:].strip()
    return title_proper, body_bleed


def sweep_t1(content: str) -> tuple[str, int]:
    """Apply T1 (heading bleed) fix to a chunk's markdown content.
    Returns (new_content, num_fixes)."""
    lines = content.split("\n")
    out: list[str] = []
    fixes = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        h_match = re.match(r"^(#{3,4})\s+(.+?)\s*$", line)
        if not h_match:
            out.append(line)
            i += 1
            continue
        marks, heading_text = h_match.group(1), h_match.group(2)
        split = find_bleed_split(heading_text)
        if not split:
            out.append(line)
            i += 1
            continue
        title_proper, body_bleed = split
        out.append(f"{marks} {title_proper}")
        # Locate the next non-empty non-heading line — that's the body
        # paragraph the bleed escaped from. Prepend the bleed onto it.
        j = i + 1
        # Skip blank lines after the heading
        while j < len(lines) and not lines[j].strip():
            out.append(lines[j])
            j += 1
        if j < len(lines):
            next_line = lines[j]
            # If the next line starts with a heading marker, the bleed has
            # nowhere natural to go — emit it as its own paragraph rather
            # than mash it into another heading.
            if re.match(r"^#{1,4}\s", next_line):
                out.append("")
                out.append(body_bleed)
            else:
                # The body line often starts with 「，」(orphan comma left
                # over from the bleed cut). Stitch cleanly.
                stitched = (body_bleed + next_line).replace("  ", " ")
                out.append(stitched)
            i = j + 1
        else:
            out.append("")
            out.append(body_bleed)
            i = j
        fixes += 1
    return "\n".join(out), fixes


def sweep_t3(content: str) -> tuple[str, int, bool]:
    """Toggle straight ASCII quotes to CJK corner brackets.

    `"`→ alternates between 「 and 」 starting with 「.
    `'`→ alternates between 『 and 』 starting with 『.

    Returns (new_content, num_replaced, ok). ok=False when a column has
    an odd number of straight quotes (likely broken pairing) — we still
    apply the toggle but caller should report.
    """
    fixes = 0
    ok = True
    n_dq = content.count('"')
    n_sq = content.count("'")
    if n_dq % 2:
        ok = False
    if n_sq % 2:
        ok = False
    # Toggle double quotes
    if n_dq:
        toggle = [True]  # True → 「, False → 」
        def _dq(_m: re.Match) -> str:
            opening = toggle[0]
            toggle[0] = not toggle[0]
            return "「" if opening else "」"
        content = re.sub(r'"', _dq, content)
        fixes += n_dq
    # Toggle single quotes (only when chunk has them; rare)
    if n_sq:
        toggle = [True]
        def _sq(_m: re.Match) -> str:
            opening = toggle[0]
            toggle[0] = not toggle[0]
            return "『" if opening else "』"
        content = re.sub(r"'", _sq, content)
        fixes += n_sq
    return content, fixes, ok


def sweep_t12(content: str) -> tuple[str, int]:
    """Insert a blank line between any ##/###/#### heading and the
    immediately-following non-heading text.

    Background: renderMarkdown uses a multiline regex
    `^###[ \\t]+([\\s\\S]+?)(?=\\n[ \\t]*\\n|\\n#|\\Z)` to capture full h3
    headings (CCEL wraps long titles across lines, so single-line `.+$`
    misses the rest). The lookahead means the heading consumes everything
    UNTIL the next blank line. When a body paragraph follows a heading
    with only a single `\\n` separator, the whole paragraph gets absorbed
    into the heading and rendered as a giant H3 — destroying ZH↔EN
    paragraph alignment in bilingual mode (chunk 11 「致腓立比人的坡旅甲
    書信」 + greeting got fused into one heading block).

    Fix: insert `\\n` between heading + body so the lookahead fires.
    """
    fixed, n = re.subn(
        r"(^#{2,4}[ \t]+[^\n]+)\n(?!\n|#)",
        r"\1\n\n",
        content, flags=re.M,
    )
    return fixed, n


def sweep_t8(content: str, term_fixes: dict[str, str]) -> tuple[str, int]:
    """Apply term-consistency replacements, longest-first to avoid prefix
    collision."""
    if not term_fixes:
        return content, 0
    fixes = 0
    # Longest first
    for wrong in sorted(term_fixes, key=len, reverse=True):
        std = term_fixes[wrong]
        if wrong == std:
            continue
        n = content.count(wrong)
        if n == 0:
            continue
        content = content.replace(wrong, std)
        fixes += n
    return content, fixes


def sweep_t2(content: str, volume: str) -> tuple[str, int]:
    """If chunk has ONE h3 NEAR THE TOP and it differs from volume,
    replace it with the volume name.

    Skipped when:
    - chunk has multiple h3s (cross-work bleed needs a chunk-split, not
      a heading rename)
    - the lone h3 appears AFTER position threshold (default 30% of the
      chunk's length): a late-positioned h3 is almost certainly the
      bleeding intro of the NEXT letter (e.g. Justin Martyr intro stuck
      at the tail of the Papias fragments chunk), so renaming it to the
      current volume corrupts the meaning. Caught after a regression on
      ANF Vol 1 chunk 48.
    """
    if not volume:
        return content, 0
    h3_iter = list(re.finditer(r"^(### )(.+?)\s*$", content, re.M))
    letter_h3s = [m for m in h3_iter
                  if not re.match(r"第[一二三四五六七八九十百千零0-9]+章",
                                  m.group(2).strip())]
    if len(letter_h3s) != 1:
        return content, 0
    m = letter_h3s[0]
    # Position guard: only fix h3s that sit in the first 30% of content.
    # A letter title is naturally at the top; anything past 30% is almost
    # always a next-letter intro that got packaged into this chunk.
    if m.start() > len(content) * 0.30:
        return content, 0
    current = m.group(2).strip()
    current_clean = re.sub(r"\[\^\d+\]", "", current).strip()
    if current_clean == volume:
        return content, 0
    def _replace(m2: re.Match) -> str:
        body = m2.group(2).strip()
        body_clean = re.sub(r"\[\^\d+\]", "", body).strip()
        if body_clean == current_clean:
            return f"### {volume}"
        return m2.group(0)
    new_content, n = re.subn(r"^(### )(.+?)\s*$", _replace, content,
                             count=1, flags=re.M)
    return new_content, n


def fetch_book(ebook_id: str) -> dict:
    r = requests.get(f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}&select=*",
                     headers=H_GET, timeout=30)
    r.raise_for_status()
    rows = r.json()
    if not rows:
        sys.exit(f"no ebooks row for {ebook_id}")
    return rows[0]


def sweep(ebook_id: str, dry_run: bool = False, push: bool = True,
          only_t1: bool = False, only_t2: bool = False,
          only_t3: bool = False, only_t8: bool = False,
          only_t12: bool = False) -> None:
    book = fetch_book(ebook_id)
    print(f"Book: {book['title']}")

    jsonl_path = CHUNKS_DIR / f"{ebook_id}.jsonl"
    chunks = [json.loads(l) for l in jsonl_path.read_text(encoding="utf-8").splitlines() if l]
    print(f"Loaded {len(chunks)} chunks")

    term_fixes = TERM_FIXES_BY_BOOK.get(ebook_id, {})

    # If any --only-X flag is set, run ONLY those steps. Else run all.
    any_only = only_t1 or only_t2 or only_t3 or only_t8 or only_t12
    run_t1 = (not any_only) or only_t1
    run_t2 = (not any_only) or only_t2
    run_t3 = (not any_only) or only_t3
    run_t8 = (not any_only) or only_t8
    run_t12 = (not any_only) or only_t12

    t1_total = t2_total = t3_total = t8_total = t12_total = 0
    t1_chunks = t2_chunks = t3_chunks = t8_chunks = t12_chunks = 0
    t3_odd_chunks: list[int] = []

    for c in chunks:
        content = c.get("content") or ""
        new_content = content
        if run_t1:
            new_content, n1 = sweep_t1(new_content)
            if n1:
                t1_total += n1
                t1_chunks += 1
        if run_t2:
            new_content, n2 = sweep_t2(new_content, c.get("volume") or "")
            if n2:
                t2_total += n2
                t2_chunks += 1
        if run_t3:
            new_content, n3, ok = sweep_t3(new_content)
            if n3:
                t3_total += n3
                t3_chunks += 1
            if not ok:
                t3_odd_chunks.append(c.get("chunk_index"))
        if run_t8 and term_fixes:
            new_content, n8 = sweep_t8(new_content, term_fixes)
            if n8:
                t8_total += n8
                t8_chunks += 1
        if run_t12:
            new_content, n12 = sweep_t12(new_content)
            if n12:
                t12_total += n12
                t12_chunks += 1
        if new_content != content:
            c["content"] = new_content

    print(f"\nT1 (heading bleed) fixes: {t1_total} in {t1_chunks} chunks")
    print(f"T2 (h3 letter-title) fixes: {t2_total} in {t2_chunks} chunks")
    print(f"T3 (quote chars) fixes:    {t3_total} in {t3_chunks} chunks")
    print(f"T12 (blank line after heading) fixes: {t12_total} in {t12_chunks} chunks")
    if t3_odd_chunks:
        print(f"  ⚠ odd-quote-count chunks (review manually): {t3_odd_chunks}")
    if term_fixes:
        print(f"T8 (term consistency) fixes: {t8_total} in {t8_chunks} chunks")
    else:
        print("T8 (term consistency): no TERM_FIXES table for this book")

    if dry_run:
        print("\n(dry-run; not writing)")
        return

    with open(jsonl_path, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"\n✓ wrote {jsonl_path.name} ({jsonl_path.stat().st_size // 1024} KB)")

    if push:
        try:
            se.push_to_r2(ebook_id, jsonl_path)
            print("✓ pushed R2")
        except Exception as e:
            print(f"⚠ R2 push: {e}", file=sys.stderr)

        # Refresh DB previews — content[:200] now reflects the fixed text.
        try:
            r = requests.delete(f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebook_id}",
                                headers=H_GET, timeout=30)
            if r.status_code not in (200, 204):
                print(f"⚠ preview DELETE: {r.status_code}", file=sys.stderr)
            rows = [{
                "ebook_id": ebook_id,
                "chunk_index": c["chunk_index"],
                "chunk_type": c.get("chunk_type", "chapter"),
                "page_number": c.get("page_number"),
                "chapter_path": c.get("chapter_path"),
                "content": (c.get("content") or "")[:200],
                "char_count": len(c.get("content") or ""),
            } for c in chunks]
            BATCH = 25
            for i in range(0, len(rows), BATCH):
                batch = rows[i:i + BATCH]
                rr = requests.post(f"{URL}/rest/v1/ebook_chunks",
                                   headers=H_JSON, json=batch, timeout=30)
                if rr.status_code not in (200, 201):
                    for row in batch:
                        requests.post(f"{URL}/rest/v1/ebook_chunks",
                                      headers=H_JSON, json=row, timeout=30)
            print(f"✓ refreshed previews ({len(rows)} rows)")
        except Exception as e:
            print(f"⚠ preview refresh: {e}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ebook_id")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--only-t1", action="store_true")
    ap.add_argument("--only-t2", action="store_true")
    ap.add_argument("--only-t3", action="store_true")
    ap.add_argument("--only-t8", action="store_true")
    ap.add_argument("--only-t12", action="store_true")
    args = ap.parse_args()
    sweep(args.ebook_id, dry_run=args.dry_run, push=not args.no_push,
          only_t1=args.only_t1, only_t2=args.only_t2,
          only_t3=args.only_t3, only_t8=args.only_t8,
          only_t12=args.only_t12)


if __name__ == "__main__":
    main()
