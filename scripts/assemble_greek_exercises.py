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

from build_greek_lemma_corpus import CACHE, bare, fold_key  # noqa: E402
from build_greek_exercises import (  # noqa: E402
    VOLUME_CORPORA,
    cumulative_sets,
    load_units,
    load_vocabulary,
)
import compose_greek_sentences as checker  # noqa: E402
from greek_reference_labels import anchor_label  # noqa: E402
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


def target_words_in(text: str, items, known, attestation, taught_forms) -> list[dict[str, Any]]:
    """Which of the lesson's twenty words a sentence actually practises.

    Delegated to the gate's own lookup, so the book and the gate can never
    disagree about what a sentence covers.
    """
    report = checker.verify_sentence(text, known, attestation, taught_forms)
    seen = set(report["lemmas"])
    seen_forms = set(report.get("forms") or ())
    written = set(report.get("written") or ())
    return [
        item.public_record()
        for item in items
        if (item.keys & seen)
        or (item.written_keys & seen_forms)
        or (item.written_keys & written)
        or (len(item.written_keys) > 1 and item.written_keys <= written)
    ]


def unreachable_words(items, known, attestation, taught_forms) -> set[int]:
    """Ordinals of words no sentence could ever practise.

    Gate one refuses a form the corpus never wrote, gate two refuses a word the
    lessons never taught, and gate three demands all twenty of a lesson's words.
    For a word with no writable form the three contradict, and the lesson is
    unsatisfiable rather than merely hard: ``πτελέα`` (the elm) is in the
    vocabulary and in neither corpus this volume checks against.

    Reachability is decided by running the real gates -- a word is reachable
    when some attested spelling both credits it and passes the taught-words
    gate.  Deciding it any other way leaves a lesson holding a word it can
    neither practise nor excuse; the Latin set had exactly that.
    """
    out: set[int] = set()
    for item in items:
        reachable = False
        for printed, keys in attestation.exact.items():
            if not ((keys & item.keys) or (fold_key(bare(printed)) in item.written_keys)):
                continue
            report = checker.verify_sentence(printed, known, attestation, taught_forms)
            # 只問語料寫不寫得出來。「已教過」自 2026-09-16 起不再是退回的理由，
            # 也就不再是「練不到」的理由。
            if not report["unattested"]:
                reachable = True
                break
        if not reachable:
            out.add(item.ordinal)
    return out


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
        taught_forms = checker.taught_forms_through(vocabulary, volume, lesson)
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
                # 書上與網頁印的是這一行，不是 patristic-plan:21:2.2#3。組題時
                # 就翻好，兩邊才不會各自維護一份書卷對照表。
                "refLabel": anchor_label(row["ref"]),
                "text": text,
                "answerKeyRef": row["ref"],
                "answerKeyEdition": ANSWER_KEY_EDITION,
                "answerKeyScope": "verse-containing-clause" if row.get("clause") else "verse",
                "targetWords": target_words_in(text, items, known, attestation, taught_forms),
                "verification": checker.verify_sentence(text, known, attestation, taught_forms),
                "reviewedBy": "corpus",
            })
        for row in drafts:
            text = row.get("greek", "")
            rows.append({
                "kind": "composed",
                "text": text,
                "targetWords": target_words_in(text, items, known, attestation, taught_forms),
                "verification": checker.verify_sentence(text, known, attestation, taught_forms),
                "reviewedBy": row.get("reviewedBy", "author" if author else "draft"),
            })
        for number, item in enumerate(rows, start=1):
            item["no"] = number

        practised = {word["ordinal"] for item in rows for word in item["targetWords"]}
        unreachable_ordinals = unreachable_words(items, known, attestation, taught_forms)
        unreachable = [item for item in items if item.ordinal in unreachable_ordinals]
        not_practised = [
            item.public_record()
            for item in items
            if item.ordinal not in practised and item.ordinal not in unreachable_ordinals
        ]
        notes = []
        if len(anchors) < QUOTED_PER_LESSON:
            notes.append("本課無可用經典原句，十題全由自撰題補")
        if unreachable:
            notes.append(
                "本讀本語料中無可用字形，因而無法入題："
                + "、".join(item.headword for item in unreachable)
            )
        lessons_out.append({
            "lesson": lesson,
            "id": f"grc-v{volume}-lesson-{lesson:02d}",
            "note": "；".join(notes),
            "items": rows,
            "coverage": {
                "lessonWords": len(items),
                "practised": len(items) - len(not_practised) - len(unreachable),
                "notPractised": not_practised,
                "notAttested": [item.public_record() for item in unreachable],
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
