#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
祆教：把「原文逐字相同」的他節譯文代入沒有譯文的節，並**標明代入來源**。

    python -X utf8 scripts/avesta_xref_en.py           # 只報告，不動檔
    python -X utf8 scripts/avesta_xref_en.py --apply   # 寫檔

═══════════════ 這支解決什麼、以及為什麼不照交接文件那樣做 ═══════════════

SBE（Mills）有些章節不另譯，直接寫 `5.(identical with Yasna 37)`、
`72.(See Y61)`。交接文件建議「把交叉引用的目標章節譯文代入那 8 章」。
**照章代入是錯的**，實測：

    Y5  vs Y37   第 3、4 節逐字相同（1.00／0.97），
                 但第 1、2、5 節只有 0.70–0.88——代進去就是錯的譯文。
    Y72 vs Y61   第 1–4 節逐字相同，但 Y72 有 11 節，Y61 只有 5 節。
    Y63 vs Y38   0.21–0.34，根本不是同一段。

所以改成**逐節比對原文**：只有正規化後**一個字都不差**才代入，
其餘留空。這是量得出來的證據，不是猜。好處是不限那 8 章——
全藏 335 個缺英譯的段落裡有 61 段在他處找得到逐字相同的節，
Yt／Vd／Vr 都有（例：Vd 3.18 ← Vd 5.49、Yt 9.33 ← Yt 5.133）。

🚨 **不可默默代入。**每一段代入都寫進 `note` 欄（reader 已會顯示，
   見 pages/avesta/text/[slug].vue），讀者一眼看得到這一節的譯文是借來的、
   借自哪一節。沒有這個標示，站上就等於宣稱 SBE 譯過這一節。

🚨 **同一個公式要代就連中譯一起代。**萬迪達德最怕同一句在不同批次
   譯得不一樣（見交接文件 `--reset` 那一條）。來源節已有中譯時一併代入，
   正是為了讓重複的禮儀公式在全站保持同一個譯法。
"""
from __future__ import annotations

import argparse
import collections
import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT_DIR = os.path.join(ROOT, "data", "avesta", "sources", "text")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

#: 太短的節不代入：兩三個字的巧合相同不足以證明是同一句。
MIN_WORDS = 3


def norm(text: str | None) -> str:
    """正規化原文轉寫：只留字母與單一空白，供逐字比對。

    大小寫、標點、換行、節號括號都不影響「是不是同一句」。

    🚨 非字母一律換成**空白**，不可直接刪掉：轉寫是逐行斷的，
       刪掉換行會把 `ýazamaidê\\nahurem` 黏成 `ýazamaidêahurem`，
       於是同一句在兩處因斷行位置不同而比不出相同——漏代而無聲。

    🚨 別自己列字母集：蓋爾德納轉寫用到 ý ð þ ŋ š ž ə 與一整排變音符號，
       列漏一個（第一版就漏了 ý）會把該字母整個吃掉，比對照樣「成功」。
       用 isalpha() 認所有 Unicode 字母。

    >>> norm('(zôt,) ithâ ât ýazamaidê\\nahurem mazdãm')
    'zôt ithâ ât ýazamaidê ahurem mazdãm'
    >>> norm('Têm at ÂHÛIRYÂ nâmênî.') == norm('têm  at âhûiryâ nâmênî')
    True
    >>> norm(None)
    ''
    """
    return " ".join(
        "".join(c if c.isalpha() else " " for c in (text or "").lower()).split())


def is_substantial(normalised: str) -> bool:
    """夠長到足以認定「同一句」嗎？

    >>> is_substantial('ashem vohu')
    False
    >>> is_substantial('ithâ ât azamaidê ahurem mazdãm')
    True
    """
    return len(normalised.split()) >= MIN_WORDS


def build_donors(segments: list[dict]) -> dict[str, list[dict]]:
    """把「有英譯」的段落依正規化原文建索引。

    >>> d = build_donors([{'ref': 'Y 1.1', 'orig': 'a b c', 'en': 'A B C'},
    ...                   {'ref': 'Y 2.1', 'orig': 'a b c', 'en': ''}])
    >>> list(d), [s['ref'] for s in d['a b c']]
    (['a b c'], ['Y 1.1'])
    """
    out: dict[str, list[dict]] = collections.defaultdict(list)
    for s in segments:
        n = norm(s.get("orig"))
        if n and is_substantial(n) and (s.get("en") or "").strip():
            out[n].append(s)
    return dict(out)


def pick_donor(donors: list[dict]) -> dict:
    """多個來源節時挑英譯最完整的那個（其餘在報告裡列為分歧）。

    >>> pick_donor([{'ref': 'A', 'en': 'short'}, {'ref': 'B', 'en': 'much longer one'}])['ref']
    'B'
    """
    return max(donors, key=lambda s: len(s.get("en") or ""))


def make_note(donor_ref: str, with_zh: bool) -> str:
    """代入標示。**這句話就是「不默默代入」本身**，不可省略。

    >>> make_note('Y 37.3', True)
    'SBE 此處未另譯；本節原文與 Y 37.3 逐字相同，英譯與中譯代入該節。'
    >>> make_note('Y 61.1', False)
    'SBE 此處未另譯；本節原文與 Y 61.1 逐字相同，英譯代入該節。'
    """
    what = "英譯與中譯" if with_zh else "英譯"
    return f"SBE 此處未另譯；本節原文與 {donor_ref} 逐字相同，{what}代入該節。"


def main() -> int:
    ap = argparse.ArgumentParser(description="祆教：逐字相同的節代入譯文")
    ap.add_argument("--apply", action="store_true", help="寫檔（預設只報告）")
    a = ap.parse_args()

    paths = sorted(glob.glob(os.path.join(TEXT_DIR, "*.json")))
    docs = {p: json.loads(io.open(p, encoding="utf-8").read()) for p in paths}
    everything = [s for d in docs.values() for s in d["segments"]]
    donors = build_donors(everything)

    filled = 0
    with_zh = 0
    conflicts = 0
    short = 0
    touched: set[str] = set()
    rows: list[tuple[str, str, bool]] = []

    for p, d in docs.items():
        for s in d["segments"]:
            if (s.get("en") or "").strip() or not (s.get("orig") or "").strip():
                continue
            n = norm(s.get("orig"))
            if not n:
                continue
            if not is_substantial(n):
                short += 1
                continue
            cand = donors.get(n)
            if not cand:
                continue
            # 🚨 來源節不可是自己（同一個 ref 不會同時缺又不缺，但防呆）
            cand = [c for c in cand if c.get("ref") != s.get("ref")]
            if not cand:
                continue
            if len({(c.get("en") or "").strip() for c in cand}) > 1:
                conflicts += 1
            donor = pick_donor(cand)
            dzh = (donor.get("zh") or "").strip()
            s["en"] = donor["en"]
            if dzh:
                s["zh"] = dzh
                with_zh += 1
            s["note"] = make_note(donor["ref"], bool(dzh))
            filled += 1
            touched.add(p)
            rows.append((s["ref"], donor["ref"], bool(dzh)))

    for ref, dref, z in rows:
        print(f"  {ref:12s} ← {dref:12s} {'（含中譯）' if z else ''}")
    print(f"\n可代入 {filled} 段（其中 {with_zh} 段連中譯一起代入）"
          f"　來源分歧 {conflicts}　太短不代入 {short}")

    if not a.apply:
        print("（只報告，未寫檔。要寫檔加 --apply）")
        return 0

    for p in sorted(touched):
        io.open(p, "w", encoding="utf-8").write(
            json.dumps(docs[p], ensure_ascii=False, indent=2) + "\n")
    print(f"✓ 已寫 {len(touched)} 個檔")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
