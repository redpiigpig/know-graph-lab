#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
音譯的「裡」改回「里」。

    python -X utf8 scripts/fix_li_transliteration.py            # 只看，不改
    python -X utf8 scripts/fix_li_transliteration.py --apply

opencc 簡轉繁會把音譯的「里」誤轉成「裡」：
「法里东→法**裡**東」「阿赫里曼→阿赫**裡**曼」，但「瓦伊里亚」又正確保留。
所以不是全錯，**要逐詞過**——這支就是那個逐詞的閘。

═══════════ 兩個絕對不能碰的東西 ═══════════

1. 🚨 **檔名清單**。`data/local_inventory.json` 存的是 Drive 的實際檔名
   （original_path / original_name / target_path），「邁克爾·裡夫斯」是真檔名。
   改了就對不上 Drive（同 feedback_set_books_split 的 file_path 教訓）。
2. 🚨 **「裡」的正當用法**。方位（這裡／心裡／家裡）與成語（互為表裡／字裡行間）
   本來就是「裡」。用白名單擋，不做通用取代。
"""
from __future__ import annotations

import argparse
import glob
import io
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 存實際檔名／路徑的檔，改了會對不上 Drive
SKIP_FILES = {"data/local_inventory.json"}
DRIVE_PATH = re.compile(r"[A-Z]:\\|/我的雲端硬碟/|\u6211\u7684")

# 「裡」的正當用法：方位詞、成語、口語
KEEP = re.compile(
    r"(這|那|哪|internal)裡|"
    r"[心手家夜城書房屋村山廟寺院店田水火土口眼骨懷夢腹胸袋箱盒櫃園林海河湖井窗門牆內外上下中前後左右天地世界國城鄉鎮村街巷路橋車船機場館堂室廳房廚廁院落園圃畈莊塢]裡|"
    r"裡(面|頭|外|邊|的|有|是|去|來|間|層|子|人|話|話兒)|"
    r"表裡|裡應外合|字裡行間|裡程|公裡?程|裡仁|鄰裡|故裡|鄉裡|裡弄|"
    r"一裡|千裡|萬裡|百裡|十裡|裡長"
)


def candidates(text: str) -> list[tuple[int, str]]:
    """回 [(位置, 含前後文的詞)]，已濾掉正當用法。"""
    out = []
    for m in re.finditer(r"[一-鿿]{0,3}裡[一-鿿]{0,3}", text):
        w = m.group(0)
        if KEEP.search(w):
            continue
        out.append((m.start(), w))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="音譯的「裡」改回「里」")
    ap.add_argument("--apply", action="store_true", help="真的寫檔（預設只看）")
    a = ap.parse_args()

    files = []
    for pat in ["data/**/*.ts", "data/**/*.json", "pages/**/*.vue", "pages/**/*.ts"]:
        files += glob.glob(str(ROOT / pat), recursive=True)

    words = Counter()
    per_file: dict[str, int] = {}
    skipped: list[str] = []
    for f in sorted(files):
        rel = str(Path(f).relative_to(ROOT)).replace("\\", "/")
        try:
            s = io.open(f, encoding="utf-8").read()
        except OSError:
            continue
        if "裡" not in s:
            continue
        if rel in SKIP_FILES or DRIVE_PATH.search(s[:4000]):
            n = len(candidates(s))
            if n:
                skipped.append(f"{rel}（{n} 處，存實際檔名／路徑）")
            continue
        cand = candidates(s)
        if not cand:
            continue
        for _, w in cand:
            words[w] += 1
        # 逐字改：只改候選位置的那一個「裡」
        pos = {p + w.index("裡") for p, w in cand}
        new = "".join("里" if i in pos else ch for i, ch in enumerate(s))
        per_file[rel] = len(cand)
        if a.apply and new != s:
            io.open(f, "w", encoding="utf-8", newline="").write(new)

    print(f"{'已改' if a.apply else '待改'}：{len(per_file)} 個檔、{sum(per_file.values())} 處\n")
    print("── 出現最多的詞 ──")
    for w, n in words.most_common(30):
        print(f"  {n:4d}  {w} → {w.replace('裡','里')}")
    print("\n── 檔案 ──")
    for rel, n in sorted(per_file.items(), key=lambda kv: -kv[1])[:20]:
        print(f"  {n:4d}  {rel}")
    if skipped:
        print("\n🚨 跳過（存實際檔名／路徑，改了會對不上 Drive）")
        for x in skipped:
            print(f"  {x}")
    if not a.apply:
        print("\n（這是 dry-run。確認上面的詞都是音譯之後，加 --apply）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
