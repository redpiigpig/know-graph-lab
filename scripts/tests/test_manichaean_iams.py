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
    find_locator,
    find_siglum_heading,
    group_words_into_lines,
    is_running_head,
    line_text,
    split_line,
    split_numbered,
    _mark_sort_key,
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
    def test_pairs_by_key_and_leaves_gaps(self):
        segs, lo, ro = align_columns([("1", "a"), ("2", "b")], [("1", "A"), ("3", "C")])
        assert [(s["n"], s["orig"], s["en"]) for s in segs] == [
            ("1", "a", "A"), ("2", "b", ""), ("3", "", "C")]
        assert (lo, ro) == (["2"], ["3"])

    def test_never_pairs_by_position(self):
        # 🚨 按位置配對會讓整篇往下錯一格，而兩欄都有內容、版面完全正常。
        segs, _, _ = align_columns([("5", "five")], [("1", "one")])
        pairs = {s["n"]: (s["orig"], s["en"]) for s in segs}
        assert pairs["5"] == ("five", "")
        assert pairs["1"] == ("", "one")

    def test_unkeyed_lead_text_is_dropped_not_misassigned(self):
        segs, _, _ = align_columns([("", "lead"), ("1", "a")], [("1", "A")])
        assert [s["n"] for s in segs] == ["1"]


class TestMarkSortKey:
    def test_numeric_order_not_string_order(self):
        assert sorted(["10", "2", "2b", "2a"], key=_mark_sort_key) == ["2", "2a", "2b", "10"]

    def test_section_markers_group_then_number(self):
        # 🚨 字串排序會讓 a.10 排在 a.2 前面：每段內容都對，順序全錯，看不出來。
        assert sorted(["a.10", "a.2", "v.1"], key=_mark_sort_key) == ["a.2", "a.10", "v.1"]


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

    def test_volume_title(self):
        assert is_running_head("II. From the Manichaean Canon")

    def test_bare_page_number(self):
        assert is_running_head("42")

    def test_body_text_is_kept(self):
        # 🚨 逐行剝，不整塊丟：整塊丟會連黏在同塊裡的正文一起刪。
        assert not is_running_head("1/ gwš wcyyhyd")
