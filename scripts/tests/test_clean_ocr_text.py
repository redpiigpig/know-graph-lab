"""Per-page OCR cleanup (clean_ocr_text) — so copied quotes don't drag in
running headers / page numbers / wrapped-line noise.

Anchored on the real failure: 《埃及、希臘與羅馬》 page 7 OCR'd as
  "ii 埃及、希臘與羅馬出。作者汲取了…"
where the running header (roman page no + book title) is glued to the body.
"""
import clean_ocr_text as c

TITLE = "埃及、希臘與羅馬"


class TestStripRunningHeader:
    def test_header_glued_to_body_is_removed(self):
        line = "ii 埃及、希臘與羅馬出。作者汲取了古代史各領域的專家的成果："
        out = c.strip_running_header(line, TITLE)
        assert out.startswith("出。作者汲取了")
        assert "埃及、希臘與羅馬" not in out
        assert "ii" not in out

    def test_standalone_header_line_dropped(self):
        text = "ii 埃及、希臘與羅馬\n正文第一句開始。"
        out = c.strip_running_header(text, TITLE)
        assert out == "正文第一句開始。"

    def test_ocr_slip_single_letter_pageno(self):
        # idx 7 real case: "m 埃及、希臘與羅馬" (OCR of iii)
        out = c.strip_running_header("m 埃及、希臘與羅馬\n內文。", TITLE)
        assert out == "內文。"

    def test_title_with_spaces_dropped_punctuation(self):
        # OCR sometimes drops 、 and adds spaces between glyphs
        out = c.strip_running_header("iv 埃及 希臘 與 羅馬 內文續。", TITLE)
        assert out.strip().startswith("內文續。")

    def test_trailing_page_number_line_removed(self):
        out = c.strip_running_header("正文最後一句。\n262", TITLE)
        assert out == "正文最後一句。"

    def test_body_without_header_untouched(self):
        body = "這一段沒有頁眉，應該原樣保留。"
        assert c.strip_running_header(body, TITLE) == body

    def test_leading_year_not_stripped(self):
        # regression: "1914—2006" must NOT be treated as a page number
        for line in ("1914—2006 年）。", "1957 年8 月，她帶我登上山", "2004 年出版發行。"):
            assert c.strip_running_header(line, TITLE) == line

    def test_latin_word_not_stripped(self):
        # regression: "Civilizations" starts with roman-numeral letters but is a word
        for line in ("Civilizations of the Ancient Mediterranean",
                     "Egypt, Greece, & Rome"):
            assert c.strip_running_header(line, TITLE) == line

    def test_title_in_body_not_at_start_kept(self):
        # title mentioned mid-sentence is content, not a header
        line = "本書談的是埃及、希臘與羅馬三大古文明。"
        assert c.strip_running_header(line, TITLE) == line

    def test_no_title_still_strips_pure_pageno_lines(self):
        out = c.strip_running_header("v\n內容。\n10", None)
        assert out == "內容。"


class TestNormalizeLinebreaks:
    def test_wrapped_cjk_lines_join_into_paragraph(self):
        text = "這是一個相當長的句子在掃描時\n被切成兩行但其實是同一段。"
        out = c.normalize_cjk_linebreaks(text)
        assert out == "這是一個相當長的句子在掃描時被切成兩行但其實是同一段。"

    def test_short_lines_not_glued(self):
        # short standalone lines (e.g. a year + a fragment) must stay separate
        text = "一九一四年\n生於某地"
        out = c.normalize_cjk_linebreaks(text)
        assert "\n\n" in out  # kept as two paragraphs, not glued

    def test_sentence_end_starts_new_paragraph(self):
        text = "第一段結束。\n第二段開始繼續寫。"
        out = c.normalize_cjk_linebreaks(text)
        assert out == "第一段結束。\n\n第二段開始繼續寫。"

    def test_heading_kept_on_its_own_line(self):
        text = "第三版序言\n本書的第一版於一九九六年出版"
        out = c.normalize_cjk_linebreaks(text)
        assert out.split("\n\n")[0] == "第三版序言"

    def test_latin_lines_join_with_space(self):
        text = "this is a wrapped\nenglish sentence"
        out = c.normalize_cjk_linebreaks(text)
        assert out == "this is a wrapped english sentence"


class TestPipeline:
    def test_full_clean_real_page(self):
        raw = ("ii 埃及、希臘與羅馬出。作者汲取了古代史各領域的專家的成果\n"
               "他總是能夠融匯各個領域最新穎的觀點。\n262")
        out = c.clean_ocr_page(raw, TITLE)
        assert "ii" not in out.split("\n")[0]
        assert "埃及、希臘與羅馬" not in out
        assert "262" not in out
        assert out.startswith("出。作者汲取了")
