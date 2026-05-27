"""
Post-process pdftotext -layout output of vatican.va Chinese encyclical PDFs
into the marker format consumed by data/creeds/paragraphParser.ts:

  ## {heading text}              (section heading; standalone short non-numbered line)
  N. {body}                      (numbered paragraph, body on a single line)
  ...
  ---
  ## Footnotes
  [^M]: {body}
  ...

vatican.va Chinese PDFs use a typesetting style that injects extra spaces
between East-Asian glyphs for justification. We collapse those (and a few
other oddities):
  - Within a run of CJK characters, collapse `[CJK] +[CJK]` -> `[CJK][CJK]`
  - Strip standalone-digit page-number lines
  - Detect footnote-definition section (per page, near bottom)
  - Merge continuation lines into the current paragraph (Chinese hard-wrap
    has no end-of-paragraph signal until the next `N. ` marker)

Usage:
  python scripts/postprocess_papal_chinese_pdf.py INPUT.txt OUTPUT.txt
"""
from __future__ import annotations

import re
import sys


# CJK Unified Ideographs + common CJK punctuation ranges
CJK_RE = re.compile(
    r"[　-〿一-鿿＀-￯㐀-䶿]"
)

PARA_NUM_RE = re.compile(r"^\s*(\d{1,3})\s*[、.]\s*(.+)$")
FOOTNOTE_NUM_RE = re.compile(r"^\s*(\d{1,3})\s+(.+)$")  # number + space (not period)
PAGE_NUM_ONLY_RE = re.compile(r"^\s*\d{1,4}\s*$")


def collapse_cjk_spaces(s: str) -> str:
    """Remove the extra padding spaces vatican.va PDFs insert between CJK glyphs.

    Repeatedly squash `<CJK> +<CJK>` until no change. Preserve spaces around
    Latin/digit runs (those are real word boundaries).
    """
    pattern = re.compile(rf"({CJK_RE.pattern})\s+(?=({CJK_RE.pattern}))")
    prev = None
    while prev != s:
        prev = s
        s = pattern.sub(r"\1", s)
    # Also kill thin-space-around-quotes oddity: 「 X 」  ->  「X」 etc.
    s = re.sub(r"([「『（《【])\s+", r"\1", s)
    s = re.sub(r"\s+([」』）》】，。；：、？！])", r"\1", s)
    return s


def is_section_heading_line(line: str) -> bool:
    """Heuristic: standalone non-numbered Chinese line — a section header.

    Reject if any of:
      - starts/ends with punctuation suggesting mid-sentence continuation
      - contains commas/semicolons/colons (heading is rarely a sub-clause)
      - contains sentence-end punctuation (already a complete sentence body)
      - too long (heading usually < 30 CJK chars)
    """
    txt = line.strip()
    if not txt:
        return False
    if PARA_NUM_RE.match(txt):
        return False
    compact = re.sub(r"\s+", "", txt)
    if not (3 <= len(compact) <= 30):
        return False
    # Must be mostly CJK
    cjk_count = len(CJK_RE.findall(compact))
    if cjk_count < len(compact) * 0.6:
        return False
    # Reject lines starting with continuation/quote punctuation
    first = compact[0]
    if first in "「」『』（）：，；。、？！．,;:.":
        return False
    # Reject lines ending with continuation punctuation
    last = compact[-1]
    if last in "，；：、,;:":
        return False
    # Reject lines containing any sentence-internal punctuation
    if any(p in compact for p in "，；：、。！？「」『』（），;:.!?"):
        return False
    return True


def detect_footnote_split(lines: list[str]) -> int:
    """Find the line index where the footnote section starts on this page.

    Strategy: walk from end backward; we expect a contiguous block of lines
    each starting with a small integer (footnote definitions), possibly
    indented continuation lines in between. Return the index of the first
    footnote line, or len(lines) if no footnotes detected.
    """
    n = len(lines)
    if n == 0:
        return n
    # Find candidate footnote-def lines by pattern
    candidates: list[int] = []
    for i in range(n - 1, -1, -1):
        m = FOOTNOTE_NUM_RE.match(lines[i])
        if m:
            num = int(m.group(1))
            # Footnote numbers should be reasonable (< 600)
            if num < 600:
                candidates.append(i)
        elif lines[i].strip() == "":
            continue
        elif PARA_NUM_RE.match(lines[i]):
            # Reached body content
            break
    if len(candidates) < 1:
        return n
    # Walk forward from the lowest candidate; require the candidates to be
    # in monotonically increasing numeric order from the first to last
    candidates.sort()
    # Find the longest tail run that starts within the bottom 50% of the page
    bottom_threshold = n // 2
    # The footnote section should start in the bottom half
    first_fn = candidates[0]
    if first_fn < bottom_threshold:
        return n  # too high up, probably misidentified
    # Verify monotonic ascending numbers
    nums = []
    for idx in candidates:
        m = FOOTNOTE_NUM_RE.match(lines[idx])
        if m:
            nums.append(int(m.group(1)))
    # If at least 2 footnotes and they're ascending, accept
    if len(nums) >= 1:
        # Check they're roughly ascending (allow 1-2 out of order)
        ascending = sum(1 for i in range(len(nums) - 1) if nums[i] < nums[i + 1])
        if len(nums) == 1 or ascending >= len(nums) - 2:
            return first_fn
    return n


def process_page(page_text: str) -> tuple[list[str], list[tuple[str, str]]]:
    """Process one page.

    Returns (body_lines, footnote_defs). body_lines preserves line structure
    so paragraph assembly can happen across pages. footnote_defs is a list
    of (num, body) tuples.
    """
    raw_lines = page_text.split("\n")
    # Strip BOM / lead/trail page-number-only lines
    while raw_lines and (raw_lines[0].strip() == "" or PAGE_NUM_ONLY_RE.match(raw_lines[0])):
        raw_lines.pop(0)
    while raw_lines and (raw_lines[-1].strip() == "" or PAGE_NUM_ONLY_RE.match(raw_lines[-1])):
        raw_lines.pop()

    fn_start = detect_footnote_split(raw_lines)
    body_lines = raw_lines[:fn_start]
    footnote_lines = raw_lines[fn_start:]

    # Strip remaining standalone page-number lines from body (sometimes at top)
    body_lines = [l for l in body_lines if not PAGE_NUM_ONLY_RE.match(l)]

    # Parse footnotes
    footnote_defs: list[tuple[str, str]] = []
    cur_num: str | None = None
    cur_body: list[str] = []
    for l in footnote_lines:
        m = FOOTNOTE_NUM_RE.match(l)
        if m:
            if cur_num is not None:
                footnote_defs.append((cur_num, " ".join(cur_body)))
            cur_num = m.group(1)
            cur_body = [m.group(2)]
        elif l.strip() and cur_num is not None:
            cur_body.append(l.strip())
    if cur_num is not None:
        footnote_defs.append((cur_num, " ".join(cur_body)))

    return body_lines, footnote_defs


def assemble_paragraphs(all_body_lines: list[str]) -> list[str]:
    """Convert raw body lines into output blocks:
      ## heading
      N. body (single line)

    Strategy:
      - Track whether previous line was blank.
      - A line starting with `N. ` begins a new paragraph.
      - A non-numbered line is treated as a HEADING only if:
          (a) preceded by a blank line, AND
          (b) followed by a blank line, AND
          (c) matches is_section_heading_line() (short, no sentence punctuation).
        Otherwise it's a continuation of the current paragraph.
    """
    out: list[str] = []
    cur_para_num: str | None = None
    cur_para_body: list[str] = []
    # Pre-compute "prev blank" / "next blank" booleans for each line index
    n = len(all_body_lines)

    def prev_is_blank(i: int) -> bool:
        for j in range(i - 1, -1, -1):
            if all_body_lines[j].strip():
                return False
            return True
        return True  # at top of stream

    def next_is_blank_or_para(i: int) -> bool:
        for j in range(i + 1, n):
            stripped = all_body_lines[j].strip()
            if not stripped:
                return True
            if PARA_NUM_RE.match(stripped):
                return True
            return False
        return True  # at end

    def flush_paragraph():
        nonlocal cur_para_num, cur_para_body
        if cur_para_num is not None:
            body = collapse_cjk_spaces(" ".join(cur_para_body))
            body = re.sub(r"\s{2,}", " ", body).strip()
            out.append(f"{cur_para_num}. {body}")
            out.append("")
        cur_para_num = None
        cur_para_body = []

    for i, raw_line in enumerate(all_body_lines):
        line = raw_line.rstrip()
        if not line.strip():
            continue
        m = PARA_NUM_RE.match(line)
        if m:
            flush_paragraph()
            cur_para_num = m.group(1)
            cur_para_body = [m.group(2)]
            continue
        # Heading detection — require blank context on both sides
        if (
            prev_is_blank(i)
            and next_is_blank_or_para(i)
            and is_section_heading_line(line)
        ):
            flush_paragraph()
            heading = collapse_cjk_spaces(line.strip())
            heading = re.sub(r"\s+", " ", heading).strip()
            out.append(f"## {heading}")
            out.append("")
            continue
        # Continuation of current paragraph
        if cur_para_num is not None:
            cur_para_body.append(line.strip())
    flush_paragraph()
    return out


def maybe_simplified_to_traditional(text: str) -> str:
    """If text is detected as simplified Chinese, convert to TW traditional.

    Heuristic: count distinct simplified-only characters; if many appear, run
    opencc s2tw. Reason: vatican.va Chinese PDFs vary between zh-CN simplified
    (older Benedict XVI / John Paul II era) and zh-TW traditional (current
    Francis era). We want output to be traditional per project convention.
    """
    # Common simplified-only chars unlikely to appear in any traditional text
    simp_markers = "国学习时实现这进经济产业过来认识让产业从们对发会觉计画运动语动"
    score = sum(text.count(c) for c in simp_markers)
    if score < 5:
        return text
    try:
        import opencc  # type: ignore
        cc = opencc.OpenCC("s2tw")
        converted = cc.convert(text)
        print(f"  Converted simplified→traditional (score={score})", file=sys.stderr)
        return converted
    except Exception as e:
        print(f"  opencc unavailable, skipping conversion: {e}", file=sys.stderr)
        return text


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: postprocess_papal_chinese_pdf.py INPUT.txt OUTPUT.txt", file=sys.stderr)
        return 1
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as f:
        text = f.read()
    text = maybe_simplified_to_traditional(text)

    pages = text.split("\x0c")
    all_body_lines: list[str] = []
    all_footnotes: list[tuple[str, str]] = []
    for page in pages:
        body, fns = process_page(page)
        all_body_lines.extend(body)
        all_body_lines.append("")  # blank between pages for safety
        all_footnotes.extend(fns)

    blocks = assemble_paragraphs(all_body_lines)

    # Dedupe footnotes by num (later occurrences may be wrap-fragments — keep first)
    seen: set[str] = set()
    unique_fns: list[tuple[str, str]] = []
    for num, body in all_footnotes:
        if num in seen:
            continue
        seen.add(num)
        body = collapse_cjk_spaces(body)
        body = re.sub(r"\s{2,}", " ", body).strip()
        unique_fns.append((num, body))
    # Sort numerically
    unique_fns.sort(key=lambda x: int(x[0]))

    if unique_fns:
        blocks.append("---")
        blocks.append("")
        blocks.append("## Footnotes")
        blocks.append("")
        for num, body in unique_fns:
            blocks.append(f"[^{num}]: {body}")
            blocks.append("")  # blank line so parseDoc treats each as its own block

    with open(dst, "w", encoding="utf-8") as f:
        f.write("\n".join(blocks).strip() + "\n")
    print(f"Wrote {dst} ({len(blocks)} blocks, {len(unique_fns)} footnotes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
