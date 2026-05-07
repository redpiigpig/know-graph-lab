#!/usr/bin/env python3
"""
Clean OCR artifacts from pong_writings id=1 and PATCH to Supabase.

Removes: airiti page-break markers, running headers/footers, footnote blocks,
         intro block (before 前言). Rejoins column-wrapped lines into paragraphs.
"""
import os, re, sys
from pathlib import Path
import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

def _sb_url(): return os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1"
def _sb_headers():
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    return {"apikey": key, "Authorization": f"Bearer {key}",
            "Content-Type": "application/json", "Prefer": "return=minimal"}

PAGE_HEADER = re.compile(
    r'^(\d+/神學論集|成聖之道.*?/\d+$|《神學論集》)',
)
# Footnote block: starts with 1-2 digit number at line start
FOOTNOTE_START = re.compile(r'^\d{1,2}($|[ A-Za-z一-鿿])')

CJK_ORDINAL = r'[壹貳參肆伍陸一二三四五六七八九十]'

def is_heading(s: str) -> bool:
    """Short CJK line without terminal punctuation."""
    t = s.strip()
    if not t or len(t) > 20:
        return False
    return not re.search(r'[，。！？、；：]$', t) and bool(re.search(r'[一-鿿]', t))

def is_section_heading(s: str) -> bool:
    """Lines starting with 壹/貳/參/一/二/三... followed by 、— section headings regardless of length."""
    t = s.strip()
    return bool(re.match(rf'^{CJK_ORDINAL}+[、,]', t))

def strip_trailing_footnote_num(s: str) -> str:
    return re.sub(r'\d{1,2}$', '', s).rstrip()


def clean(raw: str) -> str:
    # ── Split file into per-page sections by airiti ───────────────────────────
    # Pattern matches optional leading newline + airiti + newline
    sections = re.split(r'\n?airiti\n', raw)

    filtered: list[str] = []

    for sec_idx, section in enumerate(sections):
        lines = section.split('\n')

        if sec_idx == 0:
            # Before the very first airiti — skip (empty in this file)
            continue

        if sec_idx == 1:
            # First page: intro block.  Keep only from 前言 onward,
            # stopping at the second footnote marker (author bio at end).
            found_preface = False
            footnote_count = 0
            for line in lines:
                stripped = line.strip()
                if stripped == '前言':
                    found_preface = True
                if not found_preface:
                    continue
                # In preface: stop at footnote block
                if stripped and FOOTNOTE_START.match(stripped):
                    footnote_count += 1
                    break
                filtered.append(line)
            filtered.append('')  # section separator
            continue

        # Remove page header (first non-blank line matching PAGE_HEADER)
        start = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue
            if PAGE_HEADER.match(stripped):
                start = i + 1
            break

        content_lines = lines[start:]

        # Find footnote block start (first line matching FOOTNOTE_START)
        footnote_start = len(content_lines)
        for i, line in enumerate(content_lines):
            stripped = line.strip()
            if stripped and FOOTNOTE_START.match(stripped):
                footnote_start = i
                break

        page_content = content_lines[:footnote_start]
        # Strip trailing blank lines from page
        while page_content and not page_content[-1].strip():
            page_content.pop()

        filtered.extend(page_content)
        filtered.append('')  # section separator (blank between pages)

    # ── Pass 2: join column-wrapped lines into paragraphs ────────────────────
    para_buf: list[str] = []
    out: list[str] = []

    def flush():
        if para_buf:
            # Join pieces; add space when joining Latin word fragments
            result = para_buf[0]
            for s in para_buf[1:]:
                if re.search(r'[A-Za-z]$', result) and re.search(r'^[A-Za-z]', s):
                    result += ' ' + s
                else:
                    result += s
            out.append(result)
            para_buf.clear()

    i = 0
    while i < len(filtered):
        line = filtered[i]
        stripped = line.strip()

        if not stripped:
            # Blank line — real paragraph break OR page-separator
            # Treat as page-separator (don't flush) if last para_buf entry
            # doesn't end with sentence-terminal punctuation
            if (para_buf
                    and not re.search(r'[。！？」]$', para_buf[-1])
                    and i + 1 < len(filtered)
                    and filtered[i + 1].strip()):
                i += 1
                continue  # cross-page continuation; skip this blank
            flush()
            out.append('')
            i += 1
            continue

        if is_section_heading(stripped) or is_heading(stripped):
            flush()
            cleaned = strip_trailing_footnote_num(stripped)
            out.append(cleaned)
            i += 1
            continue

        para_buf.append(stripped)
        i += 1

    flush()

    result = re.sub(r'\n{3,}', '\n\n', '\n'.join(out)).strip()
    return result


def main():
    raw_path = ROOT / 'tmp_fhl' / 'writing_1_raw.txt'
    raw = raw_path.read_text(encoding='utf-8')

    cleaned = clean(raw)

    if '--dry-run' in sys.argv:
        for i, ln in enumerate(cleaned.split('\n'), 1):
            print(f"{i:3}  {ln[:100]}")
        print(f"\nTotal lines: {len(cleaned.split(chr(10)))}")
        print(f"Total chars: {len(cleaned)}")
        return

    r = requests.patch(
        f"{_sb_url()}/pong_writings",
        headers=_sb_headers(),
        params={"id": "eq.1"},
        json={"content": cleaned},
    )
    print(f"HTTP {r.status_code}" + ("  OK" if r.status_code in (200, 201, 204) else f"  {r.text[:200]}"))

if __name__ == "__main__":
    main()
