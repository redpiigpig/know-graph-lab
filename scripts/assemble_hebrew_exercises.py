#!/usr/bin/env python3
"""Assemble the Hebrew reader's ten-item exercise set from its two sources.

Three items per lesson are quoted Scripture, mined by `build_hebrew_exercises.py`
and answered from 和合本修訂版（2010）.  Seven are written by the author and
live in `composed-draft-NN.json`.  This command joins them, re-runs the corpus
verification on every item rather than trusting what a draft claims about
itself, and emits the payload that `validate_reader_exercises.py` gates.

A quoted item is only usable when its Chinese is on hand: the RCUV snapshot
covers the chapters the reader prints, not the whole Bible, so an anchor whose
verse has no cached translation is passed over rather than shipped with an
empty answer.  Lessons that cannot field three such anchors are reported, not
silently filled.
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
    load_chinese_translation,
    load_vocabulary,
    load_wlc,
)
from build_hebrew_exercises import cumulative_sets  # noqa: E402
import compose_hebrew_sentences as checker  # noqa: E402
from validate_reader_exercises import failures_for_payload, report  # noqa: E402

CACHE = ROOT / "output/source-cache/original-readers/hebrew-full"
MINED = CACHE / "exercises.json"
RCUV = CACHE / "RCUV2010.json"
OUTPUT = CACHE / "exercise-set.json"
QUOTED_PER_LESSON = 3
CHINESE_EDITION = "和合本修訂版（2010）"


def chinese_by_ref() -> dict[str, str]:
    """Every RCUV verse on hand, keyed by the Hebrew Bible's own reference.

    Two snapshots feed this: the one the reader already printed, and the one
    fetched for the chapters the exercises quote.  The mapping is the existing
    `load_chinese_translation`, not a flat read of the file, because RCUV and
    the Masoretic text number the Psalms differently -- the superscription is
    a verse on one side and not on the other -- and that crosswalk has already
    been worked out once.
    """
    translations: dict[str, str] = {}
    for path in (RCUV, CACHE / "RCUV2010-exercises.json"):
        if path.exists():
            translations.update(load_chinese_translation(path))
    return translations


MIN_CLAUSE_WORDS_FOR_ANCHOR = 4


def pick_quoted(items: list[dict[str, Any]], translations: dict[str, str]) -> list[dict[str, Any]]:
    """Take the anchors a learner can actually check an answer against.

    Whole verses come first, because the published Chinese answers exactly the
    words printed.  A clause is answered by the Chinese of the verse around it,
    which only helps when the clause is a recognisable piece of that verse: a
    three-word scrap such as בֵּית אֲחֵי אֲדֹנִי set beside the whole of Gen 24:27
    teaches nothing and reads as a mistake.  Short scraps are therefore refused
    even though they verify perfectly -- the anchor exists to be compared, and
    an anchor nobody can compare has lost its reason to be on the page.
    """
    usable = [
        item
        for item in items
        if item.get("kind") in {"verse", "clause"}
        and translations.get(item.get("ref", ""))
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
        strongs |= pointed.get(key) or skeleton.get(checker.consonants(piece)) or set()
        present_codes |= (codes or {}).get(key, set())
    return [
        item.public_record()
        for item in lesson_items
        if (set(item.strongs) & strongs) or (item.bound_codes & present_codes)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    translations = chinese_by_ref()
    mined = json.loads(MINED.read_text(encoding="utf-8"))
    mined_by_lesson = {row["lesson"]: row for row in mined.get("lessons", [])}
    vocabulary = load_vocabulary(DEFAULT_VOCAB)
    verses = load_wlc(DEFAULT_WLC)
    pointed, skeleton = checker.build_attested(verses)
    codes = bound_codes_by_form(verses)

    lessons_out: list[dict[str, Any]] = []
    thin_anchors: list[int] = []
    missing_drafts: list[int] = []

    for lesson, lesson_items, known in cumulative_sets(vocabulary):
        quoted = pick_quoted((mined_by_lesson.get(lesson) or {}).get("items", []), translations)
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
                    "chinese": translations[row["ref"]],
                    "chineseSource": CHINESE_EDITION,
                    "chineseScope": "verse" if row["kind"] == "verse" else "verse-containing-clause",
                    "targetWords": row.get("targetWords") or [],
                    "verification": checker.verify(text, set(known), pointed, skeleton),
                    "reviewedBy": "corpus",
                }
            )
        for row in drafts:
            text = row.get("hebrew", "")
            items.append(
                {
                    "kind": "composed",
                    "text": text,
                    "chinese": row.get("chinese", ""),
                    "chineseSource": "",
                    "targetWords": target_words_in(text, lesson_items, pointed, skeleton, codes),
                    "verification": checker.verify(text, set(known), pointed, skeleton),
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
        "chineseEdition": CHINESE_EDITION,
        "lessons": lessons_out,
    }

    ready = sum(1 for row in lessons_out if len(row["items"]) == 10)
    print(f"組出 {len(lessons_out)} 課，其中 {ready} 課滿十題")
    if missing_drafts:
        print(f"尚無自撰稿的課：{missing_drafts}")
    if thin_anchors:
        print(f"湊不到三題有中譯的原句：{thin_anchors}")
    if args.write:
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"寫入 {OUTPUT.relative_to(ROOT)}")
    return report(failures_for_payload(payload), label="exercise-set.json")


if __name__ == "__main__":
    sys.exit(main())
