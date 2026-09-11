#!/usr/bin/env python3
"""Mine quoted anchors for the ecclesiastical Latin reader's exercise sets.

Ten items a lesson, of which three are quotations and seven are written by the
author.  This file produces candidates for the three: real sentences out of the
corpus, never composed, never adapted.  It offers more than three so that the
assembler can drop the ones whose source has no published Chinese to answer
with -- the same division of labour the Hebrew miner arrived at.

A candidate is a whole verse of the Clementine Vulgate, or a clause cut out of
one at the punctuation the edition printed; for the lower volume it is a clause
of one of the fifty church readings.  Nothing is cut anywhere except where the
text itself stops.

The bar for printing a sentence is the same bar the composed sentences must
clear, and it is enforced by the same code: ``compose_latin_sentences`` decides
what counts as attested, what counts as taught and where an enclitic is.  If
the two gates ever disagreed, half a lesson would be held to one standard and
half to another.

An exercise carries no Chinese at all.  The owner's ruling of 2026-09-11 is
that the point of the exercise is for the learner to translate it, so only the
reading -- the worked model -- prints a translation.  What each item does carry
is ``answerKeyRef``: where the sentence came from, precise enough that a future
answer key can go and fetch the published rendering.  Recording where the
answer is and never the answer itself also means this file cannot ship one
edition's wording into a page that is supposed to be blank.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_latin_lemma_corpus import (  # noqa: E402
    OUTPUT as CORPUS_FILES,
    Tagger,
    appendix_keys,
    clause_pieces,
    comma_pieces,
    load_vocabulary,
    tokenise,
)
from compose_latin_sentences import Corpus, corpora_for, word_reading  # noqa: E402

CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
OUTPUT_FILE = CACHE / "exercises.json"

# The miner supplies anchors, not a whole lesson: three are printed and the
# spec's other seven are the author's.  Offering six leaves the assembler room
# to refuse the ones it does not want.  Where the corpus cannot yield three --
# lesson one of the upper volume has one verb among its twenty words -- the
# lesson says so and the author writes all ten.
CANDIDATES_PER_LESSON = 6
MIN_WORDS = 3
MAX_WORDS = 8
NEVER = (99, 99)  # a word no lesson teaches

# Editorial angle brackets survive in eleven places in the lower volume's
# readings.  They are the edition's supplied letters, not the author's words,
# and a line of an exercise is no place to explain that.
APPARATUS = ("&lt;", "&gt;", "[", "]", "<", ">")


@dataclass(frozen=True)
class Unit:
    uid: str
    ref: str  # what may only be quoted once: a verse, or one reading block
    source: str  # what to cite: the verse reference, or the reading's title
    kind: str  # verse | clause | block
    part: int
    part_count: int
    text: str
    words: tuple[str, ...]
    book: str
    chapter: int
    verse: int
    lesson: int  # the church reading this came from; 0 for the Vulgate

    @property
    def word_count(self) -> int:
        return len(self.words)


# ---------------------------------------------------------------------------
# pure helpers
# ---------------------------------------------------------------------------

def first_taught_index(
    entries: Sequence[Any], appendix: set[str]
) -> tuple[dict[str, tuple[int, int]], dict[str, tuple[int, int]],
           dict[str, set[tuple[int, int]]], dict[str, set[tuple[int, int]]]]:
    """When each lemma and each written form becomes available, and to whom.

    Two directions are needed and they are not the same question.  "Has this
    word been taught yet" wants the earliest lesson that teaches it; "which of
    this lesson's twenty does this sentence practise" wants every entry the
    word could be.  Building both here means a lesson's scan is set lookups
    rather than a walk over two thousand entries.

    Appendix material -- the proper names, the numerals, the kinship terms, the
    calendar -- is available from the start, which is what the reader's own
    contract says: names are appendix only, never a lesson slot.
    """
    lemma_first: dict[str, tuple[int, int]] = {}
    key_first: dict[str, tuple[int, int]] = {key: (0, 0) for key in appendix}
    lemma_entries: dict[str, set[tuple[int, int]]] = defaultdict(set)
    key_entries: dict[str, set[tuple[int, int]]] = defaultdict(set)
    for entry in entries:
        stamp = (entry.volume, entry.lesson)
        # Availability is asked of every lemma the headword could wear; credit
        # is given only for the ones that are this word.  `missa` makes the
        # participle of `mitto` readable from the lesson that teaches 彌撒 --
        # it is on the page, spelled that way -- but a sentence using `misit`
        # has not practised 彌撒.
        for lemma in entry.lemmas:
            if stamp < lemma_first.get(lemma, NEVER):
                lemma_first[lemma] = stamp
        for lemma in entry.credit_lemmas:
            lemma_entries[lemma].add(entry.key)
        for key in entry.form_keys:
            if stamp < key_first.get(key, NEVER):
                key_first[key] = stamp
        if not entry.phrase:
            # A phrase entry is never credited by one of its words; the
            # composed items reach those, checked whole in `practised`.
            for key in entry.credit_keys:
                key_entries[key].add(entry.key)
    return lemma_first, key_first, lemma_entries, key_entries


def part_available(
    part: dict[str, Any],
    lemma_first: dict[str, tuple[int, int]],
    key_first: dict[str, tuple[int, int]],
) -> tuple[int, int]:
    """The earliest (volume, lesson) at which this piece of a word is known."""
    best = key_first.get(part["key"], NEVER)
    for lemma in part["lemmas"]:
        stamp = lemma_first.get(lemma)
        if stamp and stamp < best:
            best = stamp
    return best


def block_id(unit: "Unit") -> str:
    """The reading block a church clause came out of.

    A church unit is ``L47#3`` and its clauses are ``L47#3#19``, so the block
    is everything before the *last* hash.  Splitting on the first one gives
    ``L47``, which matches no block at all -- the Chinese silently never
    attached and every lower-volume item reported itself as having no answer.
    """
    return unit.uid.rsplit("#", 1)[0]


def looks_like_apparatus(text: str) -> bool:
    return any(mark in text for mark in APPARATUS)


def printable_reason(
    unit: Unit,
    lemmas: Sequence[frozenset[str]],
    proper: Sequence[bool],
    verbal: Sequence[bool],
) -> str | None:
    """Reject a fragment that reads as a list, a stub, or half a thought.

    The verb test is the one that matters.  Cut at commas, the Vulgate yields
    thousands of pieces three to eight words long whose every word has been
    taught -- ``et ad Saram``, ``et in gloriam`` -- and printing those as
    translation exercises teaches the learner that a prepositional phrase is a
    sentence.  A piece with no possible predicate is not offered.
    """
    if not (MIN_WORDS <= unit.word_count <= MAX_WORDS):
        return "長度不合"
    if looks_like_apparatus(unit.text):
        return "含校勘符號"
    if not any(verbal):
        return "無謂語"
    if sum(1 for flag in proper if flag) >= 3:
        return "專名列舉"
    if sum(1 for flag in proper if not flag) < 2:
        return "缺乏實詞"
    counts: Counter[str] = Counter()
    for group in lemmas:
        for lemma in group:
            counts[lemma] += 1
    if counts and max(counts.values()) >= 3:
        return "重複用詞"
    return None


def difficulty(unit: Unit) -> tuple[int, int, int]:
    """Shorter first, whole verses ahead of clauses, then canonical order."""
    return (unit.word_count, 0 if unit.kind == "verse" else 1, unit.verse)


# ---------------------------------------------------------------------------
# corpus units
# ---------------------------------------------------------------------------

def load_units(corpus_name: str) -> list[Unit]:
    payload = json.loads(CORPUS_FILES[corpus_name].read_text(encoding="utf-8"))
    units: list[Unit] = []
    for row in payload["units"]:
        text = row["text"]
        whole_words = tuple(tokenise(text))
        # A verse may be quoted once; so may a reading block.  For the Vulgate
        # that key is the reference, for the church corpus it is the block --
        # the fifty readings have fifty titles between them, and keying on the
        # title would let one reading be spent on one lesson.
        unit_ref = row["ref"] if corpus_name == "vulgate" else row["id"]
        source = row["ref"]
        if corpus_name == "vulgate":
            units.append(
                Unit(
                    uid=row["id"], ref=unit_ref, source=source, kind="verse",
                    part=0, part_count=1, text=text, words=whole_words,
                    book=row["book"], chapter=row["chapter"], verse=row["verse"],
                    lesson=0,
                )
            )
        pieces = clause_pieces(text)
        if len(pieces) == 1 and corpus_name == "vulgate" and len(whole_words) <= MAX_WORDS:
            continue  # the clause is the verse; do not offer it twice
        # A strong-stop clause that overruns is cut again at its commas; a
        # comma piece with no verb in it is thrown out downstream.
        expanded: list[str] = []
        for piece in pieces:
            expanded.append(piece)
            if len(tokenise(piece)) > MAX_WORDS:
                expanded.extend(part for part in comma_pieces(piece) if part != piece)
        for index, piece in enumerate(expanded, start=1):
            units.append(
                Unit(
                    uid=f"{row['id']}#{index}",
                    ref=unit_ref,
                    source=source,
                    kind="clause",
                    part=index,
                    part_count=len(expanded),
                    text=piece,
                    words=tuple(tokenise(piece)),
                    book=row.get("book", ""),
                    chapter=row.get("chapter", 0),
                    verse=row.get("verse", row.get("block", 0)),
                    lesson=row.get("lesson", 0),
                )
            )
    return units


# ---------------------------------------------------------------------------
# selection
# ---------------------------------------------------------------------------

def select(
    candidates: list[tuple[Unit, set[tuple[int, int]]]],
    lesson_keys: set[tuple[int, int]],
    used_refs: set[str],
) -> list[tuple[Unit, set[tuple[int, int]]]]:
    """Greedy: widest coverage first, whole verses next, then shortest.

    Whether a published Chinese rendering happens to exist used to be the
    second key.  It no longer is: exercises print no Chinese, so ranking on it
    was ranking on something the page never shows -- and it was quietly
    preferring the forty chapters that had been fetched over better sentences
    from the other 1,300.
    """
    pool = [row for row in candidates if row[0].ref not in used_refs and row[1] & lesson_keys]
    chosen: list[tuple[Unit, set[tuple[int, int]]]] = []
    remaining = set(lesson_keys)
    taken: set[str] = set()
    seen_text: set[str] = set()
    while pool and len(chosen) < CANDIDATES_PER_LESSON:
        pool.sort(
            key=lambda row: (
                -len(row[1] & remaining),
                0 if row[0].kind == "verse" else 1,
                row[0].word_count,
                row[0].uid,
            )
        )
        best = pool.pop(0)
        if best[0].ref in taken or best[0].text in seen_text:
            continue
        if not (best[1] & remaining) and chosen:
            break
        chosen.append(best)
        taken.add(best[0].ref)
        seen_text.add(best[0].text)
        remaining -= best[1]
        pool = [row for row in pool if row[0].ref not in taken]
    chosen.sort(key=lambda row: difficulty(row[0]))
    return chosen


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--volume", type=int, default=1, choices=[1, 2])
    parser.add_argument("--lesson", type=int, help="只跑一課，用於檢查")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    volume = args.volume
    corpus_name = "vulgate" if volume == 1 else "church"
    corpus = Corpus(corpora_for(volume))
    tagger = Tagger(gold=("proiel",) if volume == 1 else ("proiel", "ittb", "llct"))
    entries = load_vocabulary(tagger=tagger)
    appendix: set[str] = set()
    for keys in appendix_keys(volume=volume).values():
        appendix |= keys
    lemma_first, key_first, lemma_entries, key_entries = first_taught_index(entries, appendix)

    units = load_units(corpus_name)
    print(f"第 {volume} 冊，語料 {corpus_name}：{len(units)} 個候選單元")

    # One pass over the distinct written forms, then everything else is lookups.
    memo: dict[str, dict[str, Any]] = {}

    def reading(word: str) -> dict[str, Any]:
        found = memo.get(word)
        if found is None:
            found = word_reading(word, corpus, tagger)
            memo[word] = found
        return found

    scored: list[tuple[Unit, set[tuple[int, int]], tuple[int, int]]] = []
    rejected: Counter[str] = Counter()
    for unit in units:
        readings = [reading(word) for word in unit.words]
        if any(not row["attested"] or not row["parts"] for row in readings):
            rejected["語料查無此形"] += 1
            continue
        lemma_groups = [frozenset(
            lemma for part in row["parts"] for lemma in part["lemmas"]
        ) for row in readings]
        proper = [tagger.is_proper(row["key"]) for row in readings]
        verbal = [tagger.is_verbal(group) for group in lemma_groups]
        reason = printable_reason(unit, lemma_groups, proper, verbal)
        if reason:
            rejected[reason] += 1
            continue
        ready = (0, 0)
        entries_hit: set[tuple[int, int]] = set()
        for row in readings:
            for part in row["parts"]:
                stamp = part_available(part, lemma_first, key_first)
                ready = max(ready, stamp)
                entries_hit |= key_entries.get(part["key"], set())
                for lemma in part["lemmas"]:
                    entries_hit |= lemma_entries.get(lemma, set())
        if ready == NEVER:
            rejected["含未收錄的詞"] += 1
            continue
        if ready[0] > volume:
            rejected["跨冊詞彙"] += 1
            continue
        scored.append((unit, entries_hit, ready))

    by_ready: dict[tuple[int, int], list[tuple[Unit, set[tuple[int, int]]]]] = defaultdict(list)
    for unit, hits, ready in scored:
        by_ready[ready].append((unit, hits))
    print(f"可印單元 {len(scored)}；退回 " + "、".join(
        f"{reason} {count}" for reason, count in rejected.most_common()
    ))

    lessons_out: list[dict[str, Any]] = []
    used_refs: set[str] = set()
    available: list[tuple[Unit, set[tuple[int, int]]]] = []
    short: list[int] = []
    no_anchor_note = "本課無可用經典原句，十題全由自撰題補"
    for lesson in range(1, 51):
        if args.lesson and lesson != args.lesson:
            continue
        available = [row for stamp, rows in by_ready.items()
                     if stamp <= (volume, lesson) for row in rows]
        lesson_keys = {entry.key for entry in entries
                       if entry.volume == volume and entry.lesson == lesson}
        chosen = select(available, lesson_keys, used_refs)
        items: list[dict[str, Any]] = []
        for number, (unit, hits) in enumerate(chosen, start=1):
            used_refs.add(unit.ref)
            items.append(
                {
                    "no": number,
                    "kind": "quoted",
                    "uid": unit.uid,
                    "ref": unit.source,
                    "clause": None if unit.kind == "verse" else f"{unit.part}/{unit.part_count}",
                    "text": unit.text,
                    "wordCount": unit.word_count,
                    "targetWords": [
                        entry.public_record() for entry in entries
                        if entry.key in (hits & lesson_keys)
                    ],
                    # Where a published rendering would be looked up, if an
                    # answer key is ever made.  Not a translation, and not a
                    # promise that one exists.
                    "answerKeyRef": unit.source if volume == 1 else block_id(unit),
                    "answerKeyScope": "verse" if unit.kind == "verse" else (
                        "verse-containing-clause" if volume == 1
                        else "block-containing-clause"),
                }
            )
        if len(items) < 3:
            short.append(lesson)
        lessons_out.append(
            {
                "lesson": lesson,
                "id": f"lat-v{volume}-lesson-{lesson:02d}",
                "anchors": items,
                "note": no_anchor_note if len(items) < 3 else "",
                "coverage": {
                    "lessonWords": len(lesson_keys),
                    "reachedByAnchors": len({
                        key for item in items for key in (
                            {(row["volume"], row["ordinal"]) for row in item["targetWords"]}
                        )
                    }),
                },
            }
        )

    total = sum(len(row["anchors"]) for row in lessons_out)
    print(f"挖到 {total} 題 / {len(lessons_out)} 課")
    if short:
        print(f"不足三題引用、需以自撰題補滿的課：{short}")

    payload = {
        "schemaVersion": "1.0.0",
        "language": "Ecclesiastical Latin",
        "languageCode": "lat",
        "volume": volume,
        "generatedOn": date.today().isoformat(),
        "direction": "original-to-chinese",
        "itemsPerLesson": 10,
        "policy": {
            "role": "十題中的三題引用；其餘七題由作者自撰，機器閘同一套。",
            "composition": "none",
            "unknownWords": "不允許：題目每個詞都須已教過（含附錄專名／數字／親屬／曆法）。",
            "chinese": "練習題不附中文（擁有者 2026-09-11 裁定）；中譯只給讀物。"
                       "answerKeyRef 只記出處，供日後編解答本用。",
            "shortLessons": "定錨不足三題者以自撰題補滿十題，該課註明無可用經典原句。",
        },
        "corpus": {
            "attestation": corpora_for(volume),
            "mined": corpus_name,
        },
        "counts": {
            "lessons": len(lessons_out),
            "anchors": total,
            "lessonsShortOfThree": short,
        },
        "lessons": lessons_out,
    }
    for row in lessons_out[:3]:
        print(f"  L{row['lesson']:02d} {len(row['anchors'])} 題，"
              f"練到 {row['coverage']['reachedByAnchors']}/{row['coverage']['lessonWords']}")
        for item in row["anchors"][:2]:
            print(f"     {item['ref']}　{item['text']}")

    if args.write:
        path = OUTPUT_FILE.with_name(f"exercises-v{volume}.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"寫入 {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
