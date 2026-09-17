#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IAMS《東方摩尼教選輯》PDF → 摩尼教經典三欄 reader 的取源管線。

    python scripts/manichaean_iams.py --list          # 列出四冊涵蓋的篇目
    python scripts/manichaean_iams.py --probe 3 5     # 看第三冊第 5 頁切欄結果
    python scripts/manichaean_iams.py --build sabuhragan

《東方摩尼教選輯》(Anthologia Manichaica Orientalia, Lieu 編，Ancient India and Iran
Trust) 四冊在 manichaeism.de 開放取用，**原文轉寫與英譯逐行並排**——
正是三欄 reader 要的形狀，也是摩尼教文獻裡少數這麼好取的來源。

═══════════════ 🚨 動它之前先讀完這四件事 ═══════════════

一、**雙欄 PDF 不可按 block 切，要按 word 的 x 座標切。**
    PyMuPDF 的 get_text('blocks') 在這批 PDF 上會吐出**跨欄的 block**
    （實測第二冊第 6 頁有一個 x0=82.8 x1=507.5 的英文 block）。
    照 block 的 bbox 判欄，那一段英譯會被歸成「跨欄標題」而整段消失。
    故一律用 get_text('words') 逐詞判邊。
    這與 [[feedback_twocolumn_pdf_reading_order]] 是同一個坑的兩種長相：
    那邊是按 (y,x) 排把右欄插進左欄，這邊是按 block 判欄把整段吃掉。

二、**置中標題會橫跨欄界，不可當成兩欄的內容。**
    「(I) THE LIVING GOSPEL (EVANGELIŌN)」的 bbox 是 181–410，跨過欄界 300。
    逐詞判邊會把它切成「(I) THE LIVING」＋「GOSPEL (EVANGELIŌN)」，
    然後前半混進原文欄、後半混進英譯欄——而版面完全正常。
    故先判「這一行是不是跨欄行」：**看行首的 x 落在哪**。
    正文左欄一律起於 x≈89，正文右欄一律起於 x≈303；
    起點落在兩者之間（如置中標題的 181）的，就是跨欄行。

三、**段號照抄，不自編。**
    本選輯的段號是抄本定位符（`[M17 V/i]`、`[So18151/R/Hd.]`）
    加上編者的行號（`1/`、`4b/`——**有字母尾碼**）。
    兩欄用的是同一組定位符，這是對齊的鍵。
    見 data/manichaean/sources/index.ts 檔首「段號照抄」那一節。

四、**對不齊時留空，不猜。**
    左右兩欄的行號偶有一方多切或少切（殘片綴輯本來就會這樣）。
    以行號為鍵各自入位，缺的那一欄留空，並在 stdout 報出差異。
    硬湊成一對一會讓整篇往下錯一格，而版面完全正常。

引擎政策：本腳本不用 LLM。繁中另走 manichaean_translate.py。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "manichaean" / "sources" / "text"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 四冊 PDF 放哪。預設在 scratchpad，可用環境變數覆寫。
import os

PDF_DIR = Path(os.environ.get("IAMS_PDF_DIR", str(ROOT / "output" / "iams")))

VOLUMES: dict[int, str] = {
    1: "DB-Antholog.-1-Hist..pdf",
    2: "DB-Antholog.-2-Canon.pdf",
    3: "DB-Antholog.-3-Sab..pdf",
    4: "DB-Antholog.-4-Hymns.pdf",
}

# ── 版面常數（實測 2026-09-16，四冊一致）──
PAGE_W = 595.0
GUTTER_X = 300.0  # 欄界：左欄正文 89–297，右欄正文 303–508
LEFT_MARGIN = 100.0  # 左欄正文行首 x0 ≈ 89.8
RIGHT_MARGIN = 296.0  # 右欄正文行首 x0 ≈ 302.9
LINE_TOL = 3.0  # 同一行的 y 容差


# ────────────────────────── 純函式 ──────────────────────────

# 🚨 **對齊鍵不只一種，而且各冊不同。** 這件事第一版沒發現，
#    拿第四冊的 `N/` 去切第三冊，兩欄各自只切出一段，
#    對齊結果「零衝突、完美對齊」——因為根本沒切開。
#
#   第四冊（讚詩）  1/ 2/ 3/、4b/ 5a/     ← 編者的行號，字母尾碼不可漏認
#   第三冊（沙卜爾干）{a.5} {v.1} {c.1}    ← 編者的節號，兩欄都印
#   第二冊（正典）  兩種混用，另有 |5 |10 |15 的行號（只印在原文欄，不能當鍵）
#
# 所以切之前要先**看兩欄各自認得出幾個**，挑兩邊都有的那一種（見 choose_scheme）。
LINE_MARK = re.compile(r"(?<![\w/])(\d{1,3}[a-z]?)/")
SECTION_MARK = re.compile(r"\{([a-z]\.\d+)\}")

# 第三種鍵：**兩欄都印的方括號抄本編號**（[M17 V/i]、[So18151/R/Hd.]）。
# 這是第二冊多數篇章唯一共用的標記。
# 🚨 不可用通用的 \[...\] 去切——那批文獻裡到處是編者的補字括號
#    （[…….]、[m](ʾ)），拿來當段界會把每一段再切成幾十片。
#    故限定「括號內以館藏編號字首起頭」。
LOCATOR_MARK = re.compile(
    r"\[((?:MIK|So|Or|M|U|T|S|P)\.?\s?\d[^\[\]]{0,32})\]")

# ✗ **試過但不能用的第四種鍵：括號行號 (120) (125)。**
#    2026-09-17 實測。動機是對的——沙卜爾干那 19 段配不上，不是右欄沒英文
#    （右欄英文完整），是 choose_scheme 挑了稀疏的 {y.N} 節號當鍵，
#    而那幾頁兩欄唯一共有的密集標記確實是括號行號。
#
#    但 `\((\d{2,4})\)` 會把**參考文獻的年份與頁碼**一起當成行號：
#      M99 I/V 1948   ← (1948) 是 Henning 的出版年
#      M99 I/V 100    ← orig 混進「Ed. and tr. W.B. Henning,」
#    結果段數 80 → 417、英譯 61 → 372、配對率 75% → 76% 看似全面改善，
#    **實際上對齊已經整體錯位**（原文講「使者站立」配到英文「equally dressed」）。
#    這正是本檔開頭第四條警告的那種失敗：數字變好看、版面正常、內容全錯。
#
#    要用括號行號，得先把書目區與正文分開（IAMS 的書目穿插在殘片之間），
#    或限定「括號數字必須遞增且與左欄的 |N 行號同步」。在那之前不要再加回來。

MARK_SCHEMES: dict[str, re.Pattern] = {
    "line": LINE_MARK,
    "section": SECTION_MARK,
    "locator": LOCATOR_MARK,
}

# 抄本定位符：[M17 V/i]、[So18151/R/Hd.]、(MIK III 8260, verso, 001-005, Leaf 1)
LOCATOR = re.compile(r"[\[(]([^\[\]()]{3,60}?)[\])]")


def group_words_into_lines(words: list[tuple], tol: float = LINE_TOL) -> list[list[tuple]]:
    """把 PyMuPDF 的 words 依 y 座標分行，行內依 x 排序。

    words 的元素是 (x0, y0, x1, y1, text, block, line, word)。

    >>> w = [(90, 10, 99, 20, 'a', 0,0,0), (110, 11, 119, 21, 'b', 0,0,1),
    ...      (90, 40, 99, 50, 'c', 0,0,2)]
    >>> [[x[4] for x in ln] for ln in group_words_into_lines(w)]
    [['a', 'b'], ['c']]
    """
    out: list[list[tuple]] = []
    for w in sorted(words, key=lambda w: (round(w[1], 1), w[0])):
        if out and abs(out[-1][0][1] - w[1]) <= tol:
            out[-1].append(w)
        else:
            out.append([w])
    for ln in out:
        ln.sort(key=lambda w: w[0])
    return out


def split_line(line: list[tuple]) -> tuple[str, str, str]:
    """把一行切成 (跨欄, 左欄, 右欄) 三段文字，用不到的回空字串。

    🚨 **不可用「行首的 x」判整行的歸屬**——第一版就是這樣寫的，結果
       同一 y 上的左右兩欄被併成一行，整行按行首歸給左欄，於是
       英譯被塞進原文欄裡：「frʾydr ʾwd why hynd °° |15 superior and better…」。
       版面完全正常，只是每一段原文後面都黏著它自己的英譯。

    判準改成「這一行有沒有從**欄的左緣**起頭的字」：
      正文左欄一律起於 x≈89.8，正文右欄一律起於 x≈302.9（四冊一致）。
      兩者皆無 → 這是置中的標題或出處，屬跨欄。
      否則 → 依欄界把詞分到兩邊。

    >>> mk = lambda *xs: [(x, 0, x + 8, 10, f'w{i}', 0, 0, i) for i, x in enumerate(xs)]
    >>> split_line(mk(89.8, 120.0))          # 左欄正文
    ('', 'w0 w1', '')
    >>> split_line(mk(302.9, 340.0))         # 右欄正文
    ('', '', 'w0 w1')
    >>> split_line(mk(89.8, 302.9))          # 同一行的左右兩欄
    ('', 'w0', 'w1')
    >>> split_line(mk(181.5, 320.0))         # 置中標題（跨欄界、不從欄左緣起頭）
    ('w0 w1', '', '')
    >>> split_line(mk(150.0, 200.0))         # 縮排續行，整行都在左邊
    ('', 'w0 w1', '')
    """
    left = [w for w in line if w[0] < GUTTER_X]
    right = [w for w in line if w[0] >= GUTTER_X]

    # 一、整行都在同一邊 → 就是那一欄，不必再問行首。
    #    🚨 少了這一條，縮排的**續行**（如「| bryd | qwn<y>d」）會因為
    #       既不從左緣也不從右緣起頭而被判成置中標題，於是整行原文被丟掉。
    if not right:
        return "", line_text(left), ""
    if not left:
        return "", "", line_text(right)

    # 二、跨越欄界的行：有從欄左緣起頭的字就是兩欄並排，否則是置中標題。
    has_left_start = any(w[0] < LEFT_MARGIN for w in line)
    has_right_start = any(RIGHT_MARGIN <= w[0] <= RIGHT_MARGIN + 16 for w in line)
    if not has_left_start and not has_right_start:
        return line_text(line), "", ""
    return "", line_text(left), line_text(right)


def line_text(line: list[tuple]) -> str:
    """一行的文字。

    >>> line_text([(1,0,2,1,'a',0,0,0), (3,0,4,1,'b',0,0,1)])
    'a b'
    """
    return " ".join(w[4] for w in line).strip()


def choose_scheme(left: str, right: str) -> str | None:
    """挑一種**兩欄都認得出**的對齊鍵。兩邊都對不上就回 None。

    🚨 回 None 時**不可**硬用其中一種去切。只有一欄有的標記（例如第二冊
       原文欄的 |5 |10 行號）拿來當鍵，會讓另一欄整個落進第一段，
       而段數看起來正常、對齊零衝突——最難發現的那種錯。

    >>> choose_scheme('1/ a 2/ b', '1/ A 2/ B')
    'line'
    >>> choose_scheme('{a.5} x {v.1} y', 'text {a.5} X {v.1} Y')
    'section'
    >>> choose_scheme('|5 plain', 'plain English') is None
    True
    """
    best, best_n = None, 0
    for name, pat in MARK_SCHEMES.items():
        n = min(len(set(pat.findall(left))), len(set(pat.findall(right))))
        if n > best_n:
            best, best_n = name, n
    return best if best_n >= 2 else None


def split_numbered(text: str, scheme: str = "line") -> list[tuple[str, str]]:
    """把一段文字按對齊鍵切成 [(鍵, 正文), …]。

    標記之前的文字（沒有鍵的引言）以空字串為鍵放在最前面。

    >>> split_numbered('1/ alpha 2/ beta')
    [('1', 'alpha'), ('2', 'beta')]
    >>> split_numbered('lead 4b/ x 5a/ y')
    [('', 'lead'), ('4b', 'x'), ('5a', 'y')]
    >>> split_numbered('no marks here')
    [('', 'no marks here')]
    >>> split_numbered('{a.5} fifth {v.1} first', 'section')
    [('a.5', 'fifth'), ('v.1', 'first')]
    """
    parts = MARK_SCHEMES[scheme].split(text)
    out: list[tuple[str, str]] = []
    lead = parts[0].strip()
    if lead:
        out.append(("", lead))
    for i in range(1, len(parts) - 1, 2):
        body = parts[i + 1].strip()
        out.append((parts[i], body))
    return out


def find_locator(text: str) -> str | None:
    """抓出一段文字裡的抄本定位符。找不到回 None——**不猜、不自編**。

    >>> find_locator('[M17 V/i] 1/ gwš wcyyhyd')
    'M17 V/i'
    >>> find_locator('(MIK III 8260, verso, 001-005, Leaf 1)')
    'MIK III 8260, verso, 001-005, Leaf 1'
    >>> find_locator('1/ plain text') is None
    True
    """
    m = LOCATOR.search(text)
    if not m:
        return None
    cand = m.group(1).strip()
    # 定位符一定含館藏編號或葉面標記；純數字或純英文句子不是定位符。
    # 館藏編號的實際長相：M17、So18151、U 82、MIK III 8260、Or. 8212、T II D II 169。
    # 🚨 別只認「字首＋數字」：MIK 那一系的編號中間夾羅馬數字（MIK III 8260），
    #    漏認的話第四冊那一整批回鶻文寫本會全部取不到定位符，
    #    段號退化成 p.N ——看起來有段號，其實是頁碼，外部完全無法引用。
    if re.search(r"\b(?:MIK|So|Or|M|U|T|S|P)\.?\s*(?:[IVX]+\s+)*\d", cand):
        return cand
    return re.search(r"\b[RV]/", cand) and cand or None


#: 置中標題行裡的抄本編號：M49 I、M470、S8、M4a I R、So 18151、MIK III 8260
SIGLUM_HEADING = re.compile(
    r"^(?:M|So|Or|U|S|T|P|MIK)\s?\d+[a-z]?(?:\s+[IVX]+)?(?:\s+[RV])?$")


def find_siglum_heading(lines: list[str]) -> str | None:
    """從跨欄行裡挑出抄本編號標題。挑不到回 None。

    🚨 沒有這一步，段號會退化成頁碼（`p.5`）——**看起來有段號，
       其實是這份 PDF 的頁碼**，換一版就對不上，外部完全無法引用。
       抄本編號才是這一段在學界的身分證。

    >>> find_siglum_heading(['M49 I', 'MP: MM ii, 306-07'])
    'M49 I'
    >>> find_siglum_heading(['What a person must do to enter the religion']) is None
    True
    """
    for t in lines:
        s = t.strip()
        if SIGLUM_HEADING.match(s):
            return s
    return None


def align_columns(
    left: list[tuple[str, str]],
    right: list[tuple[str, str]],
) -> tuple[list[dict], list[str], list[str]]:
    """把兩欄按行號對齊，回 (segments, 僅左有, 僅右有)。

    🚨 **對不齊時留空，不猜。**硬湊一對一會讓整篇往下錯一格而版面完全正常。

    >>> segs, lo, ro = align_columns([('1', 'a'), ('2', 'b')], [('1', 'A'), ('3', 'C')])
    >>> [(s['n'], s['orig'], s['en']) for s in segs]
    [('1', 'a', 'A'), ('2', 'b', ''), ('3', '', 'C')]
    >>> lo, ro
    (['2'], ['3'])
    """
    lmap = {n: t for n, t in left if n}
    rmap = {n: t for n, t in right if n}
    keys = sorted(set(lmap) | set(rmap), key=_mark_sort_key)
    segs = [{"n": k, "orig": lmap.get(k, ""), "en": rmap.get(k, "")} for k in keys]
    return segs, sorted(set(lmap) - set(rmap), key=_mark_sort_key), sorted(set(rmap) - set(lmap), key=_mark_sort_key)


def _mark_sort_key(mark: str) -> tuple[str, int, str]:
    """對齊鍵的排序：先分組字母，再比數字，最後比尾碼。

    🚨 別用字串排序：'a.10' 會排在 'a.2' 前面，於是整篇的段落順序是錯的，
       而每一段的內容都正確——版面看不出任何異常。

    >>> sorted(['10', '2', '2b', '2a'], key=_mark_sort_key)
    ['2', '2a', '2b', '10']
    >>> sorted(['a.10', 'a.2', 'v.1'], key=_mark_sort_key)
    ['a.2', 'a.10', 'v.1']
    """
    m = re.fullmatch(r"([a-z])\.(\d+)", mark)
    if m:
        return (m.group(1), int(m.group(2)), "")
    m = re.fullmatch(r"(\d+)([a-z]?)", mark)
    if m:
        return ("", int(m.group(1)), m.group(2))
    return ("zz", 10**6, mark)


# ────────────────────────── 抽頁 ──────────────────────────

@dataclass
class Section:
    """選輯裡的一篇，對應本站書目的一個 slug。"""
    slug: str
    vol: int
    pages: range  # 1-based，含頭含尾
    title_zh: str
    siglum: str
    canon: str
    volume: str
    language: str
    note: str = ""
    names: dict[str, str] = field(default_factory=dict)


# 🚨 頁碼是**實際翻過的**（2026-09-16），不是猜的。
#    改版後頁碼會跑掉，重建前先跑 --probe 對一下標題。
SECTIONS: dict[str, Section] = {
    "sabuhragan-turfan": Section(
        slug="sabuhragan-turfan", vol=3, pages=range(3, 41),
        title_zh="沙卜爾干（吐魯番殘卷）", siglum="M 470, M 472, M 473 等",
        canon="iranian", volume="canonical-fragments", language="中古波斯語",
        note="全冊三部分：自傳／宇宙論／末世論。",
    ),
    "living-gospel": Section(
        slug="living-gospel", vol=2, pages=range(5, 19),
        title_zh="活福音", siglum="七 1",
        canon="canon", volume="seven-treatises", language="中古波斯語、粟特語、阿拉伯語",
        note="七經之首的殘葉與引文。",
    ),
    "book-of-giants": Section(
        slug="book-of-giants", vol=2, pages=range(19, 38),
        title_zh="巨人書", siglum="七 5",
        canon="canon", volume="seven-treatises", language="中古波斯語、帕提亞語、粟特語、回鶻語",
        note="亨寧綴輯的 Kaw A–Zs6 各殘片。",
    ),
    "book-of-mysteries": Section(
        slug="book-of-mysteries", vol=2, pages=range(38, 42),
        title_zh="祕密之書", siglum="七 4",
        canon="canon", volume="seven-treatises", language="中古波斯語、阿拉伯語",
    ),
    "treasure-of-life": Section(
        slug="treasure-of-life", vol=2, pages=range(42, 48),
        title_zh="生命寶庫", siglum="七 2",
        canon="canon", volume="seven-treatises", language="中古波斯語、阿拉伯語",
    ),
    "epistles": Section(
        slug="epistles", vol=2, pages=range(48, 54),
        title_zh="書信集", siglum="七 6",
        canon="canon", volume="seven-treatises", language="中古波斯語、帕提亞語",
    ),
    "psalms-and-prayers": Section(
        slug="psalms-and-prayers", vol=2, pages=range(54, 60),
        title_zh="詩篇與祈禱", siglum="七 7",
        canon="canon", volume="seven-treatises", language="中古波斯語、粟特語",
    ),
    "ardahang": Section(
        slug="ardahang", vol=2, pages=range(60, 74),
        title_zh="圖經", siglum="圖",
        canon="canon", volume="picture-book", language="帕提亞語、阿拉伯語",
        note="含《圖經講義》與《群書類述》摩尼教章的英譯。",
    ),
    "huyadagman": Section(
        slug="huyadagman", vol=4, pages=range(119, 122),
        title_zh="胡雅達格曼", siglum="M 4a, M 77 等",
        canon="iranian", volume="hymn-cycles", language="帕提亞語",
    ),
    "angad-rosnan": Section(
        slug="angad-rosnan", vol=4, pages=range(122, 130),
        title_zh="安加德‧羅什南", siglum="M 33, M 233 等",
        canon="iranian", volume="hymn-cycles", language="帕提亞語",
    ),
    "bema-liturgy": Section(
        slug="bema-liturgy", vol=4, pages=range(90, 119),
        title_zh="貝馬節禮儀文", siglum="M 801 等",
        canon="iranian", volume="church-documents", language="中古波斯語、帕提亞語",
    ),
}

LICENCE = (
    "原文轉寫與英譯取自國際摩尼教研究學會（IAMS）開放取用的"
    "《東方摩尼教選輯》(Anthologia Manichaica Orientalia, Samuel N. C. Lieu 編，"
    "Ancient India and Iran Trust, Cambridge)。各篇的原校訂者與譯者見每段出處。"
    "繁中為本站自譯。"
)


def extract_page(page) -> dict:
    """抽一頁：回 {'full': [str], 'left': [str], 'right': [str]}。"""
    lines = group_words_into_lines(page.get_text("words"))
    out: dict[str, list[str]] = {"full": [], "left": [], "right": []}
    for ln in lines:
        full, left, right = split_line(ln)
        if full:
            out["full"].append(full)
        if left:
            out["left"].append(left)
        if right:
            out["right"].append(right)
    return out


def is_running_head(text: str) -> bool:
    """頁首頁尾：書名、卷名、頁碼。逐行剝，不整塊丟。

    🚨 見 [[feedback_boilerplate_strip_lines_not_blocks]]：整塊丟會連黏在
       同一塊裡的正文一起刪掉。

    >>> is_running_head('Anthologia Manichaica Orientalia')
    True
    >>> is_running_head('II. From the Manichaean Canon')
    True
    >>> is_running_head('42')
    True
    >>> is_running_head('1/ gwš wcyyhyd')
    False
    """
    t = text.strip()
    if not t or t.isdigit():
        return True
    if t.startswith("Anthologia Manichaica Orientalia"):
        return True
    if re.match(r"^(I|II|III|IV)\.\s+(From the Manichaean Canon|Šābuhragān|Texts on|Manichaean Hymns)", t):
        return True
    return t == "¥]-^µ"  # 該書的裝飾分隔符，抽文字時會變成亂碼


def build(slug: str, *, write: bool = True) -> dict:
    """把一篇的兩欄抽出來對齊，寫成 reader 吃的 JSON。"""
    import fitz  # 延後 import：--list 不必載 PyMuPDF

    sec = SECTIONS.get(slug)
    if sec is None:
        raise SystemExit(f"無此篇：{slug}。可選：{', '.join(SECTIONS)}")
    path = PDF_DIR / VOLUMES[sec.vol]
    if not path.exists():
        raise SystemExit(
            f"找不到選輯 PDF：{path}\n"
            f"下載（注意會截斷，務必驗 %%EOF）：\n"
            f"  curl -L -C - --retry 5 --max-time 900 -o '{path}' \\\n"
            f"    https://www.manichaeism.de/wp-content/uploads/.../{VOLUMES[sec.vol]}\n"
            f"或設 IAMS_PDF_DIR 指向存放處。")

    doc = fitz.open(path)

    # 先把整篇抽完，才能決定用哪一種對齊鍵（各冊不同，見 LINE_MARK 那一段）。
    pages: list[tuple[int, str, str]] = []
    for pno in sec.pages:
        if pno - 1 >= doc.page_count:
            break
        cols = extract_page(doc[pno - 1])
        pages.append((
            pno,
            " ".join(t for t in cols["left"] if not is_running_head(t)),
            " ".join(t for t in cols["right"] if not is_running_head(t)),
            find_siglum_heading([t for t in cols["full"] if not is_running_head(t)]),
        ))
    scheme = choose_scheme(" ".join(p[1] for p in pages), " ".join(p[2] for p in pages))
    if scheme is None:
        # 🚨 硬切會產出「零衝突的完美對齊」而內容全錯位。寧可不出檔。
        print(f"✗ {slug:22s} 兩欄找不到共同的對齊鍵，不產出（別硬切）")
        return {}

    locator = None
    segments: list[dict] = []
    only_left: list[str] = []
    only_right: list[str] = []

    for pno, ltxt, rtxt, head_siglum in pages:
        # 優先序：置中標題的抄本編號 > 內文的定位符 > 沿用上一頁的
        loc = head_siglum or find_locator(ltxt) or find_locator(rtxt) or locator
        locator = loc

        segs, lo, ro = align_columns(split_numbered(ltxt, scheme), split_numbered(rtxt, scheme))
        only_left += lo
        only_right += ro
        for s in segs:
            # 段號優先用抄本編號；抄本編號還沒出現時（各篇開頭數頁）
            # 退回**選輯本身的冊頁**——那仍是可引用的出版品座標，
            # 不是這份 PDF 的內部頁碼。留白的假頁碼比沒有更糟。
            sep = {"line": "/", "section": " §"}.get(scheme, "")
            base = loc or f"Anth. {sec.vol} p.{pno}"
            ref = f"{base} {s['n']}{sep}" if s["n"] else base
            segments.append({
                "chapter": loc or f"Anth. {sec.vol} p.{pno}",
                "verse": s["n"] or "—",
                "ref": ref,
                "orig": s["orig"],
                "en": s["en"],
                "zh": "",
            })

    out = {
        "slug": sec.slug,
        "siglum": sec.siglum,
        "title_zh": sec.title_zh,
        "canon": sec.canon,
        "volume": sec.volume,
        "script": "manichaean-translit",
        "orig_source": f"IAMS《東方摩尼教選輯》第 {sec.vol} 冊，pp. {sec.pages[0]}–{sec.pages[-1]}",
        "orig_url": "https://www.manichaeism.de/other-resources-2/",
        "en_source": f"同上（原文轉寫與英譯逐行並排刊出）。{sec.note}",
        "en_url": "https://www.manichaeism.de/other-resources-2/",
        "licence": LICENCE,
        "pivot": "iams-eng",
        "scheme": scheme,
        "pivot_note": (
            "本篇原文轉寫與英譯同出 IAMS 開放取用的《東方摩尼教選輯》，"
            "兩欄是同一份校訂本的並排刊文，段號沿用該書的抄本定位符與行號，本站不自編。"
        ),
        "segments": segments,
    }
    filled_o = sum(1 for s in segments if s["orig"].strip())
    filled_e = sum(1 for s in segments if s["en"].strip())

    # ── 品質閘 ──────────────────────────────────────────────────
    # 🚨 這批 PDF 的標記體例各篇不同，對齊鍵挑錯時**不會報錯**，
    #    只會產出「兩欄各自都有東西、但配對錯開一格」的檔案——
    #    而 reader 打開來版面完全正常。所以出檔前要過閘。
    #    閘沒過就不寫檔（也不留半成品騙後面的稽核）。
    both = sum(1 for s in segments if s["orig"].strip() and s["en"].strip())
    pair_rate = both / len(segments) if segments else 0.0
    if pair_rate < 0.65:
        print(f"✗ {slug:22s} 配對率僅 {pair_rate:.0%}（{both}/{len(segments)}），"
              f"對齊鍵 '{scheme}' 不適用本篇，不產出")
        old_path = OUT_DIR / f"{slug}.json"
        if old_path.exists():
            old_path.unlink()  # 不留上一版的壞檔冒充已上架
        return {}
    if write:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUT_DIR / f"{slug}.json").write_text(
            json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✓ {slug:22s} {len(segments):4d} 段　配對 {both}（{pair_rate:.0%}）　原文 {filled_o}／英譯 {filled_e}"
          + (f"　⚠ 僅原文有 {len(only_left)}／僅英譯有 {len(only_right)}" if only_left or only_right else ""))
    return out


def cmd_probe(vol: int, pno: int) -> int:
    import fitz
    doc = fitz.open(PDF_DIR / VOLUMES[vol])
    cols = extract_page(doc[pno - 1])
    for k in ("full", "left", "right"):
        print(f"───── {k} ─────")
        for t in cols[k]:
            mark = "  (頁首頁尾)" if is_running_head(t) else ""
            print(f"  {t[:100]}{mark}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="IAMS 選輯 → 摩尼教經典取源")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--probe", nargs=2, type=int, metavar=("VOL", "PAGE"))
    ap.add_argument("--build", nargs="*", metavar="SLUG")
    a = ap.parse_args()

    if a.list:
        print(f"PDF 目錄：{PDF_DIR}")
        for s in SECTIONS.values():
            ok = "✓" if (PDF_DIR / VOLUMES[s.vol]).exists() else "✗"
            print(f"  {ok} {s.slug:22s} 第 {s.vol} 冊 pp.{s.pages[0]}–{s.pages[-1]:<4d} {s.title_zh}")
        return 0
    if a.probe:
        return cmd_probe(*a.probe)
    if a.build is not None:
        for slug in (a.build or list(SECTIONS)):
            build(slug)
        return 0
    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
