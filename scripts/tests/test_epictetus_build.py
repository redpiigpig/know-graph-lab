"""Focused pure-function tests for the Epictetus collected-works driver."""

import epictetus_build as eb


DISC_GRC = """<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body><div type="edition">
<div type="textpart" subtype="book" n="1">
 <div type="textpart" subtype="chapter" n="1"><head>κεφάλαιον</head>
  <div type="textpart" subtype="section" n="1"><p>τῶν ὄντων <note>editorial</note> τὰ μέν.</p></div>
  <div type="textpart" subtype="section" n="2"><p>τὰ δὲ οὐκ ἐφ’ ἡμῖν.</p></div>
 </div>
</div></div></body></text></TEI>"""

DISC_ENG = """<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body><div type="translation">
<div type="textpart" subtype="book" n="1">
 <div type="textpart" subtype="chapter" n="1"><head>Things in our power</head>
  <p>Some things are ours; <note>long note</note> others are not.</p>
 </div>
</div></div></body></text></TEI>"""

FRAG_GRC = """<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body><div type="edition">
<div type="textpart" subtype="fragment" n="1"><head>source</head><p>τί μοι μέλει;</p></div>
<div type="textpart" subtype="fragment" n="28a"><p>μόνον Ἑλληνικόν.</p></div>
</div></body></text></TEI>"""

FRAG_HTML = """<html><body><div class="post-body entry-content">
<h3 align="center">1</h3>What matters it?<br/>
<h3 align="center">9</h3>English only.<br/>
<h3 align="center">10a</h3>Also English only.<br/>
</div></body></html>"""


def test_parse_tei_discourses_tracks_book_chapter_and_drops_notes():
    units = eb.parse_tei(DISC_GRC, "discourses")
    assert [u["key"] for u in units] == ["1.1"]
    assert "editorial" not in units[0]["text"]
    assert "κεφάλαιον" not in units[0]["text"]
    assert units[0]["text"] == "τῶν ὄντων τὰ μέν. τὰ δὲ οὐκ ἐφ’ ἡμῖν."


def test_build_discourse_unit_is_chapter_level_and_reader_aligned():
    units = eb.build_units("discourses", DISC_GRC, DISC_ENG)
    assert len(units) == 1
    unit = units[0]
    assert unit["chapter_path"] == "談話錄 · 第一卷 · 第一篇"
    assert unit["anchors"] == ["Disc. 1.1"]
    assert list(unit["sources"]) == ["grc", "en"]
    assert "long note" not in unit["sources"]["en"]


def test_matheson_parser_and_fragment_intersection_skip_unpaired():
    parsed = eb.parse_matheson_fragments(FRAG_HTML)
    assert parsed == {"1": "What matters it?", "9": "English only.", "10a": "Also English only."}
    units = eb.build_units("fragments", FRAG_GRC, FRAG_HTML)
    assert [u["anchors"] for u in units] == [["Frag. 1"]]


def test_split_for_translation_conserves_normalized_text():
    source = "πρῶτον μὲν λόγος. δεύτερον δὲ φύσις· τρίτον τέλος; " * 20
    parts = eb.split_for_translation(source, max_chars=90)
    assert len(parts) > 1
    assert " ".join(parts) == eb._clean_space(source)
    assert all(len(p) <= 90 for p in parts)


def test_auto_engine_and_epictetus_glossary_are_locked(monkeypatch, tmp_path):
    monkeypatch.setattr(eb, "CACHE", tmp_path)
    translate = eb.make_translate_fn("auto", "handbook")
    assert callable(translate)
    assert "Ἐπίκτητος→愛比克泰德" in eb.PROMPT_TMPL
    assert "προαίρεσις→抉擇意志" in eb.PROMPT_TMPL
