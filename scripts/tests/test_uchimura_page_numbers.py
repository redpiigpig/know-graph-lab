# -*- coding: utf-8 -*-
"""全集那條線的頁碼與底本 —— 「轉錄要能引用」的兩個必要條件。

背景：這條線曾把 `page_number` 填成 `chunk_index + 1`，465 頁的豪斯評傳長出
152 個假頁碼（看起來正常、照著引就是錯的）。止血之後補的是**真頁碼**：
有印刷頁碼的來源逐段記下來，沒有的（青空文庫這種電子底本）留 null 並改記底本。
見 [[feedback_transcribe_page_numbers]]。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uchimura_auto as ua  # noqa: E402
import uchimura_build as ub  # noqa: E402


# ── chunk 的頁碼 ──────────────────────────────────────────────────────────────
class TestFirstPage:
    def test_takes_the_first_paragraph_with_a_page(self):
        assert ua.first_page(["21", "21", "22"]) == 21

    def test_skips_leading_blanks(self):
        assert ua.first_page([None, None, "137"]) == 137

    def test_roman_folio_is_not_converted(self):
        """序言的 xii 跟正文的 12 是不同的兩頁——換算等於偽造。"""
        assert ua.first_page(["xii", "xiii"]) is None

    def test_no_pages_at_all(self):
        assert ua.first_page([]) is None
        assert ua.first_page([None, None]) is None

    def test_accepts_ints_as_well_as_digit_strings(self):
        assert ua.first_page([7]) == 7


class TestChunkedCarriesPages:
    def test_pages_are_sliced_alongside_the_paragraphs(self):
        zh, src = list("abcde"), list("ABCDE")
        got = list(ua._chunked(zh, src, maxp=2, pages=["1", "1", "2", "2", "3"]))
        assert [p for _z, _s, p in got] == [["1", "1"], ["2", "2"], ["3"]]

    def test_missing_pages_default_to_none_without_shifting(self):
        """頁碼給得比段落短時要補 None，不可讓後面的段落領到前面的頁碼。"""
        got = list(ua._chunked(list("abcd"), list("ABCD"), maxp=2, pages=["1"]))
        assert [p for _z, _s, p in got] == [["1", None], [None, None]]


# ── 青空文庫的底本 ────────────────────────────────────────────────────────────
def _soup(inner: str):
    from bs4 import BeautifulSoup
    return BeautifulSoup(
        f'<div class="bibliographical_information">{inner}</div>', "html.parser")


class TestSourceNote:
    def test_base_text_and_its_parent_are_kept(self):
        note = ub.parse_source_note(_soup(
            "底本：「内村鑑三全集3」岩波書店<br>1982（昭和57）年12月20日発行<br>"
            "底本の親本：「基督教新聞　578号」<br>1894（明治27）年8月24日発行<br>"
            "入力：ゆうき<br>校正：ちはる<br>2000年11月2日公開"))
        lines = note.split(chr(10))
        assert lines[0].startswith("底本：")
        assert any(ln.startswith("底本の親本：") for ln in lines)
        assert len(lines) == 4

    def test_volunteer_credits_are_dropped(self):
        """入力／校正／公開日期是志工作業紀錄，不是版本資訊。"""
        note = ub.parse_source_note(_soup(
            "底本：「後世への最大遺物」岩波文庫<br>入力：しんかい<br>校正：もりみつ"))
        assert "入力" not in note and "校正" not in note

    def test_editorial_marks_are_dropped(self):
        """※ 開頭是這個電子檔怎麼做的，不是這篇文章出自哪個版本。"""
        note = ub.parse_source_note(_soup(
            "底本：「日本の名随筆」作品社<br>※「棉羊」と「綿羊」の混在は、底本の通りです。"))
        assert "※" not in note

    def test_first_publication_is_kept(self):
        """初出＝首次發表處，引註要用。"""
        note = ub.parse_source_note(_soup(
            "底本：「ヨブ記講演」岩波文庫<br>初出：内村聖書研究会においての講義"))
        assert "初出：" in note

    def test_missing_block_returns_empty_string(self):
        from bs4 import BeautifulSoup
        assert ub.parse_source_note(BeautifulSoup("<div>本文</div>", "html.parser")) == ""
