# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import backfill_printed_pages as bp  # noqa: E402


def test_candidate_forms():
    assert bp.candidate("正文第一行\n正文第二行\n\n- 12 -") == 12
    assert bp.candidate("導論 15\n正文") == 15
    assert bp.candidate("16 第一章　緒論\n正文") == 16
    assert bp.candidate("這一段正文裡提到 1848 年的革命，但不是頁碼。\n另一行也是正文，很長很長。") is None


def test_validate_drops_isolated_and_keeps_offset_switch():
    # 前言羅馬頁沒抓到；正文從實體頁 11 起印 1；實體頁 14 被誤抓成 8（孤立）
    cands = [(11, 1), (12, 2), (13, 3), (14, 8), (15, 5), (16, 6)]
    got = bp.validate(cands)
    assert 14 not in got and got[11] == 1 and got[16] == 6


def test_fill_book_low_coverage_leaves_untouched():
    chunks = [{"chunk_type": "page", "page_number": i, "content": "正文"} for i in range(1, 21)]
    assert bp.fill_book(chunks) == (0, 20)
    assert all("printed_page" not in c for c in chunks)


def test_last_line_page_number_beats_footnote_marker():
    assert bp.candidate("信，說除非我看見\n正文\n1\n149") == 149
