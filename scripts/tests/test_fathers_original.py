# -*- coding: utf-8 -*-
"""教父卷第三欄原文的對齊核心。

回歸的是首次跑《懺悔錄》時遇到的真實情況：站上卷一只到第 18 章，原典有 20 章。
沒有覆蓋率閘的話，第 19–20 章的拉丁文會被默默併進第 18 章那一段——三欄看起來
齊，內容卻從那裡開始錯位，而畫面上看不出來。
"""
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "fathers_original", ROOT / "scripts" / "fathers_original.py")
fo = importlib.util.module_from_spec(_spec)
# @dataclass 會回頭查 sys.modules 解析型別註記，所以要先掛上去再 exec
sys.modules["fathers_original"] = fo
_spec.loader.exec_module(fo)


# ── chapter_path 解析 ───────────────────────────────────────────────────────
def test_range():
    s = fo.parse_chapter_path("懺悔錄 卷一 第1-10章")
    assert (s.book, s.first, s.last) == (1, 1, 10)


def test_single_chapter():
    s = fo.parse_chapter_path("懺悔錄 卷七 第21章")
    assert (s.book, s.first, s.last) == (7, 21, 21)


def test_en_dash_range():
    s = fo.parse_chapter_path("懺悔錄 卷十 第41–43章")
    assert (s.first, s.last) == (41, 43)


def test_whole_book_needs_chapter_count():
    """「卷二」整卷收在一段時，不知道那卷幾章就不可以猜——猜錯會接到別卷。"""
    assert fo.parse_chapter_path("懺悔錄 卷二") is None
    s = fo.parse_chapter_path("懺悔錄 卷二", chapters_in_book=10)
    assert (s.book, s.first, s.last) == (2, 1, 10)


def test_bookless_work():
    s = fo.parse_chapter_path("駁諸異端 第3章")
    assert (s.book, s.first, s.last) == (None, 3, 3)


@pytest.mark.parametrize("path", ["封面", "懺悔錄 書名頁", "奧古斯丁論其《懺悔錄》（修正錄）", ""])
def test_front_matter_unparsed(path):
    assert fo.parse_chapter_path(path) is None


# ── 原典解析 ────────────────────────────────────────────────────────────────
LATIN = """AUGUSTINI CONFESSIONUM LIBER PRIMUS

1.1.1

magnus es, domine, et laudabilis valde.

1.1.2

da mihi, domine, scire et intellegere.

1.2.3

et quomodo invocabo deum meum?
"""


def test_parse_numbered_text_keeps_paragraph_number():
    """節號一定要留著——只按章分組的話，一章十節的拉丁會全擠進同一列。"""
    got = fo.parse_numbered_text(LATIN)
    assert set(got) == {(1, 1, 1), (1, 1, 2), (1, 2, 3)}
    assert got[(1, 1, 1)].startswith("magnus es")
    assert got[(1, 2, 3)].startswith("et quomodo")


def test_parse_numbered_text_drops_heading():
    """行標之前的卷名不可以混進第一章。"""
    assert "LIBER PRIMUS" not in fo.parse_numbered_text(LATIN)[(1, 1, 1)]


def test_parse_numbered_text_drops_site_chrome():
    """頁尾導覽列位在最後一個段標之後，不擋就會被接到該卷最後一節的尾巴。"""
    txt = LATIN + "\ncommentary on 1.2.3\n\nThe Latin Library\n\nThe Classics Page\n"
    got = fo.parse_numbered_text(txt)
    assert got[(1, 2, 3)] == "et quomodo invocabo deum meum?"


def test_strip_html_keeps_line_breaks():
    assert fo.strip_html("<p>a</p><br/><p>b</p>").split() == ["a", "b"]


# ── 覆蓋率閘 ────────────────────────────────────────────────────────────────
def test_coverage_flags_missing_chapters():
    """《懺悔錄》卷一：站上到第 18 章，拉丁原典 20 章。"""
    spans = [fo.Span(1, 1, 10), fo.Span(1, 11, 18)]
    original = {(1, c): "x" for c in range(1, 21)}
    cov = fo.coverage(spans, original)[0]
    assert cov.missing == [19, 20]
    assert cov.extra == []
    assert not cov.ok


def test_coverage_clean_book():
    spans = [fo.Span(2, 1, 10)]
    cov = fo.coverage(spans, {(2, c): "x" for c in range(1, 11)})[0]
    assert cov.ok


def test_coverage_flags_extra():
    """站上多出原典沒有的章，多半是章節解析錯了。"""
    cov = fo.coverage([fo.Span(3, 1, 14)], {(3, c): "x" for c in range(1, 13)})[0]
    assert cov.extra == [13, 14]


# ── 逐節對齊 ────────────────────────────────────────────────────────────────
ZH_BODY = """# 第十一章——病患期間，母親憂慮

17. 我自幼就聽聞了永恆生命。

18. 我懇求禰，我的上帝。

——————————————————————————————

(161) 一種西方教會的聖禮。

# 第十二章——被迫而致力於學習

19. 但在我的這個童年時期。
"""


def test_split_body_drops_footnotes_keeps_headings():
    body = fo.split_body(ZH_BODY)
    assert len(body) == 5
    assert body[0].startswith("# 第十一章")
    assert body[3].startswith("# 第十二章")
    assert not any(b.startswith("(161)") for b in body)


def test_align_by_paragraph_number():
    """節號是唯一可靠的鍵：拉丁 1.11.17 對到中譯「17. …」那一段。"""
    body = fo.split_body(ZH_BODY)
    paras = {(1, 17): "audieram", (1, 18): "obsecro te", (1, 19): "sed in ista"}
    col, hit, numbered = fo.align_by_paragraph_number(body, 1, paras)
    assert (hit, numbered) == (3, 3)
    assert col == ["", "audieram", "obsecro te", "", "sed in ista"]


def test_align_leaves_gap_when_original_missing():
    """對不上就留空，絕不往下順推——順推一次之後整欄全錯而畫面看不出來。"""
    body = fo.split_body(ZH_BODY)
    col, hit, numbered = fo.align_by_paragraph_number(body, 1, {(1, 18): "obsecro te"})
    assert (hit, numbered) == (1, 3)
    assert col[1] == "" and col[2] == "obsecro te" and col[4] == ""


def test_render_column_uses_blank_placeholder():
    """空段若照原樣輸出，reader 切段時會把它丟掉，之後整欄上移一列。"""
    out = fo.render_column(["", "alpha", ""])
    assert out.split("\n\n") == [fo.BLANK_PARAGRAPH, "alpha", fo.BLANK_PARAGRAPH]


def test_by_chapter_and_by_paragraph_views():
    sections = {(1, 11, 17): "a", (1, 11, 18): "b", (1, 12, 19): "c"}
    assert fo.by_chapter(sections)[(1, 11)] == "a\n\nb"
    assert fo.by_paragraph(sections) == {(1, 17): "a", (1, 18): "b", (1, 19): "c"}


# ── sources 欄序 ────────────────────────────────────────────────────────────
def test_build_sources_order_is_en_then_original():
    sources, order = fo.build_sources(None, "English text", "en", "textus latinus", "la")
    assert order == ["en", "la"]
    assert sources == {"en": "English text", "la": "textus latinus"}


def test_build_sources_keeps_existing():
    sources, order = fo.build_sources({"en": "E", "grc": "Γ"}, None, None, "L", "la")
    assert sources["grc"] == "Γ" and sources["la"] == "L"
    assert order[0] == "en"


def test_build_sources_without_original():
    sources, order = fo.build_sources(None, "E", "en", None, "la")
    assert order == ["en"] and "la" not in sources


# ── 方括號羅馬章號（《上帝之城》《論三位一體》那一系）─────────────────────────
CIV = """Augustine: De Civitate Dei Liber I

AUGUSTINI DE CIVITATE DEI LIBER I

[Pr] Gloriosissimam ciuitatem Dei siue in hoc temporum cursu.

[I] Ex hac namque existunt inimici, aduersus quos defendenda est Dei ciuitas.

[II] Tot bella gesta conscripta sunt uel ante conditam Romam.
Interest autem plurimum, qualis sit usus.

The Latin Library
"""


def test_bracketed_chapters():
    got = fo.parse_bracketed_chapters(CIV, 1)
    assert set(got) == {(1, 0), (1, 1), (1, 2)}
    assert got[(1, 0)].startswith("Gloriosissimam")     # [Pr] 記為第 0 章
    assert got[(1, 1)].startswith("Ex hac namque")


def test_bracketed_chapter_keeps_continuation_lines():
    """沒有行標的續行屬於前一章，不可以自成一段或被丟掉。"""
    assert "Interest autem plurimum" in fo.parse_bracketed_chapters(CIV, 1)[(1, 2)]


def test_bracketed_chapter_drops_heading_and_chrome():
    got = fo.parse_bracketed_chapters(CIV, 1)
    joined = "".join(got.values())
    assert "LIBER I" not in joined
    assert "The Latin Library" not in joined


def test_roman_and_zh_numerals():
    assert fo.roman("XXI") == 21
    assert fo.roman("IV") == 4
    assert fo.roman("ABC") is None
    assert fo.zh_numeral("二十一") == 21
    assert fo.zh_numeral("一百二十三") == 123
    assert fo.zh_numeral("甲") is None


def test_align_by_chapter_heading():
    body = ["上帝之城第一卷", "# 第一章——基督名號的敵人", "蓋此塵世城邦…",
            "第二章——戰爭的慣例中…", "「垂死的普里亞摩斯…"]
    chapters = {(1, 1): "Ex hac namque", (1, 2): "Tot bella gesta"}
    col, hit, heads = fo.align_by_chapter_heading(body, 1, chapters)
    assert (hit, heads) == (2, 2)
    assert col == ["", "Ex hac namque", "", "Tot bella gesta", ""]


def test_align_by_chapter_heading_matches_headings_without_hashes():
    """中譯有時把章標題併進段落，`#` 就沒了；照樣要認得出來。"""
    col, hit, _ = fo.align_by_chapter_heading(
        ["第十二章——某某某"], 1, {(1, 12): "caput duodecimum"})
    assert hit == 1 and col[0] == "caput duodecimum"
