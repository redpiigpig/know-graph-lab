# -*- coding: utf-8 -*-
"""115-1 課表與行事曆 → .docx，交給使用者列印／存查。

第 1 頁橫向週課表（14 節 × 七天，跨節的課合併儲存格），第 2 頁學期行事曆。
資料與 /works 那張課表 artifact、Google 日曆「115-1 玄奘教課」是同一套，改這裡也要一起改。

★ 標的是自己授課的科目；其餘是修課與家教。
台神課與家教不對齊玄奘節次，格子畫的是概略位置，實際時間看格內標示。

用法：python scripts/semester_schedule_docx.py
輸出：G:\\我的雲端硬碟\\玄奘\\博一\\115-1 課表與行事曆.docx
"""
import datetime
import sys

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

OUT = r'G:\我的雲端硬碟\玄奘\博一\115-1 課表與行事曆.docx'

W = '一二三四五六日'
PERIODS = [(1, '08:30–09:20'), (2, '09:25–10:15'), (3, '10:25–11:15'), (4, '11:20–12:10'),
           (5, '12:10–13:10'), (6, '13:10–14:00'), (7, '14:10–15:00'), (8, '15:10–16:00'),
           (9, '16:10–17:00'), (10, '17:10–18:00'), (11, '18:30–19:15'), (12, '19:15–20:00'),
           (13, '20:10–20:55'), (14, '20:55–21:40')]

# (星期, 起節, 迄節, 標題, 副標)
GRID = [
    (1, 2, 4, '宗教研究基本問題與研究方法', '根瑟馬庫斯　妙然 208'),
    (1, 9, 10, '小三家教', '16:00–17:30'),
    (1, 12, 13, '國中家教', '19:00–20:30'),
    (2, 1, 2, '初階宗教學日文文獻選讀', '倪杰　妙然 M201'),
    (2, 7, 9, '希伯來文 II', '曾宗盛　台神　14:30–17:20'),
    (3, 1, 2, '★世界宗教文化導論', 'BBE275　妙然 401'),
    (3, 3, 4, '唯識思想專題研討', '釋昭慧、丹增南卓　妙然 206'),
    (3, 8, 9, '★基督宗教概論', 'BBE150　妙然 401'),
    (3, 10, 11, '小五家教', '17:00–18:30'),
    (3, 12, 13, '國中家教', '19:00–20:30'),
    (5, 10, 11, '小五家教', '17:00–18:30'),
    (5, 12, 13, '國中家教', '19:00–20:30'),
    (6, 1, 4, '宗教學理論與方法（一）', 'JJA051　根瑟馬庫斯　妙然 308　單週'),
    (6, 6, 9, '★國文', 'PPA066　妙然 206　單週'),
    (7, 6, 9, '★世界宗教文化導論', 'PPA001　妙然 401　雙週'),
]

# 假日授課：單週六國文八次、雙週日世界宗教八次，第 17／18 週自學
SAT = ['2026-09-12', '2026-09-26', '2026-10-10', '2026-10-24',
       '2026-11-07', '2026-11-21', '2026-12-05', '2026-12-19']
SUN = ['2026-09-20', '2026-10-04', '2026-10-18', '2026-11-01',
       '2026-11-15', '2026-11-29', '2026-12-13', '2026-12-27']

OTHER = [
    ('2026-09-05', '09:00–12:00', '弘誓學院地藏法會', '佛教弘誓學院'),
    ('2026-09-05', '18:30–20:30', '濟南教會演講', '濟南基督長老教會'),
    ('2026-09-06', '整日', '天母國三家教', '天母'),
    ('2026-09-13', '整日', '天母國三家教', '天母'),
    ('2026-09-18', '整日', '大專研究佛學研討會（協助）', ''),
    ('2026-09-19', '整日', '天母國三家教', '天母'),
    ('2026-10-03', '整日', '天母國三家教（待 Judy 確認）', '天母'),
    ('2026-10-09', '整日', '天母國三家教', '天母'),
    ('2026-10-11', '整日', '天母國三家教', '天母'),
    ('2026-10-16', '整日（–10/17）', '與 Soe San 出遊', ''),
]


def calendar_rows():
    rows = [(d, '13:10–17:00', f'國文（PPA066）　第 {i} 次', '玄奘大學 妙然 206')
            for i, d in enumerate(SAT, 1)]
    rows.append(('2027-01-02', '13:10–17:00', '國文（PPA066）　自學', '玄奘大學 妙然 206'))
    rows += [(d, '13:10–17:00', f'世界宗教文化導論（PPA001）　第 {i} 次', '玄奘大學 妙然 401')
             for i, d in enumerate(SUN, 1)]
    rows.append(('2027-01-10', '13:10–17:00', '世界宗教文化導論（PPA001）　自學', '玄奘大學 妙然 401'))
    rows += OTHER
    rows.sort(key=lambda r: (r[0], r[1]))
    return rows


def _font(run, name, size, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run._element.rPr.rFonts.set(qn('w:eastAsia'), name)
    if color:
        run.font.color.rgb = color


def head(doc, txt, size=17):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(txt)
    r.bold = True
    _font(r, '微軟正黑體', size)


def note(doc, txt):
    p = doc.add_paragraph()
    _font(p.add_run(txt), '新細明體', 8, RGBColor(0x60, 0x60, 0x60))


def cell_text(c, main, sub='', bold=False, size=8.5, center=True):
    c.text = ''
    p = c.paragraphs[0]
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(main)
    r.bold = bold
    _font(r, '微軟正黑體', size)
    if sub:
        p2 = c.add_paragraph()
        if center:
            p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(1)
        _font(p2.add_run(sub), '新細明體', 7, RGBColor(0x55, 0x55, 0x55))


def build():
    doc = Document()
    sec = doc.sections[0]
    sec.orientation = WD_ORIENT.LANDSCAPE
    sec.page_width, sec.page_height = sec.page_height, sec.page_width
    for m in ('top_margin', 'bottom_margin', 'left_margin', 'right_margin'):
        setattr(sec, m, Cm(1.5))

    st = doc.styles['Normal']
    st.font.name = '新細明體'
    st.font.size = Pt(9)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), '新細明體')

    head(doc, '辰瑋　115 學年度第 1 學期　一週課表')
    note(doc, '★ 為授課；其餘為修課與家教。節次時間依〈玄奘大學課堂時間表〉；'
              '台神課與家教不對齊玄奘節次，以格內標示時間為準。')

    t = doc.add_table(rows=len(PERIODS) + 1, cols=8)
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_text(t.cell(0, 0), '節次 / 時間', bold=True, size=9)
    for i, d in enumerate(W):
        cell_text(t.cell(0, i + 1), d, bold=True, size=10)
    for i, (n, tm) in enumerate(PERIODS):
        cell_text(t.cell(i + 1, 0), '午休' if n == 5 else f'第 {n} 節', tm, size=8)
    for day, p0, p1, main, sub in GRID:
        c = t.cell(p0, day).merge(t.cell(p1, day)) if p0 != p1 else t.cell(p0, day)
        cell_text(c, main, sub)
    t.columns[0].width = Cm(2.2)
    for c in range(1, 8):
        t.columns[c].width = Cm(3.3)

    doc.add_page_break()
    head(doc, '辰瑋　115 學年度第 1 學期　學期行事曆')
    note(doc, '假日授課與校外行程；每週固定的平日課程與家教不列於此，見前頁週課表。')

    rows = calendar_rows()
    t2 = doc.add_table(rows=len(rows) + 1, cols=5)
    t2.style = 'Table Grid'
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(['日期', '星期', '時間', '項目', '地點']):
        cell_text(t2.cell(0, i), h, bold=True, size=9.5)
    for i, (d, tm, name, loc) in enumerate(rows, 1):
        dt = datetime.date.fromisoformat(d)
        cell_text(t2.cell(i, 0), f'{dt.month}/{dt.day}', size=9)
        cell_text(t2.cell(i, 1), W[dt.weekday()], size=9)
        cell_text(t2.cell(i, 2), tm, size=8.5)
        cell_text(t2.cell(i, 3), name, size=9, center=False)
        cell_text(t2.cell(i, 4), loc, size=8.5, center=False)
    for w, c in zip([Cm(1.8), Cm(1.3), Cm(3.0), Cm(11.5), Cm(6.0)], t2.columns):
        c.width = w

    doc.save(OUT)
    return OUT, len(GRID), len(rows)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    p, g, n = build()
    print(f'✔ {p}　（週課表 {g} 格；行事曆 {n} 筆）')
