# -*- coding: utf-8 -*-
"""鎖住 DB 版頁碼稽核的分類判準。

最關鍵的一條是：**serial 不等於假**。一頁一 chunk 的 PDF 本來就滿足
`page_number == chunk_index + 1`，那個頁碼是真的。不分這一刀，全庫會從
「51 本待修」變成「1,146 本待修」——差二十倍。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from audit_page_numbers_db import classify  # noqa: E402


def test_epub_running_serial_is_fabricated():
    """EPUB 沒有版面就沒有頁碼，逐一遞增只可能是 chunk_index+1 冒充的。"""
    assert classify(152, 152, 152, "epub") == "serial-epub"


def test_pdf_running_serial_is_genuine_page_per_chunk():
    assert classify(4655, 4655, 4655, "pdf") == "serial-pdf"


def test_unknown_file_type_is_treated_as_suspect():
    """不知道格式時往嚴的一邊倒——寧可多查一本，不可放過一本假頁碼。"""
    assert classify(100, 100, 100, "") == "serial-epub"


def test_repeated_and_skipped_pages_are_real():
    """同一頁多個 chunk（重複）或跳號 → 真頁碼。"""
    assert classify(100, 100, 2, "epub") == "real"
    assert classify(100, 100, 2, "pdf") == "real"


def test_all_null_is_none():
    assert classify(100, 0, 0, "epub") == "none"


def test_partial_fill_is_sparse():
    assert classify(100, 60, 60, "pdf") == "sparse"


def test_empty_book():
    assert classify(0, 0, 0, "pdf") == "empty"


def test_ratio_boundary_just_under_threshold_is_real():
    """九成五是門檻：94% 命中還算真頁碼（可能只是前半本剛好對齊）。"""
    assert classify(100, 100, 94, "epub") == "real"
    assert classify(100, 100, 95, "epub") == "serial-epub"


def test_tiny_book_needs_at_least_three_hits():
    """兩個 chunk 全中不算數——樣本太小，任何頁碼都可能長這樣。"""
    assert classify(2, 2, 2, "epub") == "real"
    assert classify(3, 3, 3, "epub") == "serial-epub"
