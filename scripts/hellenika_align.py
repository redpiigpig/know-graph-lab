#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""希臘羅馬大藏經 — 銘文入庫即翻譯（希臘原文／英譯／繁中三欄對齊）。

CGRN 的希臘原文與英譯**都帶石面行號**（希臘作 `{10}`，英譯作 `(10)`），
因此可以直接以行號為對齊鍵，不必按語意重排——這正是 hellenika-epigraphy §4
要求的「以石面行分段，行號即引用基礎」。

抓取（hellenika_cgrn.py）與翻譯在同一趟完成：切段 → 對齊 → 逐段翻繁中 → 落地。

翻譯規矩見 hellenika-epigraphy §5：
  祭儀術語過詞庫／決疑體「若……則……」照原樣／口令不意譯／數字與價錢照抄。

用法：
    python scripts/hellenika_align.py --all
    python scripts/hellenika_align.py --only 13
    python scripts/hellenika_align.py --only 13 --no-translate   # 只切段對齊
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hellenika_intro import ask  # noqa: E402  引擎鏈 Gemini → NVIDIA

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, 'data', 'hellenika', 'sources', 'cgrn')

GREEK_MARK = re.compile(r'\{(\d+)\}')
EN_MARK = re.compile(r'\((\d+)\)')
FACE_MARK = re.compile(r'(Face\s+[A-Z]\b|Column\s+[IVX]+\b|Side\s+[A-Z]\b)')


# ─────────────────────── 切段與對齊 ───────────────────────

def split_by_line_marker(text: str, pattern: re.Pattern) -> list[tuple[int, str]]:
    """依行號標記切段，回傳 [(起始行號, 該段文字)]。首段起始行號記為 1。"""
    out: list[tuple[int, str]] = []
    pos, line = 0, 1
    for m in pattern.finditer(text):
        chunk = text[pos:m.start()].strip()
        if chunk:
            out.append((line, chunk))
        line = int(m.group(1))
        pos = m.end()
    tail = text[pos:].strip()
    if tail:
        out.append((line, tail))
    return out


def split_faces_en(translation: str) -> dict[str, str]:
    """英譯是一整串，內含 Face A／Face B 標記，切回各面。"""
    parts = FACE_MARK.split(translation)
    if len(parts) <= 1:
        return {'': translation.strip()}
    faces: dict[str, str] = {}
    lead = parts[0].strip()
    if lead:
        faces[''] = lead
    for i in range(1, len(parts) - 1, 2):
        faces[re.sub(r'\s+', ' ', parts[i]).strip()] = parts[i + 1].strip()
    return faces


def align(doc: dict) -> list[dict]:
    """把各面的希臘原文與英譯按行號對齊成段。"""
    en_faces = split_faces_en(doc.get('translation_en', ''))
    segments: list[dict] = []

    for face in doc['text']:
        label = face['label'].strip()
        greek_segs = split_by_line_marker(face['greek'], GREEK_MARK)
        en_text = en_faces.get(label) or en_faces.get('') or ''
        en_segs = split_by_line_marker(en_text, EN_MARK)

        lines = sorted({n for n, _ in greek_segs} | {n for n, _ in en_segs})
        gmap = dict(greek_segs)
        emap = dict(en_segs)
        for n in lines:
            g = gmap.get(n, '')
            e = emap.get(n, '')
            if not (g or e):
                continue
            segments.append({
                'face': label,
                'line_from': n,
                'greek': re.sub(r'\n', ' ', g).strip(),
                'en': re.sub(r'\s+', ' ', e).strip(),
                'zh': '',
            })
        # 一面的英譯若整段沒有行號標記，會全部落在 line 1，這是可接受的粗對齊；
        # 若某面完全沒對到，留下記號供人工檢查。
        if greek_segs and not en_segs:
            segments.append({'face': label, 'line_from': 0, 'greek': '', 'en': '',
                             'zh': '', 'note': '⚠ 此面英譯未帶行號標記，需人工對齊'})
    return segments


# ─────────────────────── 翻譯 ───────────────────────

PROMPT = """把下列古希臘祭儀銘文的英譯逐段翻成**繁體中文**。這是要收進《希臘羅馬大藏經》Κ 祭儀法卷的逐段對照，讀者會左右並排比對，因此**段落必須逐一對應，不可合併、不可拆分、不可增刪**。

銘文：{title}（{cgrn}）
出土地：{provenance}
年代：{date}

## 翻譯規矩（違反即為錯譯）

1. **法條體例照原樣。** 祭儀法多為「若……則……」的決疑體，中譯保留這個句式，**不要改寫成流暢散文**——那會抹掉它與利未記、與古代近東法典的可比性。
2. **數字、份數、價錢、日期一律照抄**，不可約略化（「九份中燒一份」不可寫成「取其一部分焚燒」）。
3. **口令與禱詞照字面譯**，不意譯、不修飾。
4. **祭儀術語用這些定譯**：淨罪／潔淨（purification）、獻祭（sacrifice）、贖罪牲（victim）、成年牲（adult animal / téleon）、初穗（first-fruits）、還願（votive）、入教（initiation）、聖所（sanctuary）、聖域（precinct）、祭壇（altar）、聖休戰（truce）、奠酒（libation）、焚燒獻祭（burnt offering）、祭司（priest）、女祭司（priestess）、不潔（polluted / miaros）、潔淨的（pure）。
5. **神名與人名用這些定譯**：宙斯、得墨忒耳、珀耳塞福涅、阿波羅、阿爾忒彌斯、雅典娜、赫拉、阿芙羅狄忒、戴奧尼索斯、赫爾墨斯、波塞頓、赫斯提亞、慈心女神（Eumenides）、**慈心者宙斯（Zeus Eumenes）**、**和善者宙斯（Zeus Meilichios）**、先祖靈（Tritopatres）、英雄（heroes）。宙斯的各種稱號務必彼此區分，不可兩個稱號譯成同一個名。不確定的神名音譯即可，不要創造意譯。
6. **英譯裡的圓括號（編者補充說明）保留為中文全形括號**；方括號〔〕表示石面已缺而由編者補入，若英譯有就保留。
7. 中間點用「‧」，全文繁體，不得出現簡體字或日文漢字寫法。
8. **不得增補英譯沒有的內容。** 看不懂的專名照音譯，寧可生硬不可臆造。

## 本篇專名定譯（**務必逐字沿用，不得另創**）

{names}

## 待譯段落

{items}

## 輸出

只輸出 JSON 物件，鍵為段落編號（字串），值為該段繁體中文譯文。不要 markdown 圍欄、不要說明。
"""

NAME_PROMPT = """下面是一篇古希臘祭儀銘文的英譯全文。請把其中出現的**專有名詞**（神名與稱號、人名、地名、聖所名、節期名、月份名、職官名）抽出來，各給一個繁體中文定譯。

規矩：
- 按希臘原文的讀音定音譯，不按英文拼寫。
- 神的**稱號**（epithet）若意義明確就意譯（Meilichios＝和善者、Eumenes＝慈心者、Katharos＝潔淨的、Miaros＝不潔的），意義不明就音譯。
- **同一個神的不同稱號必須譯成彼此可分的名**，絕不可兩個稱號共用一個中文名。
- 已定案不可改：宙斯、得墨忒耳、珀耳塞福涅、阿波羅、阿爾忒彌斯、雅典娜、赫拉、阿芙羅狄忒、戴奧尼索斯、赫爾墨斯、波塞頓、赫斯提亞、慈心女神（Eumenides）、先祖靈（Tritopatres）。
- 月份名一律音譯加「月」，如 Artemisios → 阿爾忒彌西俄斯月。
- 繁體中文，中間點用「‧」。

全文：
{text}

只輸出 JSON 物件，鍵為英文專名原樣，值為繁中定譯。不要 markdown 圍欄、不要說明。
"""


def build_name_table(doc: dict) -> dict:
    """逐篇先定名，再逐批沿用——否則同一個專名會在不同批次被譯成不同名字。"""
    text = doc.get('translation_en', '')[:12000]
    if not text:
        return {}
    try:
        raw = ask(NAME_PROMPT.format(text=text))
    except Exception as e:  # noqa: BLE001
        print(f'    ⚠ 專名表建立失敗（{e}），改由基礎詞庫兜底', flush=True)
        return {}
    raw = re.sub(r'^```(?:json)?|```$', '', raw.strip(), flags=re.M).strip()
    try:
        table = json.loads(raw)
    except json.JSONDecodeError:
        print('    ⚠ 專名表非 JSON，改由基礎詞庫兜底', flush=True)
        return {}
    table = {k: v.replace('・', '‧') for k, v in table.items()
             if isinstance(v, str) and v.strip()}
    # 撞名檢查：兩個不同專名不得共用一個中文譯名
    rev: dict[str, str] = {}
    for k, v in list(table.items()):
        if v in rev:
            print(f'    ⚠ 專名撞名：「{rev[v]}」與「{k}」都譯成「{v}」，需人工定奪', flush=True)
        rev[v] = k
    print(f'    專名表 {len(table)} 條', flush=True)
    return table


BATCH = 6


def translate(doc: dict, segments: list[dict]) -> int:
    todo = [(i, s) for i, s in enumerate(segments) if s['en'] and not s['zh']]
    if not todo:
        return 0
    table = doc.get('_names') or build_name_table(doc)
    if not table:
        # 沒有專名表就翻，專名必然前後不一致；悄悄翻完比翻不出來更糟，故中止本篇。
        print('    ✗ 無專名表，本篇暫不翻譯（下一輪重試）', flush=True)
        return 0
    doc['_names'] = table
    names = chr(10).join(f'- {k} → {v}' for k, v in sorted(table.items())) or '（無，依基礎詞庫）'
    done = 0
    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i + BATCH]
        items = '\n\n'.join(
            f"[{idx}]（{s['face']} 第 {s['line_from']} 行起）\n"
            f"英譯：{s['en']}\n"
            f"希臘原文（供參照，不必譯）：{s['greek'][:400]}"
            for idx, s in chunk)
        prompt = PROMPT.format(title=doc.get('title_zh') or doc['title_en'],
                               cgrn=f"CGRN {doc['cgrn']}",
                               provenance=doc.get('provenance', '')[:120],
                               date=doc.get('date', '')[:120],
                               names=names, items=items)
        try:
            raw = ask(prompt)
        except Exception as e:  # noqa: BLE001
            print(f'    ✗ 本批翻譯失敗：{e}', flush=True)
            continue
        raw = re.sub(r'^```(?:json)?|```$', '', raw.strip(), flags=re.M).strip()
        try:
            got = json.loads(raw)
        except json.JSONDecodeError:
            print('    ✗ 回傳非 JSON，跳過本批', flush=True)
            continue
        for idx, s in chunk:
            zh = got.get(str(idx)) or got.get(idx)
            if isinstance(zh, str) and zh.strip():
                s['zh'] = zh.strip().replace('・', '‧')
                done += 1
        time.sleep(1.5)
    return done


# ─────────────────────── run ───────────────────────

def process(path: str, do_translate: bool) -> None:
    doc = json.loads(io.open(path, encoding='utf-8').read())
    out_path = path.replace('.json', '.aligned.json')

    if os.path.exists(out_path):
        prev = json.loads(io.open(out_path, encoding='utf-8').read())
        segments = prev['segments']
        print(f"  ↻ {doc.get('title_zh')}：沿用既有 {len(segments)} 段", flush=True)
    else:
        segments = align(doc)
        print(f"  ✓ {doc.get('title_zh')}：切出 {len(segments)} 段", flush=True)

    n = translate(doc, segments) if do_translate else 0
    have = sum(1 for s in segments if s['zh'])
    payload = {
        'cgrn': doc['cgrn'], 'url': doc['url'],
        'title_zh': doc.get('title_zh'), 'title_en': doc['title_en'],
        'volume': doc.get('volume'),
        'date': doc.get('date'), 'provenance': doc.get('provenance'),
        'support': doc.get('support'), 'bibliography': doc.get('bibliography'),
        'licence': doc.get('licence'),
        'names': doc.get('_names') or {},
        'segments': segments,
    }
    io.open(out_path, 'w', encoding='utf-8').write(
        json.dumps(payload, ensure_ascii=False, indent=1) + '\n')
    print(f"    本輪新譯 {n} 段，累計 {have}/{len(segments)} 段有繁中 "
          f"→ {os.path.relpath(out_path, ROOT)}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--only', type=int)
    ap.add_argument('--no-translate', action='store_true')
    args = ap.parse_args()

    files = sorted(f for f in os.listdir(SRC_DIR)
                   if f.endswith('.json') and not f.endswith('.aligned.json'))
    if args.only:
        files = [f for f in files if f == f'cgrn-{args.only}.json']
    if not files:
        raise SystemExit('沒有可處理的來源檔，先跑 python scripts/hellenika_cgrn.py --fetch')
    if not (args.all or args.only):
        ap.print_help()
        return

    for f in files:
        process(os.path.join(SRC_DIR, f), not args.no_translate)


if __name__ == '__main__':
    main()
