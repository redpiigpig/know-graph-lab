"""The ten-item exercise contract, as executable rules.

Contract: skills/build-original-language-reader/references/exercise-sets.md.
Each test below stands for a way an exercise set has actually gone wrong, or
could go wrong silently: a page that prints ten well-set sentences while the
learner is quietly being taught a word the book has not reached, or reading a
composed sentence nobody checked as though it were Scripture.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validate_reader_exercises import (  # noqa: E402
    failures_for_item,
    failures_for_lesson,
    failures_for_payload,
)


def quoted_item(number: int = 1, **overrides) -> dict:
    item = {
        "no": number,
        "kind": "quoted",
        "ref": "Gen.18.21",
        "text": "וְאִם־לֹא אֵדָעָה",
        "chinese": "若不然，我也要知道。",
        "chineseSource": "和合本修訂版（2010）",
        "targetWords": [{"pointed": "יָדַע", "strongs": ["H3045"]}],
        "verification": {"unattested": [], "untaught": [], "passed": True},
    }
    item.update(overrides)
    return item


def composed_item(number: int = 4, **overrides) -> dict:
    item = quoted_item(number)
    item.update(
        {
            "kind": "composed",
            "text": "אַל־תִּכְתֹּב בַּשַּׁבָּת",
            "chinese": "不可在安息日書寫。",
            "chineseSource": "",
            "reviewedBy": "author",
        }
    )
    item.pop("ref", None)
    item.update(overrides)
    return item


def lesson(items=None, **overrides) -> dict:
    body = {
        "lesson": 13,
        "items": items if items is not None else [quoted_item(n) for n in range(1, 4)]
        + [composed_item(n) for n in range(4, 11)],
        "coverage": {"lessonWords": 20, "practised": 20, "notPractised": []},
    }
    body.update(overrides)
    return body


def payload(lessons=None, **overrides) -> dict:
    body = {
        "schemaVersion": "1.0.0",
        "languageCode": "hbo",
        "direction": "original-to-chinese",
        "itemsPerLesson": 10,
        "lessons": lessons if lessons is not None else [lesson()],
    }
    body.update(overrides)
    return body


def test_a_complete_set_passes():
    assert failures_for_payload(payload()) == []


def test_untaught_word_is_rejected():
    """The whole point of the cumulative rule: no word before its lesson."""
    item = composed_item(verification={"unattested": [], "untaught": ["שָׁמַר"], "passed": False})
    problems = failures_for_item(item, language="hbo")
    assert any("尚未教過" in problem for problem in problems)


def test_invented_form_is_rejected():
    item = composed_item(
        verification={"unattested": ["הַקּוֹלוֹת"], "untaught": [], "passed": False}
    )
    problems = failures_for_item(item, language="hbo")
    assert any("查無此形" in problem for problem in problems)


def test_composed_item_needs_an_author_review():
    """Machine verification is not review: the gate cannot see syntax."""
    item = composed_item(reviewedBy="model-draft")
    problems = failures_for_item(item, language="hbo")
    assert any("未經作者逐句複核" in problem for problem in problems)


def test_quoted_item_needs_reference_and_translation_credit():
    problems = failures_for_item(quoted_item(ref="", chineseSource=""), language="hbo")
    assert any("沒有出處" in problem for problem in problems)
    assert any("沒有註明譯本" in problem for problem in problems)


def test_chinese_answer_may_not_carry_the_original_script():
    """A Chinese line that still shows Hebrew is an untranslated placeholder."""
    problems = failures_for_item(
        quoted_item(chinese="若不然，我也要知道 אֵדָעָה。"), language="hbo"
    )
    assert any("混進了原文字符" in problem for problem in problems)


def test_japanese_reader_may_keep_latin_letters_out_of_the_rule():
    """Only the scripts of the taught language are barred from the answer."""
    hebrew = failures_for_item(quoted_item(chinese="安息日 shabbat 的意思"), language="hbo")
    japanese = failures_for_item(quoted_item(chinese="安息日 shabbat 的意思"), language="ja")
    assert any("拉丁字母" in problem for problem in hebrew)
    assert not any("拉丁字母" in problem for problem in japanese)


def test_lesson_must_have_exactly_ten_items():
    problems = failures_for_lesson(lesson(items=[quoted_item(n) for n in range(1, 10)]),
                                   language="hbo")
    assert any("應為 10 題" in problem for problem in problems)


def test_lesson_must_keep_three_quoted_anchors():
    """丙: composed sentences lead, but the learner always has real text to compare."""
    items = [quoted_item(1), quoted_item(2)] + [composed_item(n) for n in range(3, 11)]
    problems = failures_for_lesson(lesson(items=items), language="hbo")
    assert any("至少要 3 題" in problem for problem in problems)


def test_uncovered_vocabulary_fails_the_lesson():
    problems = failures_for_lesson(
        lesson(coverage={"lessonWords": 20, "practised": 18,
                         "notPractised": [{"pointed": "אֲרוֹן"}, {"pointed": "שַׁבָּת"}]}),
        language="hbo",
    )
    assert any("沒練到" in problem for problem in problems)
    assert any("未達全覆蓋" in problem for problem in problems)


def test_reverse_direction_is_refused():
    """中譯原文 was dropped: no single right answer, and nobody to mark it."""
    problems = failures_for_payload(payload(direction="chinese-to-original"))
    assert any("original-to-chinese" in problem for problem in problems)


def test_duplicate_lesson_numbers_are_caught():
    problems = failures_for_payload(payload(lessons=[lesson(), lesson()]))
    assert any("重複出現" in problem for problem in problems)


@pytest.mark.parametrize("field", ["text", "chinese"])
def test_empty_fields_are_caught(field):
    problems = failures_for_item(quoted_item(**{field: "  "}), language="hbo")
    assert problems
