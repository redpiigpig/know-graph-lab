"""Focused tests for the standalone Plotinus collected-works pipeline."""

from pathlib import Path

import plotinus_build as pb


GREEK_SAMPLE = """\
<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body><div type="edition">
  <div type="textpart" subtype="book" n="1">
    <div type="textpart" subtype="chapter" n="1">
      <head>ΤΙ ΤΟ ΖΩΙΟΝ</head>
      <div type="textpart" subtype="section" n="1"><p>Ἡδοναὶ <pb n="1"/> καὶ λῦπαι.</p></div>
      <div type="textpart" subtype="section" n="2"><p>ψυχὴ <del>πῶς</del> ἀθάνατος.</p></div>
    </div>
  </div>
</div></body></text></TEI>
"""


ENGLISH_SAMPLE = """\
<ThML><ThML.body>
  <div1 type="book" title="The First Ennead" id="ii">
    <div2 type="chapter" title="First Tractate. The Animate and the Man." id="ii.i">
      <h3>FIRST TRACTATE.</h3><h3>THE ANIMATE AND THE MAN.</h3>
      <p>1. Pleasure and distress.</p><p>More of section one.</p>
      <p>2. Soul is immortal.</p><p><note>translator note</note>More of section two.</p>
    </div2>
  </div1>
</ThML.body></ThML>
"""


def test_glossary_locks_plotinian_terms():
    assert pb.GLOSSARY["τὸ Ἕν"] == "太一"
    assert pb.GLOSSARY["νοῦς"] == "努斯"
    assert pb.GLOSSARY["ψυχή"] == "靈魂"
    assert pb.GLOSSARY["πρόοδος"] == "流出"
    assert pb.GLOSSARY["ἐπιστροφή"] == "回歸"


def test_catalog_enumerates_six_enneads_and_life():
    assert list(pb.WORKS) == [
        "ennead-1", "ennead-2", "ennead-3", "ennead-4",
        "ennead-5", "ennead-6", "life",
    ]
    assert len({work["ebook_id"] for work in pb.WORKS.values()}) == 7
    assert all(work["source_order"] == ["grc", "en"] for work in pb.WORKS.values())


def test_parse_greek_enneads_preserves_citation_and_omits_critical_deletions():
    parsed = pb.parse_greek_enneads(GREEK_SAMPLE)

    assert parsed[(1, 1)]["title"] == "ΤΙ ΤΟ ΖΩΙΟΝ"
    assert parsed[(1, 1)]["sections"] == [
        (1, "Ἡδοναὶ καὶ λῦπαι."),
        (2, "ψυχὴ ἀθάνατος."),
    ]


def test_parse_mackenna_groups_paragraphs_by_numbered_section():
    parsed = pb.parse_mackenna_enneads(ENGLISH_SAMPLE)

    assert parsed[(1, 1)]["title"] == "The Animate and the Man."
    assert parsed[(1, 1)]["sections"] == [
        (1, "Pleasure and distress. More of section one."),
        (2, "Soul is immortal. More of section two."),
    ]


def test_life_parsers_keep_direct_greek_marker_and_zero_width_english_heading():
    greek_html = """<div class="prp-pages-output"><p><span id="p1">1</span>. alpha</p>
    <span id="p2">2</span>. beta <p>continued</p></div>"""
    english_html = """<div class="prp-pages-output"><p>1.</p><p>alpha</p>
    <p>\u200b2.</p><p>beta continued</p></div>"""

    assert pb.parse_life_greek(greek_html) == [(1, "alpha"), (2, "beta continued")]
    assert pb.parse_life_english(english_html) == [(1, "alpha"), (2, "beta continued")]


def test_align_sections_covers_mismatched_editions_without_paragraph_drift():
    greek = [(1, "α" * 20), (2, "β" * 20), (3, "γ" * 20)]
    english = [(1, "a" * 30), (2, "b" * 30)]

    groups = pb.align_sections(greek, english)

    assert "".join(group["grc"] for group in groups).replace(" ", "") == "".join(text for _, text in greek)
    assert "".join(group["en"] for group in groups).replace(" ", "") == "".join(text for _, text in english)
    assert [n for group in groups for n in group["grc_ids"]] == [1, 2, 3]
    assert [n for group in groups for n in group["en_ids"]] == [1, 2]
    assert all("\n\n" not in group["grc"] and "\n\n" not in group["en"] for group in groups)


def test_translate_fn_resumes_from_per_section_cache(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(pb, "CACHE", tmp_path)
    cdir = tmp_path / "ennead-1_zh"
    cdir.mkdir(parents=True)
    (cdir / "I.1.1.txt").write_text("既有譯文", encoding="utf-8")
    calls = []

    translate = pb.make_translate_fn("auto", "ennead-1", engine_fn=lambda text: calls.append(text) or "新譯文")

    cached = translate({"anchor": "I.1.1", "sources": {"grc": "α", "en": "a"}})
    fresh = translate({"anchor": "I.1.2", "sources": {"grc": "β", "en": "b"}})

    assert cached == "既有譯文"
    assert fresh == "新譯文"
    assert len(calls) == 1
    assert (cdir / "I.1.2.txt").read_text(encoding="utf-8") == "新譯文"
