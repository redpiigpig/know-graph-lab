#!/usr/bin/env python3
"""把國小英語單字卡的配圖排成樣張，圖旁邊印英文與中文，供人逐張看過。

只印圖示名字看不出錯——`mdi:iron` 是熨斗不是鐵——所以每張圖旁邊一定要有它配到
的那個詞與中文。預設只看某一層（`--source preset`），因為自動配出來的那幾層才是
需要人看的。
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/flashcards"
MAP = CACHE / "english-card-images.json"
FONT_EN = "C:/Windows/Fonts/NotoSans-Bold.ttf"
FONT_ZH = "C:/Windows/Fonts/msjh.ttc"


def main() -> None:
    parser = argparse.ArgumentParser(description="國小英語單字卡的審圖樣張")
    parser.add_argument("--source", nargs="*", default=[], help="只看這幾層")
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--per-page", type=int, default=80)
    parser.add_argument("--columns", type=int, default=10)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    images = json.loads(MAP.read_text(encoding="utf-8"))["images"]
    rows = [(word, record) for word, record in images.items()
            if not args.source or record["source"] in args.source]
    rows.sort(key=lambda pair: pair[1]["lesson"])
    chunk = rows[(args.page - 1) * args.per_page: args.page * args.per_page]
    if not chunk:
        raise SystemExit(f"第 {args.page} 頁沒有東西（共 {len(rows)} 張）")

    cell, label_h = 118, 34
    columns = args.columns
    lines = math.ceil(len(chunk) / columns)
    sheet = Image.new("RGB", (columns * cell, lines * (cell + label_h)), "white")
    pen = ImageDraw.Draw(sheet)
    face_en = ImageFont.truetype(FONT_EN, 13)
    face_zh = ImageFont.truetype(FONT_ZH, 13)
    for index, (word, record) in enumerate(chunk):
        row, column = divmod(index, columns)
        x, y = column * cell, row * (cell + label_h)
        picture = Image.open(CACHE / record["file"]).convert("RGBA")
        picture.thumbnail((cell - 22, cell - 22))
        sheet.paste(picture, (x + (cell - picture.width) // 2,
                              y + (cell - picture.height) // 2), picture)
        pen.text((x + 4, y + cell - 4), word[:16], font=face_en, fill="black")
        pen.text((x + 4, y + cell + 13), record["glossZh"][:8], font=face_zh, fill="#B00020")
    out = Path(args.out or ROOT / f"output/flashcards/english-audit-{args.page}.png")
    sheet.save(out)
    print(f"  第 {args.page}/{math.ceil(len(rows) / args.per_page)} 頁，{len(chunk)} 張 → {out}")


if __name__ == "__main__":
    main()
