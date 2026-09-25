#!/usr/bin/env python3
"""替十四本原文讀本各做一張書背，體例與課程讀本那一套完全相同。

擁有者 2026-09-16：「這些讀本也都需要書背，你去參考我的課程讀本的書背形式。」
所以這支改成 `build_reader_spine.py`（課程讀本那一支）的作法，不再自己一套：

* 輸出是一張 **JIS B5**（182 × 257 mm）的紙，書背條照實際尺寸畫在正中間。
  讀本是 B5，書背也印在 B5 上——同一疊紙進印表機，不必換紙匣也不會被縮放。
* 書背條高 **247 mm**，比書矮 10 mm：排滿 257 mm 印表機的邊界會把它裁掉。
* **逐字直排**，一個字一個字正著寫、由上往下堆，字距等於字級。
  轉 90 度的字是側躺的，那跟直排是兩件事（參照《無境界者》雜誌的書背）。
* 半形字串用**縱中橫**：整串維持橫寫、縮到書背寬度以內，佔直排的一格。
* **不畫裁切框**。框外只印一行給影印店看的字：頁數與算出來的書背寬。
* **低於 100 頁不出書背**——那種書背只有幾公釐，裁不準也貼不上。

寬度是算出來的：雙面印，張數 = ⌈頁數 ÷ 2⌉，一張 80g 紙約 0.104 mm，再加 2 mm
給封面與膠層。🚨 紙磅數不同厚度就不同；裝訂前先量一下實際厚度再決定要不要重出。

    python -X utf8 scripts/build_reader_spines.py
    python -X utf8 scripts/build_reader_spines.py --only greek-original-reader-vol3
    python -X utf8 scripts/build_reader_spines.py --paper 100
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_greek_full_reader import BOOK_LABELS as GREEK_LABELS, PARTS as GREEK_PARTS  # noqa: E402
from build_hebrew_full_reader import PARTS as HEBREW_PARTS, part_label as hebrew_label, part_stem as hebrew_stem  # noqa: E402
from build_japanese_full_reader import BOOK_LABELS as JAPANESE_LABELS, PARTS as JAPANESE_PARTS  # noqa: E402
from build_latin_full_reader import BOOK_LABELS as LATIN_LABELS, PARTS as LATIN_PARTS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MASTERS = ROOT / "output" / "print-masters"
# 書背跟印刷母版放在一起，不是放 output/original-readers。
# `sync_reader_artifacts.py` 是拿 output/print-masters/*.pdf 當權威去同步三處的，
# 書背若不在那一夾，Drive 上留著的就永遠是舊版式那一張，而且不會有人被通知。
OUT_DIR = ROOT / "output" / "print-masters"
LEGACY_DIR = ROOT / "output" / "original-readers"

CJK = r"C:\Windows\Fonts\mingliu.ttc"
LATIN = r"C:\Windows\Fonts\times.ttf"
MM = 72 / 25.4
PAGE = (182 * MM, 257 * MM)
STRIP_H = 247 * MM
THICKNESS = {60: 0.08, 70: 0.09, 80: 0.104, 100: 0.13, 120: 0.15}

TITLES = {
    "hbo": "聖經希伯來文原文讀本",
    "grc": "通用希臘文原文讀本",
    "la": "教會拉丁文原文讀本",
    "ja": "日文宗教學讀本",
}

# 直排要用的縱書字形。橫排的括號堆在直排裡，開口是朝左右的，看起來像躺著。
# 🚨 只列細明體真的有字形的：︓︑︒ 在細明體是空的，硬換會印出空白。
VERTICAL = {
    "（": "︵", "）": "︶", "〈": "︿", "〉": "﹀",
    "《": "︽", "》": "︾", "「": "﹁", "」": "﹂",
    "『": "﹃", "』": "﹄", "—": "︱", "─": "︱",
}


def books() -> list[dict]:
    """One entry per physical volume, in shelf order."""
    out = [{"stem": hebrew_stem(part), "lang": "hbo",
            "volume": "" if len(HEBREW_PARTS) == 1 else hebrew_label(part)} for part in HEBREW_PARTS]
    for part in GREEK_PARTS:
        out.append({"stem": f"greek-original-reader-vol{part['book']}", "lang": "grc",
                    "volume": GREEK_LABELS[part["book"] - 1]})
    for part in LATIN_PARTS:
        out.append({"stem": f"latin-original-reader-vol{part['book']}", "lang": "la",
                    "volume": LATIN_LABELS[part["book"] - 1]})
    for part in JAPANESE_PARTS:
        out.append({"stem": f"japanese-original-reader-vol{part['book']}", "lang": "ja",
                    "volume": JAPANESE_LABELS[part["book"] - 1]})
    return out


def spine_width_mm(pages: int, gsm: int) -> float:
    return math.ceil(pages / 2) * THICKNESS.get(gsm, 0.104) + 2.0


def make_spine(stem: str, label: str, pages: int, gsm: int) -> tuple[Path, float]:
    w_mm = spine_width_mm(pages, gsm)
    w = w_mm * MM

    out = fitz.open()
    page = out.new_page(width=PAGE[0], height=PAGE[1])
    page.insert_font(fontname="CJK", fontfile=CJK)
    page.insert_font(fontname="TNR", fontfile=LATIN)

    x0 = (PAGE[0] - w) / 2
    y0 = (PAGE[1] - STRIP_H) / 2

    cjk_font = fitz.Font(fontfile=CJK)
    latin_font = fitz.Font(fontfile=LATIN)
    size = max(7.0, min(14.0, w - 4))
    runs = [(m.group(), bool(re.fullmatch(r"[\x00-\x7f]+", m.group())))
            for m in re.finditer(r"[\x00-\x7f]+|[^\x00-\x7f]", label)]

    def inline_size(text: str, base: float) -> float:
        """A half-width run set horizontally inside the vertical column.

        Discounted to 0.82 first: at the same point size a run of Latin digits
        sets wider than the column of Han characters beside it and reads as
        larger than them.
        """
        room = w - 3
        size_ = base * 0.82
        while size_ > 4 and latin_font.text_length(text, size_) > room:
            size_ -= 0.25
        return size_

    def column_height(base: float) -> float:
        return sum(base for _ in runs)

    while size > 6 and column_height(size) > STRIP_H:
        size -= 0.5

    centre = x0 + w / 2
    y = y0 + (STRIP_H - column_height(size)) / 2
    for text, latin in runs:
        if latin:
            small = inline_size(text, size)
            page.insert_text((centre - latin_font.text_length(text, small) / 2, y + size * 0.78),
                             text, fontname="TNR", fontsize=small)
        elif text.strip():
            page.insert_text((centre - size / 2, y + size * 0.86),
                             VERTICAL.get(text, text), fontname="CJK", fontsize=size)
        y += size

    note = f"{stem}　{pages} 頁　書背寬 {w_mm:.1f} mm（{gsm}g 紙，雙面）"
    page.insert_text((28, PAGE[1] - 16), note, fontname="CJK", fontsize=9, color=(0.45,) * 3)

    dst = OUT_DIR / f"{stem}-spine.pdf"
    # 一張紙印幾個字卻 27 MB——insert_font 會把整包細明體嵌進去。子集化之後
    # 只留用到的那幾個字，剩不到 100 KB。
    try:
        out.subset_fonts(verbose=False)
    except Exception:
        pass
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out.save(dst, garbage=4, deflate=True)
    out.close()
    _ = cjk_font
    return dst, w_mm


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="*", default=[])
    parser.add_argument("--paper", type=int, default=80, help="紙磅數（60/70/80/100/120）")
    parser.add_argument("--min-pages", type=int, default=100,
                        help="低於這個頁數就不出書背（太薄貼不上）")
    args = parser.parse_args()

    # 舊版的書背是自己一套版式（裸書背＋SVG），格式換了就不該留著混在同一夾。
    for stale in sorted(LEGACY_DIR.glob("*-spine.svg")):
        stale.unlink()
        print(f"－ 刪掉舊格式 {stale.name}")

    made = 0
    for book in books():
        if args.only and book["stem"] not in args.only:
            continue
        master = MASTERS / f"{book['stem']}.pdf"
        if not master.is_file():
            print(f"－ {book['stem']}：找不到印刷母版，先跑 render_and_check_reader_pdfs.py")
            continue
        with fitz.open(master) as document:
            pages = document.page_count
        if pages < args.min_pages:
            print(f"－ {book['stem']}　{pages} 頁（<{args.min_pages}）太薄，不出書背")
            continue
        label = TITLES[book["lang"]] + (f"　{book['volume']}" if book["volume"] else "")
        dst, w_mm = make_spine(book["stem"], label, pages, args.paper)
        print(f"✓ {dst.name}　{pages} 頁　書背寬 {w_mm:.1f} mm　{label}")
        made += 1
    if not made:
        print("一本都沒做——先把印刷母版排出來")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
