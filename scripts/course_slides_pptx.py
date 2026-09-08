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
import json
import re
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Cm, Pt

DRIVE = Path(r'G:\我的雲端硬碟\資料\知識圖工作室\教學')
# 一門課一個資料夾；`--course=sl` 切到宗教系國文講義。
COURSES = {
    'wr': '115-1_世界宗教文化導論',
    'sl': '115-1_宗教系國文講義',
    'ch': '115-1_基督宗教概論',
}
FOLDER = COURSES['wr']
IMGDIR = DRIVE / FOLDER / '簡報' / '圖片'

# 參考書目直接讀講義章節，不另抄一份——書目改了簡報就跟著改。
WORKS = Path(__file__).resolve().parent.parent / 'public' / 'content' / 'works'
CHAPTER_DIRS = {
    'wr': WORKS / 'world-religions-intro' / 'chapters-wr2',
    'sl': WORKS / 'sinographic-literature' / 'chapters',
    'ch': WORKS / 'christianity-intro' / 'chapters',
}
CHAPTERS = CHAPTER_DIRS['wr']


def chapter_refs(nums):
    """讀第 nums 章講義的〈參考資料〉，依序合併並去重。

    一次上課涵蓋兩章，兩章的書目常有重疊；重複列出會讓這一頁變成雜訊。
    """
    out, seen = [], set()
    for n in nums:
        f = CHAPTERS / f'ch{n:02d}.html'
        if not f.exists():
            continue
        html = f.read_text(encoding='utf-8')
        m = re.search(r'<h3>參考資料</h3>\s*<ul>(.*?)</ul>', html, re.S)
        if not m:
            continue
        for li in re.findall(r'<li>(.*?)</li>', m.group(1), re.S):
            t = re.sub(r'<[^>]+>', '', li).strip()
            if t and t not in seen:
                seen.add(t)
                out.append(t)
    return out

def load_manifest():
    f = IMGDIR / '_manifest.json'
    return json.loads(f.read_text(encoding='utf-8')) if f.exists() else {}


MANIFEST = load_manifest()
USED = []          # 本份簡報實際用到的圖，供「圖片出處」頁使用

HEI = '微軟正黑體'
KAI = '標楷體'
# 配色照使用者自己那套 114-2 簡報：封面整片深色＋米白字，內容頁米白底、
# 深色標題、近黑內文，標題下一條細線。四門課各一色，抽錯簡報一眼看得出來。
PALETTES = {
    'green':  dict(deep='457D58', dark='1F5014', light='CBDDD1', cream='F6F6E9'),
    'blue':   dict(deep='3F6D8E', dark='173D55', light='C9DCE7', cream='F4F7FA'),
    'rust':   dict(deep='A0563F', dark='5A2A1C', light='EBD6CD', cream='FBF6F2'),
    'indigo': dict(deep='6B5B8E', dark='352A4E', light='DAD3E8', cream='F8F6FC'),
}

INK = RGBColor(0x27, 0x27, 0x27)
GRAY = RGBColor(0x5E, 0x5E, 0x5E)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK = GOLD = NAVY = PALE = CREAM = MINT = None


def use_palette(name):
    """切換配色。NAVY＝標題深色、GOLD＝主色（封面底與線條）、PALE／CREAM＝米白、
    MINT＝淺色底。沿用舊名字是為了不用改動每一支繪圖函式。"""
    global NAVY, GOLD, PALE, CREAM, MINT
    p = PALETTES[name]
    NAVY = RGBColor.from_string(p['dark'])
    GOLD = RGBColor.from_string(p['deep'])
    PALE = CREAM = RGBColor.from_string(p['cream'])
    MINT = RGBColor.from_string(p['light'])


use_palette('green')

W, H = Cm(33.87), Cm(19.05)   # 16:9

# 字級一律偏大：使用者自己那套 114-2 簡報在 20 吋畫布上標題 75pt、內文 40pt，
# 換算到這裡的 13.33 吋畫布約是標題 50pt、內文 27pt。投影距離遠，寧可少放幾條。
# 🚨 s_bullets 與 split_long 必須吃同一組數字，否則「該拆的沒拆」會靜靜擠成小字。
TEACHER = '張辰瑋'
PROFILE = [
    '國立臺灣大學歷史學系',
    '國立臺北教育大學臺灣文化研究所',
    '玄奘大學宗教與文化學系博士生',
]

BULLET_SZ = {0: 31.0, 1: 25.5, 2: 22.0, 3: 32.0}
BULLET_SP = {0: 14, 1: 9, 2: 6, 3: 15}
IMG_SZ = {0: 27.0, 1: 23.0, 2: 19.5, 3: 28.0}
IMG_SP = {0: 13, 1: 9, 2: 6, 3: 14}

# 內文框的寬高（cm）。🚨 s_bullets／s_imgbullets／split_long 必須吃同一組——
# 只改其中一處，fit() 會用錯的高度估行數，該拆的沒拆，字就壓到頁尾那一行。
# 高度從 13.1 降到 12.7：框底原本只離頁尾 0.35 cm，fit() 一低估就疊上去
# （2026-09-09 稽核在三份壓縮過的簡報上抓到 16 處壓字）。
BOX_W, BOX_H = 30.9, 12.7
# fit() 的估算偏樂觀，實測會讓最後一兩個字掉到頁尾線下，所以再留一成餘裕。
FIT_MARGIN = 0.84
IMG_BOX_W = 17.0


# ── 版面工具 ────────────────────────────────────────────────────────────────
def textbox(slide, x, y, w, h, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    return tf


# 「」內六字以上視為引語（學者的話、經文），排標楷體；
# 六字以下多半是專名或術語標記（「基督教」「已然—未然」），維持原字體。
QUOTE_RE = re.compile(r'[「『][^「」『』]{6,}[」』]')


def _spans(text):
    out, at = [], 0
    for m in QUOTE_RE.finditer(text):
        if m.start() > at:
            out.append((text[at:m.start()], False))
        out.append((m.group(), True))
        at = m.end()
    if at < len(text):
        out.append((text[at:], False))
    return out or [(text, False)]


def put(tf, text, size, font=HEI, bold=False, color=INK, space_after=6,
        align=PP_ALIGN.LEFT, first=False, line=1.25, indent=0):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_after = Pt(space_after)
    p.line_spacing = line
    if indent:
        p.level = min(indent, 4)
    for chunk, is_quote in _spans(text):
        r = p.add_run()
        r.text = chunk
        r.font.size = Pt(size)
        r.font.name = KAI if (is_quote and font != KAI) else font
        r.font.bold = bold
        r.font.color.rgb = color
    return p


CM_PT = 28.35


# 一份簡報要出幾張，由這兩個數字決定，course_slides_weekly 會逐份調降來壓張數：
# FIT_FLOOR＝字最多縮到幾成；SPLIT_AT＝縮過頭就改拆成兩頁的門檻。
# 兩個一起往下調＝密的頁改「縮一點字」而不是「拆一頁」，張數就下來了。
FIT_FLOOR = 0.72
SPLIT_AT = 0.78


def fit(items, width_cm, height_cm, sizes, spaces, line=1.3, indent_cm=(0, 0.9, 1.6),
        raw=False):
    """估算這批條目實際佔幾行，回傳縮放係數（最小 FIT_FLOOR）。

    中日文一個字約等於一個字級的寬度，因此每行字數 ≈ 可用寬度 ÷ 字級。
    只縮小、不放大——版面預設就是給內容少的頁看的。
    """
    # PowerPoint 的中文行高不是「字級×行距」，而是再乘上字型的行距係數
    # （實測約 1.22）。低估的話文字會被切掉或壓到頁尾，所以這裡取 1.62。
    LINE = 1.75 / 1.3 * line
    total = 0.0
    for it in items:
        lvl, txt = (it if isinstance(it, tuple) else (0, it))
        if not txt:
            total += sizes[0] * 0.5
            continue
        avail = (width_cm - indent_cm[min(lvl, 2) if lvl != 3 else 0]) * CM_PT
        per = max(8, int(avail / sizes[lvl]))
        rows = -(-(len(txt) + 2) // per)          # ＋2 是行首的項目符號
        total += rows * sizes[lvl] * LINE + spaces[lvl]
    if not total:
        return 1.0
    v = height_cm * CM_PT / total
    # 🚨 raw=False 的下限是「夾住」不是「保證裝得下」：內容超量時它照樣回下限，
    #    字縮到下限仍然溢出。要判斷該不該拆頁，必須看沒被夾過的 raw 值。
    return min(1.0, v if raw else max(FIT_FLOOR, v))


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


# ── 標題區 ──────────────────────────────────────────────────────────────────
# 🚨 標題下那條線原本畫死在 3.80 cm，可是標題框只要長到兩行、或掛了副標，
#    字就長到線下面去——線正好橫過副標中間。2026-09-09 稽核三十七份，
#    **每一張有副標的頁都中**（線 y=108pt、副標 y=87–112pt）。
#    所以線與內文頂改成算出來的：先量標題實際佔幾行，再往下擺。
TITLE_TOP = 0.85          # 標題框頂（cm）
TITLE_SZ, SUB_SZ = 40, 21
TITLE_MIN = 32            # 標題縮到這裡為止；還是兩行就讓它兩行，線再往下讓
# PowerPoint 的中文行高＝字級 × 段落行距 × 字型係數（實測 1.2）。
# 拿 40pt 單行標題回推：24.1 + 40×1.25×1.2 = 84 pt，與 PDF 量到的一致。
LINE_MUL = 1.25 * 1.2
RULE_GAP = 6              # 標題底到線（pt）
BODY_GAP = 0.65           # 線到內文頂（cm）
BODY_TOP = 4.45           # 舊版寫死的內文頂；各繪圖函式以它為基準加 dy
BODY_BOTTOM = 17.15       # 內文框底（頁尾那一行從 17.90 起）
TWO_BOTTOM = 17.70        # 雙欄頁的欄框底：欄內字級小，可以再貼近頁尾一點


def _lines(text, size, width_cm=33.87 - 3.0):
    """這行字在 width_cm 寬、size 級時要佔幾行（中日文一字約一個字級寬）。"""
    per = max(4, int(width_cm * CM_PT / size))
    return max(1, -(-len(str(text)) // per))


def title_block(title, sub=None):
    """回傳 (標題字級, 線的 y, 內文頂的 y)，單位 cm。純函式，好驗算。

    標題盡量壓成一行——多一行就把線與內文一起往下推 2 cm，那是整整兩條內容。
    """
    tsz = next((s for s in range(TITLE_SZ, TITLE_MIN - 1, -1)
                if _lines(title, s) == 1), TITLE_MIN)
    h = _lines(title, tsz) * tsz * LINE_MUL
    if sub:
        h += 2 + _lines(sub, SUB_SZ) * SUB_SZ * LINE_MUL
    rule = TITLE_TOP + (h + RULE_GAP) / CM_PT
    return tsz, rule, rule + BODY_GAP


def slide_sub(item):
    """取出這一張的副標——可能在結尾的 kwargs，也可能是位置參數。"""
    args = list(item[1:])
    if args and isinstance(args[-1], dict):
        return args.pop().get('sub')
    i = 2 if item[0] == 'bullets' else 3        # args 內的 sub 位置
    return args[i] if len(args) > i and isinstance(args[i], str) else None


def body_h(item):
    """這一張的內文框有多高（cm）。s_bullets／s_imgbullets／split_long 共用。"""
    return BODY_BOTTOM - title_block(item[1], slide_sub(item))[2]


def slide_title(slide, title, sub=None):
    """畫標題與其下的細線，回傳內文該從哪裡開始（cm）。"""
    band(slide, PALE, Cm(0), Cm(0), W, H)
    tsz, rule, top = title_block(title, sub)
    tf = textbox(slide, Cm(1.5), Cm(TITLE_TOP), W - Cm(3.0), Cm(rule - TITLE_TOP))
    put(tf, title, tsz, bold=True, color=NAVY, first=True, space_after=2)
    if sub:
        put(tf, sub, SUB_SZ, color=GRAY, space_after=0)
    band(slide, GOLD, Cm(1.5), Cm(rule), W - Cm(9.0), Cm(0.06))
    return top


def footer(slide, n, label):
    tf = textbox(slide, Cm(1.5), H - Cm(1.15), W - Cm(3.0), Cm(0.8))
    put(tf, f'{label}　　{n}', 13, color=GRAY, first=True, space_after=0)


# ── 各種投影片 ──────────────────────────────────────────────────────────────
def s_cover(prs, d):
    s = blank(prs)
    band(s, GOLD, Cm(0), Cm(0), W, H)
    tf = textbox(s, Cm(3.0), Cm(4.2), W - Cm(6.0), Cm(1.0))
    put(tf, d['kicker'], 19, color=MINT, first=True, space_after=0)
    tf = textbox(s, Cm(3.0), Cm(5.5), W - Cm(6.0), Cm(2.4))
    put(tf, d['title'], 54, font=KAI, bold=True, color=CREAM, first=True, space_after=0)
    band(s, CREAM, Cm(3.0), Cm(8.5), Cm(4.6), Cm(0.06))
    tf2 = textbox(s, Cm(3.0), Cm(9.5), W - Cm(6.0), Cm(6.0))
    put(tf2, d['subtitle'], 26, font=KAI, color=CREAM, first=True, space_after=24)
    for line in d['meta']:
        put(tf2, line, 18, color=MINT, space_after=6)
    return s


def s_profile(prs):
    """自我介紹頁——每學期第一次上課固定放這一頁（使用者 2026-09-07 要求）。

    版面照他自己那套 114-2 簡報：左側一道深色帶、姓名獨大、學經歷條列。
    """
    s = blank(prs)
    band(s, MINT, Cm(0), Cm(0), W, H)
    band(s, GOLD, Cm(0), Cm(0), Cm(0.5), H)
    tf = textbox(s, Cm(3.0), Cm(4.4), W - Cm(6.0), Cm(10.5))
    put(tf, '授課教師', 23, bold=True, color=GOLD, first=True, space_after=12)
    put(tf, TEACHER, 58, font=KAI, bold=True, color=NAVY, space_after=26)
    for line in PROFILE:
        put(tf, '▍ ' + line, 27, color=INK, space_after=13, line=1.3)
    return s


def s_section(prs, no, title, lines):
    s = blank(prs)
    band(s, PALE, Cm(0), Cm(0), W, H)
    band(s, NAVY, Cm(0), Cm(0), Cm(0.5), H)
    tf = textbox(s, Cm(3.0), Cm(4.8), W - Cm(6.0), Cm(9.5))
    put(tf, no, 23, bold=True, color=GOLD, first=True, space_after=12)
    put(tf, title, 52, font=KAI, bold=True, color=NAVY, space_after=20)
    for ln in lines:
        put(tf, ln, 23, color=GRAY, space_after=8)
    return s


def s_big(prs, text, sub=None):
    s = blank(prs)
    band(s, GOLD, Cm(0), Cm(0), W, H)
    tf = textbox(s, Cm(3.2), Cm(2.6), W - Cm(6.4), H - Cm(5.2), anchor=MSO_ANCHOR.MIDDLE)
    put(tf, text, 46, font=KAI, bold=True, color=CREAM, first=True,
        align=PP_ALIGN.CENTER, line=1.45, space_after=18)
    if sub:
        put(tf, sub, 23, color=MINT, align=PP_ALIGN.CENTER)
    return s


def s_bullets(prs, title, bullets, sub=None):
    s = blank(prs)
    top = slide_title(s, title, sub)
    w, h = BOX_W, BODY_BOTTOM - top
    tf = textbox(s, Cm(1.5), Cm(top), Cm(w), Cm(h))
    base, sp = BULLET_SZ, BULLET_SP
    k = fit(bullets, w, h * FIT_MARGIN, base, sp)
    # 內容明顯偏少（六成高度就裝得下）就垂直置中，不要下半頁整片空白
    if k >= 1.0 and fit(bullets, w, h * 0.80, base, sp) >= 1.0:
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    firstdone = False
    for b in bullets:
        lvl, txt = (b if isinstance(b, tuple) else (0, b))
        if txt == '':
            put(tf, ' ', 9 * k, first=not firstdone, space_after=0)
            firstdone = True
            continue
        color = {0: INK, 1: RGBColor(0x3A, 0x3A, 0x3A), 2: GRAY, 3: INK}[lvl]
        mark = {0: '▍', 1: '‧', 2: '－', 3: ''}[lvl]
        put(tf, (f'{mark} ' if mark else '') + txt, base[lvl] * k, color=color,
            bold=(lvl == 0), first=not firstdone, space_after=sp[lvl] * k,
            indent=min(lvl, 2) if lvl != 3 else 0, line=1.3)
        firstdone = True
    return s


def s_two(prs, title, left, right, sub=None):
    s = blank(prs)
    top = slide_title(s, title, sub)
    colw = (W - Cm(3.8)) / 2
    for i, (head, items) in enumerate((left, right)):
        x = Cm(1.5) + i * (colw + Cm(0.8))
        band(s, NAVY if i == 0 else GOLD, x, Cm(top), colw, Cm(1.0))
        tfh = textbox(s, x + Cm(0.35), Cm(top + 0.18), colw - Cm(0.7), Cm(0.8))
        put(tfh, head, 23, bold=True, color=CREAM, first=True, space_after=0)
        cw = colw / 360000 / 10 - 0.7
        base = {0: 24.0, 1: 20.0, 2: 20.0}
        # 雙欄頁不能拆頁，只能縮字；框底離頁尾只有 0.2 cm，餘裕要吃滿
        k = max(0.62, fit(items, cw, (TWO_BOTTOM - (top + 1.3)) * FIT_MARGIN,
                          base, {0: 10, 1: 8, 2: 8}))
        tf = textbox(s, x + Cm(0.35), Cm(top + 1.3), colw - Cm(0.7),
                     Cm(TWO_BOTTOM - (top + 1.3)))
        for j, it in enumerate(items):
            lvl, txt = (it if isinstance(it, tuple) else (0, it))
            put(tf, ('‧ ' if lvl == 0 else '　－ ') + txt,
                base[min(lvl, 1)] * k,
                color=INK if lvl == 0 else GRAY,
                first=(j == 0), space_after=10 * k, line=1.3)
    return s


def s_table(prs, title, headers, rows, sub=None, note=None, widths=None):
    s = blank(prs)
    top_cm = slide_title(s, title, sub)
    top = Cm(top_cm)
    tbl = s.shapes.add_table(len(rows) + 1, len(headers),
                             Cm(1.5), top, W - Cm(3.0), Cm(1.0)).table
    # 列高給最小值，讓 PowerPoint 依內容自動撐開（不要平均攤滿整頁）
    for i, r in enumerate(tbl.rows):
        r.height = Cm(1.05) if i == 0 else Cm(0.85)
    if widths:
        total = sum(widths)
        for i, w in enumerate(widths):
            tbl.columns[i].width = int((W - Cm(3.0)) * w / total)
    for ci, h in enumerate(headers):
        c = tbl.cell(0, ci)
        c.text = ''
        c.fill.solid(); c.fill.fore_color.rgb = NAVY
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf = c.text_frame; tf.word_wrap = True
        put(tf, h, 19, bold=True, color=CREAM, first=True, space_after=0,
            align=PP_ALIGN.CENTER)
    # 🚨 表格沒有「裝不下就縮」這回事，PowerPoint 會讓它一路往下長，
    #    長過頁尾也沒有人攔。所以這裡自己估高度，塞不下就降字級。
    #    可用高度＝從表格頂 4.5 cm 到頁尾線 17.85 cm，扣掉表頭列。
    cols_cm = ([(33.87 - 3.0) * w / sum(widths) for w in widths] if widths
               else [(33.87 - 3.0) / len(headers)] * len(headers))

    def table_h(size):
        total = 1.05 * CM_PT                      # 表頭列
        for row in rows:
            lines = 1
            for ci, val in enumerate(row):
                per = max(4, int(cols_cm[ci] * CM_PT / size))
                lines = max(lines, -(-len(str(val)) // per))
            total += max(0.85 * CM_PT, lines * size * 1.5 + 6)
        return total

    # 附註跟表格搶同一段空間：先算附註要幾行、佔多高，剩下的才是表格的。
    note_size, note_h = 15, 0.0
    if note:
        while note_size > 10:
            per = max(8, int((33.87 - 3.0) * CM_PT / note_size))
            nl = -(-len(note) // per)
            note_h = (nl * note_size * 1.45 + 4) / CM_PT
            if note_h <= 1.6:
                break
            note_size -= 1
    note_top = 17.5 - note_h
    limit = (note_top - (0.3 if note else 0.0) - top_cm) * CM_PT

    tsize = 19 if len(rows) <= 5 else (17 if len(rows) <= 7 else 15)
    while tsize > 10 and table_h(tsize) > limit:
        tsize -= 1
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            c = tbl.cell(ri + 1, ci)
            c.text = ''
            c.fill.solid()
            c.fill.fore_color.rgb = WHITE if ri % 2 == 0 else PALE
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.margin_top = c.margin_bottom = Cm(0.12)
            tf = c.text_frame; tf.word_wrap = True
            put(tf, str(val), tsize, color=INK, first=True, space_after=0,
                line=1.15)
    if note:
        tf = textbox(s, Cm(1.5), Cm(note_top), W - Cm(3.0), Cm(max(1.3, note_h)))
        put(tf, note, note_size, color=GRAY, first=True, space_after=0)
    return s


def place_image(slide, key, x, y, w, h):
    """把圖等比塞進 (x,y,w,h) 的框裡並置中；圖不存在就回傳 False。"""
    m = MANIFEST.get(key)
    if not m:
        return False
    f = IMGDIR / m['file']
    if not f.exists():
        return False
    pic = slide.shapes.add_picture(str(f), x, y, width=w)
    if pic.height > h:                      # 太高就改用高度縮，維持比例
        ratio = pic.width / pic.height
        pic.height = h
        pic.width = int(h * ratio)
    pic.left = x + int((w - pic.width) / 2)
    pic.top = y + int((h - pic.height) / 2)
    if key not in USED:
        USED.append(key)
    return True


# 🚨 圖說與圖庫標籤的位置是寫死的，跟字多字少無關。頁尾那一行從 17.90 cm
#    起，所以這兩個元件的「底部」都必須壓在 17.85 cm 以內。
CAP_H = 1.0            # 圖說框高（cm）
# 🚨 圖說一往上挪，就會挪進圖片區。這兩個數字必須一起改：
#    有圖說時圖框底 16.10 cm，沒有時 17.50 cm（頁尾線 17.90）。
def img_box_h(has_cap, top=BODY_TOP):
    return Cm((16.10 if has_cap else 17.50) - top)


def caption(slide, text, x, y, w):
    tf = textbox(slide, x, y, w, Cm(CAP_H))
    put(tf, text, 16, color=GRAY, first=True, space_after=0, align=PP_ALIGN.CENTER)


def s_photo(prs, title, key, cap=None, sub=None):
    s = blank(prs)
    top = slide_title(s, title, sub)
    box_y, box_h = Cm(top), img_box_h(bool(cap), top)
    if not place_image(s, key, Cm(1.5), box_y, W - Cm(3.0), box_h):
        put(textbox(s, Cm(1.5), box_y, W - Cm(3.0), Cm(2)), f'（缺圖：{key}）',
            16, color=GRAY, first=True)
    if cap:
        caption(s, cap, Cm(1.5), H - Cm(2.75), W - Cm(3.0))
    return s


def s_gallery(prs, title, items, sub=None):
    """items: [(圖 key, 說明), ...]，二至四張並排。"""
    s = blank(prs)
    top_cm = slide_title(s, title, sub)
    n = len(items)
    gap = Cm(0.6)
    colw = int((W - Cm(3.0) - gap * (n - 1)) / n)
    # 圖框底要留給下面 2.75 cm 的標籤：標籤頂 = 圖框底 + 0.25
    top, boxh = Cm(top_cm), Cm(BODY_BOTTOM - 2.75 - 0.25 - top_cm)
    for i, (key, label) in enumerate(items):
        x = Cm(1.5) + i * (colw + gap)
        if not place_image(s, key, x, top, colw, boxh):
            put(textbox(s, x, top, colw, Cm(2)), f'（缺圖：{key}）', 13,
                color=GRAY, first=True)
        # 標籤框 2.75 cm（約三行半）。下限自己定 0.76（≒13pt），不吃 FIT_FLOOR——
        # 那個值會被壓張數的階梯調到 0.52，標籤跟著縮就變成投影看不清的 8.9pt。
        kl = max(0.76, fit([label], colw / 360000 / 10, 2.75, {0: 17.0}, {0: 0}))
        tf = textbox(s, x, top + boxh + Cm(0.25), colw, Cm(2.75))
        put(tf, label, 17 * kl, color=INK, first=True, space_after=0,
            align=PP_ALIGN.CENTER, line=1.25)
    return s


def s_imgbullets(prs, title, bullets, key, sub=None, cap=None):
    """左文右圖。"""
    s = blank(prs)
    top = slide_title(s, title, sub)
    tw = 17.0
    textw = Cm(tw)
    imgx = Cm(1.5) + textw + Cm(0.7)
    imgw = W - Cm(1.5) - imgx
    h = BODY_BOTTOM - top
    tf = textbox(s, Cm(1.5), Cm(top), textw, Cm(h))
    base, sp = IMG_SZ, IMG_SP
    k = fit(bullets, tw, h * FIT_MARGIN, base, sp)
    firstdone = False
    for b in bullets:
        lvl, txt = (b if isinstance(b, tuple) else (0, b))
        if txt == '':
            put(tf, ' ', 9 * k, first=not firstdone, space_after=0)
            firstdone = True
            continue
        color = {0: INK, 1: RGBColor(0x3A, 0x3A, 0x3A), 2: GRAY, 3: INK}[lvl]
        mark = {0: '▍', 1: '‧', 2: '－', 3: ''}[lvl]
        put(tf, (f'{mark} ' if mark else '') + txt, base[lvl] * k, color=color,
            bold=(lvl == 0), first=not firstdone, space_after=sp[lvl] * k,
            indent=min(lvl, 2) if lvl != 3 else 0, line=1.3)
        firstdone = True
    boxh = img_box_h(bool(cap), top)
    place_image(s, key, imgx, Cm(top), imgw, boxh)
    if cap:
        caption(s, cap, imgx, H - Cm(2.75), imgw)
    return s


def s_credits(prs, label):
    """圖片出處頁：課堂投影用圖必須標明作者與授權。

    條目多就分頁——擠成一頁小字會看不清，而這一頁是授權聲明，
    看不清等於沒標。
    """
    if not USED:
        return []
    per, out = 8, []
    for start in range(0, len(USED), per):
        s = blank(prs)
        top = slide_title(s, '圖片出處',
                          '本份簡報用圖均取自維基共享資源，授權為公有領域或 CC')
        tf = textbox(s, Cm(1.5), Cm(top), W - Cm(3.0), Cm(BODY_BOTTOM - top))
        for i, k in enumerate(USED[start:start + per]):
            m = MANIFEST.get(k, {})
            name = m.get('title', k)[5:]            # 去掉 'File:'
            line = f'{name}　—　{m.get("license", "")}'
            if m.get('author'):
                line += f'　／　{m["author"][:44]}'
            put(tf, line, 16, color=GRAY, first=(i == 0),
                space_after=6, line=1.25)
        out.append(s)
    return out


def s_openers(prs, course, no):
    """開場互動兩頁：口頭提問五題、手機簡答三題。

    放在封面之後，因為它的作用是在講課之前先把學生既有的認知逼出來——
    講完再問，得到的多半是覆述。第二頁的作答與抽籤走 ClassPoint 或
    AhaSlides；QR code 由該工具在播放時疊上，這裡只留位置與說明。
    """
    try:
        from course_slides_openers import OPENERS
    except ImportError:
        return []
    d = OPENERS.get(course, {}).get(no)
    if not d:
        return []
    out = []

    s1 = blank(prs)
    top = slide_title(s1, '上課前先想一想',
                      '先不查資料、不翻講義；你現在的答案本身就是這堂課的材料')
    tf = textbox(s1, Cm(1.5), Cm(top), W - Cm(3.0), Cm(BODY_BOTTOM - top))
    ka = fit([f'{i + 1}　{q}' for i, q in enumerate(d['ask'])],
             30.9, (BODY_BOTTOM - top) * FIT_MARGIN, {0: 27.0}, {0: 16})
    for i, q in enumerate(d['ask']):
        put(tf, f'{i + 1}　{q}', 27 * ka, color=INK, first=(i == 0),
            space_after=16 * ka, line=1.3)
    out.append(s1)

    s2 = blank(prs)
    top = slide_title(s2, '請用手機作答',
                      '掃描畫面上的 QR code 或輸入 PIN 碼加入，作答後抽籤請人詳細說明')
    tf = textbox(s2, Cm(1.5), Cm(top), W - Cm(19.0), Cm(BODY_BOTTOM - top))
    _q = [f'{i + 1}　{q}' for i, q in enumerate(d['answer'])]
    _q.append('一兩句話就好，答錯不扣分——這裡要的是你原本怎麼想。')
    kb = fit(_q, 14.8, (BODY_BOTTOM - top) * FIT_MARGIN, {0: 26.0}, {0: 14})
    for i, q in enumerate(d['answer']):
        put(tf, f'{i + 1}　{q}', 26 * kb, color=INK, first=(i == 0),
            space_after=14 * kb, line=1.3)
    put(tf, '一兩句話就好，答錯不扣分——這裡要的是你原本怎麼想。', 19 * kb,
        color=GRAY, space_after=0, line=1.3)
    band(s2, MINT, W - Cm(16.6), Cm(top), Cm(15.1), Cm(BODY_BOTTOM - top))
    tf2 = textbox(s2, W - Cm(16.1), Cm(top + 0.8), Cm(14.1),
                  Cm(BODY_BOTTOM - top - 1.6), anchor=MSO_ANCHOR.MIDDLE)
    put(tf2, 'QR code', 38, bold=True, color=NAVY, first=True, space_after=10,
        align=PP_ALIGN.CENTER)
    put(tf2, '（由 ClassPoint／AhaSlides 於播放時疊上）', 19, color=GRAY,
        space_after=0, align=PP_ALIGN.CENTER)
    out.append(s2)
    return out

def s_refs(prs, nums):
    """課末參考書目頁：本次上課兩章講義的〈參考資料〉。

    學生要能從投影片直接抄到書名，所以字級不壓到看不清；
    條目多就分頁，寧可多一頁也不要擠。
    """
    items = chapter_refs(nums)
    if not items:
        return []
    # 🚨 標題與副標都不出現章號——講義編號是備課用的，不給學生看。
    per, out = 7, []
    for start in range(0, len(items), per):
        s = blank(prs)
        top = slide_title(s, '參考書目', '本次上課單元的參考資料；完整註釋見課堂講義')
        tf = textbox(s, Cm(1.5), Cm(top), W - Cm(3.0), Cm(BODY_BOTTOM - top))
        for i, t in enumerate(items[start:start + per]):
            put(tf, t, 16, color=INK, first=(i == 0), space_after=10, line=1.25)
        out.append(s)
    return out

RENDER = {'cover': s_cover, 'section': s_section, 'big': s_big,
          'bullets': s_bullets, 'two': s_two, 'table': s_table,
          'photo': s_photo, 'gallery': s_gallery, 'imgbullets': s_imgbullets}



# ── 併頁：不要「一頁只有一句話」 ────────────────────────────────────────
BULLETY = ('bullets', 'imgbullets')


def _big_lines(b):
    # level 3＝導言／引文行：不掛項目符號，出處自成一行
    lines = [(3, ln) for ln in b[1].split(chr(10)) if ln.strip()]
    if len(b) > 2 and b[2]:
        lines.append((1, b[2]))
    return lines


def _swap_bullets(it, newb):
    return (it[0], it[1], newb) + tuple(it[3:])


def _to_bullets(b):
    """真的無處可併時，讓它自己成為一張有標題有內容的條列頁。"""
    lines = [ln for ln in b[1].split('\n') if ln.strip()]
    title = lines[0].rstrip('。，、')
    rest = [(0, ln) for ln in lines[1:]]
    if len(b) > 2 and b[2]:
        rest.append((1, b[2]))
    return ('bullets', title, rest or [(1, '')])


def fold_bigs(slides):
    out, pending = [], []
    for it in slides:
        if it[0] == 'big':
            pending.append(it)
            continue
        if pending:
            extra = [x for b in pending for x in _big_lines(b)]
            if it[0] in BULLETY:
                it = _swap_bullets(it, extra + [''] + list(it[2]))
            elif it[0] == 'section':
                lines = list(it[3]) if len(it) > 3 else []
                for b in pending:
                    lines += [ln for ln in b[1].split('\n') if ln.strip()]
                    if len(b) > 2 and b[2]:
                        lines.append(b[2])
                it = (it[0], it[1], it[2], lines)
            elif out and out[-1][0] in BULLETY:
                out[-1] = _swap_bullets(out[-1], list(out[-1][2]) + [''] + extra)
            else:
                out.extend(_to_bullets(b) for b in pending)
            pending = []
        out.append(it)
    for b in pending:
        if out and out[-1][0] in BULLETY:
            out[-1] = _swap_bullets(out[-1], list(out[-1][2]) + [''] + _big_lines(b))
        else:
            out.append(_to_bullets(b))
    return out


def split_long(slides):
    """一頁塞不下就拆頁，**拆到裝得下為止**，不要把字縮到看不清。

    🚨 以前只拆一次。但 fit() 的下限是夾住不是保證，內容超過兩頁份量時，
    拆完的每一半仍然裝不下，字就壓到頁尾那一行——2026-09-09 稽核抓到 16 處。
    改成迴圈：只要 raw 值仍低於門檻就繼續對半拆。
    """
    base, sp, ibase, isp = BULLET_SZ, BULLET_SP, IMG_SZ, IMG_SP

    def need(item):
        # 🚨 內文框有多高，要看標題佔掉幾行——掛副標的頁少了約 0.6 cm。
        #    這裡不用同一個算法的話，「該拆的沒拆」會靜靜擠成小字。
        items, h = list(item[2]), body_h(item)
        if item[0] == 'bullets':
            return fit(items, BOX_W, h * FIT_MARGIN, base, sp, raw=True)
        return fit(items, IMG_BOX_W, h * FIT_MARGIN, ibase, isp, raw=True)

    out = []
    for it in slides:
        if it[0] not in BULLETY:
            out.append(it)
            continue
        queue, guard = [it], 0
        while queue and guard < 16:
            guard += 1
            cur = queue.pop(0)
            items = list(cur[2])
            if need(cur) >= SPLIT_AT or len(items) < 2:
                out.append(cur)
                continue
            # 從中間往後找第一個第一層項目當切點，避免把子項目跟標題拆開
            half = len(items) // 2
            cut = next((i for i in range(half, len(items))
                        if not isinstance(items[i], tuple) or items[i][0] == 0), half)
            if cut <= 0 or cut >= len(items):
                cut = max(1, half)
            # 續頁只掛一次「（續）」，拆三次也不要變成「（續）（續）（續）」
            head = cur[1].split('（續）')[0]
            if cur[0] == 'bullets':
                rest = tuple(cur[3:])
                queue.insert(0, ('bullets', cur[1], items[:cut]) + rest)
                queue.insert(1, ('bullets', head + '（續）', items[cut:]) + rest)
            else:
                # 圖留在第一頁，續頁走純文字（整頁寬，字才放得大）
                queue.insert(0, (cur[0], cur[1], items[:cut]) + tuple(cur[3:]))
                queue.insert(1, ('bullets', head + '（續）', items[cut:]))
        out.extend(queue)
    return out


def _has_image(key):
    m = MANIFEST.get(key)
    return bool(m) and (IMGDIR / m['file']).exists()


def _fits_narrow(item):
    """配了圖之後內文欄只剩 17 cm，這一頁還裝不裝得下。"""
    return fit(list(item[2]), IMG_BOX_W, body_h(item) * FIT_MARGIN,
               IMG_SZ, IMG_SP, raw=True) >= SPLIT_AT


def prepare(slides, course='wr'):
    """配圖 → 併頁 → 拆頁。張數上限的試算與實際渲染必須走同一條，
    否則 course_slides_weekly 數出來的張數跟真的出來的不一樣。"""
    try:
        import course_slide_illustrate as ILL
        slides = ILL.apply(slides, course, _has_image, _fits_narrow)[0]
    except ImportError:
        pass
    return split_long(fold_bigs(slides))


def build(deck, no=None, course='wr', refs=None, profile=False):
    """refs＝課末書目要讀的講義章號（不印在投影片上，只用來取書目）。
    profile＝True 時在封面與開場互動之後插一頁自我介紹（每學期第一次上課）。
    """
    global USED
    USED = []
    prs = Presentation()
    prs.slide_width, prs.slide_height = W, H
    items = prepare(deck['slides'], course)
    numbered = []
    for i, item in enumerate(items):
        kind, args = item[0], list(item[1:])
        kw = args.pop() if args and isinstance(args[-1], dict) and kind != 'cover' else {}
        s = RENDER[kind](prs, *args, **kw)
        if kind not in ('cover', 'section', 'big'):
            numbered.append(s)
        # 開場兩頁緊接封面，屬前置頁，與封面一樣不編號
        if i == 0 and kind == 'cover' and no:
            s_openers(prs, course, no)
            if profile:
                s_profile(prs)
    numbered += s_credits(prs, deck['footer'])
    # 課末書目：預設每次上課兩章（第 n 次＝第 2n-1、2n 章），週次版由 refs 指定
    if refs or no:
        numbered += s_refs(prs, tuple(refs) if refs else (no * 2 - 1, no * 2))
    # 🚨 頁碼＝這一張**在檔案裡真正的位置**（使用者 2026-09-09 在第 1 週那份手改的）。
    #    舊版編的是「內容頁的序號」：封面、開場互動、自我介紹、分節頁都不算，
    #    於是投影片右下角寫 12、PowerPoint 的頁數卻是 17。有人說「第 12 頁」時
    #    對不上，投影中要翻回去更麻煩。所以等全部投影片都生完，再照位置編。
    pos = {sl.slide_id: n for n, sl in enumerate(prs.slides, 1)}
    for sl in numbered:
        footer(sl, pos[sl.slide_id], deck['footer'])
    outdir = DRIVE / FOLDER / '簡報'
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / deck['filename']
    prs.save(out)
    return out, len(prs.slides._sldIdLst)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    args = sys.argv[1:]
    course = next((a.split('=')[1] for a in args if a.startswith('--course=')), 'wr')
    if course != 'wr':
        FOLDER = COURSES[course]
        IMGDIR = DRIVE / FOLDER / '簡報' / '圖片'
        MANIFEST = load_manifest()
        CHAPTERS = CHAPTER_DIRS[course]
    if course in ('sl', 'ch'):
        if course == 'sl':
            from course_slides_data_sl import DECKS_SL as D
        else:
            from course_slides_data_ch import DECKS_CH as D
        DECKS = D
        for n in [a for a in args if not a.startswith('--')] or sorted(DECKS):
            out, cnt = build(DECKS[int(n)], int(n), course)
            print(f'✔ {out}　（{cnt} 張）')
        raise SystemExit
    from course_slides_data import DECKS
    from course_slides_data2 import DECKS2
    from course_slides_data3 import DECKS3
    from course_slides_data4 import DECKS4
    DECKS = {**DECKS, **DECKS2, **DECKS3, **DECKS4}
    for n in ([a for a in args if not a.startswith('--')] or sorted(DECKS)):
        out, cnt = build(DECKS[int(n)], int(n), course)
        print(f'✔ {out}　（{cnt} 張）')
