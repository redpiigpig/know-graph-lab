# -*- coding: utf-8 -*-
"""教父卷中英重新對齊／補譯閘的純函式測試（fathers_realign.py、fathers_fill_gaps.py）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import fathers_realign as fr  # noqa: E402
import fathers_fill_gaps as ff  # noqa: E402

LONG_EN = ("Therefore it is said that the Lord is merciful and just, and that He judges the world "
           "in righteousness; and this we must hold fast. ") * 3
LONG_ZH = "因此經上說主是憐憫的，也是公義的，祂要按公義審判世界；這一點我們必須持守。" * 3


def test_kind_of_distinguishes_body_footnote_and_rule():
    assert fr.kind_of("1. Some body text") == "B"
    assert fr.kind_of("(277) See on Ps. lxxxiv.") == "F"
    assert fr.kind_of("[^15]: 約翰福音 14:26。") == "F"
    assert fr.kind_of("—" * 20) == "S"


def test_clean_rows_drops_tags_and_zero_width_placeholders():
    rows = fr.clean_rows("{{s:3-1}}甲乙丙\n\n​\n\n丁戊")
    assert rows == ["甲乙丙", "丁戊"]


def test_align_matches_by_section_number_and_skips_missing_translation():
    en = [f"{i}. " + LONG_EN for i in range(1, 6)]
    zh = [f"{i}. " + LONG_ZH for i in (1, 2, 4, 5)]          # 第 3 節沒譯
    al = fr.demote_bad(fr.align(zh, en, 0.3), zh, en)
    pairs = {tuple(a): tuple(b) for a, b in al if a and b}
    assert pairs[(0,)] == (0,) and pairs[(1,)] == (1,)
    assert pairs[(2,)] == (3,) and pairs[(3,)] == (4,)
    assert any(not a and b == [2] for a, b in al)            # en 第 3 節 → 缺譯


def test_align_never_pairs_footnote_with_body():
    en = ["1. " + LONG_EN, "—" * 20, "(1) Matt. v. 3 ."]
    zh = ["1. " + LONG_ZH, "—" * 20, "(1) 馬太福音 5:3。"]
    al = fr.align(zh, en, 0.3)
    assert [(a, b) for a, b in al] == [([0], [0]), ([1], [1]), ([2], [2])]


def test_file_en_merges_whole_copies_and_slices_without_duplicating():
    whole = [f"{i}. " + LONG_EN for i in range(1, 7)]
    e, _ = fr.file_en([whole, whole, whole])
    assert e == whole                                        # 整檔重複掛在每塊 → 得到那一份
    e2, _ = fr.file_en([whole[:3], whole[3:]])
    assert e2 == whole                                       # 不重疊的切片 → 依序串接
    e3, _ = fr.file_en([whole, whole[2:4]])
    assert e3 == whole                                       # 切片已在整檔裡 → 不重複


def test_demote_bad_splits_wildly_mismatched_pair():
    en = ["1. " + LONG_EN * 4]
    zh = ["1. 短。"]
    al = fr.demote_bad([([0], [0])], zh, en)
    assert al == [([0], []), ([], [0])]


def test_gate_row_rejects_reply_phrases_ref_mismatch_and_wrong_footnote_number():
    en = "And the Lord said these things [^12] to His disciples, as it is written. " * 2
    ok = "主對祂的門徒說了這些話[^12]，正如經上所記。" * 2
    assert ff.gate_row(ok, en, "B") == ""
    assert ff.gate_row("我注意到您提供的內容是英文，" + ok, en, "B") == "meta-reply"
    assert ff.gate_row(ok.replace("[^12]", ""), en, "B") == "refs-mismatch"
    assert ff.gate_row("(7) 約翰福音 1:1。", "(8) John i. 1 .", "F") == "fn-number"


def test_find_targets_reserves_the_next_paragraph_number():
    c = {"chunk_index": 5, "chapter_path": "第1章",
         "content": "{{s:1-1}}" + LONG_ZH + "\n\n​\n\n{{s:1-3}}" + LONG_ZH,
         "source_text": "1. " + LONG_EN + "\n\n2. " + LONG_EN + "\n\n3. " + LONG_EN, "source_lang": "en"}
    ts = ff.find_targets(c)
    assert len(ts) == 1 and ts[0]["row"] == 1 and ts[0]["n"] == 2 and ts[0]["label"] == "1"


def test_tidy_rows_moves_footnotes_to_chunk_end_with_a_single_rule():
    import fathers_realign_volume as rv
    rule = "—" * 20
    rows = [("甲", "A", 1), (rule, rule, 0), ("(1) 註一", "(1) n1", 1), ("乙", "B", 1),
            (rule, rule, 0), ("(2) 註二", "(2) n2", 1)]
    out = rv.tidy_rows(rows)
    assert [r[1] for r in out] == ["A", "B", fr.FOOT_RULE, "(1) n1", "(2) n2"]
    assert [r[0] for r in out] == ["甲", "乙", fr.FOOT_RULE, "(1) 註一", "(2) 註二"]
