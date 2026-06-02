"""PDF text normalization — collapse_cjk_spacing (standardize_pdf_lite).

OCR / PDF text extraction often injects spaces between CJK glyphs ("時 間").
This collapses them while leaving Latin word spacing intact. Over-eager
collapsing would glue English words together; under-collapsing leaves the
正文 looking broken.
"""
import standardize_pdf_lite as pl


def test_collapses_space_between_cjk():
    assert pl.collapse_cjk_spacing("時 間") == "時間"


def test_collapses_multiple_cjk_gaps():
    assert pl.collapse_cjk_spacing("時 間 是 最 偉 大 的") == "時間是最偉大的"


def test_latin_spacing_preserved():
    assert pl.collapse_cjk_spacing("hello world") == "hello world"


def test_mixed_cjk_latin_boundary_kept():
    # CJK runs collapse; the space around the embedded Latin word stays.
    assert pl.collapse_cjk_spacing("中 文 abc 英 文") == "中文 abc 英文"


def test_empty_passthrough():
    assert pl.collapse_cjk_spacing("") == ""
    assert pl.collapse_cjk_spacing(None) is None
