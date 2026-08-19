"""Focused parser and source-policy tests for the Presocratic pilot."""

import presocratics_build as pb
import presocratics_registry as registry


HERACLITUS_TEI = """<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body><div type="edition">
<div type="textpart" subtype="fragment" n="1"><p><label>[2 Bywater]</label>
<bibl>Sext. adv. math. VII 132</bibl> τοῦ δὲ λόγου τοῦδ’ ἐόντος ἀεὶ ἀξύνετοι γίνονται ἄνθρωποι.</p></div>
<div type="textpart" subtype="fragment" n="50"><p><label>[1]</label>
<bibl>Hippol. refut. IX 9</bibl> Ἡ. μὲν οὖν φησιν· οὐκ ἐμοῦ ἀλλὰ τοῦ λόγου ἀκούσαντας.</p></div>
</div></body></text></TEI>"""

PARMENIDES_TEI = """<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body><div type="edition">
<div type="textpart" subtype="fragment" n="3"><p><bibl>Procl. in Parm.</bibl>
This is later witness context.<quote>ξυνὸν δὲ μοί ἐστιν, ὁππόθεν ἄρξωμαι.</quote></p></div>
<div type="textpart" subtype="fragment" n="4"><p><bibl>Procl. in Tim.</bibl>
<quote>εἰ δ’ ἄγ’ ἐγὼν ἐρέω.</quote></p></div>
<div type="textpart" subtype="fragment" n="5"><p><bibl>Clem. Strom.</bibl>
<quote>τὸ γὰρ αὐτὸ νοεῖν ἐστίν τε καὶ εἶναι.</quote></p></div>
</div></body></text></TEI>"""

HERACLITUS_HTML = """<html><body>
<p>The fragments. 65. I give a version according to the arrangement of Bywater.</p>
<p>(1) It is wise to hearken, not to me, but to my Word.</p>
<p>(2) Though this Word is true evermore, men do not understand it. <sup class="reference">[1]</sup></p>
<p>66. The doxographical tradition. This is commentary, not a fragment.</p>
<p>(3) Must not be parsed.</p>
</body></html>"""

PARMENIDES_HTML = """<html><body>
<p>The fragments of Parmenides are preserved by Simplicius. I follow the arrangement of Diels.</p>
<p>(3)</p><p>It is all one to me where I begin.</p>
<p>(4, 5)</p><p>Come now, I will tell thee the two ways.</p>
<p>86. Philosophy. Commentary begins here.</p>
</body></html>"""


def test_fourteen_hubs_and_dk_identity_policy_are_locked():
    assert list(registry.HUBS) == [
        "thales", "anaximander", "anaximenes", "pythagoras", "xenophanes",
        "heraclitus", "parmenides", "anaxagoras", "zeno-elea", "empedocles",
        "protagoras", "gorgias", "socrates", "democritus",
    ]
    assert registry.HUBS["heraclitus"]["dk_chapter"] == 22
    assert registry.HUBS["parmenides"]["dk_chapter"] == 28
    assert registry.HUBS["socrates"]["dk_chapter"] is None
    assert len({hub["ebook_id"] for hub in registry.HUBS.values()}) == 14


def test_a_testimonium_can_never_be_promoted_to_author_text():
    record = pb.parse_testimonium_record("heraclitus", "1", "Diogenes reports a story.", "Diog. Laert. IX")
    assert record["record_type"] == "testimonium"
    assert record["is_author_autograph"] is False
    assert record["is_direct_quotation"] is False
    assert record["quotation_text"] == ""
    assert record["translation_voice"] == "third-person-witness"


def test_heraclitus_only_curated_quote_boundary_becomes_translatable():
    records = pb.parse_diels_b_tei(HERACLITUS_TEI, "heraclitus")
    assert records["1"]["bywater_id"] == "2"
    assert records["1"]["quotation_boundary"] == "curated-whole-tail"
    assert records["1"]["is_direct_quotation"] is True
    assert records["1"]["quotation_text"].startswith("τοῦ δὲ λόγου")
    assert "Sext." not in records["1"]["quotation_text"]
    assert records["50"]["quotation_text"] == ""
    assert records["50"]["is_direct_quotation"] is False
    assert records["50"]["quotation_boundary"] == "unreviewed-witness-context"


def test_parmenides_tei_quote_excludes_later_witness_context():
    records = pb.parse_diels_b_tei(PARMENIDES_TEI, "parmenides")
    assert records["3"]["quotation_boundary"] == "tei-quote"
    assert records["3"]["quotation_text"] == "ξυνὸν δὲ μοί ἐστιν, ὁππόθεν ἄρξωμαι."
    assert "later witness" not in records["3"]["quotation_text"]
    assert "later witness" in records["3"]["witness_context"]


def test_burnet_heraclitus_parser_is_bounded_before_doxography():
    fragments = pb.parse_burnet_fragments(HERACLITUS_HTML, "heraclitus")
    assert set(fragments) == {("1",), ("2",)}
    assert "[1]" not in fragments[("2",)]


def test_burnet_parmenides_keeps_combined_diels_groups():
    fragments = pb.parse_burnet_fragments(PARMENIDES_HTML, "parmenides")
    assert fragments[("3",)] == "It is all one to me where I begin."
    assert fragments[("4", "5")] == "Come now, I will tell thee the two ways."


def test_build_units_uses_explicit_crosswalk_and_b_only_paths():
    h_units = pb.build_units("heraclitus", HERACLITUS_TEI, HERACLITUS_HTML)
    assert len(h_units) == 1
    assert h_units[0]["citation"] == "DK 22 B1"
    assert h_units[0]["crosswalk"]["english_system"] == "Bywater 2"
    assert "B類引文殘篇" in h_units[0]["chapter_path"]
    assert "Hippol." not in h_units[0]["sources"]["grc"]

    p_units = pb.build_units("parmenides", PARMENIDES_TEI, PARMENIDES_HTML)
    assert [unit["citation"] for unit in p_units] == ["DK 28 B3", "DK 28 B4–B5"]
    assert p_units[1]["crosswalk"]["diels"] == ["DK 28 B4", "DK 28 B5"]
    assert "Clem." not in p_units[1]["sources"]["grc"]


def test_source_licenses_are_explicit_and_pilot_scope_is_narrow():
    assert registry.DIELS_1922_LICENSE["license"] == "CC BY-SA 4.0"
    assert registry.BURNET_1920_LICENSE["rights"] == "public domain"
    assert {slug for slug, hub in registry.HUBS.items() if hub["source_status"] == "pilot-ready"} == {
        "heraclitus", "parmenides"
    }
