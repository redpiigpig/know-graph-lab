#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把「整塊重複掛在連續好幾段」的英文欄，按錨點切回逐段。

  python scripts/fathers_reslice_en.py --book 709f43f9-…           # 只驗
  python scripts/fathers_reslice_en.py --book 709f43f9-… --apply

## 為什麼另寫一支

原典欄（拉丁／希臘）可以交給 `fathers_add_original.py` 從 TEI 逐段重建，英文欄不行
——它沒有可重抓的結構化來源，站上那塊就是全部。所以只能**就地切**。

切的依據是兩邊共有的錨點，兩種一起用：
  * `{{p:NNN}}` Schaff 印刷頁碼（中英兩欄都有，實測卷六 en 有 20 個、中文 36 段裡
    15 段帶）
  * 段首節號「7. 」（實測 219 段裡 86 段帶）
單用任一種都不夠，合起來才切得動。

## 為什麼沒有更精確的做法

試過、都不行，記在這裡免得再試一次：
  * **累計段落數**：中文在翻譯時被重新分段了，段落數是英文的 1.7 倍
    （卷六 228 對 125），對不起來。
  * **只用節號**：只有 39% 的段撈得到起始節號。

🚨 **沒有錨點的段留白，不沿用前一段的切片。**沿用等於把重複從「整卷」縮小成
   「一小組」——看起來好多了，但它仍然是同一段文字出現在好幾頁上，而且更難查覺。
   留白的那幾頁，其英文文字會落在前一個有錨點的段裡（切片一路切到下一個錨點），
   所以**一個字都沒有丟**，只是集中顯示。
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import shutil
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DUP_MIN_CHARS = 500

PAGE_MARK = re.compile(r"\{\{p:(\d+)\}\}")
# 段首的節號。要在段落開頭，否則會撈到句中的「約 3. 5 倍」這種。
SEC_MARK = re.compile(r"(?:^|\n)[ \t]*(\d{1,3})\.\s")


def anchors_of(text: str) -> list[tuple[str, int, int]]:
    """→ [(kind, key, 位置)]，依位置排序。kind 是 'p'（頁碼）或 's'（節號）。"""
    out = [("p", int(m.group(1)), m.start()) for m in PAGE_MARK.finditer(text or "")]
    # 🚨 位置要取 group(1) 的起點，不是 match 的起點——SEC_MARK 把前面那個換行也
    #    吃進去了，拿 m.start() 會讓切片從換行開始，切出來的頭一行是空的。
    out += [("s", int(m.group(1)), m.start(1)) for m in SEC_MARK.finditer(text or "")]
    out.sort(key=lambda x: x[2])
    return out


def block_index(block: str) -> dict[tuple[str, int], int]:
    """英文區塊裡每個錨點的位置。同一個錨點重複出現時取**最早**的一次。"""
    idx: dict[tuple[str, int], int] = {}
    for kind, key, pos in anchors_of(block):
        idx.setdefault((kind, key), pos)
    return idx


def chunk_start(zh: str, idx: dict[tuple[str, int], int]) -> int | None:
    """這一段的中文在英文區塊裡的起始位置；找不到錨點回 None。

    取這一段**最早**出現、而且英文區塊裡也有的那個錨點。頁碼優先於節號只是因為
    位置排序自然如此，不另外加權——兩者都是同一套編次。
    """
    for kind, key, _pos in anchors_of(zh):
        hit = idx.get((kind, key))
        if hit is not None:
            return hit
    return None


def plan_slices(zh_texts: list[str], block: str) -> list[str]:
    """一組共用同一塊 en 的段 → 每段各自的英文切片（沒有錨點的回空字串）。

    切片從自己的錨點一路到**下一個有錨點的段**的錨點，所以沒有錨點的段的文字會
    落在前一個有錨點的段裡——一個字都不會丟。
    """
    idx = block_index(block)
    starts = [chunk_start(z, idx) for z in zh_texts]
    out: list[str] = []
    for i, s in enumerate(starts):
        if s is None:
            out.append("")
            continue
        nxt = next((v for v in starts[i + 1:] if v is not None and v > s), len(block))
        out.append(block[s:nxt].strip())
    return out


def dup_groups(chunks: list[dict], lang: str = "en",
               min_chars: int = DUP_MIN_CHARS) -> list[list[int]]:
    groups: dict[tuple[int, str], list[int]] = collections.defaultdict(list)
    for i, c in enumerate(chunks):
        t = ((c.get("sources") or {}).get(lang)) or ""
        if len(t) >= min_chars:
            groups[(len(t), t[:120])].append(i)
    return [v for v in groups.values() if len(v) > 1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True)
    ap.add_argument("--lang", default="en")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    raw = os.environ.get("EBOOK_CHUNKS_DIR") or ""
    if not raw:
        for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
            if line.startswith("EBOOK_CHUNKS_DIR="):
                raw = line.split("=", 1)[1].strip().strip('"').strip("'")
    path = Path(raw) / f"{a.book}.jsonl"
    if not raw or not path.exists():
        print(f"找不到 {path}")
        return 1

    chunks = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    chunks.sort(key=lambda c: c.get("chunk_index", 0))
    groups = dup_groups(chunks, a.lang)
    total = sum(len(g) for g in groups)
    print(f"{a.book[:8]}  {a.lang} 整塊重複 {len(groups)} 組／{total} 段")

    planned: dict[int, str] = {}
    for g in groups:
        block = ((chunks[g[0]].get("sources") or {}).get(a.lang)) or ""
        slices = plan_slices([chunks[i].get("content") or "" for i in g], block)
        for i, sl in zip(g, slices):
            planned[i] = sl
    got = sum(1 for v in planned.values() if v)
    shrink = [len(v) for v in planned.values() if v]
    print(f"  切得出切片 {got}/{total} 段（{got / max(1, total):.0%}）；"
          f"其餘留白，文字併入前一個有錨點的段")
    if shrink:
        print(f"  切片長度 中位 {sorted(shrink)[len(shrink) // 2]} 字"
              f"（原本每段都是整塊 {len(block)} 字級）")

    if not a.apply:
        print("（只驗不寫。確認無誤後加 --apply）")
        return 0

    bak = path.with_suffix(f".jsonl.bak_reslice_{a.lang}")
    if not bak.exists():
        shutil.copy2(path, bak)
        print(f"備份 → {bak.name}")
    for i, sl in planned.items():
        c = chunks[i]
        c.setdefault("sources", {})[a.lang] = sl
        if c.get("source_lang") == a.lang:
            c["source_text"] = sl
    tmp = path.with_suffix(".jsonl.tmp")
    tmp.write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in chunks) + "\n",
                   encoding="utf-8")
    tmp.replace(path)
    print(f"已重切 {len(planned)} 段")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
