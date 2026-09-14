#!/usr/bin/env python3
"""Assemble the Koine reader's ten-item exercise set from its two sources.

The Greek counterpart of ``assemble_hebrew_exercises.py`` and
``assemble_latin_exercises.py``, and the same shape: three items per lesson are
quoted from the corpora this volume draws on, mined by
``build_greek_exercises.py``; seven are written by the author and live in
``composed-draft-v{volume}-{lesson}.json``.  This command joins them, re-runs
the corpus verification on every item rather than trusting what a draft or a
mined file claims about itself, and emits the payload
``validate_reader_exercises.py`` gates.

Two things the mined file carries that must not reach the published set:

* ``chinese``/``chineseSource``.  They are empty, but the shared gate refuses an
  exercise that prints a translation and the field is the thing that invites
  one.  The reference travels instead, so an answer booklet can be set later.
* ``targetWords`` computed when the file was mined.  Coverage recomputed from a
  stale list disagrees with the gate that later reads it -- the Latin set had a
  word that one side thought was practised and the other did not.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_greek_lemma_corpus import CACHE  # noqa: E402
from build_greek_exercises import (  # noqa: E402
    VOLUME_CORPORA,
    cumulative_sets,
    load_units,
    load_vocabulary,
)
import compose_greek_sentences as checker  # noqa: E402
from validate_reader_exercises import failures_for_payload, report  # noqa: E402

QUOTED_PER_LESSON = 3
ITEMS_PER_LESSON = 10
ANSWER_KEY_EDITION = "和合本修訂版（2010）／教父文獻另計"


def pick_anchors(items: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Take the three anchors a learner can best check an answer against.

    The miner already refuses a candidate with too few content words or one that
    does not stop on a pause the original prints, so what is left to choose on is
    how much of the lesson each one practises, and then brevity: a learner
    translating a first sentence wants the short one.
    """
    usable = sorted(
        items,
        key=lambda item: (-len(item.get("targetWords") or []), item.get("tokenCount", 99)),
    )
    return usable[:QUOTED_PER_LESSON]


def load_drafts(volume: int, lesson: int) -> tuple[list[dict[str, Any]], str]:
    path = CACHE / f"composed-draft-v{volume}-{lesson:02d}.json"
    if not path.exists():
        return [], ""
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("sentences", []), payload.get("author", "")


def target_words_in(text: str, items, known, attestation) -> list[dict[str, Any]]:
    """Which of the lesson's twenty words a sentence actually practises.

    Delegated to the gate's own lookup, so the book and the gate can never
    disagree about what a sentence covers.
    """
    report = checker.verify_sentence(text, known, attestation)
    seen = set(report["lemmas"])
    return [item.public_record() for item in items if item.keys & seen]


def build_volume(volume: int) -> dict[str, Any]:
    mined_path = CACHE / f"exercises-greek-vol{volume}.json"
    if not mined_path.exists():
        raise SystemExit(
            f"缺 {mined_path.name}，先跑 scripts/build_greek_exercises.py --volume {volume}"
        )
    mined = json.loads(mined_path.read_text(encoding="utf-8"))
    mined_by_lesson = {row["lesson"]: row for row in mined.get("lessons", [])}

    vocabulary = load_vocabulary()
    units = load_units(VOLUME_CORPORA[volume])
    attestation = checker.Attestation.from_units(units)

    lessons_out: list[dict[str, Any]] = []
    thin: list[int] = []
    missing: list[int] = []
    for lesson, items, known in cumulative_sets(vocabulary, volume):
        anchors = pick_anchors((mined_by_lesson.get(lesson) or {}).get("items", []))
        if len(anchors) < QUOTED_PER_LESSON:
            thin.append(lesson)
        drafts, author = load_drafts(volume, lesson)
        if not drafts:
            missing.append(lesson)

        rows: list[dict[str, Any]] = []
        for row in anchors:
            text = row["text"]
            rows.append({
                "kind": "quoted",
                "ref": row["ref"],
                "text": text,
                "answerKeyRef": row["ref"],
                "answerKeyEdition": ANSWER_KEY_EDITION,
                "answerKeyScope": "verse-containing-clause" if row.get("clause") else "verse",
                "targetWords": target_words_in(text, items, known, attestation),
                "verification": checker.verify_sentence(text, known, attestation),
                "reviewedBy": "corpus",
            })
        for row in drafts:
            text = row.get("greek", "")
            rows.append({
                "kind": "composed",
                "text": text,
                "targetWords": target_words_in(text, items, known, attestation),
                "verification": checker.verify_sentence(text, known, attestation),
                "reviewedBy": row.get("reviewedBy", "author" if author else "draft"),
            })
        for number, item in enumerate(rows, start=1):
            item["no"] = number

        practised = {word["ordinal"] for item in rows for word in item["targetWords"]}
        not_practised = [item.public_record() for item in items if item.ordinal not in practised]
        notes = []
        if len(anchors) < QUOTED_PER_LESSON:
            notes.append("本課無可用經典原句，十題全由自撰題補")
        lessons_out.append({
            "lesson": lesson,
            "id": f"grc-v{volume}-lesson-{lesson:02d}",
            "note": "；".join(notes),
            "items": rows,
            "coverage": {
                "lessonWords": len(items),
                "practised": len(items) - len(not_practised),
                "notPractised": not_practised,
            },
        })

    payload = {
        "schemaVersion": "1.0.0",
        "language": "Koine Greek",
        "languageCode": "grc",
        "volume": volume,
        "generatedOn": date.today().isoformat(),
        "direction": "original-to-chinese",
        "itemsPerLesson": ITEMS_PER_LESSON,
        "quotedPerLesson": QUOTED_PER_LESSON,
        "answerKeyEdition": ANSWER_KEY_EDITION,
        "lessons": lessons_out,
    }
    ready = sum(1 for row in lessons_out if len(row["items"]) == ITEMS_PER_LESSON)
    print(f"第 {volume} 冊：組出 {len(lessons_out)} 課，其中 {ready} 課滿十題")
    if missing:
        print(f"  尚無自撰稿：{missing}")
    if thin:
        print(f"  定錨不足三題（已於 note 說明）：{thin}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--volume", type=int, choices=[1, 2], action="append")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    worst = 0
    for volume in args.volume or [1, 2]:
        payload = build_volume(volume)
        output = CACHE / f"exercise-set-v{volume}.json"
        if args.write:
            output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"  寫入 {output.relative_to(ROOT)}")
        worst |= report(failures_for_payload(payload), label=output.name)
    return worst


if __name__ == "__main__":
    sys.exit(main())
