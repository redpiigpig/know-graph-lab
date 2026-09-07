"""把國小英語 50 課課程排成 B5 課本 docx（家教用紙本）。

原本的 Desktop/kids-english/ 專案連同 Happy_English_v3.docx 已佚失，這支腳本
從版控裡的課程資料重出。分課改成 50 課 × 20 字，跟 1000 張印刷單字卡一致
（舊的 20 課 × 50 字結構留在 /english 網站）。

配圖用單字卡那份人工校對過的對照表，取代課本原本自動比對的 emoji
（order→獅子、summer→啤酒那一批）。

排版規格沿用使用者定案：B5、不要 KK 音標、英文 >= 13pt、中文 >= 12pt、
課內不分頁（換下一課才換頁）、課文在單字前。超過 300 頁就分上下兩冊。

用法：
    python scripts/build_english_textbook.py              # 單冊
    python scripts/build_english_textbook.py --split      # 強制分上下冊
    python scripts/build_english_textbook.py --lessons 1-25 --volume 上冊
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
COURSE = ROOT / "public" / "content" / "english" / "course50"
CARD_IMAGES = ROOT / "output" / "source-cache" / "flashcards" / "english-card-images.json"
IMAGE_ROOT = ROOT / "output" / "source-cache" / "flashcards"
CACHE = ROOT / "output" / "english-textbook" / "img-cache"
OUT_DIR = ROOT / "output" / "english-textbook"

FONT_EN = "Verdana"
FONT_ZH = "微軟正黑體"

PALETTE = [
    "E76F51", "F4A261", "E9C46A", "2A9D8F", "264653",
    "C1666B", "48A9A6", "D4B483", "8E7CC3", "6D9DC5",
]

BLANK = "＿" * 12


# ---------------------------------------------------------------- 低階排版工具

def style_run(run, size, *, bold=False, italic=False, color=None, font_en=FONT_EN):
    """python-docx 不會自己設 eastAsia 字型，中文會掉回新細明體。"""
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    rfonts.set(qn("w:eastAsia"), FONT_ZH)
    rfonts.set(qn("w:ascii"), font_en)
    rfonts.set(qn("w:hAnsi"), font_en)


def para(container, *, space_before=0, space_after=4, align=None, indent=None, line=1.26):
    p = container.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing = line
    if align is not None:
        p.alignment = align
    if indent is not None:
        pf.left_indent = Cm(indent)
    return p


def text(container, s, size=13, **kw):
    run_kw = {k: kw.pop(k) for k in ("bold", "italic", "color", "font_en") if k in kw}
    p = para(container, **kw)
    style_run(p.add_run(s), size, **run_kw)
    return p


def cell_shade(cell, hexcolor):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hexcolor)
    cell._tc.get_or_add_tcPr().append(shd)


def para_shade(p, hexcolor):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hexcolor)
    p._p.get_or_add_pPr().append(shd)


def stick(p):
    """跟下一段黏在一起，別被分頁拆開。

    只用在「區塊標題 -> 內文」與「英文句 -> 中譯」這兩處。早期版本對幾乎每一段
    都設 keep_with_next，等於要求 Word 把整課塞進同一頁；排不下就整塊往後推，
    每頁尾巴都空掉一大半。課內不分頁指的是不要硬插分頁符，不是不准跨頁。
    """
    p.paragraph_format.keep_with_next = True


def no_table_split(table):
    for row in table.rows:
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))


def set_table_borders(table, color="D9D9D9", size=4):
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(size))
        el.set(qn("w:color"), color)
        borders.append(el)
    table._tbl.tblPr.append(borders)


def clear_cell(cell):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    return p


# ---------------------------------------------------------------- 配圖

def load_card_images() -> dict:
    return json.loads(CARD_IMAGES.read_text(encoding="utf-8"))["images"]


def alternates(en: str):
    """課本詞條有 'mother / mom'、'yes/yeah' 這種寫法，單字卡那邊是拆開的。"""
    yield en
    yield en.strip()
    yield en.strip().lower()
    for part in re.split(r"[/、]", en):
        part = part.strip()
        if part:
            yield part
            yield part.lower()


def resolve_image(en: str, images: dict) -> Path | None:
    for cand in alternates(en):
        entry = images.get(cand)
        if entry:
            path = IMAGE_ROOT / entry["file"]
            if path.exists():
                return path
    return None


def thumb(src: Path, px=140) -> Path:
    """618px 的原圖直接嵌會讓 docx 破百 MB，先縮成印刷夠用的尺寸。"""
    CACHE.mkdir(parents=True, exist_ok=True)
    out = CACHE / f"{src.stem}.{px}.png"
    if out.exists():
        return out
    im = Image.open(src).convert("RGBA")
    im.thumbnail((px, px), Image.LANCZOS)
    canvas = Image.new("RGBA", (px, px), (255, 255, 255, 0))
    canvas.paste(im, ((px - im.width) // 2, (px - im.height) // 2), im)
    canvas.save(out)
    return out


# ---------------------------------------------------------------- 各區塊

def section_head(doc, title, color):
    """區塊標題。

    原本這裡放 emoji（放大鏡、書本…），但 Verdana 與微軟正黑體都沒有那些字符，
    轉成 PDF 後整排變成空心方框。改用實心色塊，兩個字型都畫得出來。
    """
    p = para(doc, space_before=10, space_after=5)
    para_shade(p, "F7F4EF")
    style_run(p.add_run("  ▍"), 14.5, bold=True, color=color)
    style_run(p.add_run(f"{title}  "), 14.5, bold=True, color=color)
    stick(p)
    return p


def add_cover(doc, lessons, volume: str):
    for _ in range(3):
        para(doc, space_after=0)
    text(doc, "Happy English", 40, bold=True, color="E76F51",
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    text(doc, "快樂學英語", 30, bold=True, color="264653",
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)
    if volume:
        text(doc, volume, 20, bold=True, color="8E7CC3",
             align=WD_ALIGN_PARAGRAPH.CENTER, space_after=16)
    total = sum(len(l["words"]) for l in lessons)
    text(doc, f"國小英語 1000 字　‧　全 50 課", 15,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6, color="6B6B6B")
    text(doc, "課文 ‧ 單字 ‧ 文法 ‧ 例句 ‧ 練習 ‧ 解答", 13,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=40, color="6B6B6B")
    text(doc, "家教講義用書", 14, align=WD_ALIGN_PARAGRAPH.CENTER,
         space_after=4, color="8E7CC3")
    span = f"第 {lessons[0]['no']} 課－第 {lessons[-1]['no']} 課"
    text(doc, f"本冊收 {span} ‧ 共 {len(lessons)} 課 ‧ {total} 個單字", 12,
         align=WD_ALIGN_PARAGRAPH.CENTER, color="9A9A9A")
    doc.add_page_break()


def add_toc(doc, lessons):
    text(doc, "目　錄", 22, bold=True, color="264653",
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)
    table = doc.add_table(rows=0, cols=3)
    table.autofit = False
    widths = (Cm(1.7), Cm(7.4), Cm(5.1))
    set_table_borders(table, "E8E8E8")
    for lesson in lessons:
        color = PALETTE[(lesson["no"] - 1) % len(PALETTE)]
        row = table.add_row()
        for cell, w in zip(row.cells, widths):
            cell.width = w
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = clear_cell(row.cells[0])
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        style_run(p.add_run(f"L{lesson['no']}"), 13, bold=True, color=color)
        p = clear_cell(row.cells[1])
        style_run(p.add_run(lesson["title_zh"]), 13, bold=True)
        p2 = row.cells[1].add_paragraph()
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(0)
        style_run(p2.add_run(lesson["title_en"]), 11, color="8A8A8A", italic=True)
        p = clear_cell(row.cells[2])
        style_run(p.add_run(lesson.get("grammar", "")), 10.5, color="6B6B6B")
    no_table_split(table)
    doc.add_page_break()


def add_objectives(doc, lesson, color):
    section_head(doc, "學習目標", color)
    stick(text(doc, lesson["intro_zh"], 12, space_after=5))
    for item in lesson["can_do"]:
        p = para(doc, space_after=2, indent=0.5)
        style_run(p.add_run("□ "), 13, color=color, bold=True)
        style_run(p.add_run(item), 12)
        stick(p)


def add_reading(doc, lesson, color):
    reading = lesson["reading"]
    section_head(doc, "課文", color)
    p = para(doc, space_after=6)
    style_run(p.add_run(reading["title_en"]), 14, bold=True, color="264653")
    style_run(p.add_run(f"　{reading['title_zh']}"), 12, color="8A8A8A")
    stick(p)
    for i, s in enumerate(reading["sentences"], 1):
        p = para(doc, space_after=1, indent=0.5)
        style_run(p.add_run(f"{i}. "), 12, color="B0B0B0")
        style_run(p.add_run(s["en"]), 13)
        stick(p)
        p = para(doc, space_after=5, indent=1.0)
        style_run(p.add_run(s["zh"]), 12, color="6B6B6B")


def add_words(doc, lesson, color, images, stats):
    words = lesson["words"]
    section_head(doc, f"單字（{len(words)} 字）", color)
    # 英文與中譯放同一格。分成兩個窄欄時 grandmother/grandma、Dragon Boat Festival
    # 這類長詞會被 Word 從字中間硬斷成「yes/yea + h」，同格才有足夠寬度自然折行。
    rows = (len(words) + 1) // 2
    table = doc.add_table(rows=rows, cols=4)
    table.autofit = False
    widths = (Cm(0.85), Cm(6.25)) * 2
    set_table_borders(table, "EDEDED")
    for r in range(rows):
        for c in range(4):
            table.cell(r, c).width = widths[c]
    for idx, word in enumerate(words):
        r, half = idx % rows, idx // rows
        base = half * 2
        img_cell = table.cell(r, base)
        img_cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = clear_cell(img_cell)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        src = resolve_image(word["en"], images)
        if src:
            p.add_run().add_picture(str(thumb(src)), width=Cm(0.62))
            stats["with_image"] += 1
        else:
            stats["no_image"] += 1
            stats["missing"].append(word["en"])
        cell = table.cell(r, base + 1)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = clear_cell(cell)
        style_run(p.add_run(word["en"]), 13, bold=True)
        style_run(p.add_run(f"　{word['zh']}"), 12, color="4A4A4A")
    no_table_split(table)


def add_grammar(doc, lesson, color):
    section_head(doc, "文法", color)
    for point in lesson["grammar_points"]:
        stick(text(doc, point["title_zh"], 13, bold=True, color="264653",
                           space_before=5, space_after=3))
        stick(text(doc, point["explain_zh"], 12, space_after=5, indent=0.3))
        rows = point.get("table")
        if rows:
            width = max(len(r) for r in rows)
            table = doc.add_table(rows=len(rows), cols=width)
            set_table_borders(table, "D9D9D9")
            for r, line in enumerate(rows):
                for c in range(width):
                    cell = table.cell(r, c)
                    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                    p = clear_cell(cell)
                    value = line[c] if c < len(line) else ""
                    if r == 0:
                        cell_shade(cell, "F2EFE9")
                        style_run(p.add_run(value), 12, bold=True, color=color)
                    else:
                        style_run(p.add_run(value), 12)
            no_table_split(table)
            para(doc, space_after=4)
        for ex in point.get("examples") or []:
            p = para(doc, space_after=1, indent=0.5)
            style_run(p.add_run("‧ "), 13, color=color)
            style_run(p.add_run(ex["en"]), 13)
            stick(p)
            p = para(doc, space_after=4, indent=0.9)
            style_run(p.add_run(ex["zh"]), 12, color="6B6B6B")
            stick(p)


def add_sentences(doc, lesson, color):
    section_head(doc, "例句與對話", color)
    for s in lesson["sentences"]:
        p = para(doc, space_after=1, indent=0.4)
        style_run(p.add_run("‧ "), 13, color=color)
        style_run(p.add_run(s["en"]), 13)
        stick(p)
        p = para(doc, space_after=4, indent=0.8)
        style_run(p.add_run(s["zh"]), 12, color="6B6B6B")
    dialogue = lesson.get("dialogue")
    if dialogue:
        stick(text(doc, dialogue["title_zh"], 13, bold=True,
                           color="264653", space_before=6, space_after=4))
        for line in dialogue["lines"]:
            p = para(doc, space_after=1, indent=0.4)
            style_run(p.add_run(f"{line['sp']}："), 12, bold=True, color=color)
            style_run(p.add_run(line["en"]), 13)
            stick(p)
            p = para(doc, space_after=4, indent=1.4)
            style_run(p.add_run(line["zh"]), 12, color="6B6B6B")


OPTION_LABELS = "ABCD"


def add_exercises(doc, lesson, color):
    ex = lesson["exercises"]
    section_head(doc, f"練習一：選擇題（{len(ex['mcq'])} 題）", color)
    for i, item in enumerate(ex["mcq"], 1):
        p = para(doc, space_after=1, indent=0.4)
        style_run(p.add_run("（　　）"), 12, color="9A9A9A")
        style_run(p.add_run(f" {i}. "), 12, bold=True, color=color)
        style_run(p.add_run(item["q"]), 13)
        stick(p)
        p = para(doc, space_after=4, indent=1.5)
        for label, opt in zip(OPTION_LABELS, item["opts"]):
            style_run(p.add_run(f"({label}) "), 12, color=color)
            style_run(p.add_run(f"{opt}　"), 13)

    section_head(doc, f"練習二：填空（{len(ex['fill'])} 題）", color)
    for i, item in enumerate(ex["fill"], 1):
        p = para(doc, space_after=4, indent=0.4)
        style_run(p.add_run(f"{i}. "), 12, bold=True, color=color)
        style_run(p.add_run(item["q"]), 13)

    section_head(doc, f"練習三：句子重組（{len(ex['unscramble'])} 題）", color)
    for i, item in enumerate(ex["unscramble"], 1):
        p = para(doc, space_after=2, indent=0.4)
        style_run(p.add_run(f"{i}. "), 12, bold=True, color=color)
        style_run(p.add_run(item["q"]), 13)
        stick(p)
        p = para(doc, space_after=5, indent=0.9)
        style_run(p.add_run("→ " + BLANK), 13, color="C4C4C4")

    section_head(doc, f"練習四：造句翻譯（{len(ex['translate'])} 題）", color)
    for i, item in enumerate(ex["translate"], 1):
        p = para(doc, space_after=2, indent=0.4)
        style_run(p.add_run(f"{i}. "), 12, bold=True, color=color)
        style_run(p.add_run(item["q"]), 12)
        stick(p)
        p = para(doc, space_after=5, indent=0.9)
        style_run(p.add_run("→ " + BLANK), 13, color="C4C4C4")


def add_answers(doc, lesson, color):
    ex = lesson["exercises"]
    section_head(doc, "解答", color)
    labels = {"mcq": "一、選擇", "fill": "二、填空",
              "unscramble": "三、重組", "translate": "四、造句"}
    for key in ("mcq", "fill", "unscramble", "translate"):
        items = ex.get(key) or []
        if not items:
            continue
        if key == "mcq":
            parts = []
            for i, item in enumerate(items, 1):
                idx = item["opts"].index(item["ans"]) if item["ans"] in item["opts"] else 0
                parts.append(f"{i}.({OPTION_LABELS[idx]})")
            answer = "　".join(parts)
        else:
            answer = "　".join(f"{i}. {item['ans']}" for i, item in enumerate(items, 1))
        p = para(doc, space_after=3, indent=0.3)
        style_run(p.add_run(labels[key] + "　"), 12, bold=True, color=color)
        style_run(p.add_run(answer), 12, color="4A4A4A")


def add_lesson(doc, lesson, first, images, stats):
    color = PALETTE[(lesson["no"] - 1) % len(PALETTE)]
    if not first:
        doc.add_page_break()
    p = para(doc, space_after=2)
    style_run(p.add_run(f"Lesson {lesson['no']}　"), 22, bold=True, color=color)
    style_run(p.add_run(lesson["title_zh"]), 22, bold=True, color="264653")
    stick(p)
    p = para(doc, space_after=4)
    style_run(p.add_run(lesson["title_en"]), 13, italic=True, color="8A8A8A")
    style_run(p.add_run(f"　｜　{lesson.get('grammar', '')}"), 11.5, color="9A9A9A")
    stick(p)
    add_objectives(doc, lesson, color)
    add_reading(doc, lesson, color)
    add_words(doc, lesson, color, images, stats)
    add_grammar(doc, lesson, color)
    add_sentences(doc, lesson, color)
    add_exercises(doc, lesson, color)
    add_answers(doc, lesson, color)


# ---------------------------------------------------------------- 主流程

def load_course(spec: str | None) -> list[dict]:
    files = sorted(COURSE.glob("L*.json"))
    if not files:
        raise SystemExit(f"還沒有課程資料：{COURSE}\n先跑 scripts/build_english_course50.py")
    lessons = [json.loads(f.read_text(encoding="utf-8")) for f in files]
    lessons.sort(key=lambda l: l["no"])
    if spec:
        lo, _, hi = spec.partition("-")
        lo, hi = int(lo), int(hi or lo)
        lessons = [l for l in lessons if lo <= l["no"] <= hi]
    return lessons


def build(lessons: list[dict], out_path: Path, volume: str = "") -> dict:
    images = load_card_images()
    stats = {"with_image": 0, "no_image": 0, "missing": []}

    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(18.2)   # JIS B5
    section.page_height = Cm(25.7)
    section.left_margin = section.right_margin = Cm(2.0)
    section.top_margin = section.bottom_margin = Cm(1.9)

    normal = doc.styles["Normal"]
    normal.font.name = FONT_EN
    normal.font.size = Pt(13)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONT_ZH)

    add_cover(doc, lessons, volume)
    add_toc(doc, lessons)
    for i, lesson in enumerate(lessons):
        add_lesson(doc, lesson, i == 0, images, stats)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out_path)
    stats.update(lessons=len(lessons),
                 words=sum(len(l["words"]) for l in lessons),
                 questions=sum(len(q) for l in lessons
                               for q in l["exercises"].values()))
    return stats


def report(out: Path, stats: dict):
    print(f"寫出 {out}（{out.stat().st_size / 1024 / 1024:.1f} MB）")
    print(f"  {stats['lessons']} 課 / {stats['words']} 字 / {stats['questions']} 題")
    print(f"  有配圖 {stats['with_image']}　無配圖 {stats['no_image']}")
    if stats["missing"]:
        print("  無配圖詞：" + "、".join(stats["missing"]))


PAGE_LIMIT = 300
DRIVE = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\教學\家教_國小英語")


def to_pdf(docx: Path) -> Path:
    """走 Word COM 轉檔。不要用 LibreOffice——見 scripts/docx2pdf.ps1 的註記。"""
    subprocess.run([sys.executable, str(ROOT / "scripts" / "office_to_pdf.py"),
                    str(docx)], check=True)
    return docx.with_suffix(".pdf")


def page_count(pdf: Path) -> int:
    import fitz
    with fitz.open(pdf) as doc:
        return doc.page_count


def publish(paths: list[Path]):
    DRIVE.mkdir(parents=True, exist_ok=True)
    for path in paths:
        target = DRIVE / path.name
        shutil.copy2(path, target)
        print(f"  → {target}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lessons", help="課次範圍，例如 1-25")
    ap.add_argument("--volume", default="", help="冊別，例如 上冊")
    ap.add_argument("--split", action="store_true", help="直接分成上下兩冊")
    ap.add_argument("--pdf", action="store_true", help="順便轉 PDF")
    ap.add_argument("--publish", action="store_true", help="轉完 PDF 複製到 Drive 家教夾")
    ap.add_argument("-o", "--out")
    args = ap.parse_args()

    lessons = load_course(args.lessons)
    if args.split:
        half = (len(lessons) + 1) // 2
        groups = [("上冊", lessons[:half]), ("下冊", lessons[half:])]
    else:
        groups = [(args.volume, lessons)]

    made: list[Path] = []
    for name, group in groups:
        if not group:
            continue
        if args.out and len(groups) == 1:
            out = Path(args.out)
        else:
            suffix = f"_{name}" if name else ""
            out = OUT_DIR / f"Happy_English{suffix}.docx"
        report(out, build(group, out, name))
        made.append(out)

    if args.pdf or args.publish:
        for docx in list(made):
            pdf = to_pdf(docx)
            pages = page_count(pdf)
            flag = "" if pages <= PAGE_LIMIT else f"　⚠ 超過 {PAGE_LIMIT} 頁，該分冊"
            print(f"  {pdf.name}：{pages} 頁{flag}")
            made.append(pdf)

    if args.publish:
        publish(made)


if __name__ == "__main__":
    main()
