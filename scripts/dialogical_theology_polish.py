# -*- coding: utf-8 -*-
"""《諸宗教的對話神學》初稿的填充語清理。

prompt 明文禁了「值得注意的是」「你或許」這類 LLM 口頭禪，但模型守不牢，每二三十章
就會漏幾個出來。這一支把**能安全刪的**刪掉，剩下的列出來交人改寫。

🚨 分兩類處理，不可一概而論：
  A. 句首的贅詞（「值得注意的是，X」「我們可以說，X」）——整個片語連同逗號刪掉，
     句子仍然完整。只在句首（<p> 之後、或句號分號驚嘆問號之後）才刪。
  B. 句子的主幹（「你或許從未想過……」）——這種刪掉會剩下半句話，只能改寫。
     本檔不碰，只印出來。

🚨 為什麼要限定句首：「例如，我們可以說『上帝是健康的』」裡的「我們可以說」是句子的
   一部分，硬刪會變成「例如，『上帝是健康的』」——文法還通，但語氣斷掉，而且這種
   壞法不會有任何警訊。寧可少刪。

  python -X utf8 scripts/dialogical_theology_polish.py          # 試跑，只報告
  python -X utf8 scripts/dialogical_theology_polish.py --apply  # 實際寫回
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE = ROOT / "public/content/works/dialogical-theology"
HANDWRITTEN = {"chapters-d1/ch01"}          # 人手寫的那一章不要動

# A 類：句首贅詞。前面必須是段落開頭或句末標點，後面必須接逗號。
_LEAD = r"(?<=<p>)|(?<=[。！？；])"
DROPPABLE = ["值得注意的是", "我們可以說", "不難發現", "我們不難發現", "必須指出的是"]
# B 類：只報告不動手
REWRITE_ONLY = ["你或許", "你會發現", "你可能", "想像一下"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="實際寫回檔案")
    a = ap.parse_args()

    dropped = 0
    todo: list[tuple[str, str]] = []
    touched = 0

    for f in sorted(BASE.glob("chapters-d*/ch*.html")):
        key = f"{f.parent.name}/{f.stem}"
        if key in HANDWRITTEN:
            continue
        s = orig = f.read_text(encoding="utf-8")

        for w in DROPPABLE:
            s, n = re.subn(f"({_LEAD}){w}，", r"\1", s)
            dropped += n

        for w in REWRITE_ONLY:
            for m in re.finditer(f".{{0,10}}{w}.{{0,45}}", re.sub(r"<[^>]+>", "", s)):
                todo.append((key, m.group(0)))

        if s != orig:
            touched += 1
            if a.apply:
                f.write_text(s, encoding="utf-8")

    print(f"可安全刪除的贅詞 {dropped} 處，涉及 {touched} 章"
          f"{'（已寫回）' if a.apply else '（試跑，未寫回；加 --apply 才會動檔案）'}")
    if todo:
        print(f"\n需要人工改寫的 {len(todo)} 處（刪掉會剩半句話）：")
        for key, snippet in todo:
            print(f"  {key}  …{snippet}…")


if __name__ == "__main__":
    main()
