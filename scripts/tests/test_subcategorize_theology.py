"""Rule layer of theology subcategorization (subcategorize_theology.rule_based_label).

The rule layer decides the confident cases offline so they never reach the
Gemini batch classifier (quota saving) and never drift. This locks:
  - period anchors by figure (Augustine→教父, Luther→改教, Barth→近現代),
  - the 著作 vs 研究 distinction for Augustine,
  - that Schaff / Aquinas series labels are preserved (return None = keep),
  - that every emitted label is one of the 13 canonical labels.
Pure function; no network/DB.
"""
import subcategorize_theology as st


def test_emitted_labels_are_canonical():
    cases = [
        ("奧古斯丁懺悔錄", "奧古斯丁", ""),
        ("路德神學導論", "路德", ""),
        ("卡爾巴特教會教義學", "巴特", ""),
        ("基督教倫理學導論", "", ""),
        ("默觀祈禱的靈修生活", "", ""),
    ]
    for title, author, sub in cases:
        label = st.rule_based_label(title, author, sub)
        if label is not None:
            assert label in st.LABELS, f"{title!r} → non-canonical {label!r}"


class TestPeriodAnchors:
    def test_augustine_work_is_patristic(self):
        assert st.rule_based_label("奧古斯丁論三位一體", "Augustine", "") == "教父著作"

    def test_augustine_research_is_patristic_research(self):
        assert st.rule_based_label("奧古斯丁研究", "", "") == "教父研究"

    def test_luther_is_reformation(self):
        assert st.rule_based_label("路德文集", "Luther", "") == "改教著作"

    def test_calvin_is_reformation(self):
        assert st.rule_based_label("基督教要義", "Calvin", "") == "改教著作"

    def test_barth_is_modern(self):
        assert st.rule_based_label("教會教義學", "Barth", "") == "近現代著作"

    def test_aquinas_is_medieval(self):
        assert st.rule_based_label("神學大全", "阿奎那", "") == "中世紀著作"


class TestThemeAnchors:
    def test_textbook(self):
        assert st.rule_based_label("系統神學概論", "", "") == "教科書/概論"

    def test_moral_theology(self):
        assert st.rule_based_label("生命倫理神學", "", "") == "倫理神學"

    def test_spirituality(self):
        # NB: avoid 導論/概論 in the title — those hit 教科書/概論 first by design.
        assert st.rule_based_label("默觀與祈禱的靈修生活", "", "") == "靈修神學"

    def test_hermeneutics(self):
        assert st.rule_based_label("神學詮釋學釋經方法", "", "") == "神學詮釋/哲學"


class TestPreserve:
    def test_canonical_existing_sub_is_kept(self):
        assert st.rule_based_label("任何書", "", "教父著作") == "教父著作"

    def test_schaff_series_is_preserved(self):
        # Returning None tells the caller to keep the existing series label.
        assert st.rule_based_label("ANF Vol 1", "", "Schaff - ANF (10 vols)") is None

    def test_unknown_defers_to_llm(self):
        # No anchor, no existing label → None → goes to the Gemini batch.
        assert st.rule_based_label("一本難以判斷的神學書", "", "") is None
