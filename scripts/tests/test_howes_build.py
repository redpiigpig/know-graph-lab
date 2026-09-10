# -*- coding: utf-8 -*-
"""Test-first lock for the Uchimura BIOGRAPHY build module.

John F. Howes, 《Japan's Modern Prophet: Uchimura Kanzō, 1861–1930》(UBC Press
2005) is the standard critical biography of Uchimura — the first book *about*
內村鑑三 in this repo rather than *by* him. Source is a born-digital PDF with a
real text layer (Acrobat Distiller, no OCR), so paragraphs are rebuilt from PDF
line geometry, not from blank lines: body text sits at x0≈37 and a paragraph's
first line is indented to x0≈46; block quotes are set one point smaller (8.5 vs
9.0); running heads are 8.0; chapter titles are 18.0; endnote markers are
superscript spans (flags bit 0).

These pin the PURE helpers — zero PDF, network, LLM or DB. See
.claude/skills/ebook-collected-works/howes_uchimura_biography.md.
"""
import howes_build as hb

BODY, QUOTE, HEAD, TITLE = 9.0, 8.5, 8.0, 18.0


def L(text, x0=37.0, size=BODY, y=100.0):
    return {"x0": x0, "y": y, "size": size, "text": text}


class TestRegistry:
    def test_single_work_english_source(self):
        assert list(hb.REGISTRY) == ["howes-prophet"]
        assert hb.SOURCE_LANG == "en"
        assert hb.QUEUE == ["howes-prophet"]

    def test_sections_ordered_and_titled(self):
        secs = hb.REGISTRY["howes-prophet"]["sections"]
        assert len(secs) == 19  # 序＋導論＋16 章＋結論
        for a, b in zip(secs, secs[1:]):
            assert a["end"] <= b["start"], (a["title_zh"], b["title_zh"])
        for s in secs:
            assert s["start"] < s["end"] and s["title_zh"] and s["heading"]

    def test_apparatus_is_excluded(self):
        """Notes / Bibliography / Index (p428+) are reference apparatus, not prose."""
        assert max(s["end"] for s in hb.REGISTRY["howes-prophet"]["sections"]) <= 428


class TestKeepLine:
    def test_running_head_and_page_furniture_dropped(self):
        assert not hb.keep_line(L("42 Part 1: I Refuse", size=HEAD, y=36.0))
        assert not hb.keep_line(L("This page intentionally left blank", size=12.0))
        assert not hb.keep_line(L("Education of a Meiji Samurai", size=TITLE, y=78.0))
        assert not hb.keep_line(L("   ", size=BODY))

    def test_body_and_quote_kept(self):
        assert hb.keep_line(L("Although the church became a source of support"))
        assert hb.keep_line(L("With regard to my future, I have thought", x0=46.0, size=QUOTE))


class TestLinesToParas:
    def test_indent_starts_a_new_paragraph(self):
        out = hb.lines_to_paras([
            L("Although the church became a source of support for the boys,", x0=46.0),
            L("this was not the only role that it played."),
            L("Finally, everything that the students learned", x0=46.0),
            L("came through words imperfectly understood."),
        ])
        assert out == [
            "Although the church became a source of support for the boys, "
            "this was not the only role that it played.",
            "Finally, everything that the students learned "
            "came through words imperfectly understood.",
        ]

    def test_hyphenated_line_break_is_rejoined(self):
        out = hb.lines_to_paras([L("they do not ap-", x0=46.0), L("pear to have changed.")])
        assert out == ["they do not appear to have changed."]

    def test_block_quote_is_marked_and_split_off(self):
        out = hb.lines_to_paras([
            L("He wrote to his friend:", x0=46.0),
            L("With regard to my future, I have", x0=46.0, size=QUOTE),
            L("thought over and over again.", x0=46.0, size=QUOTE),
            L("The letter shows his indecision.", x0=46.0),
        ])
        assert out == [
            "He wrote to his friend:",
            "> With regard to my future, I have thought over and over again.",
            "The letter shows his indecision.",
        ]

    def test_paragraph_running_across_a_page_break_stays_one_paragraph(self):
        # Page 2 opens mid-sentence at the un-indented body x0 → must not split.
        out = hb.lines_to_paras([
            L("The opportunity was a good one to show him how", x0=46.0),
            L("much we regarded him."),
        ])
        assert len(out) == 1


class TestSuperscriptStripping:
    def test_endnote_marker_span_dropped(self):
        spans = [
            {"size": 9.0, "flags": 4, "text": "form a majority."},
            {"size": 5.2, "flags": 5, "text": "14"},
            {"size": 9.0, "flags": 4, "text": " There are more"},
        ]
        assert hb.spans_to_text(spans) == "form a majority. There are more"

    def test_ordinary_spans_concatenated(self):
        spans = [{"size": 9.0, "flags": 4, "text": "Uchimura "},
                 {"size": 9.0, "flags": 6, "text": "Kanzô"}]
        assert hb.spans_to_text(spans) == "Uchimura Kanzô"


class TestSplitLong:
    def test_short_paragraph_untouched(self):
        assert hb.split_long(["Short one."]) == ["Short one."]

    def test_long_quote_keeps_its_marker_on_every_piece(self):
        p = "> " + ("This is a sentence in the quotation. " * 30).strip()
        out = hb.split_long([p], max_chars=400)
        assert len(out) > 1
        assert all(x.startswith("> ") for x in out)
        joined = "".join(x[2:].replace(" ", "") for x in out)
        assert joined == p[2:].replace(" ", "")


class TestHangingIndent:
    def test_numbered_list_continuation_is_not_a_new_paragraph(self):
        """懸掛縮排（x0≈48.7）比段落首行縮排（45.7）還深，意思卻相反 —— 是續行。"""
        out = hb.lines_to_paras([
            L("1 A religion to assure Japan's independence. Japanese abound in", x0=36.7),
            L("patriotism. They want such a religion and so seek the power of Chris-", x0=48.7),
            L("tianity to save their nation.", x0=48.7),
        ])
        assert len(out) == 1
        assert out[0].endswith("Christianity to save their nation.")

    def test_ordinary_first_line_indent_still_starts_a_paragraph(self):
        out = hb.lines_to_paras([L("First one ends.", x0=36.7), L("Second starts.", x0=45.7)])
        assert out == ["First one ends.", "Second starts."]


class TestControlChars:
    r"""Distiller 在字中間塞字型裝飾控制碼；留著會被當成內文送去翻譯。

    這裡一律用 `\x01` 這種**轉義寫法**，不要在原始碼裡放真的控制位元組 —— 真位元組
    在終端機、diff、code review 裡全都顯示成空白，看起來就像 "beforeafter"，
    分不出測試到底有沒有在測東西（本檔就曾因此被誤判為壞掉）。每個案例都先斷言
    原字串真的比乾淨字串長：哪天寫檔掉了一層轉義，會在斷言處炸掉而不是靜靜通過。
    提字元範圍的 docstring 一律用 r-string，否則那些轉義又會變回隱形位元組。
    """

    def test_font_ornament_control_char_stripped(self):
        raw = "before\x01after"
        assert len(raw) == len("beforeafter") + 1, "轉義掉了，這個測試沒測到東西"
        assert hb.spans_to_text([{"size": 9.0, "flags": 4, "text": raw}]) == "beforeafter"

    def test_whole_control_range_and_del_stripped(self):
        r"""_CTRL_RE 蓋 \x00-\x1f 與 \x7f：定位、換行、歸位、DEL 都要清掉。"""
        raw = "a\x00b\x09c\x0ad\x0de\x1ff\x7fg"
        assert len(raw) == len("abcdefg") + 6, "轉義掉了，這個測試沒測到東西"
        assert hb.spans_to_text([{"size": 9.0, "flags": 4, "text": raw}]) == "abcdefg"

    def test_printable_neighbours_of_the_range_survive(self):
        r"""邊界外不可誤殺：空格（\x20）與 ~（\x7e）緊貼範圍兩端，都得留著。"""
        assert hb.spans_to_text([{"size": 9.0, "flags": 4, "text": "a ~b"}]) == "a ~b"


class TestPrintedPageNumbers:
    """印刷頁碼（folio）—— [[feedback_transcribe_page_numbers]]：只認書上印的，推不出來就 None。"""

    def test_folio_read_from_running_head(self):
        assert hb.folio_of([
            L("281", x0=36.3, size=HEAD, y=36.3),
            L("The Bible and Japan", x0=278.2, size=HEAD, y=36.2),
            L("In the new hall, he could", x0=45.8, y=78.3),
        ]) == "281"

    def test_roman_folio_in_front_matter(self):
        assert hb.folio_of([L("xii", x0=18.8, size=HEAD, y=36.3)]) == "xii"

    def test_body_number_is_not_mistaken_for_a_folio(self):
        """正文裡的年份（size 9.0、y 在版心）不是頁碼。"""
        assert hb.folio_of([L("1891", x0=36.8, y=240.3)]) is None

    def test_chapter_opening_page_has_no_folio(self):
        """章首頁不印書眉；章號「7」是 18.0 的標題字，不可當頁碼。"""
        assert hb.folio_of([L("7", x0=55.8, size=TITLE, y=36.8),
                            L("The Taught", x0=77.8, size=TITLE, y=36.8)]) is None

    def test_running_head_text_is_not_a_folio(self):
        assert hb.folio_of([L("Conclusion", x0=36.3, size=HEAD, y=36.2)]) is None

    def test_fill_folios_forward_and_backward(self):
        assert hb.fill_folios([None, "21", None, None, "24"]) == ["20", "21", "22", "23", "24"]

    def test_fill_folios_leaves_roman_alone(self):
        """羅馬頁碼不做算術，推不出來就留 None——不可捏一個假的。"""
        assert hb.fill_folios([None, "xii", None]) == [None, "xii", None]

    def test_fill_folios_never_produces_page_zero(self):
        assert hb.fill_folios([None, "1"]) == [None, "1"]

    def test_folio_int_rejects_roman(self):
        assert hb.folio_int("21") == 21
        assert hb.folio_int("xii") is None
        assert hb.folio_int(None) is None

    def test_paragraph_takes_the_page_it_starts_on(self):
        """跨頁的段落算在它**開始**的那一頁。"""
        a = L("A paragraph that begins here", x0=45.7, y=500.0)
        b = L("and runs onto the next page.", x0=36.7, y=78.0)
        c = L("A second paragraph.", x0=45.7, y=90.0)
        a["page"], b["page"], c["page"] = "21", "22", "22"
        assert [p for _t, p in hb.paras_with_pages([a, b, c])] == ["21", "22"]

    def test_split_long_pairs_carries_the_page_to_every_piece(self):
        out = hb.split_long_pairs([("> " + ("This is a sentence. " * 400).strip(), "137")])
        assert len(out) > 1
        assert all(p == "137" for _t, p in out)
        assert all(t.startswith("> ") for t, _p in out)

    def test_lines_to_paras_still_returns_plain_strings(self):
        """舊介面不可壞：uchimura_auto 與既有測試都還在用。"""
        assert hb.lines_to_paras([L("First one ends.", x0=36.7),
                                  L("Second starts.", x0=45.7)]) == ["First one ends.", "Second starts."]
