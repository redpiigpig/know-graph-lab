# -*- coding: utf-8 -*-
"""relink_missing_footnotes 的純函式（案例全取自 2026-09-28 民主妙法）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import relink_missing_footnotes as rl  # noqa: E402


def only(seg, n):
    c = rl.rule_candidates(seg, n)
    assert len(c) == 1, c
    st, en, how = c[0]
    return seg[st:en], how


def test_superscript():
    assert only("並試圖入臺北某佛寺²出家。母親找到了她", 12) == ("²", "上標")


def test_superscript_with_leading_digit():
    assert only("而是對二者重新詮釋，4²好教人們將其視為", 42) == ("4²", "上標")


def test_glued_to_year():
    assert only("為禪門臨濟宗第四十八代傳人。341941年，14歲的星雲", 34) == ("34", "黏年份")


def test_partial_digit():
    assert only("當時一場三壇大戒預定於臺北臨濟寺1舉行，而錦雲", 17) == ("1", "殘缺")


def test_figure_number_is_not_a_note():
    assert rl.rule_candidates("政治人物圖6星雲大師（由佛光山提供）", 6) == []


def test_quantity_is_not_a_note():
    assert rl.rule_candidates("她要求在家居士，按日各將30名", 3) == []


def test_place_after_cleans_residual_digit():
    seg = "妳也該愛妳丈夫所愛。」4而在另則故事中"
    assert rl.place_after(seg, "妳也該愛妳丈夫所愛。」", 43) == "妳也該愛妳丈夫所愛。」[^43]而在另則故事中"


def test_place_after_rejects_adjacent_ref():
    assert rl.place_after("進至一處巨大的殿前廣場。[^10]唱誦", "進至一處巨大的殿前廣場。", 6) is None


def test_place_after_requires_unique():
    assert rl.place_after("自立自立自立自立", "自立自立", 5) is None


def test_gap_count():
    rule = "\n" + "—" * 20 + "\n"
    chunks = [{"content": "正文[^1]又一句" + rule + "(1) 註一\n(2) 註二"}]
    assert rl.gap_count(chunks) == (2, 1)


def test_segment_wide_uses_nearest_linked_refs():
    body = "甲[^1]乙丙丁戊[^5]己"
    assert rl.segment(body, 3) is None                  # 窄：2、4 都沒連，不猜
    lo, hi = rl.segment(body, 3, wide=True)
    assert body[lo:hi] == "乙丙丁戊"


def test_segment_wide_without_refs_is_whole_body():
    assert rl.segment("全塊沒有任何註號", 2, wide=True) == (0, 8)


def test_book_type():
    rule = "\n" + "—" * 20 + "\n"
    long_note = "這是一則相當長的註釋內容，引用某書某頁並加以說明其論點與出處，讓平均長度超過四十字的門檻。"
    a = [{"content": "正文[^1]又一句" + rule + f"(1) {long_note}\n(2) {long_note}"}]
    e = [{"content": "正文沒有註號" + rule + "(1) 何謂善？\n(2) 何謂惡？"}]
    f = [{"content": "正文沒有註號" + rule + f"(1) {long_note}"}]
    assert (rl.book_type(a), rl.book_type(e), rl.book_type(f)) == ("A", "E", "F")


def test_place_after_rejects_hyphen_break_and_heading():
    assert rl.place_after("so that they learned to hold themselves cor-\nrectly", "hold themselves cor-", 27) is None
    assert rl.place_after("## 二十一\n復活使我們稱義\n正文", "復活使我們稱義", 1) is not None
    assert rl.place_after("## 復活使我們稱義\n正文", "復活使我們稱義", 1) is None
