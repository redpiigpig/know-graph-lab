#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修 /fathers 幾本書被正文吞掉的 `chapter_path`，讓逐段對齊器重新認得出它們。

  python scripts/fathers_repair_chapter_paths.py --book 709f43f9-…            # 只驗
  python scripts/fathers_repair_chapter_paths.py --book 709f43f9-… --apply    # 寫回

## 為什麼要這一支

2026-09-11 稽核 `/fathers` 三欄時（`scripts/audit_fathers_columns.mjs`）查到三本書
的原典欄整卷重複：讀者翻到某一卷任何一頁，原典欄都是整卷。往下追，病灶不在補原典
那一步——`fathers_add_original.py` 本身是逐段對齊的，實測卷六錨點命中 19/19。

真正的病灶是 CCEL 那個老毛病「章節標題吞內文」的殘留：這幾本有一大批段落的
`chapter_path` **不是路徑，而是「正確章名＋整段正文」**，最長一筆 785 字。例：

    第一章 — 希拉里的生平與著述希拉里是西方教會中最偉大卻研究最不足的教父之一。他之所以…

因果鏈：路徑認不出來 → `spans_for` 直接跳過那些段 → 它們保留建書當初掛上的**整卷**
`en` 與原典欄 → 每一頁都是整卷。英文欄同病，而且早於原典欄（希拉里 359/401 段）。

## 兩步修法（都是純函式，測試在 scripts/tests/test_fathers_repair_paths.py）

1. **截斷**：吞掉的路徑開頭就是對的章名，只要把黏在後面的正文切掉。章名取自各段
   內文的 `## ` 標題行——拿實際存在的標題去比對，比用標點或長度硬切可靠。
2. **補卷次**：光有「第22章」還不夠，對齊器要的是「第六卷 第22章」才解得出
   `Span(6, 22, 22)`。卷次不在 `volume` 欄（那裡是作品名「論三位一體」），只在
   前面某一段的 `chapter_path == "第六卷"`。所以逐段往下傳遞最近看到的卷次。

🚨 **只補、不覆蓋**：本來就乾淨的路徑一律不動。卷次也只加在「修過的段」上——
   對本來就寫「第六卷」的那幾段再加一次會變成「第六卷 第六卷」。

🚨 **傳遞卷次要照 chunk_index 排序**，不是照檔案順序。兩者多半一致，但一旦有人
   重排過，照檔案順序傳會把卷次傳到別卷去，而且完全看不出來。
"""
from __future__ import annotations

import argparse
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

# 「第六卷」這種單獨的卷次路徑。有後綴（「第六卷 第1-10章」）的本來就完整，不必傳。
BOOK_ONLY = re.compile(r"^第[一二三四五六七八九十百]+卷$")
HEADING = re.compile(r"^\s*#{1,6}\s*(.+?)\s*$", re.M)
# 路徑超過這個長度就當作被正文吞了。乾淨的路徑實測最長是「第三十九至二十六條」
# 這種，遠在門檻之下。
MAX_CLEAN = 60


def headings_of(content: str) -> list[str]:
    """一段內文裡的所有 `## ` 標題文字。"""
    return [m.group(1) for m in HEADING.finditer(content or "") if m.group(1)]


def truncate_path(path: str, headings: list[str]) -> str:
    """吞掉正文的路徑 → 只留章名。認不出來就原樣回傳（不猜）。

    🚨 判準是「某個**真實存在的標題**是這條路徑的嚴格前綴」，不是長度。拿長度當
    門檻會漏——《教會史》那筆吞掉的路徑只有 61 字，門檻設 60 剛好擦邊，設 64 就
    整筆漏掉，而漏掉的徵兆是「那幾段的原典欄還是整卷」，跟沒修過一模一樣。

    比對取**最長**的相符標題：「第一章」與「第一章 — 希拉里的生平與著述」都可能
    在候選裡，短的那個會把副標切掉，而十二卷裡每一卷都有「第一章」，等於自己
    製造碰撞。
    """
    p = (path or "").strip()
    cands = [h for h in headings
             if h and p.startswith(h) and len(p) > len(h)
             and not PATH_SUFFIX.match(p[len(h):])]
    if not cands:
        return p
    return max(cands, key=len)


# 合法的路徑後綴：「索引 第3章」「論基督教教義 第1-4章」「懺悔錄 卷一 第1-10章」。
# 🚨 這些的前半（索引／論基督教教義）剛好也是某一段的 `## ` 標題，只比對前綴的話
#    會把後綴當成黏上來的正文切掉——那是把好路徑改壞，比沒修更糟。
PATH_SUFFIX = re.compile(
    r"^[\s·‧]*(?:卷[一二三四五六七八九十百0-9]+[\s·‧]*)?"
    r"(?:第[0-9一二三四五六七八九十百]+(?:\s*[-–—~至]\s*[0-9一二三四五六七八九十百]+)?[章節條]?)?"
    r"[\s·‧]*$")


# 「第一章」「第十二節」這種章節號。後面要接分隔符才算有副標。
CHAPTER_HEAD = re.compile(r"^(第[一二三四五六七八九十百千0-9]+[章節])(.*)$", re.S)
# 章名與副標之間的分隔符。實檔看到的是空白、破折號、全形破折號。
SEPARATORS = " 　-—–－:：・‧.．"


def structural_trim(path: str) -> str:
    """章號後面**沒有分隔符就直接接中文**＝那不是副標，是黏上來的正文。

    🚨 這一關是必要的第二道。第一道（比對真實標題）修不掉「標題本身就被吞了」的
    那一半——實檔 211 段裡有 104 段的 `## ` 標題自己就寫成
    「## 第一章亞流主義的一般歷史及其時代基督教思想的傾向」，截到它等於沒截。

    有分隔符的一律原樣留著：「第四章 《論三位一體》的構成與特質」「第二章 — 聖希
    拉里的神學」都是真的副標。
    """
    p = (path or "").strip()
    m = CHAPTER_HEAD.match(p)
    if not m:
        return p
    head, rest = m.group(1), m.group(2)
    if not rest or rest[0] in SEPARATORS:
        return p
    return head


def propagate_book(entries: list[dict]) -> list[str]:
    """逐段補上卷次，回傳與 entries 等長的新路徑清單。

    entries 每筆要有 `path`（已截斷過）、`repaired`（路徑是不是修過的）與 `volume`。

    🚨 **`volume` 一換就要把卷次歸零。** 同一個檔案裡不只一部著作（希拉里那冊有
    導論／論會議／論三位一體／詩篇講道／正統信仰詳解），卷次會一路傳到隔壁那部去，
    把「第一章」變成「第一卷 第一章」而其實它屬於另一部——對齊器照樣配得上，
    命中率照樣好看，配到的卻是別部的原文。
    """
    out: list[str] = []
    book = ""
    vol = object()
    for e in entries:
        p = e["path"]
        if e.get("volume") != vol:
            vol = e.get("volume")
            book = ""
        if BOOK_ONLY.match(p):
            book = p
            out.append(p)
            continue
        if e.get("repaired") and book and not p.startswith(book):
            out.append(f"{book} {p}")
        else:
            out.append(p)
    return out


def repair_chunks(chunks: list[dict]) -> tuple[list[str], int]:
    """→ (與 chunks 等長的新 chapter_path, 改動段數)。chunks 依 chunk_index 排序。

    🚨 標題池要取**全書**的，不能只看該段自己。一章通常橫跨好幾段，而 `## ` 標題
    只出現在該章第一段；只看自己的話，接續段永遠找不到候選——實檔 211 段裡有 71 段
    就是這樣留在原地，而它們正是原典欄整卷重複的大宗。
    """
    pool = sorted({h for c in chunks for h in headings_of(c.get("content") or "")},
                  key=len, reverse=True)
    entries = []
    for c in chunks:
        old = c.get("chapter_path") or ""
        new = structural_trim(truncate_path(old, pool))
        entries.append({"path": new, "repaired": new != old, "volume": c.get("volume")})
    paths = propagate_book(entries)
    changed = sum(1 for c, p in zip(chunks, paths) if (c.get("chapter_path") or "") != p)
    return paths, changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True, help="ebook id")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--show", type=int, default=8)
    a = ap.parse_args()

    raw = os.environ.get("EBOOK_CHUNKS_DIR") or ""
    if not raw:
        for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
            if line.startswith("EBOOK_CHUNKS_DIR="):
                raw = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not raw:
        print("EBOOK_CHUNKS_DIR 沒設（.env 讀不到？）")
        return 1
    path = Path(raw) / f"{a.book}.jsonl"
    if not path.exists():
        print(f"找不到 {path}")
        return 1

    chunks = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    chunks.sort(key=lambda c: c.get("chunk_index", 0))
    before_bad = sum(1 for c in chunks if len(c.get("chapter_path") or "") > MAX_CLEAN)
    paths, changed = repair_chunks(chunks)
    after_bad = sum(1 for p in paths if len(p) > MAX_CLEAN)

    print(f"{a.book[:8]}  共 {len(chunks)} 段")
    print(f"  被正文吞掉：{before_bad} → {after_bad}；共改動 {changed} 段")
    shown = 0
    for c, p in zip(chunks, paths):
        old = c.get("chapter_path") or ""
        if old == p or shown >= a.show:
            continue
        shown += 1
        print(f"  #{c['chunk_index']:4}  {old[:46]!r}\n         → {p!r}")

    if not a.apply:
        print("\n（只驗不寫。確認無誤後加 --apply）")
        return 0

    bak = path.with_suffix(".jsonl.bak_paths")
    if not bak.exists():
        shutil.copy2(path, bak)
        print(f"\n備份 → {bak.name}")
    for c, p in zip(chunks, paths):
        c["chapter_path"] = p
    tmp = path.with_suffix(".jsonl.tmp")
    tmp.write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in chunks) + "\n",
                   encoding="utf-8")
    tmp.replace(path)
    print(f"已寫回 {path.name}（{changed} 段）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
