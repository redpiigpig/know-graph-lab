#!/usr/bin/env python3
"""Everything needed to write one Latin lesson's exercises, on one screen.

The Latin counterpart of ``hebrew_lesson_brief.py``, and it exists for the same
reason: writing a sentence for this reader means knowing three things at once --
which of the lesson's twenty words the quoted anchors leave unpractised, what
forms of those words the corpus actually writes, and what else is available to
build the rest of the sentence out of.  Look those up separately and you write
a plausible form instead of an attested one, and the gate sends it back.

Latin adds a trap Hebrew did not have.  A form's lemma is read off a form table
where one spelling often carries several lemmas, so the forms listed here are
only those whose lemma folds to the headword itself.  ``missa`` is both the
Mass and a participle of ``mittō``; listing ``mīsit`` under ``missa`` would
invite exactly the sentence that credits the wrong word.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_latin_lemma_corpus import (  # noqa: E402
    appendix_keys,
    cumulative_vocabulary,
    fold,
    load_vocabulary,
    Tagger,
)
import compose_latin_sentences as checker  # noqa: E402

CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
ITEMS_PER_LESSON = 10


def anchors_for(volume: int, lesson: int) -> list[dict]:
    """The anchors this lesson will print, chosen the way the assembler does."""
    path = CACHE / f"exercises-v{volume}.json"
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    for row in payload.get("lessons", []):
        if row["lesson"] == lesson:
            from assemble_latin_exercises import pick_anchors  # noqa: E402

            return pick_anchors(row.get("anchors", []))
    return []


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lesson", type=int)
    parser.add_argument("--volume", type=int, default=1, choices=[1, 2])
    parser.add_argument("--forms", type=int, default=8, help="每詞列幾個實際出現的形")
    parser.add_argument("--vocab", action="store_true", help="連同累積詞彙一起印")
    args = parser.parse_args()

    tagger = Tagger(gold=("proiel",) if args.volume == 1 else ("proiel", "ittb", "llct"))
    entries = load_vocabulary(tagger=tagger)
    targets, taught_lemmas, taught_keys = cumulative_vocabulary(entries, args.volume, args.lesson)
    corpus = checker.Corpus(checker.corpora_for(args.volume))

    anchors = anchors_for(args.volume, args.lesson)
    practised = checker.practised([row["text"] for row in anchors], targets, corpus, tagger)

    print(f"=== 第 {args.volume} 冊第 {args.lesson} 課 ===")
    print(f"定錨 {len(anchors)} 題，還要寫 {ITEMS_PER_LESSON - len(anchors)} 句")
    for row in anchors:
        print(f"  [{row['ref']}] {row['text']}")

    needed = [entry for entry in targets if entry.ordinal not in practised]
    print(f"\n本課 {len(targets)} 詞，定錨已練到 {len(targets) - len(needed)} 個，還缺 {len(needed)}：")

    # Invert the corpus once: credit-lemma -> the spellings that carry it.
    wanted = {lemma for entry in needed for lemma in entry.credit_lemmas}
    by_lemma: dict[str, Counter] = {}
    for key, row in corpus.forms.items():
        for lemma in set(row["lemmas"]) & wanted:
            by_lemma.setdefault(lemma, Counter())[row["surfaces"][0]] += row["count"]

    for entry in needed:
        pool: Counter = Counter()
        for lemma in entry.credit_lemmas:
            pool.update(by_lemma.get(lemma, Counter()))
        if pool:
            shown = "、".join(form for form, _ in pool.most_common(args.forms))
        elif entry.phrase:
            shown = "（片語，整組到齊才算練到）"
        elif entry.credit_keys:
            shown = "（只認字形）" + "、".join(sorted(entry.credit_keys)[: args.forms])
        else:
            shown = "（詞位未對上語料）"
        print(f"  {entry.headword}　{entry.gloss_zh}　[{entry.pos}]")
        print(f"      實際出現的形：{shown}")

    if not args.vocab:
        return
    appendix = appendix_keys(volume=args.volume)
    appendix_total = len({key for keys in appendix.values() for key in keys})
    print(f"\n可用詞彙：{len(taught_lemmas)} 個詞位、{len(taught_keys)} 種字形"
          f"，另有附錄 {appendix_total} 種（專名／數字／親屬／曆法）")
    known = [
        entry.headword
        for entry in entries
        if entry.volume < args.volume or (entry.volume == args.volume and entry.lesson <= args.lesson)
    ]
    print("　".join(known))


if __name__ == "__main__":
    main()
