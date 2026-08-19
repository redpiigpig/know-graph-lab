# -*- coding: utf-8 -*-
"""Source and identity registry for the 14 early-Greek-philosophy hubs.

This module is deliberately data-only.  A Diels ``A`` record is a testimonium;
a ``B`` record is an editor-classified quotation fragment.  Neither is an
authorial manuscript, and the build driver must not silently promote witness
context into the quoted text.
"""
from __future__ import annotations


DIELS_1922_LICENSE = {
    "edition": "Hermann Diels, Die Fragmente der Vorsokratiker, vol. 1 (1922)",
    "transcription": "Open Greek and Latin / First1KGreek",
    "license": "CC BY-SA 4.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
    "repository": "https://github.com/OpenGreekAndLatin/First1KGreek",
}

BURNET_1920_LICENSE = {
    "edition": "John Burnet, Early Greek Philosophy, 3rd ed. (1920)",
    "transcription": "English Wikisource",
    "rights": "public domain",
    "work_url": "https://en.wikisource.org/wiki/Early_Greek_Philosophy",
}

FAIRBANKS_1898_LICENSE = {
    "edition": "Arthur Fairbanks, The First Philosophers of Greece (1898)",
    "rights": "public domain",
    "work_url": "https://www.gutenberg.org/ebooks/78670",
}


def _hub(
    index: int,
    slug: str,
    name_zh: str,
    name_en: str,
    dk_chapter: int | None,
    *,
    source_status: str,
    burnet_page: str | None = None,
    greek_tei: str | None = None,
) -> dict:
    return {
        "slug": slug,
        "name_zh": name_zh,
        "name_en": name_en,
        "dk_chapter": dk_chapter,
        "ebook_id": f"73000000-0000-4000-8000-{index:012d}",
        "source_status": source_status,
        "greek_edition": DIELS_1922_LICENSE if dk_chapter is not None else None,
        "english_candidates": [BURNET_1920_LICENSE, FAIRBANKS_1898_LICENSE]
        if slug not in {"protagoras", "gorgias", "socrates"}
        else [],
        "burnet_page": burnet_page,
        "greek_tei": greek_tei,
    }


HUBS = {
    "thales": _hub(1, "thales", "泰利斯", "Thales", 11, source_status="inventory"),
    "anaximander": _hub(2, "anaximander", "阿那克西曼德", "Anaximander", 12, source_status="inventory"),
    "anaximenes": _hub(3, "anaximenes", "阿那克西美尼", "Anaximenes", 13, source_status="inventory"),
    "pythagoras": _hub(4, "pythagoras", "畢達哥拉斯", "Pythagoras", 58, source_status="inventory"),
    "xenophanes": _hub(5, "xenophanes", "色諾芬尼", "Xenophanes", 21, source_status="inventory"),
    "heraclitus": _hub(
        6, "heraclitus", "赫拉克利特", "Heraclitus", 22,
        source_status="pilot-ready",
        burnet_page="Early_Greek_Philosophy/Herakleitos_of_Ephesos",
        greek_tei="https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg0626/tlg002/tlg0626.tlg002.1st1K-grc1.xml",
    ),
    "parmenides": _hub(
        7, "parmenides", "巴門尼德", "Parmenides", 28,
        source_status="pilot-ready",
        burnet_page="Early_Greek_Philosophy/Parmenides_of_Elea",
        greek_tei="https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg1562/tlg002/tlg1562.tlg002.1st1K-grc1.xml",
    ),
    "anaxagoras": _hub(8, "anaxagoras", "阿那克薩哥拉", "Anaxagoras", 59, source_status="inventory"),
    "zeno-elea": _hub(9, "zeno-elea", "埃利亞的芝諾", "Zeno of Elea", 29, source_status="inventory"),
    "empedocles": _hub(10, "empedocles", "恩培多克勒", "Empedocles", 31, source_status="inventory"),
    "protagoras": _hub(
        11, "protagoras", "普羅泰戈拉", "Protagoras", 80,
        source_status="english-rights-audit-needed",
    ),
    "gorgias": _hub(
        12, "gorgias", "高爾吉亞", "Gorgias", 82,
        source_status="english-rights-audit-needed",
    ),
    "socrates": _hub(
        13, "socrates", "蘇格拉底", "Socrates", None,
        source_status="source-corpus-design-needed",
    ),
    "democritus": _hub(14, "democritus", "德謨克利特", "Democritus", 68, source_status="inventory"),
}


RECORD_TYPES = {
    "A": {
        "record_type": "testimonium",
        "label_zh": "A類見證",
        "is_author_autograph": False,
        "is_direct_quotation": False,
        "translation_voice": "third-person-witness",
    },
    "B": {
        "record_type": "quoted_fragment",
        "label_zh": "B類引文殘篇",
        "is_author_autograph": False,
        # A Diels B classification is an editorial category.  The parser flips
        # this to True only after it has isolated a non-empty quotation.
        "is_direct_quotation": False,
        "translation_voice": "quoted-source-text",
    },
}


def citation_id(slug: str, kind: str, number: str) -> str:
    """Return a display citation without inventing a DK number for Socrates."""
    if kind not in RECORD_TYPES:
        raise ValueError(f"unsupported Diels record kind: {kind}")
    chapter = HUBS[slug]["dk_chapter"]
    if chapter is None:
        raise ValueError(f"{slug} is not assigned a Diels-Kranz chapter")
    return f"DK {chapter} {kind}{number}"


def record_policy(kind: str) -> dict:
    try:
        return dict(RECORD_TYPES[kind])
    except KeyError as exc:
        raise ValueError(f"unsupported Diels record kind: {kind}") from exc
