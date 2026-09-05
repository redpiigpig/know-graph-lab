# -*- coding: utf-8 -*-
"""Test-first lock for Uchimura Kanzō's TWO ENGLISH ORIGINALS.

《代表的日本人 Representative Men of Japan》(Keiseisha 1908) and 《我如何成為基督徒
How I Became a Christian》(Keiseisha 1922) were written by Uchimura in English,
so this line runs en＋繁中 (the Aozora line in uchimura_build is ja＋繁中).
Source = archive.org djvu OCR text, so unlike the Aozora line the text needs
reflowing: running heads / page numbers dropped, hyphenation rejoined,
paragraphs healed across page breaks. These pin the PURE helpers — zero network,
LLM or DB. See .claude/skills/ebook-collected-works/uchimura_collected_works.md.
"""
import uchimura_en_build as ue


class TestRegistry:
    def test_two_works_with_distinct_ids(self):
        assert set(ue.REGISTRY) == {"representative-men", "how-i-became"}
        ids = [w["ebook_id"] for w in ue.REGISTRY.values()]
        assert len(set(ids)) == 2
        # d0000000-… namespace continues the Aozora line (…0001–0006 taken).
        assert all(i.startswith("d0000000-0000-4000-8000-0000000000") for i in ids)
        assert {i[-2:] for i in ids} == {"07", "08"}

    def test_english_source_language(self):
        assert ue.SOURCE_LANG == "en"

    def test_sections_are_ordered_non_overlapping_ranges(self):
        for slug, w in ue.REGISTRY.items():
            secs = w["sections"]
            assert secs, slug
            for a, b in zip(secs, secs[1:]):
                assert a["end"] <= b["start"], (slug, a["title_zh"])
            for s in secs:
                assert s["start"] < s["end"]
                assert s["title_zh"] and s["heading"]


class TestJunkLine:
    """Running heads and page numbers carry no lowercase letters; body text does."""

    def test_running_head_is_junk(self):
        for s in ["38  REPRESENTATIVE", "MEN  OF  JAPAN.  39", "MEN OF PA JAN. 149",
                  "EEPEESENTATIVE", "3D", "IDO", "V>A"]:
            assert ue.HEAD_RE.search(s), s

    def test_body_line_is_kept(self):
        for s in ["much  we  regarded  him.  Both  Christians  and  non-",
                  r"\X7HEN  Nippon  first,  at  Heaven's"]:
            assert not ue.HEAD_RE.search(s), s


class TestReflow:
    def test_dehyphenates_and_joins_wrapped_lines(self):
        out = ue.reflow_ocr(["He  was  so  inde-", "pendent  a  man."])
        assert out == ["He was so independent a man."]

    def test_drops_page_artifacts_and_heals_split_paragraph(self):
        # A paragraph interrupted by a page break (running head + page number)
        # must come back as ONE paragraph, not three.
        out = ue.reflow_ocr([
            "The  opportunity  was  a  good  one  to  show  him  how",
            "",
            "38  REPRESENTATIVE",
            "",
            "much  we  regarded  him.  Both  united  in  this.",
        ])
        assert out == ["The opportunity was a good one to show him how "
                       "much we regarded him. Both united in this."]

    def test_paragraph_break_is_kept_when_previous_sentence_ended(self):
        out = ue.reflow_ocr(["First  paragraph  ends  here.", "", "Second  one  starts."])
        assert out == ["First paragraph ends here.", "Second one starts."]


class TestOcrQuoteFix:
    def test_lowercase_u_before_capital_becomes_open_quote(self):
        assert ue.fix_ocr_quotes('he said, uO just tell us how.”') == 'he said, “O just tell us how.”'

    def test_real_words_and_initials_untouched(self):
        assert ue.fix_ocr_quotes("U. the Good-natured, and unusual Uchimura") == \
            "U. the Good-natured, and unusual Uchimura"


class TestSplitLongParas:
    def test_short_paragraph_untouched(self):
        assert ue.split_long_paras_en(["Short one."]) == ["Short one."]

    def test_long_paragraph_splits_on_sentence_boundary(self):
        p = ("Sentence one is fairly long. " * 40).strip()
        out = ue.split_long_paras_en([p], max_chars=400)
        assert len(out) > 1
        assert all(len(x) <= 460 for x in out)
        assert "".join(x.replace(" ", "") for x in out) == p.replace(" ", "")


class TestOcrFixes:
    def test_mangled_author_signature_restored(self):
        assert ue.fix_ocr_quotes("IvAN.25 UCHIMURA.") == "KANZO UCHIMURA."
