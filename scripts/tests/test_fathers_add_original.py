# -*- coding: utf-8 -*-
"""逐卷重編章號 → 整部連續號的換算。

阿諾比烏《駁異教徒》的中譯 chapter_path 是整部連續號（第71-80章），內文編號卻是
逐卷重編的（第二卷第六章寫成「6.」）。這兩支負責在兩種編號之間換算，換不出唯一
答案就回 None——因為猜錯的後果是七卷全部配到第一卷的拉丁文，而且看起來完全正常。
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "fathers_add_original", ROOT / "scripts" / "fathers_add_original.py")
AO = importlib.util.module_from_spec(_spec)
sys.modules["fathers_add_original"] = AO
_spec.loader.exec_module(AO)

FO = AO.FO
# 阿諾比烏七卷實際章數
BY_BOOK = {(b, n): "x" for b, size in
           enumerate([65, 78, 44, 37, 45, 27, 34], start=1)
           for n in range(1, size + 1)}


def test_bases_are_cumulative():
    assert AO.cumulative_bases(BY_BOOK) == {
        1: 0, 2: 65, 3: 143, 4: 187, 5: 224, 6: 269, 7: 296}


def test_first_book_needs_no_offset():
    assert AO.resolve_continuous(5, FO.Span(None, 1, 10),
                                 AO.cumulative_bases(BY_BOOK)) == 5


def test_second_book_chapter_six_is_not_chapter_six():
    # 站上標「第71-80章」而內文寫「6.」→ 第二卷第六章＝整部第 71 章
    assert AO.resolve_continuous(6, FO.Span(None, 71, 80),
                                 AO.cumulative_bases(BY_BOOK)) == 71


def test_last_book():
    assert AO.resolve_continuous(1, FO.Span(None, 291, 300),
                                 AO.cumulative_bases(BY_BOOK)) == 297


def test_no_fit_returns_none():
    # 沒有任何一卷的基底能把 6 送進 [201,210]，寧可空著也不硬塞
    assert AO.resolve_continuous(6, FO.Span(None, 201, 210),
                                 AO.cumulative_bases(BY_BOOK)) is None


def test_ambiguous_returns_none():
    # 兩卷都塞得進同一段時不猜
    bases = {1: 0, 2: 5}
    assert AO.resolve_continuous(3, FO.Span(None, 1, 10), bases) is None


def test_single_book_has_no_offset():
    assert AO.cumulative_bases({(1, n): "x" for n in range(1, 46)}) == {1: 0}
