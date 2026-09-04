#!/usr/bin/env python3
"""替國小英語單字卡自己畫圖：數字、星期、月份、上下午。

這一批詞沒有任何圖庫畫得出來——OpenMoji 的數字鍵帽只到 10，星期一到星期日、
八月到十一月、a.m./p.m. 更是一張都沒有。而使用者要的是**這副卡不留白**。

拿近似的圖充數是不行的（`eleven o'clock` 是時鐘不是十一），所以這裡自己畫。
畫出來的東西刻意**不帶文字語言**，只用數量與位置表達：

    十一   → 十一個點，外加阿拉伯數字 11
    第九   → 十個圈，第九個塗滿
    星期三 → 一條七格的週條，第三格塗滿
    十月   → 三乘四的年曆格，第十格塗滿
    上午   → 鐘面上半圈塗滿

這樣卡背才是一張真的圖：正面英文、背面圖加中文，中間不靠另一種文字轉手。
畫風對齊 OpenMoji：黑色描邊、平塗、同一組藍黃橘。

    python scripts/english_picture_tiles.py --write
    python scripts/english_picture_tiles.py --probe        # 排成樣張看一遍
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "output/source-cache/flashcards/english-tiles"

SIZE = 618
INK = (0, 0, 0, 255)
BLUE = (97, 178, 228, 255)      # OpenMoji 的藍
YELLOW = (252, 234, 43, 255)
ORANGE = (244, 170, 65, 255)
PAPER = (255, 255, 255, 255)
LINE = 10
FONT_PATH = "C:/Windows/Fonts/NotoSans-Bold.ttf"

# 每個字頭要畫哪一種圖。鍵是卡上的字頭，值是 (畫法, 參數)。
PLAN: dict[str, tuple[str, object]] = {}
CARDINALS = {
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "dozen": 12,
}
BIG = {"thirty": "30", "forty": "40", "fifty": "50", "sixty": "60",
       "seventy": "70", "eighty": "80", "ninety": "90", "hundred": "100",
       "thousand": "1000", "million": "1,000,000"}
ORDINALS = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
            "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10}
WEEKDAYS = {"Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4,
            "Friday": 5, "Saturday": 6, "Sunday": 7}
MONTHS = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5,
          "June": 6, "July": 7, "August": 8, "September": 9, "October": 10,
          "November": 11, "December": 12}
HALF_DAY = {"a.m.": "am", "p.m.": "pm"}

for word, value in CARDINALS.items():
    PLAN[word] = ("count", value)
for word, text in BIG.items():
    PLAN[word] = ("numeral", text)
for word, value in ORDINALS.items():
    PLAN[word] = ("ordinal", value)
for word, value in WEEKDAYS.items():
    PLAN[word] = ("weekday", value)
for word, value in MONTHS.items():
    PLAN[word] = ("month", value)
for word, value in HALF_DAY.items():
    PLAN[word] = ("halfday", value)
PLAN["half"] = ("half", None)
PLAN["week"] = ("weekday", 0)          # 整條七格都塗，那就是「一週」
PLAN["month"] = ("month", 0)           # 整張年曆都塗，那就是「一個月」
PLAN["weekend"] = ("weekday", -1)      # 週條的最後兩格


def canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    return image, ImageDraw.Draw(image)


def font(points: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, points)


def centered(draw, text: str, y: int, points: int, fill=INK) -> None:
    face = font(points)
    left, top, right, bottom = draw.textbbox((0, 0), text, font=face)
    draw.text(((SIZE - (right - left)) / 2 - left, y - top), text, font=face, fill=fill)


def draw_count(value: int) -> Image.Image:
    """幾就畫幾個點。點數本身就是那個字的意思，不需要任何文字。"""

    image, draw = canvas()
    columns = 5 if value > 4 else value
    rows = math.ceil(value / columns)
    cell = min(96, int(430 / max(columns, rows)))
    radius = int(cell * 0.36)
    grid_w = columns * cell
    top = 70 + (300 - rows * cell) // 2
    left = (SIZE - grid_w) // 2
    drawn = 0
    for row in range(rows):
        in_row = min(columns, value - drawn)
        offset = left + (grid_w - in_row * cell) // 2
        for column in range(in_row):
            cx = offset + column * cell + cell // 2
            cy = top + row * cell + cell // 2
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius),
                         fill=BLUE, outline=INK, width=LINE)
        drawn += in_row
    centered(draw, str(value), 430, 150)
    return image


def draw_numeral(text: str) -> Image.Image:
    image, draw = canvas()
    draw.rounded_rectangle((60, 170, SIZE - 60, SIZE - 170), radius=46,
                           fill=YELLOW, outline=INK, width=LINE)
    points = 210 if len(text) <= 2 else (150 if len(text) == 3 else 110)
    centered(draw, text, 232, points)
    return image


def draw_ordinal(value: int) -> Image.Image:
    """十個圈，第 N 個塗滿——序數說的正是「排在第幾個」。"""

    image, draw = canvas()
    cell, radius, middle = 60, 26, 290
    left = (SIZE - 10 * cell) // 2
    for index in range(1, 11):
        cx = left + (index - 1) * cell + cell // 2
        draw.ellipse((cx - radius, middle - radius, cx + radius, middle + radius),
                     fill=ORANGE if index == value else PAPER, outline=INK, width=9)
    tip = left + (value - 1) * cell + cell // 2
    draw.polygon([(tip, middle - 56), (tip - 46, middle - 136), (tip + 46, middle - 136)],
                 fill=ORANGE, outline=INK)
    centered(draw, f"{value}", 370, 150)
    return image


def draw_weekday(value: int) -> Image.Image:
    """七格的週條，第 N 格塗滿。value=0 代表整週，-1 代表週末那兩格。"""

    image, draw = canvas()
    cell = 78
    left = (SIZE - 7 * cell) // 2
    top = 220
    for index in range(1, 8):
        box = (left + (index - 1) * cell, top, left + index * cell, top + 110)
        filled = value == 0 or index == value or (value == -1 and index >= 6)
        draw.rectangle(box, fill=BLUE if filled else PAPER, outline=INK, width=8)
    draw.rounded_rectangle((left - 14, top - 78, left + 7 * cell + 14, top + 124),
                           radius=26, outline=INK, width=LINE)
    draw.rectangle((left - 14, top - 78, left + 7 * cell + 14, top - 8),
                   fill=ORANGE, outline=INK, width=8)
    for x in (left + 90, left + 7 * cell - 90):
        draw.rectangle((x - 14, top - 118, x + 14, top - 48), fill=PAPER,
                       outline=INK, width=8)
    return image


def draw_month(value: int) -> Image.Image:
    """三乘四的年曆，第 N 格塗滿。value=0 代表整年裡的「一個月」都算。"""

    image, draw = canvas()
    cell_w, cell_h = 132, 96
    left = (SIZE - 4 * cell_w) // 2
    top = 150
    for index in range(1, 13):
        row, column = divmod(index - 1, 4)
        box = (left + column * cell_w, top + row * cell_h,
               left + (column + 1) * cell_w, top + (row + 1) * cell_h)
        filled = index == value or value == 0
        draw.rectangle(box, fill=YELLOW if filled else PAPER, outline=INK, width=8)
    return image


def draw_halfday(part: str) -> Image.Image:
    """鐘面塗上半圈是上午，下半圈是下午。"""

    image, draw = canvas()
    box = (99, 99, SIZE - 99, SIZE - 99)
    draw.ellipse(box, fill=PAPER, outline=INK, width=LINE)
    draw.pieslice(box, 180, 360, fill=YELLOW) if part == "am" else \
        draw.pieslice(box, 0, 180, fill=BLUE)
    draw.ellipse(box, outline=INK, width=LINE)
    draw.line((SIZE / 2, 99, SIZE / 2, SIZE - 99), fill=INK, width=8)
    centre = SIZE / 2
    draw.line((centre, centre, centre, centre - 150), fill=INK, width=14)
    draw.line((centre, centre, centre + 110, centre), fill=INK, width=14)
    draw.ellipse((centre - 18, centre - 18, centre + 18, centre + 18), fill=INK)
    return image


def draw_half() -> Image.Image:
    image, draw = canvas()
    box = (109, 109, SIZE - 109, SIZE - 109)
    draw.ellipse(box, fill=PAPER, outline=INK, width=LINE)
    draw.pieslice(box, 90, 270, fill=ORANGE)
    draw.ellipse(box, outline=INK, width=LINE)
    draw.line((SIZE / 2, 109, SIZE / 2, SIZE - 109), fill=INK, width=LINE)
    return image


DRAW = {
    "count": draw_count, "numeral": draw_numeral, "ordinal": draw_ordinal,
    "weekday": draw_weekday, "month": draw_month, "halfday": draw_halfday,
    "half": lambda _: draw_half(),
}


def filename(word: str) -> str:
    return "tile-" + word.replace(".", "").replace(" ", "-").lower() + ".png"


def render_all(out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    made: dict[str, Path] = {}
    for word, (kind, value) in PLAN.items():
        path = out_dir / filename(word)
        DRAW[kind](value).save(path)
        made[word] = path
    return made


def main() -> None:
    parser = argparse.ArgumentParser(description="畫數字、星期、月份、上下午的卡背圖")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--probe", action="store_true", help="排成一張樣張看過再收")
    args = parser.parse_args()

    made = render_all(OUT_DIR)
    print(f"  {len(made)} 張 → {OUT_DIR}")
    if args.probe:
        columns, cell = 8, 150
        rows = math.ceil(len(made) / columns)
        sheet = Image.new("RGB", (columns * cell, rows * (cell + 26)), "white")
        pen = ImageDraw.Draw(sheet)
        label = ImageFont.truetype(FONT_PATH, 15)
        for index, (word, path) in enumerate(made.items()):
            row, column = divmod(index, columns)
            tile = Image.open(path).resize((cell - 16, cell - 16))
            sheet.paste(tile, (column * cell + 8, row * (cell + 26) + 4), tile)
            pen.text((column * cell + 8, row * (cell + 26) + cell - 4), word,
                     font=label, fill="black")
        out = ROOT / "output/flashcards/english-tiles.png"
        sheet.save(out)
        print(f"  樣張 → {out}")


if __name__ == "__main__":
    main()
