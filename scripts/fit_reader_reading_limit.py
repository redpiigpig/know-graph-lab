#!/usr/bin/env python3
"""從排好的書倒推「一課讀文最多多長」——用線性回歸，不要用估的。

擁有者 2026-09-17：「一課最多不能超過 8 頁。」一課印三樣東西：二十個生詞、十題
翻譯練習、一篇讀文。前兩樣長度固定，讀文長度不固定；所以一課的頁數是

    頁數 ≈ 固定開銷 + 斜率 × 讀文長度

把每一課的（讀文長度、實際頁數）丟進最小平方，截距就是固定開銷、斜率就是「讀文
每多一個單位厚幾頁」，於是

    八頁上限 = (8 − 截距) ÷ 斜率

🚨 不要用「讀文長度 ÷ 一課總頁數」當每頁容量。那個分母含生詞頁與練習頁，密度會
低估四成，上限就砍過頭。這一系列已經用那個算法訂錯過一次。

🚨 也不要用「一頁印得下幾個原文詞」回推。日文實測一頁排得下約九十四個詞，看起來
一頁可放兩百字元，實際只有一百——差在段末沒排滿的那一列、整句中譯佔的行、單元
之間的間距。只有回歸會把這些一起算進去。

🚨 量的單位要跟裁的單位一致：希臘、拉丁、希伯來以**詞**計，日文以**字元**計，
因為各語言的 clip 函式就是這樣數的。兩邊不一致算出來的上限沒有意義。

    python -X utf8 scripts/fit_reader_reading_limit.py
    python -X utf8 scripts/fit_reader_reading_limit.py --language ja --target 8
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
CACHE = ROOT / "output" / "source-cache" / "original-readers"
PDF_DIR = ROOT / "output" / "print-masters"

LESSON_TAG = re.compile(r"第\s*(\d{1,3})\s*課")
HEBREW_WORD = re.compile(r"[֐-׿]+")

BOOKS = {
    "hbo": ["hebrew-original-reader-50-lessons"],
    "grc": [f"greek-original-reader-vol{n}" for n in range(1, 5)],
    "lat": [f"latin-original-reader-vol{n}" for n in range(1, 4)],
    "ja": [f"japanese-original-reader-vol{n}" for n in range(1, 5)],
}
# 一課同一個課次可能出現在兩冊（上下冊各自從第 1 課編號），所以量到的頁數要用
# （冊, 課）當鍵。哪幾冊算同一半，各 builder 的 PARTS 說了算。
HALVES = {
    "hbo": {"hebrew-original-reader-50-lessons": 1},
    "grc": {"greek-original-reader-vol1": 1, "greek-original-reader-vol2": 1,
            "greek-original-reader-vol3": 2, "greek-original-reader-vol4": 2},
    "lat": {"latin-original-reader-vol1": 1, "latin-original-reader-vol2": 2,
            "latin-original-reader-vol3": 2},
    "ja": {"japanese-original-reader-vol1": 1, "japanese-original-reader-vol2": 1,
           "japanese-original-reader-vol3": 2, "japanese-original-reader-vol4": 2},
}
UNIT = {"hbo": "詞", "grc": "詞", "lat": "詞", "ja": "字元"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def measured_pages(language: str) -> dict[tuple[int, int], int]:
    """每一課實際印了幾頁，從 PDF 的眉標數出來。

    眉標是 STYLEREF，整課每一頁都印同一個課次，所以數眉標就是數課的厚度。附錄那
    幾節的眉標沒有課次，碰到就停止累計——不然最後一課會把一百多頁附錄算進自己。
    """
    pages: dict[tuple[int, int], int] = defaultdict(int)
    for stem in BOOKS[language]:
        pdf = PDF_DIR / f"{stem}.pdf"
        if not pdf.is_file():
            raise SystemExit(f"找不到 {pdf}；請先 render_and_check_reader_pdfs.py")
        half = HALVES[language][stem]
        document = fitz.open(pdf)
        current = None
        for page in document:
            lines = [line.strip() for line in page.get_text().splitlines()]
            head = lines[0] if lines else ""
            tag = LESSON_TAG.search(head)
            if tag:
                current = int(tag.group(1))
            elif head:
                current = None
            if current is not None:
                pages[(half, current)] += 1
        document.close()
    return dict(pages)


def size_hbo() -> dict[tuple[int, int], int]:
    data = load(CACHE / "hebrew-full" / "hebrew-reader-50-lessons.json")
    out = {}
    for lesson in data["lessons"]:
        reading = lesson["reading"]
        if reading["kind"] == "bible_chapter":
            text = " ".join(verse["text"] for verse in reading["verses"])
        else:
            text = " ".join(segment["text"] for segment in reading["segments"])
        out[(1, lesson["lesson"])] = len(HEBREW_WORD.findall(text))
    return out


def size_grc() -> dict[tuple[int, int], int]:
    data = load(CACHE / "greek-full" / "greek-reader-two-volumes.json")
    out = {}
    for volume in data["volumes"]:
        for lesson in volume["lessons"]:
            reading = lesson["reading"]
            parts = reading.get("verses") or reading.get("segments") or []
            text = " ".join(part.get("text") or part.get("sourceText") or ""
                            for part in parts)
            out[(volume["volume"], lesson["lesson"])] = len(text.split())
    return out


def size_lat() -> dict[tuple[int, int], int]:
    import build_latin_full_reader as B
    out = {}
    for half, readings in ((1, B.upper_readings()), (2, B.lower_readings())):
        for lesson, row in readings.items():
            out[(half, lesson)] = sum(len(B.L.words(latin))
                                      for latin, _ in row["pairs"])
    return out


def size_ja() -> dict[tuple[int, int], int]:
    data = load(CACHE / "japanese-full" / "readings.json")
    out = {}
    for volume in data["volumes"]:
        for lesson in volume["lessons"]:
            out[(volume["volume"], lesson["lesson"])] = sum(
                len(unit["text"]) for unit in lesson["units"])
    return out


SIZES = {"hbo": size_hbo, "grc": size_grc, "lat": size_lat, "ja": size_ja}


def fit(points: list[tuple[float, float]]) -> tuple[float, float, float]:
    """最小平方 y = a + b x，回傳 (截距, 斜率, R²)。"""
    n = len(points)
    mean_x = sum(x for x, _ in points) / n
    mean_y = sum(y for _, y in points) / n
    sxx = sum((x - mean_x) ** 2 for x, _ in points)
    sxy = sum((x - mean_x) * (y - mean_y) for x, y in points)
    if sxx == 0:
        raise SystemExit("讀文長度完全沒有變化，回歸不出斜率")
    slope = sxy / sxx
    intercept = mean_y - slope * mean_x
    syy = sum((y - mean_y) ** 2 for _, y in points)
    residual = sum((y - (intercept + slope * x)) ** 2 for x, y in points)
    r2 = 1 - residual / syy if syy else 1.0
    return intercept, slope, r2


def report(language: str, target: int) -> None:
    pages = measured_pages(language)
    sizes = SIZES[language]()
    shared = sorted(set(pages) & set(sizes))
    missing = sorted(set(sizes) - set(pages))
    points = [(float(sizes[key]), float(pages[key])) for key in shared]
    intercept, slope, r2 = fit(points)
    limit = (target - intercept) / slope if slope > 0 else float("inf")
    unit = UNIT[language]
    over = sorted(key for key in shared if pages[key] > target)
    print(f"[{language}] 量到 {len(points)} 課"
          + (f"（另有 {len(missing)} 課沒量到：{missing[:6]}）" if missing else ""))
    print(f"  讀文長度 min={min(x for x, _ in points):.0f} "
          f"med={sorted(x for x, _ in points)[len(points) // 2]:.0f} "
          f"max={max(x for x, _ in points):.0f} {unit}")
    print(f"  頁數 = {intercept:.2f} + {slope:.5f} × 讀文（{unit}），R² = {r2:.3f}")
    print(f"  固定開銷 {intercept:.2f} 頁；讀文每 {1 / slope:.0f} {unit} 厚一頁")
    print(f"  ⇒ {target} 頁上限 = ({target} − {intercept:.2f}) ÷ {slope:.5f} "
          f"= {limit:.0f} {unit}")
    print(f"  目前超過 {target} 頁的課：{len(over)} 課"
          + (f"，最厚 {max(pages[key] for key in over)} 頁" if over else ""))
    if over:
        rows = sorted((sizes[key], pages[key], key) for key in over)
        print(f"    超過的（讀文{unit}／頁數／冊課）：{rows[:8]}")
    # 回歸線給的是**平均**，散佈在線兩側，所以照回歸值設上限會有一半的課壓在
    # 線上方。實際能過的上限是「所有不超過它的課都印得下 target 頁」的最大值——
    # 也就是第一個爆表的課的讀文長度，再減一。這是量出來的，不是估的。
    if over:
        smallest_over = min(sizes[key] for key in over)
        print(f"    ⇒ 實測安全上限 = {smallest_over - 1} {unit}"
              f"（最短的爆表課讀文 {smallest_over} {unit}）")
    else:
        print(f"    ⇒ 沒有課超過 {target} 頁")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", nargs="*", default=sorted(BOOKS),
                        choices=sorted(BOOKS))
    parser.add_argument("--target", type=int, default=8, help="一課的頁數上限")
    args = parser.parse_args()
    for language in args.language:
        report(language, args.target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
