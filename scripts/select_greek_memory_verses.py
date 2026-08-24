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
VOCAB = ROOT / "data" / "originalReaders" / "vocabulary" / "greek-2000.json"
OUTPUT = CACHE / "memory-verses.json"
CANDIDATES_OUT = CACHE / "memory-candidates.json"

# 上冊 only.  下冊's two sentences per lesson come from the patristic and church
# documents, and are chosen by select_greek_memory_sentences.py.
VOLUME = 1
LESSON_COUNT = 50
# Lessons 1-25 read the New Testament and 26-50 the Greek Old Testament, so a
# memory verse is drawn from the same half's corpus as that lesson's chapter.
# Handing lesson three a Septuagint verse would set Hebraic syntax against a
# vocabulary list that has not left Mounce's first sixty words.
NT_LESSON_LAST = 25
DIVINE_FOLDED: set[str] = set()
PER_LESSON = 2

MIN_WORDS = 4
MAX_WORDS = 15

# Which books each corpus may draw on.  The New Testament is the whole SBLGNT;
# the rest are the books the twenty-five chapters already read, so a memory
# verse never sends the learner to an edition the reader does not carry.
NT_BOOKS = list(gs.SBLGNT_BOOKS)
LXX_BOOKS = ["Gen", "Exod", "Deut", "Ruth", "1Kgs", "Ps", "Prov", "Isa", "Jer", "Ezek", "Jonah"]
DEUTERO_BOOKS = ["TobS", "Jdt", "Wis", "Sir", "2Macc"]
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
GREEK_CAPITAL_RE = re.compile(r"[Ͱ-Ϣ᾿-῟ἈΆᾺ-ῌ]")
# The same editorial markers the chapter plan strips: they are apparatus, not
# Greek, and a memory verse must never be printed with them.
SIGLA_RE = re.compile(r"[⸀⸁⸂⸃⸄⸅⸆⸇⸈⸉⸊⸋⸌⸍]")
BRACKET_RE = re.compile(r"[\[\]]")
NUMERAL_RE = re.compile(r"\d")
# A verse that is a list of names or numbers is unmemorable however well it
# scores, and so is one that opens mid-sentence.
LIST_MARKERS = ("υἱὸς", "υἱοῦ", "ἐγέννησεν", "ἔτη", "χιλιάδες")
# Compile from normalised text.  Greek literals in this file are stored
# decomposed while the verse text is normalised to NFC, so an un-normalised
# pattern silently never matches - which is why every memorability flag came
# back empty on the first hundred verses.
# References whose Chinese cannot be paired by verse number.  Each is a known
# textual fact, not a gap waiting to be filled: Sirach 30-36 is transposed in the
# Greek manuscript order Swete prints; the reader's Tobit is Sinaiticus (GII)
# while the 1933 Anglican follows GI; and the Septuagint merges MT 9+10 and
# splits MT 116 and 147.
SIRACH_TRANSPOSED = range(30, 37)
TOBIT_PAIRED_CHAPTERS = {1}
PSALM_UNPAIRABLE = {9, 113, 114, 115, 146, 147}


def _chinese_counts() -> dict[tuple[str, int], int]:
    """Verse counts of the Chinese deuterocanon already exported, if any."""
    path = CACHE / "deuterocanon-zh.json"
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        (book["ref"].split(".")[0], book["chapter"]): book["verseCount"]
        for book in payload["books"]
    }


_CHINESE_COUNTS = None


def counts_agree(book: str, chapter: int, greek_count: int) -> bool:
    """Whether the two editions divide this chapter the same way.

    Where they do not, the verse numbers point at different text and the pair
    would be wrong however good the Greek is, so the verse never enters the pool.
    """
    global _CHINESE_COUNTS
    if _CHINESE_COUNTS is None:
        _CHINESE_COUNTS = _chinese_counts()
    chinese = _CHINESE_COUNTS.get((book, chapter))
    return chinese is None or chinese == greek_count


# Divine names are not a narrative signal - "凡事謝恩，因為這是上帝在基督耶穌裏
# 向你們所定的旨意" is one of the best verses in the reader, and an earlier
# version of this penalty pushed it down for containing Χριστῷ Ἰησοῦ.  Only
# names of people and places count towards it.
DIVINE_NAMES = {
    "θεός",
    "θεοῦ",
    "θεῷ",
    "θεόν",
    "κύριος",
    "κυρίου",
    "κυρίῳ",
    "κύριον",
    "κύριε",
    "χριστός",
    "χριστοῦ",
    "χριστῷ",
    "χριστόν",
    "ἰησοῦς",
    "ἰησοῦ",
    "ἰησοῦν",
    "πνεῦμα",
    "πνεύματος",
    "πνεύματι",
    "ὕψιστος",
    "ὑψίστου",
    "ὑψίστῳ",
}


def pairable(book: str, chapter: int) -> bool:
    if book == "Sir":
        return chapter not in SIRACH_TRANSPOSED
    if book == "TobS":
        return chapter in TOBIT_PAIRED_CHAPTERS
    if book == "Ps":
        return chapter not in PSALM_UNPAIRABLE
    # Everything else is asked of the one shared crosswalk rather than listed
    # again here.  It already knows that Septuagint Jeremiah 51 is split across
    # two Hebrew chapters and that Proverbs is reordered from 24:23 on, and a
    # second list would be the place where the two answers drift apart.
    from export_reader_rcuv2010_greek import target_reference

    try:
        target_reference(book, chapter, 1)
    except LookupError:
        return False
    return True


OPENING_FORMULA_RE = re.compile(
    unicodedata.normalize("NFC", r"^(καὶ\s+)?(\S+\s+){0,2}(εἶπεν|ἐγένετο|ἀπεκρίθη|ἔφη|λέγει|ἐλάλησεν)\b")
)


def load_vocabulary() -> dict[int, list[dict]]:
    payload = json.loads(VOCAB.read_text(encoding="utf-8"))
    by_lesson: dict[int, list[dict]] = {}
    for entry in payload["entries"]:
        if entry.get("volume") != VOLUME:
            continue
        by_lesson.setdefault(entry["lesson"], []).append(entry)
    if sorted(by_lesson) != list(range(1, LESSON_COUNT + 1)):
        raise ValueError(f"上冊應有 {LESSON_COUNT} 課詞彙，實得 {len(by_lesson)} 課")
    return by_lesson


def lesson_corpora(lesson: int) -> set[str]:
    if lesson <= NT_LESSON_LAST:
        return {"new-testament"}
    return {"septuagint", "deuterocanonical", "pseudepigrapha"}


def vocabulary_keys(entry: dict) -> set[str]:
    """Every folded spelling that should count as this vocabulary item."""
    keys = {fold(entry["headword"]), fold(entry["lemma"])}
    resolution = entry.get("lexiconResolution") or {}
    for field in ("sblgntLemma", "strongsLemma"):
        if resolution.get(field):
            keys.add(fold(resolution[field]))
    return {key for key in keys if key}


def verse_pool() -> list[dict]:
    if not DIVINE_FOLDED:
        DIVINE_FOLDED.update(fold(name) for name in DIVINE_NAMES)
    pool = []
    for book in NT_BOOKS + LXX_BOOKS + DEUTERO_BOOKS + PSEUDEPIGRAPHA_BOOKS:
        corpus = CORPUS_OF[book]
        try:
            verses = gs._sblgnt_book(book) if gs.is_new_testament(book) else gs._swete_book_cached(book)
        except (FileNotFoundError, KeyError):
            continue
        chapter_lengths: dict[int, int] = {}
        for verse in verses:
            chapter_lengths[verse.chapter] = chapter_lengths.get(verse.chapter, 0) + 1
        for verse in verses:
            if not pairable(book, verse.chapter):
                continue
            if corpus == "deuterocanonical" and not counts_agree(
                book, verse.chapter, chapter_lengths[verse.chapter]
            ):
                continue
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
                    # A capital mid-verse usually marks a name, but it also
                    # opens quoted speech - "αὐτῇ· Ἀγαπήσεις τὸν πλησίον σου"
                    # is the commandment to love your neighbour, not a name.
                    # Capitals that follow sentence or quotation punctuation
                    # are therefore not counted.
                    "properNames": sum(
                        1
                        for index, token in enumerate(tokens)
                        if index
                        and token.text[:1].isupper()
                        and not tokens[index - 1].text.endswith(("·", ":", ".", ";", "—"))
                        and fold(token.text.strip(".,·;:!?—")) not in DIVINE_FOLDED
                    ),
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
    names = candidate.get("properNames", 0)
    if names:
        flags.append("proper_names")
        value -= 0.7 * min(names, 3)
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
        allowed = lesson_corpora(lesson)
        scored = []
        for candidate in pool:
            if candidate["ref"] in used_refs:
                continue
            if candidate["corpus"] not in allowed:
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
        "schemaVersion": "2.0.0",
        "language": "Koine Greek",
        "languageCode": "grc",
        "volume": VOLUME,
        "volumeTitle": "上冊《新約與七十士譯本》",
        "corpusByHalf": {
            "1-25": "new-testament",
            "26-50": "septuagint / deuterocanonical / pseudepigrapha",
        },
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
