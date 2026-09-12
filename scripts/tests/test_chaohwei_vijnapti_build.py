# -*- coding: utf-8 -*-
"""《初期唯識思想》build 的純函式（零 I/O）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from chaohwei_vijnapti_build import (  # noqa: E402
    drop_leading_chapter_title,
    prefix_front_matter,
)

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
