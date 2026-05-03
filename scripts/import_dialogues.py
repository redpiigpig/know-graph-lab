import re, os, sys, json, requests, time
sys.stdout.reconfigure(encoding='utf-8')

def _load_env():
    env = {}
    with open('.env', 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            if '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env
_ENV = _load_env()
SUPABASE_URL = _ENV['SUPABASE_URL']
SERVICE_KEY  = _ENV['SUPABASE_SERVICE_ROLE_KEY']
HEADERS = {
    'apikey': SERVICE_KEY,
    'Authorization': f'Bearer {SERVICE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal',
}

base = 'c:/Users/user/Desktop/know-graph-lab/stores/Gemini對話_filtered'

PERIOD_MAP = {
    '上午': 'am', '早上': 'am', '凌晨': 'am_early',
    '中午': 'noon',
    '下午': 'pm', '傍晚': 'pm', '晚上': 'pm',
}

def parse_ts(s):
    m = re.search(
        r'(\d{4})年(\d{1,2})月(\d{1,2})日\s+(上午|下午|中午|晚上|凌晨|早上|傍晚)(\d{1,2}):(\d{2}):(\d{2})\s+CST',
        s
    )
    if not m:
        return None, None
    year, mon, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
    period = m.group(4)
    h, mi, sec = int(m.group(5)), int(m.group(6)), int(m.group(7))

    kind = PERIOD_MAP.get(period, 'pm')
    if kind == 'pm' and h < 12:
        h += 12
    elif kind == 'noon':
        h = 12
    elif kind == 'am_early' and h == 12:
        h = 0

    date_str = f'{year:04d}-{mon:02d}-{day:02d}'
    # CST = UTC+8 → subtract 8h for UTC
    total_min = h * 60 + mi - 480
    if total_min < 0:
        total_min += 1440
        # date adjustment not critical for our use
    uh = (total_min // 60) % 24
    um = total_min % 60
    ts = f'{date_str}T{uh:02d}:{um:02d}:{sec:02d}Z'
    return date_str, ts

def parse_entries(content, filename_date):
    entries = []
    raw_entries = re.split(r'(--- \[\d+\] ---\n)', content)

    i = 0
    while i < len(raw_entries):
        seg = raw_entries[i]
        if re.match(r'--- \[\d+\] ---\n', seg):
            body = raw_entries[i+1] if i+1 < len(raw_entries) else ''
            i += 2

            # Extract prompt (Prompted ... up to timestamp)
            pm = re.search(
                r'Prompted\s+(.*?)(\d{4}年\d{1,2}月\d{1,2}日)',
                body, re.DOTALL
            )
            if not pm:
                continue
            prompt_raw = pm.group(1)
            # Strip "Attached N file.\n- filename\n" lines
            prompt = re.sub(r'Attached \d+ files?\.\n(- .*\n)*', '', prompt_raw)
            prompt = prompt.strip()

            # Timestamp line
            ts_m = re.search(
                r'\d{4}年\d{1,2}月\d{1,2}日\s+(?:上午|下午|中午|晚上|凌晨|早上|傍晚)\d{1,2}:\d{2}:\d{2}\s+CST',
                body
            )
            date_str, ts_str = parse_ts(ts_m.group(0)) if ts_m else (filename_date, None)

            # Response: after timestamp line, before 產品：
            if ts_m:
                after_ts = body[ts_m.end():]
                response_m = re.match(r'\s*(.*?)(?=\n產品：|\Z)', after_ts, re.DOTALL)
                response = response_m.group(1).strip() if response_m else ''
            else:
                response = ''

            if not prompt:
                continue

            entries.append({
                'dialogue_date': date_str or filename_date,
                'dialogue_time': ts_str,
                'prompt': prompt,
                'response': response or None,
                'source': 'gemini',
            })
        else:
            i += 1
    return entries

def batch_insert(rows, batch_size=200):
    total = 0
    for start in range(0, len(rows), batch_size):
        chunk = rows[start:start+batch_size]
        resp = requests.post(
            f'{SUPABASE_URL}/rest/v1/ai_dialogues',
            headers=HEADERS,
            data=json.dumps(chunk, ensure_ascii=False).encode('utf-8'),
        )
        if resp.status_code not in (200, 201):
            print(f'  ERROR {resp.status_code}: {resp.text[:200]}')
        else:
            total += len(chunk)
            print(f'  inserted {start+len(chunk)} / {len(rows)}')
        time.sleep(0.1)
    return total

all_rows = []
for fname in sorted(os.listdir(base)):
    if not fname.endswith('.txt'):
        continue
    date = fname.replace('.txt', '')
    with open(os.path.join(base, fname), encoding='utf-8') as f:
        content = f.read()
    entries = parse_entries(content, date)
    all_rows.extend(entries)
    print(f'{date}: {len(entries)} entries')

print(f'\nTotal parsed: {len(all_rows)}')
print('Uploading...')
inserted = batch_insert(all_rows)
print(f'\nDone: {inserted} rows inserted')
