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
    """修課規定。假日班與週間班的差別只在上課節數與請假窗口。"""
    weekend = c['code'] in ('PPA066', 'PPA001')
    total = '八次' if c['code'] == 'PPA066' else ('七次' if c['code'] == 'PPA001' else '十六週')
    # 演講、參訪、報告週與考試週都算正課，缺席一樣要請假。
    out = [
        ('出席', [
            f'本課程全學期共{total}正課，另有第 17、18 週的自主學習與文本閱讀。每次上課點名。',
            '缺課時數達本科目全學期授課時數三分之一者，依本校學則規定不得參加期末考試。',
        ]),
        ('請假', [
            '請假一律事先提出：於上課前以電子郵件通知授課教師，並依系辦規定補辦請假手續。',
            '事後請假須檢附證明（診斷證明、公假單、喪假證明等），否則以缺席計。',
            '公假、病假、喪假不扣出席分數，事假逾兩次者酌扣。',
        ]),
        ('遲到早退', [
            '遲到逾十五分鐘或早退者，該次出席以二分之一計；逾半節課未到視同缺席。',
        ]),
        ('課堂進行', [
            '每次上課設有開場提問與手機即時作答（ClassPoint），請攜帶可上網的手機或平板。',
            '除即時作答與查閱資料外，課堂中請勿使用手機；錄音、錄影須先取得授課教師同意。',
        ]),
        ('考試與作業', [
            '筆試為閉書測驗，範圍見授課進度表；未依規定請假而缺考者，該次以零分計。',
            '書面作業請於指定期限前繳交，逾期一週內以八折計分，逾一週不予計分。',
        ]),
        ('學術誠信與生成式 AI', [
            '抄襲、代寫、考試舞弊者，該次成績以零分計並依校規處理。',
            '生成式 AI 可用於蒐集資料、整理大綱與潤飾文句，但須於作業末尾說明使用方式與範圍；',
            '整段由 AI 生成而未經查證、未加註明者，視同抄襲。引用文獻一律標明出處。',
        ]),
    ]
    if weekend:
        out.insert(3, ('假日班上課方式', [
            '每次上課四節（13:10–17:00），中間安排休息；請於 13:10 前入座。',
            '校外教學當次不在教室上課，集合時間、地點與交通方式另行公告，請務必留意通知。',
        ]))
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
        out.insert(4, ('期中分組報告', ['本項為分組報告，不是個人報告。'] + topic + [
            '分組與報告順序於第 8 週公告；每組報告後須繳交書面大綱一份。',
            '報告當週未到者，該項成績以零分計。',
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

    # ── 二、課程說明 ──
    heading(doc, '二、課程說明')
    para(doc, s['objective'], indent=0.4, space_after=8)

    # ── 三、成績評量 ──
    heading(doc, '三、成績評量')
    t = grid(doc, [5.0, 2.4, 9.6])
    shade(row(t, ['評量項目', '比例', '說明'], bold=True).cells)
    weekend = c['code'] in ('PPA066', 'PPA001')
    notes = {
        '出席': '每次上課點名，計算方式見第五節「修課規定」。',
        # 假日班沒有期中報告，校外參訪就是這學期的實作項目，算在課堂參與裡。
        '課堂參與': ('開場提問、手機即時作答、課堂討論，以及校外參訪活動的參與。'
                     if weekend else '開場提問、手機即時作答、課堂討論與提問。'),
        '期中報告': '分組口頭報告，分四次於課堂進行，時間見授課進度表。',
        '心得或作業撰寫': '各次上課後之閱讀心得或指定作業。',
        '期中考（筆試）': '範圍見授課進度表。',
        '期末考（筆試）': '範圍見授課進度表。',
    }
    for item, pct in c['assessment']:
        row(t, [item, pct, notes.get(item, '')])
    para(doc)

    # ── 四、授課進度 ──
    heading(doc, '四、授課進度')
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

    # ── 五、修課規定 ──
    heading(doc, '五、修課規定')
    for i, (title, items) in enumerate(rules(c), 1):
        para(doc, f'（{i}）{title}', bold=True, space_after=1, indent=0.2)
        for line in items:
            para(doc, f'　　{line}', space_after=1, indent=0.2)
    para(doc)

    # ── 六、參考書目 ──
    # 國定假日不另立一節：放假日已寫在授課進度表對應的那一列，
    # 再開一張表是多此一舉（使用者 2026-09-07 明講）。
    heading(doc, '六、參考書目')
    for i, b in enumerate(s['textbooks'], 1):
        para(doc, f'{i}. {b}', indent=0.2, space_after=1)

    outdir = DRIVE / folder
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / f"115-1修課須知_{c['name']}（{c['code']}）.docx"
    doc.save(str(out))
    return out


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    keys = [a for a in sys.argv[1:] if not a.startswith('--')] or list(CS.COURSES)
    for k in keys:
        print('✔', build(k))
