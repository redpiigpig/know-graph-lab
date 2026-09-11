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


def pick_quoted(items: list[dict[str, Any]], translations: dict[str, str]) -> list[dict[str, Any]]:
    """Take the anchors that have a published Chinese answer, widest coverage first."""
    usable = [
        item
        for item in items
        if item.get("kind") in {"verse", "clause"} and translations.get(item.get("ref", ""))
    ]
    usable.sort(key=lambda item: (-len(item.get("targetWords") or []), item.get("tokenCount", 99)))
    return usable[:QUOTED_PER_LESSON]


def load_drafts(lesson: int) -> list[dict[str, Any]]:
    path = CACHE / f"composed-draft-{lesson:02d}.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8")).get("sentences", [])


def target_words_in(text: str, lesson_items) -> list[dict[str, Any]]:
    """Which of the lesson's twenty words a sentence actually contains."""
    pieces = {checker.consonants(piece) for piece in checker.split_words(text)}
    found = []
    for item in lesson_items:
        skeleton = checker.consonants(item.pointed)
        if any(skeleton and (skeleton == piece or skeleton in piece) for piece in pieces):
            found.append(item.public_record())
    return found


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
                    "targetWords": target_words_in(text, lesson_items),
                    "verification": checker.verify(text, set(known), pointed, skeleton),
                    "reviewedBy": row.get("reviewedBy", "author"),
                }
            )
        for number, item in enumerate(items, start=1):
            item["no"] = number

        practised = {
            word.get("pointed")
            for item in items
            for word in item["targetWords"]
        }
        not_practised = [
            entry.public_record() for entry in lesson_items if entry.pointed not in practised
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
