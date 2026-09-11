#!/usr/bin/env python3
"""Mine the quoted items of the Japanese reader's ten-item exercise sets.

The exercise contract (`references/exercise-sets.md`) wants three of a lesson's
ten items to be real sentences from the corpus, so the learner always has a
correct sample to measure a composed item against.  This finds them: whole
sentences out of `lemma-corpus.json` where **every word has already been
taught** by that lesson, short enough to translate, and not used by an earlier
lesson.

Nothing is composed here and nothing is adapted.  The Hebrew miner may cut a
verse at its accents; Japanese sentences are already short, so a sentence is
taken whole or not at all — trimming a Japanese sentence at a particle changes
what it says.

**佛典訓読不引。** Those files carry `rightsChecked: false`: the Chinese
reading and its date are unverified, and the release's stop condition says an
unverified 訓読 is not to be treated as public domain.  Pass
`--include-unchecked-rights` to see them anyway; do not publish the result.

**中文欄留白。** A quoted item's Chinese must come from a published
translation, not from this script — the same split the Hebrew reader makes,
where `attach_hebrew_exercise_chinese.py` fills the RCUV2010 wording in
afterwards.  Until that step exists for Japanese the validator will report the
blank answers, which is the correct state: visible and unfilled beats invented.

    python -X utf8 scripts/build_japanese_exercises.py --write
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_japanese_lemma_corpus import (  # noqa: E402
    OUTPUT as CORPUS_PATH,
    Token,
    Vocabulary,
    global_lesson,
    load_corpus,
    load_vocabulary,
)
from compose_japanese_sentences import (  # noqa: E402
    LESSONS_PER_VOLUME,
    coverage_for,
    describe_lesson,
    entry_key,
    headword,
    lesson_targets,
    taught_grammar,
    verify_tokens,
)

OUTPUT = ROOT / "output/source-cache/original-readers/japanese-full/exercises.json"
LESSONS = 100
QUOTED_PER_LESSON = 3
# 合約：三到八個詞，短句優先。助詞助動詞算進來所以上界放到十四個詞素，
# 再多的句子印在初學課本上就不是「短句」了。
MIN_TOKENS = 4
MAX_TOKENS = 14


def tokens_of(row: dict[str, Any]) -> list[Token]:
    return [
        Token(
            surface=token["surface"],
            base=token["base"],
            pos=token["pos"],
            sub=token.get("sub", ""),
            reading=token.get("reading", ""),
        )
        for token in row["tokens"]
    ]


def citation(row: dict[str, Any]) -> str:
    """出處：作者《篇名》，沒有作者的（聖書、萬葉集）就用篇名。"""
    title = row.get("title") or row.get("docId") or ""
    author = (row.get("author") or "").strip()
    return f"{author}〈{title}〉" if author else str(title)


def select(
    rows: list[dict[str, Any]],
    *,
    vocabulary: Vocabulary,
    lemmas: dict[str, Any],
    grammar: frozenset[str],
    per_lesson: int,
    include_unchecked: bool,
) -> dict[int, list[dict[str, Any]]]:
    """一課一課往下挑，挑過的句子不再用。

    先算每句最早可讀的課次（句中所有詞裡最晚教到的那一課），再在該課之後的
    課次裡按「能練到幾個本課詞、句子多短」排。先算一次是為了不要對 100 課
    ×8,508 句各驗一次。
    """
    earliest: dict[int, int] = {}
    cache: dict[int, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if not include_unchecked and not row.get("rightsChecked", True):
            continue
        tokens = tokens_of(row)
        if not (MIN_TOKENS <= len(tokens) <= MAX_TOKENS):
            continue
        report = verify_tokens(
            tokens, vocabulary=vocabulary, lemmas=lemmas, lesson=LESSONS, grammar=grammar
        )
        if report["unattested"] or report["untaught"]:
            continue
        lessons = [
            global_lesson(entry)
            for entry in (vocabulary.lookup(token) for token in tokens)
            if entry is not None
        ]
        if not lessons:
            continue
        earliest[index] = max(lessons)
        cache[index] = report

    by_lesson: dict[int, list[int]] = {}
    for index, lesson in earliest.items():
        by_lesson.setdefault(lesson, []).append(index)

    picked: dict[int, list[dict[str, Any]]] = {}
    available: list[int] = []
    seen_text: set[str] = set()
    for lesson in range(1, LESSONS + 1):
        available.extend(by_lesson.get(lesson, []))
        targets = {entry_key(entry) for entry in lesson_targets(vocabulary, lesson)}
        chosen: list[int] = []
        covered: set[str] = set()
        pool = list(available)

        def gain(index: int) -> tuple[int, int, int, str]:
            keys = set(cache[index]["vocabulary"])
            return (
                -len((keys & targets) - covered),  # 先要練到本課詞
                # 再要「新」：句中最晚教到的詞越接近本課越好。少了這一條，後面的
                # 課次會一直挑第 3 課就讀得懂的舊句子，練不到剛學的東西。
                -earliest[index],
                len(rows[index]["tokens"]),        # 再要短
                rows[index]["id"],                 # 最後求穩定
            )

        while pool and len(chosen) < per_lesson:
            pool.sort(key=gain)
            index = pool.pop(0)
            text = rows[index]["text"]
            if text in seen_text:
                continue
            chosen.append(index)
            seen_text.add(text)
            covered |= set(cache[index]["vocabulary"]) & targets
        available = [index for index in available if index not in set(chosen)]
        picked[lesson] = [
            {"row": rows[index], "report": cache[index]} for index in chosen
        ]
    return picked


def item_for(number: int, hit: dict[str, Any], targets: list[dict[str, Any]]) -> dict[str, Any]:
    row, report = hit["row"], hit["report"]
    keys = {entry_key(entry): entry for entry in targets}
    practised = [keys[key] for key in dict.fromkeys(report["vocabulary"]) if key in keys]
    return {
        "no": number,
        "kind": "quoted",
        # 出處印給人看：青空的 manifest 鍵是「005067」，那是檔名不是出處。
        "ref": citation(row) or row.get("ref") or row["id"],
        "text": row["text"],
        # 引用題的中文必須來自既有譯本，不由本腳本生成——留白是刻意的。
        "chinese": "",
        "chineseSource": "",
        "targetWords": [
            {"headword": headword(entry), "kana": entry.get("kana", ""),
             "glossZh": entry.get("glossZh", "")}
            for entry in practised
        ],
        "source": {
            "citation": citation(row),
            "corpus": row.get("source", ""),
            "corpusRef": row.get("ref", ""),
            "url": row.get("sourceUrl", ""),
            "sentenceId": row["id"],
        },
        "verification": {
            "unattested": report["unattested"],
            "untaught": report["untaught"],
            "grammar": report["grammar"],
            "passed": report["passed"],
        },
        "reviewedBy": "",
    }


def build(corpus: dict[str, Any], vocabulary: Vocabulary, *, per_lesson: int,
          include_unchecked: bool) -> dict[str, Any]:
    grammar = taught_grammar()
    picked = select(
        corpus["sentences"],
        vocabulary=vocabulary,
        lemmas=corpus["lemmas"],
        grammar=grammar,
        per_lesson=per_lesson,
        include_unchecked=include_unchecked,
    )
    lessons_out: list[dict[str, Any]] = []
    for lesson in range(1, LESSONS + 1):
        targets = lesson_targets(vocabulary, lesson)
        hits = picked.get(lesson, [])
        items = [item_for(n, hit, targets) for n, hit in enumerate(hits, start=1)]
        coverage = coverage_for([hit["report"] for hit in hits], targets)
        lessons_out.append(
            {
                "lesson": lesson,
                "volume": (lesson - 1) // LESSONS_PER_VOLUME + 1,
                "lessonInVolume": (lesson - 1) % LESSONS_PER_VOLUME + 1,
                "items": items,
                "coverage": coverage,
            }
        )
    quoted = sum(len(row["items"]) for row in lessons_out)
    return {
        "schemaVersion": "1.0.0",
        "languageCode": "ja",
        "direction": "original-to-chinese",
        "itemsPerLesson": 10,
        "built": date.today().isoformat(),
        "tokenizer": corpus["tokenizer"],
        "note": (
            "只有引用題。每課十題的另外七題由作者自撰，寫完用 "
            "compose_japanese_sentences.py --check 過閘。引用題的中文欄留白，"
            "待既有譯本補上；本腳本不生成中文。"
        ),
        "counts": {
            "lessons": LESSONS,
            "quotedItems": quoted,
            "quotedTarget": LESSONS * QUOTED_PER_LESSON,
            "lessonsShort": sum(1 for row in lessons_out if len(row["items"]) < QUOTED_PER_LESSON),
        },
        "lessons": lessons_out,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=CORPUS_PATH)
    parser.add_argument("--per-lesson", type=int, default=QUOTED_PER_LESSON)
    parser.add_argument("--include-unchecked-rights", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    corpus = load_corpus(args.corpus)
    vocabulary = load_vocabulary()
    payload = build(
        corpus,
        vocabulary,
        per_lesson=args.per_lesson,
        include_unchecked=args.include_unchecked_rights,
    )
    counts = payload["counts"]
    print(
        f"挖到引用題 {counts['quotedItems']}/{counts['quotedTarget']} 題，"
        f"湊不滿的課次 {counts['lessonsShort']} 課"
    )
    for row in payload["lessons"]:
        if len(row["items"]) < QUOTED_PER_LESSON:
            continue
        coverage = row["coverage"]
        print(
            f"  {describe_lesson(row['lesson'])} {len(row['items'])} 題，"
            f"練到本課 {coverage['practised']}/{coverage['lessonWords']} 詞"
        )
    print("引用題的中文欄一律留白，要由既有譯本補上；留白看得出缺，編出來看不出來。")
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        print(f"寫入 {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
