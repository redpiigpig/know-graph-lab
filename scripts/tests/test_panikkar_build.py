"""Test-first lock for the Panikkar collected-works build module.

Panikkar (d. 2010) is fully in copyright → English-first, sources from private
sites (see .claude/skills/ebook-collected-works/panikkar_collected_works.md).
Pilot = 《The Unknown Christ of Hinduism》, originally English → bilingual
(en + 繁中) by default,升三欄 (en+es+繁中) when a parallel Spanish text appears.

These pin the PURE helpers (reflow / split_sections / align_secondary /
build_section_chunk / make_cover_chunk / assemble_pilot) with a stub translate
fn — zero network, LLM, or DB. The chunk shape must match what multilang_chunks
validates and the reader consumes.
"""
import json

import multilang_chunks as mc
import panikkar_build as pk


class TestReflow:
    def test_drops_page_numbers_and_blank_lines(self):
        out = pk.reflow(["A first sentence.", "", "42", "Another sentence."])
        assert out == ["A first sentence.", "Another sentence."]

    def test_heals_hyphenation_across_lines(self):
        out = pk.reflow(["The cosmothean-", "dric vision is whole."])
        assert out == ["The cosmotheandric vision is whole."]

    def test_merges_paragraph_split_by_running_head(self):
        # a paragraph that does not end in terminal punctuation is glued to the next
        out = pk.reflow(["This sentence continues", "", "onto the next page."])
        assert out == ["This sentence continues onto the next page."]

    def test_blank_line_separates_complete_paragraphs(self):
        out = pk.reflow(["First done.", "", "Second done."])
        assert out == ["First done.", "Second done."]


class TestSplitSections:
    def test_splits_on_chapter_headings(self):
        text = "CHAPTER 1\n\nbody one\n\nCHAPTER 2\n\nbody two"
        secs = pk.split_sections(text)
        assert [s["heading"] for s in secs] == ["CHAPTER 1", "CHAPTER 2"]
        assert secs[0]["paras"] == ["body one"]

    def test_front_matter_before_first_heading(self):
        text = "title page\n\nINTRODUCTION\n\nbody"
        secs = pk.split_sections(text)
        assert secs[0]["heading"] == "(front)"
        assert "title page" in secs[0]["paras"][0]
        assert secs[1]["heading"] == "INTRODUCTION"

    def test_isolates_markdown_heading_glued_to_body(self):
        # Gemini --mark-headings emits `## Title` on its own line but glued to the
        # next paragraph by a single newline; split must still break the section.
        text = "## Chapter One\nbody of one.\n\n## Chapter Two\nbody of two."
        secs = pk.split_sections(text)
        assert [s["heading"] for s in secs] == ["## Chapter One", "## Chapter Two"]
        assert secs[0]["paras"] == ["body of one."]

    def test_splits_on_cjk_headings(self):
        # existing 中譯 are split on CJK chapter headings (simplified or traditional)
        text = "导论\n\n中文正文一\n\n第一章\n\n中文正文二\n\n第二节\n\n中文正文三"
        secs = pk.split_sections(text)
        assert [s["heading"] for s in secs] == ["导论", "第一章", "第二节"]
        assert secs[0]["paras"] == ["中文正文一"]

    def test_long_line_with_chapter_word_is_not_a_heading(self):
        long = ("Chapter 1 of this work is treated at length in the following "
                "very long discursive sentence which must never split a section")
        secs = pk.split_sections(f"INTRODUCTION\n\n{long}")
        assert len(secs) == 1
        assert long in secs[0]["paras"]


class TestAlignSecondary:
    def test_equal_counts_passthrough(self):
        assert pk.align_secondary(["a", "b"], ["x", "y"]) == ["x", "y"]

    def test_empty_secondary_pads_to_primary_length(self):
        assert pk.align_secondary(["a", "b", "c"], []) == ["", "", ""]

    def test_unequal_counts_returns_primary_length(self):
        out = pk.align_secondary(["a", "b", "c"], ["x", "y"])
        assert len(out) == 3


class TestBuildSectionChunk:
    def test_bilingual_equal_rows_and_mirror(self):
        chunk = pk.build_section_chunk(
            chunk_index=1,
            title_zh="導論",
            zh_paras=["第一段中文", "第二段中文"],
            source_paras={"en": ["First para.", "Second para."]},
            source_heads={"en": "INTRODUCTION"},
            source_order=["en"],
            page_number=2,
        )
        mc.validate_multilang_chunk(chunk)
        # rows = heading + 2 paras, equal across zh and en
        assert chunk["content"].split("\n\n") == ["## 導論", "第一段中文", "第二段中文"]
        assert chunk["sources"]["en"].split("\n\n") == ["## INTRODUCTION", "First para.", "Second para."]
        assert chunk["source_lang"] == "en"
        assert chunk["source_text"] == chunk["sources"]["en"]

    def test_trilingual_pads_short_secondary_to_equal_rows(self):
        chunk = pk.build_section_chunk(
            chunk_index=1,
            title_zh="導論",
            zh_paras=["甲", "乙"],
            source_paras={"en": ["A", "B"], "es": ["Uno"]},  # es short by one
            source_heads={"en": "INTRO", "es": "INTRODUCCIÓN"},
            source_order=["en", "es"],
            page_number=2,
        )
        mc.validate_multilang_chunk(chunk)
        n = len(chunk["content"].split("\n\n"))
        assert len(chunk["sources"]["en"].split("\n\n")) == n
        assert len(chunk["sources"]["es"].split("\n\n")) == n  # padded
        assert chunk["source_order"] == ["en", "es"]


class TestCoverChunk:
    def test_cover_is_chunk_zero_page_one(self):
        cover = pk.make_cover_chunk()
        assert cover["chunk_index"] == 0
        assert cover["chunk_type"] == "cover"
        assert cover["page_number"] == 1
        mc.validate_multilang_chunk(cover)


class TestReferenceMode:
    """已有完整中譯的卷：不重譯，把既有中譯本當主欄、與英文原典逐段對照入庫
    （標第三方參考譯本）。content = 既有中譯，sources.en = 英文原典，逐段對齊。"""

    def test_build_reference_chunk_content_is_existing_translation(self):
        chunk = pk.build_reference_chunk(
            chunk_index=1, title_zh="第一章", en_head="CHAPTER 1",
            zh_paras=["既有中譯第一段", "既有中譯第二段"],
            en_paras=["English one.", "English two."],
            page_number=2,
        )
        mc.validate_multilang_chunk(chunk)
        assert chunk["content"].split("\n\n") == ["## 第一章", "既有中譯第一段", "既有中譯第二段"]
        assert chunk["sources"]["en"].split("\n\n") == ["## CHAPTER 1", "English one.", "English two."]
        assert chunk["source_lang"] == "en"
        assert chunk["source_text"] == chunk["sources"]["en"]

    def test_reference_chunk_aligns_unequal_en_to_zh(self):
        # the existing translation drives the row count; English is aligned to it
        chunk = pk.build_reference_chunk(
            chunk_index=1, title_zh="導論", en_head="INTRO",
            zh_paras=["甲", "乙", "丙"], en_paras=["A.", "B."],  # en short by one
            page_number=2,
        )
        n = len(chunk["content"].split("\n\n"))
        assert len(chunk["sources"]["en"].split("\n\n")) == n

    def test_pair_sections_pairs_by_order(self):
        en = [{"heading": "CHAPTER 1", "paras": ["a"]}, {"heading": "CHAPTER 2", "paras": ["b"]}]
        zh = [{"heading": "第一章", "paras": ["甲"]}, {"heading": "第二章", "paras": ["乙"]}]
        pairs = pk.pair_sections(en, zh)
        assert pairs[0] == ("第一章", "CHAPTER 1", ["a"], ["甲"])
        assert pairs[1] == ("第二章", "CHAPTER 2", ["b"], ["乙"])

    def test_pair_sections_pads_uneven_counts(self):
        en = [{"heading": "CH1", "paras": ["a"]}, {"heading": "CH2", "paras": ["b"]}]
        zh = [{"heading": "第一章", "paras": ["甲"]}]  # zh missing chapter 2
        pairs = pk.pair_sections(en, zh)
        assert len(pairs) == 2
        assert pairs[1][3] == []  # zh paras empty for the unpaired English chapter

    def test_assemble_reference_end_to_end(self):
        en = [{"heading": "INTRODUCTION", "paras": ["First.", "Second."]}]
        zh = [{"heading": "導論", "paras": ["第一段", "第二段"]}]
        chunks = pk.assemble_reference(en, zh)
        assert [c["chunk_index"] for c in chunks] == [0, 1]
        assert chunks[0]["chunk_type"] == "cover"
        assert chunks[1]["content"].split("\n\n") == ["## 導論", "第一段", "第二段"]
        assert chunks[1]["sources"]["en"].split("\n\n") == ["## INTRODUCTION", "First.", "Second."]
        for c in chunks:
            mc.validate_multilang_chunk(c)


class TestChapterAlignment:
    """REFERENCE books: front matter diverges between EN原典 and 中譯 (prefaces,
    TOC, 作者簡介…) and OCR can fragment a chapter into repeated `## 序言` headings.
    So before pairing chapters we merge repeated headings + drop front/end matter."""

    def test_is_frontmatter(self):
        assert pk.is_frontmatter("## Preface to the New Edition")
        assert pk.is_frontmatter("## 序言")
        assert pk.is_frontmatter("## 目錄")
        assert pk.is_frontmatter("## 作者簡介")
        assert pk.is_frontmatter("(front)")
        assert not pk.is_frontmatter("## 2. The Dialogical Dialogue")
        assert not pk.is_frontmatter("## 宗教內對話的山上訓道")

    def test_merge_repeated_headings(self):
        secs = [
            {"heading": "## 序言", "paras": ["a"]},
            {"heading": "## 序言", "paras": ["b"]},
            {"heading": "## 第一章", "paras": ["c"]},
        ]
        out = pk.merge_repeated_headings(secs)
        assert [s["heading"] for s in out] == ["## 序言", "## 第一章"]
        assert out[0]["paras"] == ["a", "b"]

    def test_chapter_sections_drops_frontmatter_and_merges(self):
        secs = [
            {"heading": "(front)", "paras": ["x"]},
            {"heading": "## 序言", "paras": ["p1"]},
            {"heading": "## 序言", "paras": ["p2"]},
            {"heading": "## 山上訓道", "paras": ["ch1"]},
            {"heading": "## 2. The Dialogical Dialogue", "paras": ["ch2"]},
            {"heading": "## 目錄", "paras": ["toc"]},
        ]
        chs = pk.chapter_sections(secs)
        assert [s["heading"] for s in chs] == ["## 山上訓道", "## 2. The Dialogical Dialogue"]

    def test_align_reference_chapters_pairs_after_filter(self):
        en = [
            {"heading": "## Preface", "paras": ["pre"]},
            {"heading": "## The Sermon", "paras": ["e1"]},
            {"heading": "## 2. Dialogue", "paras": ["e2"]},
        ]
        zh = [
            {"heading": "## 作者簡介", "paras": ["bio"]},
            {"heading": "## 山上訓道", "paras": ["z1"]},
            {"heading": "## 對話", "paras": ["z2"]},
        ]
        pairs, n_en, n_zh = pk.align_reference_chapters(en, zh)
        assert (n_en, n_zh) == (2, 2)
        assert pairs[0] == ("## 山上訓道", "## The Sermon", ["e1"], ["z1"])


class TestLoadSectionsFromSrc:
    def test_split_before_reflow_keeps_headings(self, tmp_path):
        # regression: reflow on the whole doc first glued INTRODUCTION/CHAPTER into
        # the body (headings lack terminal punctuation). Split must happen first.
        src = tmp_path / "src.txt"
        src.write_text(
            "INTRODUCTION\n\n"
            "Opening sentence wraps over\nseveral hard-wrapped li-\nnes here.\n\n"
            "42\n\n"
            "CHAPTER 1\n\nThe body of chapter one.",
            encoding="utf-8",
        )
        secs = pk.load_sections_from_src(src)
        assert [s["heads"]["en"] for s in secs] == ["INTRODUCTION", "CHAPTER 1"]
        # body de-hyphenated + de-wrapped into one paragraph
        assert secs[0]["sources"]["en"] == ["Opening sentence wraps over several hard-wrapped lines here."]
        assert secs[1]["sources"]["en"] == ["The body of chapter one."]


class TestAssemblePilot:
    def test_end_to_end_with_stub_translate(self):
        sections = [
            {"title_zh": "導論", "heads": {"en": "INTRODUCTION"},
             "sources": {"en": ["First.", "Second."]}},
            {"title_zh": "第一章", "heads": {"en": "CHAPTER 1"},
             "sources": {"en": ["Third."]}},
        ]
        chunks = pk.assemble_pilot(
            sections,
            translate_para=lambda s: "中:" + s,
            source_order=["en"],
        )
        # cover + 2 sections, contiguous indices
        assert [c["chunk_index"] for c in chunks] == [0, 1, 2]
        assert chunks[0]["chunk_type"] == "cover"
        # section content rows = heading + translated paras
        assert chunks[1]["content"].split("\n\n") == ["## 導論", "中:First.", "中:Second."]
        assert chunks[2]["sources"]["en"].split("\n\n") == ["## CHAPTER 1", "Third."]
        for c in chunks:
            mc.validate_multilang_chunk(c)

    def test_writes_valid_jsonl(self, tmp_path):
        sections = [{"title_zh": "導論", "heads": {"en": "INTRO"},
                     "sources": {"en": ["Body."]}}]
        chunks = pk.assemble_pilot(sections, translate_para=lambda s: "中:" + s, source_order=["en"])
        out = tmp_path / "pilot.jsonl"
        mc.write_jsonl(chunks, out)
        lines = [json.loads(x) for x in out.read_text(encoding="utf-8").splitlines() if x.strip()]
        assert len(lines) == 2  # cover + 1 section
        assert lines[1]["source_order"] == ["en"]
