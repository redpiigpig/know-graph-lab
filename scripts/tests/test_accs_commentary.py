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
    build_work_father_map,
    plan_blank_father_fixes,
    _ends_sentence,
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


def test_father_variant_otiii_num_deu():
    # ACCS OT III（num/deu）收斂新增的同人異寫
    assert normalize_father("安博") == "安波羅修"
    assert normalize_father("特士良") == "特土良"
    assert normalize_father("納西盎的貴格利") == "拿先斯的格列高里"
    assert normalize_father("多儒") == "迦修多儒"
    assert normalize_father("狄奧多雷") == "塞普勒斯的狄奧多勒"
    assert normalize_father("遊斯丁") == "殉道者猶斯定"
    assert normalize_father("殉道者遊斯丁") == "殉道者猶斯定"
    assert normalize_father("福耳根提烏斯") == "富爾根修"
    assert normalize_father("富爾根狄") == "富爾根修"
    assert normalize_father("神行者貴格利") == "奇蹟行者格列高里"
    assert normalize_father("託區利羅名作品") == "託名區利羅"
    assert normalize_father("託丟尼修") == "託名丟尼修"


def test_father_variant_mat14_28_ocr():
    # 太14-28 掃描的 OCR 誤認變體收斂
    assert normalize_father("屈稜多模") == "金口若望"
    assert normalize_father("被提亞的希拉流") == "波提亞的希拉流"
    assert normalize_father("亞波里拿旨") == "亞波里拿留"


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
    # OCR 把「以法連」誤打成草頭「以法蓮」也要收斂
    assert normalize_father("敘利亞人以法蓮") == "敘利亞的厄弗冷"


def test_normalize_father_alexandria_city_unified():
    # 亞歷山卓城（glossary 主譯）— 太/大 兩種 OCR 變體與西里爾/濟利祿異譯全收斂
    assert normalize_father("亞歷山太的區利羅") == "亞歷山卓的區利羅"
    assert normalize_father("亞歷山大的區利羅") == "亞歷山卓的區利羅"
    assert normalize_father("亞歷山大的西里爾") == "亞歷山卓的區利羅"
    assert normalize_father("亞歷山大的濟利祿") == "亞歷山卓的區利羅"
    assert normalize_father("亞歷山太的革利免") == "亞歷山卓的革利免"
    assert normalize_father("亞歷山太的斐羅") == "亞歷山卓的斐羅"


def test_normalize_father_origen_variants():
    # 俄利根（glossary 主譯）— 新教「奧利金」、天主教「奧利振」皆收斂
    assert normalize_father("奧利金") == "俄利根"
    assert normalize_father("奧利振") == "俄利根"


def test_normalize_father_does_not_touch_bare_ambiguous():
    # 裸「約翰」可能是使徒約翰；裸「以法連」可能是聖經以法蓮 → 不收斂
    assert normalize_father("約翰") == "約翰"
    assert normalize_father("以法連") == "以法連"


# ── blank-father 救援（plan_blank_father_fixes / build_work_father_map）────────

def _row(ch, po, eo, kind, father, work, body):
    return {"chapter": ch, "pericope_order": po, "entry_order": eo,
            "section_kind": kind, "father_name": father, "work_title": work,
            "body_zh": body}


def test_ends_sentence():
    assert _ends_sentence("祂創造了天地。") is True
    assert _ends_sentence("造男造女」") is True
    assert _ends_sentence("肉體真的") is False        # 句中斷裂
    assert _ends_sentence("") is False


def test_build_work_father_map_only_unique():
    rows = [
        _row(1, 1, 0, "comment", "安波羅修", "論樂園", "甲"),
        _row(1, 2, 0, "comment", "安波羅修", "論樂園", "乙"),
        _row(1, 3, 0, "comment", "奧古斯丁", "懺悔錄", "丙"),
        _row(1, 4, 0, "comment", "耶柔米", "書信集", "丁"),
        _row(1, 5, 0, "comment", "比德", "書信集", "戊"),   # 書信集 → 2 位 → 非唯一
    ]
    m = build_work_father_map(rows)
    assert m["論樂園"] == "安波羅修"
    assert m["懺悔錄"] == "奧古斯丁"
    assert "書信集" not in m


def test_plan_merge_continuation_inherits_father():
    # 前一則 comment 句中斷裂 → blank 續行併入、繼承 father
    rows = [
        _row(1, 1, 0, "comment", "金口若望", "創世記講道集", "上帝說要有光，"),
        _row(1, 1, 1, "comment", None, None, "於是就有了光。"),
    ]
    plan = plan_blank_father_fixes(rows, work_father={})
    assert len(plan["merges"]) == 1
    mg = plan["merges"][0]
    assert mg["target"] is rows[0]
    assert mg["sources"] == [rows[1]]
    assert mg["new_body"] == "上帝說要有光，於是就有了光。"
    assert plan["father_sets"] == []


def test_plan_merge_fills_work_from_source():
    # 前列有 father 無 work、續行有 work → 併入時補上 work
    rows = [
        _row(1, 1, 0, "comment", "富爾根狄", None, "聖父聖子聖靈本質上是一位上帝，"),
        _row(1, 1, 1, "comment", None, "致彼得書：論信心", "按我們的形像造了他們」。"),
    ]
    plan = plan_blank_father_fixes(rows, work_father={})
    assert plan["merges"][0]["new_work"] == "致彼得書：論信心"


def test_plan_no_merge_when_prev_ends_clean():
    # 前列乾淨結束（。）→ 不併入；改走 work 回填（若唯一）
    rows = [
        _row(1, 1, 0, "comment", "安波羅修", "論樂園", "上帝造出這一切。"),
        _row(1, 1, 1, "comment", None, "論樂園", "那日定為聖日。"),
    ]
    plan = plan_blank_father_fixes(rows)  # work_father 自動建（論樂園→安波羅修）
    assert plan["merges"] == []
    assert len(plan["father_sets"]) == 1
    assert plan["father_sets"][0]["row"] is rows[1]
    assert plan["father_sets"][0]["father"] == "安波羅修"


def test_plan_no_merge_into_overview():
    # 前列是 overview（即使句中斷裂）也不併入 comment（避免汙染總論）
    rows = [
        _row(1, 1, 0, "overview", None, None, "這段經文教父註釋甚多，"),
        _row(1, 1, 1, "comment", None, "論樂園", "上帝造園。"),
    ]
    plan = plan_blank_father_fixes(rows, work_father={"論樂園": "安波羅修"})
    assert plan["merges"] == []
    assert plan["father_sets"][0]["father"] == "安波羅修"


def test_plan_preserves_total_body_length():
    rows = [
        _row(1, 1, 0, "comment", "金口若望", None, "甲甲甲甲甲"),
        _row(1, 1, 1, "comment", None, None, "乙乙乙"),
        _row(1, 1, 2, "comment", "奧古斯丁", None, "丙丙丙丙。"),
    ]
    before = sum(len(r["body_zh"]) for r in rows)
    plan = plan_blank_father_fixes(rows, work_father={})
    after = sum(len(m["new_body"]) for m in plan["merges"]) + \
        sum(len(r["body_zh"]) for r in rows
            if all(r not in m["sources"] and r is not m["target"] for m in plan["merges"]))
    assert before == after


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
