# -*- coding: utf-8 -*-
import os, sys, json, glob, requests
sys.stdout.reconfigure(encoding='utf-8')
def env():
    e={}
    for l in open('c:/Users/user/Desktop/know-graph-lab/.env',encoding='utf-8-sig'):
        l=l.strip()
        if '=' in l and not l.startswith('#'):
            k,v=l.split('=',1); e[k.strip()]=v.strip()
    return e
E=env(); U=E['SUPABASE_URL']; K=E['SUPABASE_SERVICE_ROLE_KEY']
H={'apikey':K,'Authorization':'Bearer '+K}

# load dump per-date (date,seq)->id and valid id set
dump_by_ds={}; dump_ids=set()
for f in glob.glob('c:/tmp/krishna/2026-*.json'):
    d=json.load(open(f,encoding='utf-8-sig'))
    for e in d['entries']:
        dump_by_ds[(d['date'],e['seq'])]=e['id']
        dump_ids.add(e['id'])

# 1. base narrow set
base=json.load(open('c:/tmp/krishna/final_thread.json',encoding='utf-8-sig'))
items={x['id']:{'id':x['id'],'date':x['date'],'seq':x.get('seq')} for x in base}
print('base narrow:',len(items))

# 2. additions
added_raw=0
for f in sorted(glob.glob('c:/tmp/krishna/out2_*.json')):
    d=json.load(open(f,encoding='utf-8-sig'))
    for a in d.get('added',[]):
        added_raw+=1
        i=a['id']
        # recover via date+seq if id not a known dump id
        if i not in dump_ids:
            rec=dump_by_ds.get((a.get('date'),a.get('seq')))
            if rec: i=rec
        items.setdefault(i,{'id':i,'date':a.get('date'),'seq':a.get('seq')})
print('additions listed:',added_raw)
print('merged unique ids:',len(items))

ids=list(items)
# validate against DB
def fetch(idlist):
    found={}
    for s in range(0,len(idlist),100):
        ch=idlist[s:s+100]
        q='("'+'","'.join(ch)+'")'
        r=requests.get(U+'/rest/v1/ai_dialogues_gemini',headers=H,params={'select':'id,dialogue_date','id':f'in.{q}'})
        for row in r.json(): found[row['id']]=row['dialogue_date']
    return found
found=fetch(ids)
print('validated in DB:',len(found))
missing=[i for i in ids if i not in found]
for m in missing: print('  MISSING',m,items[m])

final=[{'id':i,'date':found[i]} for i in ids if i in found]
# attach seq from dump for ordering
id2seq={v:k[1] for k,v in dump_by_ds.items()}
for x in final: x['seq']=id2seq.get(x['id'],0)
final.sort(key=lambda x:(x['date'],x['seq']))
json.dump(final,open('c:/tmp/krishna/final_broad.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)

from collections import Counter
c=Counter(x['date'] for x in final)
print('\nBROAD per-date:')
for d in sorted(c): print(' ',d,c[d])
print('\nTOTAL broad validated:',len(final),'over',len(c),'dates',final[0]['date'],'..',final[-1]['date'])
