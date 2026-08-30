#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""英文版 ACCS EPUB → 譯成繁中 → 入 accs_commentary。

中文版沒有第 24-25 卷（耶利米書、哀歌），改用圖書館裡的英文版卷十二。
解析走 accs_epub.py（純函式、有測試），翻譯走 translate_ebook_to_zh 的
Gemini→NVIDIA→Haiku 鏈，署名照 theologians 詞庫換成中文定名。

逐則 checkpoint 到 c:/tmp/accs_epub_zh_{book}.jsonl，可隨時中斷續傳；
--upload 才寫資料庫，預設只翻不寫。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import requests
import translate_ebook_to_zh as te
from accs_epub import parse_chapter

EPUB = Path(r'G:\我的雲端硬碟\資料\知識圖工作室\經典對照與註釋'
            r'\基督教-古代基督徒聖經註釋叢書 ACCS\ACCS_Jeremiah_Lamentations.epub')
CKPT_DIR = Path('c:/tmp')
SOURCE_VOL = 'ACCS（耶利米書‧耶利米哀歌）'

# 不是人，是作品／文獻集。ACCS 把它們當引用來源列在署名位置，中文各卷也這樣
# （語料裡就有「使徒憲章」）。這些不進詞庫比對，直接給定譯名。
NOT_PERSONS = {
    'Apostolic Constitutions': '使徒憲章',
    'Didascalia': '十二使徒訓誨錄',
    'Didache': '十二使徒遺訓',
    'Book of Steps': '級位之書',
    'Letter of Barnabas': '巴拿巴書信',
    'Shepherd of Hermas': '黑馬牧人書',
    'Epistle of Barnabas': '巴拿巴書信',
}

# 原書本身的排字錯誤與過於簡略的稱呼，比對前先正規化到詞庫用的名字。
ALIASES = {
    'Clement of Alexandra': 'Clement of Alexandria',   # 原書拼錯
    'Ignatius': 'Ignatius of Antioch',                  # 只寫名，與羅耀拉的依納爵同名
}

PROMPT = """你是古代基督教教父文獻的專業譯者。把下列英文譯成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體）；學術散文語氣，忠實流暢，不加註、不改寫、不省略。
2. 經文引語沿用和合本語感；教父作品名依既有中譯慣例。
3. 保留原有的省略號（. . . 譯為 ……）與方括號補字。
4. **只輸出譯文本身**，不要前言、標題、編號或任何說明。

{source}"""


def build_name_map() -> dict[str, str]:
    """英文教父名 → 詞庫的中文定名。ACCS 用簡稱（Augustine），詞庫用全稱
    （Augustine of Hippo），所以除了完全相同，也接受「簡稱是全稱的前綴」。"""
    rows, off = [], 0
    while True:
        r = requests.get(f'{te.URL}/rest/v1/theologians'
                         f'?select=name_english,name_latin_std,name_recommended'
                         f'&offset={off}&limit=1000', headers=te.H_GET, timeout=60)
        r.raise_for_status()
        b = r.json()
        rows += b
        if len(b) < 1000:
            break
        off += 1000
    exact: dict[str, str] = {}
    for x in rows:
        for key in ('name_english', 'name_latin_std'):
            v = (x.get(key) or '').strip()
            if not v:
                continue
            exact.setdefault(v.lower(), x['name_recommended'])
            bare = re.sub(r'\s*\(.*?\)', '', v).strip()
            if bare:
                exact.setdefault(bare.lower(), x['name_recommended'])
    return exact


def normalize_en(name: str) -> tuple[str, bool]:
    """整理 ACCS 的英文署名，回傳 (乾淨名字, 是否標為存疑)。

    EPUB 保留了原書的**換行連字號**（Chrysos-tom、Prosper of Aqui-taine、
    Aqui­leia），直接比對一定對不上；字母間的連字號要接回去。
    另有 [dub]／[dub.] 存疑標記與 (via 某某) 轉引註記，比對前先摘掉，
    存疑與否另外記著，不要丟失這個訊息。
    """
    dubious = bool(re.search(r'\[\s*dub\.?\s*\]', name, re.I))
    s = re.sub(r'\[[^\]]*\]', ' ', name)          # [dub.]、[sp.] 之類
    s = re.sub(r'\(via[^)]*\)', ' ', s, flags=re.I)  # (via Ammon)
    s = re.sub(r'(?<=[A-Za-z])[-­](?=[a-z])', '', s)   # 換行連字號接回去
    return re.sub(r'\s+', ' ', s).strip(), dubious


def resolve_father(name: str, exact: dict[str, str]) -> tuple[str, str]:
    """回傳 (中文署名, 判定依據)。判定不出來就原樣保留英文，等人工補。"""
    if not name:
        return '', 'blank'
    clean, dubious = normalize_en(name)
    clean = ALIASES.get(clean, clean)
    suffix = '（存疑）' if dubious else ''
    if clean in NOT_PERSONS:
        return NOT_PERSONS[clean] + suffix, 'work'
    low = clean.lower()
    if low in exact:
        return exact[low] + suffix, 'exact'
    # 簡稱 ↔ 全稱兩個方向都要看：
    #   Augustine ⊂ Augustine of Hippo（前綴）
    #   Chrysostom ⊂ John Chrysostom（後綴，簡稱在後）
    words = low.split()
    cands = [full for full in exact
             if full.startswith(low + ' of ') or full.startswith(low + ' the ')
             or full.startswith(low) or full.endswith(' ' + low)
             or (len(words) > 1 and full.startswith(low))]
    picks = {exact[c] for c in cands}
    if len(picks) == 1:
        return picks.pop() + suffix, 'prefix'
    return clean + suffix, 'unresolved'


WORK_MAP = json.loads((Path(__file__).resolve().parent / 'accs_work_titles.json')
                      .read_text(encoding='utf-8'))
BOOK_MAP = WORK_MAP.get('_books', {})
WORK_MAP = {k: v for k, v in WORK_MAP.items() if not k.startswith('_')}


def resolve_work(work: str) -> tuple[str, str]:
    """英文出處 → 中文書名＋章節號。回傳 (中文, 判定依據)。

    🚨 書名絕不可交給 LLM 自由翻譯：短標題沒有上下文，模型會自行續寫。
    實測把 'City of God 18.33.1' 譯成了一整段哈巴谷引文。
    查不到又推不出來就原樣保留英文，等人工補——臆造書名比留英文糟。
    """
    if not work:
        return '', 'blank'
    m = re.match(r'^(.*?)[\s]*([\d][\d.:,\-–\s]*)?$', work.strip())
    title = (m.group(1) if m else work).strip()
    sect = (m.group(2) or '').strip() if m else ''
    zh = WORK_MAP.get(title)
    how = 'map'
    if not zh:
        # 規則推導；推不出來就保留英文
        for pat, tmpl in ((r'^Homilies? on (?:the )?(.+)$', '{}講道集'),
                          (r'^Commentary on (?:the )?(.+)$', '{}註釋'),
                          (r'^Sermons? on (?:the )?(.+)$', '{}講道集'),
                          (r'^Fragments? on (?:the )?(.+)$', '{}殘篇')):
            mm = re.match(pat, title, re.I)
            if not mm:
                continue
            base = BOOK_MAP.get(mm.group(1)) or WORK_MAP.get(mm.group(1))
            if base:
                zh, how = tmpl.format(base), 'rule'
                break
    if not zh:
        return (title + (' ' + sect if sect else '')).strip(), 'unresolved'
    return (zh + (' ' + sect if sect else '')).strip(), how


def translate(text: str) -> str:
    if not text.strip():
        return ''
    te.PROMPT_TMPL = PROMPT
    return te.gemini_with_nvidia_fallback(text)




BATCH_PROMPT = """你是古代基督教教父文獻的專業譯者。下面是若干段獨立的英文，
每段以 <<編號>> 起始。把每一段譯成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體）；學術散文語氣，忠實流暢，不加註、不改寫、不省略。
2. 經文引語沿用和合本語感。
3. 保留原有的省略號（. . . 譯為 ……）與方括號補字。
4. **輸出格式必須與輸入相同**：每段譯文前加上原本的 <<編號>>，段數與編號完全
   對應，不可合併、不可漏、不可多。編號行以外不要任何說明。

{source}"""

_MARKER = re.compile(r'<<\s*(\d+)\s*>>')


def translate_batch(items: list[str]) -> list[str] | None:
    """一次送多段，回傳等長的譯文串列；對不齊就回 None，讓呼叫端退回逐段。

    這台機器同時有十幾個工作在搶同一批引擎池，瓶頸是**呼叫次數**而不是字數
    （原本每則要打兩次：正文與小標，806 則＝1,612 次呼叫，實測 37 小時只跑完
    50 則）。合併送出把呼叫降到約 200 次。

    但批次翻譯最大的風險是段落錯位（見 [[project_alignment_gate]]），所以一律
    驗編號：少一個、多一個、或有空段就整批作廢改逐段——寧可慢，不可把甲教父的
    話配到乙教父身上。
    """
    if not items:
        return []
    src = '\n\n'.join(f'<<{i + 1}>> {s}' for i, s in enumerate(items))
    te.PROMPT_TMPL = BATCH_PROMPT
    out = te.gemini_with_nvidia_fallback(src)
    parts: dict[int, str] = {}
    cur, buf = None, []
    for line in out.splitlines():
        m = _MARKER.match(line.strip())
        if m:
            if cur is not None:
                parts[cur] = '\n'.join(buf).strip()
            cur, buf = int(m.group(1)), [_MARKER.sub('', line, count=1).strip()]
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        parts[cur] = '\n'.join(buf).strip()
    if set(parts) != set(range(1, len(items) + 1)):
        return None
    if any(not parts[i + 1] for i in range(len(items))):
        return None
    return [parts[i + 1] for i in range(len(items))]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--upload', action='store_true')
    ap.add_argument('--limit', type=int)
    ap.add_argument('--batch', type=int, default=8,
                    help='一次送幾則進 LLM；對不齊會自動退回逐段')
    ap.add_argument('--names-only', action='store_true',
                    help='只檢查署名對照，不翻譯')
    args = ap.parse_args()

    import zipfile
    z = zipfile.ZipFile(EPUB)
    names = [n for n in z.namelist() if re.search(r'p\dchap\d+\.html$', n)]
    names.sort(key=lambda n: (n.split('chap')[0], int(re.search(r'chap(\d+)', n).group(1))))
    recs: list[dict] = []
    for n in names:
        recs += parse_chapter(z.read(n).decode('utf-8', errors='replace'))
    print(f'解析出 {len(recs)} 則', flush=True)

    exact = build_name_map()
    stats: dict[str, int] = {}
    for r in recs:
        zh, how = resolve_father(r['father'], exact)
        r['father_zh'] = zh
        stats[how] = stats.get(how, 0) + 1
    print('署名對照:', stats, flush=True)
    unresolved = sorted({r['father'] for r in recs if r['father'] and r['father_zh'] == r['father']})
    if unresolved:
        print(f'  未對上 {len(unresolved)} 種: {unresolved[:20]}', flush=True)
    if args.names_only:
        return 0

    ckpt = CKPT_DIR / 'accs_epub_zh_jer_lam.jsonl'
    done: dict[str, dict] = {}
    if ckpt.exists():
        for ln in ckpt.open(encoding='utf-8'):
            try:
                d = json.loads(ln)
                done[d['key']] = d
            except Exception:
                pass
    print(f'checkpoint 已有 {len(done)} 則', flush=True)

    todo = [r for r in recs if f"{r['book_code']}|{r['chapter']}|{r['pericope_order']}|"
                               f"{r['heading']}|{r['body'][:40]}" not in done]
    if args.limit:
        todo = todo[:args.limit]
    print(f'待譯 {len(todo)} 則', flush=True)

    def key_of(r: dict) -> str:
        return (f"{r['book_code']}|{r['chapter']}|{r['pericope_order']}|"
                f"{r['heading']}|{r['body'][:40]}")

    fh = ckpt.open('a', encoding='utf-8')
    done_n = 0
    for start in range(0, len(todo), args.batch):
        group = todo[start:start + args.batch]
        # 小標與正文一起送，省掉一半呼叫（原本每則要打兩次）
        payload = []
        for r in group:
            payload.append(r['body'])
            if r['heading'] and r['heading'] != 'Overview':
                payload.append(r['heading'])
        try:
            got = translate_batch(payload)
            if got is None:            # 對不齊 → 退回逐段，寧可慢也不可錯位
                print('  ⚠ 批次對不齊，改逐段', flush=True)
                got = [translate(s) for s in payload]
        except Exception as exc:  # noqa: BLE001
            print(f'  ✗ {type(exc).__name__}: {str(exc)[:110]}', flush=True)
            time.sleep(20)
            continue
        k = 0
        for r in group:
            body_zh = got[k]
            k += 1
            if r['heading'] and r['heading'] != 'Overview':
                head_zh = got[k]
                k += 1
            else:
                head_zh = '概述' if r['heading'] == 'Overview' else ''
            work_zh, _how = resolve_work(r['work'])
            fh.write(json.dumps({**r, 'key': key_of(r), 'body_zh': body_zh,
                                 'heading_zh': head_zh, 'work_zh': work_zh},
                                ensure_ascii=False) + '\n')
            done_n += 1
        fh.flush()
        print(f'  · {done_n}/{len(todo)}  {group[-1]["book_code"]} '
              f'{group[-1]["chapter"]}:{group[-1]["verse_start"]}', flush=True)
    fh.close()

    if not args.upload:
        print('（未加 --upload，僅寫 checkpoint）', flush=True)
        return 0
    return upload(ckpt)


def upload(ckpt: Path) -> int:
    rows = []
    for ln in ckpt.open(encoding='utf-8'):
        try:
            d = json.loads(ln)
        except Exception:
            continue
        if not (d.get('body_zh') or '').strip():
            continue
        rows.append({
            'book_code': d['book_code'], 'chapter': d['chapter'],
            'verse_start': d['verse_start'], 'verse_end': d['verse_end'],
            'pericope_order': d['pericope_order'], 'entry_order': 0,
            'section_kind': d['kind'], 'heading': d.get('heading_zh') or None,
            'father_name': d.get('father_zh') or None,
            'work_title': d.get('work_zh') or None,
            'body_zh': d['body_zh'], 'source_vol': SOURCE_VOL,
        })
    # entry_order 依 pericope 內順序重編
    seq: dict[tuple, int] = {}
    for x in rows:
        k = (x['book_code'], x['chapter'], x['pericope_order'])
        x['entry_order'] = seq.get(k, 0)
        seq[k] = x['entry_order'] + 1
    print(f'準備上傳 {len(rows)} 列', flush=True)
    for i in range(0, len(rows), 100):
        r = requests.post(f'{te.URL}/rest/v1/accs_commentary',
                          headers={**te.H_JSON, 'Prefer': 'return=minimal'},
                          json=rows[i:i + 100], timeout=120)
        if not r.ok:
            print('✗', r.status_code, r.text[:300], flush=True)
            return 1
    print('上傳完成', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
