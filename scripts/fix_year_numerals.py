# -*- coding: utf-8 -*-
"""把譯文裡的**西元年份**從漢數字改成阿拉伯數字。

使用者 2026-09-11 定調：「年份像是 1901 年，都要寫阿拉伯數字而非中文字」。
豪斯評傳整本寫「一八九三年」，讀起來像清末譯本，而且要在年表裡對照時很難掃。

判準只有一條：**連續四個漢數字**（〇一二三四五六七八九，含異體 零壹…）。
四位數就是西元年，中文不會用四個連號漢數字表示別的東西。

🚨 三種**絕不可動**的，動了就是改錯史實或改壞中文：

  年號紀年   「明治二十四年」「大正十二年」——那是**位值寫法**（二十四），不是四個
             連號數字，而且年號本來就該用漢數字。本支的判準自然排除它們。
  數量與序數 「三十年」「第三章」「二十世紀」——同上，不是四位連號。
  引文原文   青空文庫的日文原文欄、並列的「原文　／　中譯」——**只改中文欄**，
             原文欄照錄。src 一律不碰。

範圍除了「四位數＋年」，還收兩種：
  「一八九三至一八九六年」——前一個沒有接「年」，靠後面的範圍標記認出來
  「一九二〇年代」——接的是「年代」，照樣算

  python -X utf8 scripts/fix_year_numerals.py --scan            # 只數，不改
  python -X utf8 scripts/fix_year_numerals.py --author howes --apply
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = ROOT / ".claude" / "skills" / "ebook-collected-works"

DIGITS = {"〇": "0", "零": "0", "一": "1", "壹": "1", "二": "2", "貳": "2",
          "三": "3", "參": "3", "四": "4", "肆": "4", "五": "5", "伍": "5",
          "六": "6", "陸": "6", "七": "7", "柒": "7", "八": "8", "捌": "8",
          "九": "9", "玖": "9", "○": "0", "Ｏ": "0"}
D = "".join(DIGITS)

# 四個連號漢數字。前後不可再接漢數字，否則「一八九三四」這種會被切錯。
_RUN = re.compile(rf"(?<![{D}])([{D}]{{4}})(?![{D}])")
# 範圍標記：一八九三**至**一八九六年
_RANGE = re.compile(rf"(?<![{D}])([{D}]{{4}})\s*([至到–—～~\-－]{{1}})\s*([{D}]{{4}})\s*年")
# 年份標記：四位數後面直接接「年」（含「年代」「年間」「年起」…）
_YEAR = re.compile(rf"(?<![{D}])([{D}]{{4}})\s*(?=年)")


def to_arabic(run: str) -> str:
    return "".join(DIGITS[c] for c in run)


def fix(text: str) -> str:
    """一段文字 → 西元年份改成阿拉伯數字。純函式，測試鎖在
    tests/test_fix_year_numerals.py。"""
    t = text or ""
    # 先處理範圍（前一個數字沒有接「年」，單看 _YEAR 抓不到）
    t = _RANGE.sub(lambda m: f"{to_arabic(m.group(1))}{m.group(2)}{to_arabic(m.group(3))}年", t)
    t = _YEAR.sub(lambda m: to_arabic(m.group(1)), t)
    return t


def count(text: str) -> int:
    """這一段有幾處會被改。"""
    return 0 if not text else sum(1 for _ in _RUN.finditer(text)) - sum(
        1 for _ in _RUN.finditer(fix(text)))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--author", help="只跑某一位（資料夾名去掉 _data，例 howes）")
    ap.add_argument("--work")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--show", type=int, default=0)
    args = ap.parse_args()

    dirs = sorted(DATA_ROOT.glob("*_data"))
    if args.author:
        dirs = [d for d in dirs if d.name == f"{args.author}_data"]
    grand = 0
    shown = 0
    for data in dirs:
        for slug in sorted(p for p in data.iterdir() if p.is_dir()):
            if args.work and slug.name != args.work:
                continue
            n = 0
            for f in sorted(slug.glob("sec*.json")):
                try:
                    d = json.loads(f.read_text(encoding="utf-8"))
                except Exception:
                    continue
                zh = d.get("zh") or []
                touched = False
                for i, z in enumerate(zh):
                    if not z:
                        continue
                    new = fix(z)
                    if new == z:
                        continue
                    n += 1
                    if shown < args.show:
                        shown += 1
                        m = _RUN.search(z)
                        a = max(0, m.start() - 24) if m else 0
                        print(f"   {slug.name}/{f.stem}[{i}]")
                        print(f"     舊 …{z[a:a+70]}…")
                        print(f"     新 …{fix(z[a:a+70])}…")
                    if args.apply:
                        zh[i] = new
                        touched = True
                if touched:
                    d["zh"] = zh
                    f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
            if n:
                print(f"  {data.name:18} {slug.name:24} {n:>5} 段")
                grand += n
    print(f"\n{'已改' if args.apply else '待改'} {grand} 段")
    if not args.apply:
        print("加 --apply 才會真的寫入；🚨 只動中文欄，原文欄（src）一律不碰")


if __name__ == "__main__":
    main()
