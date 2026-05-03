#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Year B (2023-2024) HTML scraper for 1day3read3pray.com
Usage:
  python scripts/lectionary_yearb_html.py [--dry-run] [--season advent]
  python scripts/lectionary_yearb_html.py --week 2023-12-03   # single week by Sunday date
"""

import os, re, sys, json, time, io
import urllib.request, urllib.error
from pathlib import Path
from datetime import date, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ── Config ────────────────────────────────────────────────────────────────────
ROOT     = Path(__file__).parent.parent
CACHE_DIR = ROOT / 'stores' / '三讀三禱' / 'yearb_cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

DRY_RUN    = '--dry-run' in sys.argv
FILTER_S   = next((a.split('=')[1] for a in sys.argv if a.startswith('--season=')), None)
FILTER_W   = next((a.split('=')[1] for a in sys.argv if a.startswith('--week=')), None)

YEAR_B_START = date(2023, 12, 3)   # Advent 1
YEAR_B_END   = date(2024, 11, 30)  # after Christ the King week

BASE_URL = 'https://www.1day3read3pray.com/3read3pray/2023-2024yearb/'
SUFFIXES = ['a', 'b', 'c']

DOW_ZH = ['週日', '週一', '週二', '週三', '週四', '週五', '週六']

# ── .env loader ───────────────────────────────────────────────────────────────
def load_env():
    env = {}
    for raw in (ROOT / '.env').read_text(encoding='utf-8').splitlines():
        m = re.match(r'^([^#=]+)=(.*)$', raw.strip())
        if m:
            k = m.group(1).strip()
            v = m.group(2).strip().strip('"').strip("'")
            env[k] = v
    return env

ENV    = load_env()
SB_URL = ENV.get('VITE_SUPABASE_URL', '')
SB_KEY = ENV.get('SUPABASE_SERVICE_KEY', '')

# ── Chinese number conversion ─────────────────────────────────────────────────
_CN_DIGIT = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9}
_CN_UNIT  = {'十':10,'廿':20,'三十':30,'四十':40}

def cn_to_int(s):
    s = s.strip()
    if not s:
        return 0
    # 廿X pattern (20-29)
    m = re.match(r'^廿([一二三四五六七八九]?)$', s)
    if m:
        return 20 + (_CN_DIGIT.get(m.group(1), 0))
    # 三十X pattern (30-39)
    m = re.match(r'^三十([一二三四五六七八九]?)$', s)
    if m:
        return 30 + (_CN_DIGIT.get(m.group(1), 0))
    # 十X pattern (10-19)
    m = re.match(r'^十([一二三四五六七八九]?)$', s)
    if m:
        return 10 + (_CN_DIGIT.get(m.group(1), 0))
    # single digit
    return _CN_DIGIT.get(s, 0)

# ── Season mapping ────────────────────────────────────────────────────────────
_SEASON_MAP = {
    '將臨': 'advent',
    '聖誕': 'christmas',
    '顯現': 'epiphany',
    '大齋': 'lent',
    '棕枝': 'lent',
    '復活': 'easter',
    '聖靈降臨': 'pentecost',
    '常年': 'pentecost',   # some pages use 常年期
}

def parse_liturgical_label(label):
    """'乙年將臨期第一主日' → (season_en, week_num, title_zh)"""
    if not label:
        return None, None, label
    for zh, en in _SEASON_MAP.items():
        if zh in label:
            # Extract week number
            m = re.search(r'第([一二三四五六七八九十廿三十]+)(?:週|主日)', label)
            wn = cn_to_int(m.group(1)) if m else 1
            # Title: season + week label
            season_zh = zh + '期' if not zh.endswith('期') else zh
            if zh == '棕枝':
                season_zh = '大齋期'
            title = label.replace('乙年', '').strip()
            return en, wn, title
    return 'pentecost', 1, label

# ── HTTP fetch with caching ───────────────────────────────────────────────────
def fetch_page(date_str, suffix):
    """Fetch one reading page, use cache if available. Returns (html|None, from_cache)."""
    cache_file = CACHE_DIR / f'{date_str}_{suffix}.html'
    if cache_file.exists():
        return cache_file.read_text(encoding='utf-8'), True

    url = f'{BASE_URL}{date_str}{suffix}/'
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=20) as r:
                html = r.read().decode('utf-8')
                cache_file.write_text(html, encoding='utf-8')
                return html, False
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None, False
            if e.code in (429, 503) and attempt < 3:
                wait = 5 * (2 ** attempt)
                print(f'  [{e.code}] 等待 {wait}s 重試...', flush=True)
                time.sleep(wait)
                continue
            return None, False
        except Exception:
            if attempt < 3:
                time.sleep(3)
                continue
            return None, False
    return None, False

# ── Page parser ───────────────────────────────────────────────────────────────
_STOP_PATTERN = re.compile(r'^(?:乙年（馬可年）|← |→ |歡迎收聽|播客|每日三讀三禱運動|訂閱)')

def parse_page(html, suffix):
    """Parse a single reading page. Returns dict or None."""
    idx = html.find('class="entry-content')
    if idx < 0:
        return None
    snippet = html[idx:idx+8000]

    # Convert block-level tags to newlines, strip all other tags
    text = re.sub(r'</?(p|div|h[1-6]|br|hr|figure|figcaption)[^>]*>', '\n', snippet, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    lines = [l.strip() for l in text.split('\n') if l.strip()]

    prayer_type = {'a': '早禱', 'b': '午禱', 'c': '晚禱'}.get(suffix, '')
    liturgical_label = ''
    book = ''
    passage = ''
    title = ''
    meditation_lines = []
    key_verse = ''

    i = 0
    # Skip the class="entry-content..." artifact line
    while i < len(lines) and 'entry-content' in lines[i]:
        i += 1

    # --- Detect format ---
    # Sunday a-page: "乙年將臨期第一主日" then "早禱經文：..."
    # Weekday: "【早禱/午禱/晚禱經課】" then "書名章節　標題"

    if i < len(lines) and lines[i].startswith('乙年') and '期' in lines[i]:
        liturgical_label = lines[i]
        i += 1

    reading_line = ''
    if i < len(lines):
        # Sunday format: 早禱經文：以賽亞書64章1-9節　標題
        m = re.match(r'(早禱|午禱|晚禱)(?:經文|經課)[：:](.*)', lines[i])
        if m:
            prayer_type = m.group(1)
            reading_line = m.group(2).strip()
            i += 1
        # Weekday format: 【早禱/午禱/晚禱經課】
        elif re.match(r'^【(早禱|午禱|晚禱)經課】$', lines[i]):
            prayer_type = re.match(r'^【(早禱|午禱|晚禱)經課】$', lines[i]).group(1)
            i += 1
            if i < len(lines) and not lines[i].startswith('【'):
                reading_line = lines[i]
                i += 1

    # Parse book/passage/title from reading_line
    if reading_line:
        # Split on fullwidth space or tab
        parts = re.split(r'[　\t]', reading_line, maxsplit=1)
        ref = parts[0].strip()
        title = parts[1].strip() if len(parts) > 1 else ''
        # Parse passage: "以賽亞書64章1-9節" → book="以賽亞書", passage="64章1-9節"
        bm = re.match(r'^(.*?)(\d+.*)$', ref)
        if bm:
            book = bm.group(1).strip()
            passage = bm.group(2).strip()
        else:
            # Psalm style: "詩篇63篇" → book="詩篇", passage="63篇"
            bm2 = re.match(r'^(詩篇)(\d+篇.*)$', ref)
            if bm2:
                book = bm2.group(1)
                passage = bm2.group(2)
            else:
                book = ref

    # Skip 【默想】 header
    if i < len(lines) and lines[i] in ('【默想】', '【經文默想】'):
        i += 1

    # Collect meditation lines until key verse or stop
    key_verse_lines = []
    in_key_verse = False

    while i < len(lines):
        line = lines[i]
        if _STOP_PATTERN.match(line):
            break
        if line == '【經文默想】':
            in_key_verse = True
            i += 1
            continue
        if in_key_verse:
            key_verse_lines.append(line)
        else:
            meditation_lines.append(line)
        i += 1

    meditation = '\n'.join(meditation_lines).strip()
    key_verse  = '\n'.join(key_verse_lines).strip()

    return {
        'prayer_type': prayer_type,
        'book':        book,
        'passage':     passage,
        'title':       title,
        'text':        '',
        'meditation':  meditation,
        'key_verse':   key_verse,
        'liturgical_label': liturgical_label,
    }

# ── Supabase helpers ──────────────────────────────────────────────────────────
def sb_get(path, params=''):
    url = f'{SB_URL}/rest/v1/{path}?{params}'
    req = urllib.request.Request(url, headers={
        'apikey': SB_KEY, 'Authorization': f'Bearer {SB_KEY}',
    })
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def sb_post(path, data):
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(
        f'{SB_URL}/rest/v1/{path}',
        data=body,
        headers={
            'apikey': SB_KEY, 'Authorization': f'Bearer {SB_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation',
        }
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def week_exists(year, season, week_num):
    rows = sb_get('pong_lectionary_weeks',
                  f'lectionary_year=eq.{year}&season=eq.{season}&week_num=eq.{week_num}&select=id')
    return rows[0]['id'] if rows else None

def day_exists(week_id, day_of_week):
    rows = sb_get('pong_lectionary_days',
                  f'week_id=eq.{week_id}&day_of_week=eq.{day_of_week}&select=id')
    return rows[0]['id'] if rows else None

# ── Main ──────────────────────────────────────────────────────────────────────
def process_week(sunday: date):
    """Process one liturgical week starting on sunday. Returns True on success."""
    week_dates = [sunday + timedelta(days=d) for d in range(7)]

    # Fetch all pages for the week
    week_data = {}   # date → {suffix: parsed}
    week_label = ''

    for d in week_dates:
        ds = d.strftime('%Y%m%d')
        day_readings = []
        for s in SUFFIXES:
            html, from_cache = fetch_page(ds, s)
            if not from_cache:
                time.sleep(0.5)
            if html is None:
                continue
            parsed = parse_page(html, s)
            if parsed:
                if not week_label and parsed.get('liturgical_label'):
                    week_label = parsed['liturgical_label']
                day_readings.append(parsed)
        if day_readings:
            week_data[d] = day_readings

    if not week_data:
        return False

    # Determine season/week_num from liturgical label on Sunday page
    season, week_num, title_zh = parse_liturgical_label(week_label)

    # If Sunday page had no label, try to infer from other days' labels
    if not week_label:
        for d, readings in week_data.items():
            for r in readings:
                if r.get('liturgical_label'):
                    week_label = r['liturgical_label']
                    season, week_num, title_zh = parse_liturgical_label(week_label)
                    break
            if week_label:
                break

    if FILTER_S and season != FILTER_S:
        print(f'  (skip {season} week, filter={FILTER_S})')
        return True

    # Date range
    present_dates = sorted(week_data.keys())
    date_range = f'{present_dates[0].strftime("%Y.%m.%d")}–{present_dates[-1].strftime("%Y.%m.%d")}'

    print(f'▶ B年 {season} wk{week_num} ({title_zh})')
    print(f'  {date_range}, {len(week_data)} 天')

    if DRY_RUN:
        for d, readings in sorted(week_data.items()):
            dow_print = d.isoweekday() % 7
            print(f'  {d.strftime("%Y-%m-%d")} ({DOW_ZH[dow_print]}): '
                  f'{len(readings)} 讀經 — '
                  + ', '.join(f'{r["prayer_type"]} {r["book"]}{r["passage"]}' for r in readings))
        print('  [dry-run] 不上傳')
        return True

    # Upload week
    existing_week_id = week_exists('B', season, week_num)
    if existing_week_id:
        print(f'  已存在 week_id={existing_week_id}，跳過')
        week_id = existing_week_id
    else:
        rows = sb_post('pong_lectionary_weeks', {
            'lectionary_year': 'B',
            'season':     season,
            'week_num':   week_num,
            'title':      title_zh,
            'date_range': date_range,
            'intro_letter': None,
            'theme_essay_title': None,
            'theme_essay': None,
            'appendices': None,
            'is_published': False,
        })
        week_id = rows[0]['id']

    # Upload days
    days_uploaded = 0
    for d, readings in sorted(week_data.items()):
        dow = d.isoweekday() % 7   # Mon=1..Sat=6, Sun→0
        day_label = f'{d.year}年{d.month}月{d.day}日（{DOW_ZH[dow]}）'

        existing_day_id = day_exists(week_id, dow)
        if existing_day_id:
            continue

        # Build readings array
        readings_json = [{
            'prayer_type': r['prayer_type'],
            'book':        r['book'],
            'passage':     r['passage'],
            'title':       r['title'],
            'text':        '',
            'meditation':  r['meditation'],
            'key_verse':   r['key_verse'],
        } for r in readings]

        sb_post('pong_lectionary_days', {
            'week_id':    week_id,
            'day_of_week': dow,
            'day_label':  day_label,
            'readings':   readings_json,
        })
        days_uploaded += 1

    print(f'  ✓ 上傳完成 (week_id={week_id}, {days_uploaded} 天)')
    return True


def main():
    print(f'三讀三禱 Year B HTML Pipeline  dry_run={DRY_RUN}')
    print(f'Supabase: {SB_URL[:40]}...')

    # Enumerate all Sundays in Year B
    cur = YEAR_B_START  # Dec 3, 2023 is a Sunday
    weeks_done = 0

    while cur <= YEAR_B_END:
        # If filtering by specific week
        if FILTER_W and cur.strftime('%Y-%m-%d') != FILTER_W:
            cur += timedelta(weeks=1)
            continue
        try:
            ok = process_week(cur)
            if ok:
                weeks_done += 1
        except Exception as e:
            print(f'  ✗ 錯誤: {e}')
        cur += timedelta(weeks=1)

    print(f'\n完成：{weeks_done} 週')


if __name__ == '__main__':
    main()
