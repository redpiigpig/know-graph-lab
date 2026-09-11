# -*- coding: utf-8 -*-
"""ACCS 品質稽核的判準（純函式，零 I/O）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from accs_audit_quality import (  # noqa: E402
    is_blank,
    is_cross_chapter,
    range_ok,
    simplified_chars,
    uses_book_code,
    vol_matches_book,
)


class TestVolMatchesBook:
    def test_matching_volume(self):
        assert vol_matches_book("ACCS（馬太福音）", "馬太福音") is True

    def test_bleed_across_books_is_caught(self):
        # 🚨 卷別解析錯位時整段註釋掛到隔壁書，章節與經文都對得起來，
        # 只有卷名對不上——頁面上看不出任何異狀
        assert vol_matches_book("ACCS（以賽亞書）", "馬太福音", "mat") is False

    def test_book_code_form_is_not_a_mixup(self):
        # source_vol 有三種寫法混用；只認中文名會把 15,646 列誤報成混雜
        assert vol_matches_book("ACCS（gen）", "創世記", "gen") is True

    def test_deuterocanon_shares_one_volume_name(self):
        assert vol_matches_book("ACCS（次經）", "多俾亞傳", "tob", True) is True
        assert vol_matches_book("ACCS（次經）", "馬太福音", "mat", False) is False

    def test_missing_info_is_not_flagged(self):
        assert vol_matches_book("", "馬太福音") is True
        assert vol_matches_book("ACCS（馬太福音）", "") is True

    def test_multi_book_volume_still_matches(self):
        assert vol_matches_book("ACCS（十二先知書‧何西阿書）", "何西阿書") is True


class TestRangeOk:
    def test_normal(self):
        assert range_ok(3, 1, 5) is True

    def test_reversed_range_is_not_an_error(self):
        # 🚨 `bar 1:15-10` 是巴路克 1:15–2:10 的跨章概論，schema 存不下訖點在下一章。
        # 當成錯誤報，稽核會永遠紅著，真正的問題反而被淹掉。
        assert range_ok(3, 9, 2) is True
        assert is_cross_chapter(9, 2) is True

    def test_normal_range_is_not_cross_chapter(self):
        assert is_cross_chapter(1, 5) is False

    def test_negative_verse_rejected(self):
        assert range_ok(3, -1, 5) is False

    def test_chapter_zero_rejected(self):
        assert range_ok(0, 1, 2) is False

    def test_nulls_tolerated(self):
        # 概論段沒有節號是正常的
        assert range_ok(3, None, None) is True

    def test_garbage_rejected(self):
        assert range_ok("x", 1, 2) is False


class TestSimplified:
    def test_traditional_is_clean(self):
        assert simplified_chars("這是繁體中文的註釋，論及聖經與教父傳統。") == []

    def test_simplified_detected(self):
        assert "这" not in simplified_chars("這")  # 對照組
        got = simplified_chars("他们说这个问题")
        assert "们" in got and "说" in got

    def test_variant_char_not_flagged_as_simplified(self):
        # 🚨 別用 OpenCC 轉換後比對判繁簡：「祢」會被判成簡體
        assert simplified_chars("求祢垂聽") == []

    def test_dedup_and_order(self):
        assert simplified_chars("们们对") == ["们", "对"]


class TestIsBlank:
    def test_empty(self):
        assert is_blank("") is True
        assert is_blank(None) is True

    def test_punctuation_only(self):
        assert is_blank("　。、，") is True

    def test_real_text(self):
        assert is_blank("屈梭多模論此節。") is False


class TestUsesBookCode:
    def test_code_form_detected(self):
        # 頁面直接印 source_vol，這種會顯示成「ACCS（gen）‧古代基督信仰聖經註釋叢書」
        assert uses_book_code("ACCS（gen）") is True
        assert uses_book_code("ACCS（1co）") is True

    def test_chinese_name_is_fine(self):
        assert uses_book_code("ACCS（詩篇）") is False
        assert uses_book_code("ACCS（次經）") is False
