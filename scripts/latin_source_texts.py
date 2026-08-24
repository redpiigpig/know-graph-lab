#!/usr/bin/env python3
"""Frozen Latin corpora for the ecclesiastical Latin reader.

Two families of text feed this reader and they are kept apart on purpose.

The Vulgate arrives as eBible.org's USFX transcription of the Clementine
edition.  That file carries the Glossa Ordinaria in ``<f>`` footnote elements
interleaved with the verse text -- Genesis 1:1 is followed immediately by a
paragraph of Augustine -- so a naive text sweep would silently teach the gloss
as if it were scripture.  Every footnote subtree is dropped before a verse is
recorded.

The church corpus is already in the repository: ninety-six popes' Latin under
``data/encyclicals`` and the councils under ``data/creeds``.  Those files were
gathered for the parallel readers, so each one already has a Chinese
counterpart, which is why the reader draws its later readings from them rather
than re-fetching the same documents from vatican.va.

Clementine orthography is kept exactly as printed -- ``cælum`` keeps its
ligature, ``ejus`` keeps its j -- and a separate folded form is provided for
counting and lookup, because a reader that silently modernises its source text
cannot be checked against the edition it claims to print.
"""
from __future__ import annotations

import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
USFX = CACHE / "latVUC" / "latVUC_usfx.xml"
ENCYCLICALS = ROOT / "data" / "encyclicals"
CREEDS = ROOT / "data" / "creeds"

# Elements whose entire subtree is apparatus rather than text.
DROP = {"f", "x", "fr", "fk", "ft", "fv", "xo", "xt", "note", "ref"}

LIGATURES = {"æ": "ae", "Æ": "Ae", "œ": "oe", "Œ": "Oe"}


def fold(word: str) -> str:
    """Spelling-insensitive key for counting: ligatures, j/v, case, accents."""
    text = unicodedata.normalize("NFD", word)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    for src, dst in LIGATURES.items():
        text = text.replace(src, dst)
    text = text.lower().replace("j", "i").replace("v", "u")
    return text


def words(text: str) -> list[str]:
    return [w for w in re.findall(r"[A-Za-zÀ-ÿæœÆŒ]+", text) if w]


def vulgate_verses() -> dict[str, str]:
    """Return ``{'GEN.1.1': 'In principio creavit Deus cælum et terram.'}``."""
    verses: dict[str, str] = {}
    current: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        if current and buffer:
            joined = re.sub(r"\s+", " ", "".join(buffer)).strip()
            if joined:
                verses[current] = joined

    depth_skipped = 0
    for event, elem in ET.iterparse(USFX, events=("start", "end")):
        tag = elem.tag
        if event == "start":
            if tag in DROP:
                depth_skipped += 1
                continue
            if depth_skipped:
                continue
            if tag == "v":
                flush()
                current = elem.get("bcv")
                buffer = []
            elif tag == "ve":
                flush()
                current = None
                buffer = []
        else:  # end
            if tag in DROP:
                depth_skipped -= 1
                # The tail of a footnote belongs to the verse again.
                if not depth_skipped and current and elem.tail:
                    buffer.append(elem.tail)
                continue
            if depth_skipped:
                continue
            if current:
                if elem.text and tag not in {"v", "ve"}:
                    buffer.append(elem.text)
                if elem.tail:
                    buffer.append(elem.tail)
            elem.clear()
    flush()
    return verses


def vulgate_chapters() -> dict[tuple[str, int], dict[int, str]]:
    chapters: dict[tuple[str, int], dict[int, str]] = {}
    for ref, text in vulgate_verses().items():
        book, chapter, verse = ref.split(".")
        chapters.setdefault((book, int(chapter)), {})[int(verse)] = text
    return chapters


def church_documents() -> list[dict]:
    """Latin documents already in the repository, with their Chinese status."""
    found: list[dict] = []
    for base, kind in ((ENCYCLICALS, "papal"), (CREEDS, "council")):
        for latin in sorted(base.rglob("*latin.txt")):
            slug = latin.name[: -len("-latin.txt")]
            chinese = latin.with_name(f"{slug}-chinese.txt")
            text = latin.read_text(encoding="utf-8", errors="replace")
            found.append(
                {
                    "kind": kind,
                    "slug": slug,
                    "group": latin.parent.name,
                    "path": str(latin.relative_to(ROOT)).replace("\\", "/"),
                    "hasChinese": chinese.exists(),
                    "words": len(words(text)),
                    "text": text,
                }
            )
    return found
