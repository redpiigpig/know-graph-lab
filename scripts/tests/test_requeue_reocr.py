# -*- coding: utf-8 -*-
"""Tests for scripts/requeue_reocr.py — staged gate（重 OCR 不可破壞既有良好資料）。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from requeue_reocr import staged_gate, jsonl_stats  # noqa: E402


def chunks(texts, start_page=1):
    return [{"chunk_index": i, "chunk_type": "page", "page_number": start_page + i,
             "chapter_path": None, "content": t} for i, t in enumerate(texts)]


BLANK_OLD = chunks(["", "", "這一頁有完整可讀的正文內容存在" * 10, ""])  # 3/4 空白
GOOD_NEW = chunks(["這是完整的一頁內容" * 20] * 4)  # 4 頁全滿


def test_improved_reocr_passes():
    ok, problems = staged_gate(BLANK_OLD, GOOD_NEW)
    assert ok, problems


def test_empty_new_rejected():
    ok, problems = staged_gate(BLANK_OLD, [])
    assert not ok


def test_page_coverage_loss_rejected():
    new = chunks(["內容豐富" * 50] * 2)  # 只到第 2 頁，舊檔到第 4 頁
    ok, problems = staged_gate(BLANK_OLD, new)
    assert not ok
    assert any("page coverage" in p for p in problems)


def test_no_blank_improvement_rejected():
    still_blank = chunks(["", "", "另一頁有完整可讀的正文內容存在" * 10, ""])
    ok, problems = staged_gate(BLANK_OLD, still_blank)
    assert not ok
    assert any("blank_rate" in p for p in problems)


def test_noncontiguous_index_rejected():
    new = [dict(c) for c in GOOD_NEW]
    new[2]["chunk_index"] = 99
    ok, problems = staged_gate(BLANK_OLD, new)
    assert not ok
    assert any("chunk_index" in p for p in problems)


def test_good_old_file_not_forced_to_improve():
    """舊檔本來就好（blank≤5%）→ 不因空白率沒改善而擋。"""
    good_old = chunks(["原本就有內容" * 30] * 4)
    ok, problems = staged_gate(good_old, GOOD_NEW)
    assert ok, problems


def test_stats():
    s = jsonl_stats(BLANK_OLD)
    assert s["n"] == 4 and s["max_page"] == 4 and s["blank_rate"] == 0.75
