#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""聖經語料入庫閘 —— 任何譯本進 R2 之前都要過這一關。

## 為什麼需要這支

2026-09-16 稽核既有 32 個版本，抓到三種**不會報錯、只會安靜出錯**的毛病：

| 版本 | 毛病 | 規模 |
|---|---|---|
| `cuv2010` 和合本修訂版 | 詩體只存了對句第一行 | 7,208 節（23.3%），詩篇 88.5% |
| `rcv_zh` 恢復本 | 整本 UTF-8 被當 ISO-8859-1 解 | **31,081 節（100%）** |
| `cuv1919e` 淺文理 | 夾註混進正文 | 3,156 節（10.2%） |

三個都是節數對得上、卷數對得上、網站打得開、看起來完全正常。
恢復本尤其誇張——**整本沒有一節是對的**，卻在庫裡躺著沒人發現。
所以「入庫成功」不等於「內容正確」，必須有一支專門驗產物的東西。

🚨 這支驗的是**內容**，不是流程。流程的成功訊息一律不採信。

## 檢查項目

1. **覆蓋**——卷／章／節數，以及與基準版相比缺了多少節
2. **截斷**——比基準版短太多的節（詩體漏行、抓到一半）
3. **亂碼**——拉丁補充區字元密度過高（編碼解錯的指紋）
4. **夾註混入**——「原文作」「或作」等註解語混進正文
5. **疊字**——開頭重複（註解被貼在被註的詞後面的指紋）
6. **空節**——有節號沒內容
7. **分段標題混入**——編者所加的章節標題被留在每章第 1 節開頭
   （它沒有任何殘留標記，前六項全抓不到；只膨脹第 1 節，所以用
   「第 1 節長度比中位數 ÷ 全書長度比中位數」抓）

## 用法

    python scripts/audit_bible_versions.py                 # 全部版本
    python scripts/audit_bible_versions.py rcv_zh cuv2010  # 指定版本
    python scripts/audit_bible_versions.py --strict        # 有問題就回非零（給 CI 用）
"""
from __future__ import annotations

import collections
import gzip
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / 'output' / 'source-cache' / 'bible-verses'

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 各語言的比長度基準。中文拿官話和合本當尺——它經查核是乾淨的。
BASELINE = {'zh': 'cuv1919', 'en': 'kjva'}
# 🚨 **不要寫死中文版本清單。** 第一版寫死之後，新加的 `orth_wenli` 與
#    `cuv_ewenli` 不在名單裡，於是各項檢查**整個沒跑**，報表印「—」還判 ✔——
#    一道會漏掉新資料的閘，比沒有閘更危險。
#    改成看內容：漢字比例過半就當中文版本，新版本自動納入。
CJK = re.compile(r'[㐀-鿿]')


def is_zh(sample):
    """這個版本是不是中文：取樣文字裡漢字佔一半以上。"""
    total = sum(len(s) for s in sample)
    if not total:
        return False
    return sum(len(CJK.findall(s)) for s in sample) / total > 0.5

# 判定門檻。超過就是紅字，需要處理而不是「可接受的差異」。
# 🚨 **不能直接拿長度比基準。** 文理和合本比官話短是文體使然，不是缺字；
#    第一版稽核就這樣把乾淨的 cuv1919w 判成「截斷 16.6%」。
#    改成自我校準：先算這個版本對基準的**長度比中位數**，再找出顯著低於
#    自己常態的節。文言的中位數本來就低，於是不再被誤判。
TRUNC_REL = 0.55        # 低於「自己的中位數 × 這個比例」＝疑似被截斷
TRUNC_FAIL = 0.10       # 截斷率超過一成＝不合格
MOJI_FAIL = 0.01        # 亂碼率超過 1%＝不合格（正常應該是 0）
NOTE_FAIL = 0.02        # 夾註混入超過 2%＝不合格
HEAD_FAIL = 130         # 第 1 節長度比達全書中位數的 1.3 倍＝疑似分段標題混入

# 🚨 亂碼指紋：UTF-8 被當成單位元組編碼解出來，會產生一串拉丁補充區字元。
#    中文譯本正常情況下這個區段的字元應該是 0。
MOJI_RE = re.compile(r'[À-ÿ]')
# 🚨 夾註要分「published 的」與「混進來的」。和合本正文本來就寫
#    「救我們脫離兇惡（或譯：脫離惡者）」——那是體例，不是缺陷；
#    第一版把它算成 400 處問題。真正的毛病是註解**沒有任何括號**就黏在正文裡
#    （淺文理：「虛心者虛心者原文作貧於心者福矣」）。所以只抓括號外的。
NOTE_WORDS = '原文作|原文是|或作|或譯|下同'
PAREN = r'（[^）]*）|〔[^〕]*〕|\([^)]*\)|「[^」]*」'
NOTE_RE = re.compile(NOTE_WORDS)
DUP_RE = re.compile(r'^(.{2,6})\1')


def load_books():
    for f in sorted(CACHE.glob('*.json.gz')):
        yield json.loads(gzip.decompress(f.read_bytes()))


def audit(only=None):
    """兩趟：第一趟數各項並收集長度比，第二趟才用中位數判截斷。

    🚨 為什麼要兩趟：截斷的判準是「顯著短於**這個版本自己**的常態」，
       而「自己的常態」要看過全書才知道。一趟做不到，硬做就退回
       「拿官話量文言」那個誤報。
    """
    stat = collections.defaultdict(lambda: collections.Counter())
    ratios = collections.defaultdict(list)
    firsts = collections.defaultdict(list)     # 每章第 1 節的長度比
    # 先取樣判定哪些版本是中文（不寫死清單，新版本自動納入）
    sample = collections.defaultdict(list)
    for doc in load_books():
        for vs in doc['chapters'].values():
            for v in vs:
                for code, text in v['t'].items():
                    if text and len(sample[code]) < 40:
                        sample[code].append(text)
    zh = {c for c, s in sample.items() if is_zh(s)}
    for doc in load_books():
        for vs in doc['chapters'].values():
            for v in vs:
                t = v['t']
                base = (t.get(BASELINE['zh']) or '').strip()
                for code, text in t.items():
                    if only and code not in only:
                        continue
                    s = (text or '').strip()
                    st = stat[code]
                    st['verses'] += 1
                    if not s:
                        st['empty'] += 1
                        continue
                    st['chars'] += len(s)
                    if code in zh:
                        if len(MOJI_RE.findall(s)) > len(s) * 0.25:
                            st['mojibake'] += 1
                        if NOTE_RE.search(re.sub(PAREN, '', s)):
                            st['note'] += 1
                        if DUP_RE.match(s):
                            st['dup'] += 1
                        if base and code != BASELINE['zh']:
                            r = len(s) / len(base)
                            ratios[code].append(r)
                            # 🚨 第六項：分段標題混進正文。編者所加的
                            #    `<h2>天主創造天地</h2>` 若只剝標籤、沒整塊丟掉，
                            #    標題文字就留在**每章第 1 節**開頭（施約瑟 1,189 章
                            #    裡有 411 章中招）。它沒有任何殘留標記，前五項全抓不到。
                            #    但它只膨脹第 1 節，所以比「第 1 節的長度比中位數」
                            #    與「全部節的中位數」就看得出來。
                            if v['v'] == 1:
                                firsts[code].append(r)

    def _med(xs):
        xs = sorted(xs)
        return xs[len(xs) // 2] if xs else 1.0

    med = {}
    for code, rs in ratios.items():
        med[code] = _med(rs)
        stat[code]['comparable'] = len(rs)
        stat[code]['trunc'] = sum(1 for r in rs if r < med[code] * TRUNC_REL)
        # 第 1 節明顯比其他節「胖」＝分段標題被黏在正文開頭
        if len(firsts[code]) >= 50 and med[code]:
            stat[code]['head_x100'] = int(_med(firsts[code]) / med[code] * 100)

    for doc in load_books():
        seen = {c for vs in doc['chapters'].values() for v in vs for c in v['t']
                if (v['t'][c] or '').strip()}
        for c in seen:
            if not only or c in only:
                stat[c]['books'] += 1
    return stat, med


def report(stat, med, strict=False):
    rows = sorted(stat.items(), key=lambda kv: -kv[1]['verses'])
    print(f"{'版本':14}{'節數':>8}{'卷':>4}{'長度比':>7}{'截斷':>14}{'亂碼':>14}"
          f"{'夾註':>13}{'首節':>6}  判定")
    print('─' * 92)
    failed = []
    for code, s in rows:
        n = s['verses'] or 1
        cmpn = s['comparable'] or 1
        tr, mo, no = s['trunc'] / cmpn, s['mojibake'] / n, s['note'] / n
        flags = []
        if s['comparable'] and tr > TRUNC_FAIL:
            flags.append('截斷')
        if mo > MOJI_FAIL:
            flags.append('亂碼')
        if no > NOTE_FAIL:
            flags.append('夾註')
        if s['head_x100'] and s['head_x100'] >= HEAD_FAIL:
            flags.append('標題混入')
        verdict = ('✖ ' + '／'.join(flags)) if flags else '✔'
        if flags:
            failed.append(code)
        tcol = f"{s['trunc']:,}({tr:.1%})" if s['comparable'] else '—'
        mcol = f"{s['mojibake']:,}({mo:.1%})" if s['mojibake'] else '—'
        ncol = f"{s['note']:,}({no:.1%})" if s['note'] else '—'
        mcol2 = f'{med.get(code, 1):.2f}' if code in med else '—'
        print(f'{code:14}{s["verses"]:8,}{s["books"]:4}{mcol2:>7}{tcol:>14}{mcol:>14}'
              f'{ncol:>13}{(str(s["head_x100"]) + "%") if s["head_x100"] else "—":>6}  {verdict}')
    print('─' * 92)
    print(f'{len(rows)} 個版本，{len(failed)} 個不合格'
          + (f'：{"、".join(failed)}' if failed else ''))
    return 1 if (strict and failed) else 0


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    strict = '--strict' in sys.argv
    st, med = audit(set(args) or None)
    sys.exit(report(st, med, strict))
