#!/usr/bin/env python3
"""Draw one JIS-B5-height spine per printed volume, sized from its real thickness.

Every physical volume needs its own spine, and the volumes are no longer the same
thickness: since 2026-09-08 a book may not exceed 500 pages, so the Greek reader
prints as six volumes of 264–304 pages and the Latin as three of 419–457.  A
single fixed artwork width — what the Hebrew spine used to carry — would be wrong
for all but one of them.

Width therefore comes from the rendered print master's own page count:

    書背寬 = 頁數 ÷ 2 × 每張紙厚 + 封面板

`SHEET_MM` is 80 gsm woodfree at 0.105 mm per sheet, which is what this series is
printed on; a printer using a different stock should re-run with `--sheet`.  The
height is fixed at the B5 trim of 257 mm and is never negotiable.

    python -X utf8 scripts/build_reader_spines.py            # 全部
    python -X utf8 scripts/build_reader_spines.py --only greek-original-reader-vol3
    python -X utf8 scripts/build_reader_spines.py --sheet 0.12
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import fitz
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_greek_full_reader import BOOK_LABELS as GREEK_LABELS, PARTS as GREEK_PARTS  # noqa: E402
from build_hebrew_full_reader import COVER_PALETTES  # noqa: E402
from build_japanese_full_reader import PARTS as JAPANESE_PARTS, VOLUMES as JAPANESE_VOLUMES  # noqa: E402
from build_latin_full_reader import BOOK_LABELS as LATIN_LABELS, PARTS as LATIN_PARTS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MASTERS = ROOT / "output" / "print-masters"
PDF_DIR = MASTERS
SVG_DIR = ROOT / "output" / "original-readers"

HEIGHT_MM = 257.0          # JIS B5 trim height, fixed
SHEET_MM = 0.105           # 80 gsm woodfree, per sheet
BOARD_MM = 1.0             # two cover boards plus glue
MIN_WIDTH_MM = 9.0
PT_PER_MM = 72 / 25.4
IVORY = "#FFFDF8"
YEAR = "2026"

TITLES = {
    "hbo": "聖經希伯來文原文讀本",
    "grc": "通用希臘文原文讀本",
    "la": "教會拉丁文原文讀本",
    "ja": "日文宗教學讀本",
}


def books() -> list[dict]:
    """One entry per physical volume, in shelf order."""
    out = [{
        "stem": "hebrew-original-reader-50-lessons",
        "lang": "hbo",
        "volume": "",
        "lessons": "第 01–50 課",
    }]
    for part in GREEK_PARTS:
        out.append({
            "stem": f"greek-original-reader-vol{part['book']}",
            "lang": "grc",
            "volume": GREEK_LABELS[part["book"] - 1],
            "lessons": f"第 {part['first']:02d}–{part['last']:02d} 課",
        })
    for part in LATIN_PARTS:
        out.append({
            "stem": f"latin-original-reader-vol{part['book']}",
            "lang": "la",
            "volume": LATIN_LABELS[part["book"] - 1],
            "lessons": f"第 {part['first']:02d}–{part['last']:02d} 課",
        })
    for part in JAPANESE_PARTS:
        out.append({
            "stem": f"japanese-original-reader-vol{part['book']}",
            "lang": "ja",
            "volume": part.get("label") or JAPANESE_VOLUMES[part["source"]]["label"],
            "lessons": f"第 {part['first']:02d}–{part['last']:02d} 課",
        })
    return out


def page_count(stem: str) -> int | None:
    master = MASTERS / f"{stem}.pdf"
    if not master.is_file():
        return None
    with fitz.open(master) as document:
        return document.page_count


def spine_width_mm(pages: int, sheet_mm: float) -> float:
    return max(MIN_WIDTH_MM, round(pages / 2 * sheet_mm + BOARD_MM, 1))


def mm(value: float) -> float:
    return value * PT_PER_MM


def layout(book: dict, width_mm: float) -> dict:
    """Type sizes and vertical positions, scaled to how wide the spine is."""
    title = TITLES[book["lang"]]
    title_pt = min(16.0, max(10.5, width_mm * 0.92))
    step_mm = title_pt / PT_PER_MM * 1.06
    return {
        "title": title,
        "title_pt": title_pt,
        "step_mm": step_mm,
        "top_mm": 40.0,
        "volume_pt": min(11.0, title_pt * 0.72),
        "palette": COVER_PALETTES[book["lang"]],
    }


def build_pdf(book: dict, width_mm: float, pages: int) -> Path:
    spec = layout(book, width_mm)
    palette = spec["palette"]
    path = PDF_DIR / f"{book['stem']}-spine.pdf"
    canvas = Canvas(str(path), pagesize=(mm(width_mm), mm(HEIGHT_MM)), pageCompression=1)
    canvas.setFillColor(HexColor(f"#{palette['banner']}"))
    canvas.rect(0, 0, mm(width_mm), mm(HEIGHT_MM), stroke=0, fill=1)

    center_x = mm(width_mm / 2)
    canvas.setFillColor(HexColor(IVORY))
    canvas.setFont("NotoSerifTC", spec["title_pt"])
    y_mm = HEIGHT_MM - spec["top_mm"]
    for character in spec["title"]:
        canvas.drawCentredString(center_x, mm(y_mm), character)
        y_mm -= spec["step_mm"]

    if book["volume"]:
        y_mm -= spec["step_mm"] * 0.6
        canvas.setFillColor(HexColor(f"#{palette['rule']}"))
        canvas.setFont("NotoSerifTC", spec["volume_pt"])
        for character in book["volume"]:
            canvas.drawCentredString(center_x, mm(y_mm), character)
            y_mm -= spec["volume_pt"] / PT_PER_MM * 1.06

    canvas.setStrokeColor(HexColor(f"#{palette['rule']}"))
    canvas.setLineWidth(2.4)
    canvas.line(center_x, mm(58), center_x, mm(28))
    canvas.setFillColor(HexColor(f"#{palette['rule']}"))
    canvas.setFont("NotoSerif", 7.6)
    canvas.drawCentredString(center_x, mm(16), YEAR)

    canvas.setTitle(f"{spec['title']}{('｜' + book['volume']) if book['volume'] else ''}｜B5 書背")
    canvas.setSubject(
        f"JIS B5 trim height 257 mm; spine width {width_mm} mm computed from "
        f"{pages} pages at {SHEET_MM} mm per sheet plus {BOARD_MM} mm of board. "
        "Fit to the printer's final die line if the stock differs."
    )
    canvas.showPage()
    canvas.save()
    return path


def build_svg(book: dict, width_mm: float, pages: int) -> Path:
    spec = layout(book, width_mm)
    palette = spec["palette"]
    cx = width_mm / 2
    size_mm = spec["title_pt"] / PT_PER_MM
    nodes = []
    y = spec["top_mm"]
    for character in spec["title"]:
        nodes.append(
            f'    <text x="{cx:.2f}" y="{y:.2f}" text-anchor="middle" dominant-baseline="middle" '
            f'fill="{IVORY}" font-family="Noto Serif TC, MingLiU, serif" '
            f'font-size="{size_mm:.2f}" font-weight="700">{character}</text>'
        )
        y += spec["step_mm"]
    if book["volume"]:
        y += spec["step_mm"] * 0.6
        volume_mm = spec["volume_pt"] / PT_PER_MM
        for character in book["volume"]:
            nodes.append(
                f'    <text x="{cx:.2f}" y="{y:.2f}" text-anchor="middle" dominant-baseline="middle" '
                f'fill="#{palette["rule"]}" font-family="Noto Serif TC, MingLiU, serif" '
                f'font-size="{volume_mm:.2f}">{character}</text>'
            )
            y += volume_mm * 1.06
    path = SVG_DIR / f"{book['stem']}-spine.svg"
    path.write_text(
        f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width_mm:.2f}mm" height="{HEIGHT_MM:.2f}mm" viewBox="0 0 {width_mm:.2f} {HEIGHT_MM:.2f}">
  <title>{spec['title']}{('｜' + book['volume']) if book['volume'] else ''}｜B5 書背</title>
  <desc>高度固定為 JIS B5 的 257 mm；寬度 {width_mm:.1f} mm 由 {pages} 頁、每張 {SHEET_MM} mm 加封面板 {BOARD_MM} mm 算出。紙張換過就要重算。</desc>
  <rect x="0" y="0" width="{width_mm:.2f}" height="{HEIGHT_MM:.2f}" fill="#{palette['banner']}"/>
  <g id="artwork">
{chr(10).join(nodes)}
    <line x1="{cx:.2f}" y1="199" x2="{cx:.2f}" y2="229" stroke="#{palette['rule']}" stroke-width="0.85"/>
    <text x="{cx:.2f}" y="241" text-anchor="middle" dominant-baseline="middle" fill="#{palette['rule']}" font-family="Noto Serif, serif" font-size="2.70" letter-spacing="0.25">{YEAR}</text>
  </g>
</svg>
''',
        encoding="utf-8",
    )
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="每一冊一張 B5 高書背，寬度依實際頁數")
    parser.add_argument("--only", nargs="*", default=[], help="只做這幾冊（stem）")
    parser.add_argument("--sheet", type=float, default=SHEET_MM, help="每張紙厚度 mm")
    args = parser.parse_args()

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    SVG_DIR.mkdir(parents=True, exist_ok=True)
    pdfmetrics.registerFont(TTFont("NotoSerifTC", r"C:\Windows\Fonts\NotoSerifTC-VF.ttf"))
    pdfmetrics.registerFont(TTFont("NotoSerif", r"C:\Windows\Fonts\NotoSerif-Regular.ttf"))

    missing = []
    for book in books():
        if args.only and book["stem"] not in args.only:
            continue
        pages = page_count(book["stem"])
        if pages is None:
            # 沒有印刷母版就算不出厚度。書背寬度是從書本身量出來的，不是猜的。
            missing.append(book["stem"])
            continue
        width = spine_width_mm(pages, args.sheet)
        build_pdf(book, width, pages)
        build_svg(book, width, pages)
        label = f"{TITLES[book['lang']]}{book['volume']}"
        print(f"  {label}：{pages} 頁 → 書背 {width} mm × {HEIGHT_MM:.0f} mm")
    for stem in missing:
        print(f"  {stem}：還沒有印刷母版，算不出厚度")
    raise SystemExit(1 if missing else 0)


if __name__ == "__main__":
    main()
