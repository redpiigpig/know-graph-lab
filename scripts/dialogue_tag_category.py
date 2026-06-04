import json, sys, requests
sys.stdout.reconfigure(encoding='utf-8')
def env():
    e={}
    for l in open('c:/Users/user/Desktop/know-graph-lab/.env',encoding='utf-8-sig'):
        l=l.strip()
        if '=' in l and not l.startswith('#'):
            k,v=l.split('=',1); e[k.strip()]=v.strip()
    return e
E=env(); U=E['SUPABASE_URL']; K=E['SUPABASE_SERVICE_ROLE_KEY']
H={'apikey':K,'Authorization':'Bearer '+K,'Content-Type':'application/json'}
HR=dict(H); HR['Prefer']='return=representation'

NAME='與克里須那對話'
# 1. find or create category
r=requests.get(U+'/rest/v1/ai_dialogue_categories',headers=H,params={'select':'id,name,color','name':f'eq.{NAME}'})
existing=r.json()
if existing:
    cat=existing[0]; print('Category exists:',cat)
else:
    r=requests.post(U+'/rest/v1/ai_dialogue_categories',headers=HR,
        data=json.dumps({'name':NAME,'color':'violet'},ensure_ascii=False).encode('utf-8'))
    cat=r.json()[0]; print('Created category:',cat)
cat_id=cat['id']

# 2. load thread ids
final=json.load(open('c:/tmp/krishna/final_thread.json',encoding='utf-8'))
ids=[x['id'] for x in final]
print('Tagging',len(ids),'entries...')

rows=[{'dialogue_id':i,'category_id':cat_id} for i in ids]
HU=dict(HR); HU['Prefer']='return=minimal,resolution=ignore-duplicates'
ok=0
for s in range(0,len(rows),200):
    chunk=rows[s:s+200]
    resp=requests.post(U+'/rest/v1/ai_dialogue_entry_categories?on_conflict=dialogue_id,category_id',
        headers=HU,data=json.dumps(chunk,ensure_ascii=False).encode('utf-8'))
    if resp.status_code in (200,201,204): ok+=len(chunk)
    else: print('  ERR',resp.status_code,resp.text[:300])
print('Upserted',ok,'junction rows')

# 3. verify count
r=requests.get(U+'/rest/v1/ai_dialogue_entry_categories',headers={**H,'Prefer':'count=exact','Range':'0-0'},
    params={'select':'dialogue_id','category_id':f'eq.{cat_id}'})
print('Verify content-range:',r.headers.get('content-range'))
