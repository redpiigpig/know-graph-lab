"""Two-axis, confidence-scored classifier (book_classifier.classify).

Locks the fix for "categorization still unideal":
  - scoring beats first-match-wins on the contested boundaries
    (政治思想史 / 思想史 / 宗教史 / 基督教史-傳記 / 哲學家論神學)
  - confidence drops on weak single-keyword hits → caller quarantines
  - author anchors pin the theme over a generic title word
Pure function; no network/DB/LLM.
"""
import book_classifier as bc


# ── unambiguous anchors ────────────────────────────────────────────────────

class TestClearCases:
    def test_systematic_theology(self):
        r = bc.classify("系統神學導論", "巴特")
        assert r.category == "神學" and not r.uncertain

    def test_single_religion_history_is_world_religion(self):
        assert bc.classify("中國佛教史").category == "世界宗教"

    def test_comparative_religion_is_religious_studies(self):
        assert bc.classify("比較宗教學導論").category == "宗教學"

    def test_quantum_physics_is_natural_science(self):
        assert bc.classify("量子力學與相對論").category == "自然科學"

    def test_jung_is_psychology(self):
        assert bc.classify("原型與集體潛意識", "榮格").category == "心理學"


# ── the contested boundaries (the whole point of the module) ───────────────

class TestDisambiguation:
    def test_political_thought_history_goes_to_sociopolitics(self):
        # 政治思想史 must NOT land in 哲學 (思想) or 歷史學 (史).
        r = bc.classify("西方政治思想史")
        assert r.category == "社會政治學"
        assert "政治思想" in r.reason

    def test_plain_intellectual_history_defaults_to_history(self):
        r = bc.classify("中國近代思想史")
        assert r.category == "歷史學"

    def test_intellectual_history_with_philosopher_anchor_goes_philosophy(self):
        r = bc.classify("康德思想史研究", "康德")
        assert r.category == "哲學"

    def test_comparative_religion_history(self):
        assert bc.classify("比較宗教史 諸宗教的起源").category == "宗教學"

    def test_christian_church_history_biography_is_world_religion(self):
        # 教會史 + 傳記 genre → 世界宗教, not 神學, even though 神學-ish words exist.
        r = bc.classify("基督教會史：奧古斯丁評傳")
        assert r.category == "世界宗教"

    def test_philosopher_on_theology_stays_philosophy(self):
        r = bc.classify("康德的神學", "康德")
        assert r.category == "哲學"


# ── confidence / quarantine contract ───────────────────────────────────────

class TestConfidence:
    def test_no_match_is_none_and_uncertain(self):
        r = bc.classify("一本沒有領域關鍵字的書", "某人")
        assert r.category is None and r.uncertain and r.confidence == 0.0

    def test_strong_anchor_is_confident(self):
        assert bc.classify("資本論", "馬克思").confidence >= bc.LOW_CONFIDENCE

    def test_tie_between_two_categories_is_uncertain(self):
        # equal-weight hits in two distinct themes → near-zero margin → review.
        r = bc.classify("哲學與小說")  # 哲學(2) vs 文學(2) tie
        assert r.uncertain

    def test_confidence_is_normalised_margin(self):
        r = bc.classify("系統神學", "巴特")
        assert 0.0 <= r.confidence <= 1.0


# ── genre axis ─────────────────────────────────────────────────────────────

class TestGenreAxis:
    def test_detects_collected_works(self):
        assert bc.classify("卡謬全集").genre == "原典"

    def test_detects_biography(self):
        assert bc.classify("尼采評傳").genre == "傳記"
