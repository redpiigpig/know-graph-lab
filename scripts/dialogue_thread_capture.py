# -*- coding: utf-8 -*-
"""重抓「與克里希那的對話」框 — 候選 prelabel + LLM 語氣判定（全量重分類）。

流程（見 .claude/skills/dialogues-to-writing/SKILL.md）：
  1. 拉 ai_dialogues_gemini 在 2026-01-13..2026-04-18 全部（2,219 則）。
  2. dialogue_thread_classify.prelabel 先決定高把握 IN/OUT，其餘 MAYBE。
  3. MAYBE 者**逐日整批**送 LLM 語氣判定（給整天序列當上下文，利用對話框連續性）：
       傾訴／思辨閒聊＝IN；叫 AI 幫我做出東西（程式/sql/翻譯/地圖專案/雜誌/論文…）＝OUT。
  4. 合併 → final_recapture.json（id 清單）。可 resumable（per-day ledger）。

引擎：Gemini 2.5 flash（4 keys 輪流，主）→ NVIDIA deepseek-v4-flash（fallback）；
      --haiku＝改用 Claude Haiku（OAuth/Max 額度，不撞免費池）為主。
      見 [[feedback_engine_nvidia_no_haiku]]。

用法：
  python scripts/dialogue_thread_capture.py --dry        # 只 prelabel + 統計分布、列 MAYBE 數，不呼叫 LLM
  python scripts/dialogue_thread_capture.py              # 全量（Gemini→NVIDIA）
  python scripts/dialogue_thread_capture.py --haiku      # 用 Haiku 跑 MAYBE
  python scripts/dialogue_thread_capture.py 2026-01-13   # 只跑指定日（眼校）
  python scripts/dialogue_thread_capture.py --diff       # 跑完和現有 671 tag 比對
"""
import os, sys, re, json, time, threading, urllib.request, urllib.error
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dialogue_thread_classify as C

sys.stdout.reconfigure(encoding='utf-8')

# ── env / keys ───────────────────────────────────────────────────────
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
                    if p and p not in seen:
                        seen.add(p); out.append(p)
    return out
GKEYS = gemini_keys()
NKEYS = [E[k] for k in sorted(E) if k.upper().startswith('NVIDIA_API_KEY')]
GMODEL = 'gemini-2.5-flash'
NURL = 'https://integrate.api.nvidia.com/v1/chat/completions'; NMODEL = 'deepseek-ai/deepseek-v4-flash'

DRY = '--dry' in sys.argv
HAIKU = '--haiku' in sys.argv
DODIFF = '--diff' in sys.argv
REAGG = '--reagg' in sys.argv     # 不呼叫 LLM，只用目前的 classifier 把 ledger 重新彙整（guard 覆寫）
RETAG = '--retag' in sys.argv     # 讀 final_recapture.json，刪舊 junction 後寫入新分類
DAY_ARGS = [a for a in sys.argv[1:] if re.match(r'\d{4}-\d{2}-\d{2}$', a)]

TMP = 'c:/tmp/krishna'
LEDGER = os.path.join(TMP, 'recapture.jsonl')   # 每日結果：{"date":..,"labels":{seq:IN/OUT},"ids":{seq:id}}
FINAL = os.path.join(TMP, 'final_recapture.json')
CAT_ID = '01f01e76-66cb-44b9-9cf6-3352bb6baf5d'

print(f'gemini keys: {len(GKEYS)} | nvidia keys: {len(NKEYS)} | haiku: {"ON(主)" if HAIKU else "off"}', flush=True)

# ── 拉資料 ───────────────────────────────────────────────────────────
def fetch_rows():
    url = f'{U}/rest/v1/ai_dialogues_gemini'
    rows, off, PAGE = [], 0, 1000
    while True:
        h = dict(DBH); h['Range-Unit'] = 'items'; h['Range'] = f'{off}-{off+PAGE-1}'
        q = (f'{url}?select=id,dialogue_date,dialogue_time,prompt,response'
             f'&dialogue_date=gte.{C.THREAD_START}&order=dialogue_date.asc,dialogue_time.asc.nullslast')
        b = json.load(urllib.request.urlopen(urllib.request.Request(q, headers=h)))
        if not b: break
        rows.extend(b)
        if len(b) < PAGE: break
        off += PAGE
    rows = [r for r in rows if r['dialogue_date'] <= C.THREAD_END]
    return rows

# ── LLM 判定 ─────────────────────────────────────────────────────────
SYS = (
    "你在整理一份扁平的 Gemini 對話匯出：同一天混了使用者的『多個聊天視窗』。"
    "請只把屬於『與克里希那的對話』這一個視窗（一本私人的榮格式心靈日記）的訊息挑出來。\n"
    "【IN＝這個視窗】只有以下幾類：\n"
    "  (a) 直接對 AI（暱稱克里希那/克里須那）傾訴、自稱阿周那；\n"
    "  (b) 榮格心理學、解夢、積極想像(主動想像)、原型/阿尼瑪/陰影/自性等內在心理探索；\n"
    "  (c) 對自己生活/身體/飲食/健康/情緒/人際/性/信仰的第一人稱碎念與反思"
    "（含對龐君華牧師過世的死亡與前途反思、減肥蛋白粉飲食、感情）；\n"
    "  (d) 純為了『自我理解』而非某個產出專案的宗教/神話/哲學個人思辨。\n"
    "  ※ (a)(b) 敘述裡夾帶『code』『電腦』等字眼不影響，只要核心是積極想像或對克里希那說話，仍是 IN。\n"
    "  ※ 但『潤稿/修飾文字』例外：見下方 OUT——叫 AI 把某段文字潤飾/改寫/保留我的語氣，一律 OUT，即使內容是榮格或對克里希那。\n"
    "【OUT＝其他視窗】使用者其實在『做專案』，只是語氣像聊天。以下一律 OUT，"
    "即使句子是『你覺得…好嗎？』這種思辨口吻：\n"
    "  • 世界地圖專案：把世界劃分「界域/文化圈/文化區」、替這些區域命名/排序/選英文譯名"
    "（realm/world-area、邊亞、梅公/楣公、努山塔拉、盧布林、薩爾馬提亞、次大陸、把某國放進哪個文化圈…）；\n"
    "  • 翻譯/定名計畫：替古籍史書人名地名帝王定中文譯名、書目/註釋格式、ISSN、編輯雜誌《無境界者》；\n"
    "  • 論文/學術工作：研究計劃、博士論文架構與章節、投稿、寫給老師的 line/email、招生規定；\n"
    "  • 程式/IT/工具：寫改 debug 程式、sql、部署、資料表/欄位、Heptabase/NotebookLM 等工具價格與用法；\n"
    "  • 旅遊交友網站專案、有聲書/繪本製作、歷史帝王稱號考據等為某產出服務的查證。\n"
    "  • 潤稿：叫 AI 修飾/潤飾/改寫某段文字、『保留我的語氣與字數』『記得我的行文風格』——一律 OUT。\n"
    "【判準】這是不是他在『對克里希那談自己的內心/生活/夢』？是→IN。"
    "是不是他在『請 AI 幫某個專案做決定或做出東西』？是→OUT。兩者拿不準時，傾向 OUT。\n"
    "善用上下文連續性：與相鄰 IN 訊息同一內心主題脈絡的通常也 IN；夾在一串地圖/論文/程式專案中間的通常 OUT。\n"
    "只回傳 JSON 物件，鍵是我標示『?』的 seq 數字字串、值是 \"IN\" 或 \"OUT\"，"
    "不要任何解說或程式碼框。"
)

def build_user_msg(entries, ask_seqs, prelab):
    lines = ["這一天的訊息（依序）。請判定標示『?』的 seq："]
    for e in entries:
        s = e['seq']
        tag = '?' if s in ask_seqs else prelab[s]
        p = (e.get('prompt') or '').replace('\n', ' ')[:240]
        lines.append(f"[seq {s}|{tag}] {p}")
    lines.append(f"\n要判定的 seq：{sorted(ask_seqs)}")
    return '\n'.join(lines)

glock = threading.Lock(); g_next = [0.0] * max(1, len(GKEYS)); n_next = [0.0] * max(1, len(NKEYS))
def _pick(arr, interval):
    with glock:
        i = min(range(len(arr)), key=lambda j: arr[j])
        now = time.time(); start = max(now, arr[i]); arr[i] = start + interval
        return i, start

def _parse_json(txt):
    if not txt: return None
    txt = re.sub(r'```(?:json)?|```', '', txt)
    txt = re.sub(r'<think>.*?</think>', '', txt, flags=re.S)
    m = re.search(r'\{.*\}', txt, re.S)
    if not m: return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None

def call_gemini(sysmsg, usermsg):
    if not GKEYS: return None
    body = {'systemInstruction': {'parts': [{'text': sysmsg}]},
            'contents': [{'parts': [{'text': usermsg}]}],
            'generationConfig': {'temperature': 0.0, 'maxOutputTokens': 2048,
                                 'responseMimeType': 'application/json'}}
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

def call_nvidia(sysmsg, usermsg):
    if not NKEYS: return None
    for _ in range(4):
        i, start = _pick(n_next, 5.0)
        d = start - time.time()
        if d > 0: time.sleep(d)
        try:
            req = urllib.request.Request(NURL, data=json.dumps({
                'model': NMODEL, 'temperature': 0.0, 'max_tokens': 2048,
                'messages': [{'role': 'system', 'content': sysmsg},
                             {'role': 'user', 'content': usermsg}]}).encode('utf-8'),
                headers={'Authorization': 'Bearer ' + NKEYS[i], 'Content-Type': 'application/json'}, method='POST')
            r = json.load(urllib.request.urlopen(req, timeout=150))
            return r['choices'][0]['message']['content']
        except Exception:
            with glock: n_next[i] = time.time() + 60
    return None

_hclient = None
def call_haiku(sysmsg, usermsg):
    global _hclient
    import anthropic
    from pathlib import Path
    if _hclient is None:
        cred = Path(os.environ.get('USERPROFILE', os.environ.get('HOME', ''))) / '.claude' / '.credentials.json'
        tok = json.loads(cred.read_text(encoding='utf-8'))['claudeAiOauth']['accessToken']
        _hclient = anthropic.Anthropic(auth_token=tok, timeout=150.0, max_retries=2)
    for attempt in range(5):
        try:
            m = _hclient.messages.create(model='claude-haiku-4-5', max_tokens=2048,
                                         system=sysmsg, messages=[{'role': 'user', 'content': usermsg}])
            return ''.join(b.text for b in m.content if hasattr(b, 'text')).strip()
        except anthropic.RateLimitError:
            time.sleep(8 * (attempt + 1))
        except Exception:
            if attempt == 4: return None
            time.sleep(4 * (attempt + 1))
    return None

def judge(sysmsg, usermsg):
    if HAIKU:
        return _parse_json(call_haiku(sysmsg, usermsg)) or _parse_json(call_gemini(sysmsg, usermsg))
    return _parse_json(call_gemini(sysmsg, usermsg)) or _parse_json(call_nvidia(sysmsg, usermsg))

# ── per-day ──────────────────────────────────────────────────────────
def process_day(date, entries):
    prelab = {}
    for e in entries:
        prelab[e['seq']] = C.classify_prompt(e.get('prompt') or '', e.get('response') or '')
    ask = sorted(s for s, lab in prelab.items() if lab == 'MAYBE')
    labels = {s: lab for s, lab in prelab.items() if lab != 'MAYBE'}
    if ask and not DRY:
        # 太多 seq 時分批（每批 ≤ 40），但同一天上下文盡量同批
        for chunk_start in range(0, len(ask), 40):
            chunk = ask[chunk_start:chunk_start + 40]
            res = judge(SYS, build_user_msg(entries, set(chunk), prelab)) or {}
            for s in chunk:
                v = res.get(str(s)) or res.get(s)
                labels[s] = 'IN' if v == 'IN' else 'OUT'  # 拿不到 → 保守 OUT
    elif ask and DRY:
        for s in ask:
            labels[s] = 'MAYBE'
    ids = {e['seq']: e['id'] for e in entries}
    return labels, ids, len(ask)

def load_done():
    done = {}
    if os.path.exists(LEDGER):
        for l in open(LEDGER, encoding='utf-8'):
            l = l.strip()
            if l:
                r = json.loads(l); done[r['date']] = r
    return done

def reaggregate(rows):
    """不呼叫 LLM：用目前 classifier 把 ledger 重彙整。
    prelabel 決定者（含 guard）覆寫 ledger；MAYBE 保留 ledger 內的 LLM 判定。"""
    prompts = {}
    for r in rows:
        prompts[(r['dialogue_date'], r['seq'])] = (r.get('prompt') or '', r.get('response') or '')
    in_ids, ov_in, ov_out, kept = [], 0, 0, 0
    for l in open(LEDGER, encoding='utf-8'):
        l = l.strip()
        if not l: continue
        rec = json.loads(l)
        for s, lab in rec['labels'].items():
            p, resp = prompts.get((rec['date'], int(s)), ('', ''))
            pre = C.classify_prompt(p, resp)
            if pre != 'MAYBE':
                final = pre
                if pre != lab: ov_in += (pre == 'IN'); ov_out += (pre == 'OUT')
            else:
                final = lab; kept += 1
            if final == 'IN': in_ids.append(rec['ids'][s])
    in_ids = sorted(set(in_ids))
    json.dump({'ids': in_ids, 'n': len(in_ids)}, open(FINAL, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'reagg: guard覆寫 →IN {ov_in} →OUT {ov_out} | MAYBE保留LLM {kept} | final IN {len(in_ids)}', flush=True)
    return in_ids

def retag(new_ids):
    """刪掉此分類現有 junction，重寫成 new_ids（idempotent，可由 _tagged_ids.json 回滾）。"""
    HD = dict(DBH); HD['Prefer'] = 'count=exact'
    # 刪舊
    req = urllib.request.Request(
        f'{U}/rest/v1/ai_dialogue_entry_categories?category_id=eq.{CAT_ID}',
        method='DELETE', headers={**DBH, 'Prefer': 'return=minimal'})
    urllib.request.urlopen(req)
    # 寫新（分批）
    HU = dict(DBH); HU['Content-Type'] = 'application/json'
    HU['Prefer'] = 'return=minimal,resolution=ignore-duplicates'
    ok = 0
    for s in range(0, len(new_ids), 200):
        chunk = [{'dialogue_id': i, 'category_id': CAT_ID} for i in new_ids[s:s+200]]
        body = json.dumps(chunk, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(
            f'{U}/rest/v1/ai_dialogue_entry_categories?on_conflict=dialogue_id,category_id',
            data=body, method='POST', headers=HU)
        urllib.request.urlopen(req); ok += len(chunk)
    print(f'retag: 刪舊 + 寫入 {ok} 筆 junction（分類 {CAT_ID}）', flush=True)

def main():
    # --reagg / --retag：不跑 LLM，純後處理（reagg 用 ledger，retag 用 final_recapture.json）
    if REAGG or (RETAG and not DAY_ARGS):
        rows = fetch_rows()
        by_date = defaultdict(list)
        for r in rows:
            by_date[r['dialogue_date']].append(r)
        for d in by_date:
            for idx, r in enumerate(by_date[d]):
                r['seq'] = idx
        ids = reaggregate(rows) if REAGG else json.load(open(FINAL, encoding='utf-8'))['ids']
        if DODIFF: do_diff(ids)
        if RETAG: retag(ids)
        return

    rows = fetch_rows()
    by_date = defaultdict(list)
    for r in rows:
        by_date[r['dialogue_date']].append(r)
    for d in by_date:
        for idx, r in enumerate(by_date[d]):
            r['seq'] = idx
    dates = sorted(by_date)
    if DAY_ARGS:
        dates = [d for d in dates if d in DAY_ARGS]
    print(f'rows {len(rows)} | dates {len(dates)} ({dates[0]}..{dates[-1]})', flush=True)

    # --dry：純 prelabel 統計
    if DRY:
        cnt = Counter()
        for d in dates:
            for e in by_date[d]:
                cnt[C.classify_prompt(e.get('prompt') or '', e.get('response') or '')] += 1
        print('prelabel 分布:', dict(cnt))
        print(f"  → 高把握 IN={cnt['IN']} OUT={cnt['OUT']}；交 LLM 的 MAYBE={cnt['MAYBE']}")
        return

    done = load_done() if not DAY_ARGS else {}
    todo = [d for d in dates if d not in done]
    print(f'已完成 {len(done)} 天，待跑 {len(todo)} 天', flush=True)

    lock = threading.Lock()
    fh = open(LEDGER, 'a', encoding='utf-8')
    def run(d):
        labels, ids, nask = process_day(d, by_date[d])
        rec = {'date': d, 'labels': {str(k): v for k, v in labels.items()},
               'ids': {str(k): v for k, v in ids.items()}}
        with lock:
            fh.write(json.dumps(rec, ensure_ascii=False) + '\n'); fh.flush()
            nin = sum(1 for v in labels.values() if v == 'IN')
            print(f'{d}: IN={nin}/{len(labels)}  (LLM判 {nask})', flush=True)
    workers = 8 if HAIKU else max(1, len(GKEYS))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(run, todo))
    fh.close()

    # 彙整全部 ledger → final id 清單
    done = load_done()
    in_ids = []
    for d, rec in done.items():
        for s, v in rec['labels'].items():
            if v == 'IN':
                in_ids.append(rec['ids'][s])
    in_ids = sorted(set(in_ids))
    json.dump({'ids': in_ids, 'n': len(in_ids)},
              open(FINAL, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'\nfinal IN ids: {len(in_ids)} → {FINAL}', flush=True)

    if DODIFF:
        do_diff(in_ids)

def do_diff(new_ids):
    tagged = set()
    off = 0
    while True:
        h = dict(DBH); h['Range'] = f'{off}-{off+999}'
        q = f'{U}/rest/v1/ai_dialogue_entry_categories?select=dialogue_id&category_id=eq.{CAT_ID}'
        b = json.load(urllib.request.urlopen(urllib.request.Request(q, headers=h)))
        if not b: break
        tagged.update(x['dialogue_id'] for x in b)
        if len(b) < 1000: break
        off += 1000
    new = set(new_ids)
    print(f'\n=== DIFF vs 現有 tag ===')
    print(f'現有 tag: {len(tagged)} | 新抓: {len(new)}')
    print(f'新增（原本沒標、現在 IN）: {len(new - tagged)}')
    print(f'移除（原本標了、現在 OUT）: {len(tagged - new)}')
    print(f'維持: {len(new & tagged)}')

if __name__ == '__main__':
    main()
