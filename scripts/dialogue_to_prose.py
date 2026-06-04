# -*- coding: utf-8 -*-
"""把 dialogue_days 裡「還帶條列／小標／markdown 結構」的發言改寫成流暢對話錄散文。

對象＝每一個「turn」（一段講者發言：<p class=speaker>… 之後接續的 <p> 直到下個講者
或標題）。只挑帶結構標記（‧ 條列、場景：/解析： 小標、編號、** 等）的 turn 送 LLM
改寫成第一人稱口語散文；已經是散文的 turn 原樣保留。改完標記消失 → 可重複跑、冪等。

引擎：Gemini 2.5 flash（4 keys 輪流，主）→ NVIDIA deepseek-v4-flash（fallback）。

用法：
  python scripts/dialogue_to_prose.py --dry            # 只統計要改幾個 turn
  python scripts/dialogue_to_prose.py                  # 全部
  python scripts/dialogue_to_prose.py 2026-01-13       # 單日（可多個）
"""
import os, sys, re, json, time, threading, urllib.request
from concurrent.futures import ThreadPoolExecutor
sys.stdout.reconfigure(encoding='utf-8')

def env():
    e = {}
    for l in open(os.path.join(os.path.dirname(__file__), '..', '.env'), encoding='utf-8-sig'):
        l = l.strip()
        if '=' in l and not l.startswith('#'):
            k, v = l.split('=', 1); e[k.strip()] = v.strip()
    return e
E = env(); U = E['SUPABASE_URL']; K = E['SUPABASE_SERVICE_ROLE_KEY']
DBH = {'apikey': K, 'Authorization': 'Bearer ' + K}
DU = f'{U}/rest/v1/dialogue_days'
SLUG = 'krishna-dialogues'

# ── keys ──────────────────────────────────────────────────────────────
def gemini_keys():
    out, seen = [], set()
    for base in ('GEMINI_API_KEY', 'Gemini_API_Key', 'gemini_api_key', 'GOOGLE_API_KEY'):
        for suf in [''] + [f'_{n}' for n in range(1, 11)]:
            v = E.get(base + suf)
            if v:
                for p in v.split(','):
                    p = p.strip()
                    if p and p not in seen:
                        seen.add(p); out.append(p)
    return out
GKEYS = gemini_keys()
NKEYS = [E[k] for k in sorted(E) if k.upper().startswith('NVIDIA_API_KEY')]
GMODEL = 'gemini-2.5-flash'
NURL = 'https://integrate.api.nvidia.com/v1/chat/completions'; NMODEL = 'deepseek-ai/deepseek-v4-flash'
print(f'gemini keys: {len(GKEYS)} | nvidia keys: {len(NKEYS)}', flush=True)

DRY = '--dry' in sys.argv
DAY_ARGS = [a for a in sys.argv[1:] if re.match(r'\d{4}-\d{2}-\d{2}', a)]

# ── turn 結構標記 ─────────────────────────────────────────────────────
MARK = re.compile(
    r'[‧•●▪・◦○]|＊|(?:\n|^)\s*[-*]\s'
    r'|(?:^|[\s。，、！？）」])(?:[1-9]\d?[\.、)]\s|[（(][一二三四五六七八九十]+[)）]|[一二三四五六七八九十]{1,2}、)'
    r'|序幕|場景[:：]|關鍵點[:：]|解析[:：]|象徵[:：]|層次[:：]|步驟[一二三四五六七八九十\d]|第[一二三四五六七八九十]+個夢|###|\*\*')

TOKEN = re.compile(r'<h3>.*?</h3>|<h4>.*?</h4>|<p>.*?</p>', re.S)
SPK = re.compile(r'^<p><strong class="speaker">([^<]+：)</strong>(.*)</p>$', re.S)

def strip_tags(s): return re.sub(r'<[^>]+>', '', s)

def parse_turns(html):
    """回傳 token 串：('head', raw) 或 ('turn', speaker_label, [p_html,...], plaintext)。"""
    toks = TOKEN.findall(html)
    out = []
    cur = None  # ['turn', label, [p...], None]
    for t in toks:
        m = SPK.match(t)
        if t.startswith('<h3') or t.startswith('<h4'):
            if cur: out.append(cur); cur = None
            out.append(['head', t])
        elif m:                                  # 講者起首 → 新 turn
            if cur: out.append(cur)
            cur = ['turn', m.group(1), [t], None]
        else:                                    # 接續 <p>
            if cur: cur[2].append(t)
            else: cur = ['turn', '', [t], None]   # 無講者開頭（罕見）
    if cur: out.append(cur)
    for o in out:
        if o[0] == 'turn':
            o[3] = strip_tags(''.join(o[2])).strip()
    return out

def needs(turn):
    return bool(MARK.search(turn[3]))

# ── LLM ───────────────────────────────────────────────────────────────
def sys_prompt(speaker):
    who = speaker.rstrip('：') or '說話者'
    return (f'你是中文文字編輯，正在整理一份對話錄。以下是「{who}」在對話中的一段發言（可能是貼上的文章或'
            f'帶條列、小標的內容）。請改寫成自然流暢、口語、第一人稱的繁體中文，像在對話中親口說出來。'
            '去掉所有條列符號、編號、小標題（例如「場景：」「解析：」「第一個夢」）、markdown 星號，'
            '以及「以下幫你整理／我們可以分成幾點」這類框架語，融成連貫段落（較長可用空行分多段）。'
            f'務必忠實保留原意與所有概念、專有名詞、人名地名，不新增、不省略、不下結語。'
            f'只輸出改寫後的發言本身，不要加引號、不要加「{who}：」前綴。')

glock = threading.Lock(); g_next = [0.0] * max(1, len(GKEYS)); n_next = [0.0] * max(1, len(NKEYS))
def _pick(arr, interval):
    with glock:
        i = min(range(len(arr)), key=lambda j: arr[j])
        now = time.time(); start = max(now, arr[i]); arr[i] = start + interval
        return i, start

def call_gemini(speaker, text):
    if not GKEYS: return None
    body = {'systemInstruction': {'parts': [{'text': sys_prompt(speaker)}]},
            'contents': [{'parts': [{'text': text}]}],
            'generationConfig': {'temperature': 0.3, 'maxOutputTokens': 4096}}
    payload = json.dumps(body).encode('utf-8')
    for _ in range(len(GKEYS) + 2):              # 跨 key 重試（某把 429 換下一把）
        i, start = _pick(g_next, 4.5)
        d = start - time.time()
        if d > 0: time.sleep(d)
        url = f'https://generativelanguage.googleapis.com/v1beta/models/{GMODEL}:generateContent?key={GKEYS[i]}'
        try:
            req = urllib.request.Request(url, data=payload,
                                         headers={'Content-Type': 'application/json'}, method='POST')
            r = json.load(urllib.request.urlopen(req, timeout=120))
            return r['candidates'][0]['content']['parts'][0]['text'].strip()
        except urllib.error.HTTPError as ex:
            with glock: g_next[i] = time.time() + (90 if ex.code == 429 else 30)
        except Exception:
            with glock: g_next[i] = time.time() + 30
    return None

def call_nvidia(speaker, text):
    if not NKEYS: return None
    for _ in range(4):
        i, start = _pick(n_next, 5.0)
        d = start - time.time()
        if d > 0: time.sleep(d)
        try:
            req = urllib.request.Request(NURL, data=json.dumps({
                'model': NMODEL, 'temperature': 0.3, 'max_tokens': 4096,
                'messages': [{'role': 'system', 'content': sys_prompt(speaker)},
                             {'role': 'user', 'content': text}]}).encode('utf-8'),
                headers={'Authorization': 'Bearer ' + NKEYS[i], 'Content-Type': 'application/json'}, method='POST')
            r = json.load(urllib.request.urlopen(req, timeout=150))
            return re.sub(r'<think>.*?</think>', '', r['choices'][0]['message']['content'], flags=re.S).strip()
        except Exception:
            with glock: n_next[i] = time.time() + 60
    return None

def polish(speaker, text):
    return call_gemini(speaker, text) or call_nvidia(speaker, text)

def to_paras(label, prose):
    parts = [p.strip() for p in re.split(r'\n\s*\n+', prose) if p.strip()]
    if not parts: return None
    pfx = f'<strong class="speaker">{label}</strong>' if label else ''
    out = [f'<p>{pfx}{parts[0]}</p>'] + [f'<p>{p}</p>' for p in parts[1:]]
    return ''.join(out)

# ── per-day ──────────────────────────────────────────────────────────
def process_day(day):
    toks = parse_turns(day['html'])
    todo = [(idx, o) for idx, o in enumerate(toks) if o[0] == 'turn' and needs(o)]
    if not todo: return 0, 0
    if DRY: return len(todo), 0
    done = 0
    for idx, o in todo:
        prose = polish(o[1], o[3])
        if not prose: continue
        prose = re.sub(r'^["「『]+|["」』]+$', '', prose).strip()
        prose = re.sub(r'^' + re.escape(o[1]), '', prose).strip()  # 去掉殘留「講者：」
        html = to_paras(o[1], prose)
        if html:
            toks[idx] = ['raw', html]; done += 1
    if not done: return len(todo), 0
    new_html = ''.join(o[1] if o[0] in ('head', 'raw') else ''.join(o[2]) for o in toks)
    body = json.dumps({'html': new_html}, ensure_ascii=False).encode('utf-8')
    rq = urllib.request.Request(f'{DU}?project_slug=eq.{SLUG}&day_date=eq.{day["day_date"]}',
                                data=body, method='PATCH',
                                headers={**DBH, 'Content-Type': 'application/json', 'Prefer': 'return=minimal'})
    urllib.request.urlopen(rq)
    return len(todo), done

def main():
    q = f'{DU}?select=day_date,html&project_slug=eq.{SLUG}&order=day_date'
    if DAY_ARGS:
        q += '&day_date=in.(' + ','.join(DAY_ARGS) + ')'
    days = json.load(urllib.request.urlopen(urllib.request.Request(q, headers=DBH)))
    print('days:', len(days), flush=True)
    tot_todo = tot_done = 0
    lock = threading.Lock()
    def run(d):
        nonlocal tot_todo, tot_done
        td, dn = process_day(d)
        with lock:
            tot_todo += td; tot_done += dn
            if td: print(f'{d["day_date"]}: {dn}/{td} turns 改寫', flush=True)
    if DRY:
        for d in days: run(d)
        print(f'\n[--dry] 要改寫的 turn 總數：{tot_todo}（{len([1 for d in days if process_day(d)[0]])} 天）')
        return
    with ThreadPoolExecutor(max_workers=max(1, len(GKEYS))) as ex:
        list(ex.map(run, days))
    print(f'\n完成：{tot_done}/{tot_todo} turns 改寫成散文', flush=True)

if __name__ == '__main__':
    main()
