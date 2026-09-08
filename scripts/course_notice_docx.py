# -*- coding: utf-8 -*-
"""115-1 四門授課課程的「修課須知」→ 黑白 Word（發給學生）。

週次表讀 scripts/course_schedule.py（權威來源），課程目標與參考書目讀
scripts/course_syllabus_docx.py 的既有課程資料——兩邊都不在這裡重抄。

成品依 docs/repo-hygiene.md 不進 git，輸出到 Drive：
  G:\\我的雲端硬碟\\資料\\知識圖工作室\\教學\\{課程資料夾}\\115-1修課須知_{課名}（{課號}）.docx

用法：
  python scripts/course_notice_docx.py                  # 四門全出
  python scripts/course_notice_docx.py wr-day chinese   # 只出指定的
"""
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import course_schedule as CS                      # noqa: E402
from course_syllabus_docx import COURSES as SYL   # noqa: E402

DRIVE = Path(r'G:\我的雲端硬碟\資料\知識圖工作室\教學')

# 課號 →（Drive 資料夾, course_syllabus_docx 的鍵）
META = {
    'BBE275': ('115-1_世界宗教文化導論', 'world-religions-day'),
    'PPA001': ('115-1_世界宗教文化導論', 'world-religions-intro'),
    'BBE150': ('115-1_基督宗教概論', 'christianity'),
    'PPA066': ('115-1_宗教系國文講義', 'chinese'),
}

CN = '〇一二三四五六七八九十'


def cn(n):
    return CN[n] if n <= 10 else '十' + CN[n - 10]


FONT = '標楷體'
BODY_PT = 11


def _cjk(run, size=BODY_PT, bold=False):
    run.font.name = FONT
    run.font.size = Pt(size)
    run.bold = bold
    run._element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    return run


def para(doc, text='', size=BODY_PT, bold=False, space_after=4, indent=0, align=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.line_spacing = 1.15
    if indent:
        p.paragraph_format.left_indent = Cm(indent)
    if align is not None:
        p.alignment = align
    if text:
        _cjk(p.add_run(text), size, bold)
    return p


def heading(doc, text):
    para(doc, text, size=12, bold=True, space_after=3)


def grid(doc, widths):
    t = doc.add_table(rows=0, cols=len(widths))
    t.style = 'Table Grid'
    t.autofit = False
    for i, w in enumerate(widths):
        for c in t.columns[i].cells:
            c.width = Cm(w)
    t._widths = widths
    return t


def row(t, cells, bold=False, size=BODY_PT):
    r = t.add_row()
    for i, val in enumerate(cells):
        cell = r.cells[i]
        cell.width = Cm(t._widths[i])
        cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
        lines = val if isinstance(val, list) else [val]
        cell.paragraphs[0].text = ''
        for j, line in enumerate(lines):
            p = cell.paragraphs[0] if j == 0 else cell.add_paragraph()
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.line_spacing = 1.1
            _cjk(p.add_run(line), size, bold)
    return r


def shade(cells, hexcolor='D9D9D9'):
    """灰階網底——黑白列印仍分得出標題列。"""
    for c in cells:
        el = OxmlElement('w:shd')
        el.set(qn('w:val'), 'clear')
        el.set(qn('w:fill'), hexcolor)
        c._tc.get_or_add_tcPr().append(el)


def rules(c):
    """只放使用者親口交代過的規定。

    🚨 2026-09-09：「不要寫課程規定」「其他我沒叫你寫的都不要寫」——
    原本自己補的請假、遲到早退、課堂進行、考試與作業、學術誠信、
    假日班上課方式全部刪掉，課程說明與參考書目也一併拿掉。
    要再加任何一條，先問過。
    """
    out = [
        ('出席與課堂筆記', [
            '本課程不唱名點名：每次上課都要抄筆記，筆記就是出席的依據，'
            '下課前交由教師查看或收回。請自備筆記本，或用可書寫的裝置。',
            '沒有筆記＝該次未出席；筆記只抄投影片標題而無內容者，以出席二分之一計。',
        ]),
    ]
    topic = {
        'BBE275': [
            '題目：自選一個宗教，向全班介紹這個宗教。',
            '除口頭說明外，最好能實際演示該宗教的特色——儀式動作、器物、音樂、經典誦讀、'
            '飲食或服飾皆可，讓同學看得到、聽得到，而不只是聽你講。',
            '曾實地訪問該宗教的信徒，或參訪其宗教場所者酌予加分；'
            '請在報告中說明訪問或參訪的時間、地點與對象。',
        ],
        'BBE150': [
            '題目：自選基督宗教的一個主題進行報告。',
            '報告重點不在資料堆疊，而在說明「這個主題讓你學到什麼」——'
            '你原本怎麼想、讀了看了之後改變了什麼。',
            '曾就該主題實地詢問教會人士，或參訪教堂者酌予加分；'
            '請在報告中說明對象、時間與地點。',
        ],
    }.get(c['code'])
    if topic:
        out.append(('期中分組報告', ['本項為分組報告，不是個人報告。'] + topic + [
            '分組與報告順序於第 8 週公告；報告週仍照常上課，報告與課程單元同一節進行。',
        ]))
    out.append(('生成式 AI 的使用', [
        '考試一律不得使用生成式 AI，也不得使用任何連網裝置。',
        '製作報告與查詢資料時可以使用生成式 AI——這是現在該學會的工具，不必迴避。',
        '但不能完全照抄：AI 給的文字要用自己的話重寫，它給的人名、年代與引文'
        '一定要自己查證過再寫進去（這類資訊它常常編造）。',
        '請在報告或作業末尾用一兩句話說明你怎麼用它：用在哪個環節、問了什麼。',
    ]))
    return out


def build(key):
    c = CS.COURSES[key]
    folder, syl_key = META[c['code']]
    s = SYL[syl_key]

    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = sec.bottom_margin = Cm(1.8)
    sec.left_margin = sec.right_margin = Cm(2.0)
    style = doc.styles['Normal']
    style.font.name = FONT
    style.font.size = Pt(BODY_PT)
    style.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)

    para(doc, '玄奘大學　宗教與文化學系　115 學年度第 1 學期',
         size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    para(doc, f"{c['name']}　修課須知", size=16, bold=True,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

    # ── 一、課程基本資料 ──
    heading(doc, '一、課程基本資料')
    t = grid(doc, [2.6, 6.2, 2.2, 6.0])
    shade(row(t, ['課程名稱', c['name'], '課程代碼', c['code']]).cells[:1])
    row(t, ['開課班級', c['klass'], '選修別', f"{c['elective']}　{c['credits']} 學分"])
    row(t, ['上課時間', c['time'], '上課教室', c['room']])
    row(t, ['授課教師', CS.TEACHER, '聯絡方式', CS.EMAIL])
    for r in t.rows:
        shade([r.cells[0], r.cells[2]])
    para(doc)

    # ── 二、成績評量 ──
    heading(doc, '二、成績評量')
    t = grid(doc, [5.0, 2.4, 9.6])
    shade(row(t, ['評量項目', '比例', '說明'], bold=True).cells)
    notes = {
        '出席': '不唱名點名，以每次上課的課堂筆記為依據；詳見第五節「修課規定」。',
        '課堂參與': '開場提問、手機即時作答、課堂討論與提問。',
        '期中報告': '分組口頭報告，分四次於課堂進行，時間見授課進度表。',
        '校外參訪': '參訪活動的出席、現場參與，以及參訪後的紀錄與心得。',
        '心得或作業撰寫': '各次上課後之閱讀心得或指定作業。',
        '期中考（筆試）': '範圍見授課進度表。',
        '期末考（筆試）': '範圍見授課進度表。',
    }
    for item, pct in c['assessment']:
        row(t, [item, pct, notes.get(item, '')])
    para(doc)

    # ── 三、授課進度 ──
    heading(doc, '三、授課進度')
    t = grid(doc, [2.0, 2.4, 12.6])
    shade(row(t, ['週次', '日期', '單元內容'], bold=True).cells)
    for label, date, lines in CS.rendered_rows(c):
        row(t, [label, date, lines])
    para(doc, '＊表中單元為授課參考範圍；教師得視課堂實際進度合併或調整，'
              '異動一律於課堂公告，考試範圍以公告為準。',
         size=10, indent=0.2, space_after=2)
    para(doc, '＊第 17、18 週為自主學習與文本閱讀週，不到校上課，'
              '請於期限前與教師個別討論自評。',
         size=10, indent=0.2, space_after=8)

    # ── 四以下：使用者交代過的規定 ──
    for n, (title, items) in enumerate(rules(c), 4):
        heading(doc, f'{cn(n)}、{title}')
        for line in items:
            para(doc, f'‧{line}', indent=0.2, space_after=1)
        para(doc, '', space_after=4)

    # ── 演講與校外教學缺席的補救 ──
    mk = CS.makeup_sessions(c)
    if mk:
        heading(doc, f'{cn(len(rules(c)) + 4)}、演講與校外教學缺席時的補救')
        para(doc, f'這幾次由校外講者或現場主導，無法補課。缺席者請就該次主題觀看'
                  f'下列任一支影片（或自行找同主題的中文影片），寫 '
                  f'{CS.MAKEUP_WORDS} 字心得於下次上課時繳交，即不計缺席。',
             indent=0.2, space_after=4)
        for label, date, title, vids in mk:
            # 假日班的日期本身就帶著（六）（日），一律不再包括號，用全形空白分隔
            para(doc, f'{label}　{date}　{title}', bold=True,
                 indent=0.2, space_after=1)
            for name, url in vids:
                para(doc, f'　　‧{name}' + (f'　{url}' if url else ''),
                     size=10, indent=0.2, space_after=1)
            para(doc, '', space_after=3)

    outdir = DRIVE / folder
    outdir.mkdir(parents=True, exist_ok=True)
    # 檔名帶列印份數＝已選人數＋2（使用者 2026-09-08 定），印的時候不必再查。
    out = outdir / f"115-1修課須知_{c['name']}（{c['code']}）_印{CS.copies(c)}份.docx"
    doc.save(str(out))
    return out


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    keys = [a for a in sys.argv[1:] if not a.startswith('--')] or list(CS.COURSES)
    for k in keys:
        print('✔', build(k))
