"""Transcription pain point #1 — 目錄 / 正文 章節分類.

These pure heuristics in standardize_ebook.py decide what becomes a chapter,
what is a volume divider, what is appendix/front-matter, and what title the
sidebar shows. Misclassification here is exactly the "目錄、正文分類瑕疵" the
user reported, so the tests assert the *intended* behavior (from docstrings +
the skill docs) — a failure means the heuristic diverges from intent.
"""
import pytest

import standardize_ebook as se


# ── normalize_chapter_title — cosmetic boilerplate renames ──────────────────
class TestNormalizeChapterTitle:
    def test_cip_data_becomes_copyright_page(self):
        assert se.normalize_chapter_title("圖書在版編目(CIP)數據") == "版權頁"
        assert se.normalize_chapter_title("图书在版编目（CIP）数据") == "版權頁"

    def test_cip_prefix_uppercase(self):
        assert se.normalize_chapter_title("CIP Data") == "版權頁"

    def test_copyright_variants_unified(self):
        for v in ("版權信息", "版权信息", "版權頁", "版权页"):
            assert se.normalize_chapter_title(v) == "版權頁"

    def test_real_chapter_title_untouched(self):
        assert se.normalize_chapter_title("第一章　緒論") == "第一章　緒論"

    def test_blank(self):
        assert se.normalize_chapter_title("   ") == ""
        assert se.normalize_chapter_title(None) == ""


# ── is_continuation_title — merged into previous chunk, not standalone ──────
class TestIsContinuationTitle:
    def test_single_numeral_marker(self):
        for t in ("一", "二", "十一", "1", "23", "A", "b", "二、", "3."):
            assert se.is_continuation_title(t), t

    def test_empty_is_continuation(self):
        assert se.is_continuation_title("")
        assert se.is_continuation_title("   ")

    def test_real_titles_are_not_continuations(self):
        for t in ("第一章", "緒論", "前言", "王權的誕生"):
            assert not se.is_continuation_title(t), t

    def test_four_digit_number_is_not_continuation(self):
        # _CONT_RX caps digits at 1-3, so a 4-digit run (e.g. a year) is a
        # real token, not a list marker.
        assert not se.is_continuation_title("1984")


# ── looks_like_volume — only 卷/冊/部/集/篇 may become a volume ───────────────
class TestLooksLikeVolume:
    def test_volume_markers(self):
        for t in ("第一卷", "上冊", "第三部", "第二集", "外篇"):
            assert se.looks_like_volume(t), t

    def test_non_volumes_rejected(self):
        # The whole point: 目錄/插頁/出版說明/緒論 must NOT be promoted to volumes
        # in a single-volume book.
        for t in ("目錄", "插頁", "出版說明", "緒論", "前言", "第一章"):
            assert not se.looks_like_volume(t), t


# ── _is_chapter_title vs _is_appendix_title ─────────────────────────────────
class TestChapterAndAppendixDetection:
    def test_chapter_titles(self):
        for t in ("第一章", "第3回", "第十二講", "Chapter 5", "1. Introduction", "1、緒論"):
            assert se._is_chapter_title(t), t

    def test_non_chapters(self):
        for t in ("緒論", "附錄", "索引", "前言", ""):
            assert not se._is_chapter_title(t), t

    def test_appendix_titles(self):
        for t in ("索引", "附錄", "參考文獻", "延伸閱讀", "年表", "致謝",
                  "Bibliography", "Index", "Glossary", "譯名對照"):
            assert se._is_appendix_title(t), t

    def test_real_chapter_is_not_appendix(self):
        for t in ("第一章　緒論", "導論", "Chapter 1"):
            assert not se._is_appendix_title(t), t


# ── derive_chapter_title — picking the sidebar label from chunk markdown ────
class TestDeriveChapterTitle:
    def test_uses_first_real_heading(self):
        md = "## 第一章　緒論\n\n這是內文。"
        assert se.derive_chapter_title(md, "file.html") == "第一章　緒論"

    def test_skips_numeric_marker_heading(self):
        # Academic EPUB pattern: <h2>1</h2><h1>Real Title</h1>
        md = "## 1\n\n## 知識的起源\n\n內文"
        assert se.derive_chapter_title(md, "file.html") == "知識的起源"

    def test_combines_numeric_marker_with_following_short_line(self):
        # Publisher pattern <h2>01</h2><p>王權的誕生</p>
        md = "#### 01\n\n王權的誕生\n\n正文開始……"
        assert se.derive_chapter_title(md, "file.html") == "01 王權的誕生"

    def test_cip_content_detected(self):
        md = "圖書在版編目(CIP)數據\n\n書名：……"
        assert se.derive_chapter_title(md, "file.html") == "版權頁"

    def test_earliest_short_line_wins_over_later_chapter(self):
        # "目錄" should beat a later "第一章" inside a TOC chunk.
        md = "目錄\n\n第一章　緒論\n第二章……"
        assert se.derive_chapter_title(md, "file.html") == "目錄"

    LONG_CH = "第四章　為什麼亞歷山大大帝所征服的大流士王國在他死後沒有背叛其後繼者"

    def test_long_chapter_heading_as_markdown_heading(self):
        # Normal EPUB path: el_to_md emits the title as a `## heading`, so a
        # long explicit chapter title is captured correctly.
        md = "## " + self.LONG_CH + "\n\n內文……"
        assert se.derive_chapter_title(md, "file.html") == self.LONG_CH

    def test_long_chapter_heading_alone(self):
        # No following short line: PRIORITY 2 (explicit chapter pattern) wins.
        assert se.derive_chapter_title(self.LONG_CH, "file.html") == self.LONG_CH

    @pytest.mark.xfail(
        strict=True,
        reason="FINDING: in the plain-text fallback path (no markdown heading), "
               "a long 第N章 title followed by a SHORT body line loses to the "
               "body line — derive_chapter_title checks PRIORITY 1 (earliest "
               "short non-banner line, the 目錄-beats-第一章 rule) before "
               "PRIORITY 2 (explicit chapter-head pattern). Bites degraded PDF/ "
               "OCR chunks. Fix = let an explicit 第N章/Chapter-N match at the "
               "FIRST content line win before the short-line rule, without "
               "regressing the 目錄 case. See report.",
    )
    def test_long_chapter_heading_plaintext_first_line(self):
        md = self.LONG_CH + "\n\n內文開始"
        assert se.derive_chapter_title(md, "file.html") == self.LONG_CH

    def test_fallback_truncates_instead_of_leaking_filename(self):
        # Long prose first line, no heading/short line: must NOT return the
        # raw filename; should truncate at a clause boundary + hash suffix.
        body = "這是一段很長的開場敘述，" * 10
        out = se.derive_chapter_title(body, "text/part0007.html")
        assert "part0007" not in out
        assert out != "text/part0007.html"


# ── promote_implicit_volumes — anonymous 第N部 groups ───────────────────────
class TestPromoteImplicitVolumes:
    def test_flat_book_untouched(self):
        chunks = [{"chapter_path": "第一章", "volume": None},
                  {"chapter_path": "第二章", "volume": None}]
        se.promote_implicit_volumes(chunks)
        assert all(c["volume"] is None for c in chunks)

    def test_part_divider_promoted_and_propagated(self):
        chunks = [
            {"chapter_path": "第一卷　羅馬", "volume": "第一卷　羅馬"},  # explicit
            {"chapter_path": "第二部", "volume": None},                 # implicit divider
            {"chapter_path": "下級章節", "volume": None},               # inherits
        ]
        se.promote_implicit_volumes(chunks)
        assert chunks[1]["volume"] == "第二部"
        assert chunks[2]["volume"] == "第二部"

    def test_explicit_volume_not_overwritten(self):
        chunks = [
            {"chapter_path": "第一卷", "volume": "第一卷"},
            {"chapter_path": "第二部", "volume": None},
            {"chapter_path": "第三卷", "volume": "第三卷"},  # explicit again
        ]
        se.promote_implicit_volumes(chunks)
        assert chunks[2]["volume"] == "第三卷"
