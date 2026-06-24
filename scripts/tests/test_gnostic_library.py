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


def test_make_slug_caps_length_at_word_boundary():
    long = "On the Trail of the Winged God: Hermes and Hermeticism Throughout the Ages and Beyond the Renaissance"
    s = gl.make_slug(long)
    assert len(s) <= 110
    assert not s.endswith("-")        # cut at a hyphen boundary, no trailing dash


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


CATEGORY_INDEX_NOISE_HTML = """
<html><body>
  <a href="naghamm/thunder.html">The Thunder,
        Perfect   Mind</a>
  <a href="audio/Sorrow_of_Sophia.mp3">The Sorrow of Sophia (audio)</a>
  <a href="naghamm/intro.pdf">Introduction (PDF)</a>
  <a href="library/gs.htm">Classical Gnostic Scriptures</a>
  <a href="naghamm/gthom.html">The Gospel of Thomas</a>
</body></html>
"""


def test_parse_category_index_collapses_title_whitespace():
    docs = gl.parse_category_index(CATEGORY_INDEX_NOISE_HTML, base_path="naghamm/nhl.html")
    titles = [d["title"] for d in docs]
    assert "The Thunder, Perfect Mind" in titles   # newlines + runs collapsed


def test_parse_category_index_drops_assets_and_category_crosslinks():
    docs = gl.parse_category_index(CATEGORY_INDEX_NOISE_HTML, base_path="naghamm/nhl.html")
    urls = " ".join(d["url"] for d in docs)
    assert ".mp3" not in urls            # audio dropped
    assert ".pdf" not in urls            # pdf asset dropped
    assert "gs.htm" not in urls          # cross-link to another category index dropped
    assert any(d["title"] == "The Gospel of Thomas" for d in docs)


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


# gnosis.org real-world shape: one <p> with <br>-line-broken paragraphs,
# blank lines marked by "&nbsp;<br>", inside nested <blockquote>.
BR_DOC_HTML = """
<html><head><title>The Gospel of Thomas</title></head><body>
<blockquote><blockquote>
  <h3 align="center">THE GOSPEL OF THOMAS</h3>
  <p>&nbsp;<br>
    These are the hidden sayings that the living Yeshua spoke. <br>
    &nbsp;<br>
    (1)<br>
    And he said, <br>
    Whoever discovers what these sayings mean <br>
    will not taste death.<br>
    &nbsp;<br>
    (2)<br>
    Yeshua said, <br>
    Seek and do not stop seeking until you find.<br>
  </p>
</blockquote></blockquote>
</body></html>
"""


def test_parse_document_splits_br_delimited_paragraphs():
    doc = gl.parse_document(BR_DOC_HTML)
    secs = doc["sections"]
    # 3 logical paragraphs: intro + saying 1 + saying 2 (NOT one big blob)
    assert len(secs) == 3
    assert "hidden sayings" in secs[0] and "taste death" not in secs[0]
    assert "taste death" in secs[1]
    assert "stop seeking" in secs[2]
    # &nbsp;-only lines are not their own sections
    assert all(s.replace("\xa0", "").strip() for s in secs)


# gnosis.org Manichaean/Mandaean hymn pages: ancient HTML with UNCLOSED <p>
# tags (HTML5 auto-closes <p> on the next <p>, but Python's html.parser nests
# them instead → every content <p> looked "non-leaf" and got dropped → 0
# sections). An HTML5-compliant parser must read each <p> as its own paragraph.
# Mirrors http://gnosis.org/library/hymnfa.htm (also doubly-nested <body>).
HYMN_DOC_HTML = """
<html><head><title>The Hymn to the Father of Greatness</title></head><body>
<p>
<h2>Manichaean Scriptures</h2>
<h6>Gnosis Archive | Library | Bookstore | Index</h6>
<body>
<p>The Hymn to the Father of Greatness - a hymn ascribed to Mani, in Parthian.
<p>You are worthy of praise, beneficient Father, primeval Ancestor!
<p>You, Lord, are the first alif and the last tau.
<p>All gods and aeons, the deities of Light, bring praise to you.
</body>
</body></html>
"""


def test_parse_document_handles_unclosed_p_hymn_pages():
    doc = gl.parse_document(HYMN_DOC_HTML)
    secs = doc["sections"]
    # all four content <p> become their own paragraph (not swallowed as non-leaf)
    assert len(secs) == 4
    assert "ascribed to Mani" in secs[0]
    assert "beneficient Father" in secs[1]
    assert "first alif" in secs[2]
    assert "deities of Light" in secs[3]
    # nav chrome (<h2>/<h6> menu) must not become a section
    assert all("Gnosis Archive" not in s for s in secs)


# ── Alignment gate ────────────────────────────────────────────────────────
def test_align_ok_requires_equal_length():
    assert gl.align_ok(["a", "b"], ["甲", "乙"])
    assert not gl.align_ok(["a", "b"], ["甲"])


def test_assert_aligned_raises_on_mismatch():
    with pytest.raises(ValueError):
        gl.assert_aligned(["a", "b", "c"], ["甲", "乙"])
    # no raise on match
    gl.assert_aligned(["a"], ["甲"])


# ── Translation quality gate (classify_translation) ───────────────────────
def test_gate_passes_a_faithful_translation():
    assert gl.classify_translation(
        "Yeshua said, Seek and you shall find.",
        "耶穌說：尋求，就必尋見。") is None


def test_gate_flags_halluc_heading():
    # short EN heading blown up into a long fabricated ZH essay
    assert gl.classify_translation(
        "CHAP. XII.--THE DOCTRINES OF PTOLEMY.",
        "第十二章\n\n托勒密派宣稱，在太一之上存在著一個超越一切名稱的存有，"
        "他們稱之為深淵，乃一切事物之源，與沉默配偶而居。深淵與沉默流溢出努斯"
        "與真理，努斯又流溢出邏各斯與生命，如此構成普累若麻的整體結構。索菲亞"
        "因渴慕深淵而墮落，其情慾化為物質，巨匠造物主由此而生，無知地造作了這"
        "個有缺陷的世界，並自命為唯一的神。"
    ) == "halluc_heading"


def test_gate_flags_untranslated_english_left():
    assert gl.classify_translation(
        "The Marcosians assert that things visible were made after the invisible.",
        "第十七章\n\nThe Marcosians assert that the things which are visible were made"
    ) == "untranslated"


def test_gate_flags_meta_commentary_leak():
    assert gl.classify_translation(
        "(John goes from Miletus to Ephesus.)",
        "我已準備好接收英文文本進行翻譯。請提供需要翻譯的英文段落。"
    ) == "meta_leak"


def test_gate_flags_word_by_word_english_gloss():
    assert gl.classify_translation(
        "I am the Light which is in them.",
        "我（I）是（am）那（the）光（Light），那（the）光（Light）是（is）普累若麻。"
    ) == "word_gloss"


def test_gate_does_not_flag_legit_first_person_content():
    # "我無法保持貞潔" is a real translation of "I cannot remain chaste", NOT a leak
    assert gl.classify_translation(
        "I cannot remain chaste; first, I do not fret at the cutting of trees.",
        "我無法保持貞潔；首先，我不為砍伐樹木而憂慮。") is None


def test_gate_does_not_flag_legit_scholarly_transliterations():
    # （gnosis）（batos）（syzygy）are valid annotations, not a word-gloss leak
    assert gl.classify_translation(
        "Sophia, without her consort, emanated from the Pleroma.",
        "索菲亞未經其配偶（syzygy）便從普累若麻流出，墮入無知（gnosis）的深淵（batos）。"
    ) is None


def test_gate_does_not_flag_a_short_heading_kept_short():
    assert gl.classify_translation("PREFACE.", "序言") is None
    assert gl.classify_translation("OF GOD AND THE UNIVERSE", "論神與宇宙") is None


def test_gate_flags_wenyan_classical_drift():
    # 白話/和合本 mandated; 名曰 / 焉 / 矣 are classical particles → flag
    assert gl.classify_translation(
        "There were two snakes; one was named 'Heavy-laden'. Its tail was very long.",
        "又聞昔日有二蛇，其中一蛇名曰「負重者」。其尾甚為長焉。") == "wenyan"


def test_gate_allows_baihua_union_version_register():
    # proper 白話/和合本 voice must pass (uses 名叫/說/看哪/他便, not 曰/焉)
    assert gl.classify_translation(
        "Like a shepherd who sees a lion, he takes a lamb and sets it as a snare.",
        "如同牧人看見獅子，他便取一隻羊羔，設為陷阱。看哪，他就這樣救了羊圈。") is None
    # 白話 words containing 乎/其 must NOT be flagged
    assert gl.classify_translation(
        "He almost reached the gate, among the others.",
        "他幾乎到了門口，在其他人當中。") is None


def test_gate_flags_classical_pronouns():
    assert gl.classify_translation("Because you were absent, my son longed to learn.",
                                   "因為汝不在時，我的兒子渴望學習。") == "wenyan"
    assert gl.classify_translation("I was compelled to tell him.",
                                   "吾被迫告訴他。") == "wenyan"


def test_gate_does_not_flag_baihua_pronouns():
    assert gl.classify_translation("Because you were absent, I told my son.",
                                   "因為你不在，我就告訴了我的兒子。") is None


def test_gate_allows_hehe_ben_zai_exclamations():
    # 和合本 uses 哉-exclamations freely (聖哉 Sanctus 啟4:8, 禍哉 woe 太23,
    # 哀哉 lament 啟18) — these are the TARGET register, not 文言 drift.
    assert gl.classify_translation(
        "They all said with one voice: Holy, Holy, Holy! Amen.",
        "他們都同聲說：「聖哉，聖哉，聖哉！阿們！」") is None
    assert gl.classify_translation(
        "they deserve woe from the Creator.", "他們才該遭受造物主的禍哉。") is None
    # genuine 文言 drift via real markers (汝/曰/矣) is still flagged
    assert gl.classify_translation("Well said, my son!", "善哉！汝言是也。") == "wenyan"
