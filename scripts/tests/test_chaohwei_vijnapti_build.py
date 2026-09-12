# -*- coding: utf-8 -*-
"""《初期唯識思想》build 的純函式（零 I/O）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from chaohwei_vijnapti_build import (  # noqa: E402
    canonical_heading,
    drop_leading_chapter_title,
    heading_level,
    prefix_front_matter,
    toc_keys,
)

TOC = toc_keys("一、傳統研究法／一三\n（一）文獻學為主之研究法／三〇\n"
               "1. 中國與西方之文獻學研究／三〇\n㈠ 識緣名色，名色緣識／一三二\n"
               "二、現代佛教學研究法／三〇")

SECTIONS = [
    {"title": "出版前言", "wp": (1, 1), "prefix": "前言"},
    {"title": "自序", "wp": (2, 7), "prefix": "自序"},
    {"title": "目次", "wp": (8, 16), "prefix": "目次"},
]

CHS = [
    {"title": "壹　緒論", "start": "1", "end": "12"},
    {"title": "肆　根本佛法與唯識學——「心為主導性」的思考脈絡", "start": "119", "end": "162"},
]


def _rec(wp, printed):
    return {"work_page": wp, "printed": printed, "text": "正文"}


class TestPrefixFrontMatter:
    def test_front_matter_folio_gets_its_section_prefix(self):
        out = prefix_front_matter([_rec(3, "2")], SECTIONS, body_start=18)
        assert out[0]["printed"] == "自序2"

    def test_body_folio_untouched(self):
        out = prefix_front_matter([_rec(18, "1")], SECTIONS, body_start=18)
        assert out[0]["printed"] == "1"

    def test_the_four_page_ones_stop_colliding(self):
        # 出版前言／自序／目次／正文 各有一個「頁 1」
        recs = [_rec(1, "1"), _rec(2, "1"), _rec(8, "1"), _rec(18, "1")]
        out = prefix_front_matter(recs, SECTIONS, body_start=18)
        assert [r["printed"] for r in out] == ["前言1", "自序1", "目次1", "1"]

    def test_page_without_a_folio_stays_empty(self):
        # 沒讀到頁碼就留空，不要生出一個只有前綴的假頁碼
        out = prefix_front_matter([_rec(3, "")], SECTIONS, body_start=18)
        assert out[0]["printed"] == ""

    def test_original_records_are_not_mutated(self):
        recs = [_rec(3, "2")]
        prefix_front_matter(recs, SECTIONS, body_start=18)
        assert recs[0]["printed"] == "2"


class TestDropLeadingChapterTitle:
    def test_single_line_title_is_dropped(self):
        units = [("13", "貳研究方法論", 0), ("13", "一、傳統研究法", 0)]
        out = drop_leading_chapter_title(units, [{"title": "貳　研究方法論"}])
        assert [u[1] for u in out] == ["一、傳統研究法"]

    def test_title_split_across_two_printed_lines_is_dropped_whole(self):
        # 🚨 長章名在書上折成兩行，只比第一段的話下半截會留在正文最前面
        units = [("119", "肆根本佛法與唯識學", 1),
                 ("119", "——「心為主導性」的思考脈絡", 1),
                 ("119", "就「唯識學探源」之主題而言，印順導師已自", 1)]
        out = drop_leading_chapter_title(units, CHS)
        assert [u[1] for u in out] == ["就「唯識學探源」之主題而言，印順導師已自"]

    def test_body_that_is_not_the_title_is_kept(self):
        units = [("1", "唯識學不僅是一門體系龐大的學問", 0)]
        out = drop_leading_chapter_title(units, CHS)
        assert len(out) == 1

    def test_only_the_start_of_a_chapter_is_examined(self):
        # 章名在後面又出現一次（引用自己的章名）→ 那是正文，不能刪
        units = [("1", "正文第一段", 0), ("2", "壹　緒論", 0)]
        out = drop_leading_chapter_title(units, CHS)
        assert len(out) == 2

    def test_each_chapter_is_handled_independently(self):
        units = [("1", "壹緒論", 0), ("1", "正文", 0),
                 ("119", "肆根本佛法與唯識學", 1),
                 ("119", "——「心為主導性」的思考脈絡", 1), ("119", "正文二", 1)]
        out = drop_leading_chapter_title(units, CHS)
        assert [u[1] for u in out] == ["正文", "正文二"]

    def test_front_matter_index_is_left_alone(self):
        units = [("目次1", "出版前言／〇一——〇八", -1)]
        assert len(drop_leading_chapter_title(units, CHS)) == 1


class TestTocKeys:
    def test_page_number_after_the_slash_is_stripped(self):
        assert toc_keys("一、傳統研究法／一三") == {"傳統研究法": (1, "一、")}

    def test_level_comes_from_the_numbering_style(self):
        assert TOC["傳統研究法"][0] == 1
        assert TOC["文獻學為主之研究法"][0] == 2
        assert TOC["中國與西方之文獻學研究"][0] == 3
        assert TOC["識緣名色名色緣識"] == (2, "㈠")

    def test_two_entries_run_together_still_split(self):
        # 目次 OCR 常把兩條黏成一行：「…／五〇10. 小結／五三」
        assert toc_keys("9. 檢視研究動機與範疇／五〇10. 小結／五三") == {
            "檢視研究動機與範疇": (3, "9."), "小結": (3, "10.")}

    def test_empty(self):
        assert toc_keys("") == {}


class TestHeadingLevel:
    def test_three_levels(self):
        assert heading_level("一、傳統研究法", TOC) == 1
        assert heading_level("（一）文獻學為主之研究法", TOC) == 2
        assert heading_level("1. 中國與西方之文獻學研究", TOC) == 3

    def test_circled_number_is_level_two(self):
        assert heading_level("㈠ 識緣名色，名色緣識", TOC) == 2

    def test_in_the_toc_beats_the_length_cap(self):
        # 目次認得的長標題照收
        assert heading_level("㈠ 識緣名色，名色緣識", TOC, max_len=6) == 2

    def test_prose_list_item_with_a_full_stop_is_not_a_heading(self):
        # 🚨 散文列舉長得跟標題一模一樣，差別在句號
        assert heading_level("2. 知道法門廣大，所以不再局限於三論與唯識。", TOC) is None
        assert heading_level("一、細心相續：特別與唯識學中阿陀那識執受根身有關。", TOC) is None

    def test_a_date_is_not_a_heading(self):
        # 自序文末「九十、三、十九 于尊梅樓」
        assert heading_level("九十、三、十九 于尊梅樓", TOC) is None

    def test_long_prose_not_in_the_toc_is_rejected(self):
        s = "二、北魏之北印度菩提流支，所譯之《深密解脫經》（五〇八）五十"
        assert heading_level(s, TOC) is None

    def test_short_heading_missing_from_the_toc_is_still_accepted(self):
        # 目次 OCR 漏字時（正文「現代佛教教學研究法」目次讀成「現代佛教學研究法」）
        assert heading_level("二、現代佛教教學研究法", TOC) == 1

    def test_plain_paragraph(self):
        assert heading_level("唯識學不僅是一門體系龐大的學問", TOC) is None

    def test_already_a_markdown_heading_is_left_alone(self):
        assert heading_level("## 貳　研究方法論", TOC) is None

    def test_numbering_with_no_text_after_it(self):
        assert heading_level("一、", TOC) is None

    def test_circled_number_misread_as_a_real_character(self):
        # 🚨 ㈡ 被 OCR 讀成「口」、㈢ 讀成「曰」、㈣ 讀成「四」——都是真的漢字，
        # 認不得字形，只能反過來問「拿掉它之後是不是目次上的標題」
        assert heading_level("口識緣名色，名色緣識", TOC) == 2
        assert heading_level("曰識緣名色，名色緣識", TOC) == 2

    def test_a_sentence_merely_starting_with_that_character_is_not_a_heading(self):
        assert heading_level("口中唸唸有詞地說著什麼", TOC) is None

    def test_whole_paragraph_equal_to_a_toc_entry(self):
        assert heading_level("傳統研究法", TOC) == 1

    def test_the_length_cap_still_applies_to_the_whitelist_fallback(self):
        long = "識緣名色，名色緣識" + "補" * 40
        assert heading_level(long, TOC) is None


class TestCanonicalHeading:
    def test_misread_circle_number_is_restored_from_the_toc(self):
        # 「口識緣名色，名色緣識」→ 目次印的是 ㈠
        assert canonical_heading("口識緣名色，名色緣識", TOC) == "㈠ 識緣名色，名色緣識"

    def test_bracket_numbering_joins_without_a_space(self):
        toc = toc_keys("（二）諸行無常法則／六四")
        assert canonical_heading("口諸行無常法則", toc) == "（二）諸行無常法則"

    def test_a_readable_numbering_is_never_rewritten(self):
        assert canonical_heading("一、傳統研究法", TOC) == "一、傳統研究法"
        assert canonical_heading("（一）文獻學為主之研究法", TOC) == "（一）文獻學為主之研究法"

    def test_title_with_no_numbering_at_all_is_left_as_is(self):
        assert canonical_heading("傳統研究法", TOC) == "傳統研究法"

    def test_unknown_text_is_left_as_is(self):
        assert canonical_heading("口中唸唸有詞", TOC) == "口中唸唸有詞"
