"""Build one printer-adjustable, JIS-B5-height spine for the Hebrew reader."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "original-readers"
PDF_PATH = OUT / "hebrew-original-reader-spine-b5-height.pdf"
SVG_PATH = OUT / "hebrew-original-reader-spine-b5-height.svg"

HEIGHT_MM = 257.0
# Artwork width is intentionally adjustable.  It is not a paper-thickness
# estimate and the printer should fit it to the final cover die line.
ARTWORK_WIDTH_MM = 16.0

BROWN = "#3A2720"
GOLD = "#D4A653"
IVORY = "#FFFDF8"
PT_PER_MM = 72 / 25.4
TITLE = "聖經希伯來文原文讀本"


def mm(value: float) -> float:
    return value * PT_PER_MM


def build_pdf() -> None:
    canvas = Canvas(
        str(PDF_PATH),
        pagesize=(mm(ARTWORK_WIDTH_MM), mm(HEIGHT_MM)),
        pageCompression=1,
    )
    canvas.setFillColor(HexColor(BROWN))
    canvas.rect(0, 0, mm(ARTWORK_WIDTH_MM), mm(HEIGHT_MM), stroke=0, fill=1)
    center_x = mm(ARTWORK_WIDTH_MM / 2)
    canvas.setFillColor(HexColor(IVORY))
    canvas.setFont("NotoSerifTC", 14.8)
    for index, character in enumerate(TITLE):
        canvas.drawCentredString(center_x, mm(HEIGHT_MM - 42 - index * 14), character)
    canvas.setStrokeColor(HexColor(GOLD))
    canvas.setLineWidth(2.4)
    canvas.line(center_x, mm(58), center_x, mm(28))
    canvas.setFillColor(HexColor(GOLD))
    canvas.setFont("NotoSerif", 7.6)
    canvas.drawCentredString(center_x, mm(16), "2026")
    canvas.setTitle("聖經希伯來文原文讀本｜B5 高書背")
    canvas.setSubject(
        "JIS B5 trim height 257 mm. Width is an adjustable artwork width, "
        "not a spine-thickness calculation; fit to the printer's final die line."
    )
    canvas.showPage()
    canvas.save()


def build_svg() -> None:
    cx = ARTWORK_WIDTH_MM / 2
    title_nodes = "\n".join(
        f'    <text x="{cx:.2f}" y="{42 + index * 14:.2f}" text-anchor="middle" '
        f'dominant-baseline="middle" fill="{IVORY}" font-family="Noto Serif TC, MingLiU, serif" '
        f'font-size="5.20" font-weight="700">{character}</text>'
        for index, character in enumerate(TITLE)
    )
    SVG_PATH.write_text(
        f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{ARTWORK_WIDTH_MM:.2f}mm" height="{HEIGHT_MM:.2f}mm" viewBox="0 0 {ARTWORK_WIDTH_MM:.2f} {HEIGHT_MM:.2f}">
  <title>聖經希伯來文原文讀本｜B5 高書背</title>
  <desc>高度固定為 JIS B5 的 257 mm。寬度只是可編輯畫布，並非厚度計算；請由印刷廠依最終刀模調整。</desc>
  <rect x="0" y="0" width="{ARTWORK_WIDTH_MM:.2f}" height="{HEIGHT_MM:.2f}" fill="{BROWN}"/>
  <g id="artwork">
{title_nodes}
    <line x1="{cx:.2f}" y1="199" x2="{cx:.2f}" y2="229" stroke="{GOLD}" stroke-width="0.85"/>
    <text x="{cx:.2f}" y="241" text-anchor="middle" dominant-baseline="middle" fill="{GOLD}" font-family="Noto Serif, serif" font-size="2.70" letter-spacing="0.25">2026</text>
  </g>
</svg>
''',
        encoding="utf-8",
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    pdfmetrics.registerFont(TTFont("NotoSerifTC", r"C:\Windows\Fonts\NotoSerifTC-VF.ttf"))
    pdfmetrics.registerFont(TTFont("NotoSerif", r"C:\Windows\Fonts\NotoSerif-Regular.ttf"))
    build_pdf()
    build_svg()
    print(PDF_PATH)
    print(SVG_PATH)


if __name__ == "__main__":
    main()
