"""Tests for ingest_gnostic pure heuristics (env-gated import via conftest)."""
import ingest_gnostic as ig


def test_is_trivial_source_keeps_real_markers():
    # genuine page/citation markers → trivial (keep verbatim, no LLM)
    assert ig.is_trivial_source("(Text: R. 354; Pat. at end of last piece.)")
    assert ig.is_trivial_source("pp. 51-54 of codex almost completely missing") is True
    assert ig.is_trivial_source("p. 5")
    assert ig.is_trivial_source("cf. John 1:1")
    assert ig.is_trivial_source("Page numbers have been removed from this edition.")
    assert ig.is_trivial_source("123")          # pure digits
    assert ig.is_trivial_source("—")            # punctuation only


def test_is_trivial_source_does_not_skip_pagels_prose():
    # "Pagels" (Elaine Pagels, the gnostic scholar) must NOT match the `page`
    # citation marker — this is real prose that needs translating.
    assert ig.is_trivial_source(
        "Pagels realized that, like creation stories of other cultures, "
        "the Genesis story addresses profound and basic questions.") is False
