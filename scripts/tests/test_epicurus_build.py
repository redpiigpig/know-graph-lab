# -*- coding: utf-8 -*-
"""Focused, zero-network tests for the independent Epicurus pipeline."""
from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import epicurus_build as eb


def _tei(inner: str) -> str:
    return f'<TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body><div type="edition">{inner}</div></body></text></TEI>'


def _book10(sections: str) -> str:
    return _tei(f'<div type="textpart" subtype="book" n="10"><div type="textpart" subtype="chapter" n="1">{sections}</div></div>')


def test_parse_letter_sections_trims_menoeceus_preamble_and_editor_notes():
    grc = _book10(
        '<div type="textpart" subtype="section" n="121"><p>前言。 Ἐπίκουρος Μενοικεῖ χαίρειν. 希臘一<note>校勘雜訊</note></p></div>'
        '<div type="textpart" subtype="section" n="122"><p>希臘二</p></div>'
    )
    en = _book10(
        '<div type="textpart" subtype="section" n="121"><p>Preamble. Epicurus to Menoeceus, greeting. English one<note>editorial noise</note></p></div>'
        '<div type="textpart" subtype="section" n="122"><p>English two</p></div>'
    )
    items = eb.parse_letter_sections(grc, en, 121, 122)
    assert [x["id"] for x in items] == ["DL10.121", "DL10.122"]
    assert items[0]["grc"].startswith("Ἐπίκουρος Μενοικεῖ χαίρειν")
    assert items[0]["en"].startswith("Epicurus to Menoeceus, greeting")
    assert "校勘雜訊" not in items[0]["grc"]
    assert "editorial noise" not in items[0]["en"]


def _doctrine_xmls() -> tuple[str, str]:
    grc_sections = []
    en_sections = []
    for dl, numbers in eb._DOCTRINES_BY_DL_SECTION.items():
        grc = "".join(
            f'<add>[<foreign xml:lang="eng">{_roman(n)}.</foreign>]</add> 希臘教義{n}。' for n in numbers
        )
        en = " ".join(f"{n}. English doctrine {n}." for n in numbers)
        grc_sections.append(f'<div type="textpart" subtype="section" n="{dl}"><p>{grc}</p></div>')
        en_sections.append(f'<div type="textpart" subtype="section" n="{dl}"><p>{en}</p></div>')
    return _book10("".join(grc_sections)), _book10("".join(en_sections))


def _roman(n: int) -> str:
    values = ((10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"))
    out = ""
    for value, symbol in values:
        while n >= value:
            out += symbol
            n -= value
    return out


def test_parse_principal_doctrines_produces_exactly_forty_aligned_items():
    grc, en = _doctrine_xmls()
    items = eb.parse_principal_doctrines(grc, en)
    assert len(items) == 40
    assert items[0] == {"id": "PD.1", "grc": "希臘教義1。", "en": "English doctrine 1."}
    assert items[-1]["id"] == "PD.40"
    assert items[-1]["grc"] == "希臘教義40。"


def test_parse_vatican_greek_requires_all_eighty_one_items():
    sections = "".join(
        f'<div type="textpart" subtype="section" n="{n}"><p>格言{n}</p></div>' for n in range(1, 82)
    )
    parsed = eb.parse_vatican_greek(_tei(sections))
    assert len(parsed) == 81
    assert parsed[1] == "格言1"
    assert parsed[81] == "格言81"


def test_bailey_page_parser_handles_greek_roman_and_ocr_markers():
    markers = [
        "XV.", "XVI.", "XVII.", "AVIII.", "XIX.", "ΧΧΙ.",
        "XXII.", "XXIV.", "AXV.", "XXVI.", "XXVII.",
    ]
    text = "Page 108 V. FRAGMENTS 109 continuation. " + " ".join(
        f"{marker} Saying {i}." for i, marker in enumerate(markers, start=1)
    )
    prefix, items = eb._split_bailey_page(text, 108)
    assert prefix == "continuation."
    assert list(items) == list(eb._BAILEY_PAGE_ITEMS[108])
    assert items[21] == "Saying 6."
    assert items[23] == "Saying 7."


def test_vatican_duplicate_map_covers_bailey_omissions():
    printed = {n for values in eb._BAILEY_PAGE_ITEMS.values() for n in values}
    duplicates = set(eb._VATICAN_PD_DUPLICATES)
    assert printed.isdisjoint(duplicates)
    # Bailey prints 56-57 as one restored sentence; the parser splits 57 out.
    assert printed | duplicates | {57} == set(range(1, 82))


def test_translate_cache_is_per_work_and_resumes_without_second_engine_call(tmp_path, monkeypatch):
    calls = []

    def fake_engine(source: str) -> str:
        calls.append(source)
        return "繁中譯文"

    fake = types.SimpleNamespace(
        PROMPT_TMPL="",
        gemini_with_haiku_fallback=fake_engine,
        nvidia_translate=fake_engine,
        haiku_translate=fake_engine,
        sonnet_translate=fake_engine,
    )
    monkeypatch.setitem(sys.modules, "translate_ebook_to_zh", fake)
    unit = {
        "_cache_id": "DL10.35",
        "chapter_path": "測試",
        "sources": {"grc": "希臘", "en": "English"},
    }
    fn = eb.make_translate_fn("nvidia", "herodotus", cache_root=tmp_path)
    assert fn(unit) == "繁中譯文"
    assert fn(unit) == "繁中譯文"
    assert len(calls) == 1
    assert (tmp_path / "herodotus_zh" / "DL10.35.txt").read_text(encoding="utf-8") == "繁中譯文"


def test_build_units_keeps_grc_en_and_one_anchor_per_item():
    units = eb.build_units("principal-doctrines", [{"id": "PD.1", "grc": "γ", "en": "e"}])
    assert units[0]["sources"] == {"grc": "γ", "en": "e"}
    assert units[0]["anchors"] == ["PD 1"]
    assert units[0]["_cache_id"] == "PD.1"
