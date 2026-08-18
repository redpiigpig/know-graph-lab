#!/usr/bin/env python3
"""Loaders for the 25 patristic / creed / decree readings of the Greek reader.

Four frozen source families, each with its own provenance and its own reason
for being trusted:

* ``apostolic_fathers`` -- Open Apostolic Fathers (Tauber & Macdonald 2019,
  CC BY-SA 4.0), the corrected Lake text, one ``chapter.verse text`` line per
  segment.
* ``first1k`` -- Open Greek and Latin *First Thousand Years of Greek*
  (CC BY-SA 4.0) TEI, addressed by chapter and section.
* ``creed`` -- the Greek versions already carried by ``data/creeds/**`` in this
  repository, whose own provenance (Schaff, DCO) is recorded per creed file.
* ``goarch`` -- Greek liturgical texts from glt.goarch.org, used for the
  Paschal homily, Vespers hymnody and the Divine Liturgy appendix.

Every loader returns ordered segments with a stable reference, so an excerpt is
always addressable and can never be silently relabelled as a complete work.
"""

from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
AF_DIR = CACHE / "sources" / "apostolic-fathers"
FIRST1K_DIR = CACHE / "sources" / "first1k"
LITURGY_DIR = CACHE / "sources" / "liturgy"
CREEDS_DIR = ROOT / "data" / "creeds"

TEI_NS = {"tei": "http://www.tei-c.org/ns/1.0"}
GREEK_RE = re.compile(r"[Ͱ-Ͽἀ-῿]")

AF_EDITION = (
    "Open Apostolic Fathers, ed. James Tauber & Seumas Macdonald (2019), "
    "corrected text of Kirsopp Lake"
)
AF_URL = "https://github.com/jtauber/apostolic-fathers"
FIRST1K_EDITION = "Open Greek and Latin, First Thousand Years of Greek (First1KGreek)"
FIRST1K_URL = "https://github.com/OpenGreekAndLatin/First1KGreek"
GOARCH_EDITION = "Greek Liturgical Texts, ed. Seraphim Dedes (Greek Orthodox Archdiocese of America)"
GOARCH_URL = "https://glt.goarch.org/"


class Segment(NamedTuple):
    ref: str
    text: str


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


# --------------------------------------------------------------------------
# Open Apostolic Fathers
# --------------------------------------------------------------------------

def load_apostolic_father(stem: str) -> list[Segment]:
    path = AF_DIR / f"{stem}.txt"
    if not path.exists():
        raise FileNotFoundError(f"missing frozen Apostolic Fathers source: {path}")
    segments = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        ref, _, text = line.partition(" ")
        # 1 Clement and the Shepherd label a superscription "SB.1", so the
        # reference is not always numeric; it must still be a bare token.
        if not re.fullmatch(r"[A-Za-z0-9.]+", ref) or not any(c.isdigit() for c in ref):
            raise ValueError(f"unexpected line in {path.name}: {line[:60]!r}")
        segments.append(Segment(ref, _clean(text)))
    if not segments:
        raise ValueError(f"empty Apostolic Fathers source: {path}")
    return segments


def slice_chapters(segments: list[Segment], first: int, last: int) -> list[Segment]:
    """Keep whole chapters ``first``..``last`` of a ``chapter.verse`` work."""
    kept = [
        s for s in segments
        if s.ref.split(".")[0].isdigit() and first <= int(s.ref.split(".")[0]) <= last
    ]
    if not kept:
        raise LookupError(f"chapters {first}-{last} are absent from this work")
    return kept


# --------------------------------------------------------------------------
# First1KGreek TEI
# --------------------------------------------------------------------------

def load_first1k(filename: str, first_chapter: int = 0, last_chapter: int = 0) -> list[Segment]:
    path = FIRST1K_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"missing frozen First1KGreek source: {path}")
    # Some First1KGreek files carry undefined HTML entities left over from the
    # OCR pipeline, which the strict stdlib parser refuses.  lxml in recovery
    # mode reads them; the stdlib parser stays as the fallback so the module
    # still works where lxml is unavailable.
    try:
        from lxml import etree as LET

        tree = LET.parse(str(path), LET.XMLParser(recover=True, resolve_entities=False))
    except ImportError:
        tree = ET.parse(path)
    edition = tree.find(".//tei:text/tei:body/tei:div[@type='edition']", TEI_NS)
    if edition is None:
        raise ValueError(f"no edition division in {path.name}")
    segments: list[Segment] = []
    for chapter in edition.findall("tei:div[@subtype='chapter']", TEI_NS):
        number = int(chapter.get("n", "0"))
        if first_chapter and not (first_chapter <= number <= last_chapter):
            continue
        sections = chapter.findall("tei:div[@subtype='section']", TEI_NS)
        if sections:
            for section in sections:
                text = _clean("".join(section.itertext()))
                if text:
                    segments.append(Segment(f"{number}.{section.get('n')}", text))
        else:
            text = _clean("".join(chapter.itertext()))
            if text:
                segments.append(Segment(str(number), text))
    if not segments:
        raise LookupError(f"{filename}: chapters {first_chapter}-{last_chapter} produced nothing")
    return segments


# --------------------------------------------------------------------------
# Repository creed files
# --------------------------------------------------------------------------

# A creed version either inlines its text in a template literal or points at a
# scraped file through ``textKey``.  Both forms have to be followed, because the
# council files use the second one exclusively.
_VERSION_RE = re.compile(r"\{\s*lang:\s*'(?P<lang>[^']+)',(?P<body>.*?)\n    \},", re.S)
_INLINE_RE = re.compile(r"text:\s*`(?P<text>.*?)`", re.S)
_TEXTKEY_RE = re.compile(r"textKey:\s*'(?P<key>[^']+)'")
_SOURCE_RE = re.compile(r"source:\s*'(?P<source>[^']*)'")


def load_creed_greek(relative_path: str) -> tuple[list[Segment], str]:
    """Return the Greek version of a repository creed, split into lines."""
    path = CREEDS_DIR / relative_path
    if not path.exists():
        raise FileNotFoundError(f"missing creed file: {path}")
    document = path.read_text(encoding="utf-8")
    for match in _VERSION_RE.finditer(document):
        if match.group("lang") != "grc":
            continue
        body = match.group("body")
        source_match = _SOURCE_RE.search(body)
        source = source_match.group("source") if source_match else ""
        inline = _INLINE_RE.search(body)
        raw = inline.group("text") if inline and inline.group("text").strip() else ""
        if not raw:
            key_match = _TEXTKEY_RE.search(body)
            if not key_match:
                raise LookupError(f"{relative_path}: Greek version has neither text nor textKey")
            scraped = path.parent / path.stem.split("-")[0] / f"{key_match.group('key')}.txt"
            if not scraped.exists():
                raise FileNotFoundError(f"missing scraped Greek text: {scraped}")
            raw = "\n".join(
                line
                for line in scraped.read_text(encoding="utf-8").splitlines()
                if not line.startswith("#")
            )
        lines = [_clean(line) for line in raw.split("\n")]
        lines = [line for line in lines if line and GREEK_RE.search(line)]
        if not lines:
            raise LookupError(f"{relative_path}: Greek version resolved to no Greek text")
        segments = [Segment(str(index), line) for index, line in enumerate(lines, start=1)]
        return segments, source
    raise LookupError(f"{relative_path} carries no Greek version")


# --------------------------------------------------------------------------
# glt.goarch.org liturgical HTML
# --------------------------------------------------------------------------

def _goarch_text(filename: str) -> str:
    path = LITURGY_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"missing frozen liturgical source: {path}")
    body = path.read_text(encoding="utf-8")
    body = re.sub(r"<script\b.*?</script>", " ", body, flags=re.S | re.I)
    body = re.sub(r"<style\b.*?</style>", " ", body, flags=re.S | re.I)
    # Block-level tags become paragraph breaks; inline tags simply disappear,
    # because this site wraps individual words in their own <span> elements and
    # a naive tag-to-newline conversion shatters every sentence.
    body = re.sub(r"</?(p|div|tr|table|br|h[1-6]|li)\b[^>]*>", "\n", body, flags=re.I)
    body = re.sub(r"<[^>]+>", "", body)
    return html.unescape(body)


def load_goarch_block(filename: str, start_pattern: str, end_pattern: str) -> list[Segment]:
    """Take the paragraphs between two anchors of a liturgical page."""
    text = _goarch_text(filename)
    start = re.search(start_pattern, text)
    if not start:
        raise LookupError(f"{filename}: start anchor {start_pattern!r} not found")
    tail = text[start.start() :]
    end = re.search(end_pattern, tail[1:])
    if end:
        tail = tail[: end.start() + 1]
    segments = []
    for index, block in enumerate(tail.split("\n"), start=1):
        block = _clean(block)
        if block and GREEK_RE.search(block):
            segments.append(Segment(str(len(segments) + 1), block))
    if not segments:
        raise LookupError(f"{filename}: block between anchors held no Greek")
    return segments
