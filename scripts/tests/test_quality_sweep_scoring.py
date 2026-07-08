# -*- coding: utf-8 -*-
"""Tests for scripts/quality_sweep.py — 全館轉錄品質計分核心（純規則零 LLM）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from quality_sweep import (  # noqa: E402
    BookSignals,
    score_book_quality,
    TIER_REOCR,
    TIER_RESTANDARDIZE,
    TIER_FIX_TOC,
    TIER_GOOD,
    TIER_FAIR,
)


def sig(**kw) -> BookSignals:
    """健康章節書的基準訊號，測試逐項覆寫。"""
    base = dict(
        n_chunks=100,
        blank_rate=0.0,
        no_toc_rate=0.0,
        tiny_rate=0.0,
        giant_n=0,
        mess_wo_toc=0.0,
        per_page_only=False,
        needs_ocr=False,
        path_broken=False,
        standardized=True,
    )
    base.update(kw)
    return BookSignals(**base)


def test_healthy_book_is_good_100():
    score, flags, tier = score_book_quality(sig())
    assert score == 100
    assert flags == []
    assert tier == TIER_GOOD


def test_needs_ocr_is_zero_and_reocr():
    score, flags, tier = score_book_quality(sig(needs_ocr=True))
    assert score == 0
    assert "NEEDS_OCR" in flags
    assert tier == TIER_REOCR


def test_blank_over_half_forces_reocr():
    score, flags, tier = score_book_quality(sig(blank_rate=0.6))
    assert tier == TIER_REOCR
    assert "BLANK_BODY" in flags
    assert score <= 50


def test_blank_penalty_caps_at_50():
    s_60, _, _ = score_book_quality(sig(blank_rate=0.6))
    s_99, _, _ = score_book_quality(sig(blank_rate=0.99))
    assert s_60 == s_99 == 50  # min(50, rate×100)


def test_no_toc_penalty_20():
    score, flags, _ = score_book_quality(sig(no_toc_rate=0.95))
    assert score == 80
    assert "NO_TOC" in flags


def test_partial_toc_penalty_10():
    score, flags, _ = score_book_quality(sig(no_toc_rate=0.5))
    assert score == 90
    assert "PARTIAL_TOC" in flags


def test_page_type_book_exempt_from_toc_and_frag_penalty():
    """822 本逐頁書不因無章節/逐頁碎片扣分 — 只記 flag。"""
    score, flags, tier = score_book_quality(
        sig(per_page_only=True, no_toc_rate=1.0, tiny_rate=0.6)
    )
    assert score == 100
    assert "PER_PAGE_ONLY" in flags
    assert "NO_TOC" not in flags
    assert tier == TIER_GOOD


def test_over_fragmented_penalty():
    score, flags, _ = score_book_quality(sig(tiny_rate=0.5))
    assert score == 85
    assert "OVER_FRAGMENTED" in flags


def test_giant_chunk_penalty():
    score, flags, _ = score_book_quality(sig(giant_n=2))
    assert score == 85
    assert "UNDER_SEGMENTED" in flags


def test_mess_penalty_caps_at_20():
    score, flags, _ = score_book_quality(sig(mess_wo_toc=100.0))
    assert score == 80
    assert "STRUCTURE_MESS" in flags


def test_score_clamped_at_zero():
    score, _, _ = score_book_quality(
        sig(blank_rate=0.49, no_toc_rate=1.0, tiny_rate=0.5, giant_n=1, mess_wo_toc=100.0)
    )
    assert score == 0


def test_fix_toc_tier_when_only_defect_is_toc():
    """章節書只缺目錄 → FIX_TOC（餵 fix_book_structure.py）。"""
    _, _, tier = score_book_quality(sig(no_toc_rate=0.95))
    assert tier == TIER_FIX_TOC


def test_restandardize_tier_structural():
    """已標準化但結構爛（非空白主因）→ RESTANDARDIZE。"""
    score, _, tier = score_book_quality(
        sig(no_toc_rate=0.95, tiny_rate=0.5, giant_n=1, mess_wo_toc=60.0)
    )
    assert score < 60
    assert tier == TIER_RESTANDARDIZE


def test_not_standardized_never_restandardize():
    """沒標準化過的書不能進 RESTANDARDIZE（要先走正常 pipeline）。"""
    _, flags, tier = score_book_quality(
        sig(standardized=False, no_toc_rate=0.95, tiny_rate=0.5, mess_wo_toc=60.0)
    )
    assert "NOT_STANDARDIZED" in flags
    assert tier != TIER_RESTANDARDIZE


def test_path_broken_flag_and_never_reocr():
    """檔案路徑壞 → 不能進 REOCR 佇列（沒檔可 OCR）。"""
    _, flags, tier = score_book_quality(sig(path_broken=True, blank_rate=0.8))
    assert "PATH_BROKEN" in flags
    assert tier != TIER_REOCR


def test_fair_band():
    score, _, tier = score_book_quality(sig(no_toc_rate=0.5, tiny_rate=0.5, giant_n=1))
    assert 60 <= score < 80
    assert tier == TIER_FAIR
