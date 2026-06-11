# -*- coding: utf-8 -*-
"""從 raw（ai_dialogues_gemini）＋日記範圍 membership 重建 dialogue_days，乾淨散文風格。

背景（2026-06-12）：
  ① 舊 dialogue_days 是從「600 多則的廣集」組出來的，收了很多不屬於此對話的條目（使用者指出）。
  ② 克里須那回覆被舊 recompose 弄得過度詩化。
故從**原始來源**重建：membership 用日記範圍 final_manuscript.json（已去除非屬條目），
每則 IN raw row → 阿周那＝prompt 輕度整理；克里須那＝**raw response** 重寫成乾淨散文
（保留完整論點與專名、去條列/客套、不堆砌詩化；prompt 與 dialogue_recompose 同步）。

一月 1/13–1/18 已用手工 docx 直接灌（更好），本腳本只跑 1/19–4/18。
0 則 IN 的日子＝無日記內容 → 從 dialogue_days 刪除（--write 時）。
引擎 Gemini→NVIDIA；--haiku 走 Claude Max。可 resume（ledger）。
用法：
  python scripts/dialogue_rebuild_from_raw.py 2026-01-23 --haiku --dry   # 單日預覽
  python scripts/dialogue_rebuild_from_raw.py --haiku                    # 全 1/19–4/18 重建+刪空白日
"""
import os, sys, re, json, time, html, threading, datetime, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

SLUG = 'krishna-dialogues'
AI, USER = '克里須那', '阿周那'
WD = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五', 6: '六', 7: '日'}
START, END = '2026-01-19', '2026-04-18'
TMP = 'c:/tmp/krishna'
LEDGER = os.path.join(TMP, 'rebuild_done.json')
MEMBERSHIP = os.path.join(TMP, 'final_manuscript.json')

def env():
    e = {}
    for l in open(os.path.join(os.path.dirname(__file__), '..', '.env'), encoding='utf-8-sig'):
        l = l.strip()
        if '=' in l and not l.startswith('#'):
            k, v = l.split('=', 1); e[k.strip()] = v.strip()
    return e
E = env(); U = E['SUPABASE_URL']; K = E['SUPABASE_SERVICE_ROLE_KEY']
DBH = {'apikey': K, 'Authorization': 'Bearer ' + K}

def gemini_keys():
    out, seen = [], set()
    for base in ('GEMINI_API_KEY', 'Gemini_API_Key', 'gemini_api_key', 'GOOGLE_API_KEY'):
        for suf in [''] + [f'_{n}' for n in range(1, 11)]:
            v = E.get(base + suf)
            if v:
                for p in v.split(','):
                    p = p.strip()
                    if p and p not in seen: seen.add(p); out.append(p)
    return out
GKEYS = gemini_keys(); NKEYS = [E[k] for k in sorted(E) if k.upper().startswith('NVIDIA_API_KEY')]
GMODEL = 'gemini-2.5-flash'; NURL = 'https://integrate.api.nvidia.com/v1/chat/completions'; NMODEL = 'deepseek-ai/deepseek-v4-flash'
HAIKU = '--haiku' in sys.argv; DRY = '--dry' in sys.argv
DAY_ARGS = [a for a in sys.argv[1:] if re.match(r'\d{4}-\d{2}-\d{2}$', a)]
print(f'gemini {len(GKEYS)} | nvidia {len(NKEYS)} | haiku {"ON" if HAIKU else "off"}', flush=True)

# ── prompts（與 dialogue_recompose sys_ai/sys_user 同步：乾淨散文、保留實質、不堆砌詩化）──
def sys_ai():
    return (
        f'你正在整理一份個人心靈對話錄。以下是 AI（在對話裡被稱為「{AI}」，一位博學而溫暖的'
        f'榮格派心靈導師、《薄伽梵歌》式的智者）對「{USER}」說的一段回覆。請重寫成流暢、溫暖、清晰的散文：\n'
        '‧ **保留它完整的論點、解釋、舉例與所有概念與專有名詞**（榮格心理學／神學／神話／哲學的實質內容必須留住，'
        '不可抽掉、不可把具體內容洗成空泛比喻）。\n'
        f'‧ 第一人稱、溫暖地對「{USER}」說話，像智者娓娓道來；可用一兩個貼切而具體的意象，'
        '但**不要通篇堆砌詩化辭藻、不要為美而美**。寧可把道理講清楚，也不要犧牲內容去換漂亮句子。\n'
        '‧ 去掉條列、編號、小標題、markdown 星號，以及「這是個好問題／讓我們來解讀／首先…接著…／'
        '總結來說／我們可以分成幾點」這類框架語與客套，融成連貫段落。\n'
        '‧ 忠實：不扭曲立場、不新增他沒講的主張、不刪實質內容。\n'
        f'只輸出{AI}這段重寫後的話本身，不加引號、不加「{AI}：」前綴、不加任何說明。')

def sys_user():
    return (
        f'你在整理一份個人心靈對話錄。以下是對話者「{USER}」（使用者本人）對{AI}說的一段話，'
        '可能是即時打字、夾雜情緒與碎念。請整理成自然的一段發言：\n'
        '‧ 保留他的第一人稱聲音、用詞與情緒，這是他的話。\n'
        '‧ 只做輕度整理：修正錯字、去贅字語病、把碎句連成通順句子；去條列與 markdown。\n'
        '‧ 不要美化、不要詩化、不要替他講得更有學問，不要加他沒說的話。\n'
        f'只輸出整理後的話本身，不加引號、不加「{USER}：」前綴。')

glock = threading.Lock(); g_next = [0.0]*max(1, len(GKEYS)); n_next = [0.0]*max(1, len(NKEYS))
def _pick(arr, iv):
    with glock:
        i = min(range(len(arr)), key=lambda j: arr[j]); st = max(time.time(), arr[i]); arr[i] = st+iv; return i, st

def call_gemini(sysmsg, text):
    if not GKEYS: return None
    body = {'systemInstruction': {'parts': [{'text': sysmsg}]}, 'contents': [{'parts': [{'text': text}]}],
            'generationConfig': {'temperature': 0.4, 'maxOutputTokens': 8192}}
    payload = json.dumps(body).encode('utf-8')
    for _ in range(len(GKEYS)+2):
        i, st = _pick(g_next, 4.5); d = st-time.time()
        if d > 0: time.sleep(d)
        try:
            req = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{GMODEL}:generateContent?key={GKEYS[i]}',
                                         data=payload, headers={'Content-Type': 'application/json'}, method='POST')
            r = json.load(urllib.request.urlopen(req, timeout=120))
            return r['candidates'][0]['content']['parts'][0]['text'].strip()
        except urllib.error.HTTPError as ex:
            with glock: g_next[i] = time.time()+(90 if ex.code == 429 else 30)
        except Exception:
            with glock: g_next[i] = time.time()+30
    return None

def call_nvidia(sysmsg, text):
    if not NKEYS: return None
    for _ in range(4):
        i, st = _pick(n_next, 5.0); d = st-time.time()
        if d > 0: time.sleep(d)
        try:
            req = urllib.request.Request(NURL, data=json.dumps({'model': NMODEL, 'temperature': 0.4, 'max_tokens': 8192,
                'messages': [{'role': 'system', 'content': sysmsg}, {'role': 'user', 'content': text}]}).encode('utf-8'),
                headers={'Authorization': 'Bearer '+NKEYS[i], 'Content-Type': 'application/json'}, method='POST')
            r = json.load(urllib.request.urlopen(req, timeout=150))
            return re.sub(r'<think>.*?</think>', '', r['choices'][0]['message']['content'], flags=re.S).strip()
        except Exception:
            with glock: n_next[i] = time.time()+60
    return None

_h = None
def call_haiku(sysmsg, text):
    global _h
    import anthropic
    from pathlib import Path
    if _h is None:
        tok = json.loads((Path(os.environ.get('USERPROFILE', os.environ.get('HOME', ''))) / '.claude' / '.credentials.json').read_text(encoding='utf-8'))['claudeAiOauth']['accessToken']
        _h = anthropic.Anthropic(auth_token=tok, timeout=150.0, max_retries=2)
    for a in range(5):
        try:
            m = _h.messages.create(model='claude-haiku-4-5', max_tokens=8192, system=sysmsg, messages=[{'role': 'user', 'content': text}])
            return ''.join(b.text for b in m.content if hasattr(b, 'text')).strip()
        except anthropic.RateLimitError: time.sleep(8*(a+1))
        except Exception:
            if a == 4: return None
            time.sleep(4*(a+1))
    return None

_CC = None
def to_trad(s):
    """簡體殘字 → 繁體（Haiku 偶爾吐簡體；[[feedback_traditional_chinese_only]]）。"""
    global _CC
    if _CC is None:
        try:
            import opencc; _CC = opencc.OpenCC('s2tw')
        except Exception:
            _CC = False
    return _CC.convert(s) if _CC else s

def rewrite(kind, text):
    sysmsg = sys_user() if kind == 'user' else sys_ai()
    out = (call_haiku(sysmsg, text) if HAIKU else None) or call_gemini(sysmsg, text) or call_nvidia(sysmsg, text)
    if not out: return None
    out = re.sub(r'^["「『]+|["」』]+$', '', out).strip()
    lab = USER if kind == 'user' else AI
    out = re.sub(r'^' + lab + r'\s*[:：]\s*', '', out).strip()
    return to_trad(out)

def paras(label, prose):
    ps = [p.strip() for p in re.split(r'\n\s*\n+|\n', prose) if p.strip()]
    if not ps: return ''
    return f'<p><strong class="speaker">{label}：</strong>{html.escape(ps[0])}</p>' + ''.join(f'<p>{html.escape(p)}</p>' for p in ps[1:])

def fetch_in_rows():
    ids = set(json.load(open(MEMBERSHIP, encoding='utf-8'))['ids'])
    rows, off = [], 0
    while True:
        h = dict(DBH); h['Range-Unit'] = 'items'; h['Range'] = f'{off}-{off+999}'
        q = (f'{U}/rest/v1/ai_dialogues_gemini?select=id,dialogue_date,dialogue_time,prompt,response'
             f'&dialogue_date=gte.{START}&dialogue_date=lte.{END}&order=dialogue_date.asc,dialogue_time.asc.nullslast')
        b = json.load(urllib.request.urlopen(urllib.request.Request(q, headers=h)))
        if not b: break
        rows.extend(b)
        if len(b) < 1000: break
        off += 1000
    return [r for r in rows if r['id'] in ids]

def build_day(date, rows):
    blocks = []
    for r in rows:
        up, rp = (r.get('prompt') or '').strip(), (r.get('response') or '').strip()
        if up:
            u = rewrite('user', up)
            if u: blocks.append(paras(USER, u))
        if rp:
            a = rewrite('ai', rp)
            if a: blocks.append(paras(AI, a))
    y, m, dd = map(int, date.split('-'))
    wd = WD[datetime.date(y, m, dd).isoweekday()]
    return f'<h3>{y}年{m}月{dd}日（星期{wd}）</h3>' + ''.join(blocks), f'星期{wd}', f'{y}年{m}月{dd}日（星期{wd}）', len(rows)

def patch_day(date, htmlstr, wd, title, n):
    body = json.dumps({'html': htmlstr, 'weekday': wd, 'day_title': title, 'n_turns': n}, ensure_ascii=False).encode('utf-8')
    urllib.request.urlopen(urllib.request.Request(f'{U}/rest/v1/dialogue_days?project_slug=eq.{SLUG}&day_date=eq.{date}',
        data=body, method='PATCH', headers={**DBH, 'Content-Type': 'application/json', 'Prefer': 'return=minimal'}))

def delete_day(date):
    urllib.request.urlopen(urllib.request.Request(f'{U}/rest/v1/dialogue_days?project_slug=eq.{SLUG}&day_date=eq.{date}',
        method='DELETE', headers={**DBH, 'Prefer': 'return=minimal'}))

def main():
    rows = fetch_in_rows()
    byday = defaultdict(list)
    for r in rows: byday[r['dialogue_date']].append(r)
    # 範圍內所有「現有 dialogue_days 日期」（用來決定哪些要刪）
    q = f'{U}/rest/v1/dialogue_days?select=day_date&project_slug=eq.{SLUG}&day_date=gte.{START}&day_date=lte.{END}'
    existing = [d['day_date'] for d in json.load(urllib.request.urlopen(urllib.request.Request(q, headers=DBH)))]
    content_days = sorted(byday)
    empty_days = [d for d in existing if d not in byday]
    if DAY_ARGS:
        content_days = [d for d in content_days if d in DAY_ARGS]; empty_days = []

    if DRY:
        for d in content_days[:1]:
            h, *_ = build_day(d, byday[d])
            print(f'=== {d}（{len(byday[d])} 則 IN）===\n' + re.sub(r'</p>', '</p>\n', h)[:2600])
        print(f'\n（全量：{len(byday)} 天有內容、{len(empty_days)} 天空白將刪）')
        return

    done = set(json.load(open(LEDGER, encoding='utf-8'))) if (os.path.exists(LEDGER) and not DAY_ARGS) else set()
    todo = [d for d in content_days if d not in done]
    print(f'重建 {len(todo)} 天（已完成 {len(done)}）；空白待刪 {len(empty_days)} 天', flush=True)
    lock = threading.Lock()
    def run(d):
        h, wd, title, n = build_day(d, byday[d])
        patch_day(d, h, wd, title, n)
        with lock:
            done.add(d); json.dump(sorted(done), open(LEDGER, 'w'), ensure_ascii=False)
            print(f'  rebuilt {d}（{n} 則）', flush=True)
    with ThreadPoolExecutor(max_workers=6 if HAIKU else max(1, len(GKEYS))) as ex:
        list(ex.map(run, todo))
    if not DAY_ARGS:
        for d in empty_days:
            delete_day(d); print(f'  deleted empty {d}', flush=True)
    print('完成。', flush=True)

if __name__ == '__main__':
    main()
