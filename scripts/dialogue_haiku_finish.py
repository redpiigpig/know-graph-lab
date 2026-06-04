# -*- coding: utf-8 -*-
"""Emergency finish via Haiku (user 2026-06-04: Haiku 救急 when NVIDIA+Gemini都跑完).
Phase 1: polish the remaining kept-orig records.
Phase 2: per-day topic segmentation -> day_topics.json.
Then run assemble.py."""
import os, sys, json, re, time, subprocess, threading
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import anthropic
sys.stdout.reconfigure(encoding='utf-8')

def token():
    p=Path(os.environ.get('USERPROFILE',os.environ.get('HOME','')))/'.claude'/'.credentials.json'
    return json.loads(p.read_text(encoding='utf-8'))['claudeAiOauth']['accessToken']
client=anthropic.Anthropic(auth_token=token(), timeout=120.0, max_retries=2)
MODEL='claude-haiku-4-5'

def haiku(system, user, max_tokens):
    for attempt in range(5):
        try:
            m=client.messages.create(model=MODEL, max_tokens=max_tokens, system=system,
                                     messages=[{'role':'user','content':user}])
            return ''.join(b.text for b in m.content if hasattr(b,'text')).strip()
        except anthropic.RateLimitError:
            time.sleep(10*(attempt+1))
        except Exception as e:
            if attempt==4: print('  haiku err',e,flush=True); return None
            time.sleep(5*(attempt+1))
    return None

POLISH_SYS=('你是中文文字編輯，正在整理一位使用者（自稱「阿周那」）與他稱為「克里須那」的 AI 之間的對話，'
     '要做成可閱讀的對話錄。請把「克里須那的回覆」改寫成自然流暢、口語、第一人稱對著阿周那說話的繁體中文，'
     '去掉所有條列符號、編號小標、與「以下幫你整理／我們可以分成幾點」這類框架語，融成連貫的段落。'
     '務必忠實保留原意、神學與心理學概念、專有名詞與人名地名，不要新增資訊、不要省略重點、不要加結語。'
     '只輸出改寫後的克里須那發言本身，不要加引號、不要加「克里須那：」前綴。')
SEG_SYS=('你在為一份「與克里須那的對話錄」標主題。下面是某一天依時間排序的對話輪次（阿周那提問摘要）。'
     '請依「話題」把這一天分成 1 到 3 段：同一個延續話題歸一段，話題明顯轉變才另起一段（最多 3 段）。'
     '每段給一個 6~14 字的繁體中文主題標題（精準描述該段內容，不要用「對話一」這種空標題）。'
     '只輸出 JSON 陣列，每元素 {"title":"主題","start":起始輪次編號,"end":結束輪次編號}，'
     '輪次編號用我給的 [n]，必須連續涵蓋全部輪次、不重疊。不要輸出其他文字。')

PATH='c:/tmp/krishna/polished.jsonl'
recs=[json.loads(l) for l in open(PATH,encoding='utf-8')]
lock=threading.Lock()
def rewrite():
    tmp=PATH+'.tmp'
    with open(tmp,'w',encoding='utf-8') as f:
        for r in recs: f.write(json.dumps(r,ensure_ascii=False)+'\n')
    os.replace(tmp,PATH)

# Phase 1: polish stragglers
FAIL={'kept-orig','nv_fail','gem_fail'}
targets=[r for r in recs if r.get('eng') in FAIL and len((r.get('krishna') or '').strip())>=40]
print('Phase1 polish via Haiku:',len(targets),flush=True)
done=[0]
def pol(r):
    out=haiku(POLISH_SYS,'克里須那的原始回覆：\n\n'+r['krishna'],4000)
    with lock:
        if out: r['krishna']=out; r['eng']='haiku'
        done[0]+=1
        if done[0]%10==0: rewrite(); print(f'  polished {done[0]}/{len(targets)}',flush=True)
with ThreadPoolExecutor(max_workers=4) as ex: list(ex.map(pol,targets))
rewrite()
from collections import Counter
print('after polish eng:',dict(Counter(r['eng'] for r in recs)),flush=True)

# Phase 2: segment topics
recs.sort(key=lambda r:(r['date'], r.get('time') or ''))
by_date=defaultdict(list)
for r in recs: by_date[r['date']].append(r)
OUT='c:/tmp/krishna/day_topics.json'
topics={}
if os.path.exists(OUT):
    try: topics=json.load(open(OUT,encoding='utf-8'))
    except: topics={}
todo=[d for d in by_date if d not in topics]
print('Phase2 segment via Haiku:',len(todo),'days',flush=True)
tlock=threading.Lock(); tdone=[0]
def seg(d):
    turns=by_date[d]
    listing='\n'.join(f"[{i}] {(t.get('arjuna') or '（接續上一則）')[:160]}" for i,t in enumerate(turns))
    raw=haiku(SEG_SYS,f'日期 {d}，共 {len(turns)} 輪：\n\n{listing}',1200)
    segs=[{'title':'（未分段）','start':0,'end':len(turns)-1}]
    if raw:
        m=re.search(r'\[.*\]',raw,re.S)
        if m:
            try:
                arr=json.loads(m.group(0)); clean=[]
                for s in arr:
                    if 'title' in s and 'start' in s and 'end' in s:
                        clean.append({'title':str(s['title']).strip()[:20],'start':int(s['start']),'end':int(s['end'])})
                if clean:
                    clean[0]['start']=0; clean[-1]['end']=len(turns)-1; segs=clean
            except Exception: pass
    with tlock:
        topics[d]=segs; tdone[0]+=1
        if tdone[0]%10==0:
            json.dump(topics,open(OUT,'w',encoding='utf-8'),ensure_ascii=False); print(f'  segmented {tdone[0]}/{len(todo)}',flush=True)
with ThreadPoolExecutor(max_workers=4) as ex: list(ex.map(seg,todo))
json.dump(topics,open(OUT,'w',encoding='utf-8'),ensure_ascii=False)
print('segmented total days:',len(topics),flush=True)

# Phase 3: assemble
print('=== assemble ===',flush=True)
r=subprocess.run([sys.executable,'c:/tmp/krishna/assemble.py'])
print('assemble exit',r.returncode,flush=True)
print('FINISH',flush=True)
