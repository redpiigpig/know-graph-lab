# -*- coding: utf-8 -*-
"""avesta_fetch.py 的解析層測試。

這支管線最危險的錯不是抓不到，是**抓到錯的東西而版面完全正常**：
腳註被當成經文、節號往下錯位一格。以下每一條都是釘住那類錯誤的。
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from avesta_fetch import (  # noqa: E402
    build_chapter,
    parse_sbe_chapter,
    parse_translit_book,
    strip_tags,
    BOOKS,
)


# ────────────────── 英譯：經文欄與腳註欄必須分開 ──────────────────

SBE_PAGE = """
<TABLE>
<TR>
<TD VALIGN=TOP>
1.<SUP>1</SUP> Ahura Mazda spake unto Spitama Zarathushtra, saying:
<P>
I have made every land dear to its people.
<TD CLASS="NOTE">
   <B>Notes:</B>
   <P>
   1. Or Spitamide. Zarathushtra was descended from Spitama.
   <P>
   2. 'Everyone fancies that the land where he was born is the best.'
</TD>
</TR>
<TR>
<TD VALIGN=TOP>
2.<SUP>4</SUP> The first of the good lands which I, Ahura Mazda, created,
was the Airyana Vaeja<SUP>5</SUP>.
<TD CLASS="NOTE">
   <B>Notes:</B>
   <P>
   4. See Vd3.36 ff.
</TD>
</TR>
</TABLE>
"""


def test_footnotes_never_become_verses():
    """腳註欄的『1. Or Spitamide...』絕不可變成第 1 節。

    這是本管線的頭號陷阱：兩欄的段落都長成「N. 某某」，
    整頁抓下來再找數字的話，第 1 節會被註解蓋掉而看不出異狀。
    """
    verses = parse_sbe_chapter(SBE_PAGE)
    assert sorted(verses) == [1, 2]
    assert "Ahura Mazda spake" in verses[1]
    assert "Spitamide" not in verses[1]
    assert "Everyone fancies" not in verses[1]
    assert "See Vd3.36" not in verses[2]


def test_verse_text_keeps_continuation_paragraphs():
    verses = parse_sbe_chapter(SBE_PAGE)
    assert "I have made every land dear" in verses[1]


def test_superscript_note_markers_are_dropped_not_inlined():
    """<SUP>5</SUP> 是註號。留著會變成正文裡的裸數字，下游切節時被當成節號。"""
    verses = parse_sbe_chapter(SBE_PAGE)
    assert "Airyana Vaeja." in verses[2]
    assert "5" not in verses[2]


def test_strip_tags_removes_html_comments():
    # avesta.org 每頁夾著 <!-- p. 4, ... --> 的頁碼註解
    assert "p. 4" not in strip_tags("abc <!-- p. 4, Joseph H. Peterson --> def")


# ────────────────── 轉寫：章、節都不可錯位 ──────────────────

def v(chapter: dict, n: int) -> str:
    """轉寫的鍵是 (起, 訖) 區間——單節即 (n, n)。見 _parse_definition_list。"""
    return chapter[(n, n)]


TRANSLIT_PAGE = """
<A NAME="chapter1"></A>Fargard 1.
1 mraot ahur&ocirc; mazd&aring; spitam&acirc;i zarathushtr&acirc;i.
2 paoir&icirc;m asangh&atilde;mca sh&ocirc;ithran&atilde;mca vahishtem.
3 dasa avathra m&aring;ngh&ocirc; zayana dva h&atilde;mina.
<A NAME="chapter2"></A>Fargard 2.
1 peresat zarathushtr&ocirc; ahurem mazd&atilde;m.
2 &acirc;at mraot ahur&ocirc; mazd&aring;.
"""


def test_chapters_split_on_anchors():
    book = parse_translit_book(TRANSLIT_PAGE)
    assert sorted(book) == [1, 2]
    assert sorted(book[1]) == [(1, 1), (2, 2), (3, 3)]
    assert sorted(book[2]) == [(1, 1), (2, 2)]


def test_chapter_heading_not_swallowed_into_first_verse():
    book = parse_translit_book(TRANSLIT_PAGE)
    assert not v(book[1], 1).startswith("Fargard")
    assert v(book[1], 1).startswith("mraot")


def test_entities_are_decoded():
    book = parse_translit_book(TRANSLIT_PAGE)
    assert "ahurô mazdå" in v(book[1], 1)
    assert "&ocirc;" not in v(book[1], 1)


def test_verse_numbers_must_increase():
    """節號倒退代表那不是節號（頁碼、註記）。倒退的一段併回上一節，不開新節。"""
    page = '<A NAME="chapter1"></A>Fargard 1.\n1 alpha 2 beta 1 gamma 3 delta\n'
    book = parse_translit_book(page)
    assert sorted(book[1]) == [(1, 1), (2, 2), (3, 3)]
    # 「1 gamma」不可另開一節、也不可蓋掉第 1 節
    assert v(book[1], 1) == "alpha"
    assert "gamma" in v(book[1], 2)


# ────────────────── 對齊：不齊就留空，絕不硬湊 ──────────────────

def test_misaligned_verses_leave_blanks_instead_of_shifting():
    """兩邊節數不同時，若按序號硬配對，整章會往下錯一格而完全看不出來。"""
    spec = BOOKS["vendidad"]
    en = {1: "one", 2: "two", 4: "four"}
    orig = {1: "yek", 2: "do", 3: "se"}
    doc = build_chapter(spec, 1, en, orig)

    by_ref = {s["ref"]: s for s in doc["segments"]}
    assert sorted(by_ref) == ["Vd 1.1", "Vd 1.2", "Vd 1.3", "Vd 1.4"]
    # 第 3 節只有轉寫、第 4 節只有英譯——各自入位，不互相頂替
    assert by_ref["Vd 1.3"]["en"] == ""
    assert by_ref["Vd 1.3"]["orig"] == "se"
    assert by_ref["Vd 1.4"]["en"] == "four"
    assert by_ref["Vd 1.4"]["orig"] == ""


def test_built_chapter_matches_reader_contract():
    spec = BOOKS["vendidad"]
    doc = build_chapter(spec, 3, {1: "a"}, {1: "b"})
    assert doc["slug"] == "vendidad-03"        # 兩位數補零，對得上書目 slug
    assert doc["siglum"] == "Vd 3"
    assert doc["canon"] == "avestan"
    assert doc["volume"] == "vendidad"
    # 舊式羅馬轉寫：站上據此不開阿維斯陀字母切換
    assert doc["orig_scheme"] == "geldner-roman"
    assert doc["pivot"] == "sbe-eng"
    assert doc["segments"][0]["zh"] == ""      # 中文欄留待翻譯，不可先填英文


@pytest.mark.parametrize("chap,expected", [(1, "vendidad-01"), (22, "vendidad-22")])
def test_slug_zero_padding(chap, expected):
    # 書目那邊用 String(n).padStart(2,'0')；兩邊不一致的話 reader 就走不到正文，
    # 而書目頁照樣顯示——典型的「看起來成功的失敗」。
    assert build_chapter(BOOKS["vendidad"], chap, {1: "a"}, {})["slug"] == expected


# ────────── 回歸：第一版真的踩到的兩個「看起來成功的失敗」 ──────────

def test_one_cell_may_hold_many_verses():
    """一格裝好幾節。只取每格第一節的話，第 4 章 55 節只會抓到 30 節。

    2026-09-06 首次抓取實際發生：頁面完全正常，沒有任何地方看得出少了 25 節。
    """
    page = """
    <TR><TD VALIGN=TOP>
    23. first verse text
    <P>
    24. second verse text
    <P>
    25. third verse text
    <TD CLASS="NOTE"><B>Notes:</B><P>23. a footnote that must not become a verse.
    </TD></TR>
    """
    verses = parse_sbe_chapter(page)
    assert sorted(verses) == [23, 24, 25]
    assert verses[23] == "first verse text"
    assert verses[25] == "third verse text"
    assert "footnote" not in verses[23]


def test_roman_numeral_section_headers_are_not_glued_onto_verses():
    """『I.』『Ia.』這種小標自成一格，不可被當成前一節的續段。"""
    page = """
    <TR><TD VALIGN=TOP>1. the first verse.</TD></TR>
    <TR><TD VALIGN=TOP>Ia.</TD></TR>
    <TR><TD VALIGN=TOP>2. the second verse.</TD></TR>
    """
    verses = parse_sbe_chapter(page)
    assert verses[1] == "the first verse."
    assert "Ia." not in verses[1]


def test_chapters_without_anchors_are_still_found():
    """第 10 章以後只有『Fargard N.』標題、沒有 anchor。

    2026-09-06 首次抓取實際發生：只認 anchor 導致第 10–22 章原文整段消失，
    而書目頁與 reader 都照常顯示，只是原文欄空著。
    """
    page = (
        '<A NAME="chapt9"></A><DL><DT>1<DD>alpha<DT>2<DD>beta</DL>'
        '<H3>Fargard 10.</H3><DL><DT>1<DD>gamma<DT>2<DD>delta</DL>'
        '<H3>Fargard 11.</H3><DL><DT>1<DD>epsilon</DL>'
    )
    book = parse_translit_book(page)
    assert sorted(book) == [9, 10, 11]
    assert v(book[10], 1) == "gamma"
    assert v(book[11], 1) == "epsilon"


def test_cross_reference_in_body_does_not_split_a_chapter():
    """正文或註解裡的「參 Fargard 13」不是章界。

    若把它當章界，第 12 章會從互見處被攔腰截斷——而頁面照常顯示，
    只是後半節不見了。故章題只認 <H1>–<H4> 標籤內的。
    """
    page = (
        '<H3 id=chapt12>Fargard 12.</H3>'
        '<DL><DT>1<DD>alpha<DT>2<DD>compare Fargard 13. and see</DL>'
        '<H3 id=chapt13>Fargard 13.</H3><DL><DT>1<DD>beta</DL>'
    )
    book = parse_translit_book(page)
    assert sorted(book) == [12, 13]
    assert sorted(book[12]) == [(1, 1), (2, 2)]   # 第 2 節沒有被互見切掉
    assert v(book[13], 1) == "beta"


def test_definition_list_verses_with_and_without_period():
    """同一份檔案裡 <DT>1 與 <DT>1. 兩種寫法混用，兩種都要解得出來。

    2026-09-06 首次抓取實際發生：只認不帶句點的，第 17、18 章原文全空、
    第 12 章只剩 3 節，而書目與 reader 都照常顯示。
    """
    page = (
        '<H3 id=chapt16>Fargard 16.</H3><DL COMPACT><DT>1 <DD>no period here</DL>'
        '<H3 id=chapt17>Fargard 17.</H3><DL COMPACT><DT>1. <DD>with period here'
        '<DT>2. <DD>second</DL>'
    )
    book = parse_translit_book(page)
    assert v(book[16], 1) == "no period here"
    assert sorted(book[17]) == [(1, 1), (2, 2)]
    assert v(book[17], 1) == "with period here"


def test_chapter_marks_do_not_double_count_anchor_and_heading():
    """同一章既有 anchor 又有標題時只能算一次，否則會切出空章。"""
    page = '<A NAME="chapter1"></A>Fargard 1.\n1 alpha 2 beta\n<A NAME="chapter2"></A>Fargard 2.\n1 gamma\n'
    book = parse_translit_book(page)
    assert sorted(book) == [1, 2]
    assert v(book[1], 1) == "alpha"
    assert v(book[2], 1) == "gamma"


def test_verse_ranges_in_transliteration():
    """<DT>3-4 是節號區間，不是壞資料。

    2026-09-06 首次抓取實際發生：只認純數字，第 12 章 13 個條目裡的 10 個區間
    整條被跳過，只剩 3 節而頁面照樣顯示。
    """
    page = (
        '<H3 id=chapt12>Fargard 12.</H3>'
        '<DL COMPACT><DT>1<DD>alpha<DT>3-4<DD>beta gamma<DT>22-24<DD>omega</DL>'
    )
    book = parse_translit_book(page)
    assert sorted(book[12]) == [(1, 1), (3, 4), (22, 24)]
    assert book[12][(3, 4)] == "beta gamma"


def test_range_absorbs_the_english_verses_it_spans():
    """轉寫的一段涵蓋英譯數節時，那幾節併成同一列，不可各自留下孤兒列。"""
    spec = BOOKS["vendidad"]
    en = {1: "one", 3: "three", 4: "four", 5: "five"}
    orig = {(1, 1): "yek", (3, 4): "se-chahar"}
    doc = build_chapter(spec, 12, en, orig)

    refs = [s["ref"] for s in doc["segments"]]
    assert refs == ["Vd 12.1", "Vd 12.3-4", "Vd 12.5"]

    merged = doc["segments"][1]
    assert merged["orig"] == "se-chahar"
    assert merged["en"] == "three\nfour"     # 兩節英譯併入同一列
    assert merged["verse"] == "3-4"

    # 區間外的英譯節照常自成一列，原文欄留空而不是硬塞
    assert doc["segments"][2]["en"] == "five"
    assert doc["segments"][2]["orig"] == ""
