# -*- coding: utf-8 -*-
"""上課筆記單 → A4 雙面 Word（發給學生手寫）。

使用者的四門課都不唱名點名，改成**每次上課抄筆記、下課前交查，筆記就是出席依據**
（2026-09-08 定）。這張單子就是那份筆記的載體：正面填基本欄位＋橫線，背面全是橫線。

課程名稱由學生自己填，所以四門課共用同一張，不必一課一版。

成品依 docs/repo-hygiene.md 不進 git，輸出到 Drive：
  G:\\我的雲端硬碟\\資料\\知識圖工作室\\教學\\115-1上課筆記單.docx

用法：python scripts/course_notes_sheet_docx.py
"""
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_ROW_HEIGHT_RULE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

# 🚨 課堂紙本放使用者自己的教學夾（同修課須知），不是網站鏡射用的
#    「資料\知識圖工作室\教學」——2026-09-09 他自己把檔案搬過去的。
OUT = (Path(r'G:\我的雲端硬碟\玄奘\博一上\教學') / '115-1修課須知'
       / '115-1上課筆記單.docx')

FONT = '標楷體'
RULE_PT = 27          # 橫線間距：約 0.95 cm，一般人手寫剛好
ROW_H = 1.4           # 欄位列高：12pt 一行約 0.7 cm，兩倍即 1.4
FRONT_RULES = 20      # 正面扣掉抬頭與欄位後放得下的行數
BACK_RULES = 24       # 背面只有一行小抬頭，放得多


def _cjk(run, size=12, bold=False):
    run.font.name = FONT
    run.font.size = Pt(size)
    run.bold = bold
    run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    return run


def para(doc, text='', size=12, bold=False, after=4, align=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(after)
    if align is not None:
        p.alignment = align
    if text:
        _cjk(p.add_run(text), size, bold)
    return p


def rule(doc):
    """一條供手寫的橫線：空段落＋下框線，行高固定。"""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = Pt(RULE_PT)
    pPr = p._p.get_or_add_pPr()
    borders = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')          # 0.75pt，夠淡不搶字
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '999999')
    borders.append(bottom)
    pPr.append(borders)
    return p


def field_table(doc):
    """基本欄位：學號／班級／姓名一列，課程名稱／上課日期／週次一列。"""
    t = doc.add_table(rows=2, cols=6)
    t.style = 'Table Grid'
    t.autofit = False
    # 兩列共用同一組欄寬，所以第 3 欄要放得下「　　年　　月　　日」九個字
    widths = [2.0, 3.4, 1.8, 4.0, 1.4, 4.4]
    for ri, cells in enumerate(([('學號', ''), ('班級', ''), ('姓名', '')],
                                [('課程名稱', ''), ('上課日期', '　　年　　月　　日'),
                                 ('週次', '第　　週')])):
        for ci, (lab, val) in enumerate(cells):
            lc, vc = t.rows[ri].cells[ci * 2], t.rows[ri].cells[ci * 2 + 1]
            for cell, text, bold, fill in ((lc, lab, True, 'EFEFEF'), (vc, val, False, None)):
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                p = cell.paragraphs[0]
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.space_before = Pt(2)
                _cjk(p.add_run(text), 12, bold)
                if fill:
                    shd = OxmlElement('w:shd')
                    shd.set(qn('w:val'), 'clear')
                    shd.set(qn('w:fill'), fill)
                    cell._tc.get_or_add_tcPr().append(shd)
    # 行高兩倍——欄位是手寫的，一行的高度寫不下（使用者 2026-09-09 要求）
    for r in t.rows:
        r.height = Cm(ROW_H)
        r.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST
    for i, w in enumerate(widths):
        for c in t.columns[i].cells:
            c.width = Cm(w)
    return t


def build():
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = sec.bottom_margin = Cm(1.6)
    sec.left_margin = sec.right_margin = Cm(1.8)
    style = doc.styles['Normal']
    style.font.name = FONT
    style.font.size = Pt(12)
    style.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)

    # ── 正面 ──
    para(doc, '上課筆記', size=18, bold=True, after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
    para(doc, '本單為出席依據，請於下課前交回。', size=10, after=6,
         align=WD_ALIGN_PARAGRAPH.CENTER)
    field_table(doc)
    para(doc, '', after=6)
    for _ in range(FRONT_RULES):
        rule(doc)

    # ── 背面 ──
    doc.add_section(WD_SECTION.NEW_PAGE)
    back = doc.sections[1]
    back.top_margin = back.bottom_margin = Cm(1.6)
    back.left_margin = back.right_margin = Cm(1.8)
    para(doc, '姓名：＿＿＿＿＿＿＿＿　　學號：＿＿＿＿＿＿＿＿　　（背面．續）',
         size=11, after=6)
    for _ in range(BACK_RULES):
        rule(doc)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUT))
    return OUT


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    print('✔', build())
