# -*- coding: utf-8 -*-
"""把 dialogue_days 的對話重鑄成「哲學家對話錄」語體（風格升級，非僅去條列）。

兩種 register，逐 turn 改寫：
  ‧ 克里希那（AI）  → 大膽再創作：凝練、有韻致、富哲思，砍冗、抓核心洞見重講一遍。
  ‧ 阿周那（使用者）→ 輕度整理：貼合本人語氣與第一人稱聲音，只去贅字／凌亂，不美化不詩化。

對象＝每一個「turn」（一段講者發言：<p class=speaker>… 後接續的 <p> 直到下個講者或標題）。
與 dialogue_to_prose.py 不同：本腳本**改寫每一個 turn**（不只帶結構標記的），所以是一次性的
全篇風格升級。為避免重複跑時把已詩化的文字越改越飄，用 **per-day ledger 冪等**
（c:/tmp/krishna/recompose_done.json 記已完成日期；--redo 忽略 ledger）。

引擎：Gemini 2.5 flash（4 keys 輪流，主）→ NVIDIA deepseek-v4-flash（fallback）。
見 [[feedback_engine_nvidia_no_haiku]]。

用法：
  python scripts/dialogue_recompose.py --dry          # 只統計天數/turn 數，不改
  python scripts/dialogue_recompose.py                # 全部（跳過 ledger 已完成）
  python scripts/dialogue_recompose.py 2026-01-13     # 單日（可多個；忽略 ledger）
  python scripts/dialogue_recompose.py --redo         # 全部重做，忽略 ledger
"""
import os, sys, re, json, time, threading, urllib.request, urllib.error
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
LEDGER = 'c:/tmp/krishna/recompose_done.json'

# persona 對照（依場合換串時改這裡）：誰是 AI（大膽再創作）、誰是使用者（輕度整理）
AI_NAME = '克里希那'
USER_NAME = '阿周那'

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
print(f'gemini keys: {len(GKEYS)} | nvidia keys: {len(NKEYS)} | haiku: {"ON(主)" if "--haiku" in sys.argv else "off"}', flush=True)

DRY = '--dry' in sys.argv
REDO = '--redo' in sys.argv
HAIKU = '--haiku' in sys.argv     # 主引擎用 Haiku（Claude OAuth/Max 額度，不撞 Gemini/NVIDIA 配額）
DAY_ARGS = [a for a in sys.argv[1:] if re.match(r'\d{4}-\d{2}-\d{2}', a)]

# ── Haiku（Claude OAuth，Max 額度；使用者 2026-06-05 指定用 Haiku 額度跑此重批）──
_hclient = None
def haiku_client():
    global _hclient
    if _hclient is None:
        import anthropic
        from pathlib import Path
        cred = Path(os.environ.get('USERPROFILE', os.environ.get('HOME', ''))) / '.claude' / '.credentials.json'
        tok = json.loads(cred.read_text(encoding='utf-8'))['claudeAiOauth']['accessToken']
        _hclient = anthropic.Anthropic(auth_token=tok, timeout=150.0, max_retries=2)
    return _hclient
HMODEL = 'claude-haiku-4-5'
def call_haiku(label, text):
    import anthropic
    cli = haiku_client()
    for attempt in range(5):
        try:
            m = cli.messages.create(model=HMODEL, max_tokens=8192, system=sys_prompt(label),
                                    messages=[{'role': 'user', 'content': text}])
            return ''.join(b.text for b in m.content if hasattr(b, 'text')).strip()
        except anthropic.RateLimitError:
            time.sleep(8 * (attempt + 1))
        except Exception:
            if attempt == 4: return None
            time.sleep(4 * (attempt + 1))
    return None

# ── turn 解析（與 dialogue_to_prose 同）──────────────────────────────
TOKEN = re.compile(r'<h3>.*?</h3>|<h4>.*?</h4>|<p>.*?</p>', re.S)
# 講者起首段：class="speaker" 後可帶屬性（如 data-rc="1" 標記已重鑄）。
SPK = re.compile(r'^<p><strong class="speaker"([^>]*)>([^<]+：)</strong>(.*)</p>$', re.S)
def strip_tags(s): return re.sub(r'<[^>]+>', '', s)

def parse_turns(html):
    """回傳 token 串：['head', raw] 或 ['turn', label, [p_html...], plaintext, done]。
    done=True 表示該 turn 已重鑄（speaker 帶 data-rc="1"）→ 跳過，逐 turn 冪等。"""
    toks = TOKEN.findall(html); out = []; cur = None
    for t in toks:
        m = SPK.match(t)
        if t.startswith('<h3') or t.startswith('<h4'):
            if cur: out.append(cur); cur = None
            out.append(['head', t])
        elif m:
            if cur: out.append(cur)
            cur = ['turn', m.group(2), [t], None, ('data-rc' in m.group(1))]
        else:
            if cur: cur[2].append(t)
            else: cur = ['turn', '', [t], None, False]
    if cur: out.append(cur)
    for o in out:
        if o[0] == 'turn':
            o[3] = strip_tags(''.join(o[2])).strip()
    return out

# ── 兩種 register 的 system prompt ────────────────────────────────────
def sys_ai():
    # 2026-06-12 改版：舊版「大膽再創作詩意」把克里須那洗成通篇紫色辭藻、把實質內容抽掉。
    # 使用者一月手工稿才是要的風格＝清晰溫暖的散文、保留完整論點與專名、只去結構與客套、不堆砌詩化。
    return (
        f'你正在整理一份個人心靈對話錄。以下是 AI（在對話裡被稱為「{AI_NAME}」，一位博學而溫暖的'
        f'榮格派心靈導師、《薄伽梵歌》式的智者）對「{USER_NAME}」說的一段話。請重寫成流暢、溫暖、'
        '清晰的散文：\n'
        '‧ **保留它完整的論點、解釋、舉例與所有概念與專有名詞**（榮格心理學／神學／神話／哲學的實質內容必須留住，'
        '不可抽掉、不可把具體內容洗成空泛比喻）。\n'
        f'‧ 第一人稱、溫暖地對「{USER_NAME}」說話，像智者娓娓道來；可用一兩個貼切而具體的意象，'
        '但**不要通篇堆砌詩化辭藻、不要為美而美**。寧可把道理講清楚，也不要犧牲內容去換漂亮句子。\n'
        '‧ 去掉條列、編號、小標題、markdown 星號，以及「這是個好問題／讓我們來解讀／首先…接著…／'
        '總結來說／我們可以分成幾點」這類框架語與客套，融成連貫段落。\n'
        '‧ 忠實：不扭曲立場、不新增他沒講的主張、不刪實質內容。\n'
        f'只輸出{AI_NAME}這段重寫後的話本身，不要加引號、不要加「{AI_NAME}：」前綴、不要任何說明。')

def sys_user():
    return (
        f'你正在整理一份哲學對話錄。以下是對話者「{USER_NAME}」（這是使用者本人）說的一段話——'
        '可能是即時打字、夾雜情緒與碎念，或貼上的長段文字。\n'
        '請把它整理成對話錄裡自然的一段發言，原則是「貼合他本人的語氣，但讀起來像對話錄」：\n'
        '‧ 保留他的第一人稱聲音、用詞習慣、坦白與情緒——這是他的話，不是你的話。\n'
        '‧ 只做輕度整理：去掉贅字、語病、重複與純打字的凌亂，把口語碎句連成通順的句子。\n'
        '‧ 不要美化、不要詩化、不要替他講得更漂亮或更有學問，不要加入他沒說過的想法。\n'
        '‧ 去掉條列、編號、markdown 星號，融成連貫段落。\n'
        f'只輸出整理後{USER_NAME}這段話本身，不加引號、不加「{USER_NAME}：」前綴。')

def sys_prompt(label):
    who = (label or '').rstrip('：')
    return sys_user() if who == USER_NAME else sys_ai()

# ── LLM（多 key 輪流＋節流；Gemini 主、NVIDIA fallback）──────────────
glock = threading.Lock(); g_next = [0.0] * max(1, len(GKEYS)); n_next = [0.0] * max(1, len(NKEYS))
def _pick(arr, interval):
    with glock:
        i = min(range(len(arr)), key=lambda j: arr[j])
        now = time.time(); start = max(now, arr[i]); arr[i] = start + interval
        return i, start

def call_gemini(label, text):
    if not GKEYS: return None
    body = {'systemInstruction': {'parts': [{'text': sys_prompt(label)}]},
            'contents': [{'parts': [{'text': text}]}],
            'generationConfig': {'temperature': 0.4, 'maxOutputTokens': 8192}}
    payload = json.dumps(body).encode('utf-8')
    for _ in range(len(GKEYS) + 2):
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

def call_nvidia(label, text):
    if not NKEYS: return None
    for _ in range(4):
        i, start = _pick(n_next, 5.0)
        d = start - time.time()
        if d > 0: time.sleep(d)
        try:
            req = urllib.request.Request(NURL, data=json.dumps({
                'model': NMODEL, 'temperature': 0.4, 'max_tokens': 8192,
                'messages': [{'role': 'system', 'content': sys_prompt(label)},
                             {'role': 'user', 'content': text}]}).encode('utf-8'),
                headers={'Authorization': 'Bearer ' + NKEYS[i], 'Content-Type': 'application/json'}, method='POST')
            r = json.load(urllib.request.urlopen(req, timeout=150))
            return re.sub(r'<think>.*?</think>', '', r['choices'][0]['message']['content'], flags=re.S).strip()
        except Exception:
            with glock: n_next[i] = time.time() + 60
    return None

def recompose(label, text):
    if HAIKU:
        return call_haiku(label, text) or call_gemini(label, text) or call_nvidia(label, text)
    return call_gemini(label, text) or call_nvidia(label, text)

def to_paras(label, prose):
    parts = [p.strip() for p in re.split(r'\n\s*\n+', prose) if p.strip()]
    if not parts: return None
    # data-rc="1"＝已重鑄標記，供 parse_turns 偵測並跳過（逐 turn 冪等）。
    pfx = f'<strong class="speaker" data-rc="1">{label}</strong>' if label else ''
    out = [f'<p>{pfx}{parts[0]}</p>'] + [f'<p>{p}</p>' for p in parts[1:]]
    return ''.join(out)

# ── ledger ────────────────────────────────────────────────────────────
def load_ledger():
    try: return set(json.load(open(LEDGER, encoding='utf-8')))
    except Exception: return set()
def save_ledger(done):
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    tmp = LEDGER + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(sorted(done), f, ensure_ascii=False)
    os.replace(tmp, LEDGER)

# ── per-day ──────────────────────────────────────────────────────────
def process_day(day):
    toks = parse_turns(day['html'])
    # 只挑「有內容且尚未重鑄」的 turn（o[4]=done 標記）→ 逐 turn 冪等，re-run 不碰已重鑄
    turns = [(idx, o) for idx, o in enumerate(toks) if o[0] == 'turn' and o[3] and not o[4]]
    if not turns: return 0, 0
    if DRY: return len(turns), 0
    done = 0
    for idx, o in turns:
        prose = recompose(o[1], o[3])
        if not prose: continue
        prose = re.sub(r'^["「『]+|["」』]+$', '', prose).strip()
        prose = re.sub(r'^' + re.escape(o[1].rstrip('：')) + r'[：:]\s*', '', prose).strip()
        html = to_paras(o[1], prose)
        if html:
            toks[idx] = ['raw', html]; done += 1
    if not done: return len(turns), 0
    new_html = ''.join(o[1] if o[0] in ('head', 'raw') else ''.join(o[2]) for o in toks)
    body = json.dumps({'html': new_html}, ensure_ascii=False).encode('utf-8')
    rq = urllib.request.Request(f'{DU}?project_slug=eq.{SLUG}&day_date=eq.{day["day_date"]}',
                                data=body, method='PATCH',
                                headers={**DBH, 'Content-Type': 'application/json', 'Prefer': 'return=minimal'})
    urllib.request.urlopen(rq)
    return len(turns), done

def main():
    q = f'{DU}?select=day_date,html&project_slug=eq.{SLUG}&order=day_date'
    if DAY_ARGS:
        q += '&day_date=in.(' + ','.join(DAY_ARGS) + ')'
    days = json.load(urllib.request.urlopen(urllib.request.Request(q, headers=DBH)))
    ledger = set() if (DAY_ARGS or REDO) else load_ledger()
    if ledger:
        days = [d for d in days if d['day_date'] not in ledger]
    print(f'days to recompose: {len(days)} (ledger skip {len(ledger)})', flush=True)

    if DRY:
        tot = 0
        for d in days:
            td, _ = process_day(d); tot += td
        print(f'[--dry] turns to recompose: {tot}（{len(days)} 天）')
        return

    lock = threading.Lock(); tot_turns = [0]; tot_done = [0]; done_dates = set(ledger)
    def run(d):
        td, dn = process_day(d)
        with lock:
            tot_turns[0] += td; tot_done[0] += dn
            # 只在整天的待重鑄 turn 全數成功（含 td==0 全已重鑄）才記 ledger；
            # 部分失敗（配額耗盡 fallback 也掛）不記 → 下次 run 自動補（逐 turn 標記跳過已成功的）
            if not DAY_ARGS and dn == td:
                done_dates.add(d['day_date']); save_ledger(done_dates)
            flag = '' if dn == td else '  ⚠ 部分失敗，未記 ledger（待補）'
            print(f'{d["day_date"]}: {dn}/{td} turns 重鑄{flag}', flush=True)
    workers = 8 if HAIKU else max(1, len(GKEYS))   # Haiku/Max 額度可較高並發
    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(run, days))
    print(f'\n完成：{tot_done[0]}/{tot_turns[0]} turns 重鑄', flush=True)

if __name__ == '__main__':
    main()
