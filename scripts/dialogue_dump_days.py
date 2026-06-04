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
HEADERS = {'apikey': SERVICE_KEY, 'Authorization': f'Bearer {SERVICE_KEY}', 'Content-Type': 'application/json'}

url = f'{SUPABASE_URL}/rest/v1/ai_dialogues_gemini'
rows = []
offset = 0; PAGE = 1000
while True:
    h = dict(HEADERS); h['Range-Unit']='items'; h['Range']=f'{offset}-{offset+PAGE-1}'
    resp = requests.get(url, headers=h, params={
        'select':'id,dialogue_date,dialogue_time,title,prompt,response',
        'dialogue_date':'gte.2026-01-13',
        'order':'dialogue_date.asc,dialogue_time.asc.nullslast'})
    batch = resp.json()
    if not isinstance(batch,list) or not batch: break
    rows.extend(batch)
    if len(batch) < PAGE: break
    offset += PAGE
rows = [r for r in rows if r['dialogue_date'] <= '2026-04-18']

from collections import defaultdict
by_date = defaultdict(list)
for r in rows:
    by_date[r['dialogue_date']].append(r)

os.makedirs('c:/tmp/krishna', exist_ok=True)
# write full data as json (prompt full, response truncated 500) per date
alldates = sorted(by_date)
for d in alldates:
    ents = by_date[d]
    out = []
    for idx, r in enumerate(ents):
        resp_t = (r.get('response') or '')
        out.append({
            'id': r['id'],
            'seq': idx,
            'time': r.get('dialogue_time'),
            'prompt': (r.get('prompt') or '').strip(),
            'response': resp_t.strip()[:500],
        })
    with open(f'c:/tmp/krishna/{d}.json','w',encoding='utf-8') as f:
        json.dump({'date':d,'count':len(ents),'entries':out}, f, ensure_ascii=False, indent=1)
print(f'Wrote {len(alldates)} date files to c:/tmp/krishna/')
print('Dates:', alldates[0], '..', alldates[-1])
# index of counts
for d in alldates:
    print(d, len(by_date[d]))
