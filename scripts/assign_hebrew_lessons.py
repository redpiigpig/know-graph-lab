#!/usr/bin/env python3
"""Assign the 1,000 Hebrew words to 50 lessons on the textbook's own schedule.

The reader follows Pratico–Van Pelt *Basics of Biblical Hebrew* while the
textbook lasts, so a lesson is a textbook chapter, not a fixed quota.  BBH2
carries vocabulary in chapters 3–35 (chapters 1–2 are alphabet and pointing),
and those chapters are deliberately uneven — chapter 8 has 39 words, chapter 32
has 4.  Slicing that stream into equal twenties would silently break the
progression the learner is actually following.

Lessons 1–33 therefore mirror BBH2 chapters 3–35 exactly.  The frequency
extension that fills the curriculum to 1,000 is then spread as evenly as
possible over the remaining lessons, keeping its frequency order.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "data" / "originalReaders" / "vocabulary" / "hebrew-1000.json"
LESSON_COUNT = 50
TEXTBOOK_SOURCE = "bbh2_order"


def assign(entries: list[dict]) -> list[dict]:
    textbook = [item for item in entries if item["sourceType"] == TEXTBOOK_SOURCE]
    extension = [item for item in entries if item["sourceType"] != TEXTBOOK_SOURCE]

    by_chapter: dict[int, list[dict]] = defaultdict(list)
    for item in textbook:
        by_chapter[item["sourceChapter"]].append(item)
    chapters = sorted(by_chapter)
    if len(chapters) > LESSON_COUNT:
        raise ValueError(f"課本章數 {len(chapters)} 超過 {LESSON_COUNT} 課")

    for lesson, chapter in enumerate(chapters, start=1):
        for slot, item in enumerate(sorted(by_chapter[chapter], key=lambda entry: entry["ordinal"]), start=1):
            item["lesson"] = lesson
            item["lessonSlot"] = slot

    remaining_lessons = LESSON_COUNT - len(chapters)
    if remaining_lessons <= 0:
        if extension:
            raise ValueError("課本已佔滿 50 課，延伸詞無處可放")
        return entries

    # Spread the extension evenly; the earlier lessons absorb the remainder so
    # the final lessons never end up heavier than the ones before them.
    base, extra = divmod(len(extension), remaining_lessons)
    cursor = 0
    for offset in range(remaining_lessons):
        lesson = len(chapters) + offset + 1
        size = base + (1 if offset < extra else 0)
        for slot, item in enumerate(extension[cursor : cursor + size], start=1):
            item["lesson"] = lesson
            item["lessonSlot"] = slot
        cursor += size
    if cursor != len(extension):
        raise ValueError("延伸詞分配不完整")
    return entries


def report(entries: list[dict]) -> None:
    counts = Counter(item["lesson"] for item in entries)
    for lesson in range(1, LESSON_COUNT + 1):
        source = next((item["sourceType"] for item in entries if item["lesson"] == lesson), "")
        chapter = next((item["sourceChapter"] for item in entries if item["lesson"] == lesson), None)
        label = f"BBH2 第{chapter}章" if source == TEXTBOOK_SOURCE else "頻率延伸"
        print(f"  第 {lesson:02d} 課  {counts[lesson]:>2} 詞  {label}")
    print(f"  合計 {sum(counts.values())} 詞，最少 {min(counts.values())}、最多 {max(counts.values())}")


def main() -> None:
    parser = argparse.ArgumentParser(description="依課本章次重新分配希伯來文 50 課詞彙")
    parser.add_argument("--write", action="store_true", help="寫回詞彙主檔")
    args = parser.parse_args()

    entries = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    if len(entries) != 1000:
        raise ValueError(f"詞彙主檔應有 1000 詞，實得 {len(entries)}")
    assign(entries)
    report(entries)
    if args.write:
        VOCAB_PATH.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已寫回 {VOCAB_PATH}")
    else:
        print("（未寫檔；加 --write 才會更新主檔）")


if __name__ == "__main__":
    main()
