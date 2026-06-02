"""Transcription pain point #1 — PDF 目錄 (TOC) driven chunking.

normalize_toc decides whether a PDF's bookmark TOC is usable and which
entries become chapter boundaries; build_chapter_path builds the 祖/父/本
hierarchy; page_number must stay sacred. These are the heuristics behind
"目錄分類瑕疵" for scanned/text PDFs.
"""
import standardize_pdf as sp


def toc(*rows):
    """rows are (level, title, page) tuples — the fitz get_toc() shape."""
    return [list(r) for r in rows]


class TestNormalizeTocRejection:
    def test_too_few_entries_returns_none(self):
        assert sp.normalize_toc(toc((1, "序", 1), (1, "第一章", 2)), 100) is None

    def test_empty_toc_returns_none(self):
        assert sp.normalize_toc([], 100) is None
        assert sp.normalize_toc(None, 100) is None

    def test_page_level_toc_rejected(self):
        # One bookmark per page (e.g. 中東史 654/661) — no chapter structure.
        rows = toc(*[(1, f"p{i}", i) for i in range(1, 101)])
        assert sp.normalize_toc(rows, 100) is None


class TestNormalizeTocAccept:
    def test_basic_chapters_kept_and_sorted(self):
        rows = toc((1, "第三章", 60), (1, "第一章", 10), (1, "第二章", 35))
        out = sp.normalize_toc(rows, 200)
        assert out is not None
        assert [e["start_page"] for e in out] == [10, 35, 60]

    def test_deep_levels_dropped(self):
        # MAX_LEVEL = 2: level-3 entries are inline headings, not boundaries.
        rows = toc((1, "第一章", 10), (1, "第二章", 30), (1, "第三章", 50),
                   (3, "太深的小節", 12))
        out = sp.normalize_toc(rows, 200)
        assert all(e["level"] <= sp.MAX_LEVEL for e in out)
        assert "太深的小節" not in [e["title"] for e in out]

    def test_nul_byte_stripped_from_title(self):
        rows = toc((1, "封面\x00", 1), (1, "第一章", 10), (1, "第二章", 30))
        out = sp.normalize_toc(rows, 200)
        assert out[0]["title"] == "封面"

    def test_page_clamped_into_range(self):
        rows = toc((1, "第一章", 0), (1, "第二章", 30), (1, "第三章", 9999))
        out = sp.normalize_toc(rows, 200)
        assert min(e["start_page"] for e in out) >= 1
        assert max(e["start_page"] for e in out) <= 200

    def test_same_start_page_deduped(self):
        rows = toc((1, "章A", 10), (2, "節A", 10), (1, "章B", 30), (1, "章C", 50))
        out = sp.normalize_toc(rows, 200)
        pages = [e["start_page"] for e in out]
        assert len(pages) == len(set(pages))


class TestBuildChapterPath:
    def test_walks_back_to_ancestors(self):
        entries = [
            {"level": 1, "title": "第一部", "start_page": 1},
            {"level": 2, "title": "第一章", "start_page": 5},
        ]
        assert sp.build_chapter_path(entries, 1) == "第一部 / 第一章"

    def test_top_level_is_itself(self):
        entries = [{"level": 1, "title": "第一部", "start_page": 1}]
        assert sp.build_chapter_path(entries, 0) == "第一部"

    def test_three_level_hierarchy(self):
        entries = [
            {"level": 0, "title": "上卷", "start_page": 1},
            {"level": 1, "title": "第一部", "start_page": 5},
            {"level": 2, "title": "第一章", "start_page": 9},
        ]
        assert sp.build_chapter_path(entries, 2) == "上卷 / 第一部 / 第一章"


class TestHeadingForDepth:
    def test_single_part_gets_h2(self):
        assert sp._heading_for("第一部") == "## 第一部"

    def test_two_parts_gets_h3_leaf(self):
        assert sp._heading_for("第一部 / 第一章") == "### 第一章"

    def test_three_plus_capped_at_h4(self):
        assert sp._heading_for("上卷 / 第一部 / 第一章") == "#### 第一章"


class TestPrependHeading:
    def test_prepends_when_absent(self):
        out = sp._prepend_heading("正文內容", "第一部")
        assert out.startswith("## 第一部")
        assert "正文內容" in out

    def test_does_not_double_heading(self):
        content = "## 已有標題\n\n正文"
        assert sp._prepend_heading(content, "第一部") == content
