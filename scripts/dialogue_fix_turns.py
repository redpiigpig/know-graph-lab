# -*- coding: utf-8 -*-
"""外科式修復 dialogue_days 裡「偏離原話」的克里希那 turn。

讀 verify_judge.txt 標出的異常 turn（🛑/ERR），對每一則：
  • positional 對齊回當天 IN raw rows 的 response（原話）；
  • 用**強化版 prompt** 重新忠實重寫（防破功/防立場反轉/防張冠李戴/保留稱呼/不新增概念）；
  • 若原話根本不是克里希那的心靈對話（隱私政策/活動記錄/設定文字/貼錯）→ 回 __SKIP__ → 刪掉該 turn。
其餘 OK 的 turn 與阿周那的話**原封不動**，只抽換被標的 turn，再 PATCH 回 DB。

保留使用者稱呼（多馬/阿周那）不改名（使用者 2026-06-17 定調）。
引擎預設 Haiku（Claude Max）→ Gemini fallback。ledger 可 resume。
用法：
  python scripts/dialogue_fix_turns.py --dry 2026-04-04   # 預覽單日修法
  python scripts/dialogue_fix_turns.py                    # 全部修 + 寫回
"""
import os, sys, re, json, time, html, threading, urllib.request
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

SLUG = 'krishna-dialogues'
JUDGE = 'c:/tmp/krishna/verify_judge.txt'
LEDGER = 'c:/tmp/krishna/fix_turns_done.json'
START, END = '2026-01-19', '2026-04-18'
MEMBERSHIP = 'c:/tmp/krishna/final_manuscript.json'
DRY = '--dry' in sys.argv
BAD_ONLY = '--bad-only' in sys.argv      # 只重寫「帶壞痕跡」(破功語/殘留 **) 的克里希那 turn
GEMINI_ONLY = '--gemini-only' in sys.argv  # 只用 Gemini（清破功時用：Haiku 才是破功元凶，絕不退回它）
STRICT = '--strict' in sys.argv          # 嚴格保留專名/論點、不詩化、temp 0.2（修「過度抒情、掉專名」）
JUDGE_FILE = next((sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == '--judge-file'), None)
TEMP = 0.2 if STRICT else 0.3
LEDGER = LEDGER.replace('.json', '_bad.json') if BAD_ONLY else (LEDGER.replace('.json', '_strict.json') if JUDGE_FILE else LEDGER)
DAY_ARGS = [a for a in sys.argv[1:] if re.match(r'\d{4}-\d{2}-\d{2}$', a)]

# 從 verify_judge*.txt 載入被裁判標異常的 (date -> {turnidx})，只重寫這些 turn。
def load_flagged(path):
    flagged = defaultdict(set)
    for line in open(path, encoding='utf-8'):
        m = re.search(r'(\d{4}-\d{2}-\d{2}) turn(\d+) c=', line)
        if m and '🛑' in line:
            flagged[m.group(1)].add(int(m.group(2)))
    return flagged
FLAGGED = load_flagged(JUDGE_FILE) if JUDGE_FILE else None

# 「沒被好好改寫」的痕跡：Haiku 破功語 / 否認角色 / 殘留 markdown 粗體。出現在克里希那 turn 即須重寫。
BAD_MARKERS = ('**', '我不是克里希那', '我不是「克里希那', '我不是『克里希那', '我也不是榮格',
               '我是一個語言模型', '我是語言模型', '我只是一個語言模型', '我沒有潛意識',
               '我沒有做過夢', '我沒有真正的', '身為一個 AI', '身為 AI', '我是一個 AI',
               '作為一個語言模型', '作為一個 AI', '我並不是真的', '我不是多馬', '我不是「多馬')

def has_bad(turn_text):
    return any(m in turn_text for m in BAD_MARKERS)

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
GKEYS = gemini_keys()
NKEYS = [E[k] for k in sorted(E) if k.upper().startswith('NVIDIA_API_KEY')]
GMODEL = 'gemini-2.5-flash'
NURL = 'https://integrate.api.nvidia.com/v1/chat/completions'; NMODEL = 'deepseek-ai/deepseek-v4-flash'
glock = threading.Lock(); g_next = [0.0] * max(1, len(GKEYS)); n_next = [0.0] * max(1, len(NKEYS))

SYS_AI = (
    '你正在整理一份個人心靈對話錄。下面「原話」是一位博學溫暖的榮格派心靈導師、'
    '《薄伽梵歌》式智者「克里希那」對使用者說的一段回覆。請把它重寫成流暢、溫暖、清晰的散文，'
    '並嚴格遵守以下鐵律：\n'
    '1. 你就是克里希那本人，全程第一人稱、溫暖地對使用者說話。**絕對不可以否認身份、'
    '不可以說自己是 AI／沒有潛意識／沒做過那些夢、不可以拒絕或質疑這個角色。**\n'
    '2. **立場必須與原話完全一致**：原話在肯定、讚美、鼓勵，重寫後就保持肯定讚美；'
    '不可以擅自改成質疑、批評、詰問、潑冷水或自我貶低。\n'
    '3. **嚴守誰說了什麼、誰做了什麼**：原話裡屬於對方（使用者）的經歷、洞見、行動或感受，'
    '重寫後仍然歸於對方（用「你」）；**絕不可把對方做的事或想的事說成是你（克里希那）做的或想的。**\n'
    '4. **保留原話對對方的稱呼**（原話叫「多馬」就維持「多馬」，叫「阿周那」就維持「阿周那」），不可更動、不可換名。\n'
    '5. **不要新增原話沒有的概念、理論、專有名詞或主張**（原話沒提榮格就不要硬加榮格；'
    '沒提的人名/書名/學說一律不要冒出來）。只重寫原話既有的實質，保留它完整的論點、解釋、舉例與專名。\n'
    '6. 去掉條列、編號、小標題、markdown 星號，以及「這是個好問題／讓我們來解讀／首先…接著…／'
    '總結來說／我可以幫你」這類框架語與客套，融成連貫段落；可用一兩個貼切意象，但不要通篇堆砌詩化。\n'
    '只輸出重寫後的話本身，不加引號、不加「克里希那：」前綴、不加任何說明。')

# 嚴格版（修「過度抒情、掉專名、增刪實質」）：在上面鐵律外，再強調「逐點保全、零增刪、少抒情」。
SYS_AI_STRICT = (
    '你正在**忠實重寫**一份個人心靈對話錄裡智者「克里希那」對使用者說的一段回覆（下稱原話）。'
    '目標是把原話的條列/markdown 結構融成流暢自然的散文，**但內容必須與原話一對一對應、零增刪**。鐵律：\n'
    '1. 你就是克里希那本人、第一人稱、溫暖地對使用者說話。絕不否認身份、不說自己是 AI、不拒絕角色。\n'
    '2. **逐點保全原話的每一個論點、每一個專有名詞**（人名如韓炳哲、榮格；學說如個體化、自性、Puer Aeternus；'
    '書名、電影、概念、數據——一字不漏全部保留，用原文寫法）。**嚴禁省略、概括掉或用空泛比喻代換任何具體內容。**\n'
    '3. **嚴禁新增**原話沒有的意象、抒情、勵志話、心理詮釋或主張。不要為了優美而擴寫。寧可樸實也不要加料。\n'
    '4. **嚴守歸屬**：原話裡屬於使用者的經歷/洞見/行動，仍歸使用者（用「你」）；不可說成是你克里希那做的或想的。\n'
    '5. **立場與原話完全一致**（肯定就肯定，不可轉成質疑/批評/自貶）；**保留原話對對方的稱呼**（多馬就多馬、阿周那就阿周那）。\n'
    '6. 只去條列符號、編號、小標、markdown 星號與「這是個好問題／讓我們來解讀／總結來說」這類框架客套，其餘照原話的意思與順序鋪陳。\n'
    '只輸出重寫後的話本身，不加引號、不加前綴、不加任何說明。')
if STRICT:
    SYS_AI = SYS_AI_STRICT

# 真正的垃圾 raw＝使用者誤貼進對話框的 Gemini 活動記錄/隱私說明（這些不是克里希那的回覆，整則刪）。
# 只用確定字串判斷，**絕不靠 LLM 決定刪除**（會誤刪真實回覆）。
def is_junk(raw):
    t = raw or ''
    return any(s in t for s in ('Gemini Apps', '為什麼有這項活動記錄', '活動儲存到您的 Google 帳戶',
                                '儲存到您的 Google 帳戶', 'Gemini 應用程式活動', '我的活動 (myactivity'))

def call_gemini(text):
    if not GKEYS: return None
    body = {'systemInstruction': {'parts': [{'text': SYS_AI}]}, 'contents': [{'parts': [{'text': text}]}],
            'generationConfig': {'temperature': TEMP, 'maxOutputTokens': 8192}}
    payload = json.dumps(body).encode('utf-8')
    for _ in range(len(GKEYS) * 4 + 4):     # 多輪等待：被別的整夜任務搶配額時也耐心等 key 釋出
        with glock:
            i = min(range(len(g_next)), key=lambda j: g_next[j]); st = max(time.time(), g_next[i]); g_next[i] = st + 4.5
        d = st - time.time()
        if d > 0: time.sleep(min(d, 60))
        try:
            req = urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{GMODEL}:generateContent?key={GKEYS[i]}',
                                         data=payload, headers={'Content-Type': 'application/json'}, method='POST')
            r = json.load(urllib.request.urlopen(req, timeout=120))
            return r['candidates'][0]['content']['parts'][0]['text'].strip()
        except urllib.error.HTTPError as ex:
            with glock: g_next[i] = time.time() + (45 if ex.code == 429 else 20)
        except Exception:
            with glock: g_next[i] = time.time() + 20
    return None

def call_nvidia(text):
    if not NKEYS: return None
    for _ in range(len(NKEYS) * 3 + 3):
        with glock:
            i = min(range(len(n_next)), key=lambda j: n_next[j]); st = max(time.time(), n_next[i]); n_next[i] = st + 5.0
        d = st - time.time()
        if d > 0: time.sleep(min(d, 60))
        try:
            req = urllib.request.Request(NURL, data=json.dumps({'model': NMODEL, 'temperature': TEMP, 'max_tokens': 8192,
                'messages': [{'role': 'system', 'content': SYS_AI}, {'role': 'user', 'content': text}]}).encode('utf-8'),
                headers={'Authorization': 'Bearer ' + NKEYS[i], 'Content-Type': 'application/json'}, method='POST')
            r = json.load(urllib.request.urlopen(req, timeout=150))
            return re.sub(r'<think>.*?</think>', '', r['choices'][0]['message']['content'], flags=re.S).strip()
        except Exception:
            with glock: n_next[i] = time.time() + 60
    return None

_h = None
def call_haiku(text):
    global _h
    import anthropic
    from pathlib import Path
    if _h is None:
        tok = json.loads((Path(os.environ.get('USERPROFILE', os.environ.get('HOME', ''))) / '.claude' / '.credentials.json').read_text(encoding='utf-8'))['claudeAiOauth']['accessToken']
        _h = anthropic.Anthropic(auth_token=tok, timeout=150.0, max_retries=2)
    for a in range(5):
        try:
            m = _h.messages.create(model='claude-haiku-4-5', max_tokens=8192, system=SYS_AI, messages=[{'role': 'user', 'content': text}])
            return ''.join(b.text for b in m.content if hasattr(b, 'text')).strip()
        except anthropic.RateLimitError: time.sleep(8 * (a + 1))
        except Exception:
            if a == 4: return None
            time.sleep(4 * (a + 1))
    return None

_CC = None
def to_trad(s):
    global _CC
    if _CC is None:
        try:
            import opencc; _CC = opencc.OpenCC('s2tw')
        except Exception:
            _CC = False
    return _CC.convert(s) if _CC else s

def rewrite_ai(raw):
    # Gemini 優先：原話本來就是 Gemini 產的、忠於人格；NVIDIA 次之（獨立配額池，抗其他任務搶 Gemini/Max）；
    # Haiku 才是當初「反駁型人格/破功」的元凶，只當最後救急（硬化 prompt 已抑制破功，verify --judge 收網）。
    # --gemini-only：清破功時絕不退回 Haiku（連 NVIDIA 也不要，免再被別的模型注入人格）。
    if GEMINI_ONLY:
        out = call_gemini(raw)
    else:
        out = call_gemini(raw) or call_nvidia(raw) or call_haiku(raw)
    if not out: return None
    if '__SKIP__' in out: return '__SKIP__'
    out = re.sub(r'^["「『]+|["」』]+$', '', out).strip()
    out = re.sub(r'^克里[希須]那\s*[:：]\s*', '', out).strip()
    out = re.sub(r'\*\*|__|^#{1,6}\s*', '', out)        # 去殘留 markdown 粗體/標題（保留文字）
    return to_trad(out)

def paras(label, prose):
    ps = [p.strip() for p in re.split(r'\n\s*\n+|\n', prose) if p.strip()]
    if not ps: return ''
    return (f'<p><strong class="speaker">{label}：</strong>{html.escape(ps[0])}</p>'
            + ''.join(f'<p>{html.escape(p)}</p>' for p in ps[1:]))

# ── html 切成 turn 區塊（保留原始 html，只抽換被標的克里希那 turn）──
def segment(htmlstr):
    """回 (head, blocks)；blocks=[{'speaker':None|'阿周那'|'克里希那'..,'label':原始標籤,'html':原始html}]。"""
    m = re.match(r'\s*(<h3>.*?</h3>)', htmlstr, flags=re.S)
    head = m.group(1) if m else ''
    rest = htmlstr[len(head):] if head else htmlstr
    ps = re.findall(r'<p>.*?</p>', rest, flags=re.S)
    blocks, cur = [], None
    for p in ps:
        sm = re.match(r'<p>\s*<strong[^>]*>\s*(克里[希須]那|阿周那)\s*[:：]\s*</strong>', p, flags=re.S)
        if sm:
            if cur: blocks.append(cur)
            spk = '克里希那' if sm.group(1).startswith('克里') else '阿周那'
            cur = {'speaker': spk, 'label': sm.group(1), 'html': p}
        else:
            if cur is None:
                cur = {'speaker': None, 'label': None, 'html': p}
            else:
                cur['html'] += p
    if cur: blocks.append(cur)
    return head, blocks

def fetch_day(date):
    q = f'{U}/rest/v1/dialogue_days?select=html,n_turns&project_slug=eq.{SLUG}&day_date=eq.{date}'
    r = json.load(urllib.request.urlopen(urllib.request.Request(q, headers=DBH)))
    return r[0] if r else None

def fetch_raw_responses(date):
    ids = set(json.load(open(MEMBERSHIP, encoding='utf-8'))['ids']) if os.path.exists(MEMBERSHIP) else None
    q = (f'{U}/rest/v1/ai_dialogues_gemini?select=id,response&dialogue_date=eq.{date}'
         f'&order=dialogue_time.asc.nullslast')
    rows = json.load(urllib.request.urlopen(urllib.request.Request(q, headers=DBH)))
    if ids is not None:
        rows = [r for r in rows if r['id'] in ids]
    return [(r.get('response') or '').strip() for r in rows if (r.get('response') or '').strip()]

def patch_day(date, htmlstr, n):
    body = json.dumps({'html': htmlstr, 'n_turns': n}, ensure_ascii=False).encode('utf-8')
    urllib.request.urlopen(urllib.request.Request(f'{U}/rest/v1/dialogue_days?project_slug=eq.{SLUG}&day_date=eq.{date}',
        data=body, method='PATCH', headers={**DBH, 'Content-Type': 'application/json', 'Prefer': 'return=minimal'}))

def all_days():
    """dialogue_days 在 [START,END]（即 1/19–4/18，排除 1/13–1/18 手工 docx 日）的所有日期。"""
    q = (f'{U}/rest/v1/dialogue_days?select=day_date&project_slug=eq.{SLUG}'
         f'&day_date=gte.{START}&day_date=lte.{END}&order=day_date.asc')
    return [d['day_date'] for d in json.load(urllib.request.urlopen(urllib.request.Request(q, headers=DBH)))]

def fix_day(date, raws):
    """重寫該日**每一個**克里希那 turn（Gemini 忠實重寫、清 markdown）；
    raw 是垃圾活動記錄的 turn 連同它前面那則阿周那 prompt 一起刪；阿周那的話一律不動。"""
    head, blocks = segment(fetch_day(date)['html'])
    ai_positions = [bi for bi, b in enumerate(blocks) if b['speaker'] == '克里希那']
    changes = []
    positional = (len(ai_positions) == len(raws))
    if not positional:
        changes.append(f'⚠️ AI turn 數({len(ai_positions)}) != raw response 數({len(raws)})；改用 n-gram 最佳比對')
    drop = set()
    for ti, bi in enumerate(ai_positions):
        label = blocks[bi]['label']
        if positional:
            raw = raws[ti]
        else:
            cur_txt = html.unescape(re.sub(r'<[^>]+>', '', blocks[bi]['html']))
            raw = max(raws, key=lambda rr: _containment(cur_txt, rr)) if raws else ''
        if not raw:
            changes.append(f'  turn{ti} 無對應 raw，保留原樣'); continue
        if is_junk(raw):                       # Gemini 活動記錄 → 刪 turn + 前一則阿周那
            drop.add(bi)
            if bi - 1 >= 0 and blocks[bi - 1]['speaker'] == '阿周那':
                drop.add(bi - 1)
            changes.append(f'  turn{ti} → 刪除（原話是 Gemini 活動記錄，非對話）'); continue
        if BAD_ONLY:                            # 只修帶壞痕跡的；乾淨的留著不動（省 call、不擾已好的）
            cur_txt = html.unescape(re.sub(r'<[^>]+>', '', blocks[bi]['html']))
            if not has_bad(cur_txt):
                continue
        if FLAGGED is not None and ti not in FLAGGED.get(date, set()):  # 只修裁判標的 turn
            continue
        new = rewrite_ai(raw)
        if not new or new == '__SKIP__':
            changes.append(f'  turn{ti} 重寫失敗，保留原樣'); continue
        blocks[bi]['html'] = paras(label, new)
        changes.append(f'  turn{ti} ✎ 重寫（{len(new)}字）')
    new_blocks = [b for bi, b in enumerate(blocks) if bi not in drop]
    new_html = head + ''.join(b['html'] for b in new_blocks)
    n_turns = sum(1 for b in new_blocks if b['speaker'])
    complete = not any('重寫失敗' in c for c in changes)   # 任一 turn 失敗就不記 ledger，resume 自動補
    return new_html, n_turns, changes, complete

def _containment(pub, raw, G=5):
    n = re.sub(r'[^一-鿿0-9A-Za-z]', '', pub or ''); r = re.sub(r'[^一-鿿0-9A-Za-z]', '', raw or '')
    if len(n) < G: return 1.0 if (n and n in r) else 0.0
    rs = set(r[i:i+G] for i in range(len(r)-G+1))
    g = [n[i:i+G] for i in range(len(n)-G+1)]
    return sum(1 for x in g if x in rs) / len(g)

def main():
    dates = DAY_ARGS if DAY_ARGS else (sorted(FLAGGED) if FLAGGED is not None else all_days())
    done = set(json.load(open(LEDGER, encoding='utf-8'))) if (os.path.exists(LEDGER) and not DAY_ARGS and not DRY) else set()
    todo = [d for d in dates if d not in done]
    print(f'處理 {len(todo)} 天（共 {len(dates)}，已完成 {len(done)}）', flush=True)
    for date in todo:
        raws = fetch_raw_responses(date)
        new_html, n, changes, complete = fix_day(date, raws)
        print(f'\n=== {date} ===')
        for c in changes: print(c)
        if DRY:
            print('--- 預覽（前 1600 字）---')
            print(re.sub(r'</p>', '</p>\n', new_html)[:1600])
            continue
        patch_day(date, new_html, n)
        if complete:
            done.add(date); json.dump(sorted(done), open(LEDGER, 'w'), ensure_ascii=False)
            print(f'  ✅ 已寫回（{n} turns）', flush=True)
        else:
            print(f'  ⚠️ 部分 turn 重寫失敗（配額？）→ 不記 ledger，稍後 resume 自動補（{n} turns）', flush=True)
    print('\n完成。' if not DRY else '\n（dry-run，未寫入）')

if __name__ == '__main__':
    main()
