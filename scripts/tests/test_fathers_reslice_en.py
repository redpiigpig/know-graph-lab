# -*- coding: utf-8 -*-
"""英文欄重切的純函式測試。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fathers_reslice_en import (  # noqa: E402
    anchors_of, block_index, chunk_start, dup_groups, plan_slices,
)

BLOCK = (
    "{{p:98}}\n\n1. I am fully conscious of the danger of the age.\n\n"
    "{{p:99}}\n\n7. Who does not see the slimy trail of the serpent?\n\n"
    "11. Next comes this: nor as Sabellius made one into two.\n\n"
    "{{p:100}}\n\n14. Then again, after an interval of preparation.\n"
)


def test_anchors_of_reads_both_kinds_in_order():
    got = [(k, n) for k, n, _ in anchors_of("{{p:98}}\n\n1. First\n\n7. Second")]
    assert got == [("p", 98), ("s", 1), ("s", 7)]


def test_anchors_of_ignores_numbers_inside_a_sentence():
    """🚨 節號要在段落開頭。句中的「about 3. 5 times」撈進來會切在半句話上。"""
    assert anchors_of("the ratio was about 3. 5 times larger") == []


def test_anchors_of_blank():
    assert anchors_of("") == []


def test_block_index_keeps_the_earliest_occurrence():
    """同一個節號在區塊裡出現兩次（正文一次、註釋一次）時取最早的。"""
    idx = block_index("1. first\n\ntext\n\n1. again")
    assert idx[("s", 1)] == 0


def test_chunk_start_matches_on_a_page_marker():
    assert chunk_start("{{p:99}}某段中文", block_index(BLOCK)) == BLOCK.index("{{p:99}}")


def test_chunk_start_matches_on_a_section_number():
    assert chunk_start("11. 接下來是這樣的", block_index(BLOCK)) == BLOCK.index("11.")


def test_chunk_start_returns_none_without_a_shared_anchor():
    """沒有共同錨點就回 None——留白，不猜。"""
    assert chunk_start("（780）這裡原文殘缺", block_index(BLOCK)) is None


def test_chunk_start_ignores_anchors_absent_from_the_block():
    assert chunk_start("{{p:999}}另一卷的頁碼", block_index(BLOCK)) is None


# ── plan_slices ─────────────────────────────────────────────────────────────

def test_plan_slices_cuts_at_the_next_anchored_chunk():
    zh = ["{{p:98}}1. 我滿懷著", "7. 誰看不出", "11. 接下來是這樣的"]
    out = plan_slices(zh, BLOCK)
    assert out[0].startswith("{{p:98}}") and "7. Who does not" not in out[0]
    # 這一段的中文只帶節號 7，所以切片從英文的「7.」起——不是從它前面那個
    # {{p:99}} 起。頁碼歸帶著頁碼的那一段。
    assert out[1].startswith("7. Who does not") and "11. Next comes" not in out[1]
    assert "14. Then again" in out[2]


def test_plan_slices_blanks_chunks_without_anchors():
    """🚨 沒有錨點就留白，不沿用前一段的切片——沿用只是把重複從「整卷」縮小成
    「一小組」，仍然是同一段文字出現在好幾頁，而且更難查覺。"""
    zh = ["{{p:98}}1. 我滿懷著", "（780）這裡原文殘缺", "7. 誰看不出"]
    out = plan_slices(zh, BLOCK)
    assert out[1] == ""


def test_plan_slices_loses_no_text():
    """留白那幾段的文字會落在前一個有錨點的段裡，一個字都不能丟。"""
    zh = ["{{p:98}}1. 我滿懷著", "沒有錨點的接續段", "{{p:100}}14. 然後"]
    out = plan_slices(zh, BLOCK)
    assert "7. Who does not" in out[0] and "11. Next comes" in out[0]


def test_plan_slices_all_unanchored():
    assert plan_slices(["沒有錨點", "也沒有"], BLOCK) == ["", ""]


def test_plan_slices_ignores_backwards_anchors():
    """後面那一段的錨點若比自己早（章節倒回去），不可以拿它當切點——會切出空字串。"""
    zh = ["{{p:100}}14. 然後", "1. 我滿懷著"]
    out = plan_slices(zh, BLOCK)
    assert out[0].startswith("{{p:100}}")


# ── dup_groups ──────────────────────────────────────────────────────────────

def test_dup_groups_finds_repeated_blocks():
    big = "x" * 600
    chunks = [{"sources": {"en": big}}, {"sources": {"en": big}}, {"sources": {"en": "y" * 600}}]
    assert dup_groups(chunks) == [[0, 1]]


def test_dup_groups_ignores_short_shared_text():
    chunks = [{"sources": {"en": "short"}}, {"sources": {"en": "short"}}]
    assert dup_groups(chunks) == []
