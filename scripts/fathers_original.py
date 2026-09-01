# -*- coding: utf-8 -*-
"""教父卷第三欄「原文」的純函式核心 —— 拉丁／希臘原文按卷章切段、與站上章節對齊。

站上教父卷已經是兩欄（content = 繁中，source_text = Schaff 英譯）。要補的第三
欄是拉丁／希臘原典。對齊靠的是章節編號：站上的 chapter_path 寫成
「懺悔錄 卷一 第1-10章」，原典電子本也按 liber.caput 編號，兩邊都是同一套古典
分章，機械對得起來——不需要逐句語意對齊。

🚨 對齊前一定要先過覆蓋率閘（`coverage`）。首次跑《懺悔錄》就靠它抓到站上卷一
只到第 18 章、第 19–20 章中英文都不存在——書打得開、讀起來順，兩章卻不見了。
沒有這道閘，那兩章的拉丁原文會被默默併進第 18 章那一段，變成三欄看起來齊、
內容卻錯位。

無網路、無 DB，測試在 scripts/tests/test_fathers_original.py。
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass

# ── 章節編號 ────────────────────────────────────────────────────────────────
# 🚨 卷次一律走 zh_numeral() 現算，不要再列舉對照表。先前列到「二十」為止，
#    《上帝之城》有 22 卷，卷二十一與卷二十二整整兩卷就靜靜地沒被解析到——
#    腳本照跑、不報錯，只是那兩卷沒有原文。

CHAPTER_PATH = re.compile(
    r"卷([一二三四五六七八九十]+)"          # 卷次（無「卷」的單卷著作見下）
    r"(?:\s*第(\d+)(?:[-–](\d+))?章)?\s*$")
CHAPTER_ONLY = re.compile(r"第(\d+)(?:[-–](\d+))?章\s*$")


@dataclass(frozen=True)
class Span:
    """站上一段所涵蓋的原典範圍。book=None 表示該著作不分卷。"""
    book: int | None
    first: int
    last: int

    def chapters(self) -> list[int]:
        return list(range(self.first, self.last + 1))


def parse_chapter_path(path: str, chapters_in_book: int | None = None) -> Span | None:
    """把 chapter_path 解析成卷章範圍；解析不出來回 None（前言、書名頁之類）。

    「懺悔錄 卷一 第1-10章」→ Span(1, 1, 10)
    「懺悔錄 卷二」          → Span(2, 1, chapters_in_book)   ← 整卷一段
    「駁諸異端 第3章」       → Span(None, 3, 3)
    """
    if not path:
        return None
    m = CHAPTER_PATH.search(path)
    if m:
        book = zh_numeral(m.group(1))
        if book is None:
            return None
        if m.group(2) is None:
            # 整卷收在一段（《懺悔錄》卷二就是這樣）。要知道那一卷幾章才填得出
            # 範圍；不知道就不猜——猜錯會把別卷的原文接上去。
            if chapters_in_book is None:
                return None
            return Span(book, 1, chapters_in_book)
        first = int(m.group(2))
        return Span(book, first, int(m.group(3)) if m.group(3) else first)
    m = CHAPTER_ONLY.search(path)
    if m:
        first = int(m.group(1))
        return Span(None, first, int(m.group(2)) if m.group(2) else first)
    return None


# ── 原典解析 ────────────────────────────────────────────────────────────────
def strip_html(raw: str) -> str:
    raw = re.sub(r"(?is)<(script|style).*?</\1>", "", raw)
    raw = re.sub(r"(?i)<br\s*/?>|</p\s*>|</div\s*>|</h\d\s*>", "\n", raw)
    raw = re.sub(r"<[^>]+>", "", raw)
    return html.unescape(raw)


# The Latin Library 的段標形如 `1.13.21` = liber.caput.paragraphus，獨佔一行。
LL_MARK = re.compile(r"^\s*(\d+)\.(\d+)(?:\.(\d+))?\s*$")

# 頁面本身的導覽文字。這些在頁尾，位置在最後一個段標「之後」，所以會被當成正文
# 接到該卷最後一節的尾巴——13 卷就是 13 節被汙染，而且只看命中率看不出來。
SITE_CHROME = re.compile(
    r"^(The Latin Library|The Classics Page|Christian Latin|commentary on [\d.]+"
    r"|Perseus|Documenta Catholica Omnia|Wikisource)\s*$", re.I)


def parse_numbered_text(text: str, default_book: int | None = None,
                        drop: re.Pattern[str] = SITE_CHROME
                        ) -> dict[tuple[int | None, int, int | None], str]:
    """把帶 `卷.章.節` 行標的原典切成 {(卷, 章, 節): 文字}。

    節號（paragraphus）一定要留著。站上的中英譯段落開頭正好也帶同一組節號
    （「17. 我自幼就聽聞了…」／「17. Even as a boy I had heard…」），那是把拉丁
    逐段對到中譯的唯一可靠鍵——只按章對的話，一章十段拉丁會全擠在第一列。

    行標之前的內容（卷名、頁眉）一律丟棄，留著會混進第一節。
    """
    out: dict[tuple[int | None, int, int | None], list[str]] = {}
    key: tuple[int | None, int, int | None] | None = None
    for line in text.split("\n"):
        line = line.strip()
        m = LL_MARK.match(line)
        if m:
            if m.group(3):
                key = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
            else:
                key = (default_book, int(m.group(1)), int(m.group(2)))
            out.setdefault(key, [])
        elif key is not None and line and not drop.match(line):
            out[key].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items() if v}


# 第二種行標：章號用方括號夾的羅馬數字，寫在該章第一行的行首，同行接正文。
#   [Pr] Gloriosissimam ciuitatem Dei…      ← 序言
#   [I]  Ex hac namque existunt inimici…
# 《上帝之城》《論三位一體》這一系的電子本都是這個樣子，沒有節號可用，只能對到章。
BRACKET_CHAPTER = re.compile(r"^\[(Pr|[IVXLCDM]+)\]\s*(.*)$", re.I)
_ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def roman(s: str) -> int | None:
    """羅馬數字轉整數；讀不準就回 None，不猜。"""
    total = highest = 0
    for ch in reversed(s.upper()):
        v = _ROMAN.get(ch)
        if not v:
            return None
        total += v if v >= highest else -v
        highest = max(highest, v)
    return total


def parse_bracketed_chapters(text: str, book: int,
                             drop: re.Pattern[str] = SITE_CHROME
                             ) -> dict[tuple[int | None, int], str]:
    """把 `[I] …` 這種行標的原典切成 {(卷, 章): 文字}。序言記為第 0 章。"""
    out: dict[tuple[int | None, int], list[str]] = {}
    key: tuple[int | None, int] | None = None
    for line in text.split("\n"):
        line = line.strip()
        if not line or drop.match(line):
            continue
        m = BRACKET_CHAPTER.match(line)
        if m:
            n = 0 if m.group(1).lower() == "pr" else roman(m.group(1))
            if n is None:
                continue
            key = (book, n)
            out.setdefault(key, [])
            if m.group(2):
                out[key].append(m.group(2))
        elif key is not None:
            out[key].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items() if v}


# 第三種行標：章號。同一個網站的同一位作者就有五種寫法（實測 The Latin Library
# 的特土良）：
#   I. [1] Si non licet…        行首羅馬數字後直接接正文
#   I / [1] Qui status fidei…   羅馬數字獨佔一行
#   Capitulum I                 拼出 Capitulum
#   CAPUT 1. [1] Varie…         拼出 CAPUT，用阿拉伯數字
#   …CAP. 1. [1] De Sacramento… 整篇沒有換行，章標只能在行中找
# 所以不預設某一種，而是每種都掃一遍、取「遞增序列最長」的那一種。
# 🚨 每一種都要允許行首縮排。少了 `[ 	]*`，只要那個檔的行有縮排就一個章標也
#    掃不到，而腳本只會回報「命中 0」，看不出是格式沒對上還是原典真的沒有。
CHAPTER_PATTERNS = (
    # 🚨 CAP 後面的句點可有可無：de Ieiunio 只有第一章寫「CAP.  I.」，其餘全是
    #    「CAP II.」。硬要那個句點的話，那一篇就只認得出第一章。
    re.compile(r"(?:^|(?<=[\s.]))(?:CAPUT|CAP|Capitulum|Caput)(?![A-Za-z])\.?\s*([IVXLCDM]+|\d+)\s*\.?\s+", re.M),
    re.compile(r"^[ 	]*([IVXLCDM]{1,7})\.\s+", re.M),
    re.compile(r"^[ 	]*(\d{1,3})\.\s+", re.M),
    re.compile(r"^[ 	]*([IVXLCDM]{1,7})\.?[ 	]*$", re.M),
)
# 頁尾導覽列，在整篇不換行的檔案裡會黏在最後一章的尾巴。
TRAILING_CHROME = re.compile(
    r"(?:Tertullian|Christian Latin|The Latin Library|The Classics Page|"
    r"Augustine|Ambrose|Jerome)[\s\w]*$")


def _longest_increasing(marks):
    """在候選章標裡取「章號遞增」的最長一串，其餘丟掉。

    不能只用「最多往後跳 N 章」那種簡單門檻：The Latin Library 的
    de Praescriptione 檔案本身就缺了第 4–22 章，III 之後直接跳 XXIII，門檻一擋
    就只剩三章。但也不能完全不管——正文裡任何大寫羅馬字母加句點的行（縮寫、
    人名縮寫）都會被讀成一個天文數字的章號，把後面整串毀掉。取最長遞增子序列
    兩邊都顧得到：容得下缺章，又會自動丟掉離群值。
    """
    if not marks:
        return []
    best = [0] * len(marks)
    prev = [-1] * len(marks)
    for i in range(len(marks)):
        best[i] = 1
        for j in range(i):
            if marks[j][2] < marks[i][2] and best[j] + 1 > best[i]:
                best[i] = best[j] + 1
                prev[i] = j
    i = max(range(len(marks)), key=lambda k: best[k])
    out = []
    while i >= 0:
        out.append(marks[i])
        i = prev[i]
    return out[::-1]


def _chapter_marks(text, pat):
    """該寫法掃得出的 (章標起點, 章標終點, 章號)，取最長遞增的一串。"""
    found = []
    for m in pat.finditer(text):
        token = m.group(1)
        n = int(token) if token.isdigit() else roman(token)
        if n is not None and 0 < n < 400:
            found.append((m.start(), m.end(), n))
    return _longest_increasing(found)


def parse_chapter_markers(text: str) -> dict[tuple[int | None, int], str]:
    """把帶章標的原典切成 {(None, 章): 文字}，自動判斷該檔用哪一種章標寫法。"""
    best: list[tuple[int, int, int]] = []
    for pat in CHAPTER_PATTERNS:
        marks = _chapter_marks(text, pat)
        if len(marks) > len(best):
            best = marks
    if len(best) < 2:
        return {}
    out: dict[tuple[int | None, int], str] = {}
    for i, (_, mark_end, n) in enumerate(best):
        # 這一章的正文從自己的章標之後，切到「下一個章標之前」——不是下一個章標
        # 之後，否則每一章都會把下一章的標記一起吞進來。
        stop = best[i + 1][0] if i + 1 < len(best) else len(text)
        body = text[mark_end:stop]
        if i + 1 == len(best):
            body = TRAILING_CHROME.sub("", body)
        kept = [l.strip() for l in body.split("\n")
                if l.strip() and not SITE_CHROME.match(l.strip())]
        if kept:
            out[(None, n)] = "\n".join(kept)
    return out

# ── TEI 原典（Open Greek and Latin 的 First1KGreek）──────────────────────────
# 使徒教父、猶斯定、亞歷山卓的革利免、俄利根都在裡面，是機讀的 TEI XML，不必自己
# OCR。結構是 <div type="textpart" subtype="chapter" n="1"> 內含 subtype="section"；
# 伊格那丟那份多一層 subtype="epistle"，七封書信裝在同一個檔裡。
#
# 🚨 <note> 是校勘註釋，必須整個剔掉。留著的話異文與手稿代號會混進正文，而讀者
#    看到的是一段「看起來像希臘文」的東西——這種錯不會有任何訊號。
TEI_PREFACE = {"praef": 0, "prooemium": 0, "preface": 0, "pr": 0, "praefatio": 0}


def parse_tei_chapters(xml: str, epistle: str | None = None
                       ) -> dict[tuple[int | None, int], str]:
    """把 First1KGreek 的 TEI 切成 {(卷, 章): 文字}。序言記為第 0 章。

    檔案沒有 book 這一層時卷次是 None（伊格那丟、革利免那些單卷著作）。

    `epistle` 有值時只取那一封（伊格那丟七書共用一個檔，n 是 "1".."7"）。
    """
    from lxml import etree

    root = etree.fromstring(xml.encode("utf-8"))
    ns = {"t": "http://www.tei-c.org/ns/1.0"}

    scope = root
    if epistle is not None:
        found = root.xpath(f'.//t:div[@subtype="epistle"][@n="{epistle}"]', namespaces=ns)
        if not found:
            return {}
        scope = found[0]

    # 🚨 章那一層不一定叫 chapter。提阿非羅《致奧托呂庫書》那份只有 book/section
    #    兩層，硬找 chapter 會解析出 0 章——而腳本只回報「命中 0」，看起來像取源
    #    壞掉。找不到 chapter 就退而用 section。
    divs = scope.xpath('.//t:div[@subtype="chapter"]', namespaces=ns)
    if not divs:
        divs = scope.xpath('.//t:div[@subtype="section"]', namespaces=ns)

    out: dict[tuple[int | None, int], str] = {}
    for div in divs:
        raw = (div.get("n") or "").strip()
        n = TEI_PREFACE.get(raw.lower())
        if n is None:
            if not raw.isdigit():
                continue
            n = int(raw)
        # 🚨 有 book 這一層就一定要把卷次帶進鍵。《駁塞爾蘇斯》八卷的章號各自從
        #    一起算，只用章號當鍵的話八卷會互相覆蓋，最後每一卷都拿到第八卷的
        #    內容——命中率照樣滿分，三欄照樣排得整整齊齊。
        book: int | None = None
        for anc in div.iterancestors():
            if anc.get("subtype") == "book":
                token = (anc.get("n") or "").strip()
                book = TEI_PREFACE.get(token.lower(),
                                       int(token) if token.isdigit() else None)
                break
        # 校勘註釋整個拿掉，連同它的 tail（註釋之後、下一個節點之前的文字仍是正文，
        # 所以 tail 要接回去，不能連著 note 一起刪）
        clone = etree.fromstring(etree.tostring(div))
        for note in clone.xpath('.//*[local-name()="note"]'):
            tail = note.tail or ""
            parent = note.getparent()
            prev = note.getprevious()
            if prev is not None:
                prev.tail = (prev.tail or "") + tail
            else:
                parent.text = (parent.text or "") + tail
            parent.remove(note)
        text = " ".join(" ".join(clone.itertext()).split())
        if text:
            out[(book, n)] = text
    return out


# ── 希臘原典（Migne PG 的 OCR 稿）───────────────────────────────────────────
# 第三種行標：希臘字母數字。ΛΟΓΟΣ 分卷、α΄ β΄ γ΄ 分節，節號正好對得上 NPNF 中英譯
# 段落開頭的 1. 2. 3.（同一套本篤會編次）。
GREEK_LETTER_VALUE = {
    "α": 1, "β": 2, "γ": 3, "δ": 4, "ε": 5, "ϛ": 6, "ς": 6, "ζ": 7, "η": 8, "θ": 9,
    "ι": 10, "κ": 20, "λ": 30, "μ": 40, "ν": 50, "ξ": 60, "ο": 70, "π": 80,
    "ρ": 100, "σ": 200, "τ": 300, "υ": 400, "φ": 500, "χ": 600, "ψ": 700, "ω": 800,
}
GREEK_SECTION = re.compile(r"^\s*([α-ωϛ]{1,3})[΄'’]\s*[.·]?\s*(.*)$")
GREEK_BOOK_WORD = {
    "ΠΡΩΤΟΣ": 1, "ΔΕΥΤΕΡΟΣ": 2, "ΤΡΙΤΟΣ": 3,
    "ΤΕΤΑΡΤΟΣ": 4, "ΠΕΜΠΤΟΣ": 5, "ΕΚΤΟΣ": 6, "ΕΚΤΟΣ.": 6,
}
GREEK_BOOK = re.compile(r"^\s*ΛΟΓΟΣ\s+([Α-Ωα-ωϛ]{1,9})[΄'’]?\.?\s*$")
# 每一卷正文前都有一份目錄，開頭是 ΤΑΔΕ ΕΝΕΣΤΙΝ，而且同樣用 α΄ β΄ γ΄ 編號。
GREEK_TOC = re.compile(r"ΤΑΔΕ\s+ΕΝΕΣΤΙΝ")


TOC_ORDINAL = (("ΠΡΩΤ", 1), ("ΔΕΥΤΕΡ", 2), ("ΤΡΙΤ", 3),
               ("ΤΕΤΑΡΤ", 4), ("ΠΕΜΠΤ", 5), ("ΕΚΤ", 6),
               ("ΕΒΔΟΜ", 7), ("ΟΓΔΟ", 8), ("ΕΝΑΤ", 9), ("ΔΕΚΑΤ", 10))


def toc_book_number(line: str) -> int | None:
    """從「ΤΑΔΕ ΕΝΕΣΤΙΝ ΕΝ ΤΩ ΠΡΩΤΩ ΛΟΓΩ」讀出這是第幾卷。讀不出回 None。"""
    up = line.upper()
    for stem, n in TOC_ORDINAL:
        if stem in up:
            return n
    return None


def greek_numeral(s: str) -> int | None:
    """「ια΄」→ 11。讀不準回 None，不猜。"""
    total = 0
    for ch in s:
        v = GREEK_LETTER_VALUE.get(ch)
        if v is None:
            return None
        total += v
    return total or None


def dedupe_ledger(rows: list[dict], key: tuple[str, ...] = ("page", "crop")) -> list[dict]:
    """帳本去重：同一個裁切只留最後寫入的那一筆。

    🚨 OCR 帳本是 append-only，兩個程序同時跑就會各自 OCR 同一個裁切、各寫一列
       （實際發生過，4 個裁切重複）。不去重的話那幾塊的原文會被接兩遍，讀起來是
       同一段話講了兩次——通順、看不出錯。
    """
    latest: dict[tuple, dict] = {}
    for r in rows:
        latest[tuple(r[k] for k in key)] = r
    return list(latest.values())


def join_crops(texts: list[str]) -> str:
    """把同一頁上下兩半（含 1.5% 重疊）的 OCR 稿接起來，去掉接縫處重複的行。

    留重疊是為了不讓剛好切在字行中間的那一行消失；代價是接縫上下各有幾行相同，
    不去重就會在正文裡憑空多出重複的句子。
    """
    out: list[str] = []
    for chunk in texts:
        lines = [l.rstrip() for l in chunk.split("\n")]
        while lines and not lines[0].strip():
            lines.pop(0)
        tail = [l.strip() for l in out[-6:] if l.strip()]
        while lines and lines[0].strip() in tail:
            lines.pop(0)
            while lines and not lines[0].strip():
                lines.pop(0)
        out.extend(lines)
    return "\n".join(out)


def parse_greek_sections(text: str) -> dict[tuple[int | None, int], str]:
    """把 PG 的希臘 OCR 稿切成 {(卷, 節): 文字}。

    三個陷阱，都是掃描本 OCR 稿特有的：

    ① **每卷正文前有一份目錄**（ΤΑΔΕ ΕΝΕΣΤΙΝ ΕΝ ΤΩ ΠΡΩΤΩ ΛΟΓΩ），同樣用
       α΄ β΄ γ΄ 編號。不濾掉就會拿目錄的一行摘要當整節原文，而三欄照樣排得整整
       齊齊。作法：ΤΑΔΕ 之後進「目錄模式」，節號回頭（又見 α΄）才算目錄結束。
       🚨 不要改成「一回頭就把已收的整串丟掉」——正文裡只要有一個 OCR 誤判的低
       節號，那一卷就會被整卷丟光，而且沒有任何錯誤訊息。
    ② **卷號不在 `ΛΟΓΟΣ ΠΡΩΤΟΣ` 那一行**——書名頁常被 OCR 拆成 `ΛΟΓ` / `ΛΟΓΟΣ`
       兩個殘行，卷號整個掉了。改以目錄標題那一行的序數（ΠΡΩΤΩ／ΔΕΥΤΕΡΩ…）為準，
       讀不出來就在前一卷上加一。
    ③ **正文中間會冒出書眉 `ΛΟΓΟΣ Α΄`**。同一卷的書眉不可以觸發換卷，否則那一卷
       會被切成好幾段。
    """
    result: dict[tuple[int | None, int], list[str]] = {}
    book: int | None = None
    current: list[str] | None = None
    last = 0
    in_toc = False
    toc_last = 0

    def new_book(n: int | None) -> None:
        nonlocal book, current, last
        book = n if n is not None else ((book or 0) + 1)
        current, last = None, 0

    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            continue

        if GREEK_TOC.search(line):
            new_book(toc_book_number(line))
            in_toc, toc_last = True, 0
            continue

        m = GREEK_BOOK.match(line)
        if m:
            n = GREEK_BOOK_WORD.get(m.group(1)) or greek_numeral(m.group(1).lower())
            if n is not None and n != book:       # 同一卷的書眉不算換卷
                new_book(n)
                in_toc = False
            continue

        m = GREEK_SECTION.match(line)
        n = greek_numeral(m.group(1)) if m else None

        if in_toc:
            if n is not None and n <= toc_last:
                in_toc = False                     # 節號回頭 → 目錄結束，正文開始
            else:
                if n is not None:
                    toc_last = n
                continue                           # 目錄項一律不收

        # 正文只認遞增的節號，往下最多跳兩節（OCR 偶爾漏一個，ς΄ 最常漏）。
        # 其餘一律當成內文接下去——普通希臘字後面接撇號長得很像節號。
        if n is not None and last < n <= last + 3:
            current = [m.group(2)] if m.group(2) else []
            result[(book, n)] = current
            last = n
        elif current is not None:
            current.append(line)

    return {k: "\n".join(x for x in v if x).strip()
            for k, v in result.items() if any(x.strip() for x in v)}


ZH_CHAPTER_HEAD = re.compile(r"^#{0,4}\s*第([零〇一二三四五六七八九十百]+)章")


def zh_numeral(s: str) -> int | None:
    """「二十一」→ 21。讀不準回 None。與 lib/multilang-sources.ts 的同名函式同規則。"""
    digits = {"零": 0, "〇": 0, "一": 1, "二": 2, "三": 3, "四": 4,
              "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
    if not s:
        return None
    if "十" not in s and "百" not in s:
        v = 0
        for ch in s:
            if ch not in digits:
                return None
            v = v * 10 + digits[ch]
        return v
    acc = digit = 0
    for ch in s:
        if ch in digits:
            digit = digits[ch]
        elif ch == "十":
            acc += (digit or 1) * 10
            digit = 0
        elif ch == "百":
            acc += (digit or 1) * 100
            digit = 0
        else:
            return None
    return acc + digit


def book_of(numbers: list[int]) -> list[int]:
    """章號序列 → 每個章號屬於第幾卷。章號不再遞增就算換了一卷。

    多卷著作的中譯有兩種編號習慣，同一冊裡都有：《駁馬吉安》五卷是整部連續
    編號 1–145，《論婦女裝飾》兩卷卻是每卷從第一章重來。前者要把原典各卷的
    章號累計接續，後者要按卷分開對——搞反了就整部對不上。這個函式服務後者。
    """
    out: list[int] = []
    book = 1
    last = 0
    for n in numbers:
        if n <= last:
            book += 1
        out.append(book)
        last = n
    return out


def work_name(chapter_path: str) -> str:
    """把 chapter_path 的「作品名」切出來（去掉「 第N章」「 卷一 第N章」後綴）。

    🚨 比對一定要用「作品名完全相符」，不可以用 startswith。ANF 第一卷同時收了
       〈依納爵致以弗所人書〉與〈依納爵致以弗所人書（敘利亞文版）〉——敘利亞短本
       是另一個文本，用 startswith 就會把標準希臘本配到它身上，而三欄照樣排得
       整整齊齊。
    """
    name = re.sub(r"\s*第\d+.*$", "", chapter_path or "")
    # 「懺悔錄 卷二」整卷收成一段時沒有「第N章」後綴，卷次也要剝掉，
    # 否則那一整卷會被當成另一部著作而整段跳過。
    name = re.sub(r"\s*卷[一二三四五六七八九十]+\s*$", "", name)
    return name.strip()


def chapter_headings(body: list[str]) -> list[tuple[int, int]]:
    """回傳 [(段索引, 章號)]，只收讀得準的。"""
    out: list[tuple[int, int]] = []
    for i, p in enumerate(body):
        m = ZH_CHAPTER_HEAD.match(p)
        n = zh_numeral(m.group(1)) if m else None
        if n is not None:
            out.append((i, n))
    return out


def fill_column(size: int, hits: list[tuple[int, str]]) -> list[str]:
    """把 (段索引, 原文) 排進一個與中文欄等長的欄位。"""
    col = [""] * size
    for i, text in hits:
        col[i] = text
    return col

def align_by_chapter_heading(body: list[str], book: int | None,
                             chapters: dict[tuple[int | None, int], str]
                             ) -> tuple[list[str], int, int]:
    """沒有節號的著作，退一級對到章：整章原文放在該章中文標題那一格。

    比逐節粗，但位置是對的。粗而對，好過細而錯位——錯位在畫面上看不出來。
    """
    col = [""] * len(body)
    hit = heads = 0
    for i, p in enumerate(body):
        m = ZH_CHAPTER_HEAD.match(p)
        if not m:
            continue
        n = zh_numeral(m.group(1))
        if n is None:
            continue
        heads += 1
        text = chapters.get((book, n))
        if text:
            col[i] = text
            hit += 1
    return col, hit, heads


def by_chapter(sections: dict[tuple[int | None, int, int | None], str]
               ) -> dict[tuple[int | None, int], str]:
    """{(卷,章,節)} → {(卷,章)}，節內容依節號順序接起來。覆蓋率閘用這一層。"""
    grouped: dict[tuple[int | None, int], list[tuple[int, str]]] = {}
    for (book, chap, para), text in sections.items():
        grouped.setdefault((book, chap), []).append((para or 0, text))
    return {k: "\n\n".join(t for _, t in sorted(v)) for k, v in grouped.items()}


def by_paragraph(sections: dict[tuple[int | None, int, int | None], str]
                 ) -> dict[tuple[int | None, int], str]:
    """{(卷,章,節)} → {(卷, 節): 文字}。節號在一卷之內連號，是對齊鍵。"""
    out: dict[tuple[int | None, int], str] = {}
    for (book, _chap, para), text in sections.items():
        if para is not None:
            out[(book, para)] = text
    return out


# ── 逐段對齊 ────────────────────────────────────────────────────────────────
# 與 lib/ebook-render.ts 的 splitBodyAndFootnotes 同一套規則。對照欄是按索引
# zip 的（lib/multilang-sources.ts 的 zipParallel），所以這邊切出來的正文段序
# 必須跟 reader 那邊一模一樣，否則整欄錯位而畫面上看不出來。
FOOTNOTE_SEP = re.compile(r"^[—－\-]{15,}$")
HEADING = re.compile(r"^#{1,4}\s")
LEADING_NO = re.compile(r"^(\d+)\.\s")


def split_body(md: str) -> list[str]:
    """取正文段（丟掉註釋區）。分隔線切換正文／註釋，標題行重置回正文。"""
    body: list[str] = []
    in_footnotes = False
    for p in (x.strip() for x in re.split(r"\n{2,}", md or "")):
        if not p:
            continue
        if FOOTNOTE_SEP.match(p):
            in_footnotes = not in_footnotes
            continue
        if HEADING.match(p):
            in_footnotes = False
            body.append(p)
            continue
        if not in_footnotes:
            body.append(p)
    return body


def align_by_paragraph_number(body: list[str], book: int | None,
                              paragraphs: dict[tuple[int | None, int], str]
                              ) -> tuple[list[str], int, int]:
    """把原典按節號排進與 body 等長的一欄。回傳 (該欄, 命中數, 有節號的段數)。

    對不上的位置留空字串——標題、註腳、沒有節號的段落本來就沒有對應的原文。
    寧可留空也不要往下順推：順推一次，之後整欄全錯，而畫面上看起來很正常。
    """
    col = [""] * len(body)
    hit = numbered = 0
    for i, p in enumerate(body):
        m = LEADING_NO.match(p)
        if not m:
            continue
        numbered += 1
        text = paragraphs.get((book, int(m.group(1))))
        if text:
            col[i] = text
            hit += 1
    return col, hit, numbered


# ── 覆蓋率閘 ────────────────────────────────────────────────────────────────
@dataclass
class Coverage:
    book: int | None
    ours: set[int]
    theirs: set[int]

    @property
    def missing(self) -> list[int]:
        """原典有、站上沒有的章 —— 站上的中英譯就缺這幾章。"""
        return sorted(self.theirs - self.ours)

    @property
    def extra(self) -> list[int]:
        """站上有、原典沒有的章 —— 多半是章節解析錯了，別硬接。"""
        return sorted(self.ours - self.theirs)

    @property
    def ok(self) -> bool:
        return not self.missing and not self.extra


def coverage(spans: list[Span], original: dict[tuple[int | None, int], str]
             ) -> list[Coverage]:
    """逐卷比對站上章節與原典章節。回傳每一卷一筆，照卷次排序。"""
    ours: dict[int | None, set[int]] = {}
    for s in spans:
        ours.setdefault(s.book, set()).update(s.chapters())
    theirs: dict[int | None, set[int]] = {}
    for book, chap in original:
        theirs.setdefault(book, set()).add(chap)
    books = sorted(set(ours) | set(theirs), key=lambda b: (b is None, b))
    return [Coverage(b, ours.get(b, set()), theirs.get(b, set())) for b in books]


# ── 組裝 ──────────────────────────────────────────────────────────────────
# 對照欄按索引 zip，而 reader 重建欄位時會丟掉空白段（見 lib/multilang-sources.ts
# 的 BLANK_PARAGRAPH）。所以沒有對應原文的位置要放這個佔位符，不能放空字串。
BLANK_PARAGRAPH = "​"


def render_column(col: list[str]) -> str:
    """把對齊好的一欄接成 reader 讀得回同樣段序的字串。"""
    return "\n\n".join(p if p else BLANK_PARAGRAPH for p in col)


def build_sources(existing: dict | None, source_text: str | None,
                  source_lang: str | None, original: str | None,
                  original_lang: str) -> tuple[dict[str, str], list[str]]:
    """算出這一段的 sources 與欄序。欄序照使用者要的「中文 英文 原文」：

    content 永遠是繁中（reader 的主欄），所以 source_order 是 [英, 原]。
    既有的 sources 一律保留，只補原文那一欄。
    """
    sources = dict(existing or {})
    if not sources and source_text and source_lang:
        sources[source_lang] = source_text
    if original:
        sources[original_lang] = original
    order = [k for k in ("en", original_lang) if k in sources]
    order += [k for k in sources if k not in order]
    return sources, order
