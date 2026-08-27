"""把 /works 學位論文計畫書的 markdown 轉成可直接送件的 .docx。

用法：
    python scripts/build_proposal_docx.py public/content/works/hcu-phd-proposal.md

版式（比照系上送件慣例）：
    A4、頁邊 2.54cm；內文 12pt 新細明體 + Times New Roman、行距 1.5、首行縮排兩字
    #    → 主標 18pt 置中粗體      ##   → 章節標 14pt 粗體
    ###  → 子標 13pt 粗體          #### → 小標 12pt 粗體
    *斜體行* → 置中斜體（英文題名）  **粗體** → 行內粗體
    ---  → 分隔線（略過不印）
    「參考書目」之後的段落自動改成懸掛縮排（書目體例）
"""
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

EN_FONT = "Times New Roman"
CJK_FONT = "新細明體"


def add_run(par, text, *, bold=False, italic=False, size=12):
    run = par.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.name = EN_FONT
    run._element.rPr.rFonts.set(qn("w:eastAsia"), CJK_FONT)
    return run


def add_inline(par, text, *, size=12, bold=False, italic=False):
    """只處理 **粗體**，其餘照原樣。"""
    for i, chunk in enumerate(re.split(r"\*\*([^*]+)\*\*", text)):
        if chunk:
            add_run(par, chunk, bold=bold or i % 2 == 1, italic=italic, size=size)


def new_par(doc, *, align=None, space_after=6, first_indent=None, hanging=None):
    par = doc.add_paragraph()
    fmt = par.paragraph_format
    fmt.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    fmt.space_after = Pt(space_after)
    if align is not None:
        par.alignment = align
    if first_indent is not None:
        fmt.first_line_indent = first_indent
    if hanging is not None:
        fmt.left_indent = hanging
        fmt.first_line_indent = -hanging
    return par


def build(md_path: Path, out_path: Path) -> None:
    doc = Document()
    section = doc.sections[0]
    section.page_height, section.page_width = Cm(29.7), Cm(21.0)
    for side in ("top", "bottom", "left", "right"):
        setattr(section, f"{side}_margin", Cm(2.54))

    normal = doc.styles["Normal"]
    normal.font.name = EN_FONT
    normal.font.size = Pt(12)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), CJK_FONT)

    in_biblio = False
    on_cover = True  # 「摘要」之前都算封面：一律置中、不縮排
    for raw in md_path.read_text(encoding="utf8").splitlines():
        line = raw.strip()
        if not line or re.fullmatch(r"-{3,}", line):
            continue

        head = re.match(r"^(#{1,6})\s+(.*)$", line)
        if head:
            level, text = len(head.group(1)), head.group(2)
            if text.strip() == "摘要":
                on_cover = False
            if "參考書目" in text:
                in_biblio = True
            elif level <= 2 and in_biblio and "附錄" in text:
                in_biblio = False
            size = {1: 18, 2: 14, 3: 13}.get(level, 12)
            align = WD_ALIGN_PARAGRAPH.CENTER if (level == 1 or on_cover) else None
            par = new_par(doc, align=align, space_after=10)
            par.paragraph_format.space_before = Pt(12 if level <= 2 else 8)
            add_inline(par, text, size=size, bold=True)
            continue

        # 整行斜體（英文題名）
        whole_italic = re.fullmatch(r"\*([^*].*[^*])\*", line)
        if whole_italic:
            par = new_par(doc, align=WD_ALIGN_PARAGRAPH.CENTER)
            add_run(par, whole_italic.group(1), italic=True)
            continue

        if on_cover:
            par = new_par(doc, align=WD_ALIGN_PARAGRAPH.CENTER)
        elif in_biblio:
            par = new_par(doc, space_after=4, hanging=Cm(0.85))
        else:
            par = new_par(doc, first_indent=Pt(24))
        add_inline(par, line)

    doc.save(out_path)
    print(f"{out_path}  ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    src = Path(sys.argv[1])
    build(src, src.with_suffix(".docx"))
