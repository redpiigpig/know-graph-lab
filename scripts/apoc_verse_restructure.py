# -*- coding: utf-8 -*-
"""
典外文獻 逐節重建 driver（golden template = 以諾一書 1-enoch）。

把 /apocrypha 從「整頁 OCR」改為「章:節逐節 + 英文逐節對照」。
設計（user 2026-06-10 拍板）：**英文公版（Charles APOT 1913）的章:節 = 權威骨架**，
黃根春中文「貼上」骨架 1:1（節數跟英文、不過度切節、中英同 (ch,v) 對齊）。

純邏輯（解析/分頁/order_index/merge-clamp/coverage）在 scripts/apocrypha_verses.py
（pytest: scripts/tests/test_apocrypha_verses.py）。本檔只做 network/LLM/DB I/O。

引擎 NVIDIA-first（qwen3-next）：徹夜 jung/mueller 把 Gemini free pool 佔滿且
request 會 hang；deepseek-v4-flash reasoning 模型大 JSON 會 timeout。見 SKILL.md。

用法：
  python -X utf8 scripts/apoc_verse_restructure.py 1-enoch --en      # 英文骨架
  python -X utf8 scripts/apoc_verse_restructure.py 1-enoch --zh      # 中文貼骨架
  python -X utf8 scripts/apoc_verse_restructure.py 1-enoch --all
  python -X utf8 scripts/apoc_verse_restructure.py 1-enoch --zh --dry # 不寫 DB
"""
from __future__ import annotations
import os, sys, re, json, time, html, threading, urllib.request
import requests

sys.path.insert(0, os.path.dirname(__file__))
import apocrypha_verses as AV   # pure, tested helpers


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


# ── engine chain: NVIDIA(qwen→deepseek) → Gemini ───────────────────────
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
NMODELS = ['qwen/qwen3-next-80b-a3b-instruct', 'deepseek-ai/deepseek-v4-flash']
PREFER_NVIDIA = os.environ.get('APOC_ENGINE', 'nvidia').lower() != 'gemini'
_lock = threading.Lock()
_gnext = [0.0] * max(1, len(GKEYS))
_nnext = [0.0] * max(1, len(NKEYS))


def _pick(arr, interval):
    with _lock:
        i = min(range(len(arr)), key=lambda j: arr[j])
        now = time.time(); start = max(now, arr[i]); arr[i] = start + interval
        return i, start


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
                with _lock: _nnext[i] = time.time() + (60 if ex.code == 429 else 20)
            except Exception:
                with _lock: _nnext[i] = time.time() + 20
    return None


def _try_gemini(system, user, max_tokens, temperature):
    if not GKEYS: return None
    body = {'systemInstruction': {'parts': [{'text': system}]},
            'contents': [{'parts': [{'text': user}]}],
            'generationConfig': {'temperature': temperature, 'maxOutputTokens': max_tokens,
                                 'responseMimeType': 'application/json'}}
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
            with _lock: _gnext[i] = time.time() + (120 if ex.code == 429 else 20)
        except Exception:
            with _lock: _gnext[i] = time.time() + 20
    return None


def llm_json(system: str, user: str, max_tokens=16000, temperature=0.2) -> str:
    order = ([_try_nvidia, _try_gemini] if PREFER_NVIDIA else [_try_gemini, _try_nvidia])
    for fn in order:
        out = fn(system, user, max_tokens, temperature)
        if out is not None:
            return out
    raise RuntimeError('all engines failed (NVIDIA + Gemini)')


# ── per-doc source config ──────────────────────────────────────────────
DOC_SOURCES = {
    '1-enoch': {
        'en_version': 'charles_apot',
        'en_kind': 'ccel-enoch',
        'en_base': 'https://www.ccel.org/c/charles/otpseudepig/enoch/',
        'en_pages': 5,
        'book_name': '以諾一書 (1 Enoch)',
        'source_ebooks': ['基督教典外文獻-舊約篇-第1冊'],
    },
}


# ── English: CCEL → plain text → AV.parse_charles_chapters ──────────────
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}


def fetch_ccel_enoch(base, n_pages) -> str:
    full = []
    for n in range(1, n_pages + 1):
        r = requests.get(f'{base}ENOCH_{n}.HTM', headers=UA, timeout=40)
        r.encoding = r.apparent_encoding or 'utf-8'
        t = r.text
        t = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', t, flags=re.S | re.I)
        t = re.sub(r'</(p|div|br|tr|li|h\d)>', '\n', t, flags=re.I)
        t = re.sub(r'<br\s*/?>', '\n', t, flags=re.I)
        t = re.sub(r'<[^>]+>', ' ', t)
        t = html.unescape(t).replace('\r', '')
        full.append(t)
    s = '\n'.join(full)
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'\n[ \t]+', '\n', s)
    return s


def english_skeleton(slug) -> dict:
    cfg = DOC_SOURCES[slug]
    if cfg['en_kind'] != 'ccel-enoch':
        raise SystemExit(f'unknown en_kind {cfg["en_kind"]}')
    raw = fetch_ccel_enoch(cfg['en_base'], cfg['en_pages'])
    return AV.parse_charles_chapters(raw)


# ── DB I/O ─────────────────────────────────────────────────────────────
def db_get(path):
    r = requests.get(f'{REST}/{path}', headers=DBH, timeout=60); r.raise_for_status(); return r.json()


def db_delete_version(slug, version):
    r = requests.delete(f'{REST}/apocrypha_sections?doc_slug=eq.{slug}&version_code=eq.{version}',
                        headers={**DBH, 'Prefer': 'return=minimal'}, timeout=60)
    r.raise_for_status()


def db_insert_sections(rows):
    for i in range(0, len(rows), 200):
        batch = rows[i:i+200]
        r = requests.post(f'{REST}/apocrypha_sections', headers={**DBH, 'Prefer': 'return=minimal'},
                          data=json.dumps(batch), timeout=120)
        if not r.ok:
            print('INSERT FAIL', r.status_code, r.text[:400]); r.raise_for_status()


def db_patch_doc(slug, patch):
    r = requests.patch(f'{REST}/apocrypha_documents?slug=eq.{slug}',
                       headers={**DBH, 'Prefer': 'return=minimal'}, data=json.dumps(patch), timeout=60)
    r.raise_for_status()


# ── English flow ───────────────────────────────────────────────────────
def do_english(slug, dry=False):
    cfg = DOC_SOURCES[slug]
    print(f'[EN] fetch {cfg["en_kind"]} …')
    verses = english_skeleton(slug)
    nv = sum(len(v) for v in verses.values())
    print(f'[EN] parsed {len(verses)} chapters / {nv} verses')
    rows = AV.verse_rows(slug, cfg['en_version'], verses)
    if dry:
        for ch in [1, 6, 108]:
            if ch in verses:
                print(f'  {ch}:1  {verses[ch][min(verses[ch])][:80]!r}')
        return
    db_delete_version(slug, cfg['en_version'])
    db_insert_sections(rows)
    print(f'[EN] ingested {len(rows)} verse-rows as {cfg["en_version"]}')


# ── Chinese flow (map ZH onto EN skeleton) ─────────────────────────────
def load_zh_body(slug):
    """Full Chinese text from the durable snapshot (ebook_chunks is truncated to
    200-char previews; never read the mutable cct_zh). Returns body string."""
    snap = os.path.join(os.path.dirname(__file__), '_apoc_snapshots', f'{slug}.json')
    if not os.path.exists(snap):
        raise SystemExit(f'no snapshot {snap}; build it from cct_zh first')
    return json.load(open(snap, encoding='utf-8')).get('body', '')


def split_windows(body, max_chars=4000, overlap_chars=600):
    lines = body.split('\n')
    wins, cur, n = [], [], 0
    for ln in lines:
        cur.append(ln); n += len(ln) + 1
        if n >= max_chars:
            wins.append('\n'.join(cur))
            tail, tn = [], 0
            for t in reversed(cur):
                tail.insert(0, t); tn += len(t) + 1
                if tn >= overlap_chars: break
            cur, n = list(tail), tn
    if cur and ''.join(cur).strip() and '\n'.join(cur) not in wins:
        wins.append('\n'.join(cur))
    return wins


ZH_SYS = (
    '你是嚴謹的古典文獻編輯。下面給你一份「英文版聖經式骨架」（某卷典外文獻的章:節，含每節英文開頭內容），'
    '以及一段該卷的「中文 OCR 全文」。你的工作：把中文按照「英文骨架的章:節」切開、對位，輸出乾淨 JSON。\n'
    '規則：\n'
    '1. 只輸出 JSON：{"verses":[{"chapter":N,"verse":M,"text":"中文"}…],"last":[章,節]}。\n'
    '2. **章:節一律以英文骨架為準**：每一段中文要判斷它在講的內容對應到英文的哪一章哪一節，就標那個 (章,節)。'
    '英文骨架沒有的章/節，不要自己發明；中文若有多餘內容對不上，就併進最接近的那一節或捨去。'
    '**若某節找不到對應的中文，就不要輸出那一節；千萬不要把英文骨架的英文字句填進 text（text 永遠只放中文）。**\n'
    '3. text 要把 OCR 換行接回成通順段落，忠實保留每個字、標點、括號 ( )（譯者補字），不改寫不翻譯不加字。\n'
    '4. 刪除頁眉雜訊（「基督教典外文獻」「舊約篇 第N冊」）、純頁碼、純小標題行、頁末註釋定義行（如「1民 24:3。」）。\n'
    '5. 處理整個 window（通常跨多章）；只有結尾被切斷的半節才略過，並在 last 回報最後一節。\n'
    '6. 嚴禁 markdown 或解說，只有 JSON。'
)


def _anchor_block(skeleton, lo_ch, hi_ch):
    lines = []
    for ch in sorted(skeleton):
        if lo_ch <= ch <= hi_ch:
            v1 = skeleton[ch][min(skeleton[ch])]
            opening = ' '.join(re.sub(r'\s+', ' ', v1).strip().split()[:20])
            lines.append(f'  第 {ch} 章（共 {len(skeleton[ch])} 節）開頭：{opening}')
    return '\n'.join(lines)


def zh_prompt(skeleton, prev_cv, window_text):
    max_ch = max(skeleton)
    lo = max(1, (prev_cv[0] - 2) if prev_cv else 1)
    anchors = _anchor_block(skeleton, lo, lo + 24)
    prev = f'{prev_cv[0]}:{prev_cv[1]}' if prev_cv else '（從頭開始）'
    return (f'英文骨架共 {len(skeleton)} 章，最大章號 {max_ch}（章號不得超過）。\n'
            f'相關章節的英文開頭（用來判斷中文每段屬於哪一章哪一節）：\n{anchors}\n\n'
            f'上一個 window 大約處理到：{prev}。\n\n中文 OCR 全文（本 window）：\n\n{window_text}')


def do_chinese(slug, dry=False):
    skeleton = english_skeleton(slug)
    body = load_zh_body(slug)
    print(f'[ZH] skeleton {len(skeleton)} ch / {sum(len(v) for v in skeleton.values())} v | body {len(body)} chars')

    wins = split_windows(body)
    print(f'[ZH] {len(wins)} windows')
    frags = []
    prev_cv = None
    for wi, w in enumerate(wins):
        out = llm_json(ZH_SYS, zh_prompt(skeleton, prev_cv, w))
        try:
            j = json.loads(out)
        except Exception:
            m = re.search(r'\{.*\}', out, re.S)
            j = json.loads(m.group(0)) if m else {'verses': []}
        frag = {}
        for it in j.get('verses', []):
            try:
                ch = int(it['chapter']); v = int(it['verse'])
            except (KeyError, ValueError, TypeError):
                continue
            t = (it.get('text') or '').strip()
            if t:
                frag.setdefault(ch, {})[v] = t
        frags.append(frag)
        if j.get('last'):
            try: prev_cv = (int(j['last'][0]), int(j['last'][1]))
            except Exception: pass
        print(f'  win {wi+1}/{len(wins)}: +{sum(len(x) for x in frag.values())} verses, last={prev_cv}')

    verses = AV.merge_verse_windows(frags, skeleton)   # clamp to skeleton + keep-longest
    verses = AV.clean_zh_verses(verses)                # drop leaked English / leading verse nums
    rep = AV.coverage(skeleton, verses)
    print(f'[ZH] coverage: {rep}')
    if dry:
        for ch in [1, 3, 6, 9]:
            if ch in verses:
                print(f'  {ch}:1  {verses[ch][min(verses[ch])][:70]!r}')
        return
    rows = AV.verse_rows(slug, 'cct_zh', verses)
    db_delete_version(slug, 'cct_zh')
    db_insert_sections(rows)
    print(f'[ZH] ingested {len(rows)} verse-rows as cct_zh')


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
    print(f'engines: nvidia={len(NKEYS)} gemini={len(GKEYS)} prefer_nvidia={PREFER_NVIDIA}')
    if do_en: do_english(slug, dry=dry)
    if do_zh: do_chinese(slug, dry=dry)
    if not (do_en or do_zh):
        raise SystemExit('pass --en / --zh / --all')
