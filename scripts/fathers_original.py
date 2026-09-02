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
# 書信集的 chapter_path 是「書信 第12封」，不是「第12章」。
LETTER_PATH = re.compile(r"第(\d+)封")


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
# 章號也可能是阿拉伯數字（拉克坦提烏《論逼迫者之死》：`[1] Audivit dominus…`）。
BRACKET_CHAPTER = re.compile(r"^\[(Pr|\d{1,3}|[IVXLCDM]+)\]\s*(.*)$", re.I)
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
            token = m.group(1)
            if token.lower() == "pr":
                n = 0
            elif token.isdigit():
                n = int(token)
            else:
                n = roman(token)
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


def parse_tei_letters(xml: str) -> dict[int, list[str]]:
    """把書信集的 TEI 切成 {信件編號: [收信人, 第一段, 第二段, …]}。

    巴西流《書信集》（Perseus tlg2040.tlg004）只有 letter 這一層，信裡的分節不
    是 div 而是 <p>。NPNF 中譯的「1. 2. 3.」節號對的就是這些 <p>，所以段落順序
    本身就是鍵——也因此段數對不上時絕不能硬排，見 align_letter()。

    第 0 格放 <head>（收信人），校勘註釋一律拿掉。
    """
    from lxml import etree

    root = etree.fromstring(xml.encode("utf-8"))
    ns = {"t": "http://www.tei-c.org/ns/1.0"}
    out: dict[int, list[str]] = {}
    for div in root.xpath('.//t:div[@subtype="letter"]', namespaces=ns):
        raw = (div.get("n") or "").strip()
        if not raw.isdigit():
            continue
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
        parts = []
        for el in clone.xpath('.//*[local-name()="head" or local-name()="p"]'):
            text = " ".join(" ".join(el.itertext()).split())
            if text:
                parts.append(text)
        if parts:
            out[int(raw)] = parts
    return out


# ── Corpus Corporum 的 Migne PL（mlat.uzh.ch）─────────────────────────────────
# 蘇黎世大學把整套《拉丁教父學大全》做成了機讀的 TEI（5,277 部、8,550 萬字，
# 底本是 Open Greek and Latin 的 patrologia_latina-dev）。The Latin Library 與兩個
# 希臘 TEI 庫都沒有的拉丁教父——居普良、耶柔米書信、迦仙、安波羅修——都在裡面，
# 所以這一批不必走 PL 掃描本的自家 OCR。
#
#   目錄：https://mlat.uzh.ch/php_modules/navigate.php?load=/38/{作者}/{作品}
#   取檔：https://mlat.uzh.ch/php_modules/download.php?idno={文本 idno}&type=file-xml
#
# 🚨 這份 TEI 的 <emph> 幾乎都是 Migne 的欄號（1,123 個裡 1,113 個是純數字），
#    夾在句子中間（「Saepe <emph>1</emph> a me…」）。不剔掉的話拉丁文裡會冒出
#    一串莫名其妙的數字——讀者看得到，卻看不出那是什麼。
# 🚨 <note> 同樣要整個剔掉，但 tail 要接回去（同 parse_tei_chapters 的理由）。
NUMERIC_ONLY = re.compile(r"^\s*\d{1,4}\s*$")
CC_SECTION_HEAD = re.compile(r"^\s*(\d{1,3})\s*\.?\s*$")
CC_EPISTLE_HEAD = re.compile(r"EPISTOLA\s+([IVXLCDM]+)")


def strip_apparatus(el, numeric_emph: bool = False):
    """回傳剔掉 <note>（與純數字 <emph>）之後的純文字。

    刪節點時一定要把它的 tail 接到前一個節點上——不接的話，註釋後面那一截正文
    會跟著消失，而畫面上留下的仍是一段通順的拉丁文。
    """
    from lxml import etree

    clone = etree.fromstring(etree.tostring(el))
    targets = './/*[local-name()="note"]'
    if numeric_emph:
        targets += ' | .//*[local-name()="emph"]'
    for bad in clone.xpath(targets):
        if bad.tag.endswith("emph") and not NUMERIC_ONLY.match("".join(bad.itertext())):
            continue
        tail = bad.tail or ""
        parent, prev = bad.getparent(), bad.getprevious()
        if prev is not None:
            prev.tail = (prev.tail or "") + tail
        else:
            parent.text = (parent.text or "") + tail
        parent.remove(bad)
    return " ".join(" ".join(clone.itertext()).split())


def parse_cc_letters(xml: str) -> tuple[dict[tuple[int, int], str], list[str]]:
    """把 Corpus Corporum 的書信集 TEI 切成 {(信號, 節號): 拉丁文}。

    結構是 <div1> 一封信、<div3> 一節，節的 <head> 就是「1.」「2.」。回傳的第二
    項是逐封的自我檢查訊息，空的才算對得上。

    🚨 **信號取 div1 的順序，不取 <head> 裡的羅馬數字**——126 封的 head 寫成
       「EPISTOLA XVI.」，另外 24 封寫成「EPISTOLA XLVIII,」（逗號）或整個沒有
       head。但兩者一致與否是最好的閘：150 個 div1 逐一比對下來全部相符，
       所以順序是可信的。不符就記進 problems，寧可整封不收。

    🚨 **第一節常常沒有自己的 div3**（150 封裡有 27 封），正文落在 div1 這一層的
       <p>，而那一層的第一段是 Migne 的內容提要（argumentum，整段斜體）不是正文。
       不認出來的話每一封的第一節都會拿到提要——提要是第三人稱的拉丁散文，貼在
       第三欄讀起來完全像正文。判法是「這一段幾乎整段包在 <hi> 裡」。
    """
    from lxml import etree

    root = etree.fromstring(xml.encode("utf-8"), etree.XMLParser(recover=True))
    ns = "{http://www.tei-c.org/ns/1.0}"
    body = root.find(f".//{ns}body")
    out: dict[tuple[int, int], str] = {}
    problems: list[str] = []
    if body is None:
        return out, ["TEI 裡找不到 <body>"]
    for no, div in enumerate(body.findall(f"{ns}div1"), start=1):
        declared = None
        for head in div.findall(f"{ns}head"):
            m = CC_EPISTLE_HEAD.search(strip_apparatus(head, True).upper())
            if m:
                declared = roman_to_int(m.group(1))
                break
        if declared is not None and declared != no:
            problems.append(f"第 {no} 封的 head 自稱 EPISTOLA {declared}")
            continue
        sections: dict[int, str] = {}
        # 🚨 節不一定是 div1 的直屬子節點：有序言或問題目次的信（117、120、121）
        #    多一層 div2，只找直屬子節點的話那三封整封空著，而其餘 147 封滿分。
        for sub in div.iter(f"{ns}div3"):
            head = sub.find(f"{ns}head")
            m = CC_SECTION_HEAD.match(strip_apparatus(head, True)) if head is not None else None
            if not m:
                continue
            if head is not None:
                sub = etree.fromstring(etree.tostring(sub))
                sub.remove(sub.find(f"{ns}head"))
            sections[int(m.group(1))] = strip_apparatus(sub, True)
        if 1 not in sections:
            kept = []
            for i, para in enumerate(div.findall(f"{ns}p")):   # 只看直屬的
                whole = strip_apparatus(para, True)
                italic = sum(len("".join(h.itertext())) for h in para.findall(f"{ns}hi"))
                if i == 0 and italic > 0.8 * max(len(whole), 1):
                    continue          # Migne 的內容提要，不是正文
                if whole:
                    kept.append(whole)
            if kept:
                sections[1] = " ".join(kept)
        for n, text in sections.items():
            if text:
                out[(no, n)] = text
    return out, problems


CC_CAPUT = re.compile(r"^\s*CAPUT\s+([IVXLCDM]+|PRIM\w+)\b", re.I)


def parse_cc_chapters(xml: str) -> tuple[dict[tuple[int, int], str], list[str]]:
    """把 Corpus Corporum 的多卷著作 TEI 切成 {(卷, 章): 拉丁文}。

    結構是 <div1> 一卷、<div2> 一章，章的 <head> 寫「CAPUT II. De cingulo Monachi.」
    ——章標題留著不剔，那正是第三欄該有的東西。回傳的第二項是逐卷的檢查訊息。

    🚨 **卷次只數「真的有章的 div1」。** 序言（Praefatio）與《會談錄》的三個
       PARS 分隔頁也是 div1，但底下一章都沒有。把它們算進去的話整部的卷次會往
       後推一格——第二卷的章配到第一卷、第三卷配到第二卷，逐章排得整整齊齊而
       每一章都是隔壁卷的內容。
    """
    from lxml import etree

    root = etree.fromstring(xml.encode("utf-8"), etree.XMLParser(recover=True))
    ns = "{http://www.tei-c.org/ns/1.0}"
    body = root.find(f".//{ns}body")
    out: dict[tuple[int, int], str] = {}
    notes: list[str] = []
    if body is None:
        return out, ["TEI 裡找不到 <body>"]
    book = 0
    for div in body.findall(f"{ns}div1"):
        chapters: dict[int, str] = {}
        for sub in div.iter(f"{ns}div2"):
            head = sub.find(f"{ns}head")
            m = CC_CAPUT.match(strip_apparatus(head, True)) if head is not None else None
            if not m:
                continue
            raw = m.group(1).upper()
            n = 1 if raw.startswith("PRIM") else roman_to_int(raw)
            if n:
                chapters[n] = strip_apparatus(sub, True)
        if not chapters:
            continue
        book += 1
        head = div.find(f"{ns}head")
        label = strip_apparatus(head, True)[:46] if head is not None else "(無標題)"
        notes.append(f"卷 {book}：{len(chapters)} 章 — {label}")
        for n, text in chapters.items():
            if text:
                out[(book, n)] = text
    return out, notes



def split_restart_blocks(seq: list[tuple[int, int, int]]
                         ) -> list[list[tuple[int, int, int]]]:
    """把 [(段索引, 段內位置, 章號)] 依「章號掉回去」切成一卷一塊。"""
    out: list[list[tuple[int, int, int]]] = []
    cur: list[tuple[int, int, int]] = []
    for item in seq:
        if cur and item[2] <= cur[-1][2]:
            out.append(cur)
            cur = []
        cur.append(item)
    if cur:
        out.append(cur)
    return out


def match_blocks_by_size(zh: list[int], la: list[int]) -> list[int | None]:
    """按「章數完全相等」把中譯的每一塊配到原典的某一卷，回傳逐塊的卷次（1-based）。

    只在**保序**（前一塊配到的卷次一定在後一塊之前）且**章數一模一樣**時才算配上；
    原典的卷可以被跳過（中譯漏收整卷時會這樣）。最佳解不只一個時，只留「每個最佳
    解都指向同一卷」的那些塊，其餘回 None。

    為什麼要這麼保守：迦仙那一冊的中譯與 Migne 逐卷對不齊——《會院規章》缺了整個
    第六書，而第一、八、十一書各多一章（NPNF 把一章拆成兩章）。用章號硬對的話，
    多出來的那一章之後整卷往下錯一位，而每一章都還是同一卷、同一位作者、同一個
    題材，讀起來完全通順。章數相等是唯一擋得住這種錯位的訊號。
    """
    n, m = len(zh), len(la)
    NEG = float("-inf")
    # best[i][j] ＝ 前 i 塊用掉原典前 j 卷時，最多配上幾塊
    best = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(0, m + 1):
            skip_zh = best[i - 1][j]
            skip_la = best[i][j - 1] if j else NEG
            take = (best[i - 1][j - 1] + 1
                    if j and zh[i - 1] == la[j - 1] else NEG)
            best[i][j] = max(skip_zh, skip_la, take)
    # 回頭收集：每一塊在所有最佳解裡用過哪些卷
    used: list[set[int]] = [set() for _ in range(n)]
    seen = set()
    stack = [(n, m, best[n][m])]
    while stack:
        i, j, want = stack.pop()
        if (i, j, want) in seen or i == 0:
            continue
        seen.add((i, j, want))
        if best[i - 1][j] == want:
            stack.append((i - 1, j, want))
        if j and best[i][j - 1] == want:
            stack.append((i, j - 1, want))
        if j and zh[i - 1] == la[j - 1] and best[i - 1][j - 1] + 1 == want:
            used[i - 1].add(j)
            stack.append((i - 1, j - 1, want - 1))
    return [next(iter(u)) if len(u) == 1 else None for u in used]



CC_BARE_NO = re.compile(r"^\s*(\d{1,3})\s*\.?\s*$")


def parse_cc_paragraphs(xml: str) -> tuple[dict[tuple[int, int], str], list[str]]:
    """把 Corpus Corporum 的 TEI 切成 {(卷, 節): 拉丁文}——鍵是 Migne 的**節號**。

    與 parse_cc_chapters 的差別只在讀哪一層：Migne 的奧古斯丁同時有 CAPUT（章）與
    節號兩套編號，而 Schaff 的英譯是**按節號編章的**（《論聖靈與字句》拉丁本 36 個
    CAPUT、66 個節，NPNF 的「第 N 章」跑到 66）。拿 CAPUT 對的話前 36 章配得上、
    看起來很正常，第 37 章之後整段落空——而落空的原因看不出來。
    """
    from lxml import etree

    root = etree.fromstring(xml.encode("utf-8"), etree.XMLParser(recover=True))
    ns = "{http://www.tei-c.org/ns/1.0}"
    body = root.find(f".//{ns}body")
    out: dict[tuple[int, int], str] = {}
    notes: list[str] = []
    if body is None:
        return out, ["TEI 裡找不到 <body>"]
    book = 0
    for div in body.findall(f"{ns}div1"):
        got: dict[int, str] = {}
        for sub in div.iter(f"{ns}div3"):
            head = sub.find(f"{ns}head")
            m = CC_BARE_NO.match(strip_apparatus(head, True)) if head is not None else None
            if not m:
                continue
            clone = etree.fromstring(etree.tostring(sub))
            clone.remove(clone.find(f"{ns}head"))
            got[int(m.group(1))] = strip_apparatus(clone, True)
        if not got:
            continue
        book += 1
        head = div.find(f"{ns}head")
        label = strip_apparatus(head, True)[:46] if head is not None else "(無標題)"
        notes.append(f"卷 {book}：{len(got)} 節 — {label}")
        for n, text in got.items():
            if text:
                out[(book, n)] = text
    return out, notes


CC_ANY_NO = re.compile(r"^\s*(\d{1,3}|[IVXLCDM]{1,9})\s*\.?\s*$")


def parse_cc_work(xml: str) -> tuple[dict[tuple[int, int], str], list[str]]:
    """單一著作的 Corpus Corporum TEI → {(1, 章): 拉丁文}。章號阿拉伯或羅馬都認。

    居普良那一批的章在 <div3>（head 是「I.」「II.」），但《論行為與施捨》的章
    直接掛在 <div1>（26 個）。找不到帶編號的 div3 就退用 div1——不退的話那一部
    解析出 0 章，而腳本只回報「命中 0」，看起來像取源壞掉。
    """
    from lxml import etree

    root = etree.fromstring(xml.encode("utf-8"), etree.XMLParser(recover=True))
    ns = "{http://www.tei-c.org/ns/1.0}"
    body = root.find(f".//{ns}body")
    if body is None:
        return {}, ["TEI 裡找不到 <body>"]

    def collect(level: str) -> dict[int, str]:
        got: dict[int, str] = {}
        for sub in body.iter(f"{ns}{level}"):
            head = sub.find(f"{ns}head")
            m = CC_ANY_NO.match(strip_apparatus(head, True)) if head is not None else None
            if not m:
                continue
            raw = m.group(1)
            n = int(raw) if raw.isdigit() else roman_to_int(raw)
            if not n:
                continue
            clone = etree.fromstring(etree.tostring(sub))
            clone.remove(clone.find(f"{ns}head"))
            got[n] = strip_apparatus(clone, True)
        return got

    got = collect("div3") or collect("div1")
    if not got:
        return {}, ["div3 與 div1 都找不到帶編號的章"]
    return ({(1, n): t for n, t in got.items() if t},
            [f"卷 1：{len(got)} 章（最大 {max(got)}）"])


def both_anchors(body: list[str]) -> list[tuple[int, int]]:
    """章標題與節號合併，同一段兩種都中時以節號那一段為準。

    🚨 這個函式**只能餵單一部著作的段落**。餵一整個壓了十部著作的巨塊時，「這個
       號碼已經被別處佔用了」這條去重規則會把十七個章標題全部丟掉——它們的號碼
       都被隔壁那部著作的節號佔走了，而腳本只回報「命中 0」。
    """
    out = dict(letter_anchors(body))          # 「17. 」與獨佔一行的「## 17」
    taken = set(out.values())
    for i, n in chapter_headings(body):       # 「## 第十七章」
        if n not in taken:
            out[i] = n
    return sorted(out.items())


def split_marker_blocks(seq: list[tuple[int, int, int]],
                        marks: list[tuple[int, int]]) -> list[list[tuple[int, int, int]]]:
    """依「著作起點」把錨點序列切塊，一塊一部著作。

    `marks` 是逐部著作第一段的 (段索引, 段內位置)，已按閱讀順序排好。用在一個
    chunk 裡壓了好幾部著作的場合（居普良論述集那 14 萬字的巨塊）——那裡章號重編
    的位置**不能**當切點：十部著作的編號互相穿插，而且中譯本身就缺了兩部的正文。
    """
    blocks: list[list[tuple[int, int, int]]] = [[] for _ in marks]
    for item in seq:
        here = (item[0], item[1])
        k = -1
        for j, mark in enumerate(marks):
            if mark <= here:
                k = j
        if k >= 0:
            blocks[k].append(item)
    return blocks


def align_cc_books(seq: list[tuple[int, int, int]],
                   by_book: dict[tuple[int, int], str],
                   declared: list[int | None] | None = None,
                   numbering_verified: list[int] | None = None,
                   blocks: list[list[tuple[int, int, int]]] | None = None
                   ) -> tuple[dict[int, list[tuple[int, str]]], int, int, list[str]]:
    """多卷著作逐章對齊：中譯依章號重編切塊，一塊配原典的一卷。

    `declared` 是 spec 裡逐塊寫死、**逐塊讀過內容確認過**的卷次（None ＝ 那一塊
    不收）。沒給就退回按「章數相等且唯一」自動配。回傳 (逐段的 [(段內位置, 原文)],
    命中, 錨點數, 逐塊報告)。

    🚨 **章數相等且唯一，不代表配對正確。** 迦仙《會談錄》第三部的第一塊有 16 章，
       而原典第十八次會談有 17 章、第十九次剛好 16 章——自動配就唯一地配到第十九次
       去了，兩邊都是同一位作者的沙漠會談錄，逐章排得整整齊齊。是讀了第一章才發現
       中譯寫「我們如何來到狄奧爾科斯並受到皮阿蒙修士長的接待」而拉丁文是「論保羅
       長老的共居修院」。所以正式收的每一部都把逐塊卷次寫死在 spec 裡。

    🚨 **卷次配對正確，章號仍可能整卷錯開一位。** NPNF 的中譯把 Migne 的某一章拆成
       兩章（《會院規章》第一、八、十一書，《會談錄》第十八、二十、十三、十七次），
       多出來的那一章之後整卷往下錯一格——同一卷、同一題材，讀起來完全通順。所以
       即使 spec 指名了卷次，**章數不相等的那一塊照樣整塊留空**。
    """
    sizes: dict[int, int] = {}
    for b, n in by_book:
        sizes[b] = max(sizes.get(b, 0), n)
    order = sorted(sizes)
    if blocks is None:
        blocks = split_restart_blocks(seq)
    if declared is None:
        picks = match_blocks_by_size([len(b) for b in blocks],
                                     [sizes[b] for b in order])
    elif len(declared) != len(blocks):
        return {}, 0, len(seq), [
            f"spec 的 blocks 有 {len(declared)} 筆，中譯卻切出 {len(blocks)} 塊"
            f"（各 {[len(b) for b in blocks]} 章）——分段變了，整部不收"]
    else:
        picks = list(declared)

    # 連續幾塊指到同一卷時要合起來判：中譯偶爾會在一卷中間重複一次編號
    #（〈論伯拉糾案的審理〉第二十一章寫了兩次），切塊器因此把一卷切成兩塊，
    # 各自的最大編號都小於原典的節數，兩塊就都被判成錯開而整卷留空。
    groups: list[tuple[list[int], int | None]] = []
    for k, pick in enumerate(picks):
        if groups and groups[-1][1] == pick and pick is not None:
            groups[-1][0].append(k)
        else:
            groups.append(([k], pick))

    out: dict[int, list[tuple[int, str]]] = {}
    hit = 0
    report: list[str] = []
    for idxs, pick in groups:
        label = "塊 " + "＋".join(str(i + 1) for i in idxs)
        items = [x for i in idxs for x in blocks[i]]
        if pick is None:
            report.append(f"{label}（{len(items)} 個錨點）沒有對應的原典卷 → 留空")
            continue
        if not 1 <= pick <= len(order):
            report.append(f"{label} 指到原典卷 {pick}，但只解析出 {len(order)} 卷"
                          f"——多半是 unit 挑錯層（章在 div2 還是 div3）→ 留空")
            continue
        book = order[pick - 1]
        top = max(n for _, _, n in items)
        # 🚨 比的是「最大編號」不是「錨點個數」：中譯常有幾個章標題沒被解析出來
        #    （《論聖靈與字句》66 章只讀得出 57 個標題），拿個數比會把整部好好的
        #    著作誤判成錯開。編號本身對得上就行，讀不出標題的那幾格本來就留空。
        # 編號數對不上有兩種原因，數字上長得一模一樣：①中譯只是漏掉幾個標題、或
        # 尾巴沒收完（安全，照實留空即可）②NPNF 把一章拆成兩章／併成一章，整卷
        # 從那裡開始錯位（不安全）。所以預設一律留空；**逐章讀過首、中、末確認
        # 編號真的對得上**，才把卷次列進 numbering_verified。
        if book in (numbering_verified or []):
            report.append(f"{label}（{len(items)} 個錨點，最大 {top}）→ 原典卷 {book}"
                          f"（{sizes[book]} 節；編號已人工逐點核對）")
        elif top != sizes[book]:
            report.append(f"{label}（{len(items)} 個錨點，最大 {top}）對原典卷 {book}"
                          f"（{sizes[book]} 節）——編號對不上，整卷會錯開 → 留空")
            continue
        else:
            report.append(f"{label}（{len(items)} 個錨點，最大 {top}）→ 原典卷 {book}")
        for ci, i, n in items:
            text = by_book.get((book, n))
            if text:
                out.setdefault(ci, []).append((i, text))
                hit += 1
    return out, hit, len(seq), report



# ── 中譯自己宣告的信號 ──────────────────────────────────────────────────────
# 耶柔米那一冊的 chapter_path 從第 140 段起與內文脫節（見 SKILL.md），所以「這是
# 第幾封信」只能問內文自己。同一冊裡至少有十四種寫法：
#   第一信／信件第四封／Letter VIII./第十一函／十二、／書信第十三封／XVI./
#   第二十二封／信簡四十／信函 L./第60封信／第一三一號／信第一百四十四封／信件CL.
ZH_POSITIONAL = {"零": 0, "〇": 0, "○": 0, "一": 1, "二": 2, "三": 3, "四": 4,
                 "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
ROMAN_VALUE = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
_ZH = r"[零〇○一二三四五六七八九十百]+"
_UNIT = r"(?:封信|封|函|號|信|卷|篇|書信|簡狀)"
# 「第一三一號」是逐位寫的（131），「第一百三十一」是進位寫的。有十／百／千就是
# 後者，交給 zh_numeral；沒有就逐位讀。
LETTER_FORMS = [
    (re.compile(rf"第\s*({_ZH})\s*{_UNIT}"), "zh"),
    (re.compile(rf"第\s*({_ZH})(?![零〇○一二三四五六七八九十百章節次年日月世個位人])"), "zh"),
    (re.compile(rf"第\s*(\d{{1,3}})\s*{_UNIT}"), "int"),
    (re.compile(rf"(?:信函|書信|信札|信簡|書簡|信件|信)\s*({_ZH})(?=\s*[致論出來從自，。：:])"), "zh"),
    (re.compile(rf"({_ZH})、"), "zh"),
    (re.compile(r"(?:Letter|Epistle)\s+([IVXLCDM]+)\b"), "roman"),
    (re.compile(r"(?<![A-Za-z])([IVXLCDM]{1,9})(?![A-Za-z])"), "roman"),
]


def roman_to_int(s: str) -> int | None:
    n = 0
    for i, ch in enumerate(s):
        v = ROMAN_VALUE.get(ch)
        if v is None:
            return None
        nxt = ROMAN_VALUE.get(s[i + 1]) if i + 1 < len(s) else None
        n += -v if nxt and nxt > v else v
    return n


def positional_numeral(s: str) -> int | None:
    if any(c in s for c in "十百千"):
        return zh_numeral(s.replace("○", "〇"))
    n = 0
    for c in s:
        if c not in ZH_POSITIONAL:
            return None
        n = n * 10 + ZH_POSITIONAL[c]
    return n


def heading_region(md: str, limit: int = 60) -> str:
    """只取開頭那幾行標題。整段掃會讀到內文的交叉引用而讀成別封信。"""
    out: list[str] = []
    for line in (md or "").split("\n"):
        s = re.sub(r"\{\{?p:\d+\}?\}", "", line).strip()
        if not s:
            continue
        out.append(s.lstrip("#").strip())
        if len(" ".join(out)) > 40:
            break
    return " ".join(out)[:limit]


def declared_letter_no(md: str, ceiling: int = 150) -> int | None:
    """從中譯自己的標題讀出信號。讀不準回 None——猜不如空著。

    🚨 取「最早出現」的那個編號，不是「第一種成立的寫法」。〈書簡 LVI〉的導言
       第二句就寫著「寫給耶柔米的第一封信」，先試「第N封信」那一式會讀成第 1 封，
       而第 1 封本來就在，於是同一封拉丁文被貼到兩個地方，兩邊都通順。
    """
    head = heading_region(md)
    best: tuple[int, int] | None = None
    for pat, kind in LETTER_FORMS:
        m = pat.search(head)
        if not m:
            continue
        raw = m.group(1)
        n = (positional_numeral(raw) if kind == "zh"
             else int(raw) if kind == "int" else roman_to_int(raw))
        if n and 1 <= n <= ceiling and (best is None or m.start() < best[1]):
            best = (n, m.start())
    return best[0] if best else None


def letter_anchors(body: list[str]) -> list[tuple[int, int]]:
    """書信裡的節錨點：段首的「3. 」與獨佔一行的「## 3」兩種都算。

    耶柔米那一冊 150 封裡有 147 封用前者，第 1、3、7 封用後者——只認一種的話
    那三封整封空著，而其餘 147 封滿分，看起來像那三封本來就沒有原文。
    """
    out = dict(section_numbers(body))
    for i, p in enumerate(body):
        m = NUM_HEADING.match(p)
        if not m or i in out:
            continue
        # 「## 3」自己是一行標題、正文在下一段。原文放在標題那一格的話，中譯欄
        # 那一列只有一個「3」，而正文那一列空著——兩欄看起來就差了一列。
        at = i + 1 if i + 1 < len(body) and i + 1 not in out else i
        out[at] = int(m.group(1))
    return sorted(out.items())


NUM_HEADING = re.compile(r"^#{1,4}\s*(\d{1,3})\s*\.?\s*$")



def align_by_letter_section(body: list[str], letter: int | None,
                            sections: dict[tuple[int, int], str]
                            ) -> tuple[list[str], int, int]:
    """書信集逐節對齊：把第 letter 封的第 n 節排到中譯第 n 節那一格。"""
    col = [""] * len(body)
    hit = numbered = 0
    for i, n in letter_anchors(body):
        numbered += 1
        text = sections.get((letter, n))
        if text:
            col[i] = text
            hit += 1
    return col, hit, numbered



# 第六種行標：方括號裡是「羅馬章號＋阿拉伯節號」，同章其餘的節只寫節號。
#   [I 1] Lecturus haec quae de trinitate disserimus…
#   [2]   Vt ergo ab huiusmodi falsitatibus…
# 奧古斯丁《論三位一體》十五卷是這個樣子。
# 🚨 拿 parse_bracketed_chapters 讀會把 `[2]` 當成第二章——卷一因此變成 21 章
#    （實際 13 章），而且每一章的內容都從節的中間開始。
ROMAN_SECTION = re.compile(r"^\[([IVXLCDM]+)(?:\s+(\d+))?\]\s*(.*)$")
BARE_SECTION = re.compile(r"^\[(\d+)\]\s*(.*)$")


def parse_roman_bracketed_chapters(text: str, book: int | None = None,
                                   drop: "re.Pattern[str]" = SITE_CHROME
                                   ) -> dict[tuple[int | None, int], str]:
    """把 `[I 1] … [2] …` 這種行標的原典切成 {(卷, 章): 文字}。"""
    out: dict[int, list[str]] = {}
    current: list[str] | None = None
    for line in text.split(chr(10)):
        line = line.strip()
        if not line or drop.match(line):
            continue
        m = ROMAN_SECTION.match(line)
        if m:
            n = roman(m.group(1))
            if n is None:
                continue
            current = out.setdefault(n, [])
            if m.group(3):
                current.append(m.group(3))
            continue
        c = BARE_SECTION.match(line)
        if c:
            if current is not None and c.group(2):
                current.append(c.group(2))
            continue
        if current is not None:
            current.append(line)
    return {(book, n): chr(10).join(v).strip() for n, v in out.items() if any(v)}


def _chain(values: list[int], low: int, high: int) -> list[int]:
    """values 裡「大於 low、不超過 high、而且遞增」的最長一串（回傳選中的位置）。"""
    idx = [i for i, v in enumerate(values) if low < v <= high]
    if not idx:
        return []
    best = [1] * len(idx)
    prev = [-1] * len(idx)
    for a in range(len(idx)):
        for b in range(a):
            if values[idx[b]] < values[idx[a]] and best[b] + 1 > best[a]:
                best[a], prev[a] = best[b] + 1, b
    k = max(range(len(idx)), key=lambda i: best[i])
    out = []
    while k >= 0:
        out.append(idx[k])
        k = prev[k]
    return out[::-1]


def assign_books(chunk_anchors: list[list[int]], sizes: list[int]
                 ) -> list[tuple[int | None, list[int]]]:
    """逐段的錨點序列 → 每一段 (原典第幾卷, 用得上的錨點位置)。卷次 1-based。

    用在「中譯每卷都從第一節重新編號，而 chapter_path 完全看不出卷次」的著作。
    亞他那修《駁亞流派講辭》四篇就是這樣：站上的「第1章…第35章」只是分段序號，
    內文的節號則是 23…64、1…82、1…67、1…35 四段。

    🚨 不能靠「編號變小就是換了一卷」回頭偵測。那一部的中譯有兩段的節號重疊
       （第8章收 1–9、第9章又從 1 開始），偵測法會切出八篇而不是四篇，命中率
       掉到三成——而且錯配的那幾段看起來完全正常。

    改用原典自己給的資訊：每一卷幾節是已知的。在「同一卷內遞增、不超過該卷節數」
    這個限制下，用動態規劃找出讓最多錨點成立的切法。卷的順序不可調換，可以整卷
    沒有對應的段落。不合限制的錨點不配——重複的那幾段因此會空著，這是對的。
    """
    if not sizes:
        return [(None, []) for _ in chunk_anchors]
    states: dict[tuple[int, int], tuple] = {(0, 0): (0, None, None, [])}
    trail = []
    for anchors in chunk_anchors:
        nxt: dict[tuple[int, int], tuple] = {}
        for (b, last), (score, _, _, _) in states.items():
            for nb in range(b, len(sizes)):
                got = _chain(anchors, last if nb == b else 0, sizes[nb])
                s2 = score + len(got)
                last2 = anchors[got[-1]] if got else (last if nb == b else 0)
                key = (nb, last2)
                if key not in nxt or nxt[key][0] < s2:
                    nxt[key] = (s2, (b, last), nb if got else None, got)
        states = nxt
        trail.append(states)
    key = max(states, key=lambda k: states[k][0])
    out: list[tuple[int | None, list[int]]] = []
    for step in reversed(trail):
        _, prev, nb, got = step[key]
        out.append((None if nb is None else nb + 1, got))
        key = prev
    return out[::-1]


# 收信人自成一段時就是短短一句（「致坎迪狄亞努」）。超過這個長度表示中譯把收信
# 人與正文第一段併在一起了——356 封裡有 88 封這樣。
ADDRESS_MAX = 60


def align_letter(body: list[str], letter: list[str]) -> tuple[list[str], int, int]:
    """一封信的中譯段落 → 原文欄。只在確定的情形下填，其餘整封空著。

    🚨 這裡沒有編號可以查，只有順序，所以絕不能「大致排一排」。實測巴西流第五
       封：中譯兩節，原文四段——NPNF 的節號是本篤版的分節，Perseus 那份走的是
       更細的分段，一節等於兩三段。硬排的話第二節會配到原文第二段，往後每一段
       都錯開一格，讀起來完全通順。

    🚨 有 88 封的中譯把收信人與正文第一段併成一段。不認出來的話段數會少一段，
       而少一段有時剛好等於原文段數——整封位移一格，照樣填滿。所以先看第二段有
       多長。

    填的情形：
      · 收信人那一行 ↔ 原文的 <head>（位置固定，每封都對得上）
      · 剩下的段數剛好相等 → 逐段一對一
      · 中譯只剩一段 → 整封原文併進那一格（沒有切錯的餘地）
    """
    col = [BLANK_PARAGRAPH] * len(body)
    if not letter or len(body) < 2:
        return col, 0, 0
    head, rest = letter[0], letter[1:]
    merged = len(body[1].lstrip("# ").strip()) > ADDRESS_MAX
    if merged and rest:
        col[1] = head + chr(10) + rest[0]
        rest = rest[1:]
    else:
        col[1] = head
    zh = body[2:]
    hit = 1
    if rest and len(zh) == len(rest):
        for i, text in enumerate(rest):
            col[i + 2] = text
        hit += len(rest)
    elif rest and len(zh) == 1:
        col[2] = chr(10).join(rest)
        hit += 1
    return col, hit, len(zh) + 1


# 第四種行標：`章.節` 寫在行首、同行接正文。
#   1.1 Quoniam comperi nonnullos, qui se plurimum sapere…
#   1.2. Hoc in loco tribui si ulla facultas posset…
# 阿諾比烏《駁異教徒》那一系是這個樣子。與 LL_MARK 的差別在於標記不獨佔一行，
# 所以那支解析不到（實測七卷全部回 0 章）。
DOTTED_MARK = re.compile(
    r"^[ 	]*(?P<ch>\d{1,3})\.(?P<sec>\d{1,3})\.?\s+(?P<text>.*)$")

# 第五種：章號在行首，節號用括號夾，同行接正文。
#   1 (1) Res a mundi exordio sacris litteris editas…
# 蘇皮丘‧塞維魯《編年史》《聖瑪爾定傳》是這個樣子。
PAREN_MARK = re.compile(
    r"^[ 	]*(?P<ch>\d{1,3})\s*\((?P<sec>\d{1,3})\)\s+(?P<text>.*)$")


# 第七種：章號單獨用括號夾在行首，同行接正文。
#   (1) Inter multos saepe dubitatum est…
# 耶柔米《首位隱士保羅傳》是這個樣子。
SOLO_PAREN = re.compile(r"^[ 	]*\((?P<ch>\d{1,3})\)\s+(?P<text>.*)$")


def parse_dotted_chapters(text: str, drop: "re.Pattern[str]" = SITE_CHROME,
                          mark: "re.Pattern[str]" = DOTTED_MARK
                          ) -> dict[tuple[int | None, int], str]:
    """把 `章.節 正文` 這種行標的原典切成 {(None, 章): 文字}，同章的節接起來。

    章號必須不遞減——正文裡的年份、聖經章節引用（「2.15」）都長得像行標，一遞減
    就知道那不是章標。
    """
    out: dict[int, list[str]] = {}
    current: list[str] | None = None
    last = 0
    for line in text.split("\n"):
        line = line.strip()
        if not line or drop.match(line):
            continue
        m = mark.match(line)
        n = int(m.group("ch")) if m else None
        if n is not None and last <= n <= last + 3:
            if n != last:
                current = out.setdefault(n, [])
                last = n
            if m.group("text"):
                current.append(m.group("text"))
        elif current is not None:
            current.append(line)
    return {(None, n): "\n".join(v).strip() for n, v in out.items() if any(v)}


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


def section_numbers(body: list[str]) -> list[tuple[int, int]]:
    """回傳 [(段索引, 節號)]，取段首的「17. 」那個數字。

    與 chapter_headings() 是同一個形狀，好讓對齊器可以換著用：有些著作的錨點是
    章標題（《上帝之城》），有些是節號（亞他那修《駁亞流派講辭》——那一部整卷
    沒有可用的章標題，只有連續節號，而且每篇講辭都從一重新起算）。
    """
    out: list[tuple[int, int]] = []
    for i, p in enumerate(body):
        m = LEADING_NO.match(p)
        if m:
            out.append((i, int(m.group(1))))
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
