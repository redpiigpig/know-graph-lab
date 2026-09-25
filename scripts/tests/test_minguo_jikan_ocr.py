# -*- coding: utf-8 -*-
"""minguo_jikan_ocr / minguo_jikan_dila_catalog 純函式測試。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import minguo_jikan_ocr as m                      # noqa: E402
import minguo_jikan_dila_catalog as cat           # noqa: E402


def test_merge_and_subtract_ranges():
    assert m.merge_ranges([[5, 7], [1, 3], [4, 4]]) == [[1, 7]]
    assert m.subtract_ranges([[0, 10]], [[3, 4], [8, 8]]) == [[0, 2], [5, 7], [9, 10]]
    assert m.subtract_ranges([[0, 10]], [[0, 10]]) == []
    assert m.subtract_ranges([[5, 6]], [[0, 2]]) == [[5, 6]]
    assert m.covered([[0, 10]], 3, 5) and not m.covered([[0, 4]], 3, 5)


def test_chunk_ranges_and_pages_in():
    assert m.chunk_ranges([[0, 45]], 20) == [[0, 19], [20, 39], [40, 45]]
    assert m.pages_in([[0, 19], [20, 39], [10, 15]]) == 40


def test_page_range():
    assert m.page_range("315~317") == (315, 317)
    assert m.page_range("315") == (315, 315)
    assert m.page_range("5730574") is None or m.page_range("5730574") == (5730574, 5730574)
    assert m.page_range("300~200") is None
    assert m.page_range("") is None


def test_learn_offset_prefers_jicheng_numbers():
    # 頁底 -N- 集成頁碼（offset 2）與版心原刊頁碼（offset 大）混在一起
    recs = [{"pdf_index": 144 + i, "page_numbers": [f"-{142 + i}-", f"{4 + i}"]} for i in range(5)]
    assert m.learn_offset(recs) == 2
    # 樣本太少 → None
    assert m.learn_offset(recs[:2]) is None
    # 不同意 → None
    bad = [{"pdf_index": 10 + i, "page_numbers": [str(8 + i), str(7 + i)]} for i in range(4)]
    assert m.learn_offset(bad) is None


def test_infer_orig_page():
    rows = [{"集成頁": "142~145", "原刊頁": "4~7", "篇名": "甲"},
            {"集成頁": "146~150", "原刊頁": "8", "篇名": "乙"}]
    assert m.infer_orig_page(143, rows) == (5, "甲")
    assert m.infer_orig_page(148, rows) == (10, "乙")
    assert m.infer_orig_page(200, rows) == (None, "")
    # 兩篇給不同答案 → 留空
    rows2 = rows + [{"集成頁": "143", "原刊頁": "99", "篇名": "丙"}]
    assert m.infer_orig_page(143, rows2) == (None, "")


def test_split_content():
    body, notes = m.split_content("正文\n\n" + m.FOOTNOTE_RULE + "\n註一\n註二")
    assert body == "正文" and notes == ["註一", "註二"]
    assert m.split_content("只有正文") == ("只有正文", [])


def test_priority_tier():
    assert m.priority_tier({"命中關鍵字": "世界佛學苑、作者太虛"}) == 0
    assert m.priority_tier({"命中關鍵字": "漢藏教理院"}) == 1
    assert m.priority_tier({"命中關鍵字": "法舫"}) == 2
    assert m.priority_tier({"命中關鍵字": "太虛"}) == 3


def test_merge_ranges_gap():
    assert m.merge_ranges([[1, 2], [6, 7], [20, 21]], gap=4) == [[1, 7], [20, 21]]
    assert m.merge_ranges([[1, 2], [6, 7]]) == [[1, 2], [6, 7]]


def test_cut_text_header_and_pages():
    pages = {144: {"text": "頁一", "footnotes": [], "原刊頁": 4},
             145: {"text": "頁二", "footnotes": ["註"], "原刊頁": None}}
    row = {"集成頁": "142~143", "篇名": "歡迎法尊", "原書資訊原文": "海潮音,v.15,no.6,p.4~7", "作者": "法舫"}
    t = m.cut_text("正編187", row, pages, 2, "CPU")
    assert t.startswith("《民國佛教期刊文獻集成》正編第187冊，頁 142–143：歡迎法尊（海潮音,v.15,no.6,p.4~7）　作者：法舫")
    assert "【集成 正編187 頁 142｜原刊 頁 4】\n頁一" in t
    assert "【集成 正編187 頁 143｜原刊 頁 ?】\n頁二\n" + m.FOOTNOTE_RULE + "\n註" in t


SAMPLE_ITEM = '''<div class="resultItem">
<div style="float:right;"><a href="#top" title="44">top</a></div><div class="paperTitle">2 『太虛大師答崇明王蓉清居士問（附來問書）』</div><div class="showItemInfo">叢刊資訊：MFQB,vol.1,p.115~120</div><div class="showItemInfo">原書資訊：<a target="_self" href="?journalName=%EF%BB%BF%E8%A6%BA%E7%A4%BE%E5%8F%A2%E6%9B%B8">﻿覺社叢書</a>,no.4,p.1~6,<span><em>未登錄日期</em></span></div><div class="showItemInfo">文章類別：答問/<a href="?subClassName=x">答問</a></div><div class="showItemInfo">作者：<a target="_self" href="?paperAuthor=%E5%A4%AA%E8%99%9B">太虛</a> <a href="?paperAuthor=x">編者</a> </div></div><hr class="tailHr"/>
<div class="resultItem"><a href="#top" title="9">top</a><div class="paperTitle">1 『學佛之目的』</div><div class="showItemInfo">叢刊資訊：MFQ,vol.171,p.315</div><div class="showItemInfo">原書資訊：<a href="?journalName=%E6%B5%B7%E6%BD%AE%E9%9F%B3">海潮音</a>,v.9,no.10,p.1~3,1928-11-01</div><div class="showItemInfo">作者：此文無記作者姓名</div></div><hr class="tailHr"/>'''


def test_parse_page_fields():
    rows = cat.parse_page(SAMPLE_ITEM)
    assert len(rows) == 2
    r = rows[0]
    assert r["叢刊"] == "補編" and r["冊"] == "1" and r["集成頁"] == "115~120"
    assert r["篇名"] == "太虛大師答崇明王蓉清居士問（附來問書）"
    assert r["原刊"] == "覺社叢書" and r["原刊期"] == "4" and r["原刊頁"] == "1~6" and r["日期"] == ""
    assert r["作者"] == "太虛；編者" and r["類別"].startswith("答問") and r["dila_id"] == "44"
    r2 = rows[1]
    assert r2["叢刊"] == "正編" and r2["冊"] == "171" and r2["原刊卷"] == "9" and r2["原刊期"] == "10"
    assert r2["日期"] == "1928-11-01" and r2["作者"] == ""
    assert cat.taixu_hits(rows[0]) == ["太虛", "作者太虛"]
    assert cat.taixu_hits(rows[1]) == []
