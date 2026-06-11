"""Contract for the /apocrypha 逐節重建 pure helpers (apocrypha_verses.py).

Locks: order_index round-trip, 10-chapters-per-page pagination, the CCEL Charles
chapter:verse parser (incl. single-verse chapters Charles omits the '1' for),
the ZH-onto-EN-skeleton merge (clamp + keep-longest), and the coverage gate.
See .claude/skills/scripture-canon/ + [[feedback_apocrypha_verse_process]].
"""
import apocrypha_verses as av


class TestOrderIndex:
    def test_roundtrip(self):
        assert av.order_index(6, 3) == 6003
        assert av.decode_order_index(6003) == (6, 3)

    def test_chapter_108(self):
        assert av.decode_order_index(av.order_index(108, 42)) == (108, 42)

    def test_sorts_by_chapter_then_verse(self):
        ois = [av.order_index(c, v) for c, v in [(10, 2), (2, 10), (2, 1), (10, 1)]]
        assert sorted(ois) == [av.order_index(2, 1), av.order_index(2, 10),
                               av.order_index(10, 1), av.order_index(10, 2)]

    def test_verse_out_of_range(self):
        import pytest
        with pytest.raises(ValueError):
            av.order_index(1, 1000)


class TestChapterPages:
    def test_ten_per_page(self):
        pages = av.chapter_pages(range(1, 26), per=10)
        assert [len(p) for p in pages] == [10, 10, 5]
        assert pages[0] == list(range(1, 11))
        assert pages[2] == [21, 22, 23, 24, 25]

    def test_dedup_and_sort(self):
        pages = av.chapter_pages([3, 1, 2, 2, 1], per=10)
        assert pages == [[1, 2, 3]]

    def test_non_contiguous(self):
        # Skeleton with gaps (chapters 4,5 absent) still groups by count of 10.
        pages = av.chapter_pages([1, 2, 3, 6, 8, 9, 10, 11, 12, 13, 20], per=10)
        assert pages[0] == [1, 2, 3, 6, 8, 9, 10, 11, 12, 13]
        assert pages[1] == [20]

    def test_labels(self):
        assert av.page_label(list(range(1, 11))) == "第 1–10 章"
        assert av.page_label([11]) == "第 11 章"
        assert av.page_label([]) == ""

    def test_page_index_for_chapter(self):
        pages = av.chapter_pages(range(1, 26), per=10)
        assert av.page_index_for_chapter(pages, 1) == 1
        assert av.page_index_for_chapter(pages, 15) == 2
        assert av.page_index_for_chapter(pages, 25) == 3
        assert av.page_index_for_chapter(pages, 999) == 1  # fallback


# Minimal CCEL-style fixture: chapter markers + bare sequential verse numbers,
# plus a single-verse chapter (3) where Charles omits the "1".
CHARLES_FIXTURE = """
[ Chapter 1 ]
1 The words of the blessing of Enoch.
2 And he took up his parable and said.
[ Chapter 2 ]
1 Observe everything in heaven.
[ Chapter 3 ]
Observe the trees in winter, fourteen do not shed leaves.
[ Chapter 6 ]
1 And it came to pass when men multiplied.
2 the angels saw the daughters of men.
3 and they said, let us choose wives.
"""


class TestParseCharles:
    def setup_method(self):
        self.v = av.parse_charles_chapters(CHARLES_FIXTURE)

    def test_chapters_found(self):
        assert set(self.v) == {1, 2, 3, 6}

    def test_verse_counts(self):
        assert len(self.v[1]) == 2
        assert len(self.v[6]) == 3

    def test_single_verse_chapter_no_marker(self):
        # Chapter 3 has no "1" marker → whole body becomes verse 1.
        assert list(self.v[3]) == [1]
        assert "fourteen" in self.v[3][1]

    def test_verse_text(self):
        assert self.v[1][1].startswith("The words of the blessing")
        assert self.v[6][2] == "the angels saw the daughters of men."

    def test_numerals_in_prose_not_taken_as_verses(self):
        # "fourteen" is a word, not a verse marker; ch3 stays single-verse.
        assert len(self.v[3]) == 1


# Real CCEL Charles markup: per-verse <a name="C_V"> anchors, with the verse
# number floated mid-sentence inside a <sup>. Includes ch9's real quirk where
# CCEL omits the v8 anchor (v8 text folds into v7) and ch3 single verse.
CCEL_ANCHORED_FIXTURE = """
<b>[<a name="Chapter 9">Chapter 9</a>]</b><p>
<a name="9_1"><sup> 1</sup></a> And then Michael and Gabriel looked down and saw much
blood being <a name="9_2"><sup> 2</sup></a> shed upon the earth, and all lawlessness wrought.
<a name="9_3"><sup> 3</sup></a> And now to you, the holy ones, the souls
of men make their suit. <a name="9_7"><sup> 7</sup></a> And Semjaza, to whom Thou
hast given authority, and have slept with the 8 women, and have defiled themselves.
<a name="9_9"><sup> 9</sup></a> And the women have borne giants.
<a name="9_11"><sup> 11</sup></a> And Thou knowest all things before they come to pass.</p>
<b>[<a name="Chapter 3">Chapter 3</a>]</b><p>
<a name="3_1"><sup> 1</sup></a> Observe the trees in winter, fourteen do not shed leaves.</p>
"""


class TestParseCcelAnchored:
    def setup_method(self):
        self.v = av.parse_ccel_anchored(CCEL_ANCHORED_FIXTURE)

    def test_chapters_found(self):
        assert set(self.v) == {9, 3}

    def test_anchor_boundaries_not_midword(self):
        # v1 must END at the v2 anchor, even though "blood being" wraps a line.
        assert self.v[9][1].startswith("And then Michael")
        assert self.v[9][1].rstrip().endswith("much\nblood being") or \
               self.v[9][1].rstrip().endswith("blood being")
        assert self.v[9][2].startswith("shed upon the earth")

    def test_trailing_verses_not_merged(self):
        # The whole point: 9..11 are distinct, not collapsed into v7.
        assert set(self.v[9]) == {1, 2, 3, 7, 9, 11}
        assert self.v[9][9].startswith("And the women have borne giants")
        assert self.v[9][11].startswith("And Thou knowest all things")

    def test_unanchored_verse_folds_into_prior(self):
        # CCEL omits the 9:8 anchor → its text stays attached to v7 (a gap, not a
        # wrong boundary). The bare "8" in prose is NOT taken as a verse.
        assert 8 not in self.v[9]
        assert "slept with the 8 women" in self.v[9][7]

    def test_single_verse_chapter(self):
        assert list(self.v[3]) == [1]
        assert "fourteen" in self.v[3][1]

    def test_chapter_taken_from_verse_anchor(self):
        # chapter number comes from the verse anchor (9_1), robust to heading noise
        assert 9 in self.v and 1 in self.v[9]


# pseudepigrapha.com Charles markup: per-chapter <h5>[Chapter N]</h5> + <ol><li>.
# Includes a leading editorial <blockquote> summary that must NOT become a verse.
PSEUD_FIXTURE = """
<blockquote><em>Moses receives the tables, 1-4. Apostasy, 5-9.</em></blockquote>
<blockquote>THIS is the history of the division of the days.</blockquote>
<h5>[Chapter 1]</h5>
<ol>
  <li>And it came to pass in the first year of the exodus, that God spake to Moses.</li>
  <li>And He said: 'Come up to Me on the Mount.'</li>
  <li>And Moses went up into the mount of God.</li>
</ol>
<h5>[Chapter 2]</h5>
<ol>
  <li>And the angel of the presence spake to Moses.</li>
  <li>For on the first day He created the heavens.</li>
</ol>
"""


class TestParsePseudepigrapha:
    def setup_method(self):
        self.v = av.parse_pseudepigrapha_html(PSEUD_FIXTURE)

    def test_chapters_and_counts(self):
        assert set(self.v) == {1, 2}
        assert len(self.v[1]) == 3
        assert len(self.v[2]) == 2

    def test_verses_are_li_items_in_order(self):
        assert self.v[1][1].startswith("And it came to pass")
        assert self.v[1][2] == "And He said: 'Come up to Me on the Mount.'"
        assert self.v[2][1].startswith("And the angel of the presence")

    def test_summary_blockquote_not_a_verse(self):
        # the <blockquote> summary/intro must not leak in as verse text
        joined = " ".join(self.v[1].values()) + " ".join(self.v[2].values())
        assert "Apostasy" not in joined
        assert "history of the division" not in joined

    def test_single_chapter_no_marker(self):
        html = "<ol><li>First saying.</li><li>Second saying.</li></ol>"
        v = av.parse_pseudepigrapha_html(html)
        assert list(v) == [1]
        assert v[1] == {1: "First saying.", 2: "Second saying."}

    def test_nested_tags_stripped(self):
        html = "<h5>[Chapter 5]</h5><ol><li>And <small>HE</small> said <i>peace</i>.</li></ol>"
        v = av.parse_pseudepigrapha_html(html)
        assert v[5][1] == "And HE said peace ."

    def test_unclosed_li(self):
        # pseudepigrapha.com leaves <li> UNCLOSED (no </li>) — must still split.
        html = ("<h5>[Chapter 1]</h5><ol>\n"
                "<li>And it came to pass in the first year.\n"
                "<li>And He said: Come up.\n"
                "<li>And Moses went up.\n</ol>")
        v = av.parse_pseudepigrapha_html(html)
        assert len(v[1]) == 3
        assert v[1][1].startswith("And it came to pass")
        assert v[1][3] == "And Moses went up."


class TestMergeOntoSkeleton:
    def setup_method(self):
        self.skeleton = {1: {1: "e", 2: "e"}, 2: {1: "e"}, 6: {1: "e", 2: "e", 3: "e"}}

    def test_keeps_only_skeleton_keys(self):
        frags = [{1: {1: "甲", 2: "乙"}, 2: {1: "丙"},
                  99: {1: "外章"},          # chapter not in skeleton → dropped
                  6: {1: "丁", 2: "戊", 3: "己", 4: "多餘"}}]  # verse 4 not in skeleton → dropped
        out = av.merge_verse_windows(frags, self.skeleton)
        assert set(out) == {1, 2, 6}
        assert 99 not in out
        assert set(out[6]) == {1, 2, 3}

    def test_keep_longest_across_overlap(self):
        frags = [{1: {1: "短"}}, {1: {1: "比較長的版本"}}]
        out = av.merge_verse_windows(frags, self.skeleton)
        assert out[1][1] == "比較長的版本"

    def test_blank_text_ignored(self):
        frags = [{1: {1: "  "}}, {1: {1: "實際內容"}}]
        out = av.merge_verse_windows(frags, self.skeleton)
        assert out[1][1] == "實際內容"


class TestVerseRows:
    def test_row_shape_and_order_index(self):
        rows = av.verse_rows("1-enoch", "cct_zh", {6: {1: "abc", 2: "de"}})
        assert len(rows) == 2
        r = rows[0]
        assert r["doc_slug"] == "1-enoch"
        assert r["version_code"] == "cct_zh"
        assert r["order_index"] == 6001
        assert r["chapter"] == 6 and r["verse"] == 1
        assert r["section_label"] == "6:1"
        assert r["char_count"] == 3


class TestCleanZhVerses:
    def test_strip_leading_verse_markers(self):
        assert av.strip_leading_verse_markers("7 你們明白") == "你們明白"
        assert av.strip_leading_verse_markers("10 11 他們") == "他們"
        assert av.strip_leading_verse_markers("以諾的說辭") == "以諾的說辭"
        # glued number is left (not a bare leading token)
        assert av.strip_leading_verse_markers("7你們") == "7你們"

    def test_looks_english(self):
        assert av.looks_english("Another book which Enoch wrote for his son") is True
        assert av.looks_english("以諾的說辭：這是以諾對被揀選者") is False
        assert av.looks_english("亞撒謝(Azaz'el)教人造劍") is False   # CJK-dominant w/ latin name
        assert av.looks_english("short") is False                      # too short

    def test_clean_drops_english_and_strips_numbers(self):
        raw = {108: {1: "Another book which Enoch wrote for his son Methuselah",
                     2: "7 你們明白他們將把自己的靈魂帶到陰間"}}
        out = av.clean_zh_verses(raw)
        assert 1 not in out.get(108, {})            # English dropped
        assert out[108][2] == "你們明白他們將把自己的靈魂帶到陰間"

    def test_clean_removes_empty_chapter(self):
        raw = {5: {1: "Only English here that should be dropped entirely now"}}
        assert av.clean_zh_verses(raw) == {}


class TestRenumberSequential:
    def test_compacts_chapter_keys(self):
        # LLM emitted chapters 3,7,9 → become 1,2,3
        raw = {3: {1: "a", 2: "b"}, 7: {1: "c"}, 9: {1: "d"}}
        out = av.renumber_chapters_sequential(raw)
        assert sorted(out) == [1, 2, 3]
        assert out[1] == {1: "a", 2: "b"}
        assert out[3] == {1: "d"}

    def test_renumbers_verses(self):
        raw = {1: {5: "x", 9: "y"}}   # odd verse numbers → 1,2
        out = av.renumber_chapters_sequential(raw)
        assert out[1] == {1: "x", 2: "y"}

    def test_drops_empty(self):
        raw = {1: {1: "a"}, 2: {1: "  "}}
        out = av.renumber_chapters_sequential(raw)
        assert sorted(out) == [1]


class TestExtractVerseObjects:
    def test_valid_json(self):
        raw = '{"verses":[{"chapter":1,"verse":1,"text":"甲"},{"chapter":1,"verse":2,"text":"乙"}],"last":[1,2]}'
        out = av.extract_verse_objects(raw)
        assert [(o["chapter"], o["verse"], o["text"]) for o in out] == [(1, 1, "甲"), (1, 2, "乙")]

    def test_truncated_json_salvaged(self):
        # array cut off mid-3rd object (token cap) → first two still recovered
        raw = '{"verses":[{"chapter":1,"verse":1,"text":"甲"},{"chapter":1,"verse":2,"text":"乙"},{"chapter":1,"verse":3,"text":"丙'
        out = av.extract_verse_objects(raw)
        assert [(o["chapter"], o["verse"]) for o in out] == [(1, 1), (1, 2)]

    def test_escaped_quotes_in_text(self):
        raw = r'{"verses":[{"chapter":2,"verse":1,"text":"他說：\"平安\"。"}]}'
        out = av.extract_verse_objects(raw)
        assert out[0]["text"] == '他說："平安"。'

    def test_garbage_returns_empty(self):
        assert av.extract_verse_objects("not json at all") == []


class TestUnionFill:
    def test_refills_dropped_seed_verse(self):
        # a prior pass had 1:1 and 1:2; the new pass lost 1:2 (clean dropped it).
        seed = {1: {1: "舊甲", 2: "舊乙"}}
        verses = {1: {1: "新甲較長"}}
        out = av.union_fill(verses, seed)
        assert out[1][1] == "新甲較長"   # new verse wins
        assert out[1][2] == "舊乙"        # dropped seed verse refilled → monotonic

    def test_new_chapter_kept(self):
        seed = {1: {1: "甲"}}
        verses = {1: {1: "甲"}, 2: {1: "新章"}}
        out = av.union_fill(verses, seed)
        assert set(out) == {1, 2}

    def test_monotonic_count(self):
        seed = {1: {i: f"v{i}" for i in range(1, 11)}}     # 10 verses
        verses = {1: {1: "x", 5: "y"}}                      # pass kept only 2
        out = av.union_fill(verses, seed)
        assert sum(len(v) for v in out.values()) == 10      # never below seed


class TestCoverage:
    def test_full_alignment(self):
        en = {1: {1: "a", 2: "b"}}
        zh = {1: {1: "甲", 2: "乙"}}
        c = av.coverage(en, zh)
        assert c["aligned"] == 2 and c["coverage"] == 1.0 and c["en_only"] == 0

    def test_partial(self):
        en = {1: {1: "a", 2: "b"}, 2: {1: "c"}}
        zh = {1: {1: "甲"}}
        c = av.coverage(en, zh)
        assert c["en_verses"] == 3 and c["aligned"] == 1 and c["en_only"] == 2
        assert c["coverage"] == round(1 / 3, 4)

    def test_zh_extra_zero_after_clamp(self):
        en = {1: {1: "a"}}
        zh = {1: {1: "甲"}}
        assert av.coverage(en, zh)["zh_extra"] == 0
