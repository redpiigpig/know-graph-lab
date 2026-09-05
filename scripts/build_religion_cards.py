#!/usr/bin/env python3
"""可裁切的印刷宗教卡：世界宗教十五張，課堂比手畫腳用。

版面、卡框沿用單字卡那一套（`build_flashcards`），同一把裁刀通吃，所以這裡不重算
任何尺寸——只換卡面。

**單面卡，沒有說明頁。** 使用者要的是比手畫腳的題目卡：抽一張、看一眼、上台比。
背面印東西反而會透光被看到，說明頁夾在裡面還要多裁一張。神觀、起源、經典、人數
那些欄位留在 JSON 裡當備課對照，不上卡。

**每一張都有圖**（使用者要求，比手畫腳要有東西可以看著比）。有十張用的是那個宗教
自己採用的符號（十字架、法輪、大衛之星……），另外六張沒有統一符號，圖是替它挑的
代表物——小米、鼓、燈籠、號角、經卷、原子。JSON 裡的 `ownSymbol` 分辨這兩種，
簡報那三頁就是拿這個差別當討論題，不要把兩種混為一談。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Mm, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_flashcards as base  # noqa: E402
import build_playing_cards as cards  # noqa: E402  （借它的 OpenMoji 載入與查圖）

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/teachingCards/world-religions.json"
OUTPUT_DIR = ROOT / "output/teaching-cards"

FRONT_COLOR = "4A4A4A"      # 正面一律深灰：四色分類是答案，不能印在題目上
ICON_MM = 24
TRANSLIT_PT = 8.5
DRAWN = {}   # 自繪符號，key 是 JSON 裡 `draw:` 後面那一段

# 「臺灣原住民族傳統宗教」十一個字與「道教」兩個字要並存，字級按長度縮
NAME_STEPS = ((3, 22), (4, 19), (6, 17), (8, 14), (10, 12), (99, 10.5))


def nine_pointed_star(color: str = "F4900C", size: int = 618) -> Path:
    """巴哈伊的九角星。emoji 集裡沒有九角星，八角星（✴）點數不對不能拿來充數；
    但它就是個幾何圖形，照 {9/3}（三個正三角形疊起來）的比例畫出來即可。"""

    from PIL import Image, ImageDraw

    path = base.CACHE / "flashcards/drawn/nine-pointed-star.png"
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)

    import math
    outer = size * 0.47
    inner = outer * math.cos(math.pi / 3) / math.cos(math.pi / 9)   # {9/3} 的內接半徑
    centre = size / 2
    points = []
    for step in range(18):
        radius = outer if step % 2 == 0 else inner
        angle = -math.pi / 2 + step * math.pi / 9
        points.append((centre + radius * math.cos(angle), centre + radius * math.sin(angle)))

    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(image).polygon(points, fill=f"#{color}")
    image.save(path)
    return path


def name_size(text: str) -> float:
    for limit, size in NAME_STEPS:
        if len(text) <= limit:
            return size
    return NAME_STEPS[-1][1]


def fill_front(cell, card: dict, icon: Path | None, place) -> None:
    cell = base.framed(cell, FRONT_COLOR, place)
    if icon:
        picture = cell.add_paragraph()
        picture.alignment = WD_ALIGN_PARAGRAPH.CENTER
        picture.paragraph_format.space_after = Pt(6)
        picture.add_run().add_picture(str(icon), width=Mm(ICON_MM))
    else:
        base.blank(cell, 16)
    name = cell.add_paragraph()
    name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    name.paragraph_format.space_after = Pt(4)
    base.write(name, card["name"], base.FONT_ZH, name_size(card["name"]))
    translit = cell.add_paragraph()
    translit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    translit.paragraph_format.space_after = Pt(0)
    base.write(translit, card["translit"], cards.FONT_LATIN, TRANSLIT_PT, color=base.MUTED)


def build(deck: dict, icons: dict[str, Path | None], output: Path) -> Path:
    document = Document()
    base.configure(document)

    per_page = base.COLS * base.ROWS
    for start in range(0, len(deck["cards"]), per_page):
        page = deck["cards"][start : start + per_page]
        if start:
            base.page_break(document)
        table = base.new_grid(document)
        for offset, card in enumerate(page):
            row, column = divmod(offset, base.COLS)
            fill_front(table.cell(row, column), card, icons[card["name"]],
                       (column, row, 1000 + start + offset))

    output.parent.mkdir(parents=True, exist_ok=True)
    document.save(output)
    return output


DRAWN["nine-pointed-star"] = nine_pointed_star


def main() -> None:
    parser = argparse.ArgumentParser(description="產生宗教卡（A4 橫式、每頁 8 張、雙面）")
    parser.add_argument("--output", default="world-religion-cards.docx")
    args = parser.parse_args()

    deck = json.loads(DATA.read_text("utf-8"))
    index = cards.openmoji()
    icons = {}
    for card in deck["cards"]:
        name = card["icon"]
        if not name:
            icons[card["name"]] = None
        elif name.startswith("draw:"):
            icons[card["name"]] = DRAWN[name[len("draw:"):]]()
        else:
            icons[card["name"]] = cards.icon_path(index, name)

    unknown = {card["category"] for card in deck["cards"]} - set(deck["categories"])
    if unknown:
        raise SystemExit(f"卡片用了沒定義的分類：{sorted(unknown)}")

    path = build(deck, icons, OUTPUT_DIR / args.output)
    tally = {name: sum(1 for c in deck["cards"] if c["category"] == name)
             for name in deck["categories"]}
    print(f"  {deck['title']}：{len(deck['cards'])} 張，"
          f"單面共 {-(-len(deck['cards']) // 8)} 頁（每頁 8 張，"
          f"{base.CARD_W_MM:.2f}×{base.CARD_H_MM:.0f} mm）")
    print("  " + "　".join(f"{k} {v} 張" for k, v in tally.items()))
    print(f"  有符號 {sum(1 for v in icons.values() if v)}，留白 {sum(1 for v in icons.values() if not v)}")
    print(path)


if __name__ == "__main__":
    main()
