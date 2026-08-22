#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""希臘羅馬大藏經 — 埃庇道洛斯治癒銘文（Ἰάματα）切案並直譯。

與 CGRN 那批的關鍵差異：**本批沒有公有領域英譯可當中介**。
LiDonnici (1995)、Edelstein (1945) 都在版權內，因此繁中直接譯自希臘原文，
頁面必須明白標示這一點——這是比「經由學術英譯」更高的風險，讀者有權知道。

切段單位是**案例**而非石面行：治癒銘文本身就以 (I) (II) (III)… 逐案編號，
那既是原碑的分段，也是學界引用的單位（A4、B12…）。每案仍記錄石面行範圍。

用法：
    python scripts/hellenika_iamata.py --split          # 只切案不翻
    python scripts/hellenika_iamata.py --all            # 切案並翻譯
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
from hellenika_intro import ask  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, 'data', 'hellenika', 'sources', 'phi')

CASE = re.compile(r'\((\d+|[IVXLC]+)\)')
BATCH_CHARS = 1800
SOLO_CHARS = 600


def split_cases(doc: dict) -> list[dict]:
    """依 (I) (II) … 切案；案前的抬頭（θεός、ἰάματα…）自成一段。

    🚨 案號常出現在**行的中間**（石工不換行接著刻），此時該行在案號之前的部分
    仍屬上一案。整行歸給新案會讓每個案界都錯一截——案 I 的結尾「三年懷胎」的
    「懷胎」會跑到案 II 的開頭去。故在行內就地切開。
    """
    segs: list[dict] = []
    cur = {'case': '', 'line_from': doc['lines'][0]['line'] if doc['lines'] else 0,
           'line_to': 0, 'greek': '', 'zh': ''}

    def push() -> None:
        if cur['greek'].strip():
            segs.append(dict(cur))

    for l in doc['lines']:
        text, pos = l['text'], 0
        for m in CASE.finditer(text):
            pre = text[pos:m.start()].strip()
            if pre:
                cur['greek'] = (cur['greek'] + ' ' + pre).strip()
                cur['line_to'] = l['line']
            push()
            cur = {'case': m.group(1), 'line_from': l['line'], 'line_to': l['line'],
                   'greek': '', 'zh': ''}
            pos = m.start()          # 案號本身留在新案開頭，便於核對
        rest = text[pos:].strip()
        if rest:
            cur['greek'] = (cur['greek'] + ' ' + rest).strip()
            cur['line_to'] = l['line']
    push()
    for s in segs:
        s['greek'] = re.sub(r'\s+', ' ', s['greek']).strip()
    return segs


PROMPT = """把下列古希臘銘文逐案翻成**繁體中文**。這是埃庇道洛斯阿斯克勒庇俄斯聖所的治癒紀錄（Ἰάματα），刻在聖所石板上，一則一案：某人得何病、在聖所內殿夢見神做了什麼、醒來如何。

🚨 **本批沒有第三方英譯可依據，你是直接從希臘原文翻。** 因此：

1. **逐字直譯，不得潤飾、不得補充原文沒有的細節。** 寧可生硬，不可流暢而失真。
2. **看不懂或殘缺處，照實標「〔缺〕」或「〔文義不明〕」，絕對不要猜。** 這比譯錯重要得多——本藏經寧可留白。
3. 原文的 Leiden 符號要對應保留：方括號 `[ ]` 內是石面已缺而由編者補入的字，中譯對應處用〔〕；`⟨空⟩` 是石面留白（vacat），中譯作 ⟨空⟩。
4. 這是**多利安方言**，不是雅典的阿提卡方言，拼法會不一樣（ποὶ＝πρός、τοὶ＝οἱ、ἱαρός＝ἱερός、ἐνεκάθευδε＝入殿臥寢求夢）。
5. 敘事一律用第三人稱過去式，語氣平實如案卷，不要加入戲劇性形容。
6. **數字、年數、病名、身體部位照抄不約略**（「五年懷胎」不可寫成「多年懷胎」）。
7. 中間點用「‧」，全文繁體，不得出現簡體字或日文漢字寫法。

## 定譯

阿斯克勒庇俄斯（Ἀσκλαπιός，醫神）、阿波羅（Ἀπόλλων）、內殿／禁地（ἄβατον，聖所中供病人臥寢求夢之處）、臥寢求夢（ἐγκοιμάομαι／ἐνκαθεύδω）、求問者（ἱκέτις／ἱκέτας）、還願（ἀνάθεμα）、祭金（ἴατρα，治癒謝禮）、聖所（ἱαρόν）。

{names}

## 待譯各案

{items}

## 輸出

只輸出 JSON 物件，鍵為案號（原樣，如 "I"、"XII"、"序"），值為該案繁中譯文。不要 markdown 圍欄、不要說明。
"""


def make_batches(todo):
    out, cur, n = [], [], 0
    for item in todo:
        size = len(item['greek'])
        if size > SOLO_CHARS:
            if cur:
                out.append(cur)
                cur, n = [], 0
            out.append([item])
            continue
        if cur and n + size > BATCH_CHARS:
            out.append(cur)
            cur, n = [], 0
        cur.append(item)
        n += size
    if cur:
        out.append(cur)
    return out


def translate(doc: dict, segs: list[dict], names: dict) -> int:
    todo = [s for s in segs if s['greek'] and not s['zh']]
    if not todo:
        return 0
    ntxt = ('\n'.join(f'- {k} → {v}' for k, v in sorted(names.items()))
            if names else '（無額外專名）')
    done = 0
    for chunk in make_batches(todo):
        items = '\n\n'.join(
            f"案號 {s['case'] or '序'}（第 {s['line_from']}–{s['line_to']} 行）\n{s['greek']}"
            for s in chunk)
        try:
            raw = ask(PROMPT.format(names=ntxt, items=items))
        except Exception as e:  # noqa: BLE001
            print(f'    ✗ 本批失敗：{e}', flush=True)
            continue
        raw = re.sub(r'^```(?:json)?|```$', '', raw.strip(), flags=re.M).strip()
        try:
            got = json.loads(raw)
        except json.JSONDecodeError:
            print('    ✗ 回傳非 JSON，跳過本批', flush=True)
            continue
        for s in chunk:
            key = s['case'] or '序'
            zh = got.get(key)
            if isinstance(zh, str) and zh.strip():
                s['zh'] = zh.strip().replace('・', '‧')
                done += 1
        time.sleep(1.5)
    return done


def process(path: str, do_translate: bool) -> None:
    doc = json.loads(io.open(path, encoding='utf-8').read())
    out_path = path.replace('.json', '.aligned.json')

    if os.path.exists(out_path):
        prev = json.loads(io.open(out_path, encoding='utf-8').read())
        segs = prev['segments']
        names = prev.get('names') or {}
        print(f"  ↻ {doc['title_zh']}：沿用既有 {len(segs)} 案", flush=True)
    else:
        segs = split_cases(doc)
        names = {}
        print(f"  ✓ {doc['title_zh']}：切出 {len(segs)} 案", flush=True)

    n = translate(doc, segs, names) if do_translate else 0
    have = sum(1 for s in segs if s['zh'])
    io.open(out_path, 'w', encoding='utf-8').write(json.dumps({
        'phi': doc['phi'], 'url': doc['url'], 'siglum': doc['siglum'],
        'title_zh': doc['title_zh'], 'title_en': doc['title_en'],
        'stele': doc['stele'], 'volume': doc['volume'],
        'licence': doc['licence'],
        # 🚨 供頁面標示：本批無第三方英譯中介，繁中直接譯自希臘原文
        'pivot': 'none',
        'pivot_note': '本篇無公有領域英譯可依據（LiDonnici 1995、Edelstein 1945 均在版權內），'
                      '繁中直接譯自希臘原文；殘缺與難解處一律留白標記，不作臆補。',
        'names': names,
        'segments': segs,
    }, ensure_ascii=False, indent=1) + '\n')
    print(f'    本輪新譯 {n} 案，累計 {have}/{len(segs)} 案有繁中 '
          f'→ {os.path.relpath(out_path, ROOT)}', flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--split', action='store_true')
    ap.add_argument('--only', type=int)
    args = ap.parse_args()

    files = sorted(f for f in os.listdir(SRC_DIR)
                   if f.endswith('.json') and not f.endswith('.aligned.json'))
    if args.only:
        files = [f for f in files if f == f'phi-{args.only}.json']
    if not (args.all or args.split or args.only):
        ap.print_help()
        return
    for f in files:
        process(os.path.join(SRC_DIR, f), not args.split)


if __name__ == '__main__':
    main()
