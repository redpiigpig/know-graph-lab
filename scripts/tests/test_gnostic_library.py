"""Test-first contract for scripts/gnostic_library.py.

Pure functions only — HTML fixtures are inline, no network. Covers:
  - CATEGORIES taxonomy (the gnosis.org → /gnostic sub-categories)
  - make_slug / normalize_title (slug + dedup keys)
  - parse_category_index (a gnosis.org category page → doc links)
  - parse_document (a gnosis.org treatise page → English paragraph sections)
  - is_duplicate (skip docs already in /apocrypha or /fathers)
  - assert_aligned / align_ok (the EN↔ZH per-paragraph alignment gate)
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import gnostic_library as gl  # noqa: E402


# ── Taxonomy ──────────────────────────────────────────────────────────────
def test_categories_cover_the_thirteen_gnosis_sections():
    keys = {c["key"] for c in gl.CATEGORIES}
    # The 13 gnosis.org library sections we mirror as sub-categories.
    expected = {
        "nag_hammadi", "gnostic_scriptures", "valentinus", "mead",
        "polemics", "christian_apocrypha", "hermetica", "manichaean",
        "mandaean", "cathar", "alchemical", "modern", "dead_sea",
    }
    assert expected <= keys


def test_each_category_has_zh_label_and_order_and_index_path():
    for c in gl.CATEGORIES:
        assert c["label_zh"] and isinstance(c["label_zh"], str)
        assert isinstance(c["display_order"], int)
        assert c["index_path"].startswith(("library/", "naghamm/"))


def test_polemics_and_christian_apocrypha_are_dedup_categories():
    # Per user: these overlap /fathers and /apocrypha — dedup before ingest.
    dedup = {c["key"] for c in gl.CATEGORIES if c.get("dedup_against_existing")}
    assert "polemics" in dedup
    assert "christian_apocrypha" in dedup
    assert "nag_hammadi" not in dedup  # core Gnostic, always ingest


# ── Slug ──────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("title,expected", [
    ("The Gospel of Thomas", "gospel-of-thomas"),
    ("The Gospel of Truth (Robinson translation)", "gospel-of-truth"),
    ("Pistis Sophia", "pistis-sophia"),
    ("The Apocryphon of John (The Secret Book of John)", "apocryphon-of-john"),
    ("Poimandres", "poimandres"),
    ("On the Origin of the World", "on-the-origin-of-the-world"),
    ("  The   Thunder, Perfect Mind  ", "thunder-perfect-mind"),
])
def test_make_slug(title, expected):
    assert gl.make_slug(title) == expected


def test_make_slug_is_stable_and_url_safe():
    s = gl.make_slug("The Hymn of the Pearl — Acts of Thomas")
    assert s == s.lower()
    assert all(ch.isalnum() or ch == "-" for ch in s)
    assert "--" not in s
    assert not s.startswith("-") and not s.endswith("-")


# ── Dedup key ─────────────────────────────────────────────────────────────
def test_normalize_title_drops_leading_the_parentheticals_and_punct():
    a = gl.normalize_title("The Gospel of Thomas")
    b = gl.normalize_title("Gospel of Thomas (Lambdin translation)")
    c = gl.normalize_title("  gospel  of   thomas! ")
    assert a == b == c == "gospel of thomas"


def test_is_duplicate_matches_against_existing_english_titles():
    existing = ["1 Enoch", "Gospel of Thomas", "Against Heresies"]
    assert gl.is_duplicate("The Gospel of Thomas (Patterson/Meyer)", existing)
    assert gl.is_duplicate("Against Heresies", existing)
    assert not gl.is_duplicate("Pistis Sophia", existing)


# ── Category index parsing ────────────────────────────────────────────────
CATEGORY_INDEX_HTML = """
<html><head><title>Nag Hammadi Library</title></head>
<body>
  <a href="welcome.html">Gnosis Archive</a>
  <a href="../search_form.html">Search</a>
  <table>
    <tr><td><a href="naghamm/gthom.html">The Gospel of Thomas</a></td></tr>
    <tr><td><a href="naghamm/gop.html">The Gospel of Philip</a></td></tr>
    <tr><td><a href="naghamm/apocjn.html">The Apocryphon of John</a></td></tr>
  </table>
  <a href="bookstore1.htm">Bookstore</a>
  <a href="#top">top</a>
  <a href="mailto:x@y.com">email</a>
</body></html>
"""


def test_parse_category_index_returns_content_doc_links_only():
    docs = gl.parse_category_index(CATEGORY_INDEX_HTML, base_path="naghamm/nhl.html")
    titles = [d["title"] for d in docs]
    assert "The Gospel of Thomas" in titles
    assert "The Gospel of Philip" in titles
    assert "The Apocryphon of John" in titles
    # nav / boilerplate excluded
    assert "Search" not in titles
    assert "Bookstore" not in titles
    assert "Gnosis Archive" not in titles


def test_parse_category_index_resolves_relative_urls():
    docs = gl.parse_category_index(CATEGORY_INDEX_HTML, base_path="naghamm/nhl.html")
    gthom = next(d for d in docs if d["title"] == "The Gospel of Thomas")
    # href "naghamm/gthom.html" relative to base "naghamm/nhl.html"
    assert gthom["url"].endswith("/naghamm/gthom.html")
    assert gthom["url"].startswith("http")


# ── Document parsing ──────────────────────────────────────────────────────
DOC_HTML = """
<html><head><title>The Gospel of Thomas - The Nag Hammadi Library</title></head>
<body>
  <div class="nav"><a href="../index.html">back</a></div>
  <script>var x = 1;</script>
  <h1>The Gospel of Thomas</h1>
  <p>These are the secret sayings that the living Jesus spoke.</p>
  <p>&nbsp;</p>
  <blockquote>(1) And he said, "Whoever discovers the interpretation of these sayings will not taste death."</blockquote>
  <p>(2) Jesus said, "Let one who seeks not stop seeking until that person finds."</p>
  <p>   </p>
  <div class="footer">Copyright The Gnostic Society Library</div>
</body></html>
"""


def test_parse_document_extracts_title_and_paragraph_sections():
    doc = gl.parse_document(DOC_HTML)
    assert "Gospel of Thomas" in doc["title"]
    secs = doc["sections"]
    assert any("secret sayings" in s for s in secs)
    assert any("taste death" in s for s in secs)
    assert any("not stop seeking" in s for s in secs)


def test_parse_document_drops_empty_and_script_blocks():
    doc = gl.parse_document(DOC_HTML)
    for s in doc["sections"]:
        assert s.strip() != ""
        assert "var x" not in s
        # &nbsp;-only paragraph dropped
        assert s.replace("\xa0", "").strip() != ""


def test_parse_document_preserves_section_order():
    doc = gl.parse_document(DOC_HTML)
    secs = doc["sections"]
    i_intro = next(i for i, s in enumerate(secs) if "secret sayings" in s)
    i_one = next(i for i, s in enumerate(secs) if "taste death" in s)
    i_two = next(i for i, s in enumerate(secs) if "not stop seeking" in s)
    assert i_intro < i_one < i_two


# ── Alignment gate ────────────────────────────────────────────────────────
def test_align_ok_requires_equal_length():
    assert gl.align_ok(["a", "b"], ["甲", "乙"])
    assert not gl.align_ok(["a", "b"], ["甲"])


def test_assert_aligned_raises_on_mismatch():
    with pytest.raises(ValueError):
        gl.assert_aligned(["a", "b", "c"], ["甲", "乙"])
    # no raise on match
    gl.assert_aligned(["a"], ["甲"])
