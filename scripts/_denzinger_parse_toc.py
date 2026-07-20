"""
Parse Denzinger 詳細目錄 (chunk_index=6) into structured TOC:
  - dh_titles.json — {dh_number: chinese_title} for every entry
  - toc_tree.json  — 3-level tree (part → volume → entry) for sidebar nav

Output is consumed by `_denzinger_relabel.py` to rewrite chapter_path /
volume / parent_volume on every chunk so the reader sidebar shows real
Chinese titles instead of "DH 100 / DH 101 / ..." flat list.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

EBOOK_ID = "568726d3-967e-457a-ab69-7452b21d606f"
# Locate by chapter_path label — chunk_index drifts whenever segmenter re-runs.
TOC_CHAPTER_PATH = "詳細目錄"
CHUNKS_DIR = Path(r"G:/我的雲端硬碟/資料/知識圖工作室/_chunks")
JSONL_PATH = CHUNKS_DIR / f"{EBOOK_ID}.jsonl"
OUT_DIR = Path(__file__).parent / "_denzinger_toc"


# Lines that are pure noise within 詳細目錄 content.
NOISE_LINE = re.compile(r"^\s*(?:\(\d+\)|\d{1,4}|詳細目錄)\s*$")

# "第一部分：XXX" / "第二部分：XXX" / "第三部分：XXX"
PART_RE = re.compile(r"^第[一二三四五]部分[:：]\s*(.+?)\s*$")

# Roman-numeral subsection in Part 1 ("I. ...", "II. ...")
ROMAN_RE = re.compile(r"^(I{1,3}|IV|V|VI{0,3})\.\s+(.+?)\s*$")
# Letter sub-sub ("A. ...", "B. ...")
LETTER_RE = re.compile(r"^([A-Z])\.\s+(.+?)\s*$")
# Appendix marker ("附錄一/二/三/四/五  XXX")
APPENDIX_RE = re.compile(r"^附錄[一二三四五六七八九十]\s+(.+?)\s*$")

# Pope header: "克雷孟一世 (Clemens I)：92 (882)—101 (97?) 年"
# Heuristic: contains 「：」 and contains a 4-digit year
POPE_HEADER_HINT = re.compile(r"[：:].*\d{2,4}\s*年")
# Council header: contains 「大公會議」 or 「地區會議」or 「地方會議」 and NOT a DH entry (no leading digit)
COUNCIL_HINT = re.compile(r"(大公會議|地區會議|地方會議|宗教會議)")

# DH entry start: optional leading whitespace, then DH number (with optional
# range and optional letter suffix), then whitespace, then title content.
# Examples that should match:
#   "1    宗徒們的書信..."
#   "3-5   埃及(Egypt)教會典章..."
#   "5099a-b 《主，請同我們一起住下能》..."
#   "251a-251e b) 奈斯多略..."
ENTRY_START_RE = re.compile(
    r"^\s*(\d{1,4}[a-z]?(?:-\d{0,4}[a-z]?)?)\s+(.+?)\s*$"
)

# Part 2 layout: a line that is JUST a DH range / DH number, no title; the
# title sits on the next non-empty line. Examples:
#   "300-303"
#   "5099a-b"
#   "251a-251e"
# We require a hyphen or letter suffix so we don't collide with NOISE_LINE
# (pure 1-4 digit pages → NOISE).
ENTRY_DH_ONLY_RE = re.compile(
    r"^\s*(\d{1,4}[a-z]?(?:-\d{0,4}[a-z]?)|\d{1,4}[a-z])\s*$"
)

# Page-number tail: ".......... 123" — the line buffer is "complete" when
# we see this. Some entries' tails wrap with only the page number on its
# own line (rare).
TAIL_RE = re.compile(r"\.{2,}\s*\d{1,4}\s*$")
ONLY_PAGE_RE = re.compile(r"^\.{0,}\s*\d{1,4}\s*$")


_NOISE_STRIP_LINE = re.compile(
    r"^\s*(?:---\s*拉丁文\s*---|---\s*中譯\s*---|詳細目錄|<empty>)\s*$"
)


def load_toc_content() -> str:
    """Read every chunk whose chapter_path == '詳細目錄' and join their
    contents. Segmenter merges all adjacent TOC pages into a single chunk
    (chapter='詳細目錄'), but if it ever fragments we still want the full
    text. Strips dividers + per-page 「詳細目錄」 reprints + recolumn
    `<empty>` sentinels left over from column-aware OCR."""
    parts: list[str] = []
    with JSONL_PATH.open(encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            if c.get("chapter_path") == TOC_CHAPTER_PATH:
                txt = c.get("content", "") or ""
                kept: list[str] = []
                for ln in txt.split("\n"):
                    if _NOISE_STRIP_LINE.match(ln):
                        continue
                    kept.append(ln)
                parts.append("\n".join(kept))
    if not parts:
        raise RuntimeError("No chunks with chapter_path='詳細目錄' found")
    return "\n".join(parts)


def strip_tail(title: str) -> str:
    """Remove the dot-leader + page number tail from a buffered entry."""
    # Remove trailing dots and digits and page-number patterns.
    title = re.sub(r"\s*\.{2,}\s*\d{1,4}\s*$", "", title)
    title = re.sub(r"\s+\d{1,4}\s*$", "", title)  # tail with only spaces+page
    return title.strip()


def collapse_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def parse_dh_range(dh_token: str) -> tuple[int | None, int | None, str]:
    """`5099a-b` → (5099, 5099, 'a-b')。 `3-5` → (3, 5, '')。 `251a-251e` → (251, 251, 'a-e')。"""
    if "-" in dh_token:
        left, right = dh_token.split("-", 1)
    else:
        left, right = dh_token, dh_token
    m_left = re.match(r"^(\d{1,4})([a-z]?)$", left)
    m_right = re.match(r"^(\d{0,4})([a-z]?)$", right)
    if not m_left:
        return None, None, ""
    lnum = int(m_left.group(1))
    lsuf = m_left.group(2)
    if m_right and m_right.group(1):
        rnum = int(m_right.group(1))
        rsuf = m_right.group(2)
    else:
        rnum = lnum
        rsuf = m_right.group(2) if m_right else ""
    suffix = ""
    if lsuf or rsuf:
        suffix = f"{lsuf}-{rsuf}" if lsuf and rsuf else (lsuf or rsuf)
    return lnum, rnum, suffix


def parse() -> dict:
    raw = load_toc_content()
    lines = raw.split("\n")

    entries: list[dict] = []
    # Tree shape: list of {kind: 'part'/'volume'/'entry', ...}
    # parent_volume = 第N部分, volume = pope/council/group title, dh_titles[N] = title
    cur_part: str | None = None
    cur_volume: str | None = None
    # For Part 1 we maintain a deeper hierarchy collapsed into volume:
    cur_section_group: str | None = None  # e.g. "簡單的信經", "分成部分的信經"
    cur_roman: str | None = None  # e.g. "I. 分成「聖三」三部分的信經"
    cur_letter: str | None = None  # e.g. "A. 西方教會的信經格式"

    buf: list[str] = []
    buf_done: bool = False

    def flush_entry():
        nonlocal buf, buf_done, cur_part, cur_volume
        if not buf:
            return
        joined = collapse_whitespace(" ".join(buf))
        m = ENTRY_START_RE.match(joined)
        if not m:
            buf = []
            buf_done = False
            return
        dh_token, rest = m.group(1), m.group(2)
        title = strip_tail(rest)
        lnum, rnum, suffix = parse_dh_range(dh_token)
        if lnum is None:
            buf = []
            buf_done = False
            return
        # Compose volume label.
        # Part 1: pick the deepest, most specific group label. Joining
        # ("Ⅰ. 分成「聖三」三部分的信經 / 宗徒信經") collides in the sidebar
        # because the truncated prefix looks identical across sub-groups,
        # producing four "Ⅰ. 分成「聖三」三部分的..." rows. We surface only
        # the deepest layer so each sub-group renders as its own distinct
        # volume row.
        if cur_part and cur_part.startswith("第一部分"):
            volume = cur_letter or cur_roman or cur_section_group or cur_volume
        else:
            volume = cur_volume or cur_section_group
        entries.append({
            "dh_token": dh_token,
            "dh_start": lnum,
            "dh_end": rnum,
            "dh_suffix": suffix,
            "title": title,
            "part": cur_part,
            "volume": volume,
        })
        buf = []
        buf_done = False

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()
        i += 1

        if not stripped or NOISE_LINE.match(stripped):
            if buf_done:
                flush_entry()
            continue

        # ── Headers ───────────────────────────────────────────────
        m = PART_RE.match(stripped)
        if m:
            flush_entry()
            cur_part = f"第{stripped[1]}部分：{m.group(1)}"
            cur_volume = None
            cur_section_group = None
            cur_roman = None
            cur_letter = None
            continue

        if APPENDIX_RE.match(stripped):
            flush_entry()
            cur_volume = stripped
            cur_section_group = None
            cur_roman = None
            cur_letter = None
            continue

        if ROMAN_RE.match(stripped):
            flush_entry()
            cur_roman = stripped
            cur_letter = None
            continue
        if LETTER_RE.match(stripped):
            flush_entry()
            cur_letter = stripped
            continue

        # Pope header — has 「：」 followed by year
        if POPE_HEADER_HINT.search(stripped) and not ENTRY_START_RE.match(stripped):
            # Make sure it's not a wrapped entry continuation that happens
            # to contain ":NNNN 年"
            if not buf:
                flush_entry()
                cur_volume = stripped
                cur_section_group = None
                cur_roman = None
                cur_letter = None
                continue

        # Council header — contains 大公會議/地區會議 and no leading DH
        if COUNCIL_HINT.search(stripped) and not ENTRY_START_RE.match(stripped):
            if not buf:
                # Look ahead: next non-empty line may be the date range
                # — supported formats:
                #   "451 年 10 月 8 日—11 月初"        (Chalcedon)
                #   "【1139年4月4日開幕】"              (Lateran II / III / V / Vatican II)
                #   "1512 年 5 月 3 日—1517 年 3 月 16 日" (Lateran V on rare rows)
                # We accept any line whose first 5 chars contain a 4-digit year.
                lookahead = ""
                j = i
                while j < len(lines):
                    ls = lines[j].strip()
                    j += 1
                    if not ls or NOISE_LINE.match(ls):
                        continue
                    if re.match(r"^[【\(\[]?\s*\d{3,4}\s*年", ls):
                        lookahead = ls
                    break
                flush_entry()
                cur_volume = stripped if not lookahead else f"{stripped}（{lookahead}）"
                if lookahead:
                    i = j
                cur_section_group = None
                cur_roman = None
                cur_letter = None
                continue

        # ── Entry buffering ───────────────────────────────────────
        is_entry_start = bool(ENTRY_START_RE.match(stripped))
        if is_entry_start:
            flush_entry()
            buf.append(stripped)
            if TAIL_RE.search(stripped) or ONLY_PAGE_RE.match(stripped):
                buf_done = True
                flush_entry()
            continue

        # Multi-line layout (Part 2): bare DH range, title on following line(s).
        # Synthesise a one-line "DH<space>" prefix so flush_entry's ENTRY_START_RE
        # match works once continuations append the title.
        if ENTRY_DH_ONLY_RE.match(stripped):
            flush_entry()
            buf.append(stripped + " ")  # trailing space lets next line concat
            continue

        # Continuation of current buffered entry
        if buf:
            buf.append(stripped)
            if TAIL_RE.search(stripped) or ONLY_PAGE_RE.match(stripped):
                buf_done = True
                flush_entry()
            continue

        # Otherwise — treat as a section group label (no leading number,
        # no pope/council markers, no current entry buffer). E.g.
        # "簡單的信經", "宗徒信經", "洗禮信經問答短式".
        if cur_part and cur_part.startswith("第一部分"):
            # Distinguish section_group (top-level under part) vs deeper
            # group: heuristic — if currently inside a Roman/Letter scope,
            # this line is a smaller group; otherwise it resets the chain.
            if cur_roman or cur_letter:
                cur_letter = None  # treat as a fresh group under current section
                # Use as fallback volume — replace letter with this group label
                cur_letter = stripped
            else:
                cur_section_group = stripped
                cur_roman = None
                cur_letter = None
        else:
            # Part 2 / Part 3 — non-entry line that's not a recognized
            # header. Could be a misread pope name, a council's date row
            # (already swallowed above), or a stray. Try treating as a
            # volume update if it ends with no punctuation and is short.
            if 4 <= len(stripped) <= 40 and not stripped.endswith("。"):
                cur_volume = stripped

    # Final flush
    flush_entry()

    # Build dh_titles dict (each DH number in a range maps to the entry title)
    dh_titles: dict[str, str] = {}
    for e in entries:
        start, end = e["dh_start"], e["dh_end"]
        if start is None:
            continue
        for n in range(start, (end or start) + 1):
            # First write wins (TOC entries are in DH order; later collisions
            # are sub-entries that shouldn't override the canonical title).
            dh_titles.setdefault(str(n), e["title"])

    return {
        "dh_titles": dh_titles,
        "entries": entries,
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    result = parse()
    (OUT_DIR / "dh_titles.json").write_text(
        json.dumps(result["dh_titles"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUT_DIR / "entries.json").write_text(
        json.dumps(result["entries"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    entries = result["entries"]
    parts = {}
    for e in entries:
        p = e["part"] or "(unknown)"
        parts.setdefault(p, []).append(e)
    print(f"Parsed {len(entries)} entries → {len(result['dh_titles'])} DH numbers")
    for p, es in parts.items():
        print(f"  {p}: {len(es)} entries (DH {es[0]['dh_start']}…{es[-1]['dh_end']})")
    print(f"Wrote → {OUT_DIR}/dh_titles.json + entries.json")
    # Show a sample
    print()
    print("─ Sample first 8 entries ─")
    for e in entries[:8]:
        print(f"  DH {e['dh_token']:<10} [{e['part']}] [{e['volume']}] → {e['title'][:50]}")
    print()
    print("─ Sample around DH 100 (Part 2 start) ─")
    for e in entries:
        if e["dh_start"] and 100 <= e["dh_start"] <= 115:
            print(f"  DH {e['dh_token']:<10} [{e['volume']}] → {e['title'][:50]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
