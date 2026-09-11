#!/usr/bin/env python3
"""Everything needed to write one lesson's exercises, on one screen.

Writing a sentence for this reader means knowing three things at once: which of
the lesson's twenty words still need practice after the quoted anchors, what
forms of those words the Hebrew Bible actually writes, and which words are
available to build the rest of the sentence from.  Looking each up separately
is where the invented forms came from -- הַמִּגְרָשׁ and וַיִּנְצֹר were written
because a plausible form was easier to reach for than an attested one.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from select_hebrew_memory_verses import DEFAULT_VOCAB, DEFAULT_WLC, load_vocabulary, load_wlc  # noqa: E402
import compose_hebrew_sentences as checker  # noqa: E402

CACHE = ROOT / "output/source-cache/original-readers/hebrew-full"
GLOSSES = CACHE / "hebrew-gloss-zh-reviewed-by-lemma.json"
ASSEMBLED = CACHE / "exercise-set.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lesson", type=int)
    parser.add_argument("--forms", type=int, default=8, help="attested forms to list per word")
    parser.add_argument("--vocab", action="store_true", help="also print the cumulative word list")
    args = parser.parse_args()

    vocabulary = load_vocabulary(DEFAULT_VOCAB)
    glosses = {
        row["strong"].lstrip("H"): row["glossZh"]
        for row in json.loads(GLOSSES.read_text(encoding="utf-8"))["items"]
    }
    items = vocabulary[args.lesson]

    anchors: list[dict] = []
    practised: set[int] = set()
    if ASSEMBLED.exists():
        payload = json.loads(ASSEMBLED.read_text(encoding="utf-8"))
        for row in payload["lessons"]:
            if row["lesson"] != args.lesson:
                continue
            anchors = [item for item in row["items"] if item["kind"] == "quoted"]
            practised = {
                word.get("ordinal") for item in anchors for word in item.get("targetWords") or []
            }

    print(f"=== 第 {args.lesson} 課 ===")
    print(f"定錨 {len(anchors)} 題，還要寫 {10 - len(anchors)} 句")
    for item in anchors:
        print(f"  [{item['ref']}] {item['text']}")

    needed = [item for item in items if item.ordinal not in practised]
    print(f"\n本課二十詞，定錨已練到 {len(items) - len(needed)} 個，還缺 {len(needed)}：")
    verses = load_wlc(DEFAULT_WLC)
    forms: dict[str, Counter] = {}
    wanted = {strong for item in needed for strong in item.strongs}
    for verse in verses:
        for token in verse.tokens:
            for strong in token.strongs & wanted:
                forms.setdefault(strong, Counter())[checker.bare(token.text)] += 1
    for item in needed:
        gloss = next((glosses.get(s, "") for s in item.strongs if s in glosses), "")
        pool = Counter()
        for strong in item.strongs:
            pool.update(forms.get(strong, Counter()))
        shown = "、".join(form for form, _ in pool.most_common(args.forms)) or "（無 Strong，屬詞素）"
        print(f"  {item.pointed}　{gloss}")
        print(f"      實際出現的形：{shown}")

    if not args.vocab:
        return
    known = [
        entry.pointed
        for number in sorted(vocabulary)
        if number <= args.lesson
        for entry in vocabulary[number]
    ]
    print(f"\n可用詞彙（{len(known)} 個）：")
    print("　".join(known))


if __name__ == "__main__":
    main()
