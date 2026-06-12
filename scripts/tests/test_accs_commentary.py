"""Tests for scripts/accs_commentary.py — the pure ACCS-commentary core."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from accs_commentary import (  # noqa: E402
    parse_verse_range,
    normalize_father,
    build_rows,
)


# ── parse_verse_range ────────────────────────────────────────────────────────

def test_single_verse_with_chapter():
    assert parse_verse_range("1:1", 1) == (1, 1)


def test_range_hyphen():
    assert parse_verse_range("1:1-2", 1) == (1, 2)


def test_range_en_dash():
    assert parse_verse_range("1:3–5", 1) == (3, 5)


def test_range_em_dash_and_spaces():
    assert parse_verse_range(" 1 : 24 — 31 ", 1) == (24, 31)


def test_book_prefix_stripped():
    assert parse_verse_range("創 1:5", 1) == (5, 5)
    assert parse_verse_range("Gen 2:4-7", 2) == (4, 7)


def test_bare_verse_no_chapter():
    assert parse_verse_range("9", 1) == (9, 9)
    assert parse_verse_range("9-14", 1) == (9, 14)


def test_fullwidth_colon():
    assert parse_verse_range("1：26", 1) == (26, 26)


def test_cross_chapter_clamped_to_start():
    # 1:30-2:3 跨章 → 夾到本章起節
    assert parse_verse_range("1:30-2:3", 1) == (30, 30)


def test_reversed_range_clamped():
    assert parse_verse_range("1:5-3", 1) == (5, 5)


def test_garbage_returns_none():
    assert parse_verse_range("總論", 1) is None
    assert parse_verse_range("", 1) is None


# ── normalize_father ─────────────────────────────────────────────────────────

def test_father_variant_to_glossary():
    assert normalize_father("屈梭多模") == "金口若望"
    assert normalize_father(" 金口约翰 ") == "金口若望"
    assert normalize_father("巴西略") == "巴西流"


def test_father_passthrough_unknown():
    assert normalize_father("愛任紐") == "愛任紐"


def test_father_strips_brackets_and_space():
    assert normalize_father("「奧古斯丁」") == "奧古斯丁"
    assert normalize_father("奧古 斯丁") == "奧古斯丁"


def test_father_empty_is_none():
    assert normalize_father("") is None
    assert normalize_father(None) is None


# ── build_rows ───────────────────────────────────────────────────────────────

def _sample_entries():
    return [
        {"ref": "1:1-2", "kind": "overview", "heading": "起初的創造",
         "body": "編者導語：論天地受造……"},
        {"ref": "1:1-2", "kind": "comment", "father": "巴西略", "work": "創世六日",
         "body": "神的『起初』非時間之始……"},
        {"ref": "1:1-2", "kind": "comment", "father": "屈梭多模", "work": "創世講道",
         "body": "摩西以樸實之言……"},
        {"ref": "1:3-5", "kind": "comment", "father": "奧古斯丁", "work": "創世釋義",
         "body": "光的受造……"},
    ]


def test_build_rows_pericope_and_entry_order():
    rows = build_rows("gen", 1, _sample_entries(), "ACCS OT I（創 1–11）")
    assert len(rows) == 4
    # 兩個段落
    assert rows[0]["pericope_order"] == 1
    assert rows[1]["pericope_order"] == 1
    assert rows[2]["pericope_order"] == 1
    assert rows[3]["pericope_order"] == 2
    # 段落內 entry_order 由 0 累加
    assert [r["entry_order"] for r in rows] == [0, 1, 2, 0]
    # 節範圍
    assert (rows[3]["verse_start"], rows[3]["verse_end"]) == (3, 5)


def test_build_rows_overview_has_no_father():
    rows = build_rows("gen", 1, _sample_entries(), "vol")
    ov = rows[0]
    assert ov["section_kind"] == "overview"
    assert ov["father_name"] is None
    assert ov["work_title"] is None


def test_build_rows_normalizes_father_in_row():
    rows = build_rows("gen", 1, _sample_entries(), "vol")
    assert rows[1]["father_name"] == "巴西流"   # 巴西略 → 巴西流
    assert rows[2]["father_name"] == "金口若望"  # 屈梭多模 → 金口若望


def test_build_rows_skips_empty_body_and_bad_ref():
    entries = [
        {"ref": "1:1", "kind": "comment", "father": "巴西流", "body": "   "},
        {"ref": "亂碼", "kind": "comment", "father": "巴西流", "body": "有內容"},
        {"ref": "1:1", "kind": "comment", "father": "巴西流", "body": "真正內容"},
    ]
    rows = build_rows("gen", 1, entries, "vol")
    assert len(rows) == 1
    assert rows[0]["body_zh"] == "真正內容"


def test_build_rows_bad_kind_defaults_comment():
    entries = [{"ref": "1:1", "kind": "xxx", "father": "巴西流", "body": "x"}]
    rows = build_rows("gen", 1, entries, "vol")
    assert rows[0]["section_kind"] == "comment"
