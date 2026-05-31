"""
Extract footnote definitions from apocrypha_sections (cct_zh).

黃根春《基督教典外文獻》puts footnote definitions at the end of each chapter
section, formatted as:
    ²⁰ 歐 18:11。
    ²¹ 歐 9:6。
    ²² 何 10:8；路 23:3
These are typically Bible references but can be any short text.

This script:
  1. For each section, scans from end backwards for consecutive
     `^<superscript>+ <text>$` lines.
  2. Builds {marker: text} map.
  3. Stores in `footnote_defs` JSONB column; strips defs from body text.
  4. Reader merges these across the 10 sections on a page → renders at bottom.

Usage:
  python -X utf8 scripts/extract_apocrypha_footnotes.py --dry-run
  python -X utf8 scripts/extract_apocrypha_footnotes.py
"""
from __future__ import annotations
import os, sys, json, re, argparse, time
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


# Pattern: a line that starts with one-or-more Unicode superscript digits,
# optional whitespace, then short text (Bible reference or comment).
SUPERSCRIPT_CHARS = '⁰¹²³⁴⁵⁶⁷⁸⁹'
_RE_FN_DEF_LINE = re.compile(
    rf'^[{SUPERSCRIPT_CHARS}]+[ \t　]+\S.{{0,300}}$'
)
# Detect if a line is purely a footnote def (no trailing main-text continuation).
# Heuristic: short line (< 80 Chinese chars typical) starting with superscript.


def superscript_to_ascii(s: str) -> str:
    """¹⁵ → 15"""
    mapping = {c: str(i) for i, c in enumerate(SUPERSCRIPT_CHARS)}
    return ''.join(mapping.get(c, c) for c in s)


def extract_footnotes(text: str) -> tuple[str, dict]:
    """Scan from end of text backwards collecting footnote-def lines.
    Returns (cleaned_text, defs_map)."""
    lines = text.split('\n')
    defs: dict[str, str] = {}

    # Walk from end while we keep seeing footnote-def lines (allowing
    # 1-2 blank lines between them).
    keep_until = len(lines)
    blanks = 0
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].rstrip()
        if not line:
            blanks += 1
            if blanks > 2: break
            continue
        # Must start with at least one superscript digit
        if not line[0] in SUPERSCRIPT_CHARS:
            break
        m = _RE_FN_DEF_LINE.match(line)
        if not m:
            break
        # Extract marker (leading superscript run)
        j = 0
        while j < len(line) and line[j] in SUPERSCRIPT_CHARS:
            j += 1
        marker_super = line[:j]
        marker_ascii = superscript_to_ascii(marker_super)
        defn = line[j:].strip()
        defs[marker_ascii] = defn
        keep_until = i
        blanks = 0

    if not defs:
        return text, {}

    cleaned = '\n'.join(lines[:keep_until]).rstrip()
    return cleaned, defs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    rows = mgmt_query("""
SELECT id, text FROM apocrypha_sections WHERE version_code = 'cct_zh' ORDER BY id
""")
    print(f'Fetched {len(rows)} sections')

    updates = []
    for r in rows:
        cleaned, defs = extract_footnotes(r['text'])
        if defs:
            updates.append({'id': r['id'], 'text': cleaned, 'footnote_defs': defs})

    print(f'{len(updates)} sections have footnote definitions')
    total_defs = sum(len(u['footnote_defs']) for u in updates)
    print(f'Total footnote defs extracted: {total_defs}')

    if args.dry_run:
        for u in updates[:5]:
            orig = next(r['text'] for r in rows if r['id'] == u['id'])
            print(f'\n=== id {u["id"]} ===')
            print(f'BODY (last 200): ...{u["text"][-200:]!r}')
            print(f'DEFS: {u["footnote_defs"]}')
        return

    H = {'apikey': SERVICE_KEY, 'Authorization': f'Bearer {SERVICE_KEY}',
         'Content-Type': 'application/json', 'Prefer': 'return=minimal'}
    updated = 0
    for u in updates:
        for attempt in range(3):
            r = requests.patch(
                f"{SUPABASE_URL}/rest/v1/apocrypha_sections?id=eq.{u['id']}",
                headers=H,
                data=json.dumps({
                    'text': u['text'],
                    'char_count': len(u['text']),
                    'footnote_defs': u['footnote_defs'],
                }),
                timeout=30,
            )
            if r.status_code in (200, 201, 204):
                updated += 1
                break
            if r.status_code >= 500 and attempt < 2:
                time.sleep(1 + attempt); continue
            print(f'  ERROR id {u["id"]}: {r.status_code} {r.text[:200]}')
            break
        if updated and updated % 100 == 0:
            print(f'  updated {updated}/{len(updates)}', flush=True)
    print(f'Done. updated={updated}')


if __name__ == '__main__':
    main()
