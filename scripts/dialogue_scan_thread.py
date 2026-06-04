import os, sys, json, requests
sys.stdout.reconfigure(encoding='utf-8')

def _load_env():
    env = {}
    with open('c:/Users/user/Desktop/know-graph-lab/.env', 'r', encoding='utf-8-sig') as f:
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
}

url = f'{SUPABASE_URL}/rest/v1/ai_dialogues_gemini'
# paginate fully across date range
rows = []
offset = 0
PAGE = 1000
while True:
    h = dict(HEADERS)
    h['Range-Unit'] = 'items'
    h['Range'] = f'{offset}-{offset+PAGE-1}'
    resp = requests.get(url, headers=h, params={
        'select': 'id,dialogue_date,dialogue_time,title,prompt,response',
        'dialogue_date': 'gte.2026-01-13',
        'order': 'dialogue_date.asc,dialogue_time.asc.nullslast',
    })
    batch = resp.json()
    if not isinstance(batch, list) or not batch:
        break
    rows.extend(batch)
    if len(batch) < PAGE:
        break
    offset += PAGE
rows = [r for r in rows if r['dialogue_date'] <= '2026-04-18']
print(f'Total gemini rows 2026-01-13..2026-04-18: {len(rows)}')

KRISHNA = ['克里須那', '克里希納', '克里斯那', 'Krishna', '克里須納', '克里希那', '克里希纳']
JUNG    = ['榮格', 'Jung', '阿尼瑪', '阿尼姆斯', '自性', '原型', '無意識', '集體潛意識', '陰影', '共時性', '個體化']
DREAM   = ['夢']

from collections import defaultdict
by_date = defaultdict(lambda: {'total':0,'krishna':0,'jung':0,'dream':0})
for r in rows:
    t = (r.get('prompt') or '') + '\n' + (r.get('response') or '')
    d = r['dialogue_date']
    by_date[d]['total'] += 1
    if any(k in t for k in KRISHNA): by_date[d]['krishna'] += 1
    if any(k in t for k in JUNG):    by_date[d]['jung'] += 1
    if any(k in t for k in DREAM):   by_date[d]['dream'] += 1

print('\n date       | total | krishna | jung | dream')
print('-'*50)
for d in sorted(by_date):
    s = by_date[d]
    star = '  <==' if s['krishna'] else ''
    print(f"{d} | {s['total']:5d} | {s['krishna']:7d} | {s['jung']:4d} | {s['dream']:5d}{star}")

kdates = sorted([d for d,s in by_date.items() if s['krishna']])
print(f"\nDates containing '克里須那': {kdates[0]} .. {kdates[-1]}  ({len(kdates)} dates)")
total_krishna = sum(s['krishna'] for s in by_date.values())
print(f"Total entries mentioning Krishna: {total_krishna}")
