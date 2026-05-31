"""
Parse chapter numbers from apocrypha_sections.text (cct_zh) → populate
the `chapter` INT column. Best-effort; only assigns when confident.

Detection heuristics (in priority order):
  1. Section text contains "第N章" / "第N編" Chinese chapter marker.
  2. Section text contains a line of form "<digit(s)>\\s+¹" (chapter N verse 1).
     This is 黃根春's typical chapter-start format: `12 ¹...` or `²⁸ ¹...`.
  3. Section text starts with a standalone chapter number on its own line
     (e.g. "26\n¹拉比以賽瑪利說...").
  4. Section text contains a *superscript* chapter pair "²⁸ ¹"
     (both superscript) — chapter 28 verse 1.

Returns the FIRST chapter referenced in the section. Sections that span
multiple chapters take the first one (matches PDF page semantics — the
visible header shows the chapter that page begins in).

Usage:
  python -X utf8 scripts/parse_apocrypha_chapters.py --dry-run
  python -X utf8 scripts/parse_apocrypha_chapters.py
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


SUPERSCRIPT_CHARS = '⁰¹²³⁴⁵⁶⁷⁸⁹'
SUPER_MAP = {c: str(i) for i, c in enumerate(SUPERSCRIPT_CHARS)}
def super_to_ascii(s: str) -> str:
    return ''.join(SUPER_MAP.get(c, c) for c in s)


# Chinese number → int (handles up to 999)
CN_DIGITS = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
             '六': 6, '七': 7, '八': 8, '九': 9}
def cn_to_int(s: str) -> int | None:
    if not s: return None
    # Simple two-digit forms like 二十三 / 一百零五
    if '百' in s or '千' in s:
        return None  # skip complex; rare in chapter numbers
    if '十' in s:
        before, _, after = s.partition('十')
        tens = CN_DIGITS.get(before, 1) if before else 1
        ones = CN_DIGITS.get(after, 0) if after else 0
        return tens * 10 + ones
    if len(s) == 1 and s in CN_DIGITS:
        return CN_DIGITS[s]
    return None


# Patterns
_RE_CHN_CHAPTER = re.compile(r'第([零一二三四五六七八九十]+)[ \t　]*章')  # only 章, not 部/卷/編
# Chapter N verse 1 with mixed superscript (very common in 1 Enoch / Wisdom)
_RE_NUM_SUPER_ONE = re.compile(r'(?:^|\n)[ \t　]*(\d{1,3})[ \t　]+¹(?=[ \t　]|[一-鿿])')
# Chapter N on its own line followed by verse-1 marker
_RE_SOLO_CHAPTER = re.compile(r'(?:^|\n)[ \t　]*(\d{1,3})[ \t　]*\n[ \t　]*¹')
# All-superscript chapter pair (rare but possible: ²⁸ ¹)
_RE_SUPER_PAIR = re.compile(rf'(?:^|\n)[ \t　]*([{SUPERSCRIPT_CHARS}]{{1,3}})[ \t　]+¹')


def parse_chapter(text: str) -> int | None:
    """Return the first chapter number referenced in the section."""
    # 1. Chinese chapter marker
    m = _RE_CHN_CHAPTER.search(text[:500])
    if m:
        ch = cn_to_int(m.group(1))
        if ch and 1 <= ch <= 250: return ch

    # 2. Mixed digit + superscript "1" — "<N>\\s¹"
    m = _RE_NUM_SUPER_ONE.search(text)
    if m:
        ch = int(m.group(1))
        if 1 <= ch <= 250: return ch

    # 3. Solo digit line followed by ¹
    m = _RE_SOLO_CHAPTER.search(text)
    if m:
        ch = int(m.group(1))
        if 1 <= ch <= 250: return ch

    # 4. Superscript pair
    m = _RE_SUPER_PAIR.search(text)
    if m:
        ch_super = m.group(1)
        try: ch = int(super_to_ascii(ch_super))
        except ValueError: ch = 0
        if 1 <= ch <= 250: return ch

    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    rows = mgmt_query("""
SELECT id, doc_slug, order_index, text FROM apocrypha_sections
WHERE version_code = 'cct_zh' ORDER BY doc_slug, order_index
""")
    print(f'Fetched {len(rows)} sections')

    updates = []
    by_doc: dict[str, int] = {}
    by_doc_total: dict[str, int] = {}
    for r in rows:
        by_doc_total[r['doc_slug']] = by_doc_total.get(r['doc_slug'], 0) + 1
        ch = parse_chapter(r['text'])
        if ch is None:
            continue
        updates.append({'id': r['id'], 'chapter': ch, 'doc_slug': r['doc_slug']})
        by_doc[r['doc_slug']] = by_doc.get(r['doc_slug'], 0) + 1

    print(f'{len(updates)} sections matched ({100*len(updates)/len(rows):.1f}%)')
    print(f'\nTop docs by chapter coverage:')
    sorted_docs = sorted(by_doc.items(), key=lambda x: -x[1])[:15]
    for doc, n in sorted_docs:
        total = by_doc_total[doc]
        print(f'  {doc:30s} {n}/{total} ({100*n/total:.0f}%)')

    if args.dry_run:
        print('\nSample matches:')
        for u in updates[:8]:
            text = next(r['text'] for r in rows if r['id'] == u['id'])
            print(f'  [{u["doc_slug"]}] ch={u["chapter"]}  {text[:120]!r}')
        return

    H = {'apikey': SERVICE_KEY, 'Authorization': f'Bearer {SERVICE_KEY}',
         'Content-Type': 'application/json', 'Prefer': 'return=minimal'}
    updated = 0
    for u in updates:
        for attempt in range(3):
            r = requests.patch(
                f"{SUPABASE_URL}/rest/v1/apocrypha_sections?id=eq.{u['id']}",
                headers=H,
                data=json.dumps({'chapter': u['chapter']}),
                timeout=30,
            )
            if r.status_code in (200, 201, 204):
                updated += 1
                break
            if r.status_code >= 500 and attempt < 2:
                time.sleep(1 + attempt); continue
            print(f'  ERROR id {u["id"]}: {r.status_code} {r.text[:200]}')
            break
        if updated and updated % 200 == 0:
            print(f'  updated {updated}/{len(updates)}', flush=True)
    print(f'Done. updated={updated}')


if __name__ == '__main__':
    main()
