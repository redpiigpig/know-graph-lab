#!/usr/bin/env python3
"""Everything needed to write one Koine lesson's exercises, on one screen.

The Greek counterpart of ``hebrew_lesson_brief.py`` and ``latin_lesson_brief.py``,
and it exists for the same reason: writing a sentence for this reader means
knowing three things at once -- which of the lesson's twenty words the quoted
anchors leave unpractised, what forms of those words the corpus actually writes,
and what else is available to build the rest of the sentence out of.  Looking
those up separately is how a plausible form gets written instead of an attested
one, and the gate sends it back.

Every form printed here has already been put through the gate's own lookup, so a
form that appears in this list is one the checker will accept.  The Latin brief
learned that the hard way: listing the commonest spellings instead sent draft
after draft back, because "the corpus has this word" and "the gate will take
this form" are different questions.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

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

ITEMS_PER_LESSON = 10
ANCHORS_PER_LESSON = 3


def anchors_for(volume: int, lesson: int) -> list[dict]:
    """The anchors this lesson will print, chosen the way the assembler does."""
    path = CACHE / f"exercises-greek-vol{volume}.json"
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    for row in payload.get("lessons", []):
        if row["lesson"] == lesson:
            from assemble_greek_exercises import pick_anchors  # noqa: E402

            return pick_anchors(row.get("items", []))
    return []


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lesson", type=int)
    parser.add_argument("--through", type=int, help="一次印到第幾課為止（含）")
    parser.add_argument("--volume", type=int, default=1, choices=[1, 2])
    parser.add_argument("--forms", type=int, default=6, help="每詞列幾個可用的形")
    parser.add_argument("--vocab", action="store_true", help="連同累積詞彙一起印")
    args = parser.parse_args()

    # Loading the corpora costs a minute, so one run briefs a whole batch.
    vocabulary = load_vocabulary()
    units = load_units(VOLUME_CORPORA[args.volume])
    attestation = checker.Attestation.from_units(units)

    # One pass over the corpus: lemma key -> the spellings that carry it, by
    # frequency.  Doing this per word would be a full scan per word.
    forms_by_lemma: dict[str, Counter] = {}
    for unit in units:
        for form, lemma, _layer in unit.tokens:
            if not lemma:
                continue
            printed = bare(form)
            if printed:
                forms_by_lemma.setdefault(fold_key(lemma), Counter())[printed] += 1

    rows = {row[0]: row for row in cumulative_sets(vocabulary, args.volume)}
    for number in range(args.lesson, (args.through or args.lesson) + 1):
        brief_one(number, args, rows, attestation, forms_by_lemma)


def brief_one(lesson, args, rows, attestation, forms_by_lemma) -> None:
    if lesson not in rows:
        raise SystemExit(f"第 {args.volume} 冊沒有第 {lesson} 課")
    _number, items, known = rows[lesson]
    anchors = anchors_for(args.volume, lesson)

    print(f"=== 第 {args.volume} 冊第 {lesson} 課 ===")
    print(f"定錨 {len(anchors)} 題，還要寫 {ITEMS_PER_LESSON - len(anchors)} 句")
    practised: set[str] = set()
    for row in anchors:
        text = row.get("text") or row.get("clause") or ""
        print(f"  [{row.get('ref', '')}] {text}")
        report = checker.verify_sentence(text, known, attestation)
        practised |= set(report["lemmas"])

    needed = [item for item in items if not (item.keys & practised)]
    print(f"\n本課 {len(items)} 詞，定錨已練到 {len(items) - len(needed)} 個，還缺 {len(needed)}：")
    for item in needed:
        pool: Counter = Counter()
        for key in item.keys:
            pool.update(forms_by_lemma.get(key, Counter()))
        usable = []
        for form, _count in pool.most_common(args.forms * 4):
            keys, _how = attestation.look_up(form)
            # The gate resolves a written form back to a lemma and then asks
            # whether that lemma has been taught.  A form whose lemma resolves
            # to something else is attested and still refused, so it must not be
            # offered here.
            if keys and (keys & item.keys) and (keys <= known or keys & known):
                usable.append(form)
            if len(usable) >= args.forms:
                break
        shown = "、".join(usable) if usable else "🚨 本冊語料中沒有可用的形，這一課練不到它"
        print(f"  {item.headword}　{item.gloss_zh}　[{item.pos}]")
        print(f"      可用的形：{shown}")

    if not args.vocab:
        return
    print(f"\n可用詞彙：{len(known)} 個詞位鍵")


if __name__ == "__main__":
    main()
