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


# ── 希臘原典（Migne PG 的 OCR 稿）───────────────────────────────────────────
GREEK = """ΛΟΓΟΣ ΠΡΩΤΟΣ.

[362] ΤΑΔΕ ΕΝΕΣΤΙΝ ΕΝ ΤΩ ΠΡΩΤΩ ΛΟΓΩ.
α΄. Βασίλειος ὁ πάντας ὑπερβαλλόμενος.
β΄. Ἡ ὁμόνοια Βασιλείου καὶ Χρυσοστόμου.

α΄. Ἐμοὶ πολλοὶ μὲν ἐγένοντο φίλοι γνήσιοί τε καὶ ἀληθεῖς
καὶ τοὺς τῆς φιλίας νόμους εἰδότες.
β΄. Ἦν δὲ καὶ ἕτερα πολλὰ τὰ συνάγοντα ἡμᾶς.

ΛΟΓΟΣ ΔΕΥΤΕΡΟΣ.

α΄. Ὅτι μὲν οὖν ἔστιν ἀπάτῃ χρήσασθαι καλῶς.
"""


def test_greek_numeral():
    assert fo.greek_numeral("α") == 1
    assert fo.greek_numeral("ς") == 6
    assert fo.greek_numeral("ια") == 11
    assert fo.greek_numeral("x") is None


def test_parse_greek_sections_skips_table_of_contents():
    """每卷正文前的目錄也是 α΄ β΄ γ΄。不濾掉就會拿目錄的一行摘要當整節原文，
    而三欄照樣排得整整齊齊——最難察覺的那種錯。"""
    got = fo.parse_greek_sections(GREEK)
    assert set(got) == {(1, 1), (1, 2), (2, 1)}
    assert got[(1, 1)].startswith("Ἐμοὶ πολλοὶ")     # 正文，不是目錄那行
    assert "ὑπερβαλλόμενος" not in got[(1, 1)]


def test_parse_greek_sections_keeps_continuation_lines():
    assert "νόμους εἰδότες" in fo.parse_greek_sections(GREEK)[(1, 1)]


def test_parse_greek_sections_reads_book_ordinals():
    got = fo.parse_greek_sections(GREEK)
    assert got[(2, 1)].startswith("Ὅτι μὲν οὖν")


def test_greek_sections_feed_the_existing_paragraph_aligner():
    """希臘節號與中英譯的 1. 2. 是同一套編次，所以直接餵既有的逐節對齊器。"""
    body = ["## 第一卷", "1. 我有許多真誠而忠實的友人…", "2. 除此之外…"]
    paras = fo.parse_greek_sections(GREEK)
    col, hit, numbered = fo.align_by_paragraph_number(body, 1, paras)
    assert (hit, numbered) == (2, 2)
    assert col[1].startswith("Ἐμοὶ πολλοὶ")


def test_join_crops_removes_overlap_at_the_seam():
    """上下兩半刻意留重疊（免得切在字行中間弄丟一行），接稿時要把重複的去掉。"""
    top = "alpha\nbeta\ngamma"
    bottom = "beta\ngamma\ndelta"
    assert fo.join_crops([top, bottom]).split("\n") == ["alpha", "beta", "gamma", "delta"]


def test_join_crops_keeps_distinct_text():
    assert fo.join_crops(["a\nb", "c\nd"]).split("\n") == ["a", "b", "c", "d"]


GREEK_WITH_RUNNING_HEAD = """[362] ΤΑΔΕ ΕΝΕΣΤΙΝ ΕΝ ΤΩ ΠΡΩΤΩ ΛΟΓΩ.
α΄. Βασίλειος ὁ πάντας ὑπερβαλλόμενος.
β΄. Ἡ ὁμόνοια Βασιλείου.

α΄. Ἐμοὶ πολλοὶ μὲν ἐγένοντο φίλοι.
β΄. Καὶ ἕτερα δὲ πρὸς τούτοις.
ΛΟΓΟΣ Α΄.
γ΄. Ἐπειδὴ δὲ ἔδει τὸν μακάριον.

ΤΑΔΕ ΕΝΕΣΤΙΝ ΕΝ ΤΩ ΔΕΥΤΕΡΩ ΛΟΓΩ.
α΄. Ὅτι ἔστιν ἀπάτῃ χρήσασθαι.

α΄. Ὅτι μὲν οὖν ἔστιν ἀπάτῃ χρήσασθαι καλῶς, τοσοῦτον.
"""


def test_book_number_comes_from_the_toc_heading():
    """書名頁的 ΛΟΓΟΣ ΠΡΩΤΟΣ 常被 OCR 拆成殘行，卷號整個掉了；目錄標題那一行
    「ΕΝ ΤΩ ΠΡΩΤΩ ΛΟΓΩ」才是可靠的卷號來源。"""
    assert fo.toc_book_number("ΤΑΔΕ ΕΝΕΣΤΙΝ ΕΝ ΤΩ ΠΡΩΤΩ ΛΟΓΩ.") == 1
    assert fo.toc_book_number("ΤΑΔΕ ΕΝΕΣΤΙΝ ΕΝ ΤΩ ΔΕΥΤΕΡΩ ΛΟΓΩ.") == 2
    got = fo.parse_greek_sections(GREEK_WITH_RUNNING_HEAD)
    assert (1, 1) in got and (2, 1) in got
    assert got[(1, 1)].startswith("Ἐμοὶ")
    assert got[(2, 1)].startswith("Ὅτι μὲν οὖν")


def test_running_head_does_not_split_a_book():
    """正文中間的書眉 ΛΟΓΟΣ Α΄ 若被當成換卷，那一卷會被切碎、只留最後一段。"""
    got = fo.parse_greek_sections(GREEK_WITH_RUNNING_HEAD)
    assert {n for (b, n) in got if b == 1} == {1, 2, 3}


def test_section_numbers_must_stay_in_sequence():
    """普通希臘字後面接撇號會長得像節號。σ΄ 若照收就會冒出「第 200 節」。"""
    text = "α΄. πρῶτον\nσ΄ τι δὴ τοῦτο λέγω\nβ΄. δεύτερον\n"
    got = fo.parse_greek_sections(text)
    assert set(got) == {(None, 1), (None, 2)}
    assert "τι δὴ τοῦτο" in got[(None, 1)]      # 當成第 1 節的內文接下去


def test_ocr_may_drop_a_section_and_the_next_still_lands():
    """OCR 偶爾漏掉一個節號（ς΄ 最常漏）。往下跳兩節之內仍要收，否則後面全丟。"""
    got = fo.parse_greek_sections("α΄. ενα\nβ΄. δυο\nδ΄. τεσσερα\n")
    assert set(got) == {(None, 1), (None, 2), (None, 4)}


# ── 行首羅馬章號（特土良全集那一系）─────────────────────────────────────────
TERT = """Tertullian: Apology

TERTULLIANI APOLOGETICUM

I. [1] Si non licet vobis, Romani imperii antistites, in aperto et edito.
[2] Nihil de causa sua deprecatur, quia nec de condicione miratur.

II. [1] Si certum est nos nocentissimos esse.

III. [1] Quid quod ita plerique clausis oculis in odium eius impingunt.

The Latin Library
"""


def test_parse_chapter_markers():
    got = fo.parse_chapter_markers(TERT)
    assert set(got) == {(None, 1), (None, 2), (None, 3)}
    assert got[(None, 1)].startswith("[1] Si non licet")
    assert "[2] Nihil de causa" in got[(None, 1)]      # 章內的節接在同一章
    assert got[(None, 2)].startswith("[1] Si certum")


def test_parse_chapter_markers_drops_heading_and_chrome():
    joined = "".join(fo.parse_chapter_markers(TERT).values())
    assert "APOLOGETICUM" not in joined
    assert "The Latin Library" not in joined


def test_parse_chapter_markers_rejects_out_of_sequence_numerals():
    """正文裡以大寫羅馬字母起頭又跟著句點的行（縮寫、人名）不可當成新的一章，
    否則後面的內容會被整段切走。"""
    text = "I. [1] primum\nD. Iunius Iuvenalis haec scripsit.\nII. [1] secundum\n"
    got = fo.parse_chapter_markers(text)
    assert set(got) == {(None, 1), (None, 2)}
    assert "Iuvenalis" in got[(None, 1)]               # 當成第 1 章的內文接下去


def test_roman_chapters_feed_the_chapter_aligner():
    body = ["### 第一章", "若不許你們…", "# 第二章", "倘若我們確實是…"]
    col, hit, heads = fo.align_by_chapter_heading(body, None, fo.parse_chapter_markers(TERT))
    assert (hit, heads) == (2, 2)
    assert col[0].startswith("[1] Si non licet")
    assert col[2].startswith("[1] Si certum")


# The Latin Library 的特土良同一位作者就有五種章標寫法，解析器要自己認出用哪一種。
@pytest.mark.parametrize("text,label", [
    ("I. [1] alpha\n\nII. [1] beta\n\nIII. [1] gamma\n", "行首羅馬數字後接正文"),
    ("I\n[1] alpha\n\nII\n[1] beta\n\nIII\n[1] gamma\n", "羅馬數字獨佔一行"),
    ("Capitulum I\n[1] alpha\nCapitulum II\n[1] beta\nCapitulum III\n[1] gamma\n", "Capitulum"),
    ("CAPUT 1. [1] alpha\nCAPUT 2. [1] beta\nCAPUT 3. [1] gamma\n", "CAPUT＋阿拉伯數字"),
    ("LIBER DE BAPTISMO CAP. 1. [1] alpha CAP. 2. [1] beta CAP. 3. [1] gamma", "整篇不換行"),
])
def test_chapter_markers_cover_every_house_style(text, label):
    got = fo.parse_chapter_markers(text)
    assert set(got) == {(None, 1), (None, 2), (None, 3)}, label
    assert got[(None, 1)].startswith("[1] alpha"), label
    assert "beta" not in got[(None, 1)], label      # 不可把下一章吞進來


def test_chapter_markers_do_not_swallow_the_next_marker():
    """章內文要切到「下一個章標之前」。切到之後的話，每一章都會把下一章的標記
    吞進來，畫面上看起來只是多了幾個字，實際上章與章的邊界整個錯開。"""
    got = fo.parse_chapter_markers("I. [1] alpha\n\nII. [1] beta\n")
    assert "II" not in got[(None, 1)]


def test_chapter_markers_need_at_least_two():
    assert fo.parse_chapter_markers("I. [1] only one chapter\n") == {}


# ── 多卷著作的兩種中譯編號習慣 ───────────────────────────────────────────────
def test_book_of_detects_restart():
    """《論婦女裝飾》兩卷，中譯每卷從第一章重來。"""
    assert fo.book_of([1, 2, 3, 1, 2, 3, 4]) == [1, 1, 1, 2, 2, 2, 2]


def test_book_of_keeps_one_book_when_numbering_is_continuous():
    """《駁馬吉安》五卷，中譯卻是整部連續編號 1–145，不算換卷。"""
    assert fo.book_of([1, 2, 3, 4, 5]) == [1, 1, 1, 1, 1]


def test_chapter_headings_indexes_only_readable_numbers():
    body = ["前言", "# 第一章——甲", "內文", "第二章 乙", "# 第甲章"]
    assert fo.chapter_headings(body) == [(1, 1), (3, 2)]


def test_fill_column_lands_on_the_right_slots():
    assert fo.fill_column(4, [(1, "alpha"), (3, "beta")]) == ["", "alpha", "", "beta"]


def test_chapter_markers_accept_cap_without_a_period():
    """de Ieiunio 只有第一章寫「CAP.  I.」，其餘全是「CAP II.」。硬要那個句點的
    話那一篇就只認得出第一章——而腳本只會回報命中低，看不出是格式沒對上。"""
    text = "CAP.  I.  1.  Mirarer psychicos\nCAP II.  1.  Nam quod\nCAP III.  1.  Itaque nos\n"
    got = fo.parse_chapter_markers(text)
    assert set(got) == {(None, 1), (None, 2), (None, 3)}
    assert got[(None, 2)].startswith("1.  Nam quod")


def test_cap_must_not_match_inside_a_word():
    text = "CAPTIVITAS non est caput\nI. [1] alpha\nII. [1] beta\n"
    got = fo.parse_chapter_markers(text)
    assert set(got) == {(None, 1), (None, 2)}
