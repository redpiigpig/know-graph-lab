# -*- coding: utf-8 -*-
"""Per-day topic segmentation: read polished.jsonl, group by date, ask NVIDIA to
split each day's turns into 1-3 topical segments with 6-14 char 繁中 titles.
Writes day_topics.json: {date: [{"title":..., "start":i, "end":j}]}. Resumable."""
import os, sys, json, re, time, requests
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import threading
sys.stdout.reconfigure(encoding='utf-8')
def env():
    e={}
    for l in open('c:/Users/user/Desktop/know-graph-lab/.env',encoding='utf-8-sig'):
        l=l.strip()
        if '=' in l and not l.startswith('#'):
            k,v=l.split('=',1); e[k.strip()]=v.strip()
    return e
E=env()
KEYS=[E[k] for k in sorted(E) if k.upper().startswith('NVIDIA_API_KEY')]
URL='https://integrate.api.nvidia.com/v1/chat/completions'; MODEL='deepseek-ai/deepseek-v4-flash'
PER_KEY_INTERVAL=5.0; COOLDOWN_429=120.0
_klock=threading.Lock(); _next=[0.0]*len(KEYS)
def _pick():
    with _klock:
        i=min(range(len(KEYS)),key=lambda j:_next[j]); now=time.time()
        start=max(now,_next[i]); _next[i]=start+PER_KEY_INTERVAL; return i,start
def _cool(i):
    with _klock: _next[i]=time.time()+COOLDOWN_429

recs=[json.loads(l) for l in open('c:/tmp/krishna/polished.jsonl',encoding='utf-8')]
recs.sort(key=lambda r:(r['date'], r.get('time') or ''))
by_date=defaultdict(list)
for r in recs: by_date[r['date']].append(r)

OUT='c:/tmp/krishna/day_topics.json'
done={}
if os.path.exists(OUT):
    try: done=json.load(open(OUT,encoding='utf-8'))
    except: done={}

SYS=('你在為一份「與克里須那的對話錄」標主題。下面是某一天依時間排序的對話輪次（阿周那提問摘要）。'
     '請依「話題」把這一天分成 1 到 3 段：同一個延續話題歸一段，話題明顯轉變才另起一段（最多 3 段）。'
     '每段給一個 6~14 字的繁體中文主題標題（精準描述該段內容，不要用「對話一」這種空標題）。'
     '只輸出 JSON 陣列，每元素 {"title":"主題","start":起始輪次編號,"end":結束輪次編號}，'
     '輪次編號用我給的 [n]，必須連續涵蓋全部輪次、不重疊。不要輸出其他文字。')

def segment(date, turns):
    listing='\n'.join(f"[{i}] {(t.get('arjuna') or '（接續上一則）')[:160]}" for i,t in enumerate(turns))
    body={'model':MODEL,'messages':[{'role':'system','content':SYS},
          {'role':'user','content':f'日期 {date}，共 {len(turns)} 輪：\n\n{listing}'}],
          'temperature':0.2,'max_tokens':1200}
    for attempt in range(8):
        i,start=_pick()
        d=start-time.time()
        if d>0: time.sleep(d)
        try:
            r=requests.post(URL,headers={'Authorization':'Bearer '+KEYS[i],'Content-Type':'application/json'},json=body,timeout=120)
            if r.status_code==429: _cool(i); continue
            if r.status_code==200:
                txt=r.json()['choices'][0]['message']['content']
                txt=re.sub(r'<think>.*?</think>','',txt,flags=re.S)
                m=re.search(r'\[.*\]',txt,re.S)
                if m:
                    segs=json.loads(m.group(0))
                    # validate/repair
                    clean=[]
                    for s in segs:
                        if 'title' in s and 'start' in s and 'end' in s:
                            clean.append({'title':str(s['title']).strip()[:20],
                                          'start':int(s['start']),'end':int(s['end'])})
                    if clean:
                        clean[0]['start']=0; clean[-1]['end']=len(turns)-1
                        return clean
            elif r.status_code in (429,503): time.sleep(5*(attempt+1)); continue
        except Exception: time.sleep(3*(attempt+1))
    # fallback: single segment
    return [{'title':'（未分段）','start':0,'end':len(turns)-1}]

lock=threading.Lock()
todo=[d for d in by_date if d not in done]
print('days total',len(by_date),'todo',len(todo),flush=True)
def work(d):
    segs=segment(d, by_date[d])
    with lock:
        done[d]=segs
        json.dump(done,open(OUT,'w',encoding='utf-8'),ensure_ascii=False,indent=0)
    return d
with ThreadPoolExecutor(max_workers=6) as ex:
    for i,d in enumerate(ex.map(work, todo),1):
        if i%10==0: print(f'  {i}/{len(todo)}',flush=True)
print('DONE topics for',len(done),'days',flush=True)
