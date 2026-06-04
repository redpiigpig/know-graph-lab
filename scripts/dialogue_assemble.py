# -*- coding: utf-8 -*-
"""Assemble polished.jsonl into editable dialogue transcripts, split by month
into sibling /works cards ('pages'). Main card becomes an index/overview."""
import os, sys, json, re, datetime, requests
from collections import defaultdict, OrderedDict
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

WK=['星期一','星期二','星期三','星期四','星期五','星期六','星期日']
MONTH_ZH={'01':'一月','02':'二月','03':'三月','04':'四月'}
def esc(s): return (s or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
def turn_html(speaker,text):
    paras=[p.strip() for p in re.split(r'\n\n+', text or '') if p.strip()] or ['']
    out=[]
    for i,p in enumerate(paras):
        p=esc(p).replace('\n','<br>')
        out.append(f'<p><strong>{speaker}：</strong>{p}</p>' if i==0 else f'<p>{p}</p>')
    return ''.join(out)

recs=[json.loads(l) for l in open('c:/tmp/krishna/polished.jsonl',encoding='utf-8')]
print('records:',len(recs))
try:
    DAY_TOPICS=json.load(open('c:/tmp/krishna/day_topics.json',encoding='utf-8'))
except Exception:
    DAY_TOPICS={}
print('days with topics:',len(DAY_TOPICS))
recs.sort(key=lambda r:(r['date'], r.get('time') or ''))
by_month=defaultdict(lambda: defaultdict(list))
for r in recs:
    by_month[r['date'][:7]][r['date']].append(r)

def header(d):
    y,m,dd=map(int,d.split('-'))
    w=WK[datetime.date(y,m,dd).weekday()]
    return f'{y}年{m}月{dd}日（{w}）'

# build per-month HTML + create/update sibling cards
months=sorted(by_month)
url=f'{U}/rest/v1/writing_projects'
sort=2
links=[]
for mo in months:
    ym=mo.replace('-','')
    slug=f'krishna-dialogues-{mo}'
    parts=[f'<h1>與克里須那對話 · 2026年{MONTH_ZH[mo[5:]]}</h1>',
           '<p><em>夢境與榮格學說的長談（可編輯草稿）。克里須那的回覆由 NVIDIA 潤飾成對話錄；阿周那為原話。</em></p>']
    nday=0; nturn=0
    for d in sorted(by_month[mo]):
        nday+=1
        turns=by_month[mo][d]
        parts.append(f'<h2>{header(d)}</h2>')
        segs=DAY_TOPICS.get(d) or []
        seg_at={int(s['start']):str(s.get('title','')).strip() for s in segs}
        if 0 not in seg_at:  # ensure the day always opens with a topic header
            seg_at[0]=(segs[0].get('title','').strip() if segs else '') or '當日對話'
        for i,r in enumerate(turns):
            ttl=seg_at.get(i)
            if ttl and ttl!='（未分段）':
                parts.append(f'<h3>主題：{esc(ttl)}</h3>')
            nturn+=1
            if r.get('arjuna'): parts.append(turn_html('阿周那', r['arjuna']))
            parts.append(turn_html('克里須那', r.get('krishna','')))
    html=''.join(parts)
    # upsert card
    ex=requests.get(url,headers=H,params={'select':'slug','slug':f'eq.{slug}'}).json()
    payload={'slug':slug,'title':f'與克里須那對話 · 2026年{MONTH_ZH[mo[5:]]}',
             'subtitle':f'夢境與榮格 · {mo}','emoji':'🪈','color':'violet',
             'status':'草稿','sort_order':sort,'content_json':html}
    if ex:
        requests.patch(url+f'?slug=eq.{slug}',headers=HR,data=json.dumps({'content_json':html,'title':payload['title'],'status':'草稿'},ensure_ascii=False).encode('utf-8'))
        print('updated',slug,f'{nday}天 {nturn}則 {len(html)//1024}KB')
    else:
        requests.post(url,headers=HR,data=json.dumps(payload,ensure_ascii=False).encode('utf-8'))
        print('created',slug,f'{nday}天 {nturn}則 {len(html)//1024}KB')
    links.append((mo,slug,nday,nturn))
    sort+=1

# main card → index/overview
idx=['<h1>與克里須那對話</h1>',
     '<p><em>夢境與榮格學說的一場長談，也是一段日子的生活絮語 · 2026-01-13 → 2026-04-18</em></p>',
     '<p>完整對話依月份分成四「頁」（可各自編輯）。克里須那的回覆已用 NVIDIA 潤飾成流暢對話錄，阿周那為原話；每日標有日期與星期。</p>',
     '<h2>分月對話（點入各卡片編輯）</h2>','<ul>']
for mo,slug,nday,nturn in links:
    idx.append(f'<li><strong>2026年{MONTH_ZH[mo[5:]]}</strong>：{nday} 天 · {nturn} 則 — <a href="/works/{slug}">/works/{slug}</a></li>')
idx.append('</ul>')
idx.append('<p style="color:#888">※ 全部對話亦標籤於 /ai-dialogues 分類「與克里須那對話」。</p>')
requests.patch(url+'?slug=eq.krishna-dialogues',headers=HR,
    data=json.dumps({'content_json':''.join(idx),'status':'草稿'},ensure_ascii=False).encode('utf-8'))
print('main index updated')
print('eng breakdown:')
from collections import Counter
print(Counter(r['eng'] for r in recs))
