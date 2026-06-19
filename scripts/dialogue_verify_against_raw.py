# -*- coding: utf-8 -*-
"""稽核 dialogue_days 的克里希那回覆是否「忠於 raw 原話」。

背景：dialogue_days 的克里希那 turn 是用 LLM 從 ai_dialogues_gemini.response（原話）
重寫成乾淨散文。重寫應**保留完整論點與專名、忠實不增刪**。但偶爾 LLM 會：
  ① 失敗/漂走→產生與原話幾乎無關的內容；② 反過來「回應」原話而非重寫它
  （冒出「好的／以下是／我幫你整理／希望對你有幫助」等助理框架語）；③ 把實質抽空成空泛比喻。

做法：每天的克里希那 turn 依序對齊到當天 IN raw rows 的 response（build_day 是
user→ai 交替輸出，AI block 順序＝有 response 的 row 順序）。對每個 turn 算「published
克里希那文字的 CJK n-gram 有多少出現在它對應 raw response 裡」(containment)。
忠實改寫保留大量專名/詞彙→containment 高；憑空產生→趨近 0。再偵測助理框架語洩漏。

用法：
  python scripts/dialogue_verify_against_raw.py            # 全部，印每日分數 + 可疑 turn
  python scripts/dialogue_verify_against_raw.py 2026-03-05 # 單日細看（印 published vs raw 對照）
"""
import os, sys, re, json, html, urllib.request
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

SLUG = 'krishna-dialogues'
G = 5
LOW = 0.18          # turn containment 低於此 → 可疑（憑空/漂走）
START, END = '2026-01-13', '2026-04-18'
MEMBERSHIP = 'c:/tmp/krishna/final_manuscript.json'
# 助理框架語：克里希那回覆裡不該出現（代表 LLM 在「回應」而非「重寫」）
FRAME = ['好的，', '好的!', '以下是', '我幫你', '幫你整理', '整理如下', '希望這', '希望對你',
         '希望能幫', '作為一個', '作為一名', '身為一個', '很高興能', '我可以幫', '需要我',
         '如果你需要', '讓我來幫', '當然可以', '沒問題', '我已經', '以下我']

def env():
    e = {}
    for l in open(os.path.join(os.path.dirname(__file__), '..', '.env'), encoding='utf-8-sig'):
        l = l.strip()
        if '=' in l and not l.startswith('#'):
            k, v = l.split('=', 1); e[k.strip()] = v.strip()
    return e
E = env(); U = E['SUPABASE_URL']; K = E['SUPABASE_SERVICE_ROLE_KEY']
DBH = {'apikey': K, 'Authorization': 'Bearer ' + K}

def norm(s):
    return re.sub(r'[^一-鿿0-9A-Za-z]', '', s or '')

def containment(pub, raw):
    """published 文字的 n-gram 有多少比例出現在 raw 裡。"""
    p = norm(pub); r = norm(raw)
    if len(p) < G:
        return 1.0 if (p and p in r) else 0.0
    rs = set(r[i:i+G] for i in range(len(r)-G+1))
    grams = [p[i:i+G] for i in range(len(p)-G+1)]
    return sum(1 for g in grams if g in rs) / len(grams)

def fetch_days():
    q = (f'{U}/rest/v1/dialogue_days?select=day_date,html,n_turns&project_slug=eq.{SLUG}'
         f'&day_date=gte.{START}&day_date=lte.{END}&order=day_date.asc')
    return json.load(urllib.request.urlopen(urllib.request.Request(q, headers=DBH)))

def fetch_raw():
    ids = set(json.load(open(MEMBERSHIP, encoding='utf-8'))['ids']) if os.path.exists(MEMBERSHIP) else None
    rows, off = [], 0
    while True:
        h = dict(DBH); h['Range-Unit'] = 'items'; h['Range'] = f'{off}-{off+999}'
        q = (f'{U}/rest/v1/ai_dialogues_gemini?select=id,dialogue_date,dialogue_time,response'
             f'&dialogue_date=gte.{START}&dialogue_date=lte.{END}'
             f'&order=dialogue_date.asc,dialogue_time.asc.nullslast')
        b = json.load(urllib.request.urlopen(urllib.request.Request(q, headers=h)))
        if not b: break
        rows.extend(b)
        if len(b) < 1000: break
        off += 1000
    if ids is not None:
        rows = [r for r in rows if r['id'] in ids]
    by = defaultdict(list)
    for r in rows:
        if (r.get('response') or '').strip():
            by[r['dialogue_date']].append(r['response'])
    return by

def ai_turns(htmlstr):
    """抽出 html 裡每個克里希那 turn 的純文字（一個 turn = 從 speaker 段到下一個 speaker 段前）。"""
    # 切成段落
    paras = re.findall(r'<p>(.*?)</p>', htmlstr, flags=re.S)
    turns, cur, cur_is_ai = [], [], False
    for p in paras:
        m = re.match(r'\s*<strong[^>]*>\s*(克里[希須]那|阿周那)\s*[:：]\s*</strong>(.*)', p, flags=re.S)
        if m:
            if cur and cur_is_ai:
                turns.append(' '.join(cur))
            spk, rest = m.group(1), m.group(2)
            cur_is_ai = spk.startswith('克里')
            cur = [rest] if cur_is_ai else []
        else:
            if cur_is_ai:
                cur.append(p)
    if cur and cur_is_ai:
        turns.append(' '.join(cur))
    return [html.unescape(re.sub(r'<[^>]+>', '', t)).strip() for t in turns]

DOCX_DAYS = {f'2026-01-{d:02d}' for d in range(13, 19)}  # 1/13–1/18 來自手工 docx，不比對 raw

_h = None
def call_haiku(sysmsg, text):
    """LLM 忠實度裁判（走 Claude Max OAuth）。"""
    global _h
    import time, anthropic
    from pathlib import Path
    if _h is None:
        tok = json.loads((Path(os.environ.get('USERPROFILE', os.environ.get('HOME', ''))) / '.claude' / '.credentials.json').read_text(encoding='utf-8'))['claudeAiOauth']['accessToken']
        _h = anthropic.Anthropic(auth_token=tok, timeout=120.0, max_retries=2)
    for a in range(4):
        try:
            m = _h.messages.create(model='claude-haiku-4-5', max_tokens=400, system=sysmsg, messages=[{'role': 'user', 'content': text}])
            return ''.join(b.text for b in m.content if hasattr(b, 'text')).strip()
        except anthropic.RateLimitError:
            time.sleep(6 * (a + 1))
        except Exception:
            if a == 3: return None
            time.sleep(3 * (a + 1))
    return None

JUDGE_SYS = (
    '你在稽核一份「個人心靈對話錄」。其中 AI（克里希那）的每段回覆，'
    '原本應該是把「原始回覆(RAW)」重寫成乾淨溫暖的散文——忠實保留完整論點與專名、'
    '可改寫措辭、可凝練，但不可扭曲立場、不可張冠李戴、不可憑空新增主張、不可抽空實質。\n'
    '給你 RAW（原話）與 PUBLISHED（成品）。判斷 PUBLISHED 是否忠於 RAW。只回一行 JSON：\n'
    '{"verdict":"OK|DIVERGED|DISTORTED|META","why":"<20字內中文理由>"}\n'
    'OK＝忠實重寫（即使大幅改寫措辭也算，只要論點/歸屬/專名一致）；'
    'DIVERGED＝內容明顯對不上原話（談的不是同一件事/憑空生成）；'
    'DISTORTED＝同一主題但扭曲了立場或把話張冠李戴（誰說的、誰是什麼弄反）；'
    'META＝成品在「評論輸入」而非重寫（如說「你貼的是隱私政策/設定文字，不是對話」）。')

def judge(raw, pub):
    out = call_haiku(JUDGE_SYS, f'RAW：\n{raw[:3000]}\n\nPUBLISHED：\n{pub[:3000]}')
    if not out: return {'verdict': 'ERR', 'why': 'no response'}
    m = re.search(r'\{.*\}', out, flags=re.S)
    try:
        return json.loads(m.group(0)) if m else {'verdict': 'ERR', 'why': out[:30]}
    except Exception:
        return {'verdict': 'ERR', 'why': out[:30]}

def run_judge():
    """positional 對齊 turn↔raw response，對 containment<0.4 的 turn 跑 LLM 裁判。"""
    days = fetch_days(); raw_by = fetch_raw()
    suspects = []
    for d in days:
        date = d['day_date']
        if date in DOCX_DAYS:
            continue
        turns = ai_turns(d['html']); raws = raw_by.get(date, [])
        n = min(len(turns), len(raws))
        for i in range(n):
            c = containment(turns[i], raws[i])
            if c < 0.4:                       # 只送可疑的去裁判（高 containment 必忠實）
                suspects.append((date, i, c, raws[i], turns[i]))
        if len(turns) != len(raws):
            suspects.append((date, -1, -1, f'(turns={len(turns)} != raw_resp={len(raws)})', ''))
    print(f'送裁判 {len(suspects)} 個可疑 turn（含對不齊日）…\n', flush=True)
    bad = []
    for date, i, c, raw, pub in suspects:
        if i == -1:
            print(f'⚠️ {date} turn數對不齊：{raw}'); bad.append((date, i, 'COUNT', raw)); continue
        v = judge(raw, pub)
        verd = v.get('verdict')
        mark = '✅' if verd == 'OK' else '🛑'
        print(f'{mark} {date} turn{i} c={c:.2f} {verd}：{v.get("why","")}', flush=True)
        if verd not in ('OK', 'ERR'):
            bad.append((date, i, verd, v.get('why', '')))
    print('\n========== 確認異常 ==========')
    byday = defaultdict(list)
    for date, i, verd, why in bad: byday[date].append((i, verd, why))
    for date in sorted(byday):
        items = byday[date]
        print(f'● {date}：' + '；'.join(f'turn{i}={v}({w})' if i >= 0 else f'{v}({w})' for i, v, w in items))
    print(f'\n共 {len(byday)} 天、{len(bad)} 個 turn 異常')

def main():
    if '--judge' in sys.argv:
        return run_judge()
    day_arg = next((a for a in sys.argv[1:] if re.match(r'\d{4}-\d{2}-\d{2}$', a)), None)
    days = fetch_days()
    raw_by = fetch_raw()
    flagged = []
    for d in days:
        date = d['day_date']
        if day_arg and date != day_arg:
            continue
        turns = ai_turns(d['html'])
        raws = raw_by.get(date, [])
        # 對每個 published AI turn 找最佳對應 raw response 的 containment
        scores = []
        for i, t in enumerate(turns):
            best = max((containment(t, rr) for rr in raws), default=0.0)
            frame = [f for f in FRAME if f in t]
            scores.append((i, best, frame, t))
        if not scores:
            continue
        worst = min(s[1] for s in scores)
        avg = sum(s[1] for s in scores) / len(scores)
        bad = [s for s in scores if s[1] < LOW or s[2]]
        if day_arg:
            print(f'=== {date}  turns={len(turns)} raw_resp={len(raws)} avg={avg:.2f} worst={worst:.2f} ===')
            for i, sc, fr, t in scores:
                tag = '  ⚠️' if (sc < LOW or fr) else '    '
                fl = f' [框架語:{",".join(fr)}]' if fr else ''
                print(f'{tag} turn{i} containment={sc:.2f}{fl}')
                print(f'      published: {t[:160]}')
                # 印最佳對應 raw 開頭
                if raws:
                    bestraw = max(raws, key=lambda rr: containment(t, rr))
                    print(f'      raw      : {re.sub(chr(10)," ",bestraw)[:160]}')
            continue
        if bad:
            flagged.append((date, len(turns), avg, worst, bad))
    if day_arg:
        return
    flagged.sort(key=lambda x: x[3])
    print(f'\n稽核 {len(days)} 天；可疑 {len(flagged)} 天，共 {sum(len(f[4]) for f in flagged)} 個可疑 turn')
    print(f'（containment<{LOW} 或 含助理框架語）\n')
    for date, nt, avg, worst, bad in flagged:
        print(f'● {date}  turns={nt} avg={avg:.2f} worst={worst:.2f}  可疑 {len(bad)} 個')
        for i, sc, fr, t in bad:
            fl = f' [框架語:{",".join(fr)}]' if fr else ''
            print(f'    turn{i} c={sc:.2f}{fl}: {t[:90]}')

if __name__ == '__main__':
    main()
