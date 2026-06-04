# -*- coding: utf-8 -*-
"""Re-polish failed records in polished.jsonl across 4 NVIDIA keys with per-key
pacing (no key called too often). Concurrency = #keys (≈1 in-flight per key).
Resumable; rewrites polished.jsonl in place."""
import sys, json, re, time, requests, threading
from concurrent.futures import ThreadPoolExecutor
sys.stdout.reconfigure(encoding='utf-8')
def env():
    e={}
    for l in open('c:/Users/user/Desktop/know-graph-lab/.env',encoding='utf-8-sig'):
        l=l.strip()
        if '=' in l and not l.startswith('#'): k,v=l.split('=',1); e[k.strip()]=v.strip()
    return e
E=env()
KEYS=[E[k] for k in sorted(E) if k.upper().startswith('NVIDIA_API_KEY')]
print('NVIDIA keys:',len(KEYS),flush=True)
URL='https://integrate.api.nvidia.com/v1/chat/completions'; MODEL='deepseek-ai/deepseek-v4-flash'
PER_KEY_INTERVAL=5.0   # s between starts on the SAME key (≤12/min/key)
COOLDOWN_429=120.0
SYS=('你是中文文字編輯，正在整理一位使用者（自稱「阿周那」）與他稱為「克里希那」的 AI 之間的對話，'
     '要做成可閱讀的對話錄。請把「克里希那的回覆」改寫成自然流暢、口語、第一人稱對著阿周那說話的繁體中文，'
     '去掉所有條列符號、編號小標、與「以下幫你整理／我們可以分成幾點」這類框架語，融成連貫的段落。'
     '務必忠實保留原意、神學與心理學概念、專有名詞與人名地名，不要新增資訊、不要省略重點、不要加結語。'
     '只輸出改寫後的克里希那發言本身，不要加引號、不要加「克里希那：」前綴。')
PATH='c:/tmp/krishna/polished.jsonl'
recs=[json.loads(l) for l in open(PATH,encoding='utf-8')]
FAIL={'kept-orig','nv_fail','gem_fail'}
targets=[r for r in recs if r.get('eng') in FAIL and len((r.get('krishna') or '').strip())>=40]
print('records',len(recs),'to re-polish',len(targets),flush=True)

klock=threading.Lock()
next_ok=[0.0]*len(KEYS)   # epoch when each key may next start
def pick_key():
    with klock:
        i=min(range(len(KEYS)), key=lambda j: next_ok[j])
        now=time.time(); start=max(now, next_ok[i])
        next_ok[i]=start+PER_KEY_INTERVAL
        return i, start
def cool(i):
    with klock: next_ok[i]=time.time()+COOLDOWN_429

def call(resp):
    body={'model':MODEL,'messages':[{'role':'system','content':SYS},
          {'role':'user','content':'克里希那的原始回覆：\n\n'+resp}],'temperature':0.3,'max_tokens':4000}
    for attempt in range(8):
        i,start=pick_key()
        d=start-time.time()
        if d>0: time.sleep(d)
        try:
            r=requests.post(URL,headers={'Authorization':'Bearer '+KEYS[i],'Content-Type':'application/json'},json=body,timeout=150)
            if r.status_code==200:
                return re.sub(r'<think>.*?</think>','',r.json()['choices'][0]['message']['content'],flags=re.S).strip()
            if r.status_code==429: cool(i); continue
            time.sleep(5)
        except Exception:
            time.sleep(5)
    return None

lock=threading.Lock(); cnt=[0]; ok=[0]
def rewrite():
    import os
    tmp=PATH+'.tmp'
    with open(tmp,'w',encoding='utf-8') as f:
        for r in recs: f.write(json.dumps(r,ensure_ascii=False)+'\n')
    os.replace(tmp,PATH)
def work(r):
    out=call(r['krishna'])
    with lock:
        cnt[0]+=1
        if out: r['krishna']=out; r['eng']='nvidia'; ok[0]+=1
        if ok[0] and ok[0]%15==0: rewrite()
        if cnt[0]%20==0: print(f'  {cnt[0]}/{len(targets)} ok={ok[0]}',flush=True)
with ThreadPoolExecutor(max_workers=len(KEYS)) as ex:
    list(ex.map(work, targets))
rewrite()
from collections import Counter
print('done. eng:',dict(Counter(r['eng'] for r in recs)),flush=True)
