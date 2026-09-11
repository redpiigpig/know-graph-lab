#!/usr/bin/env python3
"""Compose graded Biblical Hebrew practice sentences from attested patterns.

The owner's decision of 2026-09-11: composed sentences lead, quoted Scripture
supports.  Ten items per lesson, every one of the lesson's twenty words present,
and the early lessons must stay easy -- a sentence may only use words already
taught, and prefers the earliest-taught ones for everything that is not the
word being practised.

Nothing about the Hebrew is invented.  A sentence is a clause pattern lifted
from the Hebrew Bible with its morph tags kept, and every word dropped into a
slot is a form that is actually written somewhere in the text with exactly that
tag.  What this file adds over a blind swap is the pattern filter: the
constructions that cannot survive substitution are thrown out before they are
ever used as a template.

A morph tag does not prove sense.  Composed sentences leave here marked
`pending_semantic_review` and are meant to go through the semantic gate before
they reach a page.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from select_hebrew_memory_verses import (  # noqa: E402
    DEFAULT_VOCAB,
    DEFAULT_WLC,
    Token,
    Verse,
    VocabItem,
    load_vocabulary,
    load_wlc,
)
from build_hebrew_exercises import (  # noqa: E402
    CANTILLATION_RE,
    Unit,
    build_form_bank,
    build_units,
    cumulative_sets,
    readable,
    token_shape,
)

OUTPUT = ROOT / "output/source-cache/original-readers/hebrew-full/composed-sentences.json"

# MorphHB verb code: V + stem + aspect + person/gender/number.
VERB_RE = re.compile(r"^HV(.)(.)")
FINITE_ASPECTS = set("pqiwvh")          # perfect, imperfect, waw-consecutive, imperative
INFINITIVE_ABSOLUTE = "a"               # the paronomastic construction: never a template
PARTICIPLE_ASPECTS = set("rs")


def morph_of(token: Token) -> str:
    return token.morph or ""


def is_finite_verb(token: Token) -> bool:
    match = VERB_RE.match(morph_of(token))
    return bool(match) and match.group(2) in FINITE_ASPECTS


def pattern_rejection(unit: Unit) -> str | None:
    """Reject clauses whose grammar is bound to the particular words in them.

    Every rule here stands for a sentence that a tag-identical swap has already
    broken or would break: a cognate-accusative frame that requires both words
    to share a root, a construct chain whose head governs the noun after it, a
    verb whose sense lives in the preposition it takes, a quotation that only
    parses because of what follows it in its own verse.
    """
    tokens = unit.tokens
    if not (3 <= len(tokens) <= 6):
        return "長度不適合當句型"
    morphs = [morph_of(token) for token in tokens]
    if any(not morph for morph in morphs):
        return "缺形態標記"
    finite = [token for token in tokens if is_finite_verb(token)]
    if len(finite) != 1:
        return "不是單一謂述句"
    for morph in morphs:
        match = VERB_RE.match(morph)
        if match and match.group(2) == INFINITIVE_ABSOLUTE:
            return "同源賓語／不定詞絕對式，換字即壞"
        if match and match.group(2) in PARTICIPLE_ASPECTS:
            return "分詞句，主語判定不穩"
    if any(morph.startswith("HNc") and morph.endswith("c") for morph in morphs):
        return "含附屬形，與後詞綁定"
    if any("Np" in morph for morph in morphs):
        return "含專名，替換後語意不可控"
    if any(morph.startswith(("HVq", "HVn", "HVp")) is False and morph.startswith("HV") for morph in morphs):
        return "罕用詞幹，例句不宜"
    if sum(morph.startswith("HR") for morph in morphs) >= 2:
        return "多介系詞，支配關係不可換"
    if any(morph.startswith("HTi") or morph.startswith("HTj") for morph in morphs):
        return "疑問／感嘆詞，句式受限"
    counts = Counter(s for token in tokens for s in token.strongs)
    if counts and max(counts.values()) >= 2:
        return "句中重複用詞"
    return None


@dataclass(frozen=True)
class Pattern:
    """A slot sequence taken from one real clause."""

    ref: str
    morphs: tuple[str, ...]
    prefixes: tuple[str, ...]
    original: tuple[str, ...]
    swappable: tuple[int, ...]

    @property
    def size(self) -> int:
        return len(self.morphs)


def build_patterns(units: Sequence[Unit]) -> list[Pattern]:
    patterns: list[Pattern] = []
    seen: set[tuple[str, ...]] = set()
    for unit in units:
        if unit.kind == "verse":
            continue
        if pattern_rejection(unit) is not None:
            continue
        words = unit.text.split(" ")
        if len(words) != len(unit.tokens):
            continue
        shapes = [token_shape(token) for token in unit.tokens]
        if any(shape is None for shape in shapes):
            continue
        morphs = tuple(shape[1] for shape in shapes)
        prefixes = tuple(shape[2] for shape in shapes)
        key = morphs + prefixes
        if key in seen:
            continue
        seen.add(key)
        swappable = tuple(
            index
            for index, token in enumerate(unit.tokens)
            if token.strongs and morph_of(token).startswith(("HNc", "HV", "HA"))
        )
        if not swappable:
            continue
        patterns.append(
            Pattern(
                ref=unit.uid,
                morphs=morphs,
                prefixes=prefixes,
                original=tuple(CANTILLATION_RE.sub("", word) for word in words),
                swappable=swappable,
            )
        )
    return patterns


def lesson_rank(vocabulary: dict[int, list[VocabItem]]) -> dict[str, int]:
    """Every taught word's lesson number, so fillers can prefer the earliest."""
    rank: dict[str, int] = {}
    for lesson in sorted(vocabulary):
        for item in vocabulary[lesson]:
            for strong in item.strongs:
                rank.setdefault(strong, lesson)
    return rank


def compose_for_lesson(
    targets: Sequence[VocabItem],
    known: set[str],
    patterns: Sequence[Pattern],
    bank: dict[tuple[str, str, str], Counter[str]],
    rank: dict[str, int],
    fillers: dict[tuple[str, str], list[tuple[int, str, str]]],
    wanted_per_sentence: int = 2,
) -> tuple[list[dict[str, Any]], list[VocabItem]]:
    """Fill patterns so that every target word appears, easiest words elsewhere.

    A word no pattern can hold comes back in the second list: quoting the text
    is the fallback, which is the division of labour the owner asked for --
    composed sentences lead, Scripture supports.
    """
    remaining = list(targets)
    out: list[dict[str, Any]] = []
    used_patterns: set[str] = set()
    while remaining:
        best: dict[str, Any] | None = None
        for pattern in patterns:
            if pattern.ref in used_patterns:
                continue
            filled: list[str | None] = [None] * pattern.size
            placed: list[VocabItem] = []
            for index in pattern.swappable:
                if len(placed) >= wanted_per_sentence:
                    break
                for item in remaining:
                    if item in placed:
                        continue
                    form = next(
                        (
                            bank[(strong, pattern.morphs[index], pattern.prefixes[index])].most_common(1)[0][0]
                            for strong in item.strongs
                            if (strong, pattern.morphs[index], pattern.prefixes[index]) in bank
                        ),
                        None,
                    )
                    if form:
                        filled[index] = CANTILLATION_RE.sub("", form)
                        placed.append(item)
                        break
            if not placed:
                continue
            # Everything still empty keeps the pattern's own word when it is
            # already taught, otherwise the earliest-taught word that fits.
            ok = True
            for index in range(pattern.size):
                if filled[index] is not None:
                    continue
                shape_key = (pattern.morphs[index], pattern.prefixes[index])
                choice = next(
                    (row for row in fillers.get(shape_key, ()) if row[1] in known),
                    None,
                )
                if choice is None:
                    ok = False
                    break
                filled[index] = CANTILLATION_RE.sub("", choice[2])
            if not ok:
                continue
            record = {
                "kind": "composed",
                "patternRef": pattern.ref,
                "text": " ".join(word for word in filled if word),
                "targetWords": [item.public_record() for item in placed],
                "status": "pending_semantic_review",
            }
            if best is None or len(placed) > len(best["targetWords"]):
                best = record
                best["_placed"] = placed
                best["_pattern"] = pattern.ref
            if best and len(best["targetWords"]) >= wanted_per_sentence:
                break
        if best is None:
            return out, remaining
        used_patterns.add(best.pop("_pattern"))
        placed = best.pop("_placed")
        out.append(best)
        remaining = [item for item in remaining if item not in placed]
    return out, []


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lesson", type=int, action="append", help="only these lessons")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    vocabulary = load_vocabulary(DEFAULT_VOCAB)
    verses = load_wlc(DEFAULT_WLC)
    units = build_units(verses)
    patterns = build_patterns(units)
    bank = build_form_bank(verses)
    rank = lesson_rank(vocabulary)
    fillers: dict[tuple[str, str], list[tuple[int, str, str]]] = {}
    for (strong, morph, prefixes), forms in bank.items():
        fillers.setdefault((morph, prefixes), []).append(
            (rank.get(strong, 999), strong, forms.most_common(1)[0][0])
        )
    for key in fillers:
        fillers[key].sort()
    print(f"可用句型：{len(patterns)}（自 {len(units)} 個單元篩出）")

    wanted = set(args.lesson or [])
    rows: list[dict[str, Any]] = []
    for lesson, items, known in cumulative_sets(vocabulary):
        if wanted and lesson not in wanted:
            continue
        usable = patterns
        composed, unplaceable = compose_for_lesson(items, known, usable, bank, rank, fillers)
        rows.append({"lesson": lesson, "sentences": composed,
                     "needsQuotation": [item.public_record() for item in unplaceable]})
        print(f"L{lesson:02d} 造出 {len(composed)} 句，涵蓋 {sum(len(s['targetWords']) for s in composed)}/{len(items)} 詞"
              + (f"；造不出來需引經文：{'、'.join(i.pointed for i in unplaceable)}" if unplaceable else ""))
        for sentence in composed:
            print(f"   {sentence['text']}   ← 句型 {sentence['patternRef']}  練：" +
                  "、".join(word["pointed"] for word in sentence["targetWords"]))

    if args.write:
        OUTPUT.write_text(
            json.dumps(
                {
                    "schemaVersion": "0.1.0",
                    "generatedOn": date.today().isoformat(),
                    "status": "draft-pending-semantic-review",
                    "lessons": rows,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"寫入 {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
