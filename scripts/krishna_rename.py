# -*- coding: utf-8 -*-
"""一次性：把「與克里須那對話」寫作計畫的舊譯名 克里須那 → 克里希那（對齊翻譯詞庫權威譯名）。
就地 find-replace，不重生內容（保留人工編輯）。

  python scripts/krishna_rename.py --dry   # 只統計、不寫
  python scripts/krishna_rename.py         # 真的寫入
"""
import os, sys, json, requests
sys.stdout.reconfigure(encoding='utf-8')

OLD, NEW = '克里須那', '克里希那'
DRY = '--dry' in sys.argv

def env():
    e = {}
    for l in open(os.path.join(os.path.dirname(__file__), '..', '.env'), encoding='utf-8-sig'):
        l = l.strip()
        if '=' in l and not l.startswith('#'):
            k, v = l.split('=', 1); e[k.strip()] = v.strip()
    return e

E = env(); U = E['SUPABASE_URL']; K = E['SUPABASE_SERVICE_ROLE_KEY']
H = {'apikey': K, 'Authorization': 'Bearer ' + K, 'Content-Type': 'application/json'}
HR = dict(H); HR['Prefer'] = 'return=minimal'

def count(s): return (s or '').count(OLD)

# 1) writing_projects（主卡，slug like krishna-dialogues%）
print('── writing_projects ──')
r = requests.get(U + '/rest/v1/writing_projects', headers=H,
                 params={'select': 'id,slug,title,subtitle,description,content_json', 'slug': 'like.krishna-dialogues%'})
for row in r.json():
    fields = ['title', 'subtitle', 'description', 'content_json']
    n = sum(count(row.get(f)) for f in fields)
    print(f"  {row['slug']}: {n} 處")
    if n and not DRY:
        upd = {f: (row[f].replace(OLD, NEW)) for f in fields if row.get(f) and OLD in row[f]}
        u = requests.patch(U + f"/rest/v1/writing_projects?id=eq.{row['id']}", headers=HR,
                           data=json.dumps(upd, ensure_ascii=False).encode('utf-8'))
        print('    patch', u.status_code)

# 2) dialogue_days（每天一筆 html）
print('── dialogue_days ──')
r = requests.get(U + '/rest/v1/dialogue_days', headers=H,
                 params={'select': 'id,day_date,day_title,html', 'project_slug': 'eq.krishna-dialogues'})
days = r.json()
tot = 0
for row in days:
    n = count(row.get('day_title')) + count(row.get('html'))
    tot += n
    if n and not DRY:
        upd = {}
        for f in ('day_title', 'html'):
            if row.get(f) and OLD in row[f]:
                upd[f] = row[f].replace(OLD, NEW)
        u = requests.patch(U + f"/rest/v1/dialogue_days?id=eq.{row['id']}", headers=HR,
                           data=json.dumps(upd, ensure_ascii=False).encode('utf-8'))
        if u.status_code not in (200, 204):
            print('    ERR', row['day_date'], u.status_code, u.text[:200])
print(f"  {len(days)} 天，共 {tot} 處")

# 3) ai_dialogue_categories（分類名稱）
print('── ai_dialogue_categories ──')
r = requests.get(U + '/rest/v1/ai_dialogue_categories', headers=H,
                 params={'select': 'id,name', 'name': f'eq.與{OLD}對話'})
for row in r.json():
    print(f"  「{row['name']}」 → 「與{NEW}對話」")
    if not DRY:
        u = requests.patch(U + f"/rest/v1/ai_dialogue_categories?id=eq.{row['id']}", headers=HR,
                           data=json.dumps({'name': f'與{NEW}對話'}, ensure_ascii=False).encode('utf-8'))
        print('    patch', u.status_code)

print('\nDRY-RUN（未寫入）' if DRY else '\n完成寫入')
