#!/usr/bin/env python3
"""Choose the hundred memory verses, two for each of the fifty lessons.

A memory verse earns its place by being sayable after the lesson that carries
it: it should be built out of words the learner has just met, short enough to
hold, and a complete sentence rather than a clause torn out of one.

Two matching methods are used, and every verse records which one produced it,
because they are not equally strong:

* ``lemma`` — New Testament verses, where MorphGNT gives the lemma of every
  token, so "this verse uses ἀγάπη" is a fact, not an inference;
* ``surface`` — Septuagint, deuterocanonical and pseudepigraphal verses, where
  the frozen Swete database carries no morphology.  A hit means the *printed
  form* matches the vocabulary headword letter for letter once accents are
  folded away, so the method under-counts and never over-counts.

Scores and the reasons behind them are written out for every candidate that was
considered, not just the winners, so the human review the contract requires has
something to review.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import greek_source_texts as gs
from verify_greek_vocab_lexicon import fold


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
VOCAB = ROOT / "data" / "originalReaders" / "vocabulary" / "greek-1000.json"
OUTPUT = CACHE / "memory-verses.json"
CANDIDATES_OUT = CACHE / "memory-candidates.json"

LESSON_COUNT = 50
PER_LESSON = 2

MIN_WORDS = 4
MAX_WORDS = 15

# Which books each corpus may draw on.  The New Testament is the whole SBLGNT;
# the rest are the books the twenty-five chapters already read, so a memory
# verse never sends the learner to an edition the reader does not carry.
NT_BOOKS = list(gs.SBLGNT_BOOKS)
LXX_BOOKS = ["Gen", "Exod", "Ps", "Isa"]
DEUTERO_BOOKS = ["TobS", "Jdt", "Wis", "Sir"]
PSEUDEPIGRAPHA_BOOKS = ["1En", "PssSol"]

CORPUS_OF = {}
for book in NT_BOOKS:
    CORPUS_OF[book] = "new-testament"
for book in LXX_BOOKS:
    CORPUS_OF[book] = "septuagint"
for book in DEUTERO_BOOKS:
    CORPUS_OF[book] = "deuterocanonical"
for book in PSEUDEPIGRAPHA_BOOKS:
    CORPUS_OF[book] = "pseudepigrapha"

# Floors, not quotas: the reader promised all four corpora, so each must appear,
# but a lesson is never handed a bad verse merely to fill a corpus.
CORPUS_FLOORS = {"septuagint": 15, "deuterocanonical": 10, "pseudepigrapha": 5}

GREEK_RE = re.compile(r"[Ͱ-Ͽἀ-῿]")
# The same editorial markers the chapter plan strips: they are apparatus, not
# Greek, and a memory verse must never be printed with them.
SIGLA_RE = re.compile(r"[⸀⸁⸂⸃⸄⸅⸆⸇⸈⸉⸊⸋⸌⸍]")
BRACKET_RE = re.compile(r"[\[\]]")
NUMERAL_RE = re.compile(r"\d")
# A verse that is a list of names or numbers is unmemorable however well it
# scores, and so is one that opens mid-sentence.
LIST_MARKERS = ("υἱὸς", "υἱοῦ", "ἐγέννησεν", "ἔτη", "χιλιάδες")
OPENING_FORMULA_RE = re.compile(
    r"^(καὶ )?(εἶπεν|ἐγένετο|ἀπεκρίθη|ἔφη|λέγει)", re.I
)


def load_vocabulary() -> dict[int, list[dict]]:
    entries = json.loads(VOCAB.read_text(encoding="utf-8"))
    by_lesson: dict[int, list[dict]] = {}
    for entry in entries:
        by_lesson.setdefault(entry["lesson"], []).append(entry)
    return by_lesson


def vocabulary_keys(entry: dict) -> set[str]:
    """Every folded spelling that should count as this vocabulary item."""
    keys = {fold(entry["headword"]), fold(entry["lemma"])}
    resolution = entry.get("lexiconResolution") or {}
    for field in ("sblgntLemma", "strongsLemma"):
        if resolution.get(field):
            keys.add(fold(resolution[field]))
    return {key for key in keys if key}


def verse_pool() -> list[dict]:
    pool = []
    for book in NT_BOOKS + LXX_BOOKS + DEUTERO_BOOKS + PSEUDEPIGRAPHA_BOOKS:
        corpus = CORPUS_OF[book]
        try:
            verses = gs._sblgnt_book(book) if gs.is_new_testament(book) else gs._swete_book_cached(book)
        except (FileNotFoundError, KeyError):
            continue
        for verse in verses:
            tokens = [token for token in verse.tokens if GREEK_RE.search(token.text)]
            if not (MIN_WORDS <= len(tokens) <= MAX_WORDS):
                continue
            text = " ".join(token.text for token in tokens)
            if BRACKET_RE.search(text) or NUMERAL_RE.search(text):
                continue
            if any(marker in text for marker in LIST_MARKERS):
                continue
            if gs.is_new_testament(book):
                keys = {fold(token.lemma) for token in tokens if token.lemma}
                method = "lemma"
            else:
                keys = {fold(token.text.strip(".,·;:!?—")) for token in tokens}
                method = "surface"
            pool.append(
                {
                    "ref": verse.ref,
                    "book": book,
                    "chapter": verse.chapter,
                    "verse": verse.verse,
                    "corpus": corpus,
                    "wordCount": len(tokens),
                    "sourceText": unicodedata.normalize("NFC", verse.text),
                    "text": unicodedata.normalize(
                        "NFC", re.sub(r"\s{2,}", " ", SIGLA_RE.sub("", verse.text)).strip()
                    ),
                    "keys": keys,
                    "matchMethod": method,
                }
            )
    return pool


def score(candidate: dict, lesson_keys: set[str], known_keys: set[str]) -> dict:
    matched = candidate["keys"] & lesson_keys
    known = candidate["keys"] & known_keys
    coverage = len(known) / max(len(candidate["keys"]), 1)
    # Weight the lesson's own words heavily, cumulative coverage next, and give
    # a mild preference to the middle of the length window, where a verse is
    # long enough to be a sentence and short enough to memorise.
    length_fit = 1.0 - abs(candidate["wordCount"] - 9) / 12
    value = len(matched) * 3.0 + coverage * 4.0 + length_fit
    flags = []
    if OPENING_FORMULA_RE.match(candidate["text"]):
        flags.append("opens_with_narrative_formula")
        value -= 1.5
    if candidate["wordCount"] <= 5:
        flags.append("very_short")
        value -= 0.5
    if candidate["matchMethod"] == "surface":
        # Surface matching cannot see inflected forms, so an equal score means
        # a stronger verse; nudge it up rather than let lemma matching sweep.
        value += 0.6
    return {
        "matchCount": len(matched),
        "matchedTerms": sorted(matched),
        "knownCoverage": round(coverage, 3),
        "lengthFit": round(length_fit, 3),
        "memorabilityFlags": flags,
        "score": round(value, 3),
    }


def select(by_lesson: dict[int, list[dict]], pool: list[dict]) -> tuple[list[dict], list[dict]]:
    chosen: list[dict] = []
    used_refs: set[str] = set()
    corpus_taken: Counter[str] = Counter()
    review_rows: list[dict] = []

    known_keys: set[str] = set()
    lesson_key_sets: dict[int, set[str]] = {}
    for lesson in range(1, LESSON_COUNT + 1):
        keys: set[str] = set()
        for entry in by_lesson.get(lesson, []):
            keys |= vocabulary_keys(entry)
        lesson_key_sets[lesson] = keys

    remaining_lessons = LESSON_COUNT
    for lesson in range(1, LESSON_COUNT + 1):
        known_keys |= lesson_key_sets[lesson]
        lesson_keys = lesson_key_sets[lesson]
        scored = []
        for candidate in pool:
            if candidate["ref"] in used_refs:
                continue
            if not candidate["keys"] & lesson_keys:
                continue
            scored.append((score(candidate, lesson_keys, known_keys), candidate))
        scored.sort(key=lambda pair: pair[0]["score"], reverse=True)
        review_rows.append(
            {
                "lesson": lesson,
                "candidatesConsidered": len(scored),
                "top": [
                    {"ref": c["ref"], "corpus": c["corpus"], **s} for s, c in scored[:8]
                ],
            }
        )

        slots = []
        # Slot one takes the best verse outright.
        if scored:
            slots.append(scored[0])
        # Slot two prefers a corpus still short of its floor, so the promised
        # Septuagint, deuterocanonical and pseudepigraphal verses actually
        # appear instead of being crowded out by the much larger New Testament.
        needed = [
            corpus for corpus, floor in CORPUS_FLOORS.items()
            if corpus_taken[corpus] < floor
        ]
        second = None
        if needed:
            for entry in scored:
                if entry[1]["corpus"] in needed and entry[1]["ref"] != slots[0][1]["ref"]:
                    second = entry
                    break
        if second is None:
            for entry in scored[1:]:
                if entry[1]["ref"] != slots[0][1]["ref"]:
                    second = entry
                    break
        if second is not None:
            slots.append(second)

        for slot_index, (verse_score, candidate) in enumerate(slots[:PER_LESSON], start=1):
            used_refs.add(candidate["ref"])
            corpus_taken[candidate["corpus"]] += 1
            chosen.append(
                {
                    "lesson": lesson,
                    "slot": slot_index,
                    "ref": candidate["ref"],
                    "book": candidate["book"],
                    "chapter": candidate["chapter"],
                    "verse": candidate["verse"],
                    "corpus": candidate["corpus"],
                    "matchMethod": candidate["matchMethod"],
                    "wordCount": candidate["wordCount"],
                    "text": candidate["text"],
                    "translationZh": "",
                    "reviewStatus": "pending_human_review",
                    **verse_score,
                }
            )
        remaining_lessons -= 1
    return chosen, review_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="挑選希臘文讀本的 100 個記憶單元")
    parser.add_argument("--write", action="store_true", help="寫出 memory-verses.json")
    args = parser.parse_args()

    by_lesson = load_vocabulary()
    pool = verse_pool()
    print(f"候選經節池 {len(pool)} 節")
    chosen, review = select(by_lesson, pool)

    corpus_counts = Counter(item["corpus"] for item in chosen)
    method_counts = Counter(item["matchMethod"] for item in chosen)
    per_lesson = Counter(item["lesson"] for item in chosen)
    short = [lesson for lesson in range(1, LESSON_COUNT + 1) if per_lesson[lesson] < PER_LESSON]

    for item in chosen[:6]:
        print(
            f"  第 {item['lesson']:>2d} 課 slot{item['slot']}  {item['ref']:<14s}"
            f" {item['corpus']:<17s} 命中 {item['matchCount']} 詞  {item['text'][:60]}"
        )
    print(f"  ...共 {len(chosen)} 節")
    print(f"  語料分佈 {dict(corpus_counts)}")
    print(f"  比對方式 {dict(method_counts)}")
    if short:
        print(f"  ⚠ 湊不滿兩節的課次：{short}")

    payload = {
        "schemaVersion": "1.0.0",
        "language": "New Testament Greek",
        "languageCode": "grc",
        "target": LESSON_COUNT * PER_LESSON,
        "selected": len(chosen),
        "perLesson": PER_LESSON,
        "matchMethods": {
            "lemma": "新約：MorphGNT 逐詞詞位，精確比對",
            "surface": "七十士／次經／偽經：Swete 無形態標註，只比對印刷字形，寧可少算不多算",
        },
        "corpusFloors": CORPUS_FLOORS,
        "corpusCounts": dict(corpus_counts),
        "lessonsShort": short,
        "reviewNote": "全部標 pending_human_review；依約定須人工複核可記憶性後才可定案。",
        "verses": chosen,
    }

    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        CANDIDATES_OUT.write_text(
            json.dumps({"schemaVersion": "1.0.0", "lessons": review}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"已寫出 {OUTPUT}")
        print(f"已寫出 {CANDIDATES_OUT}")
    else:
        print("（未寫檔；加 --write 才會輸出）")


if __name__ == "__main__":
    main()
