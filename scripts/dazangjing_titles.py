#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""列出基督教大藏經某時代既有的全部 title_zh（供研究流程去重用）。

用法：
  python scripts/dazangjing_titles.py <era>
    era ∈ pre / ancient / medieval / early-modern / modern
  python scripts/dazangjing_titles.py all      # 全部時代

前藏(pre)資料在 data/dazangjing/index.ts，其餘在各自 <era>.ts。
輸出：每行一個 title_zh（已去重、排序），方便餵給 dazangjing-research workflow 的 existingTitles。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "dazangjing"
FILES = {
    "pre": DATA / "index.ts",
    "ancient": DATA / "ancient.ts",
    "medieval": DATA / "medieval.ts",
    "early-modern": DATA / "early-modern.ts",
    "modern": DATA / "modern.ts",
}

TITLE_RE = re.compile(r"title_zh:\s*'([^']+)'")


def titles_for(era: str):
    path = FILES[era]
    text = path.read_text(encoding="utf-8")
    return TITLE_RE.findall(text)


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    eras = list(FILES) if arg == "all" else [arg]
    seen = set()
    for era in eras:
        if era not in FILES:
            print(f"unknown era: {era}", file=sys.stderr)
            sys.exit(1)
        for t in titles_for(era):
            seen.add(t)
    for t in sorted(seen):
        print(t)


if __name__ == "__main__":
    main()
