# -*- coding: utf-8 -*-
"""玄奘大學課程授課大綱 → Word（照學校「114.2 基督宗教概論」表單體例）。

表單七區塊：課程基本資料／核心能力／課程目標／教學方法／修課提醒／
授課進度與內容（18 週）／學習評量方式／學習參考資源。

成品是 docx，依 docs/repo-hygiene.md 不進 git，輸出到 Drive：
  G:\\我的雲端硬碟\\資料\\知識圖工作室\\教學\\{學年學期}_{課名}\\

用法：python scripts/course_syllabus_docx.py [course_key ...]（預設全部）
"""
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

HEI = 'Microsoft JhengHei'
MING = 'PMingLiU'
DRIVE = Path(r'G:\我的雲端硬碟\資料\知識圖工作室\教學')

# ── 課程資料 ────────────────────────────────────────────────────────────────
WORLD_RELIGIONS = {
    'key': 'world-religions-intro',
    'folder': '115-1_世界宗教文化導論',
    'filename': '115.1世界宗教文化導論',
    'basic': [
        ('學年', '115', '學期', '1'),
        ('授課教師', '張辰瑋', '開課系所', '宗教與文化學系'),
        ('班級', '宗教與文化學系二年制在職專班1年A班（雙週）', '授課語言', '主要：中文\n次要：'),
        ('上課時數', '2', '學分數', '2'),
        ('選修別', '專業必修', '課程名稱', '世界宗教文化導論'),
        ('課程代碼', 'PPA001', '上課時間地點', '週日 13:00–17:00　妙然401'),
        ('課程描述', '世界宗教文化導論', '課程屬性', ''),
        ('前置課程', '', '延伸課程', ''),
    ],
    'abilities': [
        ('專業能力', '20%'), ('獨立思考', '20%'), ('自主發展', '20%'),
        ('公民素養', '20%'), ('社會實踐', '20%'), ('勤奮務實', '0'),
        ('溝通及團隊合作', '0'),
    ],
    'objective': (
        '本課程是宗教與文化學系的入門必修，目標是讓學生建立兩項基本能力。'
        '其一是「說得清楚宗教是什麼」：理解宗教作為人類對神聖的一種經驗與探詢，'
        '以及由此形成的一系列組織與活動；掌握宗教學史上幾種經典定義及其爭議，'
        '並理解十九世紀歐洲原本以「拜神」界定宗教，如何在接觸儒教、佛教等傳統之後被迫修正。'
        '其二是「分得出宗教的類型」：課程以〈神學地圖〉的四大信仰型態——泛神論、多神論、'
        '一神論、實用神論——為主軸，輔以語言民族型分類（泛亞伯拉罕諸教、泛印度諸教等），'
        '將全世界信徒人數一千萬以上的宗教全部安置在同一張地圖上，理解各型態之間的'
        '歷史關聯與相互轉化，而非把世界宗教讀成彼此無關的一格一格。'
        '課程最後兩次上課回到現代世界的宗教處境與臺灣宗教現況，'
        '使學生能運用全學期所學的架構，分析自己身處的宗教環境。'
    ),
    'methods_on': ['講述', '媒體融入教學（如影片教學等)', '問題導向學習',
                   '合作學習（如小組討論等)', '即時互動（如互動軟體、社群軟體等)',
                   '對話教學法', '個別指導'],
    'reminder': '無',
    'schedule': [
        ('9月20日', '第一章　什麼是宗教——神聖的經驗與探詢；宗教學者的定義譜系；'
                    '十九世紀歐洲從「宗教＝拜神」的轉向'),
        ('9月20日', '第二章　宗教裡有什麼——神聖者、經驗、神話、教義、儀式、倫理、社群、物質'),
        ('10月4日', '第三章　信仰、體制與範疇——聖書與專職宗教師的門檻；'
                    '普世宗教／民族宗教／少數民族宗教／新興宗教'),
        ('10月4日', '第四章　宗教怎麼分類——語言民族型分類與〈神學地圖〉四大信仰型態；'
                    '信徒千萬以上的宗教全數歸位'),
        ('10月18日', '第五章　泛神論（上）：泛靈論與哲學泛神論'),
        ('10月18日', '第六章　泛神論（下）：自然神論與萬有在神論'),
        ('11月1日', '第七章　多神論（上）：神話多神論——王權、祭司與諸神譜系'),
        ('11月1日', '第八章　多神論（下）：哲學多神論——梵、道、太一、邏各斯'),
        ('11月15日', '第九章　一神論（上）：統攝一神論與本體一神論'),
        ('11月15日', '第十章　一神論（下）：二元神論與融合一神論'),
        ('11月29日', '第十一章　實用神論（上）：功能神論與非神中心論'),
        ('11月29日', '第十二章　實用神論（下）：不可知論與無神論'),
        ('12月13日', '第十三章　現代世界的宗教（上）：世俗化論爭、政教關係、宗教市場'),
        ('12月13日', '第十四章　現代世界的宗教（下）：靈性個人化、基要主義、'
                     '宗教與暴力、跨宗教對話'),
        ('12月27日', '第十五章　臺灣宗教（上）：歷史層積——南島祭儀、漢人移民信仰、'
                     '荷西與清領、日治、戰後'),
        ('12月27日', '第十六章　臺灣宗教（下）：當代圖像——四種型態在同一座島上。期末考'),
        ('1月10日', '自由學習：個別與老師討論自評'),
        ('1月10日', '自由學習：個別與老師討論自評'),
    ],
    'assessment': [
        ('出席', '25%', True), ('課堂參與', '25%', True),
        ('口頭報告(含小組或個人)', '25%', True), ('期末考-筆試', '25%', True),
    ],
    'foreign_text': '有',
    'textbooks': [
        '休斯頓‧史密士（Huston Smith）著，劉安雲譯。《人的宗教：人類偉大的智慧傳統》。臺北：立緒文化，1998。',
        '涂爾幹（Émile Durkheim）著，芮傳明、趙學元譯。《宗教生活的基本形式》。臺北：桂冠圖書，1992。',
        '伊利亞德（Mircea Eliade）著，楊素娥譯。《聖與俗：宗教的本質》。臺北：桂冠圖書，2001。',
        '詹姆斯（William James）著，蔡怡佳、劉宏信譯。《宗教經驗之種種》。臺北：立緒文化，2001。',
        '奧托（Rudolf Otto）著，成窮、周邦憲譯。《論「神聖」》。成都：四川人民出版社，1995。',
        '韋伯（Max Weber）著，康樂、簡惠美譯。《宗教社會學》。臺北：遠流出版，1993。',
        '瞿海源。《台灣宗教變遷的社會政治分析》。臺北：桂冠圖書，1997。',
        '張辰瑋。《世界宗教文化導論》（授課講義，十六章）。線上版：redpiigpig.com/works',
    ],
    'online': '本課程線上講義全書：redpiigpig.com/works（「講義寫作」分區）。'
              '互動式世界宗教界域地圖：redpiigpig.com/maps/world-religions。',
}

COURSES = {'world-religions-intro': WORLD_RELIGIONS}


# ── Word 工具 ───────────────────────────────────────────────────────────────
def run_ea(par, text, font=MING, size=10.5, bold=False, color=None):
    r = par.add_run(text)
    r.font.name = 'Times New Roman'
    r._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), font)
    r.font.size = Pt(size)
    r.font.bold = bold
    if color:
        r.font.color.rgb = color
    return r


def shade(cell, hexcolor):
    el = OxmlElement('w:shd')
    el.set(qn('w:val'), 'clear')
    el.set(qn('w:fill'), hexcolor)
    cell._tc.get_or_add_tcPr().append(el)


def set_cell(cell, text, bold=False, fill=None, size=10.5, align=None):
    cell.text = ''
    par = cell.paragraphs[0]
    par.paragraph_format.space_before = Pt(2)
    par.paragraph_format.space_after = Pt(2)
    if align is not None:
        par.alignment = align
    for i, line in enumerate(str(text).split('\n')):
        if i:
            par = cell.add_paragraph()
            par.paragraph_format.space_before = Pt(0)
            par.paragraph_format.space_after = Pt(2)
        run_ea(par, line, HEI if bold else MING, size, bold)
    if fill:
        shade(cell, fill)


def section_title(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    run_ea(p, text, HEI, 12, bold=True, color=RGBColor(0x1F, 0x39, 0x64))


def new_table(doc, rows, cols, widths=None):
    t = doc.add_table(rows=rows, cols=cols)
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    if widths:
        for row in t.rows:
            for cell, w in zip(row.cells, widths):
                cell.width = Cm(w)
    return t


def page_numbers(doc):
    par = doc.sections[0].footer.paragraphs[0]
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fld = OxmlElement('w:fldSimple')
    fld.set(qn('w:instr'), 'PAGE')
    par._p.append(fld)


# ── 產生 ────────────────────────────────────────────────────────────────────
def build(c):
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = sec.bottom_margin = Cm(1.8)
    sec.left_margin = sec.right_margin = Cm(2.0)
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.element.rPr.rFonts.set(qn('w:eastAsia'), MING)
    style.font.size = Pt(10.5)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_ea(title, '玄奘大學　課程教學大綱', HEI, 16, bold=True)
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_ea(sub, f"{c['basic'][0][1]} 學年度第 {c['basic'][0][3]} 學期", HEI, 11,
           color=RGBColor(0x55, 0x55, 0x55))

    # 課程基本資料
    section_title(doc, '課程基本資料')
    t = new_table(doc, len(c['basic']), 4, [3.2, 5.8, 3.2, 4.8])
    for i, (k1, v1, k2, v2) in enumerate(c['basic']):
        set_cell(t.rows[i].cells[0], k1, bold=True, fill='EEF2F7')
        set_cell(t.rows[i].cells[1], v1)
        set_cell(t.rows[i].cells[2], k2, bold=True, fill='EEF2F7')
        set_cell(t.rows[i].cells[3], v2)

    # 核心能力
    section_title(doc, '核心能力')
    ab = c['abilities']
    t = new_table(doc, (len(ab) + 1) // 2, 4, [4.5, 2.0, 4.5, 2.0])
    for i in range(0, len(ab), 2):
        row = t.rows[i // 2]
        set_cell(row.cells[0], ab[i][0], bold=True, fill='EEF2F7')
        set_cell(row.cells[1], ab[i][1], align=WD_ALIGN_PARAGRAPH.CENTER)
        if i + 1 < len(ab):
            set_cell(row.cells[2], ab[i + 1][0], bold=True, fill='EEF2F7')
            set_cell(row.cells[3], ab[i + 1][1], align=WD_ALIGN_PARAGRAPH.CENTER)
        else:
            set_cell(row.cells[2], '')
            set_cell(row.cells[3], '')

    # 課程目標
    section_title(doc, '課程目標')
    t = new_table(doc, 1, 1, [17.0])
    set_cell(t.rows[0].cells[0], c['objective'])
    t.rows[0].cells[0].paragraphs[0].paragraph_format.first_line_indent = Pt(21)

    # 教學方法
    section_title(doc, '教學方法')
    on = set(c['methods_on'])
    all_methods = [
        '講述', '媒體融入教學（如影片教學等)', '實作教學（如作品創作、實際操作等)',
        '專家演講（如經驗分享、講座等)', '問題導向學習', '合作學習（如小組討論等)',
        '產業/機構實習', '產業/機構見習', '即時互動（如互動軟體、社群軟體等)',
        '專題實作', '個別指導', '督導/反思引導', '服務學習', '體驗教學',
        '實地考察/參訪', '角色扮演實境教學', '示範教學/觀摩學習', '個案/案例研討',
        '對話教學法', '自主學習', '移地教學', '樣本觀察', '競賽遊戲', '競賽讀書會',
        '電子教學', '人工智慧（AI）工具', '其他',
    ]
    rows = (len(all_methods) + 2) // 3
    t = new_table(doc, rows, 3, [5.7, 5.7, 5.7])
    for i, m in enumerate(all_methods):
        mark = '☒' if m in on else '☐'
        set_cell(t.rows[i // 3].cells[i % 3], f'{mark}  {m}', size=9.5)

    # 修課提醒
    section_title(doc, '修課提醒')
    t = new_table(doc, 1, 2, [8.5, 8.5])
    set_cell(t.rows[0].cells[0], '☒  無' if c['reminder'] == '無' else '☐  無')
    set_cell(t.rows[0].cells[1], '☐  有' if c['reminder'] == '無' else f"☒  有：{c['reminder']}")

    # 授課進度與內容
    section_title(doc, '授課進度與內容')
    sch = c['schedule']
    t = new_table(doc, len(sch) + 1, 3, [2.6, 10.4, 4.0])
    hdr = t.rows[0]
    for j, h in enumerate(['周次', '單元／授課重點', '作業內容']):
        set_cell(hdr.cells[j], h, bold=True, fill='DDE6F0',
                 align=WD_ALIGN_PARAGRAPH.CENTER)
    for i, (date, topic) in enumerate(sch):
        row = t.rows[i + 1]
        set_cell(row.cells[0], f'{i + 1:02d}\n{date}', size=9.5,
                 align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell(row.cells[1], topic, size=9.5)
        set_cell(row.cells[2], '☒  無　☐  有課前閱讀', size=9)

    # 學習評量方式
    section_title(doc, '學習評量方式')
    t = new_table(doc, len(c['assessment']) + 1, 2, [12.0, 5.0])
    set_cell(t.rows[0].cells[0], '方式', bold=True, fill='DDE6F0')
    set_cell(t.rows[0].cells[1], '百分比', bold=True, fill='DDE6F0',
             align=WD_ALIGN_PARAGRAPH.CENTER)
    for i, (name, pct, on_) in enumerate(c['assessment']):
        set_cell(t.rows[i + 1].cells[0], f"{'☒' if on_ else '☐'}  {name}")
        set_cell(t.rows[i + 1].cells[1], pct, align=WD_ALIGN_PARAGRAPH.CENTER)

    # 學習參考資源
    section_title(doc, '學習參考資源')
    t = new_table(doc, 3, 2, [4.0, 13.0])
    set_cell(t.rows[0].cells[0], '使用原文教材', bold=True, fill='EEF2F7')
    set_cell(t.rows[0].cells[1], c['foreign_text'])
    set_cell(t.rows[1].cells[0], '教科書／參考書目', bold=True, fill='EEF2F7')
    set_cell(t.rows[1].cells[1], '\n'.join(c['textbooks']), size=9.5)
    set_cell(t.rows[2].cells[0], '課程教材（參考網址）', bold=True, fill='EEF2F7')
    set_cell(t.rows[2].cells[1], c['online'], size=9.5)

    page_numbers(doc)

    outdir = DRIVE / c['folder']
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / f"{c['filename']}.docx"
    doc.save(out)
    return out


if __name__ == '__main__':
    keys = sys.argv[1:] or list(COURSES)
    for k in keys:
        print('✔', build(COURSES[k]))
