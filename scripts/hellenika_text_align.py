#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""希臘羅馬大藏經 — 把 sources/text/*.json 的段落逐段譯成繁體中文。

與 hellenika_align.py（祭儀法銘文）分工：那支譯的是決疑體法條，這支譯的是
**六步格詩**——赫西俄德《神譜》《工作與時日》、荷馬詩頌。文類不同，規矩也不同，
所以 prompt 另寫一份，不共用。

取源見 hellenika_text.py；引擎鏈沿用 hellenika_intro.ask
（Gemini → NVIDIA → OpenRouter → Haiku）。要只走 Haiku：

    set HELLENIKA_ENGINE=haiku

🚨 逐段對應是硬要求：讀者左右並排比對，段落數對不齊就是壞掉。本腳本每批送出
   後會核對回傳的鍵，數目或編號對不上就整批丟棄重來，不做部分採用。

用法：
    python scripts/hellenika_text_align.py --status
    python scripts/hellenika_text_align.py --file theogony            # 單篇
    python scripts/hellenika_text_align.py --all                      # 全部
    python scripts/hellenika_text_align.py --file theogony --limit 2  # 只跑兩批試水
"""
from __future__ import annotations

import argparse
import glob
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
TEXT_DIR = os.path.join(ROOT, 'data', 'hellenika', 'sources', 'text')
BATCH = 3          # 每批段數。一段約 20 行詩，三段已近 60 行，再多品質會掉。

PROMPT = """把下列古希臘詩的英譯逐段翻成**繁體中文**。這是要收進《希臘羅馬大藏經》的逐段對照，讀者會左右並排比對希臘原文、英譯與中譯，因此**段落必須逐一對應，不可合併、不可拆分、不可增刪**。

篇名：{title}（{siglum}）
作者：{author}

## 翻譯規矩（違反即為錯譯）

1. **這是史詩，不是散文。** 譯成有節奏的書面漢語，句子不要拖長成現代長句；但**不要押韻、不要湊字數、不要仿騷體或五七言**——那是改寫不是翻譯。
2. **一行詩的內容留在一行的位置上。** 英譯把數行併成一句時，中譯依原順序展開，不要為求通順而把後面的意象提前。
3. **不得增補英譯沒有的內容。** 荷馬式的固定修飾語（雲聚者宙斯、白臂赫拉、遠射者阿波羅）照譯，不可省略也不可自行添加。
4. **神名與人名用這些定譯**：宙斯、赫拉、波塞頓、得墨忒耳、赫斯提亞、雅典娜、阿波羅、阿爾忒彌斯、阿芙羅狄忒、赫爾墨斯、阿瑞斯、赫菲斯托斯、戴奧尼索斯、克洛諾斯、瑞亞、烏拉諾斯、蓋婭、塔爾塔羅斯、厄洛斯、涅墨西斯、繆斯、命運三女神、復仇女神、泰坦、獨眼巨人、百手巨人、俄刻阿諾斯、忒堤斯、赫利俄斯、塞勒涅、厄俄斯、珀耳塞福涅、哈得斯、普羅米修斯、厄庇米修斯、潘朵拉、赫拉克勒斯、佩加索斯。
   不在表上的專名按**希臘原文讀音**音譯，不按英文拼寫（Cronos 作克洛諾斯不作克羅諾斯；Uranus 作烏拉諾斯不作天王星）。
5. **神的稱號（epithet）意義明確就意譯**（aegis-holding＝持盾牌的、cloud-gathering＝雲聚的、ox-eyed＝牛眼的、silver-bowed＝銀弓的）；同一位神的不同稱號必須譯得彼此可分。
6. **地名用古典學界通行譯法**：赫利孔山、奧林匹斯、俄林波斯不可混用（一律作奧林匹斯）、皮埃里亞、德爾菲、提洛、厄琉息斯、克里特、忒拜、特洛伊。
7. **英譯的圓括號（編者補充）保留為中文全形括號**；方括號〔〕表示原文有闕而由編者補入，若英譯有就保留。
8. 中間點用「‧」，全文繁體，不得出現簡體字或日文漢字寫法。
9. 看不懂的專名照音譯，寧可生硬不可臆造。

## 本篇專名定譯（**務必逐字沿用，不得另創**）

{names}

## 待譯段落

{items}

## 輸出

只輸出 JSON 物件，鍵為段落編號（字串），值為該段繁體中文譯文。不要 markdown 圍欄、不要說明。
"""


def parse_json(raw: str) -> dict | None:
    """模型偶爾會包 markdown 圍欄或前後加話，剝掉再解。"""
    t = raw.strip()
    t = re.sub(r'^```(?:json)?\s*', '', t)
    t = re.sub(r'\s*```$', '', t)
    i, j = t.find('{'), t.rfind('}')
    if i < 0 or j < i:
        return None
    try:
        d = json.loads(t[i:j + 1])
    except json.JSONDecodeError:
        return None
    return d if isinstance(d, dict) else None


def normalise(zh: str) -> str:
    """統一中間點。模型十次有八次給半形 · 或日文 ・，repo 慣例一律用「‧」。"""
    return zh.strip().replace('·', '‧').replace('・', '‧')


def translate_batch(doc: dict, batch: list[tuple[int, dict]]) -> int:
    items = '\n\n'.join(
        '### 第 %d 段（詩行 %d–%d）\n%s' % (i, s['line_from'], s['line_to'], s['en'])
        for i, s in batch)
    names = '\n'.join('- %s → %s' % (k, v) for k, v in (doc.get('names') or {}).items()) or '（無）'
    prompt = PROMPT.format(title=doc['title_zh'], siglum=doc['siglum'],
                           author=doc.get('author', ''), names=names, items=items)
    try:
        raw = ask(prompt)
    except Exception as e:                       # noqa: BLE001
        print('    X 引擎全乾：%s' % e, file=sys.stderr, flush=True)
        return 0
    got = parse_json(raw)
    if not got:
        print('    X 回傳非 JSON，整批丟棄', file=sys.stderr, flush=True)
        return 0
    want = {str(i) for i, _ in batch}
    if set(got) != want:                          # 編號對不上就整批丟棄，不做部分採用
        print('    X 段號對不上（要 %s，得 %s），整批丟棄'
              % (sorted(want), sorted(got)), file=sys.stderr, flush=True)
        return 0
    n = 0
    for i, seg in batch:
        zh = normalise(str(got[str(i)]))
        if zh:
            seg['zh'] = zh
            n += 1
    return n


def process(path: str, limit: int | None) -> tuple[int, int, int]:
    doc = json.load(io.open(path, encoding='utf-8'))
    segs = doc['segments']
    todo = [(i, s) for i, s in enumerate(segs) if not s.get('zh')]
    if not todo:
        return 0, len(segs), len(segs)
    batches = [todo[i:i + BATCH] for i in range(0, len(todo), BATCH)]
    if limit:
        batches = batches[:limit]
    done = 0
    for b in batches:
        done += translate_batch(doc, b)
        io.open(path, 'w', encoding='utf-8', newline='\n').write(
            json.dumps(doc, ensure_ascii=False, indent=2) + '\n')
        time.sleep(1)
    have = sum(1 for s in segs if s.get('zh'))
    print('  %-22s 本輪 +%d，累計 %d/%d 段有繁中'
          % (doc['slug'], done, have, len(segs)), flush=True)
    return done, have, len(segs)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--file')
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--status', action='store_true')
    ap.add_argument('--limit', type=int)
    a = ap.parse_args()

    paths = sorted(glob.glob(os.path.join(TEXT_DIR, '*.json')))
    if a.file:
        paths = [p for p in paths if os.path.basename(p) == a.file + '.json']
        if not paths:
            sys.exit('找不到 %s' % a.file)

    if a.status:
        th = tt = 0
        for p in paths:
            d = json.load(io.open(p, encoding='utf-8'))
            h = sum(1 for s in d['segments'] if s.get('zh'))
            th += h
            tt += len(d['segments'])
            if h < len(d['segments']):
                print('  %-22s %d/%d' % (d['slug'], h, len(d['segments'])))
        print('\n合計 %d/%d 段有繁中' % (th, tt))
        return

    if not (a.file or a.all):
        sys.exit('要 --file 或 --all')
    th = tt = 0
    for p in paths:
        _, h, t = process(p, a.limit)
        th += h
        tt += t
    print('\n合計 %d/%d 段有繁中' % (th, tt))


if __name__ == '__main__':
    main()
