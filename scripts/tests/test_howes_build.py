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
