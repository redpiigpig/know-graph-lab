#!/usr/bin/env python3
"""Everything needed to write one Japanese lesson's exercises, on one screen.

The Japanese counterpart of ``hebrew_lesson_brief.py``, ``latin_lesson_brief.py``
and ``greek_lesson_brief.py``, and it exists for the same reason: writing a
sentence for this reader means knowing which of the lesson's twenty words the
three quoted anchors leave unpractised, and what each of those words actually
is — its kanji, its reading, its part of speech.  Looking those up separately is
how a draft gets written around a word the anchors already covered while another
never appears at all.

Japanese needs less from the brief than the other three do, and for a reason
worth writing down: its first gate checks the **base form**, not the written
form (see ``compose_japanese_sentences.py``).  Inflection is regular, so
読む→読みます→読んで is derivable and there is no list of "forms the corpus
actually writes" to consult — the trap the Latin and Greek briefs exist to
avoid does not arise here.  What can still bite is the closed-class rule: a
one-kana particle is never looked up in the word list (は is not 齒), so a
sentence may only use particles the reader itself teaches.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_japanese_lemma_corpus import (  # noqa: E402
    OUTPUT as CORPUS_PATH,
    Segmenter,
    load_corpus,
    load_vocabulary,
)
import compose_japanese_sentences as checker  # noqa: E402

CACHE = ROOT / "output" / "source-cache" / "original-readers" / "japanese-full"
EXERCISES = CACHE / "exercises.json"
ITEMS_PER_LESSON = 10
ANCHORS_PER_LESSON = 3


def anchors_for(lesson: int, keep=None) -> list[dict[str, Any]]:
    """The anchors this lesson will print, chosen the way the assembler does.

    Including the gate the assembler re-runs on each candidate: nine of the
    three hundred mined anchors no longer pass it, and briefing a lesson around
    an anchor that will be dropped leaves that lesson's words unwritten.
    """
    if not EXERCISES.is_file():
        return []
    payload = json.loads(EXERCISES.read_text(encoding="utf-8"))
    for row in payload.get("lessons", []):
        if row["lesson"] == lesson:
            from assemble_japanese_exercises import pick_anchors  # noqa: PLC0415

            return pick_anchors(row.get("items", []), keep=keep)
    return []


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lesson", type=int, help="課次；不給 --volume 時是 1–100 通編")
    parser.add_argument("--through", type=int, help="一次印到第幾課為止（含）")
    parser.add_argument("--volume", type=int, choices=(1, 2))
    args = parser.parse_args()

    # Loading the corpus costs a minute, so one run briefs a whole batch.
    corpus = load_corpus(CORPUS_PATH)
    vocabulary = load_vocabulary()
    segmenter = Segmenter()
    grammar = checker.taught_grammar()
    first = checker.resolve_lesson(args.lesson, args.volume)
    last = checker.resolve_lesson(args.through, args.volume) if args.through else first
    for lesson in range(first, last + 1):
        brief_one(lesson, vocabulary, corpus, segmenter, grammar)


def brief_one(lesson: int, vocabulary, corpus, segmenter, grammar) -> None:
    targets = checker.lesson_targets(vocabulary, lesson)

    def passes(row) -> bool:
        return checker.verify(
            row["text"], segmenter=segmenter, vocabulary=vocabulary,
            lemmas=corpus["lemmas"], lesson=lesson, grammar=grammar,
        )["passed"]

    anchors = anchors_for(lesson, keep=passes)

    print(f"=== {checker.describe_lesson(lesson)} ===")
    print(f"定錨 {len(anchors)} 題，還要寫 {ITEMS_PER_LESSON - len(anchors)} 句")
    practised: set[str] = set()
    for row in anchors:
        print(f"  [{row.get('ref', '')}] {row['text']}")
        report = checker.verify(
            row["text"], segmenter=segmenter, vocabulary=vocabulary,
            lemmas=corpus["lemmas"], lesson=lesson, grammar=grammar,
        )
        practised |= set(report["vocabulary"])

    needed = [entry for entry in targets if checker.entry_key(entry) not in practised]
    print(f"\n本課 {len(targets)} 詞，定錨已練到 {len(targets) - len(needed)} 個，"
          f"還缺 {len(needed)}：")
    for entry in needed:
        kanji = (entry.get("kanji") or "").strip()
        kana = (entry.get("kana") or "").strip()
        written = f"{kanji}（{kana}）" if kanji and kanji != kana else kana
        print(f"  {written}　{entry.get('glossZh', '')}　[{entry.get('pos', '')}]")


if __name__ == "__main__":
    main()
