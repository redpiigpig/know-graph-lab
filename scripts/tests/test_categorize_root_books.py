"""Golden-set regression guard for categorize_root_books.classify.

The user manually curated MANUAL_OVERRIDES by moving mis-filed books by hand.
Those corrections are the ground truth — they must never silently regress when
the keyword RULES are edited (first-match-wins makes RULES fragile to reorder).

This suite:
  1. asserts every MANUAL_OVERRIDES entry still resolves to its curated label
     (overrides must win over RULES),
  2. pins a few documented "bleed" filenames that RULES alone would get wrong,
  3. checks the classifier is deterministic and only emits known categories.
Pure function; no Drive/DB.
"""
import categorize_root_books as crb

VALID_CATEGORIES = {
    "神學", "世界宗教", "宗教學", "哲學", "歷史學",
    "社會政治學", "心理學", "自然科學", "人類生物學", "文學",
}


def test_every_manual_override_is_honored():
    """Overrides take precedence over RULES — the whole point of the dict."""
    misfires = []
    for filename, expected in crb.MANUAL_OVERRIDES.items():
        got = crb.classify(filename)
        if got != expected:
            misfires.append((filename, expected, got))
    assert not misfires, "overrides not honored:\n" + "\n".join(
        f"  {f!r}: want {e!r} got {g!r}" for f, e, g in misfires)


def test_overrides_use_only_valid_categories():
    bad = {c for c in crb.MANUAL_OVERRIDES.values() if c not in VALID_CATEGORIES}
    assert not bad, f"overrides use unknown categories: {bad}"


def test_classify_is_deterministic():
    sample = "韋伯，新教倫理與資本主義精神.epub"
    assert crb.classify(sample) == crb.classify(sample)


def test_classify_returns_valid_or_none():
    for filename in list(crb.MANUAL_OVERRIDES)[:20]:
        cat = crb.classify(filename)
        assert cat is None or cat in VALID_CATEGORIES


class TestDocumentedBleedCases:
    """Filenames the user explicitly re-filed; lock them so RULES can't undo it."""

    def test_weber_science_as_vocation_is_sociopolitics(self):
        assert crb.classify(
            "李猛 【德】馬克斯·韋伯，科學作為天職.azw3") == "社會政治學"

    def test_gushibian_doubting_antiquity_is_history(self):
        assert crb.classify(
            "admin，顧頡剛的疑古思想漢儒、孔子與經典.pdf") == "歷史學"

    def test_jiang_weiqiao_buddhist_history_is_world_religion(self):
        assert crb.classify("蔣維喬，蔣維喬中國佛教史.pdf") == "世界宗教"

    def test_eliade_comparative_religion_is_religious_studies(self):
        assert crb.classify(
            "伊利亞德，神聖的存在 比較宗教的範型.pdf") == "宗教學"
