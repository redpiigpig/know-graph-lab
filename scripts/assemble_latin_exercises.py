#!/usr/bin/env python3
"""Assemble the Latin reader's ten-item exercise set from its two sources.

The Latin counterpart of ``assemble_hebrew_exercises.py``, and the same shape:
three items per lesson are quoted from the corpus this volume draws on, mined
by ``build_latin_exercises.py``; seven are written by the author and live in
``composed-draft-v{volume}-{lesson}.json``.  This command joins them, re-runs
the corpus verification on every item rather than trusting what a draft claims
about itself, and emits the payload ``validate_reader_exercises.py`` gates.

No exercise carries a translation.  Printing the Chinese beside the sentence
would answer the question the exercise asks; what each item keeps instead is
the reference, so an answer booklet can be set later from 思高譯本.

Two volumes, two files, one schema.  The published payload is per volume
because the printed books are per volume, and because a volume-two lesson
three is not a volume-one lesson three -- the lesson number alone never
identifies a lesson in this reader.
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

from build_latin_lemma_corpus import (  # noqa: E402
    appendix_keys,
    ENCLITICS,
    cumulative_stems,
    cumulative_vocabulary,
    load_vocabulary,
    STEM_FLOOR,
    Tagger,
)
import compose_latin_sentences as checker  # noqa: E402
from validate_reader_exercises import failures_for_payload, report  # noqa: E402

CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
QUOTED_PER_LESSON = 3
ITEMS_PER_LESSON = 10
ANSWER_KEY_EDITION = "思高譯本"


def pick_anchors(anchors: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Take the three anchors a learner can best check an answer against.

    Whole verses first: an answer key can point at one without qualification.
    Then the clauses that practise most of the lesson's words, shortest first.

    There is deliberately no minimum word count here, unlike the Hebrew
    assembler.  That floor existed to throw out verbless scraps -- a three-word
    noun phrase has nothing in it to translate -- and ``build_latin_exercises``
    already refuses those at the source: a candidate with no verbal form among
    its lemmas never reaches this file.  Adding the floor anyway would leave
    twenty-six of the fifty upper-volume lessons short of three anchors and
    replace real Vulgate clauses with sentences of my own.
    """
    usable = sorted(
        anchors,
        key=lambda item: (
            0 if item.get("clause") is None else 1,
            -len(item.get("targetWords") or []),
            item.get("wordCount", 99),
        ),
    )
    return usable[:QUOTED_PER_LESSON]


def load_drafts(volume: int, lesson: int) -> tuple[list[dict[str, Any]], str]:
    path = CACHE / f"composed-draft-v{volume}-{lesson:02d}.json"
    if not path.exists():
        return [], ""
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("sentences", []), payload.get("author", "")


def target_words_in(
    text: str, targets: Sequence[Any], corpus: checker.Corpus, tagger: Tagger
) -> list[dict[str, Any]]:
    """Which of the lesson's twenty words a sentence actually practises.

    Delegated to the gate's own ``practised``, so the book and the gate can
    never disagree about what a sentence covers -- including the rule that a
    lemma only credits its headword when it folds to it, which is what keeps
    ``mīsit`` from practising 彌撒.
    """
    hits = checker.practised([text], targets, corpus, tagger)
    return [entry.public_record() for entry in targets if entry.ordinal in hits]


def unreachable_words(
    entries: Sequence[Any], corpus: checker.Corpus, tagger: Tagger, appendix: set[str]
) -> set[int]:
    """Ordinals of words no sentence could ever practise.

    Gate one refuses a form the corpus never wrote, gate two refuses a word the
    lessons never taught, and gate three demands all twenty of a lesson's words.
    For some words the three cannot all hold, and the lesson is unsatisfiable
    rather than merely hard.  Two shapes of it:

    * the word has no attested form at all -- ``Kyrie``, ``eléison``, ``tellus``,
      the month names.  This reader's vocabulary comes from Collins and its
      attestation from the Vulgate, which is not the book Collins teaches from;
    * every form that would credit it is a different word the lessons never
      taught -- ``speciō`` survives in the Vulgate only as the adjective
      ``speciōsus``, so the one spelling that could credit it is refused by the
      gate before it can.

    So reachability is decided by running the real gates rather than by a rule
    of its own: a word is reachable when some corpus form both credits it and
    would pass the taught-words gate.  Deciding it any other way leaves a lesson
    holding a word it can neither practise nor excuse.
    """
    keys = corpus.keys
    taught_lemmas = {lemma for entry in entries for lemma in entry.lemmas}
    taught_keys = {key for entry in entries for key in entry.written_keys} | appendix
    taught_stems = {stem for entry in entries for stem in entry.credit_stems}

    by_lemma: dict[str, set[str]] = {}
    lemmaless_by_prefix: dict[str, set[str]] = {}
    for key, row in corpus.forms.items():
        for lemma in row["lemmas"]:
            by_lemma.setdefault(lemma, set()).add(key)
        if not row["lemmas"]:
            for length in range(STEM_FLOOR, len(key) + 1):
                lemmaless_by_prefix.setdefault(key[:length], set()).add(key)

    def writable(key: str) -> bool:
        part = {"key": key, "lemmas": corpus.lemmas(key) | tagger.lemmas_for_key(key)}
        return checker.part_is_taught(part, taught_lemmas, taught_keys, taught_stems)

    out: set[int] = set()
    for entry in entries:
        if getattr(entry, "phrase", False):
            if not (entry.credit_keys <= keys and all(writable(k) for k in entry.credit_keys)):
                out.add(entry.ordinal)
            continue
        candidates: set[str] = set()
        for lemma in entry.credit_lemmas:
            candidates |= by_lemma.get(lemma, set())
        candidates |= entry.written_keys & keys
        # An enclitic is never a corpus form on its own -- ``-que`` is only ever
        # the tail of another word -- but the gate does split it off and credit
        # it, so it is reachable and must not be filed as absent.
        candidates |= entry.written_keys & set(ENCLITICS)
        for stem in entry.credit_stems:
            candidates |= lemmaless_by_prefix.get(stem, set())
        if not any(key in ENCLITICS or writable(key) for key in candidates):
            out.add(entry.ordinal)
    return out


def build_volume(volume: int) -> dict[str, Any]:
    mined_path = CACHE / f"exercises-v{volume}.json"
    if not mined_path.exists():
        raise SystemExit(f"缺 {mined_path.name}，先跑 scripts/build_latin_exercises.py --volume {volume}")
    mined = json.loads(mined_path.read_text(encoding="utf-8"))
    mined_by_lesson = {row["lesson"]: row for row in mined.get("lessons", [])}

    tagger = Tagger(gold=("proiel",) if volume == 1 else ("proiel", "ittb", "llct"))
    entries = load_vocabulary(tagger=tagger)
    corpus = checker.Corpus(checker.corpora_for(volume))
    appendix = appendix_keys(volume=volume)
    appendix_all: set[str] = set()
    for keys in appendix.values():
        appendix_all |= keys

    unreachable_ordinals = unreachable_words(
        [entry for entry in entries if entry.volume <= volume], corpus, tagger, appendix_all
    )
    lessons_out: list[dict[str, Any]] = []
    thin: list[int] = []
    missing: list[int] = []
    for lesson in sorted(mined_by_lesson):
        targets, taught_lemmas, taught_keys = cumulative_vocabulary(entries, volume, lesson)
        taught_keys = taught_keys | appendix_all
        taught_stems = cumulative_stems(entries, volume, lesson)
        anchors = pick_anchors(mined_by_lesson[lesson].get("anchors", []))
        if len(anchors) < QUOTED_PER_LESSON:
            thin.append(lesson)
        drafts, author = load_drafts(volume, lesson)
        if not drafts:
            missing.append(lesson)

        items: list[dict[str, Any]] = []
        for row in anchors:
            text = row["text"]
            items.append({
                "kind": "quoted",
                "ref": row["ref"],
                "text": text,
                "answerKeyRef": row.get("answerKeyRef") or row["ref"],
                "answerKeyEdition": ANSWER_KEY_EDITION,
                "answerKeyScope": row.get("answerKeyScope") or "verse",
                "targetWords": row.get("targetWords") or [],
                "verification": checker.verify(
                    text, corpus, tagger, taught_lemmas, taught_keys, taught_stems
                ),
                "reviewedBy": "corpus",
            })
        for row in drafts:
            text = row.get("latin", "")
            items.append({
                "kind": "composed",
                "text": text,
                "targetWords": target_words_in(text, targets, corpus, tagger),
                "verification": checker.verify(
                    text, corpus, tagger, taught_lemmas, taught_keys, taught_stems
                ),
                "reviewedBy": row.get("reviewedBy", "author" if author else "draft"),
            })
        for number, item in enumerate(items, start=1):
            item["no"] = number

        practised_ordinals = {
            word.get("ordinal") for item in items for word in item["targetWords"]
        }
        unreachable = [entry for entry in targets if entry.ordinal in unreachable_ordinals]
        not_practised = [
            entry.public_record()
            for entry in targets
            if entry.ordinal not in practised_ordinals
            and entry.ordinal not in unreachable_ordinals
        ]
        notes = []
        if len(anchors) < QUOTED_PER_LESSON:
            notes.append("本課無可用經典原句，十題全由自撰題補")
        if unreachable:
            notes.append(
                "本冊語料中無任何字形，因而無法入題："
                + "、".join(entry.headword for entry in unreachable)
            )
        lessons_out.append({
            "lesson": lesson,
            "id": f"lat-v{volume}-lesson-{lesson:02d}",
            "note": "；".join(notes),
            "items": items,
            "coverage": {
                "lessonWords": len(targets),
                "practised": len(targets) - len(not_practised) - len(unreachable),
                "notPractised": not_practised,
                "notAttested": [entry.public_record() for entry in unreachable],
            },
        })

    payload = {
        "schemaVersion": "1.0.0",
        "language": "Ecclesiastical Latin",
        "languageCode": "lat",
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
            output.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"  寫入 {output.relative_to(ROOT)}")
        worst |= report(failures_for_payload(payload), label=output.name)
    return worst


if __name__ == "__main__":
    sys.exit(main())
