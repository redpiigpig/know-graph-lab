# -*- coding: utf-8 -*-
"""
典外文獻 逐節重建 pipeline（golden template = 以諾一書 1-enoch）。

把 /apocrypha 既有「整頁 OCR」的 cct_zh sections 重建成「章:節」逐節結構，
並補進公有領域英譯（Charles APOT 1913 / M.R. James 1924）做逐節對照。

對齊鍵：order_index = chapter*1000 + verse （中英共用 → reader 同列對照）

三件事：
  1. 英文：抓 CCEL 結構化 HTML（已有 ch:v）→ 解析 (ch, v, text_en) → ingest charles_apot
  2. 中文：把既有 cct_zh 整頁 OCR 的「正文」段落，用 Gemini 重排成逐節 JSON
          （清頁眉、合併跨頁、依英文章節結構定章號）→ ingest cct_zh（逐節）
  3. 簡介：把正文前的「導論／簡介」段落用 Gemini 萃取乾淨 → documents.intro_zh

引擎：Gemini 2.5 flash（多 key 輪流）。見 [[feedback_engine_nvidia_no_haiku]]。

用法：
  python -X utf8 scripts/apoc_verse_restructure.py 1-enoch --en          # 只做英文
  python -X utf8 scripts/apoc_verse_restructure.py 1-enoch --zh          # 只做中文+簡介
  python -X utf8 scripts/apoc_verse_restructure.py 1-enoch --all         # 全做
  python -X utf8 scripts/apoc_verse_restructure.py 1-enoch --zh --dry    # 中文不寫 DB，只印
"""
from __future__ import annotations
import os, sys, re, json, time, html, threading, urllib.request
import requests

# ── env ───────────────────────────────────────────────────────────────
def _env():
    e = {}
    p = os.path.join(os.path.dirname(__file__), '..', '.env')
    for l in open(p, encoding='utf-8-sig'):
        l = l.strip()
        if '=' in l and not l.startswith('#'):
            k, v = l.split('=', 1); e[k.strip()] = v.strip().strip('"').strip("'")
    return e
E = _env()
URL = E['SUPABASE_URL']; KEY = E['SUPABASE_SERVICE_ROLE_KEY']
DBH = {'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json'}
REST = f'{URL}/rest/v1'

# ── gemini ────────────────────────────────────────────────────────────
def _gemini_keys():
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
GKEYS = _gemini_keys()
GMODEL = 'gemini-2.5-flash'
NKEYS = [E[k] for k in sorted(E) if k.upper().startswith('NVIDIA_API_KEY') and E[k]]
NURL = 'https://integrate.api.nvidia.com/v1/chat/completions'
# qwen3-next is fast & non-reasoning (good for big JSON); deepseek-v4-flash is a
# slow reasoning model that times out on large outputs → keep it last-resort only.
NMODELS = ['qwen/qwen3-next-80b-a3b-instruct', 'deepseek-ai/deepseek-v4-flash']
_glock = threading.Lock()
_gnext = [0.0] * max(1, len(GKEYS))
_nnext = [0.0] * max(1, len(NKEYS))

def _pick(arr, interval):
    with _glock:
        i = min(range(len(arr)), key=lambda j: arr[j])
        now = time.time(); start = max(now, arr[i]); arr[i] = start + interval
        return i, start

# Overnight jung/mueller loops saturate the free Gemini pool (requests HANG, not
# just 429), so default to NVIDIA-first here. Override with APOC_ENGINE=gemini.
PREFER_NVIDIA = os.environ.get('APOC_ENGINE', 'nvidia').lower() != 'gemini'

def _try_gemini(system, user, max_tokens, temperature):
    if not GKEYS: return None
    body = {
        'systemInstruction': {'parts': [{'text': system}]},
        'contents': [{'parts': [{'text': user}]}],
        'generationConfig': {'temperature': temperature, 'maxOutputTokens': max_tokens,
                             'responseMimeType': 'application/json'},
    }
    payload = json.dumps(body).encode('utf-8')
    for _ in range(2):
        i, start = _pick(_gnext, 4.5)
        d = start - time.time()
        if d > 0: time.sleep(d)
        u = f'https://generativelanguage.googleapis.com/v1beta/models/{GMODEL}:generateContent?key={GKEYS[i]}'
        try:
            req = urllib.request.Request(u, data=payload,
                                         headers={'Content-Type': 'application/json'}, method='POST')
            r = json.load(urllib.request.urlopen(req, timeout=45))
            return r['candidates'][0]['content']['parts'][0]['text'].strip()
        except urllib.error.HTTPError as ex:
            with _glock: _gnext[i] = time.time() + (120 if ex.code == 429 else 20)
        except Exception:
            with _glock: _gnext[i] = time.time() + 20
    return None

def _try_nvidia(system, user, max_tokens, temperature):
    if not NKEYS: return None
    mt = min(max_tokens, 16000)
    for model in NMODELS:
        for _ in range(len(NKEYS) + 1):
            i, start = _pick(_nnext, 5.0)
            d = start - time.time()
            if d > 0: time.sleep(d)
            try:
                req = urllib.request.Request(NURL, data=json.dumps({
                    'model': model, 'temperature': temperature, 'max_tokens': mt,
                    'response_format': {'type': 'json_object'},
                    'messages': [{'role': 'system', 'content': system},
                                 {'role': 'user', 'content': user}]}).encode('utf-8'),
                    headers={'Authorization': 'Bearer ' + NKEYS[i], 'Content-Type': 'application/json'},
                    method='POST')
                r = json.load(urllib.request.urlopen(req, timeout=180))
                txt = r['choices'][0]['message']['content']
                return re.sub(r'<think>.*?</think>', '', txt, flags=re.S).strip()
            except urllib.error.HTTPError as ex:
                with _glock: _nnext[i] = time.time() + (60 if ex.code == 429 else 20)
            except Exception:
                with _glock: _nnext[i] = time.time() + 20
    return None

def gemini(system: str, user: str, max_tokens=32000, temperature=0.2) -> str:
    """Engine chain. NVIDIA-first by default (Gemini pool saturated overnight)."""
    order = ([_try_nvidia, _try_gemini] if PREFER_NVIDIA else [_try_gemini, _try_nvidia])
    out = None
    for fn in order:
        out = fn(system, user, max_tokens, temperature)
        if out is not None:
            return out
    raise RuntimeError('all engines failed (Gemini + NVIDIA)')

# ── per-doc source config ─────────────────────────────────────────────
# english: ('ccel-enoch', base_url, n_pages)  — parser keyed by 'kind'
DOC_SOURCES = {
    '1-enoch': {
        'en_version': 'charles_apot',
        'en_kind': 'ccel-enoch',
        'en_base': 'https://www.ccel.org/c/charles/otpseudepig/enoch/',
        'en_pages': 5,
        'book_name': '以諾一書 (1 Enoch)',
        # Which 黃根春 volume(s) this doc lives in (immutable OCR source). We
        # re-derive the original page-OCR from ebook_chunks every run, never from
        # the (overwritten) cct_zh rows — so the script is safely re-runnable.
        'source_ebooks': ['基督教典外文獻-舊約篇-第1冊'],
    },
}

# ── English: CCEL Charles parser ──────────────────────────────────────
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def fetch_ccel_enoch(base, n_pages) -> str:
    full = []
    for n in range(1, n_pages + 1):
        r = requests.get(f'{base}ENOCH_{n}.HTM', headers=UA, timeout=40)
        r.encoding = r.apparent_encoding or 'utf-8'
        t = r.text
        t = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', t, flags=re.S | re.I)
        # block tags → newline (preserve poetry stichs), inline → space
        t = re.sub(r'</(p|div|br|tr|li|h\d)>', '\n', t, flags=re.I)
        t = re.sub(r'<br\s*/?>', '\n', t, flags=re.I)
        t = re.sub(r'<[^>]+>', ' ', t)
        t = html.unescape(t)
        t = t.replace('\r', '')
        full.append(t)
    s = '\n'.join(full)
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'\n[ \t]+', '\n', s)
    return s

def parse_charles_enoch(text: str) -> dict[int, dict[int, str]]:
    """Return {chapter: {verse: text}} from CCEL Charles 1 Enoch."""
    parts = re.split(r'\[\s*Chapter\s+(\d+)\s*\]', text)
    out: dict[int, dict[int, str]] = {}
    for i in range(1, len(parts), 2):
        ch = int(parts[i]); body = parts[i + 1]
        # accept only sequential verse markers (1,2,3,...) to avoid numerals in prose
        nums = list(re.finditer(r'(?<![\d.])(\d{1,3})(?![\d])', body))
        seq = []; expect = 1
        for m in nums:
            if int(m.group(1)) == expect:
                seq.append((expect, m.start(), m.end())); expect += 1
        vmap = {}
        if not seq:
            # single-verse chapter: Charles omits the "1" marker → whole body is v1
            txt = re.sub(r'\n{2,}', '\n', body).strip()
            txt = re.sub(r'[ \t]*\n[ \t]*', '\n', txt)
            if txt:
                vmap[1] = txt
        for j, (v, s, e) in enumerate(seq):
            end = seq[j + 1][1] if j + 1 < len(seq) else len(body)
            txt = body[e:end].strip()
            # collapse blank-line runs (poetry) to single newline, trim
            txt = re.sub(r'\n{2,}', '\n', txt).strip()
            txt = re.sub(r'[ \t]*\n[ \t]*', '\n', txt)
            if txt:
                vmap[v] = txt
        if vmap:
            out[ch] = vmap
    return out

# ── DB helpers ────────────────────────────────────────────────────────
def db_get(path):
    r = requests.get(f'{REST}/{path}', headers=DBH, timeout=60); r.raise_for_status(); return r.json()

def db_delete_version(slug, version):
    r = requests.delete(f'{REST}/apocrypha_sections?doc_slug=eq.{slug}&version_code=eq.{version}',
                        headers={**DBH, 'Prefer': 'return=minimal'}, timeout=60)
    r.raise_for_status()

def db_insert_sections(rows):
    for i in range(0, len(rows), 300):
        batch = rows[i:i+300]
        r = requests.post(f'{REST}/apocrypha_sections', headers={**DBH, 'Prefer': 'return=minimal'},
                          data=json.dumps(batch), timeout=120)
        if not r.ok:
            print('INSERT FAIL', r.status_code, r.text[:400]); r.raise_for_status()

def db_patch_doc(slug, patch):
    r = requests.patch(f'{REST}/apocrypha_documents?slug=eq.{slug}',
                       headers={**DBH, 'Prefer': 'return=minimal'}, data=json.dumps(patch), timeout=60)
    r.raise_for_status()

def make_rows(slug, version, verses: dict[int, dict[int, str]], footnotes_by_cv=None):
    rows = []
    for ch in sorted(verses):
        for v in sorted(verses[ch]):
            txt = verses[ch][v]
            row = {
                'doc_slug': slug, 'version_code': version,
                'order_index': ch * 1000 + v,
                'chapter': ch, 'verse': v,
                'section_label': f'{ch}:{v}',
                'text': txt, 'char_count': len(txt),
            }
            fn = (footnotes_by_cv or {}).get((ch, v))
            if fn:
                row['footnote_defs'] = fn
            rows.append(row)
    return rows

# ── English flow ──────────────────────────────────────────────────────
def do_english(slug, dry=False):
    cfg = DOC_SOURCES[slug]
    print(f'[EN] fetch {cfg["en_kind"]} …')
    if cfg['en_kind'] == 'ccel-enoch':
        raw = fetch_ccel_enoch(cfg['en_base'], cfg['en_pages'])
        verses = parse_charles_enoch(raw)
    else:
        raise SystemExit(f'unknown en_kind {cfg["en_kind"]}')
    nv = sum(len(v) for v in verses.values())
    print(f'[EN] parsed {len(verses)} chapters / {nv} verses')
    rows = make_rows(slug, cfg['en_version'], verses)
    if dry:
        for ch in [1, 6, 108]:
            if ch in verses:
                v1 = sorted(verses[ch])[0]
                print(f'  {ch}:{v1}  {verses[ch][v1][:90]!r}')
        return
    db_delete_version(slug, cfg['en_version'])
    db_insert_sections(rows)
    print(f'[EN] ingested {len(rows)} verse-rows as {cfg["en_version"]}')

# ── Chinese flow ──────────────────────────────────────────────────────
HEADER_NOISE = re.compile(r'^(基督教典外文獻|[舊黃]約篇|新約篇|第[一二三四五六七八九十\d]+冊).*$', re.M)
# Footnote definition lines, e.g. "1民 24:3 與跟著的一節經文。" "3但 4:13, 17, 23。"
# = digit(s) + 1-3 CJK (book abbrev) + digits + ：/: + digits.  Distinguished from a
# verse start ("1 你們要觀看…") which has a space + CJK and no scripture ref.
FOOTNOTE_DEF = re.compile(r'^\d{1,3}\s?[一-鿿]{1,4}\s*\d+\s*[:：]\s*\d.*$', re.M)

def load_zh_body(slug):
    """Return (intro_sections[list[str]], body_text[str]).

    Source priority:
      1. scripts/_apoc_snapshots/{slug}.json — a durable full-text snapshot
         (used when ebook_chunks holds only 200-char previews). intro empty →
         we keep the already-extracted documents.intro_zh untouched.
      2. the IMMUTABLE ebook_chunks source (classify + clean), split at 文本.
    Never reads the mutable cct_zh, so the script is safely re-runnable."""
    snap = os.path.join(os.path.dirname(__file__), '_apoc_snapshots', f'{slug}.json')
    if os.path.exists(snap):
        data = json.load(open(snap, encoding='utf-8'))
        return data.get('intro_sections', []), data.get('body', '')

    import importlib
    ING = importlib.import_module('ingest_apocrypha_zh')
    cfg = DOC_SOURCES[slug]
    texts: list[str] = []
    for ebname in cfg['source_ebooks']:
        eid = ING.EBOOKS[ebname]
        chunks = ING.fetch_chunks(eid)
        slugs = ING.classify_with_inheritance(chunks)
        for c, s in zip(chunks, slugs):
            if s == slug:
                t = ING.clean_text(c.get('content') or '')
                if t.strip():
                    texts.append(t)
    # body starts at first section containing a standalone 文本 heading line
    body_start = None
    for i, t in enumerate(texts):
        if re.search(r'(?m)^\s*文\s*本\s*$', t) or t.lstrip().startswith('文本'):
            body_start = i; break
    if body_start is None:
        # fallback: first section with a leading "1 " verse run
        for i, t in enumerate(texts):
            if re.search(r'(?m)^\s*1\s', t):
                body_start = max(0, i); break
    if body_start is None:
        body_start = 0
    intro = texts[:body_start]
    body = '\n'.join(texts[body_start:])
    body = HEADER_NOISE.sub('', body)
    body = FOOTNOTE_DEF.sub('', body)
    body = re.sub(r'\n{3,}', '\n\n', body)
    return intro, body

ZH_SYS = (
    '你是嚴謹的古典文獻編輯，正在把一份 OCR 出來的中文典外文獻「整頁文字」重排成「逐節」結構。'
    '輸入是繁體中文 OCR，內含阿拉伯數字的節號（行首的 1, 2, 3…），章與章之間節號會重新從 1 起算。'
    '你的工作：把文字切成一節一節，判斷每節所屬的「章」與「節」號，並輸出乾淨 JSON。\n'
    '規則：\n'
    '1. 只輸出 JSON：{"verses":[{"chapter":N,"verse":M,"text":"…"}…],"last":[章,節]}。\n'
    '2. text 要把 OCR 的換行接回成通順段落（去掉因排版產生的斷行），但忠實保留每一個字、標點、'
    '括號 ( )（這是譯者補字，務必保留）。不要改寫、不要翻譯、不要加字。\n'
    '3. 章號判斷【最重要】：下方會給你「英文各章開頭內容」。請依「內容意義」把每一節中文對應到'
    '正確的英文章號——即這節中文在講的事，對應到哪一章英文，就標那一章。不要只靠 OCR 的節號重置來數章，'
    '因為中文短章可能被 OCR 合併或錯切。例如中文若在講「米迦勒、加百列從天上往下看見血」，那對應的是'
    '英文裡「Michael…looked down…saw blood」那一章，就用那個章號。中文的節號（行首數字）通常仍對應'
    '該章的節次，可沿用；但章號一律以內容對齊英文為準。\n'
    '4. 刪除頁眉雜訊（如「基督教典外文獻」「舊約篇 第一冊」）、純頁碼、以及小標題行'
    '（如「義人和孤兒」「以諾的比喻」這類非經文的段落標題，不要當成一節）。\n'
    '5. 註腳：頁末若有「1民 24:3。」「3但 4:13。」這類註釋定義行（行首數字+經文出處），'
    '不要放進 text。改成把該章的註釋收進對應節的 "footnotes":{"1":"民 24:3。",…}（鍵為註號字串）。'
    '若無法判斷註號屬於哪一節，就掛在該章第 1 節。\n'
    '6. 務必處理「整個 window」裡的所有節（通常會跨好幾章，例如第 1 章到第 5 章），'
    '不要只做第一章就停下。只有當 window 最後結尾那一節明顯被切斷、不完整時，才略過該節，'
    '並在 last 回報你最後輸出的那一節 [章, 節]。\n'
    '7. 嚴禁輸出 markdown 或解說，只有 JSON。'
)

def _en_anchor(text: str, n=22) -> str:
    """First ~n words of an English verse, single line, as a content anchor."""
    t = re.sub(r'\s+', ' ', text).strip()
    words = t.split(' ')
    return ' '.join(words[:n])

def zh_window_prompt(skeleton, prev_cv, window_text, anchors):
    sk = ', '.join(f'{ch}:{n}' for ch, n in skeleton)
    prev = f'{prev_cv[0]}:{prev_cv[1]}' if prev_cv else '（從頭開始）'
    anchor_lines = '\n'.join(f'  第 {ch} 章開頭：{txt}' for ch, txt in anchors)
    return (f'英文版章節結構（章:該章節數，共 {len(skeleton)} 章，最大章號 {skeleton[-1][0]}）：{sk}\n\n'
            f'英文各章開頭內容（用來依「內容」判斷中文每節屬於第幾章）：\n{anchor_lines}\n\n'
            f'⚠ 本書只有 {skeleton[-1][0]} 章，章號不得超過這個數字。\n'
            f'上一個 window 大約處理到：{prev}。\n\n'
            f'以下是要重排的中文 OCR 文字：\n\n{window_text}')

def split_windows(body, max_chars=4000, overlap_chars=500):
    """Split body into ~max_chars line-aligned windows with a small tail overlap,
    so a verse straddling a boundary is still captured whole in the next window.
    Duplicate (ch,v) across overlapping windows are merged keep-longest later."""
    lines = body.split('\n')
    wins, cur, n = [], [], 0
    for ln in lines:
        cur.append(ln); n += len(ln) + 1
        if n >= max_chars:
            wins.append('\n'.join(cur))
            # carry the tail lines (~overlap_chars) into the next window
            tail, tn = [], 0
            for t in reversed(cur):
                tail.insert(0, t); tn += len(t) + 1
                if tn >= overlap_chars: break
            cur, n = list(tail), tn
    if cur and ''.join(cur).strip() and '\n'.join(cur) not in wins:
        wins.append('\n'.join(cur))
    return wins

def do_chinese(slug, dry=False):
    cfg = DOC_SOURCES[slug]
    # need English skeleton to guide chapter assignment
    raw = fetch_ccel_enoch(cfg['en_base'], cfg['en_pages'])
    en = parse_charles_enoch(raw)
    skeleton = [(ch, len(en[ch])) for ch in sorted(en)]

    intro_sections, body = load_zh_body(slug)
    print(f'[ZH] intro sections: {len(intro_sections)} | body chars: {len(body)}')

    # ── intro extraction ──
    intro_raw = '\n\n'.join(intro_sections)
    intro_raw = HEADER_NOISE.sub('', intro_raw)
    intro_sys = (
        '你是文獻編輯。下面是某卷典外文獻「正文之前」的 OCR 文字，混雜了：整本書的目錄、'
        '該部別（如「啟示文學」）的總簡介、以及「這一卷書」本身的簡介／導論。'
        f'請只萃取「{cfg["book_name"]}」這一卷書本身的簡介／導論，重排成通順的繁體中文段落'
        '（接回 OCR 斷行、刪頁眉頁碼與目錄、刪其他卷的內容）。只輸出 JSON：{"intro":"…"}。忠實保留原文字句，不改寫不翻譯。'
    )
    intro_zh = ''
    if intro_raw.strip():
        try:
            j = json.loads(gemini(intro_sys, intro_raw, max_tokens=8000))
            intro_zh = (j.get('intro') or '').strip()
        except Exception as ex:
            print('[ZH] intro extract failed:', ex)
    else:
        print('[ZH] no intro sections (snapshot mode) — keeping existing intro_zh')
    print(f'[ZH] intro_zh: {len(intro_zh)} chars — {intro_zh[:80]!r}')

    # English content anchors (chapter → first verse opening) for content-based
    # chapter assignment.
    max_ch = skeleton[-1][0]
    all_anchors = [(ch, _en_anchor(en[ch].get(1, next(iter(en[ch].values()))))) for ch in sorted(en)]

    # ── body → verses ──
    wins = split_windows(body)
    print(f'[ZH] {len(wins)} windows')
    verses: dict[int, dict[int, str]] = {}
    footnotes_by_cv: dict[tuple, dict] = {}
    prev_cv = None
    for wi, w in enumerate(wins):
        # anchor slice: a few chapters before the cursor through ~22 ahead
        lo = max(1, (prev_cv[0] - 2) if prev_cv else 1)
        anchors = [a for a in all_anchors if lo <= a[0] <= lo + 24]
        out = gemini(ZH_SYS, zh_window_prompt(skeleton, prev_cv, w, anchors), max_tokens=32000)
        try:
            j = json.loads(out)
        except Exception:
            m = re.search(r'\{.*\}', out, re.S)
            j = json.loads(m.group(0)) if m else {'verses': []}
        vlist = j.get('verses', [])
        for it in vlist:
            try:
                ch = int(it['chapter']); v = int(it['verse'])
            except (KeyError, ValueError, TypeError):
                continue
            if ch < 1 or ch > max_ch or v < 1:   # clamp to real chapter range
                continue
            txt = (it.get('text') or '').strip()
            if not txt: continue
            prev = verses.get(ch, {}).get(v)
            if prev is None or len(txt) > len(prev):   # overlap → keep longest
                verses.setdefault(ch, {})[v] = txt
            fn = it.get('footnotes')
            if fn: footnotes_by_cv[(ch, v)] = fn
        if j.get('last'):
            prev_cv = tuple(j['last'])
        nv = sum(len(x) for x in verses.values())
        print(f'  win {wi+1}/{len(wins)}: +{len(vlist)} verses (total {nv}), last={prev_cv}')

    nv = sum(len(v) for v in verses.values())
    print(f'[ZH] total {len(verses)} chapters / {nv} verses')
    if dry:
        for ch in sorted(verses)[:2] + sorted(verses)[-1:]:
            for v in sorted(verses[ch])[:2]:
                print(f'  {ch}:{v}  {verses[ch][v][:80]!r}')
        return
    rows = make_rows(slug, 'cct_zh', verses, footnotes_by_cv)
    db_delete_version(slug, 'cct_zh')
    db_insert_sections(rows)
    if intro_zh:
        db_patch_doc(slug, {'intro_zh': intro_zh})
    print(f'[ZH] ingested {len(rows)} verse-rows as cct_zh + intro_zh')

# ── main ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    slug = args[0]
    dry = '--dry' in args
    do_en = '--en' in args or '--all' in args
    do_zh = '--zh' in args or '--all' in args
    if slug not in DOC_SOURCES:
        raise SystemExit(f'no source config for {slug}; add to DOC_SOURCES')
    print(f'gemini keys: {len(GKEYS)}')
    if do_en: do_english(slug, dry=dry)
    if do_zh: do_chinese(slug, dry=dry)
    if not (do_en or do_zh):
        raise SystemExit('pass --en / --zh / --all')
