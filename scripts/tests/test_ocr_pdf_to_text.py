"""Lock the pure assembly of ocr_pdf_to_text (page dicts → one text blob).

The Gemini upload/network path isn't unit-tested (it needs keys + a PDF); only
the deterministic page→text join is, since that's what feeds
panikkar_build --zh-src (and CJK-heading splitting depends on headings landing
on their own lines).
"""
import ocr_pdf_to_text as o


class TestPagesToText:
    def test_joins_nonempty_pages_with_blank_line(self):
        pages = [{"page": 1, "text": "导论\n\n第一段。"}, {"page": 2, "text": "第二段。"}]
        assert o.pages_to_text(pages) == "导论\n\n第一段。\n\n第二段。"

    def test_skips_empty_and_whitespace_pages(self):
        pages = [{"page": 1, "text": "甲"}, {"page": 2, "text": "   "}, {"page": 3, "text": "乙"}]
        assert o.pages_to_text(pages) == "甲\n\n乙"

    def test_strips_per_page_edges_but_keeps_internal_breaks(self):
        pages = [{"page": 1, "text": "  第一章\n\n正文一  "}, {"page": 2, "text": "正文二"}]
        assert o.pages_to_text(pages) == "第一章\n\n正文一\n\n正文二"

    def test_sorts_by_page_number(self):
        pages = [{"page": 2, "text": "乙"}, {"page": 1, "text": "甲"}]
        assert o.pages_to_text(pages) == "甲\n\n乙"

    def test_empty_input(self):
        assert o.pages_to_text([]) == ""
