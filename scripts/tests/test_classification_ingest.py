"""Ingest keyword pre-classifier (ingest_new_books.fallback_category).

The cheap keyword classifier must cover the dominant Christian-studies
backlog so daily ingest doesn't burn Gemini quota (skill: target ≥95%
coverage, 0 Gemini calls). Tests lock the documented routing and the
filename-fallback behavior (parse strips subtitle + s2tw, so the raw
filename must still be searched).
"""
import ingest_new_books as ing


class TestChristianStudiesRouting:
    def test_english_patristic_keywords_to_theology(self):
        for kw in ("Augustine Confessions", "Schaff Nicene Fathers",
                   "Tertullian Apology", "Chrysostom Homilies"):
            assert ing.fallback_category(kw, "") == "神學", kw

    def test_chinese_theology_keywords(self):
        for kw in ("神學大全", "教父原典", "信理神學", "三位一體論"):
            assert ing.fallback_category(kw, "") == "神學", kw


class TestWorldReligionRouting:
    def test_chinese_world_religion_history(self):
        for kw in ("佛教史", "伊斯蘭教史", "可蘭經", "猶太教"):
            assert ing.fallback_category(kw, "") == "世界宗教", kw

    def test_english_world_religion(self):
        assert ing.fallback_category("Avesta and Zoroastrian ritual", "") == "世界宗教"
        assert ing.fallback_category("Islam in the modern world", "") == "世界宗教"


class TestFilenameFallback:
    def test_keyword_only_in_raw_filename_still_matches(self):
        # title/author lost the keyword (subtitle stripped), but the raw
        # filename retains it — must still classify.
        cat = ing.fallback_category("某書", "", "Bonhoeffer - Letters and Papers.epub")
        assert cat == "神學"


class TestUnmatched:
    def test_returns_none_when_nothing_matches(self):
        # Plain literature with no domain keyword → defer to Gemini (None).
        assert ing.fallback_category("A Novel About Nothing", "Some Author") is None
