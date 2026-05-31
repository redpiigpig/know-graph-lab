"""
Strip running-header bleed from apocrypha_sections.text (cct_zh).

After Vision OCR, ~194 sections start with `<page-num> 基督教典外文獻—...第N冊`
where the page header was extracted as inline text. Also 122 sections start
with `第N部分:卷X{name}` headers, and some have headers in the middle.

This script:
  1. Removes leading page-number + book-title bleed from text
  2. Removes trailing book-title bleed
  3. Removes mid-text running header lines
  4. Removes part-header bleed at the very top of sections
  5. Removes Vision-OCR "(此頁為空白或未提供影像)" placeholder
  6. Updates apocrypha_sections via PATCH

Usage:
  python -X utf8 scripts/clean_apocrypha_headers.py --dry-run
  python -X utf8 scripts/clean_apocrypha_headers.py
"""
from __future__ import annotations
import os, sys, json, re, argparse
import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
SUPABASE_URL = os.environ['SUPABASE_URL']
PROJECT_REF = SUPABASE_URL.split('//')[1].split('.')[0]
ACCESS_TOKEN = os.environ['SUPABASE_ACCESS_TOKEN']
SERVICE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']


def mgmt_query(sql: str):
    r = requests.post(
        f'https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query',
        headers={'Authorization': f'Bearer {ACCESS_TOKEN}', 'Content-Type': 'application/json'},
        json={'query': sql}, timeout=120)
    r.raise_for_status()
    return r.json() if r.text else []


# ── Header bleed patterns ───────────────────────────────────────────────
#
# Common forms (collected from sample queries):
#   "16 基督教典外文獻 — 舊約篇 第一冊\n"        # page-num + title at top
#   "104 到羞辱。耶穌,我向你..."                # page-num + sentence run-on
#   "20 太地因盼望嬰孩的來臨而..."              # page-num + sentence
#   "基督教典外文獻──新約篇 第二冊                    302"  # header line with right-pad page num
#   "基督教典外文獻——黃約篇  第六冊"
#   "第五部分：卷三 敘利亞語門安德藏言       183"  # part header line
#   "（此頁為空白或未提供影像）"                  # Vision OCR empty marker

# Match a single Chinese-language running header line ending with optional
# trailing page-number (often right-aligned with multiple spaces).
_RE_HEADER_LINE = re.compile(
    r'(?m)^[ 　\t]*基督教典外文獻[—─——\-]+[新舊黃]約篇[^\n]*第[一二三四五六七八九十]+冊[^\n]*$',
)
# Same header pattern but mid-text (not start-of-line) — applied as a global
# replacement, gobbles up to next newline ONLY.
_RE_HEADER_INLINE = re.compile(
    r'基督教典外文獻[—─——\-]+[新舊黃]約篇[^\n]{0,40}第[一二三四五六七八九十]+冊[ \t　]*\d*',
)

# Page-number prefix + immediate "基督教典外文獻..." continuation (the most
# common form at start of a Vision-OCR chunk).
_RE_LEADING_PAGENUM_TITLE = re.compile(
    r'^[ \t]*\d{1,3}[ \t　]+基督教典外文獻[^\n]*(?:\n|$)',
)

# Leading bare page number followed by Chinese sentence start (no
# space-separated header word).
_RE_LEADING_PAGENUM_ALONE = re.compile(
    r'^[ \t]*(\d{1,3})[ \t　]+(?=[一-鿿])',
)

# Part header bleed — strip ONLY the "第N部分:卷X{文獻名}" prefix portion,
# not the entire line (Vision OCR often concatenates header and content
# inline without a newline: "第一部分:卷一以諾一書23判。³²...").
_RE_PART_HEADER_PREFIX = re.compile(
    r'^[ \t]*第[一二三四五六七八九十]+部分[：:][ \t　]*卷[一二三四五六七八九十百千]+[ \t　]*[一-鿿]{2,15}書?',
)
# Part header as its own line (less common after the inline fix above).
_RE_PART_HEADER_LINE = re.compile(
    r'(?m)^[ \t]*第[一二三四五六七八九十]+部分[：:][ \t　]*卷[一二三四五六七八九十百千]+[^\n]{0,30}$',
)

# Vision OCR empty-page placeholder — discard the whole section content.
_RE_EMPTY_PLACEHOLDER = re.compile(
    r'（此頁為空白或未提供影像）|（此頁為.*?空白.*?）|（此頁未提供.*?）'
)


def clean(text: str) -> str | None:
    """Return cleaned text or None if section should be entirely removed."""
    t = text

    # Strip the empty-page placeholder if it's the entire content
    if _RE_EMPTY_PLACEHOLDER.match(t.strip()):
        return ''
    t = _RE_EMPTY_PLACEHOLDER.sub('', t)

    # Strip leading page-num + title combo
    t = _RE_LEADING_PAGENUM_TITLE.sub('', t)

    # Strip any standalone header lines (anywhere in text)
    t = _RE_HEADER_LINE.sub('', t)
    # Also strip inline header (no leading whitespace required)
    t = _RE_HEADER_INLINE.sub('', t)

    # Strip leading part-header PREFIX (inline form — "第一部分:卷一以諾一書"
    # immediately followed by content on same line).
    t = _RE_PART_HEADER_PREFIX.sub('', t).lstrip()

    # Strip standalone part-header lines
    t = _RE_PART_HEADER_LINE.sub('', t)

    # If the cleaned text starts with a bare page number followed by Chinese
    # content (e.g. "20 太地因..."), strip the page number prefix only when
    # the first line is short — this catches header bleed without nuking
    # legitimate "1 the first verse" style verse numbers (which are usually
    # preserved by the verse-marker logic and have other line context).
    m = _RE_LEADING_PAGENUM_ALONE.match(t)
    if m:
        # Only strip if this is in fact a page-number bleed (not a verse marker).
        # Heuristic: if the number is >= 10 and the rest of the line is
        # long-running prose (not a separate "Chapter N verse N" type intro),
        # treat as header bleed.
        page_num = int(m.group(1))
        first_line_end = t.find('\n')
        if first_line_end == -1: first_line_end = len(t)
        first_line = t[m.end():first_line_end]
        if page_num >= 10 and len(first_line.strip()) > 30:
            t = t[m.end():]

    # Collapse 3+ newlines to 2; strip leading/trailing whitespace
    t = re.sub(r'\n{3,}', '\n\n', t)
    t = t.strip()

    if not t:
        return ''
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    rows = mgmt_query("""
SELECT id, text FROM apocrypha_sections WHERE version_code = 'cct_zh' ORDER BY id
""")
    print(f'Fetched {len(rows)} sections')

    changed = []
    deleted = 0
    for r in rows:
        orig = r['text']
        new = clean(orig)
        if new is None:
            continue
        if new != orig:
            changed.append({'id': r['id'], 'text': new, 'char_count': len(new)})
            if not new:
                deleted += 1

    print(f'{len(changed)} sections changed ({deleted} would be emptied)')

    if args.dry_run:
        # Show 3 sample diffs
        for c in changed[:3]:
            orig = next(r['text'] for r in rows if r['id'] == c['id'])
            print(f'\n=== id {c["id"]} ===')
            print(f'BEFORE: {orig[:200]!r}')
            print(f'AFTER : {c["text"][:200]!r}')
        return

    # Apply via PATCH batch (50 each to avoid timeout)
    H = {'apikey': SERVICE_KEY, 'Authorization': f'Bearer {SERVICE_KEY}',
         'Content-Type': 'application/json', 'Prefer': 'return=minimal'}
    import time
    updated = 0
    for c in changed:
        for attempt in range(3):
            r = requests.patch(
                f"{SUPABASE_URL}/rest/v1/apocrypha_sections?id=eq.{c['id']}",
                headers=H,
                data=json.dumps({'text': c['text'], 'char_count': c['char_count']}),
                timeout=30,
            )
            if r.status_code in (200, 201, 204):
                updated += 1
                break
            if r.status_code >= 500 and attempt < 2:
                time.sleep(1 + attempt)
                continue
            print(f'  ERROR id {c["id"]}: {r.status_code} {r.text[:200]}')
            break
        if updated % 100 == 0 and updated > 0:
            print(f'  updated {updated}/{len(changed)}', flush=True)
    print(f'Done. updated={updated}')


if __name__ == '__main__':
    main()
