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
