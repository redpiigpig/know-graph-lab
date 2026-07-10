# -*- coding: utf-8 -*-
"""《當代的大愛道革命》全書初稿 → 網頁版 md + Word（docx）。

來源：repo 根目錄《當代的大愛道革命_全書初稿.md》
輸出：public/content/works/mahaprajapati-revolution-book.md（網頁渲染用，去工作筆記）
      public/content/works/mahaprajapati-revolution-book.docx（下載用）

Word 體例：章起新頁；訪談引文（blockquote）標楷體縮排；尾註標記上標；
章末尾註列表小字懸掛縮排。python-docx 不支援真腳註，故依本書體例採「章末尾註」。
"""
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / '當代的大愛道革命_全書初稿.md'
OUT_MD = ROOT / 'public/content/works/mahaprajapati-revolution-book.md'
OUT_DOCX = ROOT / 'public/content/works/mahaprajapati-revolution-book.docx'

KAI = 'DFKai-SB'      # 標楷體
MING = 'PMingLiU'     # 新細明體（正文）

FN_RE = re.compile(r'\[\^([^\]]+)\]')
BOLD_RE = re.compile(r'(\*\*[^*]+\*\*|\[\^[^\]]+\])')


def set_font(run, name: str, size: float | None = None, bold: bool | None = None):
    run.font.name = name
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), name)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold


def add_runs(par, text: str, font: str, size: float):
    """處理 **粗體** 與 [^n] 尾註上標。"""
    for tok in BOLD_RE.split(text):
        if not tok:
            continue
        if tok.startswith('**') and tok.endswith('**'):
            r = par.add_run(tok[2:-2])
            set_font(r, font, size, bold=True)
        elif tok.startswith('[^'):
            r = par.add_run(tok[2:-1])
            set_font(r, font, max(size - 3, 7))
            r.font.superscript = True
            r.font.color.rgb = RGBColor(0x8B, 0x1A, 0x2F)
        else:
            r = par.add_run(tok)
            set_font(r, font, size)


def build():
    md = SRC.read_text(encoding='utf-8')
    cut = md.find('## 【全書初稿工作筆記】')
    if cut >= 0:
        md = md[:cut].rstrip() + '\n'
    OUT_MD.write_text(md, encoding='utf-8')

    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = sec.bottom_margin = Cm(2.5)
    sec.left_margin = sec.right_margin = Cm(2.8)

    # 封面
    for txt, size, bold, before in [
        ('當代的大愛道革命', 26, True, 220),
        ('昭慧法師與性廣法師的人間佛教思想與實踐', 14, False, 18),
        ('張辰瑋', 14, False, 60),
        ('（全書初稿）', 10, False, 10),
    ]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(before)
        set_font(p.add_run(txt), KAI, size, bold)

    first_heading = True
    for raw in md.replace('\r\n', '\n').split('\n'):
        t = raw.strip()
        if not t or re.fullmatch(r'-{3,}', t):
            continue
        m = re.match(r'^(#{1,6})\s+(.*)$', t)
        if m:
            lvl, text = len(m.group(1)), m.group(2)
            if lvl == 1:  # 章：起新頁
                if not first_heading:
                    doc.add_page_break()
                else:
                    doc.add_page_break()
                    first_heading = False
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(36)
                p.paragraph_format.space_after = Pt(24)
                add_runs(p, text, KAI, 18)
                for r in p.runs:
                    r.font.bold = True
            else:
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(16)
                p.paragraph_format.space_after = Pt(8)
                add_runs(p, text, KAI, 14 if lvl == 2 else 12)
                for r in p.runs:
                    r.font.bold = True
            continue
        m = re.match(r'^\[\^([^\]]+)\]:\s*(.*)$', t)
        if m:  # 尾註條目：小字、懸掛縮排
            p = doc.add_paragraph()
            pf = p.paragraph_format
            pf.left_indent = Cm(1.2)
            pf.first_line_indent = Cm(-0.8)
            pf.space_after = Pt(2)
            pf.line_spacing = 1.15
            r = p.add_run(f'{m.group(1)}. ')
            set_font(r, MING, 9, bold=True)
            add_runs(p, m.group(2), MING, 9)
            continue
        if t.startswith('>'):  # 引文：標楷體、縮排
            p = doc.add_paragraph()
            pf = p.paragraph_format
            pf.left_indent = pf.right_indent = Cm(1.0)
            pf.space_before = Pt(6)
            pf.space_after = Pt(6)
            pf.line_spacing = 1.6
            add_runs(p, re.sub(r'^>\s?', '', t), KAI, 11)
            continue
        # 一般段落
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.first_line_indent = Cm(0.85)
        pf.line_spacing = 1.7
        pf.space_after = Pt(4)
        add_runs(p, t, MING, 11)

    doc.save(OUT_DOCX)
    print(f'md   → {OUT_MD} ({OUT_MD.stat().st_size:,} bytes)')
    print(f'docx → {OUT_DOCX} ({OUT_DOCX.stat().st_size:,} bytes)')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    build()
