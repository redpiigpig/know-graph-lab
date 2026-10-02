# -*- coding: utf-8 -*-
"""relink_from_epub 的純函式。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import relink_from_epub as rf  # noqa: E402


def test_norm_map_positions():
    nb, pos = rf.norm_map("甲，{{s:1-2}}乙[^3] 丙")
    assert nb == "甲乙丙" and [pos[0], pos[1], pos[2]] == [0, 11, 17]


def test_note_key_strips_leading_number_and_punct():
    assert rf.note_key("(1) 丹纳，《艺术哲学》，人民文学") == rf.note_key("丹納《藝術哲學》人民文學")


def test_split_notes_keeps_continuation_lines():
    assert rf.split_notes("(1) 註一\n續行\n(2) 註二\n") == [(1, "註一\n續行"), (2, "註二")]


def test_renumber_by_appearance_and_moved_tags():
    body = "甲[^@1]乙[^2]丙"
    b, ns = rf.renumber(body, [("2", "舊二"), ("@1", "搬來的"), ("9", "沒引用")])
    assert b == "甲[^1]乙[^2]丙"
    assert ns == "(1) 搬來的\n(2) 舊二\n(3) 沒引用\n"


def test_split_notes_number_on_own_line():
    assert rf.split_notes("\n(1)\n  註一\n\n(2)\n 註二") == [(1, "註一"), (2, "註二")]


def test_renumber_keeps_duplicate_numbers():
    b, ns = rf.renumber("甲[^1]乙[^@1]丙", [("1", "第一章註一"), ("1", "第二章註一"), ("@1", "搬來的")])
    assert b == "甲[^1]乙[^2]丙"
    assert ns == "(1) 第一章註一\n(2) 搬來的\n(3) 第二章註一\n"
