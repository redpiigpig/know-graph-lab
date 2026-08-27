#!/usr/bin/env python3
"""Give the Greek vocabulary the part-of-speech field it never had.

Hebrew reads its part of speech from the vocabulary master and Latin from
Collins's own citation line, so the lesson tables of those two readers print a
詞類 column.  Greek's master carries no such field, and the column was simply
absent — while the flashcard deck has been printing one all along, worked out by
``flashcard_pos.greek_part_of_speech``.  The same answer therefore already
exists; it was just never written back to where the reader and the web page can
see it.

This writes it to both places that need it:

* ``data/originalReaders/vocabulary/greek-2000.json`` — the source the master is
  built from, so a full rebuild reproduces the field rather than dropping it;
* ``output/source-cache/original-readers/greek-full/greek-reader-two-volumes.json``
  — the built master every surface actually reads, so the field appears without
  re-running the whole Greek build.

``build_greek_reader_data.py`` copies ``pos`` through, so the two stay in step.

A blank is a legitimate answer and is written as one: a wrong label is learned
as fact.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from flashcard_pos import greek_part_of_speech  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
VOCAB = ROOT / "data/originalReaders/vocabulary/greek-2000.json"
CACHE = ROOT / "output/source-cache/original-readers/greek-full"
MASTER = CACHE / "greek-reader-two-volumes.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, payload) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def gloss_map(master) -> dict[str, str]:
    """Chinese by lemma, read from the built master.

    The reviewed gloss lives in the master's own vocabulary rows, and two of the
    part-of-speech rules read it: 「（配屬格）」 marks a preposition and a gloss
    whose senses all end in 「的」 an adjective.  Reading it from the by-lemma
    gloss cache instead returned empty strings for the Septuagint and patristic
    adjectives — which is exactly the set those two rules exist to settle.
    """

    return {
        word["lemma"]: word.get("glossZh", "")
        for volume in master["volumes"]
        for lesson in volume["lessons"]
        for word in lesson["vocabulary"]
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the two files")
    args = parser.parse_args()

    master = load(MASTER)
    glosses = gloss_map(master)
    vocab = load(VOCAB)
    entries = vocab["entries"]

    decided: dict[str, str] = {}
    for entry in entries:
        lemma = entry["lemma"]
        pos = greek_part_of_speech(entry, glosses.get(lemma, ""))
        decided[lemma] = pos
        entry["pos"] = pos

    filled = sum(1 for pos in decided.values() if pos)
    print(f"詞條 {len(entries)}，判出詞類 {filled}，留白 {len(entries) - filled}")
    by_label: dict[str, int] = {}
    for pos in decided.values():
        by_label[pos or "（留白）"] = by_label.get(pos or "（留白）", 0) + 1
    for label, count in sorted(by_label.items(), key=lambda pair: -pair[1]):
        print(f"  {label}: {count}")

    touched = 0
    for volume in master["volumes"]:
        for lesson in volume["lessons"]:
            for word in lesson["vocabulary"]:
                word["pos"] = decided.get(word["lemma"], "")
                touched += 1
    print(f"主檔詞條 {touched} 筆已補 pos")

    if not args.write:
        print("（未寫入；加 --write）")
        return 0

    dump(VOCAB, vocab)
    dump(MASTER, master)
    print(f"已寫入 {VOCAB.relative_to(ROOT)}")
    print(f"已寫入 {MASTER.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
