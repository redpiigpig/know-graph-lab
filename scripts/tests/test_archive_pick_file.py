# -*- coding: utf-8 -*-
"""archive.org 下載時挑哪個檔（archive_org_fetch.pick_file）。

🚨 Google 掃描的項目（identifier 以 `goog` 結尾）**PDF 沒有文字層**：
下載回來 527 頁的《Einleitung in die Religionswissenschaft》全書只有 3,467 字，
而且那些字全是 Google 的版權聲明（"This is a digital copy of a book…"）。
檔案大小、頁數、下載流程全部正常，只有內容是空的 —— 要拿同一個項目的
`_djvu.txt` 才有正文。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from archive_org_fetch import pick_file  # noqa: E402


def _f(name, size):
    return {"name": name, "size": str(size)}


FILES = [
    _f("book.pdf", 8_000_000),
    _f("book_bw.pdf", 6_000_000),
    _f("book_djvu.txt", 1_100_000),
    _f("book.epub", 2_000_000),
]


class TestPickFile:
    def test_pdf_wins_for_a_normal_item(self):
        name, ext, _ = pick_file(FILES, "elementsofthesci01tieluoft")
        assert ext == ".pdf" and name == "book.pdf"

    def test_google_scan_prefers_djvu_txt(self):
        name, ext, _ = pick_file(FILES, "einleitungindie00gehrgoog")
        assert ext == ".txt" and name == "book_djvu.txt"

    def test_google_scan_falls_back_to_pdf_when_no_djvu_txt(self):
        files = [_f("book.pdf", 8_000_000)]
        name, ext, _ = pick_file(files, "lehrbuchderreli00sausgoog")
        assert ext == ".pdf"

    def test_identifier_is_optional(self):
        assert pick_file(FILES)[1] == ".pdf"

    def test_goog_must_be_the_suffix_not_anywhere(self):
        # 「googlebooks-xyz」開頭含 goog 但不是 Google 掃描件的命名慣例
        assert pick_file(FILES, "googlyitem00abc")[1] == ".pdf"

    def test_tiny_files_are_skipped(self):
        files = [_f("index.pdf", 1000), _f("book_djvu.txt", 900_000)]
        name, ext, _ = pick_file(files, "x")
        assert name == "book_djvu.txt"

    def test_text_pdf_variant_is_skipped(self):
        files = [_f("book_text.pdf", 39_000_000), _f("book.pdf", 20_000_000)]
        assert pick_file(files, "x")[0] == "book.pdf"

    def test_nothing_usable(self):
        assert pick_file([_f("book_meta.xml", 900_000)], "x") is None
