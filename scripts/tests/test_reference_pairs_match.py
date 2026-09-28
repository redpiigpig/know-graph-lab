# -*- coding: utf-8 -*-
"""Pure-function tests for scripts/reference_pairs_match.py.

跑法：`pytest scripts/tests/test_reference_pairs_match.py -q`。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import reference_pairs_match as rpm  # noqa: E402


def test_normalize_title_strips_punctuation_and_vol_prefix():
    assert rpm.normalize_title("Vol. 11 St. Chrysostom") == "stchrysostom"
    assert rpm.normalize_title("《基督教要義》（上冊）") == "基督教要義上冊"


def test_title_similarity_containment_boost():
    # 短候選完整包含在較長的目標字串裡：不該被逐字比對的分母拖到門檻以下。
    assert rpm.title_similarity("愚人頌", "愚人頌  [荷]伊拉斯謨") >= 0.9


def test_title_similarity_empty_inputs():
    assert rpm.title_similarity("", "任何") == 0.0
    assert rpm.title_similarity("任何", "") == 0.0


def test_extract_zh_title_candidates_prefers_brackets():
    note = "同書（Richard Baxter, The Sin of Man-Pleasing = 《取悅於人之罪》）"
    assert rpm.extract_zh_title_candidates(note) == ["取悅於人之罪"]


def test_extract_zh_title_candidates_no_bracket_falls_back_to_equal_sign():
    note = "同書＝討好人的罪"
    assert rpm.extract_zh_title_candidates(note) == ["討好人的罪"]


def test_extract_zh_title_candidates_empty():
    assert rpm.extract_zh_title_candidates("") == []
    assert rpm.extract_zh_title_candidates("未中譯，無候選") == []


def test_is_fathers_dup():
    assert rpm.is_fathers_dup("/fathers：NPNF1 Vol 11（uuid）— 與英文原書書目重複編目")
    assert not rpm.is_fathers_dup("同書（《愚人頌》）")
    assert not rpm.is_fathers_dup("")


def test_best_match_prefers_title_field_over_colliding_author_field():
    """回歸案例：2026-09-28 拿《討好人的罪》試跑時，`author` 欄剛好跟另一本
    英文重複記錄一模一樣（1.0 分），但那本其實不是中譯本；`title` 欄裡才
    藏著真正的中譯書名。要挑到含中譯書名的那筆，不能被 author 欄的巧合
    滿分騙走。"""
    ebooks = [
        {"id": "wrong-en-dup", "title": "The Sin of Man-Pleasing - Moder - Richard Baxter",
         "author": "討好人的罪 The Sin of Man-Pleasing"},
        {"id": "correct-zh", "title": "《取悅於人之罪》理查德·巴克斯特The-Sin-of-Man-Pleasing-Baxter",
         "author": "討好人的罪 The Sin of Man-Pleasing"},
    ]
    candidates = ["取悅於人之罪", "討好人的罪 The Sin of Man-Pleasing"]
    row, score, field = rpm.best_match(candidates, ebooks, exclude_id="self")
    assert row is not None
    assert row["id"] == "correct-zh"


def test_best_match_rejects_ambiguous_author_only_tie():
    """`author` 欄常是同作者好幾本書共用的通用短題；候選只在 author 欄打平
    分數、完全指不到特定一本時，寧可回「配不到」也不要賭一把。"""
    ebooks = [
        {"id": "book-a", "title": "和他的工作", "author": "馬丁路德 Martin Luther"},
        {"id": "book-b", "title": "馬丁·路德：The Bondage of the Will",
         "author": "馬丁路德 Martin Luther"},
    ]
    row, score, field = rpm.best_match(["馬丁路德 Martin Luther"], ebooks, exclude_id="self")
    assert row is None


def test_best_match_excludes_non_han_candidates():
    """找的是中譯本，候選書名本身沒有漢字（純英文）的一律不算數——那多半是
    另一本英文原書的重複記錄，不是中譯本。"""
    ebooks = [
        {"id": "en-dup", "title": "Augustine - Confessions and Letters - NPNF1 Vol 1",
         "author": "Augustine of Hippo"},
    ]
    row, score, field = rpm.best_match(["Confessions"], ebooks, exclude_id="self")
    assert row is None
