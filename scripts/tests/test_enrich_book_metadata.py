"""Pure matching/extraction helpers of enrich_book_metadata.

The online providers (Open Library, Google Books) are network calls, but the
match-acceptance logic that decides whether a candidate *is* the book — and the
subject extraction that feeds the classifier — are pure. Those are where wrong
metadata sneaks in, so they're what we lock. `_gb_match` / `_ol_match` are fed
hand-built provider-shaped dicts (no network).
"""
import enrich_book_metadata as em


class TestIsCjk:
    def test_chinese_title(self):
        assert em.is_cjk("神聖的存在 比較宗教的範型")

    def test_english_title(self):
        assert not em.is_cjk("The Sacred and the Profane")

    def test_empty(self):
        assert not em.is_cjk("")


class TestTitleMatch:
    def test_exact(self):
        assert em.title_match("資本論", "資本論")

    def test_substring(self):
        assert em.title_match("神聖的存在", "神聖的存在 比較宗教的範型")

    def test_punctuation_insensitive(self):
        assert em.title_match("存在與時間", "存在與時間：")

    def test_unrelated(self):
        assert not em.title_match("資本論", "純粹理性批判")


class TestAuthorMatch:
    def test_missing_query_author_passes(self):
        # caller chose to skip the author check
        assert em.author_match("", ["Anyone"])

    def test_token_overlap(self):
        assert em.author_match("Max Weber", ["Weber, Max"])

    def test_cjk_contains(self):
        assert em.author_match("韋伯", ["馬克斯·韋伯"])

    def test_no_match(self):
        assert not em.author_match("Kant", ["Hegel"])


class TestYear:
    def test_extracts_first_plausible_year(self):
        assert em._year("c1998, reprinted 2003") == 1998

    def test_none_when_absent(self):
        assert em._year("no date here") is None


class TestTitleVariants:
    def test_strips_brackets_and_subtitle(self):
        variants = list(em._title_variants("《存在與時間：基本問題》"))
        assert "存在與時間：基本問題" in variants  # brackets stripped
        assert "存在與時間" in variants            # subtitle dropped


class TestCleanSubjects:
    def test_splits_compound_lcsh(self):
        out = em.clean_subjects(["Religion / Christian Theology / History"])
        assert out == ["Religion", "Christian Theology", "History"]

    def test_dedupes_case_insensitive(self):
        out = em.clean_subjects(["Philosophy", "philosophy", "Ethics"])
        assert out == ["Philosophy", "Ethics"]

    def test_respects_limit(self):
        assert len(em.clean_subjects([str(i) for i in range(50)], limit=5)) == 5

    def test_empty(self):
        assert em.clean_subjects(None) == []
        assert em.clean_subjects([]) == []


class TestGbMatch:
    def _item(self, title, authors, publisher=None, date=None, categories=None):
        return {"volumeInfo": {
            "title": title, "authors": authors,
            "publisher": publisher, "publishedDate": date,
            "categories": categories,
        }}

    def test_accepts_matching_and_extracts_subjects(self):
        items = [self._item("純粹理性批判", ["康德"], "商務印書館", "2004",
                            ["Philosophy / Criticism"])]
        hit = em._gb_match(items, "純粹理性批判", "康德")
        assert hit["publisher"] == "商務印書館"
        assert hit["publish_year"] == 2004
        assert hit["subjects"] == ["Philosophy", "Criticism"]
        assert hit["source"] == "google_books"

    def test_rejects_wrong_author(self):
        items = [self._item("純粹理性批判", ["黑格爾"], "X", "2004")]
        assert em._gb_match(items, "純粹理性批判", "康德") is None

    def test_rejects_wrong_title(self):
        items = [self._item("小邏輯", ["康德"], "X", "2004")]
        assert em._gb_match(items, "純粹理性批判", "康德") is None


class TestOlMatch:
    def _doc(self, title, authors, publisher=None, year=None, subject=None):
        return {"title": title, "author_name": authors,
                "publisher": [publisher] if publisher else None,
                "first_publish_year": year, "subject": subject}

    def test_accepts_and_extracts(self):
        docs = [self._doc("The Sacred and the Profane", ["Mircea Eliade"],
                          "Harcourt", 1959, ["Religion", "Comparative religion"])]
        hit = em._ol_match(docs, "The Sacred and the Profane", "Eliade")
        assert hit["publish_year"] == 1959
        assert "Comparative religion" in hit["subjects"]
        assert hit["source"] == "open_library"
