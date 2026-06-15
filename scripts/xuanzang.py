# -*- coding: utf-8 -*-
"""Pure helpers for the 玄奘佛學研究學報 ingest (test-first).

The only genuinely tricky pure bit is turning a Chinese-numeral issue label
（第四十五期玄奘佛學研究學報）into an int. Kept here + tested so the driver
(scripts/xuanzang_journal.py) stays thin.
"""
from __future__ import annotations

import re
from typing import Optional

_CJK_DIGIT = {"零": 0, "〇": 0, "一": 1, "二": 2, "兩": 2, "三": 3, "四": 4,
              "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}


def cjk_numeral(s: str) -> Optional[int]:
    """Parse a Chinese numeral (supports 1–99 with 十) → int. None if unparseable.

    十 → 10, 十五 → 15, 二十 → 20, 四十五 → 45, 三 → 3.
    """
    s = (s or "").strip()
    if not s:
        return None
    if s.isdigit():
        return int(s)
    if "十" not in s:
        # plain digits string e.g. 一二 is ambiguous; only single digit supported
        if len(s) == 1 and s in _CJK_DIGIT:
            return _CJK_DIGIT[s]
        # multi-char without 十 → concatenated digits (rare): 一〇 → 10
        if all(c in _CJK_DIGIT for c in s):
            return int("".join(str(_CJK_DIGIT[c]) for c in s))
        return None
    tens, _, ones = s.partition("十")
    t = _CJK_DIGIT.get(tens, 1) if tens else 1   # 十五 → tens implied 1
    o = _CJK_DIGIT.get(ones, 0) if ones else 0
    if tens and tens not in _CJK_DIGIT:
        return None
    if ones and ones not in _CJK_DIGIT:
        return None
    return t * 10 + o


_ISSUE_RE = re.compile(r"第\s*([零〇一二兩三四五六七八九十\d]+)\s*期")


def parse_issue_no(title: str) -> Optional[int]:
    """第四十五期玄奘佛學研究學報 → 45 (handles Arabic or Chinese numerals)."""
    m = _ISSUE_RE.search(title or "")
    if not m:
        return None
    return cjk_numeral(m.group(1))
