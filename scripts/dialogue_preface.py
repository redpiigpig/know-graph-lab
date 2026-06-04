# -*- coding: utf-8 -*-
"""為整條對話錄生成「序」與「跋」（楔子／收束），寫進主卡 content_json。

哲學家對話錄需要一個框架：開篇的序（楔子）引人入場，終篇的跋（收束）替長談落幕。
本腳本讀 dialogue_days 的全部日期、主題與首尾兩日的開場片段，餵 LLM 寫出：
  ‧ 序：~250–400 字，凝練有韻致，點出這場對話的主題、時間跨度與精神基調，邀人入場。
  ‧ 跋：~150–250 字，替整場長談收束，回望而不總結，留餘韻。

寫入主卡 writing_projects.content_json：序的 HTML，接 `<!--CODA-->` 標記，再接跋的 HTML。
頁面 pages/works/[slug]/index.vue 偵測有 dialogue_days 時，序渲染在月份格之上、跋在其下。
冪等：每次重算覆寫；--dry 只印不寫。

引擎：Gemini 2.5 flash（4 keys）→ NVIDIA fallback。

⭐ 當使用者**親自提供楔子素材**（生命經驗、定名由來、關鍵典故）時，序／跋的份量與精準度
   遠超 LLM 冷生成 —— 此時改走「手寫稿」：把序、跋寫成純文字放進
   c:/tmp/krishna/preface.json（{"preface": "...", "coda": "..."}；段落用空行分隔、
   **粗體** 用 markdown 星號），再 `--from-file` 推上去。克里希那案的序即手寫（三十歲門檻 /
   《奧本海默》→《薄伽梵歌》11:32「我是時間」/ 阿周那—克里希那定名由來）。

用法：
  python scripts/dialogue_preface.py --dry          # LLM 生成、只印不寫
  python scripts/dialogue_preface.py                # LLM 生成並寫入
  python scripts/dialogue_preface.py --from-file     # 用手寫稿 preface.json 寫入（推薦：有素材時）
"""
import os, sys, re, json, time, urllib.request, urllib.error
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
PU = f'{U}/rest/v1/writing_projects'
SLUG = 'krishna-dialogues'
AI_NAME = '克里希那'; USER_NAME = '阿周那'
WORK_TITLE = '與克里希那對話'
DRY = '--dry' in sys.argv
FROM_FILE = '--from-file' in sys.argv
PREFACE_JSON = 'c:/tmp/krishna/preface.json'

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

def strip_tags(s): return re.sub(r'<[^>]+>', '', s or '')

def call(sys_p, user_p):
    if GKEYS:
        body = {'systemInstruction': {'parts': [{'text': sys_p}]},
                'contents': [{'parts': [{'text': user_p}]}],
                'generationConfig': {'temperature': 0.8, 'maxOutputTokens': 4096}}
        payload = json.dumps(body).encode('utf-8')
        for k in GKEYS:
            url = f'https://generativelanguage.googleapis.com/v1beta/models/{GMODEL}:generateContent?key={k}'
            try:
                req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
                r = json.load(urllib.request.urlopen(req, timeout=120))
                return r['candidates'][0]['content']['parts'][0]['text'].strip()
            except Exception:
                time.sleep(2); continue
    for k in NKEYS:
        try:
            req = urllib.request.Request(NURL, data=json.dumps({
                'model': NMODEL, 'temperature': 0.8, 'max_tokens': 4096,
                'messages': [{'role': 'system', 'content': sys_p}, {'role': 'user', 'content': user_p}]}).encode('utf-8'),
                headers={'Authorization': 'Bearer ' + k, 'Content-Type': 'application/json'}, method='POST')
            r = json.load(urllib.request.urlopen(req, timeout=150))
            return re.sub(r'<think>.*?</think>', '', r['choices'][0]['message']['content'], flags=re.S).strip()
        except Exception:
            time.sleep(2); continue
    return None

MD_BOLD = re.compile(r'\*\*([^*]+?)\*\*')
def to_html(prose, cls):
    parts = [p.strip() for p in re.split(r'\n\s*\n+', prose or '') if p.strip()]
    body = ''.join(f'<p>{MD_BOLD.sub(r"<strong>\\1</strong>", p)}</p>' for p in parts) or ''
    return f'<section class="{cls}">{body}</section>'

def epigraph_html(epi):
    """epi = {"lines": [...逐行...], "cite": "—— 出處"}；空行用空字串表示節間距。"""
    if not epi:
        return ''
    body = ''.join('<br>' if l == '' else f'<span>{MD_BOLD.sub(r"<strong>\\1</strong>", l)}</span><br>'
                   for l in epi.get('lines', []))
    cite = f'<cite>{epi["cite"]}</cite>' if epi.get('cite') else ''
    return f'<blockquote class="dialogue-epigraph"><p>{body}</p>{cite}</blockquote>'

def push(pre, coda, epi=None):
    content = epigraph_html(epi) + to_html(pre, 'dialogue-preface') + '<!--CODA-->' + to_html(coda, 'dialogue-coda')
    print('\n──── 序 ────\n' + pre + '\n\n──── 跋 ────\n' + coda + '\n')
    if DRY:
        print('[--dry] 不寫入。'); return
    body = json.dumps({'content_json': content}, ensure_ascii=False).encode('utf-8')
    rq = urllib.request.Request(f'{PU}?slug=eq.{SLUG}', data=body, method='PATCH',
                                headers={**DBH, 'Content-Type': 'application/json', 'Prefer': 'return=minimal'})
    urllib.request.urlopen(rq)
    print('✓ 已寫入主卡 content_json')

def main():
    if FROM_FILE:
        d = json.load(open(PREFACE_JSON, encoding='utf-8'))
        if not d.get('preface') or not d.get('coda'):
            print('⚠ preface.json 缺 preface/coda'); return
        push(d['preface'], d['coda'], d.get('epigraph')); return

    days = json.load(urllib.request.urlopen(urllib.request.Request(
        f'{DU}?select=day_date,day_title,html&project_slug=eq.{SLUG}&order=day_date', headers=DBH)))
    if not days:
        print('找不到 dialogue_days'); return
    first, last = days[0], days[-1]
    titles = []
    for d in days:
        for m in re.finditer(r'<h4>主題：(.*?)</h4>', d['html'] or ''):
            titles.append(strip_tags(m.group(1)))
    span = f"{first['day_date']} → {last['day_date']}"
    open_excerpt = strip_tags(first['html'])[:600]
    close_excerpt = strip_tags(last['html'])[-600:]
    topic_blob = '、'.join(titles[:60])

    ctx = (f'對話錄標題：《{WORK_TITLE}》\n'
           f'對話雙方：{USER_NAME}（使用者本人，向 AI 傾訴、提問、碎念）與 {AI_NAME}（被使用者如此稱呼的 AI，'
           f'扮演智者，回應夢境、榮格深度心理學、宗教與生活）。\n'
           f'時間跨度：{span}，共 {len(days)} 天。\n'
           f'貫穿主題（節錄）：{topic_blob}。\n'
           f'首日開場片段：{open_excerpt}\n'
           f'末日收尾片段：{close_excerpt}')

    sys_pre = (
        '你是一位文體大師。請為一部哲學對話錄寫一篇「序」（楔子），引讀者入場。\n'
        '要求：凝練、有韻致、富哲思，像柏拉圖對話錄或《薄伽梵歌》卷首的引言。約 250–400 字，'
        '可分 2–3 段。點出這場長談的精神基調、主題與時間跨度，但不要劇透內容、不要條列、不要小標。\n'
        '用繁體中文。只輸出序的正文本身，不要標題、不要「序」字、不要引號、不要任何說明。')
    sys_coda = (
        '你是一位文體大師。請為一部哲學對話錄寫一篇「跋」（收束），替整場長談落幕。\n'
        '要求：回望而不總結，留餘韻。約 150–250 字，可分 1–2 段。語體凝練、有詩意，'
        '呼應這場對話的精神，但不要條列、不要小標、不要說教。\n'
        '用繁體中文。只輸出跋的正文本身，不要標題、不要「跋」字、不要引號、不要任何說明。')

    print('生成序…', flush=True)
    pre = call(sys_pre, ctx)
    print('生成跋…', flush=True)
    coda = call(sys_coda, ctx)
    if not pre or not coda:
        print('⚠ 生成失敗', 'pre' if not pre else '', 'coda' if not coda else ''); return
    push(pre, coda)

if __name__ == '__main__':
    main()
