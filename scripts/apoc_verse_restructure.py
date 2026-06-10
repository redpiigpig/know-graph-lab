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
    # OT pseudepigrapha with a Charles APOT (CCEL) English edition.
    '1-enoch': {
        'en_version': 'charles_apot', 'en_kind': 'ccel-enoch',
        'en_base': 'https://www.ccel.org/c/charles/otpseudepig/enoch/', 'en_pages': 5,
        'book_name': '以諾一書 (1 Enoch)',
    },
    # Deuterocanon: skeleton from our own bible_verses (KJVA, correct ch:v).
    'sirach': {
        'en_version': 'kjva_apoc', 'en_kind': 'bible',
        'bible_book': 'sir', 'bible_version': 'kjva',
        'book_name': '德訓篇 / 便西拉智訓 (Sirach)',
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


def bible_skeleton(book, version) -> dict:
    """Skeleton from our own bible_verses table (deuterocanon already ingested via
    /scripture): {chapter: {verse: text}}. Paged to beat the 1000-row cap."""
    out: dict = {}
    off = 0
    while True:
        rows = db_get(f'bible_verses?book_code=eq.{book}&version_code=eq.{version}'
                      f'&select=chapter,verse,text&order=chapter,verse&limit=1000&offset={off}')
        if not rows:
            break
        for r in rows:
            t = (r['text'] or '').strip()
            if t:
                out.setdefault(r['chapter'], {})[r['verse']] = t
        if len(rows) < 1000:
            break
        off += 1000
    return out


def english_skeleton(slug) -> dict:
    cfg = DOC_SOURCES[slug]
    kind = cfg['en_kind']
    if kind == 'ccel-enoch':
        return AV.parse_charles_chapters(fetch_ccel_enoch(cfg['en_base'], cfg['en_pages']))
    if kind == 'bible':
        return bible_skeleton(cfg['bible_book'], cfg['bible_version'])
    raise SystemExit(f'unknown en_kind {kind}')


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
        try:
            out = llm_json(ZH_SYS, zh_prompt(skeleton, prev_cv, w))
            objs = AV.extract_verse_objects(out)
        except Exception as ex:
            print(f'  win {wi+1}/{len(wins)}: LLM/parse error ({ex}); skipping window')
            frags.append({}); continue
        frag = {}
        for it in objs:
            t = it['text'].strip()
            if t:
                frag.setdefault(it['chapter'], {})[it['verse']] = t
        frags.append(frag)
        if objs:
            prev_cv = (objs[-1]['chapter'], objs[-1]['verse'])
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


# ── snapshot any doc's full text from its (still page-OCR) cct_zh ───────
def snapshot_from_cct_zh(slug, force=False):
    """Capture a doc's full Chinese text from its current cct_zh page-OCR rows
    into _apoc_snapshots/{slug}.json (durable; ebook_chunks is truncated). Skips
    if a snapshot already exists unless force."""
    path = os.path.join(os.path.dirname(__file__), '_apoc_snapshots', f'{slug}.json')
    if os.path.exists(path) and not force:
        return path
    rows, off = [], 0
    while True:
        b = db_get(f'apocrypha_sections?doc_slug=eq.{slug}&version_code=eq.cct_zh'
                   f'&select=order_index,verse,text&order=order_index&limit=1000&offset={off}')
        if not b: break
        rows += b
        if len(b) < 1000: break
        off += 1000
    body = '\n'.join((f"{r['verse']} {r['text']}" if r.get('verse') else (r['text'] or '')).strip()
                     for r in rows if (r.get('text') or '').strip())
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump({'slug': slug, 'body': body, 'source': 'cct_zh page-OCR snapshot'},
              open(path, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'[SNAP] {slug}: {len(rows)} rows → {len(body)} chars')
    return path


# ── Chinese-own skeleton (docs without PD English) ─────────────────────
ZH_OWN_SYS = (
    '你是嚴謹的古典文獻編輯，把一份中文典外文獻的「整頁 OCR」重排成「章:節」逐節結構，'
    '只依「這份中文本身」的編號（沒有英文可對照）。\n'
    '規則：\n'
    '1. 只輸出 JSON：{"verses":[{"chapter":N,"verse":M,"text":"中文"}…],"last":[章,節]}。\n'
    '2. 中文 OCR 行首的阿拉伯數字是節號；節號重新從 1（或明顯往回跳）即進入新的一章。'
    '章號必須「連續遞增、絕不重頭從 1 算」：每個 window 我會告訴你本段「從第幾章開始」，'
    '你就從那一章往後接著編（第一節通常仍屬該章，遇到節號重置才 +1 進下一章）。\n'
    '3. text 把 OCR 換行接回成通順段落，忠實保留每個字、標點、括號 ( )（譯者補字），不改寫不翻譯不加字。\n'
    '4. 刪除頁眉雜訊（「基督教典外文獻」「舊約篇 第N冊」等）、純頁碼、純小標題行、'
    '頁末註釋定義行（如「1民 24:3。」）。\n'
    '5. 處理整個 window（通常跨多章）；只有結尾被切斷的半節才略過，並在 last 回報最後一節。\n'
    '6. 嚴禁 markdown 或解說，只有 JSON。'
)


def zh_own_prompt(prev_cv, window_text):
    start = prev_cv[0] if prev_cv else 1
    prev = f'第 {prev_cv[0]} 章第 {prev_cv[1]} 節' if prev_cv else '（這是第一段，從第 1 章開始）'
    return (f'本段「從第 {start} 章開始往後連續編號」（上一段處理到 {prev}）。'
            f'章號請從 {start} 繼續，不可重頭從 1 算。\n\n'
            f'中文 OCR 全文（本 window）：\n\n{window_text}')


def do_chinese_own(slug, dry=False):
    snapshot_from_cct_zh(slug)
    body = load_zh_body(slug)
    if not body.strip():
        print(f'[ZH-OWN] {slug}: empty body, skip'); return
    wins = split_windows(body)
    print(f'[ZH-OWN] {slug}: body {len(body)} chars / {len(wins)} windows')
    frags, prev_cv = [], None
    for wi, w in enumerate(wins):
        try:
            out = llm_json(ZH_OWN_SYS, zh_own_prompt(prev_cv, w))
            objs = AV.extract_verse_objects(out)
        except Exception as ex:
            print(f'  win {wi+1}/{len(wins)}: LLM/parse error ({ex}); skipping window')
            frags.append({}); continue
        frag = {}
        for it in objs:
            t = it['text'].strip()
            if t:
                frag.setdefault(it['chapter'], {})[it['verse']] = t
        frags.append(frag)
        if objs:
            prev_cv = (objs[-1]['chapter'], objs[-1]['verse'])
        print(f'  win {wi+1}/{len(wins)}: +{sum(len(x) for x in frag.values())} verses, last={prev_cv}')
    # merge keep-longest across overlaps (no skeleton to clamp), then renumber + clean
    merged: dict[int, dict[int, str]] = {}
    for frag in frags:
        for ch, vs in frag.items():
            for v, t in vs.items():
                prev = merged.get(ch, {}).get(v)
                if prev is None or len(t) > len(prev):
                    merged.setdefault(ch, {})[v] = t
    verses = AV.clean_zh_verses(AV.renumber_chapters_sequential(merged))
    nch = len(verses); nv = sum(len(v) for v in verses.values())
    print(f'[ZH-OWN] {slug}: {nch} chapters / {nv} verses')
    if dry:
        for ch in list(verses)[:2]:
            print(f'  {ch}:1  {verses[ch][min(verses[ch])][:70]!r}')
        return
    rows = AV.verse_rows(slug, 'cct_zh', verses)
    db_delete_version(slug, 'cct_zh')
    db_insert_sections(rows)
    print(f'[ZH-OWN] {slug}: ingested {len(rows)} verse-rows')


def all_doc_slugs():
    docs = db_get('apocrypha_documents?select=slug,display_order&order=display_order')
    return [d['slug'] for d in docs]


# Deuterocanon: slug → bible_books code. Skeleton from bible_verses (Brenton LXX —
# best coverage incl 3-4 Macc, and LXX versification matches 黃根春). psalm-151 /
# esther-additions have no clean bible source → handled via --zh-own / legacy.
DEUTERO_BIBLE = {
    'tobit': 'tob', 'judith': 'jdt', 'wisdom-solomon': 'wis', 'sirach': 'sir',
    'baruch': 'bar', 'letter-jeremiah': 'epj', '1-maccabees': '1ma',
    '2-maccabees': '2ma', '3-maccabees': '3ma', '4-maccabees': '4ma',
    '1-esdras': '1es', 'prayer-manasseh': 'man',
}


def run_batch_bible(dry=False):
    """Restructure all deuterocanon docs against their bible_verses (Brenton)
    skeleton. Checkpointed (skips already-per-verse). Each book gets correct ch:v."""
    for slug, book in DEUTERO_BIBLE.items():
        try:
            if is_restructured(slug):
                print(f'[BATCH-BIBLE] skip {slug} (already per-verse)'); continue
            DOC_SOURCES[slug] = {
                'en_version': 'brenton_apoc', 'en_kind': 'bible',
                'bible_book': book, 'bible_version': 'brenton',
                'book_name': slug,
            }
            print(f'\n[BATCH-BIBLE] === {slug} (bible {book}) ===')
            snapshot_from_cct_zh(slug)        # capture full ZH text before overwrite
            do_english(slug, dry=dry)
            do_chinese(slug, dry=dry)
        except SystemExit:
            raise
        except Exception as ex:
            print(f'[BATCH-BIBLE] {slug} FAILED: {ex}')


# ── main ──────────────────────────────────────────────────────────────
def is_restructured(slug) -> bool:
    """True if cct_zh already per-verse. Keys on `verse` (only the逐節 rebuild sets
    it) — NOT `chapter`, which the old page-OCR partially populated via
    parse_apocrypha_chapters.py, so chapter would false-positive."""
    r = db_get(f'apocrypha_sections?doc_slug=eq.{slug}&version_code=eq.cct_zh'
               f'&verse=not.is.null&select=verse&limit=1')
    return len(r) > 0


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    dry = '--dry' in args
    print(f'engines: nvidia={len(NKEYS)} gemini={len(GKEYS)} prefer_nvidia={PREFER_NVIDIA}')

    # Batch: deuterocanon via bible_verses (Brenton) skeleton.
    if '--batch-bible' in args:
        run_batch_bible(dry=dry); raise SystemExit(0)

    # Batch: Chinese-own restructure across all docs (skip 1-enoch + already-done).
    if '--batch-own' in args:
        slugs = [s for s in all_doc_slugs() if s != '1-enoch']
        print(f'[BATCH] {len(slugs)} candidate docs')
        for s in slugs:
            try:
                if is_restructured(s):
                    print(f'[BATCH] skip {s} (already per-verse)'); continue
                do_chinese_own(s, dry=dry)
            except SystemExit:
                raise
            except Exception as ex:
                print(f'[BATCH] {s} FAILED: {ex}')
        raise SystemExit(0)

    slug = args[0]
    if '--snapshot' in args:
        snapshot_from_cct_zh(slug, force='--force' in args); raise SystemExit(0)
    if '--zh-own' in args:
        do_chinese_own(slug, dry=dry); raise SystemExit(0)

    # English-skeleton path (docs with a DOC_SOURCES entry, e.g. 1-enoch)
    do_en = '--en' in args or '--all' in args
    do_zh = '--zh' in args or '--all' in args
    if slug not in DOC_SOURCES:
        raise SystemExit(f'no source config for {slug}; use --zh-own (Chinese-own skeleton) '
                         f'or add to DOC_SOURCES for English alignment')
    if do_en: do_english(slug, dry=dry)
    if do_zh: do_chinese(slug, dry=dry)
    if not (do_en or do_zh):
        raise SystemExit('pass --en / --zh / --all / --zh-own / --batch-own / --snapshot')
