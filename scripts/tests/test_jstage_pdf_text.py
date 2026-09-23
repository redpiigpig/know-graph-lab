# -*- coding: utf-8 -*-
"""jstage_pdf_text：J-STAGE 直排／雙欄 PDF 的文字層重排。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import jstage_pdf_text as J  # noqa: E402


def _col(x: float, y0: float, text: str, h: float = 8.0) -> list[J.Ch]:
    """一條直行：從 y0 往下每字一格。"""
    return [J.Ch(x, y0 + i * h, x + 7, y0 + i * h + 7, c, 7.0) for i, c in enumerate(text)]


def test_vertical_reads_right_to_left_upper_tier_first():
    # 上下兩段各六行（實際頁面有幾十行；少於四行不做上下段投票）
    up = ["あいうえおか", "かきくけこさ", "さしすせそた", "たちつてとな", "なにぬねのは", "はひふへほま"]
    lo = ["まみむめもや", "やゆよらりる", "るれろわをん", "アイウエオカ", "カキクケコサ", "サシスセソタ"]
    xs = [160, 148, 136, 124, 112, 100]
    chars = [c for x, t in zip(xs, up) for c in _col(x, 10, t)]
    chars += [c for x, t in zip(xs, lo) for c in _col(x, 100, t)]
    lines = J.vertical_lines(chars)
    assert [ln.text for ln in lines] == up + lo


def test_tier_separator_survives_a_heading_spanning_both_tiers():
    """跨兩段的標題會破壞「整頁空白帶」，投票法仍要找得到分界。"""
    chars = []
    for x in range(20, 200, 12):
        chars += _col(x, 10, "一" * 8) + _col(x, 120, "二" * 8)
    chars += _col(210, 10, "標" * 20)          # 一條從上段貫穿到下段的標題行
    seps = J.tier_separators(chars, 8.0, 7.0)
    assert len(seps) == 1 and 70 < seps[0] < 120


def test_spaced_byline_is_its_own_paragraph():
    """字距拉開的署名（並　木　浩　一）不可黏到上一段結尾。"""
    body = [_col(x, 10, "本文本文本文本文本文本文。"[: 12]) for x in (200, 188, 176)]
    byline = [J.Ch(164, y, 171, y + 7, c, 7.0) for y, c in zip((10, 40, 70, 100), "並木浩一")]
    chars = [c for col in body for c in col] + byline
    lines = J.vertical_lines(chars)
    assert any(ln.spaced and ln.text == "並木浩一" for ln in lines)


def test_join_broken_merges_long_unfinished_paragraph():
    paras = [("前半" * 40, 1), ("後半です。", 2), ("次の段落。", 2)]
    out = J.join_broken(paras)
    assert out[0] == ("前半" * 40 + "後半です。", 1)
    assert out[1][0] == "次の段落。"


def test_join_broken_leaves_headings_and_note_markers_alone():
    paras = [("本文" * 40, 1), ("註", 3), ("(1) 文献", 3)]
    assert len(J.join_broken(paras)) == 3


def test_merge_spaced_titles():
    assert J.merge_spaced_titles([("旧", 1), ("約", 1), ("学", 1)]) == [("旧約学", 1)]


def test_drop_running_heads_by_repetition():
    head = J.Line("聖書におけるユーモアとアイロニー 175", 0, 0)
    head2 = J.Line("聖書におけるユ!モアとアイロニー 176", 0, 0)
    body = J.Line("本文", 0, 0)
    pages = J.drop_running_heads([([head, body], True), ([head2, body], True)])
    assert [ln.text for ln in pages[0][0]] == ["本文"]
