#!/usr/bin/env python3
"""Assign the 1,000 Hebrew words to 50 lessons of exactly 20 words each.

The curriculum keeps one single running order — Pratico–Van Pelt *Basics of
Biblical Hebrew* chapters 3–35 first (552 words), then the corpus-frequency
extension that fills the list to 1,000 — and cuts that stream into fifty even
lessons of twenty.  A lesson therefore no longer equals a textbook chapter; it
spans whichever chapters happen to fall inside its block, and the lesson header
reports that span so the learner can still track the textbook.

This even shape is what the rest of the release already assumes: the memory
verse selector requires exactly twenty entries per lesson, and the printed
front matter and per-lesson checklist both say 「每課固定收二十個詞」.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "data" / "originalReaders" / "vocabulary" / "hebrew-1000.json"
LESSON_COUNT = 50
WORDS_PER_LESSON = 20
TEXTBOOK_SOURCE = "bbh2_order"


def assign(entries: list[dict]) -> list[dict]:
    ordered = sorted(entries, key=lambda item: item["ordinal"])
    if [item["ordinal"] for item in ordered] != list(range(1, LESSON_COUNT * WORDS_PER_LESSON + 1)):
        raise ValueError("詞彙主檔的 ordinal 必須是 1..1000 的連續序")
    for index, item in enumerate(ordered):
        item["lesson"] = index // WORDS_PER_LESSON + 1
        item["lessonSlot"] = index % WORDS_PER_LESSON + 1
    return entries


def lesson_label(entries: list[dict], lesson: int) -> str:
    block = [item for item in entries if item["lesson"] == lesson]
    chapters = sorted({item["sourceChapter"] for item in block if item["sourceType"] == TEXTBOOK_SOURCE})
    extension = [item for item in block if item["sourceType"] != TEXTBOOK_SOURCE]
    parts = []
    if chapters:
        span = f"第{chapters[0]}章" if len(chapters) == 1 else f"第{chapters[0]}–{chapters[-1]}章"
        parts.append(f"BBH2 {span}")
    if extension:
        parts.append(f"頻率延伸 {len(extension)} 詞")
    return "＋".join(parts)


def report(entries: list[dict]) -> None:
    counts = Counter(item["lesson"] for item in entries)
    for lesson in range(1, LESSON_COUNT + 1):
        print(f"  第 {lesson:02d} 課  {counts[lesson]:>2} 詞  {lesson_label(entries, lesson)}")
    sizes = set(counts.values())
    print(f"  合計 {sum(counts.values())} 詞，每課 {sorted(sizes)} 詞")
    if sizes != {WORDS_PER_LESSON}:
        raise ValueError(f"每課應固定 {WORDS_PER_LESSON} 詞，實得 {sorted(sizes)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="將希伯來文 1000 詞平均分成 50 課、每課 20 詞")
    parser.add_argument("--write", action="store_true", help="寫回詞彙主檔")
    args = parser.parse_args()

    entries = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    if len(entries) != LESSON_COUNT * WORDS_PER_LESSON:
        raise ValueError(f"詞彙主檔應有 {LESSON_COUNT * WORDS_PER_LESSON} 詞，實得 {len(entries)}")
    assign(entries)
    report(entries)
    if args.write:
        VOCAB_PATH.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已寫回 {VOCAB_PATH}")
    else:
        print("（未寫檔；加 --write 才會更新主檔）")


if __name__ == "__main__":
    main()
