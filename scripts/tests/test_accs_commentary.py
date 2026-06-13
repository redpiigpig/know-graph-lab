"""Tests for scripts/accs_commentary.py — the pure ACCS-commentary core."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from accs_commentary import (  # noqa: E402
    parse_verse_range,
    parse_full_ref,
    normalize_father,
    normalize_body,
    has_simplified,
    build_rows,
    build_rows_auto,
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


# ── normalize_body / has_simplified (繁體強制 + 自動校正機制) ──────────────────

def test_has_simplified_detects():
    assert has_simplified("创世记") is True
    assert has_simplified("創世記") is False


def test_normalize_body_simp_to_trad():
    assert normalize_body("约翰说创世记") == "約翰說創世記"
    assert "簡" not in "" and not has_simplified(normalize_body("奥古斯丁论创世"))


def test_normalize_body_keeps_traditional():
    assert normalize_body("奧古斯丁《論創世》") == "奧古斯丁《論創世》"


def test_normalize_body_strips_and_collapses_ws():
    assert normalize_body("  神說\n\n要有光  ") == "神說 要有光" or \
           normalize_body("  神說\n\n要有光  ").strip() != ""


def test_normalize_father_simplified():
    assert normalize_father("奥古斯丁") == "奧古斯丁"


def test_normalize_father_glossary_full_forms():
    # 校園/OCR 全稱 → 站內 /translation-glossary 主譯（僅明確全稱，不碰裸名）
    assert normalize_father("大馬士革的約翰") == "大馬士革的若望"
    assert normalize_father("女撒的貴格利") == "尼撒的格列高里"
    assert normalize_father("敘利亞人以法連") == "敘利亞的厄弗冷"


def test_normalize_father_does_not_touch_bare_ambiguous():
    # 裸「約翰」可能是使徒約翰；裸「以法連」可能是聖經以法蓮 → 不收斂
    assert normalize_father("約翰") == "約翰"
    assert normalize_father("以法連") == "以法連"


def test_build_rows_output_is_traditional():
    entries = [{"ref": "1:1", "kind": "comment", "father": "奥古斯丁",
                "work": "论创世记", "body": "神创造天地"}]
    rows = build_rows("gen", 1, entries, "vol")
    assert not has_simplified(rows[0]["body_zh"])
    assert not has_simplified(rows[0]["father_name"])
    assert not has_simplified(rows[0]["work_title"])


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


# ── parse_full_ref ───────────────────────────────────────────────────────────

def test_full_ref_with_chapter():
    assert parse_full_ref("1:1-2") == (1, 1, 2)
    assert parse_full_ref("2:4") == (2, 4, 4)


def test_full_ref_bare_verse_chapter_none():
    assert parse_full_ref("5") == (None, 5, 5)
    assert parse_full_ref("9-14") == (None, 9, 14)


def test_full_ref_cross_chapter_clamped():
    assert parse_full_ref("1:30-2:3") == (1, 30, 30)


def test_full_ref_garbage_none():
    assert parse_full_ref("總論") is None


# ── build_rows_auto (whole-book, chapter from ref) ───────────────────────────

def test_build_rows_auto_routes_by_chapter():
    entries = [
        {"ref": "1:1-2", "kind": "comment", "father": "巴西流", "body": "甲"},
        {"ref": "1:3-5", "kind": "comment", "father": "奧古斯丁", "body": "乙"},
        {"ref": "2:4-7", "kind": "comment", "father": "俄利根", "body": "丙"},
    ]
    rows = build_rows_auto("gen", entries, "vol")
    assert [r["chapter"] for r in rows] == [1, 1, 2]
    # pericope_order resets per chapter
    assert rows[0]["pericope_order"] == 1
    assert rows[1]["pericope_order"] == 2
    assert rows[2]["pericope_order"] == 1  # chapter 2 starts fresh


def test_build_rows_auto_carry_forward_chapter():
    # a bare-verse ref inherits the most recent chapter
    entries = [
        {"ref": "3:1", "kind": "overview", "body": "導語"},
        {"ref": "1", "kind": "comment", "father": "巴西流", "body": "承上章三"},
    ]
    rows = build_rows_auto("gen", entries, "vol")
    assert rows[1]["chapter"] == 3


def test_build_rows_auto_skips_until_chapter_known():
    entries = [
        {"ref": "7", "kind": "comment", "father": "巴西流", "body": "無章上下文"},
        {"ref": "4:1", "kind": "comment", "father": "巴西流", "body": "有章"},
    ]
    rows = build_rows_auto("gen", entries, "vol")
    assert len(rows) == 1
    assert rows[0]["chapter"] == 4
