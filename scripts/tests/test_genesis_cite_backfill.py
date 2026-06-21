# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import genesis_cite_backfill as gc


def test_term_match_keys_strips_brackets():
    assert gc.term_match_keys("倫理能見度（EVI）") == ["倫理能見度"]
    assert gc.term_match_keys("hi（誠實度）") == ["誠實度"]
    # 純拉丁無中文骨幹 → 無鍵
    assert gc.term_match_keys("EVI") == []
    # 複合詞拆出的通用 2 字詞被門檻擋掉，不污染排名
    assert gc.term_match_keys("行善≠誠實") == []
    keys = gc.term_match_keys("愛的萬物論（The Theory of Everything in Love）")
    assert "愛的萬物論" in keys


def test_split_content_recap():
    html = '<h3>一</h3><p>x</p><section class="chapter-recap"><h3>本章摘要</h3></section>'
    content, recap = gc.split_content_recap(html)
    assert "本章摘要" not in content
    assert recap.startswith('<section class="chapter-recap"')


def test_section_seq_labels_ranks_by_frequency_and_maps():
    term_keys = {"誠實度": ["誠實度"], "日擇原理": ["日擇原理"]}
    term_ids = {"誠實度": ["aaaaaaaa", "bbbbbbbb"], "日擇原理": ["cccccccc"]}
    prefix_map = {"aaaaaaaa": "C-00010", "bbbbbbbb": "C-00002", "cccccccc": "G-00001"}
    body = "誠實度誠實度誠實度 日擇原理"
    labels = gc.section_seq_labels(body, term_keys, term_ids, prefix_map)
    # 兩術語都命中 → 兩者 id 都收；排序 C 在 G 前、數字升冪
    assert labels == ["C-00002", "C-00010", "G-00001"]


def test_section_seq_labels_empty_when_no_match():
    assert gc.section_seq_labels("毫無術語的文字", {"誠實度": ["誠實度"]},
                                 {"誠實度": ["aaaaaaaa"]}, {"aaaaaaaa": "C-1"}) == []


def test_tag_html_idempotent():
    html = (
        "<h2>第一章</h2>\n<h3>一、誠實</h3>\n<p>誠實度誠實度</p>\n"
        '<section class="chapter-recap"><h3>本章摘要</h3><p>誠實度</p></section>'
    )
    tk = {"誠實度": ["誠實度"]}
    ti = {"誠實度": ["aaaaaaaa"]}
    pm = {"aaaaaaaa": "C-00001"}
    out1, n1 = gc.tag_html(html, tk, ti, pm)
    out2, n2 = gc.tag_html(out1, tk, ti, pm)
    assert n1 == 1 and n2 == 1  # 只標內容節，recap 不標
    assert out1 == out2  # 冪等
    assert "本節主要依據對話：C-00001" in out1
    assert "本章主要依據對話：C-00001" in out1  # 章末彙整
    # 兩種 source（每節 + 章末）各一
    assert out1.count('class="section-source"') == 1
    assert out1.count("chapter-source") == 1
    # recap 區的 h3 未被標
    assert out1.index("section-source") < out1.index("chapter-recap")
    assert out1.index("chapter-source") < out1.index("chapter-recap")
