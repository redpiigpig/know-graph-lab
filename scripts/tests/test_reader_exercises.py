"""The ten-item exercise contract, as executable rules.

Contract: skills/build-original-language-reader/references/exercise-sets.md.
Each test below stands for a way an exercise set has actually gone wrong, or
could go wrong silently: a page that prints ten well-set sentences while the
learner is quietly being taught a word the book has not reached, a composed
sentence nobody checked being read as though it were Scripture, or the answer
sitting in plain sight beside the question it answers.
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
        "answerKeyRef": "Gen.18.21",
        "targetWords": [{"ordinal": 12, "pointed": "יָדַע", "strongs": ["H3045"]}],
        "verification": {"unattested": [], "untaught": [], "passed": True},
    }
    item.update(overrides)
    return item


def composed_item(number: int = 4, **overrides) -> dict:
    item = quoted_item(number)
    item.update({"kind": "composed", "text": "אַל־תִּכְתֹּב בַּשַּׁבָּת", "reviewedBy": "author"})
    item.pop("ref", None)
    item.pop("answerKeyRef", None)
    item.update(overrides)
    return item


def lesson(items=None, **overrides) -> dict:
    body = {
        "lesson": 13,
        "items": items
        if items is not None
        else [quoted_item(n) for n in range(1, 4)] + [composed_item(n) for n in range(4, 11)],
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
    assert any("尚未教過" in problem for problem in failures_for_item(item))


def test_invented_form_is_rejected():
    item = composed_item(verification={"unattested": ["הַקּוֹלוֹת"], "untaught": [], "passed": False})
    assert any("查無此形" in problem for problem in failures_for_item(item))


def test_composed_item_needs_an_author_review():
    """Machine verification is not review: the gate cannot see syntax."""
    item = composed_item(reviewedBy="model-draft")
    assert any("未經作者逐句複核" in problem for problem in failures_for_item(item))


def test_quoted_item_needs_a_reference():
    assert any("沒有出處" in problem for problem in failures_for_item(quoted_item(ref="")))


def test_an_exercise_may_not_print_its_own_translation():
    """The exercise is the part the learner does; the Chinese belongs to the reading."""
    problems = failures_for_item(quoted_item(chinese="若不然，我也要知道。"))
    assert any("把答案印在題目旁邊" in problem for problem in problems)


def test_lesson_must_have_exactly_ten_items():
    items = [quoted_item(n) for n in range(1, 10)]
    assert any("應為 10 題" in problem for problem in failures_for_lesson(lesson(items=items)))


def test_short_anchors_are_allowed_only_when_the_lesson_says_why():
    """The first lessons of every reader can run out of quotable text.

    Twenty nouns and no verb leave nothing in the corpus built only from them,
    so falling short is legitimate -- but it has to be stated on the lesson, or
    a page silently drops the one part of the exercise that is guaranteed right.
    """
    items = [quoted_item(1)] + [composed_item(n) for n in range(2, 11)]
    unexplained = failures_for_lesson(lesson(items=items))
    explained = failures_for_lesson(lesson(items=items, note="本課無可用經典原句，十題全由自撰題補"))
    assert any("必須在 note 說明原因" in problem for problem in unexplained)
    assert explained == []


def test_uncovered_vocabulary_fails_the_lesson():
    problems = failures_for_lesson(
        lesson(
            coverage={
                "lessonWords": 20,
                "practised": 18,
                "notPractised": [{"pointed": "אֲרוֹן"}, {"pointed": "שַׁבָּת"}],
            }
        )
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


@pytest.mark.parametrize("field", ["text"])
def test_empty_fields_are_caught(field):
    assert failures_for_item(quoted_item(**{field: "  "}))
