# -*- coding: utf-8 -*-
"""Pure-function tests for scripts/align_reference_anchors.py.

跑法：`pytest scripts/tests/test_align_reference_anchors.py -q`。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import align_reference as ar  # noqa: E402
import align_reference_anchors as ara  # noqa: E402
import merge_original_column as moc  # noqa: E402


def test_no_anchors_falls_back_to_plain_distribute():
    """沒有任何可用錨點時，結果要跟原本的純比例分配完全一樣（不會比舊法更差）。"""
    paras = ["第一段普通文字沒有任何專名。", "第二段也是普通敘述文字。",
             "第三段依然是普通敘述。"]
    weights = [10, 20, 5]
    members = [{"content": "普通中文段落一"}, {"content": "普通中文段落二"},
               {"content": "普通中文段落三"}]
    got = ara.distribute_with_anchors(paras, weights, members)
    want = moc.distribute(paras, weights)
    assert got == want


_FILLER = "padding " * 130  # 刻意撐到遠大於其他段落，撐爆純比例分配的配額


def _sample_paras() -> list[str]:
    return [
        "Some introductory filler paragraph with nothing special in it.",
        "Here we discuss Augustine writing around 1517 in his early works.",
        "A long filler paragraph with unrelated background prose. " + _FILLER,
        "Finally we turn to Calvin writing in 1536 about the institutes.",
    ]


def _sample_members() -> list[dict]:
    return [
        {"content": "簡介文字，沒有特別的錨點內容。"},
        {"content": "提到 Augustine 的觀點（1517年）。"},
        {"content": "提到 Calvin 的觀點（1536年）。"},
        {"content": "結語文字，沒有特別的錨點內容。"},
    ]


def test_find_anchor_breakpoints_orders_by_matching_anchor_text():
    bps = ara.find_anchor_breakpoints(_sample_members(), _sample_paras())
    # member1（Augustine/1517）配到 para1；member2（Calvin/1536）配到 para3。
    assert bps == [(1, 1), (2, 3)]


def test_distribute_with_anchors_fixes_misplacement_vs_plain_proportional():
    """核心迴歸案例：一段又臭又長的填充段落會把純比例分配「撐爆」，
    導致本該屬於後面 chunk 的內容被錯配到前一個 chunk（詹姆斯／伯格兩本書
    實際發生的位移，成因相同：某一段字數異常大，把累計比例的門檻一次衝過
    好幾格）。錨點校正版本應該把帶 Calvin/1536 字樣的段落配到「內容本身也
    提到 Calvin/1536」的那個中譯 chunk，純比例分配版本配不到（會錯配到
    Augustine 那格，Calvin 該拿到的那格反而落空）。
    """
    paras = _sample_paras()
    members = _sample_members()
    weights = [1, 1, 1, 1]  # 四個中譯 chunk 權重相等，位移完全來自段落長度不均

    plain = moc.distribute(paras, weights)
    anchored = ara.distribute_with_anchors(paras, weights, members)

    augustine_para, calvin_para = paras[1], paras[3]
    # 純比例分配：巨大填充段把配額撐爆，Augustine 段被拖進第 0 格，
    # Calvin 段被迫塞進第 1 格（本該給 Calvin 的第 2 格反而是空的）。
    assert augustine_para in plain[0]
    assert calvin_para in plain[1]
    assert plain[2] == ""
    # 錨點校正：兩段都配到「自己內容也提到同一個人名／年份」的那個 chunk。
    assert augustine_para in anchored[1]
    assert calvin_para in anchored[2]


def test_distribute_with_anchors_empty_inputs():
    assert ara.distribute_with_anchors([], [1, 2], [{}, {}]) == ["", ""]
    assert ara.distribute_with_anchors(["x"], [], []) == []


def test_find_anchor_breakpoints_no_anchor_returns_empty():
    paras = ["plain text one", "plain text two"]
    members = [{"content": "普通一"}, {"content": "普通二"}]
    assert ara.find_anchor_breakpoints(members, paras) == []
