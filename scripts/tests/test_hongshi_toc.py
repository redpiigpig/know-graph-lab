# -*- coding: utf-8 -*-
"""《弘誓雙月刊》目次解析的純函式（零 I/O）。

樣本都照抄自實際 PDF 的文字層，包含 157 期改版前後兩種版面。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hongshi_toc import (  # noqa: E402
    matches_author,
    parse_toc,
    split_authors,
)

# 舊版（80–156 期）：分隔符「／」
OLD = """目
次　本期專題：印順導師百秩晉一誕辰紀念特刊
　  薪火相傳
4  　「印順學」已在形成
        ——主辦印順導師思想學術會議感言　／釋昭慧
8  　寒潭清水，映月無痕
        ——印順導師圓寂「焦點訪談」錄　／釋昭慧
30  從律典探索佛教對動物的態度（上）　／釋悟殷
42   素食主義的當代辯論　／董布諾斯基（D. Dombrowski）著，張展源譯
"""

# 新版（157 期起）：分隔符「│」、頁碼與篇名分行、上方有刊頭、中間夾封面說明
NEW = """DECEMBER 2020
vol.168
Contents
弘誓通訊（雙月刊）NO.168
導師│印順導師
發行人│釋見岸
總編輯│釋明一
電話│(03) 4987325
ISSN 17292786
目  次
民國一○九年十二月出刊│
   編輯室報告│釋明一
【本期專題】社會運動的另類修行
6
佛教比丘尼引領亞洲爭取同性婚姻合法化

──對釋昭慧而言，正語和慈悲心相輔相成

    │英文作者：茱麗雅•莉布立荷／中文翻譯：袁筱晴
16 釋昭慧法師人物專訪

──Unbound 紀錄片專案

    │攝影、錄影、訪談：凱莉•格琳
21 當修行者遇上記者│袁筱晴
38 《如理作意》自序│釋昭慧
封面說明│
美國南加大宗教與公民文化中心專案計
畫訪談昭慧法師。此一訪談計畫具有全球
2023年8月13日，第二十一屆國際學術會議
"""

# 兩欄式版面（157 期）：頁碼先成一欄吐出來，篇名在後
TWO_COLUMN = """目  次
04
10
16
25
27
31
34
民國一○八年二月出刊│
"""


class TestOldLayout:
    def setup_method(self):
        self.rows = parse_toc(OLD)

    def test_all_entries_found(self):
        assert [r["page"] for r in self.rows] == [4, 8, 30, 42]

    def test_wrapped_subtitle_keeps_its_dash(self):
        # strip 掉破折號會變成「「印順學」已在形成主辦印順導師…」
        assert self.rows[0]["title"] == "「印順學」已在形成——主辦印順導師思想學術會議感言"

    def test_section_heading_is_not_an_entry(self):
        assert all("薪火相傳" not in r["title"] for r in self.rows)

    def test_author_with_inner_punctuation_kept_whole(self):
        assert self.rows[3]["author"] == "董布諾斯基（D. Dombrowski）著，張展源譯"


class TestNewLayout:
    def setup_method(self):
        self.rows = parse_toc(NEW)

    def test_redesigned_separator_is_understood(self):
        # 🚨 只認「／」的版本在這裡回 0 筆，而且沒有任何錯誤訊息
        assert len(self.rows) >= 4

    def test_page_number_on_its_own_line_binds_to_following_title(self):
        r = next(r for r in self.rows if r["page"] == 6)
        assert r["title"].startswith("佛教比丘尼引領亞洲爭取同性婚姻合法化")
        assert "正語和慈悲心" in r["title"]

    def test_entry_complete_on_one_line(self):
        r = next(r for r in self.rows if r["page"] == 38)
        assert r["title"] == "《如理作意》自序"
        assert r["author"] == "釋昭慧"

    def test_masthead_never_becomes_an_entry(self):
        # 發行人│釋見岸 長得跟篇目一模一樣
        titles = [r["title"] for r in self.rows]
        assert not any(t in ("發行人", "導師", "總編輯", "電話") for t in titles)

    def test_pageless_editorial_note_is_kept(self):
        r = next(r for r in self.rows if r["title"] == "編輯室報告")
        assert r["page"] is None and r["author"] == "釋明一"

    def test_cover_note_prose_is_dropped(self):
        assert all("南加大" not in r["title"] for r in self.rows)

    def test_a_year_is_not_read_as_a_page_number(self):
        # 「2023年8月13日…」的 202 曾被當成頁碼
        assert all(r["page"] is None or r["page"] <= 200 for r in self.rows)


class TestTwoColumnBailsOut:
    def test_returns_empty_rather_than_garbage(self):
        # 硬解會生出 7 筆空篇名假篇目，再把後文全灌進最後一筆
        assert parse_toc(TWO_COLUMN) == []


class TestAuthors:
    def test_co_authors_split(self):
        assert split_authors("鄭幸讚、蔡美華、張月琴") == ["鄭幸讚", "蔡美華", "張月琴"]

    def test_interfaith_dialogue_split(self):
        # 不拆的話，「古倫神父‧昭慧法師」用「昭慧」比不到
        assert matches_author("古倫神父‧昭慧法師", "昭慧") is True

    def test_plain_match(self):
        assert matches_author("釋昭慧", "昭慧") is True

    def test_non_match(self):
        assert matches_author("釋性廣", "昭慧") is False
