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
ZH_NUM = {
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8,
    "九": 9, "十": 10, "十一": 11, "十二": 12, "十三": 13, "十四": 14, "十五": 15,
    "十六": 16, "十七": 17, "十八": 18, "十九": 19, "二十": 20,
}

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
        book = ZH_NUM.get(m.group(1))
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
