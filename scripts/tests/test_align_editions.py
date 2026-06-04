"""Cross-edition alignment contract (collected-works multi-language).

Locks parse_chapter_number's normalization (DE/EN/CJK headings → same key) and
align_editions' anchor-join vs order-align behavior, then checks the output
feeds straight into assemble_multilang_chunks. See
.claude/skills/ebook-collected-works/.
"""
import align_editions as al
import multilang_chunks as mc


class TestParseChapterNumber:
    def test_english_roman(self):
        assert al.parse_chapter_number("Chapter III. On Memory") == ("chapter", 3)

    def test_english_arabic_with_markdown(self):
        assert al.parse_chapter_number("## Chapter 12") == ("chapter", 12)

    def test_german_kapitel(self):
        assert al.parse_chapter_number("Kapitel 3. Über das Gedächtnis") == ("chapter", 3)

    def test_de_and_en_collapse_to_same_key(self):
        assert al.parse_chapter_number("Kapitel 3") == al.parse_chapter_number("Chapter III")

    def test_cjk_chapter(self):
        assert al.parse_chapter_number("第三章　論記憶") == ("chapter", 3)

    def test_cjk_teens(self):
        assert al.parse_chapter_number("第十二章") == ("chapter", 12)

    def test_section_sign(self):
        assert al.parse_chapter_number("§ 12") == ("section", 12)

    def test_kinds_do_not_merge(self):
        assert al.parse_chapter_number("Part 1") != al.parse_chapter_number("Chapter 1")
        assert al.parse_chapter_number("Teil 1") == al.parse_chapter_number("Part I")

    def test_no_number_returns_none(self):
        assert al.parse_chapter_number("Preface") is None
        assert al.parse_chapter_number("") is None
        assert al.parse_chapter_number("Vorwort") is None


class TestAnchorCoverage:
    def test_full_unique_coverage(self):
        secs = [{"heading": f"Chapter {i}", "text": ""} for i in (1, 2, 3)]
        assert al.anchor_coverage(secs) == 1.0

    def test_partial_coverage(self):
        secs = [{"heading": "Preface", "text": ""}, {"heading": "Chapter 1", "text": ""}]
        assert al.anchor_coverage(secs) == 0.5

    def test_duplicate_keys_kill_coverage(self):
        secs = [{"heading": "Chapter 1", "text": ""}, {"heading": "Chapter 1", "text": ""}]
        assert al.anchor_coverage(secs) == 0.0

    def test_empty(self):
        assert al.anchor_coverage([]) == 0.0


class TestAlignEditions:
    def test_anchor_join_reorders_en_to_de(self):
        de = [
            {"heading": "Kapitel 1", "text": "D1"},
            {"heading": "Kapitel 2", "text": "D2"},
        ]
        # EN out of order + roman numerals — anchor join must realign by key.
        en = [
            {"heading": "Chapter II", "text": "E2"},
            {"heading": "Chapter I", "text": "E1"},
        ]
        units = al.align_editions(de, en)
        assert [u["match"] for u in units] == ["anchor", "anchor"]
        assert units[0]["sources"] == {"de": "D1", "en": "E1"}
        assert units[1]["sources"] == {"de": "D2", "en": "E2"}

    def test_de_only_section_keeps_blank_en(self):
        de = [{"heading": "Kapitel 1", "text": "D1"}, {"heading": "Kapitel 2", "text": "D2"}]
        en = [{"heading": "Chapter 1", "text": "E1"}]
        units = al.align_editions(de, en)
        assert units[1]["match"] == "de-only"
        assert units[1]["sources"] == {"de": "D2", "en": ""}

    def test_en_only_section_appended(self):
        de = [{"heading": "Kapitel 1", "text": "D1"}]
        en = [{"heading": "Chapter 1", "text": "E1"}, {"heading": "Chapter 2", "text": "E2"}]
        units = al.align_editions(de, en)
        assert units[-1]["match"] == "en-only"
        assert units[-1]["sources"] == {"de": "", "en": "E2"}

    def test_falls_back_to_order_align_without_anchors(self):
        de = [{"heading": "Vorwort", "text": "D0"}, {"heading": "Einleitung", "text": "D1"}]
        en = [{"heading": "Preface", "text": "E0"}, {"heading": "Introduction", "text": "E1"}]
        units = al.align_editions(de, en)
        assert [u["match"] for u in units] == ["order", "order"]
        assert units[0]["sources"] == {"de": "D0", "en": "E0"}
        assert units[0]["chapter_path"] == "Vorwort"     # primary (de) heading
        assert units[1]["chapter_path"] == "Einleitung"  # primary (de) heading

    def test_order_align_pads_short_side(self):
        de = [{"heading": "Vorwort", "text": "D0"}]
        en = [{"heading": "Preface", "text": "E0"}, {"heading": "Extra", "text": "E1"}]
        units = al.align_editions(de, en)
        assert len(units) == 2
        assert units[1]["sources"] == {"de": "", "en": "E1"}
        assert units[1]["chapter_path"] == "Extra"  # falls back to en heading

    def test_chapter_path_strips_markdown(self):
        de = [{"heading": "## Kapitel 1. Titel", "text": "D"}]
        en = [{"heading": "## Chapter 1. Title", "text": "E"}]
        units = al.align_editions(de, en)
        assert units[0]["chapter_path"] == "Kapitel 1. Titel"


class TestFeedsAssembler:
    def test_aligned_units_assemble_into_valid_chunks(self):
        de = [{"heading": "Kapitel 1", "text": "Das Gedächtnis…"},
              {"heading": "Kapitel 2", "text": "Das Symbol…"}]
        en = [{"heading": "Chapter 1", "text": "Memory…"},
              {"heading": "Chapter 2", "text": "The symbol…"}]
        units = al.align_editions(de, en)
        chunks = mc.assemble_multilang_chunks(
            units, translate_fn=lambda u: "## " + u["chapter_path"] + "\n\n中譯", source_order=["de", "en"],
        )
        assert [c["chunk_index"] for c in chunks] == [0, 1]
        assert chunks[0]["sources"] == {"de": "Das Gedächtnis…", "en": "Memory…"}
        assert chunks[0]["source_lang"] == "de"
        assert chunks[0]["source_text"] == "Das Gedächtnis…"
        for c in chunks:
            mc.validate_multilang_chunk(c)
