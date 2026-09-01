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


# ── TEI 原典（First1KGreek）─────────────────────────────────────────────────
TEI = """<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
  <div type="textpart" subtype="epistle" n="1">
    <div type="textpart" subtype="chapter" n="praef">
      <div type="textpart" subtype="section" n="1"><p>Ἰγνάτιος τῇ ἐκκλησίᾳ</p></div>
    </div>
    <div type="textpart" subtype="chapter" n="1">
      <div type="textpart" subtype="section" n="1"><p>Ἀποδεξάμενος <note n="2">codd. AB</note> ἐν θεῷ</p></div>
      <div type="textpart" subtype="section" n="2"><p>τὸ πολυαγάπητόν σου ὄνομα</p></div>
    </div>
  </div>
  <div type="textpart" subtype="epistle" n="2">
    <div type="textpart" subtype="chapter" n="1">
      <div type="textpart" subtype="section" n="1"><p>Γνοὺς ὑμῶν τὸ πολυεύτακτον</p></div>
    </div>
  </div>
</div></body></text></TEI>"""


def test_tei_chapters_and_preface():
    got = fo.parse_tei_chapters(TEI, epistle="1")
    assert set(got) == {(None, 0), (None, 1)}      # praef 記為第 0 章
    assert got[(None, 0)].startswith("Ἰγνάτιος")


def test_tei_joins_sections_within_a_chapter():
    got = fo.parse_tei_chapters(TEI, epistle="1")
    assert "Ἀποδεξάμενος" in got[(None, 1)]
    assert "πολυαγάπητόν" in got[(None, 1)]


def test_tei_drops_the_apparatus_but_keeps_the_text_around_it():
    """<note> 是校勘註釋，留著會把手稿代號混進正文；但它後面的文字仍是正文，
    刪 note 時要把 tail 接回去，否則正文會缺一截而完全看不出來。"""
    got = fo.parse_tei_chapters(TEI, epistle="1")
    assert "codd. AB" not in got[(None, 1)]
    assert "ἐν θεῷ" in got[(None, 1)]


def test_tei_epistle_scoping():
    """七封書信裝在同一個檔裡，取錯一封就整部配到別封的內容。"""
    assert fo.parse_tei_chapters(TEI, epistle="2")[(None, 1)].startswith("Γνοὺς")
    assert fo.parse_tei_chapters(TEI, epistle="9") == {}


def test_work_name_strips_the_chapter_suffix():
    assert fo.work_name("特土良護教辭 第1-10章") == "特土良護教辭"
    assert fo.work_name("懺悔錄 卷一 第1-10章") == "懺悔錄"
    assert fo.work_name("依納爵致羅馬人書") == "依納爵致羅馬人書"


def test_work_name_keeps_variant_editions_distinct():
    """ANF 第一卷同時收了〈依納爵致以弗所人書〉與〈…（敘利亞文版）〉。敘利亞短本
    是另一個文本，用 startswith 比對就會把標準希臘本配到它身上，而三欄照樣排得
    整整齊齊——這是最難察覺的那種錯。"""
    a = fo.work_name("依納爵致以弗所人書 第1-10章")
    b = fo.work_name("依納爵致以弗所人書（敘利亞文版）")
    assert a != b


def test_work_name_strips_a_bare_book_suffix():
    """《懺悔錄》卷二整卷收成一段，路徑沒有「第N章」；卷次也要剝掉，否則那一整卷
    會被當成另一部著作而整段跳過（實測少了 16 節原文）。"""
    assert fo.work_name("懺悔錄 卷二") == "懺悔錄"
    assert fo.work_name("懺悔錄 卷十三 第31-38章") == "懺悔錄"


def test_chapter_lookup_must_carry_the_book_number():
    """《上帝之城》22 卷，每卷的章號都從一起算。查表時漏掉卷次的話，卷十三的第一
    章會拿到卷一第一章的拉丁文——命中率照樣很高、三欄照樣排得整整齊齊，內容卻是
    別一卷的。這是實際發生過的錯（539→514，而那 514 裡有一部分是錯的）。"""
    chapters = {(1, 1): "liber I caput I", (13, 1): "liber XIII caput I"}
    assert chapters.get((13, 1)) != chapters.get((1, 1))
    # 對齊器拿到 book=13 就該取卷十三那一條
    col, hit, _ = fo.align_by_chapter_heading(["# 第一章 甲"], 13, chapters)
    assert col[0] == "liber XIII caput I" and hit == 1


TEI_BOOKS = """<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
  <div type="textpart" subtype="book" n="1">
    <div type="textpart" subtype="chapter" n="1"><p>λόγος πρῶτος κεφάλαιον πρῶτον</p></div>
    <div type="textpart" subtype="chapter" n="2"><p>λόγος πρῶτος κεφάλαιον δεύτερον</p></div>
  </div>
  <div type="textpart" subtype="book" n="8">
    <div type="textpart" subtype="chapter" n="1"><p>λόγος ὄγδοος κεφάλαιον πρῶτον</p></div>
  </div>
</div></body></text></TEI>"""


def test_tei_keys_carry_the_book_number():
    """《駁塞爾蘇斯》八卷的章號各自從一起算。只用章號當鍵的話八卷互相覆蓋，
    每一卷都會拿到第八卷的內容——命中率照樣滿分，三欄照樣排得整整齊齊。"""
    got = fo.parse_tei_chapters(TEI_BOOKS)
    assert set(got) == {(1, 1), (1, 2), (8, 1)}
    assert got[(1, 1)].startswith("λόγος πρῶτος")
    assert got[(8, 1)].startswith("λόγος ὄγδοος")


def test_tei_without_a_book_level_keys_on_none():
    """伊格那丟、革利免那些單卷著作沒有 book 這一層，卷次留 None。"""
    assert set(fo.parse_tei_chapters(TEI, epistle="2")) == {(None, 1)}


def test_dedupe_ledger_keeps_the_last_write():
    """OCR 帳本是 append-only，兩個程序同時跑會各寫一列同一個裁切（實際發生過）。
    不去重的話那幾塊的原文會被接兩遍——同一段話講兩次，通順、看不出錯。"""
    rows = [
        {"page": 144, "crop": "c1h1", "text": "舊"},
        {"page": 145, "crop": "c0h0", "text": "甲"},
        {"page": 144, "crop": "c1h1", "text": "新"},
    ]
    got = fo.dedupe_ledger(rows)
    assert len(got) == 2
    assert {(r["page"], r["crop"]): r["text"] for r in got}[(144, "c1h1")] == "新"


TEI_SECTION_ONLY = """<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body>
<div type="edition">
  <div type="textpart" subtype="book" n="1">
    <div type="textpart" subtype="section" n="1"><p>Εὔστομον μὲν γλῶσσαν</p></div>
    <div type="textpart" subtype="section" n="2"><p>Καὶ σὺ μὲν λέγεις</p></div>
  </div>
  <div type="textpart" subtype="book" n="2">
    <div type="textpart" subtype="section" n="1"><p>Ἀχρεῖος μὲν ἡ πρόσφατος</p></div>
  </div>
</div></body></text></TEI>"""


def test_tei_falls_back_to_section_when_there_is_no_chapter_level():
    """提阿非羅《致奧托呂庫書》那份 TEI 只有 book/section 兩層。硬找 chapter 會
    解析出 0 章，而腳本只回報「命中 0」——看起來像取源壞掉，其實是層級名不同。"""
    got = fo.parse_tei_chapters(TEI_SECTION_ONLY)
    assert set(got) == {(1, 1), (1, 2), (2, 1)}
    assert got[(1, 1)].startswith("Εὔστομον")
    assert got[(2, 1)].startswith("Ἀχρεῖος")


def test_tei_prefers_chapter_over_section_when_both_exist():
    """兩層都有時要用 chapter（較粗的那層），section 是章內的細分。"""
    got = fo.parse_tei_chapters(TEI_BOOKS)
    assert set(got) == {(1, 1), (1, 2), (8, 1)}
