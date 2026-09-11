#!/usr/bin/env python3
"""Assemble the Hebrew reader's ten-item exercise set from its two sources.

Three items per lesson are quoted Scripture, mined by `build_hebrew_exercises.py`
and answered from 和合本修訂版（2010）.  Seven are written by the author and
live in `composed-draft-NN.json`.  This command joins them, re-runs the corpus
verification on every item rather than trusting what a draft claims about
itself, and emits the payload that `validate_reader_exercises.py` gates.

No exercise carries a translation.  Printing the Chinese beside the sentence
would answer the question the exercise asks; the Chinese belongs to the
reading, which is the model text.  What each item keeps instead is the
reference, so an answer booklet can be set later from the published edition.

A lesson that cannot field three quoted anchors says so on itself.  The
earliest lessons of this reader are twenty nouns with no verb among them, and
the corpus has no sentence built only from those.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from select_hebrew_memory_verses import (  # noqa: E402
    DEFAULT_VOCAB,
    DEFAULT_WLC,
    load_vocabulary,
    load_wlc,
)
from build_hebrew_exercises import cumulative_sets  # noqa: E402
import compose_hebrew_sentences as checker  # noqa: E402
from validate_reader_exercises import failures_for_payload, report  # noqa: E402

CACHE = ROOT / "output/source-cache/original-readers/hebrew-full"
MINED = CACHE / "exercises.json"
OUTPUT = CACHE / "exercise-set.json"
QUOTED_PER_LESSON = 3
ANSWER_KEY_EDITION = "和合本修訂版（2010）"


MIN_CLAUSE_WORDS_FOR_ANCHOR = 4


def pick_quoted(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Take the anchors a learner can actually check an answer against.

    Whole verses come first, and a clause has to be long enough to stand as a
    sentence on its own.  A three-word scrap such as בֵּית אֲחֵי אֲדֹנִי verifies
    perfectly and is still not an exercise: there is nothing in it to translate
    and nothing for the eventual answer key to point at.
    """
    usable = [
        item
        for item in items
        if item.get("kind") in {"verse", "clause"}
        and (item.get("kind") == "verse" or item.get("tokenCount", 0) >= MIN_CLAUSE_WORDS_FOR_ANCHOR)
    ]
    usable.sort(
        key=lambda item: (
            0 if item.get("kind") == "verse" else 1,
            -len(item.get("targetWords") or []),
            item.get("tokenCount", 99),
        )
    )
    return usable[:QUOTED_PER_LESSON]


def load_drafts(lesson: int) -> list[dict[str, Any]]:
    path = CACHE / f"composed-draft-{lesson:02d}.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("sentences", [])


def taught_codes(vocabulary, upto: int) -> frozenset:
    """The bound morphemes the learner has met by this lesson."""
    return frozenset(
        code
        for number in sorted(vocabulary)
        if number <= upto
        for entry in vocabulary[number]
        for code in entry.bound_codes
    )


def bound_codes_by_form(verses) -> dict[str, set[str]]:
    """Which bound morphemes each written form carries.

    The conjunction ו and the prepositions ב כ ל are taught as lesson words but
    never stand alone, so MorphHB gives them a letter code inside the lemma
    instead of a Strong number.  Counting coverage by Strong alone silently
    reports them as never practised, however many sentences begin with them.
    """
    index: dict[str, set[str]] = {}
    for verse in verses:
        for token in verse.tokens:
            if token.text and token.lemma_codes:
                index.setdefault(checker.bare(token.text), set()).update(token.lemma_codes)
    return index


def target_words_in(text: str, lesson_items, pointed, skeleton, codes=None) -> list[dict[str, Any]]:
    """Which of the lesson's twenty words a sentence actually practises.

    Matching is by Strong number, looked up from the written form, not by
    letters.  A consonant-substring test says אָב is practised by אָבַד and that
    the lesson word for Mass is practised by the verb "he sent" -- the same
    false-coverage this series has hit in both Hebrew and Latin.  Whatever the
    corpus says a form can be, that is what the sentence practises.
    """
    strongs: set[str] = set()
    present_codes: set[str] = set()
    for piece in checker.split_words(text):
        key = checker.bare(piece)
        for analysis_strongs, analysis_codes in (
            pointed.get(key) or skeleton.get(checker.consonants(piece)) or ()
        ):
            strongs |= analysis_strongs
            present_codes |= analysis_codes
    return [
        item.public_record()
        for item in lesson_items
        if (set(item.strongs) & strongs) or (item.bound_codes & present_codes)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    mined = json.loads(MINED.read_text(encoding="utf-8"))
    mined_by_lesson = {row["lesson"]: row for row in mined.get("lessons", [])}
    vocabulary = load_vocabulary(DEFAULT_VOCAB)
    verses = load_wlc(DEFAULT_WLC)
    pointed, skeleton = checker.build_attested(verses)
    codes = bound_codes_by_form(verses)
    curriculum_codes = taught_codes(vocabulary, max(vocabulary))

    lessons_out: list[dict[str, Any]] = []
    thin_anchors: list[int] = []
    missing_drafts: list[int] = []

    for lesson, lesson_items, known in cumulative_sets(vocabulary):
        codes_known = taught_codes(vocabulary, lesson)
        quoted = pick_quoted((mined_by_lesson.get(lesson) or {}).get("items", []))
        if len(quoted) < QUOTED_PER_LESSON:
            thin_anchors.append(lesson)
        drafts = load_drafts(lesson)
        if not drafts:
            missing_drafts.append(lesson)

        items: list[dict[str, Any]] = []
        for row in quoted:
            text = row["text"]
            items.append(
                {
                    "kind": "quoted",
                    "ref": row["ref"],
                    "text": text,
                    "answerKeyRef": row["ref"],
                    "answerKeyEdition": ANSWER_KEY_EDITION,
                    "answerKeyScope": "verse" if row["kind"] == "verse" else "verse-containing-clause",
                    "targetWords": row.get("targetWords") or [],
                    "verification": checker.verify(text, set(known), pointed, skeleton, codes_known, curriculum_codes),
                    "reviewedBy": "corpus",
                }
            )
        for row in drafts:
            text = row.get("hebrew", "")
            items.append(
                {
                    "kind": "composed",
                    "text": text,
                    "targetWords": target_words_in(text, lesson_items, pointed, skeleton, codes),
                    "verification": checker.verify(text, set(known), pointed, skeleton, codes_known, curriculum_codes),
                    "reviewedBy": row.get("reviewedBy", "author"),
                }
            )
        for number, item in enumerate(items, start=1):
            item["no"] = number

        # Coverage is keyed on the vocabulary entry's own ordinal, not on its
        # Strong number: the conjunction ו and the prepositions ב כ ל are taught
        # words that have no Strong at all, and keying on Strong reported them
        # as never practised no matter how many sentences began with them.
        practised = {
            word.get("ordinal")
            for item in items
            for word in item["targetWords"]
        }
        not_practised = [
            entry.public_record()
            for entry in lesson_items
            if entry.ordinal not in practised
        ]
        lessons_out.append(
            {
                "lesson": lesson,
                "id": f"hbo-lesson-{lesson:02d}",
                "note": (
                    "本課無可用經典原句，十題全由自撰題補"
                    if len(quoted) < QUOTED_PER_LESSON
                    else ""
                ),
                "items": items,
                "coverage": {
                    "lessonWords": len(lesson_items),
                    "practised": len(lesson_items) - len(not_practised),
                    "notPractised": not_practised,
                },
            }
        )

    payload = {
        "schemaVersion": "1.0.0",
        "language": "Biblical Hebrew",
        "languageCode": "hbo",
        "generatedOn": date.today().isoformat(),
        "direction": "original-to-chinese",
        "itemsPerLesson": 10,
        "quotedPerLesson": QUOTED_PER_LESSON,
        "answerKeyEdition": ANSWER_KEY_EDITION,
        "lessons": lessons_out,
    }

    ready = sum(1 for row in lessons_out if len(row["items"]) == 10)
    print(f"組出 {len(lessons_out)} 課，其中 {ready} 課滿十題")
    if missing_drafts:
        print(f"尚無自撰稿的課：{missing_drafts}")
    if thin_anchors:
        print(f"湊不到三題定錨原句（已在該課 note 註明）：{thin_anchors}")
    if args.write:
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"寫入 {OUTPUT.relative_to(ROOT)}")
    return report(failures_for_payload(payload), label="exercise-set.json")


if __name__ == "__main__":
    sys.exit(main())
