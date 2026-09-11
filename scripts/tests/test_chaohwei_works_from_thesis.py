# -*- coding: utf-8 -*-
"""碩論附錄三「著作一覽」的解析（純函式，零 I/O）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from chaohwei_works_from_thesis import (  # noqa: E402
    is_reprint_row,
    parse_works,
    split_sections,
    split_title_note,
)

SAMPLE = """
（一）昭慧法師

|  |  |  |
| :-: | :-: | :-: |
| 書名 | 出版社 | 出版日期 |
| 如是我思 | 大乘精舍印精會 | 1986.06 |
| 佛教倫理學 | 法界出版社 | 1995.10初版 |
| 淨心文教基金會 | 2001.09三版 |  |
| 成佛之道偈頌科判表（與性廣法師合著） | 法界出版社 | 1991.10 |
| 心靈的交會—山間對話（與彼得・辛格（Peter Singer）合著） | 法界出版社 | 2021.11 |
| 生命倫理與環境倫理——倫理抉擇的中道智慧（一） | 法界出版社 | 2022.08 |

（二）性廣法師

|  |  |  |
| :-: | :-: | :-: |
| 書名 | 出版社 | 出版日期 |
| 佛教養生學 | 法界出版社 | 2016.05 |
"""


class TestSplitTitleNote:
    def test_role_suffix_extracted(self):
        assert split_title_note("成佛之道偈頌科判表（與性廣法師合著）") == (
            "成佛之道偈頌科判表", "與性廣法師合著")

    def test_nested_parentheses(self):
        # 🚨 「（與彼得・辛格（Peter Singer）合著）」裡還有一層括號；
        # 不允許巢狀的 regex 會整組匹配不到，書名就把註記吞進去
        t, n = split_title_note("心靈的交會—山間對話（與彼得・辛格（Peter Singer）合著）")
        assert t == "心靈的交會—山間對話"
        assert "彼得" in n and "合著" in n

    def test_volume_marker_is_not_a_note(self):
        # 「（一）」是書名的一部分，不是編著身分
        t, n = split_title_note("生命倫理與環境倫理——倫理抉擇的中道智慧（一）")
        assert t.endswith("（一）") and n == ""

    def test_book_quotes_stripped(self):
        assert split_title_note("《如理作意》")[0] == "如理作意"

    def test_plain_title(self):
        assert split_title_note("律學今詮") == ("律學今詮", "")


class TestIsReprintRow:
    def test_reprint_continuation(self):
        # 再版列的第一欄是出版社、最後一欄空白
        assert is_reprint_row(["淨心文教基金會", "2001.09三版", ""]) is True

    def test_real_book_row(self):
        assert is_reprint_row(["如是我思", "大乘精舍印精會", "1986.06"]) is False

    def test_book_whose_title_contains_publisher_word_is_safe(self):
        # 三欄都有值就不是續列，即使書名含「文化」
        assert is_reprint_row(["法鼓文化五十年", "法界出版社", "2010.01"]) is False


class TestParseWorks:
    def test_counts_and_reprint_attachment(self):
        secs = split_sections(SAMPLE)
        ws = parse_works(secs["昭慧法師"])
        titles = [w["title"] for w in ws]
        # 續列不可變成一本書
        assert "淨心文教基金會" not in titles
        assert len(ws) == 5
        eth = next(w for w in ws if w["title"] == "佛教倫理學")
        assert eth["reprints"] and "淨心文教基金會" in eth["reprints"][0]

    def test_year_and_publisher(self):
        ws = parse_works(split_sections(SAMPLE)["昭慧法師"])
        w = next(w for w in ws if w["title"] == "如是我思")
        assert w["year"] == "1986" and w["publisher"] == "大乘精舍印精會"

    def test_two_people_split(self):
        secs = split_sections(SAMPLE)
        assert set(secs) == {"昭慧法師", "性廣法師"}
        assert len(parse_works(secs["性廣法師"])) == 1
