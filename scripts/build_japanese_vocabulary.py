#!/usr/bin/env python3
"""Turn《大家的日本語》's lesson order into the Japanese reader's vocabulary spine.

The contract freezes two volumes of fifty lessons of twenty words. The textbook
order governs the sequence and is never invented, so this only does three
things to the order that ``fetch_minna_vocabulary.py`` recovered:

1. **Drops the proper names.** Countries, cities, composers and institutions do
   not take a lesson slot — the same rule the Hebrew reader follows, and for
   the same reason: 「アメリカ」 teaches nothing about Japanese. They go to the
   appendix instead, in their own table.
2. **Drops a word the textbook lists twice**, keeping its first appearance.
   132 words are relisted in a later lesson for a new sense; the deck wants one
   card per word.
3. **Cuts the running order into blocks of twenty.** A lesson therefore spans
   whichever textbook lessons fall inside its block, and the header prints that
   span rather than pretending the lesson is a textbook lesson — again as in
   Hebrew.

What it does **not** do is invent words to reach 2,000. 初級 I and II yield
1,875 after the two drops; the shortfall is reported, and the contract's own
answer is to extend from the religious-studies corpus by a documented frequency
rule, exactly as the Hebrew reader extends past BBH chapter 35.

    python -X utf8 scripts/build_japanese_vocabulary.py --write
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/original-readers/japanese-full"
ORDER = CACHE / "minna-lesson-order.json"
VOCAB = ROOT / "data/originalReaders/vocabulary/japanese-2000.json"
NAMES = ROOT / "data/originalReaders/vocabulary/japanese-proper-names.json"

PER_LESSON = 20
LESSONS_PER_VOLUME = 50

# 專名不佔課內詞額。逐個讀過詞表列出來的，不是靠片假名猜的——片假名裡絕大多數
# 是外來語（ノート、テレビ、コーヒー），那些是正經的課內詞。
PROPER_NAMES: dict[str, str] = {
    # 國名與地域
    "アメリカ": "國名", "イギリス": "國名", "インド": "國名", "インドネシア": "國名",
    "タイ": "國名", "ドイツ": "國名", "フランス": "國名", "ブラジル": "國名",
    "イタリア": "國名", "スイス": "國名", "メキシコ": "國名", "スペイン": "國名",
    "オーストラリア": "國名", "シンガポール": "國名", "ロシア": "國名",
    "ベトナム": "國名", "サウジアラビア": "國名", "ドミニカ": "國名",
    "ポーランド": "國名", "イラン": "國名", "グアム": "地名",
    "ヨーロッパ": "地域", "アジア": "地域", "アフリカ": "地域",
    "韓国": "國名", "中国": "國名",
    # 都市與行政區
    "ニューヨーク": "都市", "ロンドン": "都市", "バンコク": "都市",
    "ロサンゼルス": "都市", "カリフォルニア": "地名", "ミュンヘン": "都市",
    # 人名
    "グラハム・ベル": "人名", "ショパン": "人名", "ゴッホ": "人名", "ベートーベン": "人名",
    # 機構
    "東京大学": "機構", "江戸東京博物館": "機構",
}


def load_order() -> list[dict]:
    return json.loads(ORDER.read_text(encoding="utf-8"))["words"]


def is_proper(word: dict) -> str:
    return PROPER_NAMES.get(word["kanji"]) or PROPER_NAMES.get(word["kana"]) or ""


def build() -> tuple[list[dict], list[dict], list[dict]]:
    words = load_order()
    course: list[dict] = []
    names: list[dict] = []
    repeats: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for word in words:
        identity = (word["kana"], word["kanji"])
        kind = is_proper(word)
        if kind:
            names.append({**word, "category": kind})
            continue
        if identity in seen:
            repeats.append(word)
            continue
        seen.add(identity)
        course.append(word)
    return course, names, repeats


def assign(course: list[dict]) -> list[dict]:
    """Twenty to a lesson, in the textbook's order, spans printed not hidden."""

    assigned = []
    for index, word in enumerate(course):
        lesson_index = index // PER_LESSON
        volume = lesson_index // LESSONS_PER_VOLUME + 1
        lesson = lesson_index % LESSONS_PER_VOLUME + 1
        assigned.append(
            {
                **word,
                "ordinal": index + 1,
                "volume": volume,
                "readerLesson": lesson,
                "lessonSlot": index % PER_LESSON + 1,
                # 這個詞在課本裡的課次，與讀本課次是兩回事，兩個都留著。
                "textbookLesson": word["lesson"],
            }
        )
    return assigned


def spans(assigned: list[dict]) -> dict[str, str]:
    """What each reader lesson covers in the textbook, for its header."""

    by_lesson: dict[str, list[int]] = {}
    for word in assigned:
        key = f"v{word['volume']}-{word['readerLesson']}"
        by_lesson.setdefault(key, []).append(word["textbookLesson"])
    return {
        key: (f"課本第 {min(v)} 課" if min(v) == max(v) else f"課本第 {min(v)}–{max(v)} 課")
        for key, v in by_lesson.items()
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    course, names, repeats = build()
    assigned = assign(course)
    target = PER_LESSON * LESSONS_PER_VOLUME * 2

    print(f"課本詞序 {len(load_order())} 筆")
    print(f"  專名移入附錄 {len(names)}")
    print(f"  課本重列（保留首次出現）{len(repeats)}")
    print(f"  課內詞 {len(course)}／{target}")
    if len(course) < target:
        print(f"  ⚠ 差 {target - len(course)} 詞。依體例由宗教學語料頻率延伸補足，")
        print("     不得自行造詞，也不得把專名放回來湊數。")
    full = [w for w in assigned if w["volume"] <= 2]
    print(f"  可排入兩冊的 {len(full)}，最後一課 v{full[-1]['volume']}-{full[-1]['readerLesson']}"
          f" 只有 {sum(1 for w in full if w['volume'] == full[-1]['volume'] and w['readerLesson'] == full[-1]['readerLesson'])} 詞")

    if not args.write:
        print("（未寫入；加 --write）")
        return 0

    VOCAB.write_text(
        json.dumps(
            {
                "schemaVersion": "1.0.0",
                "contract": {
                    "volumes": 2,
                    "lessonsPerVolume": LESSONS_PER_VOLUME,
                    "wordsPerLesson": PER_LESSON,
                    "target": target,
                    "order": "《大家的日本語》初級 I→II 課次順序（經 u-biq 逐課頁重建）",
                    "properNames": "不佔課內詞額，另立附錄專名表",
                },
                "counts": {
                    "course": len(course),
                    "properNames": len(names),
                    "textbookRepeats": len(repeats),
                    "shortfall": max(0, target - len(course)),
                },
                "lessonSpans": spans(assigned),
                "entries": assigned,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    NAMES.write_text(
        json.dumps(
            {
                "schemaVersion": "1.0.0",
                "note": "《大家的日本語》詞表裡的專名，不佔課內詞額，進附錄專名表。",
                "count": len(names),
                "items": names,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"已寫入 {VOCAB.relative_to(ROOT)} 與 {NAMES.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
