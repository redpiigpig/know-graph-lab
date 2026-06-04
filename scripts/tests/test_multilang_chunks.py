"""Writer-side contract for collected-works multi-language JSONL.

Mirrors the reader/JS spec (test/multilang-sources.spec.ts) so the Python
pipeline emits exactly what the (screenshot-verified) reader consumes:
`sources` + `source_order`, with the primary source mirrored into the legacy
source_text/source_lang. See .claude/skills/ebook-collected-works/.
"""
import json

import pytest

import multilang_chunks as mc


class TestNormalizeSources:
    def test_explicit_sources_honour_order(self):
        s, o = mc.normalize_sources({"de": "DE", "en": "EN"}, ["de", "en"])
        assert s == {"de": "DE", "en": "EN"}
        assert o == ["de", "en"]

    def test_order_filtered_to_existing_keys(self):
        _, o = mc.normalize_sources({"de": "DE"}, ["de", "en"])
        assert o == ["de"]

    def test_missing_keys_appended(self):
        _, o = mc.normalize_sources({"de": "DE", "en": "EN", "la": "LA"}, ["de"])
        assert o[0] == "de"
        assert set(o) == {"de", "en", "la"}

    def test_legacy_single_source(self):
        s, o = mc.normalize_sources(None, None, source_text="Hello", source_lang="en")
        assert s == {"en": "Hello"}
        assert o == ["en"]

    def test_blank_source_text_is_a_real_source(self):
        s, o = mc.normalize_sources(None, None, source_text="", source_lang="de")
        assert o == ["de"]
        assert s == {"de": ""}

    def test_monolingual_is_empty(self):
        assert mc.normalize_sources(None, None) == ({}, [])
        assert mc.normalize_sources(None, None, source_text="x", source_lang=None) == ({}, [])
        assert mc.normalize_sources({}, None) == ({}, [])


class TestMirrorPrimarySource:
    def test_mirrors_to_first_source(self):
        out = mc.mirror_primary_source({
            "content": "中譯",
            "sources": {"de": "DE", "en": "EN"},
            "source_order": ["de", "en"],
        })
        assert out["source_lang"] == "de"
        assert out["source_text"] == "DE"
        assert out["sources"] == {"de": "DE", "en": "EN"}
        assert out["source_order"] == ["de", "en"]

    def test_legacy_two_column_round_trips(self):
        out = mc.mirror_primary_source({"source_lang": "en", "source_text": "Hi"})
        assert out["source_lang"] == "en"
        assert out["source_text"] == "Hi"

    def test_monolingual_keeps_null_fields(self):
        out = mc.mirror_primary_source({"content": "純中文"})
        assert out["source_lang"] is None
        assert out["source_text"] is None

    def test_does_not_mutate_input(self):
        src = {"sources": {"de": "DE"}, "source_order": ["de"]}
        snapshot = json.loads(json.dumps(src))
        mc.mirror_primary_source(src)
        assert src == snapshot


class TestBuildMultilangChunk:
    def test_assembles_reader_ready_chunk(self):
        c = mc.build_multilang_chunk(
            chunk_index=3,
            chapter_path="第一章",
            content_zh="中譯",
            sources={"de": "DE", "en": "EN"},
            source_order=["de", "en"],
            volume="轉化的象徵",
            parent_volume="榮格",
        )
        assert c["chunk_index"] == 3
        assert c["chunk_type"] == "chapter"
        assert c["format"] == "markdown"
        assert c["content"] == "中譯"
        assert c["sources"] == {"de": "DE", "en": "EN"}
        assert c["source_order"] == ["de", "en"]
        assert c["source_lang"] == "de"          # mirrored
        assert c["source_text"] == "DE"          # mirrored
        assert c["volume"] == "轉化的象徵"
        assert c["parent_volume"] == "榮格"

    def test_source_order_defaults_to_sources_keys(self):
        c = mc.build_multilang_chunk(
            chunk_index=0, chapter_path="x", content_zh="z", sources={"de": "D", "en": "E"},
        )
        assert c["source_order"] == ["de", "en"]

    def test_optional_fields_omitted_when_absent(self):
        c = mc.build_multilang_chunk(
            chunk_index=0, chapter_path="x", content_zh="z", sources={"de": "D"},
        )
        assert "volume" not in c
        assert "parent_volume" not in c
        assert "title_en" not in c


class TestValidate:
    def test_passes_valid_chunk(self):
        c = mc.build_multilang_chunk(
            chunk_index=0, chapter_path="x", content_zh="中", sources={"de": "D", "en": "E"},
        )
        mc.validate_multilang_chunk(c)  # no raise

    def test_empty_content_raises(self):
        c = mc.build_multilang_chunk(
            chunk_index=0, chapter_path="x", content_zh="", sources={"de": "D"},
        )
        with pytest.raises(ValueError):
            mc.validate_multilang_chunk(c)

    def test_unmirrored_primary_raises(self):
        c = mc.build_multilang_chunk(
            chunk_index=0, chapter_path="x", content_zh="中", sources={"de": "D", "en": "E"},
        )
        c["source_text"] = "tampered"  # break the mirror
        with pytest.raises(ValueError):
            mc.validate_multilang_chunk(c)

    def test_sources_order_mismatch_raises(self):
        c = mc.build_multilang_chunk(
            chunk_index=0, chapter_path="x", content_zh="中", sources={"de": "D"},
        )
        c["source_order"] = ["de", "en"]  # en not in sources
        with pytest.raises(ValueError):
            mc.validate_multilang_chunk(c)

    def test_monolingual_chunk_is_valid(self):
        c = mc.mirror_primary_source({"content": "純中文"})
        mc.validate_multilang_chunk(c)  # no raise


class TestAssemble:
    UNITS = [
        {"chapter_path": "前言", "sources": {"de": "Vorwort", "en": "Preface"}},
        {"chapter_path": "第一章", "sources": {"de": "Kapitel 1", "en": "Chapter 1"},
         "volume": "卷一", "title_en": "Chapter 1"},
    ]

    def test_indexes_and_mirrors_each_unit(self):
        chunks = mc.assemble_multilang_chunks(
            self.UNITS,
            translate_fn=lambda u: "中:" + u["sources"]["de"],
            source_order=["de", "en"],
        )
        assert [c["chunk_index"] for c in chunks] == [0, 1]
        assert chunks[0]["content"] == "中:Vorwort"
        assert chunks[0]["source_lang"] == "de"
        assert chunks[0]["source_text"] == "Vorwort"
        assert chunks[1]["volume"] == "卷一"
        assert chunks[1]["title_en"] == "Chapter 1"
        # all valid
        for c in chunks:
            mc.validate_multilang_chunk(c)

    def test_parent_volume_fn_applied(self):
        chunks = mc.assemble_multilang_chunks(
            self.UNITS,
            translate_fn=lambda u: "中",
            source_order=["de", "en"],
            parent_volume_fn=lambda u: "榮格全集",
        )
        assert all(c["parent_volume"] == "榮格全集" for c in chunks)

    def test_round_trips_through_jsonl(self, tmp_path):
        chunks = mc.assemble_multilang_chunks(
            self.UNITS, translate_fn=lambda u: "中:" + u["sources"]["en"], source_order=["de", "en"],
        )
        p = tmp_path / "book.jsonl"
        mc.write_jsonl(chunks, p)
        lines = [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
        assert len(lines) == 2
        assert lines[0]["sources"] == {"de": "Vorwort", "en": "Preface"}
        assert lines[1]["source_order"] == ["de", "en"]
        # primary mirror survives serialization
        assert lines[1]["source_text"] == lines[1]["sources"][lines[1]["source_order"][0]]
