# -*- coding: utf-8 -*-
"""Test-first contract for scripts/xuanzang.py (玄奘佛學研究學報 ingest)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import xuanzang as xz  # noqa: E402


@pytest.mark.parametrize("s,n", [
    ("三", 3), ("十", 10), ("十五", 15), ("二十", 20), ("四十五", 45),
    ("九十九", 99), ("一", 1), ("40", 40), ("〇", 0),
])
def test_cjk_numeral(s, n):
    assert xz.cjk_numeral(s) == n


def test_cjk_numeral_bad():
    assert xz.cjk_numeral("") is None
    assert xz.cjk_numeral("甲") is None


@pytest.mark.parametrize("title,n", [
    ("第四十五期玄奘佛學研究學報", 45),
    ("第一期玄奘佛學研究學報", 1),
    ("第二十二期玄奘佛學研究學報", 22),
    ("第 40 期玄奘佛學研究學報", 40),
])
def test_parse_issue_no(title, n):
    assert xz.parse_issue_no(title) == n


def test_parse_issue_no_none():
    assert xz.parse_issue_no("徵稿啟事") is None
