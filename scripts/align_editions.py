"""Cross-edition alignment for collected-works multi-language books.

Two editions of the same work (e.g. German GW + English CW) are independently
edited — different paragraphing, sometimes reordered, different front matter —
so we cannot assume "section i of DE == section i of EN". This module turns two
section lists into `aligned_units` (the input `assemble_multilang_chunks` wants),
using the strategy ladder from the skill:

  1. anchor join   — both editions number their chapters/sections (Chapter III /
                     Kapitel 3 / 第三章 / § 3) → join on a normalized key.
  2. order align   — no reliable anchors → zip by index, padding the short side.
  (3) LLM-assisted — out of scope here; the caller can fall back to it when this
                     module reports low anchor coverage.

A "section" is a dict: {"heading": str, "text": str}. An aligned unit is
{"chapter_path": str, "sources": {"de": str, "en": str}, "match": str} ready for
`assemble_multilang_chunks`. The 繁中 `chapter_path` is provisional (taken from
the primary edition's heading); the translate step localizes it later.

Pure functions — no network, DB, or LLM. See
.claude/skills/ebook-collected-works/SKILL.md.
"""
from __future__ import annotations

import re

# Heading keyword → canonical division kind. German + English + CJK so
# "Kapitel 3" / "Chapter 3" / "第三章" all collapse to the same key.
_KIND_KEYWORDS = {
    "chapter": ("chapter", "chap", "kapitel", "kap"),
    "part": ("part", "teil"),
    "book": ("book", "buch"),
    "section": ("section", "abschnitt"),
}
_KEYWORD_TO_KIND = {kw: kind for kind, kws in _KIND_KEYWORDS.items() for kw in kws}
_KEYWORD_RE = re.compile(
    r"\b(" + "|".join(sorted(_KEYWORD_TO_KIND, key=len, reverse=True)) + r")\b\.?\s+"
    r"([ivxlcdm]+|\d+)\b",
    re.IGNORECASE,
)
_CJK_RE = re.compile(r"第\s*([一二三四五六七八九十百零0-9]+)\s*([章節篇部卷])")
_CJK_KIND = {"章": "chapter", "節": "section", "篇": "part", "部": "part", "卷": "book"}
_SECTION_SIGN_RE = re.compile(r"§\s*(\d+)")
_ROMAN = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}
_CJK_DIGIT = {"零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
              "六": 6, "七": 7, "八": 8, "九": 9}


def _roman_to_int(s: str) -> int | None:
    s = s.lower()
    if any(c not in _ROMAN for c in s):
        return None
    total, prev = 0, 0
    for c in reversed(s):
        v = _ROMAN[c]
        total += -v if v < prev else v
        prev = max(prev, v)
    return total or None


def _cjk_to_int(s: str) -> int | None:
    if s.isdigit():
        return int(s)
    # Handle 一..九十九 with 十/百 multipliers (chapter numbers stay small).
    total, section, last_digit = 0, 0, 0
    for ch in s:
        if ch in _CJK_DIGIT:
            last_digit = _CJK_DIGIT[ch]
            section += last_digit
        elif ch == "十":
            section = section - last_digit + (last_digit or 1) * 10
            last_digit = 0
        elif ch == "百":
            section = (section or 1) * 100
            last_digit = 0
        else:
            return None
    total += section
    return total or None


def _parse_number(token: str) -> int | None:
    token = token.strip()
    if token.isdigit():
        return int(token)
    if all(c.lower() in _ROMAN for c in token):
        return _roman_to_int(token)
    return _cjk_to_int(token)


def parse_chapter_number(heading: str) -> tuple[str, int] | None:
    """Extract a normalized (kind, number) division key from a heading, or None.

    'Chapter III. On Memory' → ('chapter', 3); 'Kapitel 3' → ('chapter', 3);
    '第三章 論記憶' → ('chapter', 3); '§ 12' → ('section', 12). Different kinds
    never merge (a 'Part 1' won't align to a 'Chapter 1').
    """
    if not heading:
        return None
    h = re.sub(r"^#{1,6}\s*", "", heading).strip()
    m = _CJK_RE.search(h)
    if m:
        n = _cjk_to_int(m.group(1))
        if n is not None:
            return (_CJK_KIND.get(m.group(2), "chapter"), n)
    m = _SECTION_SIGN_RE.search(h)
    if m:
        return ("section", int(m.group(1)))
    m = _KEYWORD_RE.search(h)
    if m:
        n = _parse_number(m.group(2))
        if n is not None:
            return (_KEYWORD_TO_KIND[m.group(1).lower()], n)
    return None


def _clean_heading(heading: str) -> str:
    return re.sub(r"^#{1,6}\s*", "", heading or "").strip()


def _key(section: dict) -> str | None:
    k = parse_chapter_number(section.get("heading", ""))
    return f"{k[0]}:{k[1]}" if k else None


def _unit(de_sec: dict | None, en_sec: dict | None, match: str) -> dict:
    primary = de_sec or en_sec or {}
    return {
        "chapter_path": _clean_heading(primary.get("heading", "")),
        "sources": {
            "de": de_sec.get("text", "") if de_sec else "",
            "en": en_sec.get("text", "") if en_sec else "",
        },
        "match": match,
    }


def anchor_coverage(sections: list[dict]) -> float:
    """Fraction of sections with a parseable, unique division key. Caller uses
    this to decide anchor-join vs order-align vs LLM fallback."""
    if not sections:
        return 0.0
    keys = [_key(s) for s in sections]
    present = [k for k in keys if k]
    unique = len(set(present)) == len(present)
    return (len(present) / len(sections)) if unique else 0.0


def align_editions(
    de_sections: list[dict],
    en_sections: list[dict],
    *,
    min_coverage: float = 0.8,
) -> list[dict]:
    """Align two editions into `aligned_units`.

    Anchor-join when BOTH editions clear `min_coverage` (unique keys); else fall
    back to order-align (zip by index, pad the short side). Result order follows
    the German (primary) edition; en-only sections are appended at the end.
    """
    if (anchor_coverage(de_sections) >= min_coverage
            and anchor_coverage(en_sections) >= min_coverage):
        return _anchor_join(de_sections, en_sections)
    return _order_align(de_sections, en_sections)


def _anchor_join(de_sections: list[dict], en_sections: list[dict]) -> list[dict]:
    en_by_key = {}
    for s in en_sections:
        k = _key(s)
        if k is not None:
            en_by_key.setdefault(k, s)
    units, used = [], set()
    for s in de_sections:
        k = _key(s)
        en = en_by_key.get(k)
        if en is not None:
            used.add(k)
            units.append(_unit(s, en, "anchor"))
        else:
            units.append(_unit(s, None, "de-only"))
    for s in en_sections:
        k = _key(s)
        if k is not None and k not in used:
            units.append(_unit(None, s, "en-only"))
    return units


def _order_align(de_sections: list[dict], en_sections: list[dict]) -> list[dict]:
    n = max(len(de_sections), len(en_sections))
    units = []
    for i in range(n):
        d = de_sections[i] if i < len(de_sections) else None
        e = en_sections[i] if i < len(en_sections) else None
        units.append(_unit(d, e, "order"))
    return units
