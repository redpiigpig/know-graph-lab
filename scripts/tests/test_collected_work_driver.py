"""Driver wiring for the trilingual collected-works pipeline.

Locks section splitting + the load→align→assemble→write_jsonl run() path with a
stub translate_fn (no network, LLM, or DB). See
.claude/skills/collected-works-multilang/.
"""
import json

import multilang_chunks as mc
import translate_collected_work as drv


class TestSplitSections:
    def test_splits_on_chapter_headings(self):
        text = "CHAPTER 1\n\nfirst body\n\nCHAPTER 2\n\nsecond body"
        secs = drv.split_sections(text)
        assert [s["heading"] for s in secs] == ["CHAPTER 1", "CHAPTER 2"]
        assert secs[0]["text"] == "first body"
        assert secs[1]["text"] == "second body"

    def test_front_matter_before_first_heading_kept(self):
        text = "title page stuff\n\nCHAPTER 1\n\nbody"
        secs = drv.split_sections(text)
        assert secs[0]["heading"] == "(front)"
        assert "title page stuff" in secs[0]["text"]
        assert secs[1]["heading"] == "CHAPTER 1"

    def test_markdown_headings(self):
        text = "## Kapitel 1\n\ndeutscher Text\n\n## Kapitel 2\n\nmehr Text"
        secs = drv.split_sections(text)
        assert [s["heading"] for s in secs] == ["## Kapitel 1", "## Kapitel 2"]

    def test_long_line_is_not_a_heading(self):
        # a 100-char line that happens to contain "Chapter 1" must not split
        long = "Chapter 1 of this work is discussed at length in the following very long sentence about memory yes"
        secs = drv.split_sections(f"## Real\n\n{long}")
        assert len(secs) == 1
        assert long in secs[0]["text"]


class TestRun:
    def _write(self, tmp_path, name, text):
        p = tmp_path / name
        p.write_text(text, encoding="utf-8")
        return str(p)

    def test_end_to_end_with_stub_translate(self, tmp_path):
        de = self._write(tmp_path, "de.txt", "Kapitel 1\n\nDas Gedächtnis\n\nKapitel 2\n\nDas Symbol")
        en = self._write(tmp_path, "en.txt", "Chapter I\n\nMemory\n\nChapter II\n\nThe symbol")
        out = tmp_path / "book.jsonl"
        chunks = drv.run(
            de, en, "test-ebook-id",
            translate_fn=lambda u: "## 中譯\n\n" + u["sources"]["de"],
            out_path=str(out),
        )
        assert [c["chunk_index"] for c in chunks] == [0, 1]
        # anchor join realigned EN roman numerals to DE
        assert chunks[0]["sources"] == {"de": "Das Gedächtnis", "en": "Memory"}
        assert chunks[0]["source_lang"] == "de"
        assert chunks[0]["source_text"] == "Das Gedächtnis"
        for c in chunks:
            mc.validate_multilang_chunk(c)

    def test_writes_valid_jsonl(self, tmp_path):
        de = self._write(tmp_path, "de.txt", "Kapitel 1\n\nA")
        en = self._write(tmp_path, "en.txt", "Chapter 1\n\nB")
        out = tmp_path / "book.jsonl"
        drv.run(de, en, "id", translate_fn=lambda u: "中", out_path=str(out))
        lines = [json.loads(x) for x in out.read_text(encoding="utf-8").splitlines() if x.strip()]
        assert len(lines) == 1
        assert lines[0]["content"] == "中"
        assert lines[0]["sources"] == {"de": "A", "en": "B"}
        assert lines[0]["source_order"] == ["de", "en"]

    def test_limit_truncates_units(self, tmp_path):
        de = self._write(tmp_path, "de.txt", "Kapitel 1\n\nA\n\nKapitel 2\n\nB\n\nKapitel 3\n\nC")
        en = self._write(tmp_path, "en.txt", "Chapter 1\n\nX\n\nChapter 2\n\nY\n\nChapter 3\n\nZ")
        out = tmp_path / "book.jsonl"
        chunks = drv.run(de, en, "id", translate_fn=lambda u: "中", out_path=str(out), limit=2)
        assert len(chunks) == 2

    def test_de_only_section_translates_and_blanks_en(self, tmp_path):
        de = self._write(tmp_path, "de.txt", "Kapitel 1\n\nA\n\nKapitel 2\n\nB")
        en = self._write(tmp_path, "en.txt", "Chapter 1\n\nX")
        out = tmp_path / "book.jsonl"
        chunks = drv.run(de, en, "id",
                         translate_fn=lambda u: "中:" + (u["sources"]["de"] or u["sources"]["en"]),
                         out_path=str(out))
        assert chunks[1]["sources"] == {"de": "B", "en": ""}
        assert chunks[1]["content"] == "中:B"  # translated the German even with no EN
