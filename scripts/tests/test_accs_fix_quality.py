# -*- coding: utf-8 -*-
"""ACCS 資料修復的判準（純函式，零 I/O）。刪除是不可逆的，判準要鎖死。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from accs_fix_quality import (  # noqa: E402
    is_index_row,
    is_term_index_row,
    normalize_source_vol,
)


class TestIsIndexRow:
    def test_author_index_line(self):
        # 作者索引：整段都是頁碼
        assert is_index_row("102, 208, 235, 302, 304, 306, 308, 352") is True

    def test_scripture_index_with_roman_numerals(self):
        assert is_index_row("xxiii, xxv, 4, 6, 14, 26, 47, 51, 58, 100, 116") is True

    def test_subject_index_line(self):
        assert is_index_row("9-10, 31-32, 115, 118, 240") is True

    def test_real_commentary_is_kept(self):
        body = ("窮人為你提供你必需的服務。甚麼服務？難道他們不是很好地服事你嗎？"
                "試想一個特別貧窮的人，他為你提供你必需的服務。")
        assert is_index_row(body) is False

    def test_commentary_citing_many_verses_is_kept(self):
        # 正文引經據典也會有數字，但不會通篇只有數字
        body = "保羅在羅馬書 8:1、8:14 與 12:2 談到聖靈的引導，屈梭多模由此推論成聖之道。"
        assert is_index_row(body) is False

    def test_short_numeric_snippet_is_not_deleted(self):
        # 「9-10」可能只是正常的節號註記，太短一律不動
        assert is_index_row("9-10") is False

    def test_empty(self):
        assert is_index_row("") is False
        assert is_index_row(None) is False


class TestNormalizeSourceVol:
    def test_code_form_is_rewritten(self):
        assert normalize_source_vol("ACCS（gen）", "創世記") == "ACCS（創世記）"

    def test_numeric_code_form(self):
        assert normalize_source_vol("ACCS（1co）", "哥林多前書") == "ACCS（哥林多前書）"

    def test_chinese_name_untouched(self):
        assert normalize_source_vol("ACCS（詩篇）", "詩篇") is None

    def test_combined_volume_name_untouched(self):
        # 🚨 合卷名不可被改掉：只動「括號內全是英數代碼」的
        assert normalize_source_vol("ACCS（耶利米書‧耶利米哀歌）", "耶利米書") is None

    def test_deuterocanon_volume_untouched(self):
        assert normalize_source_vol("ACCS（次經）", "多俾亞傳") is None

    def test_missing_book_name_is_a_noop(self):
        assert normalize_source_vol("ACCS（gen）", "") is None


class TestTermIndexRow:
    """中文索引詞型：第一版只看數字佔比，這一類 883 筆全部漏抓。"""

    def test_subject_index_with_chinese_term(self):
        assert is_term_index_row("誇張, xxii") is True
        assert is_term_index_row("使徒保羅, 1-12") is True

    def test_fullwidth_comma(self):
        assert is_term_index_row("教會是混合的群體，xxiii, 129, 135") is True

    def test_real_short_commentary_is_kept(self):
        # 正文再短也有句末標點
        assert is_term_index_row("屈梭多模論此節，意在勸勉。") is False

    def test_prose_without_page_numbers_is_kept(self):
        assert is_term_index_row("保羅在此，論到信心與行為") is False

    def test_long_line_is_not_an_index_entry(self):
        assert is_term_index_row("某某，" + "正文" * 40) is False

    def test_caught_by_the_combined_check(self):
        assert is_index_row("誇張, xxii") is True
