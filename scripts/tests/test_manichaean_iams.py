"""manichaean_iams 純解析函式測試（零 network、零 PDF）。

這支釘住的都是**實際踩過的坑**，不是假想的邊界情況。每一條的註解寫的是
「這條沒過會長什麼樣子」——因為這批錯誤的共同點是版面完全正常。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from manichaean_iams import (  # noqa: E402
    align_columns,
    choose_scheme,
    disambiguate_refs,
    find_fragment_siglum,
    find_locator,
    find_siglum_heading,
    group_words_into_lines,
    is_running_head,
    line_text,
    split_line,
    split_numbered,
)


def word(x0: float, y0: float = 0.0, text: str = "w") -> tuple:
    """造一個 PyMuPDF words 格式的詞：(x0, y0, x1, y1, text, block, line, word)。"""
    return (x0, y0, x0 + 8, y0 + 10, text, 0, 0, 0)


# ────────────────────────── 切欄 ──────────────────────────

class TestSplitLine:
    def test_left_column_body(self):
        assert split_line([word(89.8, 0, "a"), word(120, 0, "b")]) == ("", "a b", "")

    def test_right_column_body(self):
        assert split_line([word(302.9, 0, "A"), word(340, 0, "B")]) == ("", "", "A B")

    def test_two_columns_on_one_line(self):
        # 🚨 這條沒過＝英譯被塞進原文欄，每段原文後面黏著自己的英譯，版面完全正常。
        full, left, right = split_line([word(89.8, 0, "orig"), word(302.9, 0, "eng")])
        assert (full, left, right) == ("", "orig", "eng")

    def test_centred_heading_spanning_gutter(self):
        # 置中標題橫跨欄界。誤判成兩欄會把標題切成兩半分別混進兩欄。
        full, left, right = split_line([word(181.5, 0, "THE"), word(320, 0, "GOSPEL")])
        assert full == "THE GOSPEL"
        assert (left, right) == ("", "")

    def test_indented_continuation_line_stays_in_its_column(self):
        # 🚨 縮排續行既不從左緣也不從右緣起頭。第一版把它判成置中標題，
        #    於是整行原文被丟掉（「| bryd | qwn<y>d」就是這樣消失的）。
        assert split_line([word(150, 0, "x"), word(200, 0, "y")]) == ("", "x y", "")

    def test_indented_continuation_in_right_column(self):
        assert split_line([word(360, 0, "x"), word(420, 0, "y")]) == ("", "", "x y")


class TestGroupWordsIntoLines:
    def test_groups_by_y_and_sorts_by_x(self):
        words = [word(302.9, 10, "B"), word(89.8, 10, "A"), word(89.8, 40, "C")]
        lines = group_words_into_lines(words)
        assert [[w[4] for w in ln] for ln in lines] == [["A", "B"], ["C"]]

    def test_tolerates_small_y_jitter(self):
        # 同一行的詞 y 值常差一兩點；容差太小會把一行拆成好幾行。
        lines = group_words_into_lines([word(90, 10.0, "a"), word(120, 11.5, "b")])
        assert len(lines) == 1

    def test_empty(self):
        assert group_words_into_lines([]) == []


def test_line_text_joins_with_single_space():
    assert line_text([word(1, 0, "a"), word(3, 0, "b")]) == "a b"


# ────────────────────────── 對齊鍵 ──────────────────────────

class TestChooseScheme:
    def test_line_numbers(self):
        assert choose_scheme("1/ a 2/ b", "1/ A 2/ B") == "line"

    def test_section_markers(self):
        assert choose_scheme("{a.5} x {v.1} y", "t {a.5} X {v.1} Y") == "section"

    def test_bracket_locators(self):
        left = "[M17 V/i] aa [So18151 R] bb"
        right = "[M17 V/i] AA [So18151 R] BB"
        assert choose_scheme(left, right) == "locator"

    def test_marker_present_in_only_one_column_is_refused(self):
        # 🚨 最重要的一條。原文欄的 |5 |10 行號英譯欄沒有；拿它當鍵會讓
        #    英譯整個落進第一段，而段數看起來正常、對齊零衝突。
        assert choose_scheme("|5 plain |10 more", "plain English text") is None

    def test_single_shared_marker_is_not_enough(self):
        # 只有一個共同標記無法證明體例；門檻設 2。
        assert choose_scheme("1/ a", "1/ A") is None


class TestSplitNumbered:
    def test_line_scheme(self):
        assert split_numbered("1/ alpha 2/ beta") == [("1", "alpha"), ("2", "beta")]

    def test_letter_suffix_not_dropped(self):
        # 🚨 漏認字母尾碼＝帶字母的行被併進前一行，而行數看起來仍然很多。
        assert split_numbered("lead 4b/ x 5a/ y") == [("", "lead"), ("4b", "x"), ("5a", "y")]

    def test_section_scheme(self):
        assert split_numbered("{a.5} fifth {v.1} first", "section") == [
            ("a.5", "fifth"), ("v.1", "first")]

    def test_no_marks_returns_whole_text(self):
        assert split_numbered("no marks here") == [("", "no marks here")]

    def test_slash_inside_locator_is_not_a_line_number(self):
        # 「M17 V/i」裡的 V/ 不是行號；誤認會在定位符中間切一刀。
        out = split_numbered("[M17 V/i] text 1/ real")
        assert out[-1] == ("1", "real")


class TestAlignColumns:
    def test_pairs_by_shared_key(self):
        segs, lo, ro = align_columns([("1", "a"), ("2", "b")], [("1", "A"), ("2", "B")])
        assert [(s["n"], s["orig"], s["en"]) for s in segs] == [
            ("1", "a", "A"), ("2", "b", "B")]
        assert (lo, ro) == ([], [])

    def test_key_missing_from_right_column_merges_not_orphans(self):
        # 🚨 英譯欄印的節號比原文欄少是常態。拿聯集當段界，2 就成了
        #    「有原文沒英譯」的孤段（沙卜爾干實測 18 段），但英譯一個字沒少，
        #    它在右欄 1 那一塊裡。併成 1–2 才是實情。
        segs, lo, ro = align_columns(
            [("1", "a"), ("2", "b"), ("3", "c")], [("1", "A"), ("3", "C")])
        assert [(s["n"], s["orig"], s["en"]) for s in segs] == [
            ("1–2", "a b", "A"), ("3", "c", "C")]
        assert lo == ["2"]

    def test_never_pairs_by_position(self):
        # 🚨 按位置配對會讓整篇往下錯一格，而兩欄都有內容、版面完全正常。
        #    兩欄沒有任何共有鍵時併成一段，仍然不做一對一配對。
        segs, _, _ = align_columns([("5", "five")], [("1", "one")])
        assert len(segs) == 1
        assert (segs[0]["orig"], segs[0]["en"]) == ("five", "one")

    def test_document_order_is_kept_not_alphabetical(self):
        # 🚨 編者的分組字母不照字母序走（實測 a→v→t，以及 z 之後才是 ac→ad→ae）。
        #    照字母序重排：每段內容都正確、段號也都在，只有順序錯——看不出來。
        pairs = [("a.5", "x"), ("v.1", "y"), ("t.1", "z")]
        segs, _, _ = align_columns(pairs, pairs)
        assert [s["n"] for s in segs] == ["a.5", "v.1", "t.1"]

    def test_unkeyed_lead_text_is_kept_and_paired(self):
        # 🚨 舊版把未編號的引言整個丟掉，代價是沙卜爾干兩欄各少一半的字，
        #    而配對率 75%、閘全過、版面正常。兩欄的引言指同一段範圍，配在一起。
        segs, _, _ = align_columns([("", "lead"), ("1", "a")], [("", "LEAD"), ("1", "A")])
        assert [(s["n"], s["orig"], s["en"]) for s in segs] == [
            ("", "lead", "LEAD"), ("1", "a", "A")]

    def test_repeated_key_on_one_page_yields_one_segment(self):
        # 🚨 同一個鍵一頁印兩次（續段重標）時，若不去重，外層迴圈會吐出兩段
        #    內容完全相同、ref 也完全相同的段落。這條沒過＝正文被複製一份。
        segs, _, _ = align_columns(
            [("4b", "x"), ("4b", "y")], [("4b", "X")])
        assert [(s["n"], s["orig"], s["en"]) for s in segs] == [("4b", "x y", "X")]

    def test_page_with_no_marks_at_all_is_not_dropped(self):
        # 沙卜爾干 pp. 31–35 一個可認的標記都沒有，整頁正文與英譯曾就此消失。
        segs, _, _ = align_columns([("", "all of it")], [("", "ALL OF IT")])
        assert [(s["n"], s["orig"], s["en"]) for s in segs] == [
            ("", "all of it", "ALL OF IT")]


class TestSectionMarkCoversMultiLetterGroups:
    def test_two_letter_group_prefix_is_recognised(self):
        # 🚨 編者用完 a–z 接的是 ac、ad、ae。寫死 [a-z]. 會讓這 18 個節號
        #    全部認不得，沙卜爾干最後六頁整頁落進引言裡被丟掉。
        assert split_numbered("{ac.1} first {ad.2} second", "section") == [
            ("ac.1", "first"), ("ad.2", "second")]


# ────────────────────────── 定位符 ──────────────────────────

class TestFindLocator:
    def test_bracketed_manuscript_id(self):
        assert find_locator("[M17 V/i] 1/ gwš wcyyhyd") == "M17 V/i"

    def test_parenthesised_with_roman_numerals(self):
        # MIK 那一系的編號中間夾羅馬數字；漏認會讓回鶻文那批全部退化成頁碼。
        assert find_locator("(MIK III 8260, verso, 001-005, Leaf 1)") == \
            "MIK III 8260, verso, 001-005, Leaf 1"

    def test_plain_text_is_not_a_locator(self):
        assert find_locator("1/ plain text") is None

    def test_editorial_restoration_brackets_are_not_locators(self):
        # 補字括號 [……] 到處都是，誤認會把每段切碎。
        assert find_locator("[……] (.)w(.)[……]") is None


class TestDisambiguateRefs:
    def test_collision_gets_the_anthology_page(self):
        # 🚨 定位符偵測稀疏＋行號每頁從 1/ 重起 ⇒ `M644 1a/` 在六頁各出現一次，
        #    六段不同的正文共用同一個引用式，而頁面完全看不出異常。
        segs = [{"ref": "M644 1a/", "_pno": 8}, {"ref": "M644 1a/", "_pno": 9}]
        assert disambiguate_refs(segs, 2) == 2
        assert [s["ref"] for s in segs] == [
            "M644 1a/ (Anth. 2 p.8)", "M644 1a/ (Anth. 2 p.9)"]

    def test_unique_refs_are_left_alone(self):
        # 引用式一旦公布就不該無故變動：只動撞名的那幾段。
        segs = [{"ref": "M172 I", "_pno": 5}, {"ref": "M644 2a/", "_pno": 8}]
        assert disambiguate_refs(segs, 2) == 0
        assert [s["ref"] for s in segs] == ["M172 I", "M644 2a/"]


class TestFindFragmentSiglum:
    def test_plain_fragment_header(self):
        assert find_fragment_siglum("M49 MP: Ed. MM ii, 307-08, Rd. §b, 31") == "M49"

    def test_roman_numeral_and_dagger(self):
        # 🚨 沒認出這一行，pp. 36–39（實際是 M2 II）會沿用前一頁的 fc/II/R/Hd：
        #    段號完整又專業，卻指向錯的抄本——比退回頁碼更糟。
        assert find_fragment_siglum(
            "[... ...] M2 II✝ Pa.: Ed. and tr. MM iii, 849-53") == "M2 II"

    def test_long_number(self):
        assert find_fragment_siglum("M61208 MP: Henning, Giants, [Col. B]") == "M61208"

    def test_body_text_has_no_fragment_header(self):
        assert find_fragment_siglum("wyspʾn šẖrʾn ncy(h)[yd] hw wsnʾd") is None

    def test_bare_siglum_without_edition_colon_is_not_a_header(self):
        # 正文裡順帶提到的編號不是片段首行；少了「語言縮寫＋冒號」就不算。
        assert find_fragment_siglum("compare M49 and M99 here") is None


class TestFindSiglumHeading:
    def test_picks_manuscript_id_heading(self):
        assert find_siglum_heading(["M49 I", "MP: MM ii, 306-07"]) == "M49 I"

    def test_prose_heading_is_not_a_siglum(self):
        assert find_siglum_heading(["What a person must do to enter the religion"]) is None

    def test_empty(self):
        assert find_siglum_heading([]) is None


class TestIsRunningHead:
    def test_book_title(self):
        assert is_running_head("Anthologia Manichaica Orientalia")

    def test_title_halves_split_by_the_gutter(self):
        # 🚨 書名頁眉被欄界切成兩半，兩半都不等於書名：左欄帶頁碼，右欄只剩後段。
        #    只認完整書名，這兩截就會黏在每頁第一段的句首。
        assert is_running_head("6 Anthologia Manichaica")
        assert is_running_head("Orientalia")
        assert is_running_head("Orientalia 35")

    def test_journal_name_in_a_citation_is_not_a_running_head(self):
        # 🚨 Orientalia 也是期刊名。全文置換會把書目裡的正文一起刪掉。
        assert not is_running_head("‘Ein manichäisches Gigantenbuch’, Orientalia J. 23")

    def test_volume_title(self):
        assert is_running_head("II. From the Manichaean Canon")

    def test_bare_page_number(self):
        assert is_running_head("42")

    def test_body_text_is_kept(self):
        # 🚨 逐行剝，不整塊丟：整塊丟會連黏在同塊裡的正文一起刪。
        assert not is_running_head("1/ gwš wcyyhyd")
