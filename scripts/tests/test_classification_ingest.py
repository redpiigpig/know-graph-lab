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


class TestReligiousStudiesRouting:
    """🚨 宗教學必須在神學／世界宗教的關鍵字**之前**判。

    否則伊利亞德《神聖與世俗》會被「聖」系列抓進神學、Peter Brown
    《西方基督教世界的興起》會被 "christ" 抓走——兩個都是實際踩到的誤分類。
    分類表見 [[ebook-pipeline]] SKILL.md「神學 vs 世界宗教 vs 宗教學」。
    """

    def test_phenomenology_and_theory_of_religion(self):
        for kw in ("The Sacred and The Profane The Nature of Religion",
                   "The meaning and end of religion",
                   "An Interpretation of Religion",
                   "The Encyclopedia of religion",
                   "Sacred Worlds An Introduction to Geography and Religion"):
            assert ing.fallback_category(kw, "") == "宗教學", kw

    def test_sociology_and_psychology_of_religion(self):
        # 🚨 宗教心理學歸宗教學，不是心理學；宗教社會學同理
        assert ing.fallback_category("The Psychology of Religion and Coping", "") == "宗教學"
        assert ing.fallback_category("the social sources of denominationalism", "") == "宗教學"

    def test_cognitive_science_of_religion(self):
        assert ing.fallback_category("Why would anyone believe in God", "") == "宗教學"

    def test_eliade_in_both_chinese_renderings(self):
        # 同一位作者站上有兩種譯名：伊利亞德／以利亞德
        assert ing.fallback_category("神聖與世俗", "米爾恰·伊利亞德") == "宗教學"
        assert ing.fallback_category("不死與自由", "米爾恰·以利亞德") == "宗教學"
        assert ing.fallback_category("薩滿教 古老的入迷術", "米爾恰·伊利亞德") == "宗教學"

    def test_chinese_religious_studies_terms(self):
        for kw in ("宗教現象學", "宗教社會學", "宗教心理學", "神話學", "世界宗教理念史"):
            assert ing.fallback_category(kw, "") == "宗教學", kw

    def test_theology_proper_is_not_hijacked(self):
        # 真正的神學書不可以被宗教學規則吃掉
        assert ing.fallback_category("神學大全", "") == "神學"
        assert ing.fallback_category("多元、分歧與認同 神學與文化的探索", "賴品超") == "神學"
        assert ing.fallback_category("Augustine Confessions", "") == "神學"


class TestChurchHistoryRouting:
    """教會史／宗教改革史 → 世界宗教（基督教自身的歷史敘述），不是神學。"""

    def test_english_church_history(self):
        assert ing.fallback_category("The Rise of Western Christendom", "Peter Brown") == "世界宗教"
        assert ing.fallback_category(
            "War against the Idols The Reformation of Worship from Erasmus to Calvin",
            "Carlos M. N. Eire") == "世界宗教"

    def test_chinese_church_history(self):
        for kw in ("臺灣天主教史研究論集", "基督教史", "宗教改革史"):
            assert ing.fallback_category(kw, "") == "世界宗教", kw

    def test_patristic_texts_stay_theology(self):
        # 教父原典不是教會史
        assert ing.fallback_category("Schaff Nicene Fathers", "") == "神學"


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
