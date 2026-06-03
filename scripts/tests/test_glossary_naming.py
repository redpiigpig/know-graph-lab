"""Test-first contract for scripts/glossary_naming.py — the pure core of the
「翻譯定名」(/translation-glossary, promoted to a top-level card) widening.

Covers:
  - DOMAINS taxonomy (theology people/terms kept; rulers/places/deities/
    philosophers/scientists added; a 'principles' page entry)
  - root_key normalization + group_by_root
  - check_root_consistency — the user's 名根一致性 rule: entries sharing a
    name_root must render that root identically (塞琉古/塞琉西亞 ✓; 西流基 ✗).
  - split_variants (";"/"；"-separated translation variants)
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import glossary_naming as gn  # noqa: E402


# ── Taxonomy ──────────────────────────────────────────────────────────────
def test_domains_keep_theology_and_add_new_fields():
    keys = {d["key"] for d in gn.DOMAINS}
    # theology kept
    assert {"biblical_people", "theologians", "theological_terms"} <= keys
    # new domains added (per user: 帝王 / 國名城市 / 神祇宗教名詞 / 哲學家 / 科學家)
    assert {"rulers", "places", "deities", "philosophers", "scientists"} <= keys


def test_each_domain_has_label_and_table_or_is_principles():
    for d in gn.DOMAINS:
        assert d["label_zh"]
        if d["key"] == "principles":
            assert d.get("is_page")          # principles is a static page, no table
        else:
            assert d["table"]                # everything else is DB-backed


def test_new_domains_map_to_their_own_tables():
    # per user decision: keep theology tables, ADD per-domain tables
    by = {d["key"]: d for d in gn.DOMAINS}
    assert by["rulers"]["table"] == "historical_rulers"
    assert by["places"]["table"] == "place_names"
    assert by["deities"]["table"] == "deities"
    assert by["philosophers"]["table"] == "philosophers"
    assert by["scientists"]["table"] == "scientists"
    # theology untouched
    assert by["theologians"]["table"] == "theologians"
    assert by["theological_terms"]["table"] == "theological_terms"


# ── Root key + grouping ────────────────────────────────────────────────────
def test_root_key_trims_and_normalizes():
    assert gn.root_key("  塞琉 ") == "塞琉"
    assert gn.root_key("Mithra") == gn.root_key("mithra ")   # case/space-insensitive


def test_group_by_root_buckets_entries():
    entries = [
        {"id": 1, "name_root": "塞琉", "name_recommended": "塞琉古"},
        {"id": 2, "name_root": "塞琉", "name_recommended": "塞琉西亞"},
        {"id": 3, "name_root": "密特", "name_recommended": "密特拉"},
        {"id": 4, "name_root": "", "name_recommended": "雅典"},   # no root → ungrouped
    ]
    groups = gn.group_by_root(entries)
    assert set(groups.keys()) == {"塞琉", "密特"}
    assert len(groups["塞琉"]) == 2


# ── Name-root consistency (the headline rule) ──────────────────────────────
def test_check_root_consistency_flags_divergent_root_rendering():
    entries = [
        {"id": 1, "name_root": "塞琉", "name_recommended": "塞琉古"},      # ok
        {"id": 2, "name_root": "塞琉", "name_recommended": "塞琉西亞"},    # ok
        {"id": 3, "name_root": "塞琉", "name_recommended": "西流基"},      # ✗ root not honoured
    ]
    bad = gn.check_root_consistency(entries)
    bad_ids = {b["id"] for b in bad}
    assert bad_ids == {3}
    assert bad[0]["name_root"] == "塞琉"


def test_check_root_consistency_mithra_example():
    # 來自密特拉(密特)的：密特拉 / 密特里達迪 都含「密特」→ 一致；米特拉 不含 → flag
    entries = [
        {"id": 1, "name_root": "密特", "name_recommended": "密特拉"},
        {"id": 2, "name_root": "密特", "name_recommended": "密特里達迪"},
        {"id": 3, "name_root": "密特", "name_recommended": "米特拉達梯斯"},
    ]
    bad = gn.check_root_consistency(entries)
    assert {b["id"] for b in bad} == {3}


def test_check_root_consistency_clean_set_returns_empty():
    entries = [
        {"id": 1, "name_root": "亞歷山", "name_recommended": "亞歷山大"},
        {"id": 2, "name_root": "亞歷山", "name_recommended": "亞歷山卓"},
    ]
    assert gn.check_root_consistency(entries) == []


def test_check_root_consistency_ignores_rootless_entries():
    entries = [{"id": 1, "name_root": "", "name_recommended": "雅典"},
               {"id": 2, "name_root": None, "name_recommended": "羅馬"}]
    assert gn.check_root_consistency(entries) == []


# ── Variant parsing ────────────────────────────────────────────────────────
def test_split_variants_handles_both_separators_and_blanks():
    assert gn.split_variants("保羅；保祿") == ["保羅", "保祿"]
    assert gn.split_variants("亞歷山大; 亞歷山卓 ;") == ["亞歷山大", "亞歷山卓"]
    assert gn.split_variants("") == []
    assert gn.split_variants(None) == []
