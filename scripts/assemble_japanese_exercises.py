#!/usr/bin/env python3
"""Assemble the Japanese reader's ten-item exercise set from its two sources.

The Japanese counterpart of ``assemble_hebrew_exercises.py``,
``assemble_latin_exercises.py`` and ``assemble_greek_exercises.py``, and the
same shape: three items per lesson are quoted from the corpora this reader
draws on, mined by ``build_japanese_exercises.py``; seven are written by the
author and live in ``composed-draft-NN.json``.  This command joins them,
re-runs the corpus verification on every item rather than trusting what a draft
or a mined file claims about itself, and emits the payload
``validate_reader_exercises.py`` gates.

Three things the mined file carries that must not reach the published set:

* ``chinese``/``chineseSource``.  They are empty, but the shared gate refuses an
  exercise that prints a translation and the field is the thing that invites
  one.  The reference travels instead, so an answer booklet can be set later.
* ``targetWords`` computed when the file was mined, and without an ordinal.
  Coverage recomputed from a stale list disagrees with the gate that later reads
  it — the Latin set had a word one side thought was practised and the other did
  not — and the printed book binds a block to a lesson by ordinal, so the
  ordinal has to be there.
* ``reviewedBy: ""``.  An empty field reads as "not reviewed" and as "nobody
  filled this in"; the set says which of the two it is.

One lesson numbering, 1–100.  The reader is two volumes of fifty, but the
vocabulary, the corpus gate and the mined file all count straight through, and
converting between the two in three places is how a block ends up under the
wrong lesson.  The volume is recorded, never computed from.
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

from build_japanese_lemma_corpus import (  # noqa: E402
    OUTPUT as CORPUS_PATH,
    Segmenter,
    load_corpus,
    load_vocabulary,
)
import compose_japanese_sentences as checker  # noqa: E402
from validate_reader_exercises import failures_for_payload, report  # noqa: E402

CACHE = ROOT / "output" / "source-cache" / "original-readers" / "japanese-full"
MINED = CACHE / "exercises.json"
QUOTED_PER_LESSON = 3
ITEMS_PER_LESSON = 10
LESSONS_PER_VOLUME = 50
ANSWER_KEY_EDITION = "無既有中譯，解答本需自譯"


def pick_anchors(
    items: Sequence[dict[str, Any]], keep=None
) -> list[dict[str, Any]]:
    """Take the three anchors a learner can best check an answer against.

    The miner already refuses a fragment, so what is left to choose on is how
    much of the lesson each one practises, and then brevity: a learner
    translating a first sentence wants the short one.

    ``keep`` re-runs the gate on each candidate before it is chosen.  The mined
    file was written under the gate of the day and nine of its three hundred
    anchors no longer pass it — 「それはこの本でございます」 uses でございます,
    which the reader does not teach.  Each of those lessons has other mined
    candidates, so the fix is to pass over the ones that fail rather than print
    a sentence the book has not equipped anyone to read.
    """
    usable = sorted(
        (item for item in items if item.get("kind") == "quoted"),
        key=lambda item: (
            -len(item.get("targetWords") or []),
            len(item.get("text") or ""),
        ),
    )
    if keep is not None:
        usable = [item for item in usable if keep(item)]
    return usable[:QUOTED_PER_LESSON]


def load_drafts(lesson: int) -> tuple[list[dict[str, Any]], str]:
    path = CACHE / f"composed-draft-{lesson:03d}.json"
    if not path.exists():
        return [], ""
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("sentences", []), payload.get("author", "")


def creditable(entry: dict[str, Any], check) -> bool:
    """Could any sentence of this lesson ever credit this word?

    Japanese has no word the corpus cannot write — its first gate checks the
    base form and treats the textbook as authoritative where the corpus is
    merely old-fashioned (朝ご飯 against 朝飯).  What it does have is a word the
    *segmenter* will never hand back under its own identity: 人 is two entries
    in lesson one, ひと the noun and じん the suffix, and every spelling of the
    second is read as the first unless a country name precedes it — and lesson
    one teaches no country name.  The word is then unpractisable in that lesson
    however the sentence is written, exactly the way ``πτελέα`` is in Greek, and
    belongs in ``notAttested`` with a note rather than in a coverage gap that
    can never be closed.

    Deciding that by running the real gate rather than by a rule about parts of
    speech: the question is whether *the checker* will credit the word, and only
    the checker answers that.  It is asked twice, in two frames that use nothing
    past lesson one, and a word counts as reachable only if **both** credit it.
    One frame is not enough, because a lone frame turns a particle into a noun
    by accident and each does it to a different particle: ``からです`` puts から at
    the head of an utterance and the segmenter reads it as a noun, ``私のまでです``
    does the same to まで, and 「学校から美術館まで」 — the sentence a learner would
    actually meet — counts both as grammar and credits neither.  Trusting either
    frame alone leaves that lesson holding a coverage gap that cannot be closed.

    The length rule is ignored here: the frames are probes, not exercises.
    """
    for frame in (f"私の{checker.headword(entry)}です。", f"私は{checker.headword(entry)}です。"):
        report = check(frame)
        if report["untaught"] or report["unattested"]:
            return False
        if checker.entry_key(entry) not in report["vocabulary"]:
            return False
    return True


def public_record(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "ordinal": entry["ordinal"],
        "headword": checker.headword(entry),
        "kana": (entry.get("kana") or "").strip(),
        "glossZh": entry.get("glossZh", ""),
        "pos": entry.get("pos", ""),
    }


def build(write: bool, only: range | None = None) -> int:
    if not MINED.is_file():
        raise SystemExit(f"缺 {MINED.name}，先跑 scripts/build_japanese_exercises.py")
    mined = json.loads(MINED.read_text(encoding="utf-8"))
    mined_by_lesson = {row["lesson"]: row for row in mined.get("lessons", [])}

    corpus = load_corpus(CORPUS_PATH)
    vocabulary = load_vocabulary()
    segmenter = Segmenter()
    if segmenter.name != corpus["tokenizer"]["name"]:
        raise SystemExit(
            f"語料是用 {corpus['tokenizer']['name']} 斷的，現在跑的是 {segmenter.name}；"
            "基本形對不上會整批誤判，先重建語料"
        )
    grammar = checker.taught_grammar()
    lemmas = corpus["lemmas"]

    lessons_out: list[dict[str, Any]] = []
    thin: list[int] = []
    missing: list[int] = []
    for lesson in sorted(mined_by_lesson):
        if only is not None and lesson not in only:
            continue
        targets = checker.lesson_targets(vocabulary, lesson)
        by_key = {checker.entry_key(entry): entry for entry in targets}
        checked: dict[str, dict[str, Any]] = {}

        def check(text: str) -> dict[str, Any]:
            if text not in checked:
                checked[text] = checker.verify(
                    text, segmenter=segmenter, vocabulary=vocabulary,
                    lemmas=lemmas, lesson=lesson, grammar=grammar,
                )
            return checked[text]

        anchors = pick_anchors(
            mined_by_lesson[lesson].get("items", []),
            keep=lambda row: check(row["text"])["passed"],
        )
        if len(anchors) < QUOTED_PER_LESSON:
            thin.append(lesson)
        drafts, author = load_drafts(lesson)
        if not drafts:
            missing.append(lesson)

        def practised_in(verification: dict[str, Any]) -> list[dict[str, Any]]:
            """Which of the lesson's twenty words a sentence practises.

            Read off the gate's own report, so the book and the gate can never
            disagree about what a sentence covers.
            """
            seen = dict.fromkeys(verification["vocabulary"])
            return [public_record(by_key[key]) for key in seen if key in by_key]

        items: list[dict[str, Any]] = []
        for row in anchors:
            verification = check(row["text"])
            items.append({
                "kind": "quoted",
                "ref": row["ref"],
                "text": row["text"],
                "answerKeyRef": row["ref"],
                "answerKeyEdition": ANSWER_KEY_EDITION,
                "answerKeyScope": "sentence",
                "targetWords": practised_in(verification),
                "verification": verification,
                "reviewedBy": "corpus",
            })
        for row in drafts:
            verification = check(row["japanese"])
            items.append({
                "kind": "composed",
                "text": row["japanese"],
                "targetWords": practised_in(verification),
                "verification": verification,
                "reviewedBy": row.get("reviewedBy", "author" if author else "draft"),
            })
        for number, item in enumerate(items, start=1):
            item["no"] = number

        practised = {word["ordinal"] for item in items for word in item["targetWords"]}
        unreachable = [
            entry for entry in targets
            if entry["ordinal"] not in practised and not creditable(entry, check)
        ]
        unreachable_ordinals = {entry["ordinal"] for entry in unreachable}
        not_practised = [
            public_record(entry) for entry in targets
            if entry["ordinal"] not in practised
            and entry["ordinal"] not in unreachable_ordinals
        ]
        notes = []
        if len(anchors) < QUOTED_PER_LESSON:
            notes.append("本課無可用經典原句，十題全由自撰題補")
        if unreachable:
            notes.append(
                "本課教過的詞寫不出能記到它的句子，因而無法入題："
                + "、".join(checker.headword(entry) for entry in unreachable)
            )
        lessons_out.append({
            "lesson": lesson,
            "volume": (lesson - 1) // LESSONS_PER_VOLUME + 1,
            "id": f"ja-lesson-{lesson:03d}",
            "note": "；".join(notes),
            "items": items,
            "coverage": {
                "lessonWords": len(targets),
                "practised": len(targets) - len(not_practised) - len(unreachable),
                "notPractised": not_practised,
                "notAttested": [public_record(entry) for entry in unreachable],
            },
        })

    payload = {
        "schemaVersion": "1.0.0",
        "language": "Japanese",
        "languageCode": "ja",
        "generatedOn": date.today().isoformat(),
        "direction": "original-to-chinese",
        "itemsPerLesson": ITEMS_PER_LESSON,
        "quotedPerLesson": QUOTED_PER_LESSON,
        "answerKeyEdition": ANSWER_KEY_EDITION,
        "tokenizer": corpus["tokenizer"],
        "lessons": lessons_out,
    }
    ready = sum(1 for row in lessons_out if len(row["items"]) == ITEMS_PER_LESSON)
    print(f"組出 {len(lessons_out)} 課，其中 {ready} 課滿十題")
    if missing:
        print(f"  尚無自撰稿：{len(missing)} 課 {missing[:12]}{'…' if len(missing) > 12 else ''}")
    if thin:
        print(f"  定錨不足三題（已於 note 說明）：{thin}")

    output = CACHE / "exercise-set.json"
    if write:
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  寫入 {output.relative_to(ROOT)}")
    return report(failures_for_payload(payload), label=output.name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    # 寫稿時只組幾課來看覆蓋率：整本要讀一遍一千四百萬詞的語料，一輪十分鐘，
    # 而改一句話只需要知道那一課的聯集。--only 產的檔不可寫出去。
    parser.add_argument("--only", type=int, nargs=2, metavar=("FIRST", "LAST"))
    args = parser.parse_args()
    if args.only and args.write:
        raise SystemExit("--only 是寫稿時看覆蓋率用的，不可與 --write 併用")
    only = range(args.only[0], args.only[1] + 1) if args.only else None
    return build(args.write, only)


if __name__ == "__main__":
    sys.exit(main())
