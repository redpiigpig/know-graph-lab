# -*- coding: utf-8 -*-
"""課堂簡報（PPTX）。

講義全文在線上與紙本，簡報只放課堂上要投影的骨架：命題、對照、圖表、
討論題。因此投影片內容是「編輯過的重點」而非講義段落的搬運。

每一次上課一份，內容以 DECKS[<次數>] 的資料結構描述，版面由本檔統一渲染。
成品依 docs/repo-hygiene.md 不進 git，輸出到 Drive：
  G:\\我的雲端硬碟\\資料\\知識圖工作室\\教學\\{課程資料夾}\\簡報\\

用法：
  python scripts/course_slides_pptx.py          # 第 1 次
  python scripts/course_slides_pptx.py 1 2
"""
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Cm, Pt

DRIVE = Path(r'G:\我的雲端硬碟\資料\知識圖工作室\教學')
FOLDER = '115-1_世界宗教文化導論'

HEI = '微軟正黑體'
KAI = '標楷體'
NAVY = RGBColor(0x1F, 0x39, 0x64)
GOLD = RGBColor(0xB2, 0x8B, 0x3C)
INK = RGBColor(0x22, 0x22, 0x22)
GRAY = RGBColor(0x6B, 0x72, 0x80)
PALE = RGBColor(0xF4, 0xF6, 0xF9)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

W, H = Cm(33.87), Cm(19.05)   # 16:9


# ── 版面工具 ────────────────────────────────────────────────────────────────
def textbox(slide, x, y, w, h, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    return tf


def put(tf, text, size, font=HEI, bold=False, color=INK, space_after=6,
        align=PP_ALIGN.LEFT, first=False, line=1.25, indent=0):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_after = Pt(space_after)
    p.line_spacing = line
    if indent:
        p.level = min(indent, 4)
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.name = font
    r.font.bold = bold
    r.font.color.rgb = color
    return p


def band(slide, color, x, y, w, h):
    from pptx.enum.shapes import MSO_SHAPE
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    s.fill.solid()
    s.fill.fore_color.rgb = color
    s.line.fill.background()
    s.shadow.inherit = False
    return s


def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def slide_title(slide, title, sub=None):
    band(slide, NAVY, Cm(0), Cm(0), W, Cm(0.28))
    tf = textbox(slide, Cm(2.0), Cm(1.15), W - Cm(4.0), Cm(2.2))
    put(tf, title, 30, bold=True, color=NAVY, first=True, space_after=2)
    if sub:
        put(tf, sub, 15, color=GRAY, space_after=0)
    band(slide, GOLD, Cm(2.0), Cm(3.8), Cm(2.6), Cm(0.10))


def footer(slide, n, label):
    tf = textbox(slide, Cm(2.0), H - Cm(1.3), W - Cm(4.0), Cm(0.8))
    put(tf, f'{label}　　{n}', 10, color=GRAY, first=True, space_after=0)


# ── 各種投影片 ──────────────────────────────────────────────────────────────
def s_cover(prs, d):
    s = blank(prs)
    band(s, NAVY, Cm(0), Cm(0), W, H)
    tf = textbox(s, Cm(3.0), Cm(4.2), W - Cm(6.0), Cm(1.0))
    put(tf, d['kicker'], 15, color=RGBColor(0xC9, 0xD3, 0xE4), first=True, space_after=0)
    tf = textbox(s, Cm(3.0), Cm(5.5), W - Cm(6.0), Cm(2.4))
    put(tf, d['title'], 44, font=KAI, bold=True, color=WHITE, first=True, space_after=0)
    band(s, GOLD, Cm(3.0), Cm(8.5), Cm(3.4), Cm(0.12))
    tf2 = textbox(s, Cm(3.0), Cm(9.5), W - Cm(6.0), Cm(6.0))
    put(tf2, d['subtitle'], 20, font=KAI, color=RGBColor(0xE3, 0xC9, 0x8A),
        first=True, space_after=24)
    for line in d['meta']:
        put(tf2, line, 14, color=RGBColor(0xC9, 0xD3, 0xE4), space_after=6)
    return s


def s_section(prs, no, title, lines):
    s = blank(prs)
    band(s, PALE, Cm(0), Cm(0), W, H)
    band(s, NAVY, Cm(0), Cm(0), Cm(0.5), H)
    tf = textbox(s, Cm(3.4), Cm(5.4), W - Cm(6.4), Cm(8.0))
    put(tf, no, 17, bold=True, color=GOLD, first=True, space_after=12)
    put(tf, title, 38, font=KAI, bold=True, color=NAVY, space_after=18)
    for ln in lines:
        put(tf, ln, 16, color=GRAY, space_after=6)
    return s


def s_big(prs, text, sub=None):
    s = blank(prs)
    band(s, NAVY, Cm(0), Cm(0), W, H)
    tf = textbox(s, Cm(3.2), Cm(2.6), W - Cm(6.4), H - Cm(5.2), anchor=MSO_ANCHOR.MIDDLE)
    put(tf, text, 32, font=KAI, bold=True, color=WHITE, first=True,
        align=PP_ALIGN.CENTER, line=1.45, space_after=16)
    if sub:
        put(tf, sub, 16, color=RGBColor(0xE3, 0xC9, 0x8A), align=PP_ALIGN.CENTER)
    return s


def s_bullets(prs, title, bullets, sub=None):
    s = blank(prs)
    slide_title(s, title, sub)
    tf = textbox(s, Cm(2.0), Cm(4.7), W - Cm(4.0), H - Cm(6.5))
    firstdone = False
    for b in bullets:
        lvl, txt = (b if isinstance(b, tuple) else (0, b))
        if txt == '':
            put(tf, ' ', 8, first=not firstdone, space_after=0); firstdone = True; continue
        size = {0: 20, 1: 16.5, 2: 14.5}[lvl]
        color = {0: INK, 1: RGBColor(0x3A, 0x3A, 0x3A), 2: GRAY}[lvl]
        mark = {0: '▍', 1: '‧', 2: '－'}[lvl]
        put(tf, f'{mark} {txt}', size, color=color, bold=(lvl == 0),
            first=not firstdone, space_after={0: 10, 1: 6, 2: 4}[lvl],
            indent=lvl, line=1.3)
        firstdone = True
    return s


def s_two(prs, title, left, right, sub=None):
    s = blank(prs)
    slide_title(s, title, sub)
    colw = (W - Cm(5.0)) / 2
    for i, (head, items) in enumerate((left, right)):
        x = Cm(2.0) + i * (colw + Cm(1.0))
        band(s, NAVY if i == 0 else GOLD, x, Cm(4.7), colw, Cm(0.9))
        tfh = textbox(s, x + Cm(0.35), Cm(4.85), colw - Cm(0.7), Cm(0.7))
        put(tfh, head, 16, bold=True, color=WHITE, first=True, space_after=0)
        tf = textbox(s, x + Cm(0.35), Cm(6.0), colw - Cm(0.7), H - Cm(7.9))
        for j, it in enumerate(items):
            lvl, txt = (it if isinstance(it, tuple) else (0, it))
            put(tf, ('‧ ' if lvl == 0 else '　－ ') + txt,
                16 if lvl == 0 else 13.5,
                color=INK if lvl == 0 else GRAY,
                first=(j == 0), space_after=7, line=1.3)
    return s


def s_table(prs, title, headers, rows, sub=None, note=None, widths=None):
    s = blank(prs)
    slide_title(s, title, sub)
    top = Cm(4.8)
    tbl = s.shapes.add_table(len(rows) + 1, len(headers),
                             Cm(2.0), top, W - Cm(4.0), Cm(1.0)).table
    # 列高給最小值，讓 PowerPoint 依內容自動撐開（不要平均攤滿整頁）
    for i, r in enumerate(tbl.rows):
        r.height = Cm(0.95) if i == 0 else Cm(0.8)
    if widths:
        total = sum(widths)
        for i, w in enumerate(widths):
            tbl.columns[i].width = int((W - Cm(4.0)) * w / total)
    for ci, h in enumerate(headers):
        c = tbl.cell(0, ci)
        c.text = ''
        c.fill.solid(); c.fill.fore_color.rgb = NAVY
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf = c.text_frame; tf.word_wrap = True
        put(tf, h, 13, bold=True, color=WHITE, first=True, space_after=0,
            align=PP_ALIGN.CENTER)
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            c = tbl.cell(ri + 1, ci)
            c.text = ''
            c.fill.solid()
            c.fill.fore_color.rgb = WHITE if ri % 2 == 0 else PALE
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.margin_top = c.margin_bottom = Cm(0.12)
            tf = c.text_frame; tf.word_wrap = True
            put(tf, str(val), 12, color=INK, first=True, space_after=0, line=1.15)
    if note:
        tf = textbox(s, Cm(2.0), H - Cm(2.75), W - Cm(4.0), Cm(1.3))
        put(tf, note, 11, color=GRAY, first=True, space_after=0)
    return s


RENDER = {'cover': s_cover, 'section': s_section, 'big': s_big,
          'bullets': s_bullets, 'two': s_two, 'table': s_table}


def build(deck):
    prs = Presentation()
    prs.slide_width, prs.slide_height = W, H
    for i, item in enumerate(deck['slides']):
        kind, args = item[0], list(item[1:])
        kw = args.pop() if args and isinstance(args[-1], dict) and kind != 'cover' else {}
        s = RENDER[kind](prs, *args, **kw)
        if kind not in ('cover', 'section', 'big'):
            footer(s, i, deck['footer'])
    outdir = DRIVE / FOLDER / '簡報'
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / deck['filename']
    prs.save(out)
    return out, len(deck['slides'])


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    from course_slides_data import DECKS
    for n in (sys.argv[1:] or ['1']):
        out, cnt = build(DECKS[int(n)])
        print(f'✔ {out}　（{cnt} 張）')
