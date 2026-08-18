#!/usr/bin/env python3
"""Frozen Greek source-text loaders for the 50-lesson New Testament Greek reader.

Two immutable bases, kept strictly apart:

* ``SBLGNT`` -- the SBL Greek New Testament as analysed by MorphGNT.  Each line
  carries book/chapter/verse, part of speech, parsing, the *printed* form with
  its punctuation, the bare word, the normalised word and the lemma, so the
  reader can tokenise exactly the row of Greek the learner sees and still link
  every token to a lemma.
* ``Swete`` -- Henry Barclay Swete's Cambridge Septuagint (1909-1930) as a
  word-indexed database.  One edition covers the LXX, every deuterocanonical
  book, the Psalms of Solomon and the Greek 1 Enoch, so the reader needs no
  second Greek Old Testament and inherits no CCAT declaration requirement.

Nothing here normalises, de-accents or unbrackets anything.  Editorial layers
belong downstream; this module only reads the frozen sources.
"""

from __future__ import annotations

import hashlib
from functools import lru_cache
from pathlib import Path
from typing import Iterator, NamedTuple


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
SBLGNT_DIR = CACHE / "sources" / "sblgnt"
SWETE_DIR = CACHE / "sources" / "swete"

SBLGNT_EDITION = "SBL Greek New Testament (ed. Michael W. Holmes), MorphGNT analysis"
SBLGNT_VERSION = "MORPHGNT-SBLGNT"
SBLGNT_URL = "https://github.com/morphgnt/sblgnt"

SWETE_EDITION = (
    "Henry Barclay Swete, The Old Testament in Greek according to the Septuagint "
    "(Cambridge, 1909-1930)"
)
SWETE_VERSION = "SWETE-LXX-1930"
SWETE_URL = "https://github.com/eliranwong/LXX-Swete-1930"

# MorphGNT numbers the books 01-27 inside the line and 61-87 in the file name.
SBLGNT_BOOKS: dict[str, tuple[int, str]] = {
    "Matt": (1, "61-Mt"), "Mark": (2, "62-Mk"), "Luke": (3, "63-Lk"),
    "John": (4, "64-Jn"), "Acts": (5, "65-Ac"), "Rom": (6, "66-Ro"),
    "1Cor": (7, "67-1Co"), "2Cor": (8, "68-2Co"), "Gal": (9, "69-Ga"),
    "Eph": (10, "70-Eph"), "Phil": (11, "71-Php"), "Col": (12, "72-Col"),
    "1Thess": (13, "73-1Th"), "2Thess": (14, "74-2Th"), "1Tim": (15, "75-1Ti"),
    "2Tim": (16, "76-2Ti"), "Titus": (17, "77-Tit"), "Phlm": (18, "78-Phm"),
    "Heb": (19, "79-Heb"), "Jas": (20, "80-Jas"), "1Pet": (21, "81-1Pe"),
    "2Pet": (22, "82-2Pe"), "1John": (23, "83-1Jn"), "2John": (24, "84-2Jn"),
    "3John": (25, "85-3Jn"), "Jude": (26, "86-Jud"), "Rev": (27, "87-Re"),
}

# Swete's own book codes, mapped to the OSIS-style codes this reader uses.
SWETE_BOOKS: dict[str, str] = {
    "Gen": "Gen", "Exod": "Exo", "Lev": "Lev", "Num": "Num", "Deut": "Deu",
    "Josh": "Jos", "Judg": "Jdg", "Ruth": "Rut", "1Sam": "1Sa", "2Sam": "2Sa",
    "1Kgs": "1Ki", "2Kgs": "2Ki", "1Chr": "1Ch", "2Chr": "2Ch", "1Esd": "1Es",
    "Ezra": "Ezr", "Neh": "Neh", "Ps": "Psa", "Prov": "Pro", "Eccl": "Ecc",
    "Song": "Sol", "Job": "Job", "Wis": "Wis", "SirProl": "Sip", "Sir": "Sir",
    "Esth": "Est", "Jdt": "Jdt", "TobBA": "Tob", "TobS": "Tbs", "Hos": "Hos",
    "Amos": "Amo", "Mic": "Mic", "Joel": "Joe", "Obad": "Oba", "Jonah": "Jon",
    "Nah": "Nah", "Hab": "Hab", "Zeph": "Zep", "Hag": "Hag", "Zech": "Zec",
    "Mal": "Mal", "Isa": "Isa", "Jer": "Jer", "Bar": "Bar", "Lam": "Lam",
    "EpJer": "Epj", "Ezek": "Eze", "Dan": "Dan", "DanTh": "Dat", "Sus": "Sus",
    "SusTh": "Sut", "Bel": "Bel", "BelTh": "Bet", "1Macc": "1Ma", "2Macc": "2Ma",
    "3Macc": "3Ma", "4Macc": "4Ma", "PssSol": "Pss", "1En": "1En", "Odes": "Ode",
}


class Token(NamedTuple):
    """One printed word of the source text."""

    text: str          # exactly as printed, punctuation included
    word: str          # the bare word
    normalized: str    # accent-normalised form, where the source supplies one
    lemma: str         # dictionary form, where the source supplies one
    pos: str
    parsing: str


class Verse(NamedTuple):
    osis_book: str
    chapter: int
    verse: int
    ref: str
    text: str
    tokens: tuple[Token, ...]


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


# --------------------------------------------------------------------------
# SBLGNT / MorphGNT
# --------------------------------------------------------------------------

def sblgnt_path(osis_book: str) -> Path:
    if osis_book not in SBLGNT_BOOKS:
        raise KeyError(f"{osis_book} is not a New Testament book")
    return SBLGNT_DIR / f"{SBLGNT_BOOKS[osis_book][1]}-morphgnt.txt"


@lru_cache(maxsize=None)
def _sblgnt_book(osis_book: str) -> tuple[Verse, ...]:
    path = sblgnt_path(osis_book)
    if not path.exists():
        raise FileNotFoundError(f"missing frozen SBLGNT source: {path}")
    grouped: dict[tuple[int, int], list[Token]] = {}
    order: list[tuple[int, int]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 7:
            raise ValueError(f"unexpected MorphGNT line in {path.name}: {line!r}")
        code, pos, parsing, text, word, normalized, lemma = parts
        chapter, verse = int(code[2:4]), int(code[4:6])
        key = (chapter, verse)
        if key not in grouped:
            grouped[key] = []
            order.append(key)
        grouped[key].append(Token(text, word, normalized, lemma, pos, parsing))
    return tuple(
        Verse(
            osis_book=osis_book,
            chapter=chapter,
            verse=verse,
            ref=f"{osis_book}.{chapter}.{verse}",
            text=" ".join(token.text for token in grouped[(chapter, verse)]),
            tokens=tuple(grouped[(chapter, verse)]),
        )
        for chapter, verse in order
    )


# --------------------------------------------------------------------------
# Swete
# --------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _swete_words() -> dict[int, str]:
    path = SWETE_DIR / "01-Swete_word_with_punctuations.csv"
    if not path.exists():
        raise FileNotFoundError(f"missing frozen Swete source: {path}")
    words: dict[int, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        index, word = line.split("\t", 1)
        words[int(index)] = word
    return words


@lru_cache(maxsize=1)
def _swete_refs() -> tuple[tuple[int, str], ...]:
    path = SWETE_DIR / "00-Swete_versification.csv"
    if not path.exists():
        raise FileNotFoundError(f"missing frozen Swete source: {path}")
    refs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        index, ref = line.split("\t")
        refs.append((int(index), ref))
    refs.sort()
    return tuple(refs)


def _swete_book(osis_book: str) -> Iterator[Verse]:
    if osis_book not in SWETE_BOOKS:
        raise KeyError(f"{osis_book} has no Swete book code")
    code = SWETE_BOOKS[osis_book]
    words = _swete_words()
    refs = _swete_refs()
    last_index = max(words)
    prefix = code + "."
    for position, (start, ref) in enumerate(refs):
        if not ref.startswith(prefix):
            continue
        end = refs[position + 1][0] - 1 if position + 1 < len(refs) else last_index
        chapter_part, verse_part = ref[len(prefix):].split(":")
        printed = [words[index] for index in range(start, end + 1) if index in words]
        yield Verse(
            osis_book=osis_book,
            chapter=int(chapter_part),
            verse=int(verse_part),
            ref=f"{osis_book}.{chapter_part}.{verse_part}",
            text=" ".join(printed),
            tokens=tuple(Token(word, word, "", "", "", "") for word in printed),
        )


@lru_cache(maxsize=None)
def _swete_book_cached(osis_book: str) -> tuple[Verse, ...]:
    return tuple(_swete_book(osis_book))


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------

def is_new_testament(osis_book: str) -> bool:
    return osis_book in SBLGNT_BOOKS


def load_chapter(osis_book: str, chapter: int) -> list[Verse]:
    book = _sblgnt_book(osis_book) if is_new_testament(osis_book) else _swete_book_cached(osis_book)
    verses = [verse for verse in book if verse.chapter == chapter]
    if not verses:
        raise LookupError(f"{osis_book} {chapter} is absent from the frozen source")
    return verses


def load_verse(osis_book: str, chapter: int, verse: int) -> Verse:
    for candidate in load_chapter(osis_book, chapter):
        if candidate.verse == verse:
            return candidate
    raise LookupError(f"{osis_book}.{chapter}.{verse} is absent from the frozen source")


def source_metadata(osis_book: str) -> dict[str, str]:
    if is_new_testament(osis_book):
        path = sblgnt_path(osis_book)
        return {
            "source": SBLGNT_EDITION,
            "version": SBLGNT_VERSION,
            "sourceUrl": SBLGNT_URL,
            "sourceFile": str(path.relative_to(ROOT)).replace("\\", "/"),
            "sourceFileSha256": sha256_of(path),
        }
    path = SWETE_DIR / "01-Swete_word_with_punctuations.csv"
    return {
        "source": SWETE_EDITION,
        "version": SWETE_VERSION,
        "sourceUrl": SWETE_URL,
        "sourceFile": str(path.relative_to(ROOT)).replace("\\", "/"),
        "sourceFileSha256": sha256_of(path),
    }
