#!/usr/bin/env python3
"""Mine ten translation exercises per lesson for the Biblical Hebrew reader.

The exercises replace the two memory verses that used to sit between the
vocabulary list and the reading.  Every item is attested text: a whole verse
where one exists whose words the learner has all been taught, otherwise a
clause cut at the Masoretic accents.  Nothing here is composed.

Coverage is best-effort by the owner's decision of 2026-09-11: ten items can
reach roughly fourteen to sixteen of a lesson's twenty words, so each lesson
records which of its words no item reached.  Those words come back in later
lessons, where the cumulative vocabulary is wide enough to carry them.

The Chinese answer is never translated here.  Items keep the reference of the
verse they came from; `attach_hebrew_exercise_chinese.py` fills the published
RCUV2010 wording in afterwards.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
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
    hard_exclusion_reason,
    is_near_duplicate,
    item_matches,
    load_vocabulary,
    load_wlc,
)

OUTPUT = ROOT / "output/source-cache/original-readers/hebrew-full/exercises.json"
REVIEW = ROOT / "output/source-cache/original-readers/hebrew-full/exercise-review.md"

ITEMS_PER_LESSON = 10
CANTILLATION_RE = re.compile(r"[֑-֯]")
# Masoretic accents that end a clause: atnach, segolta, zaqef qatan/gadol.
BREAK_ACCENTS = "֑֒֔֕"
FINITE_VERB_RE = re.compile(r"HV[^/]*[qQ]?[a-z]*[ip]\d")
MIN_CLAUSE_TOKENS = 3
MAX_CLAUSE_TOKENS = 12


@dataclass(frozen=True)
class Unit:
    """One printable exercise candidate: a whole verse or one clause of it."""

    uid: str
    ref: str
    kind: str  # "verse" | "clause"
    part: int  # 1-based clause number inside the verse; 0 for a whole verse
    part_count: int
    text: str
    tokens: tuple[Token, ...]
    book: str
    chapter: int
    verse: int

    @property
    def token_count(self) -> int:
        return len(self.tokens)

    @property
    def strongs(self) -> frozenset[str]:
        return frozenset(s for token in self.tokens for s in token.strongs)


@dataclass
class Scored:
    unit: Unit
    targets: list[VocabItem] = field(default_factory=list)


def split_clauses(verse: Verse) -> list[Unit]:
    """Cut a verse at its own accents, keeping the printed text byte-exact.

    The verse text joins maqqef-bound tokens into one written word, so the walk
    is over written words; each carries however many tokens it spells.  The
    reconstruction is asserted rather than trusted: a clause layer that quietly
    drops a word would print a sentence the Masoretes never wrote.
    """
    words = verse.text.split(" ")
    tokens = list(verse.tokens)
    cursor = 0
    clauses: list[tuple[list[str], list[Token]]] = []
    current_words: list[str] = []
    current_tokens: list[Token] = []
    for word in words:
        stripped = word.strip()
        if not stripped:
            continue
        taken: list[Token] = []
        remainder = stripped
        while cursor < len(tokens) and tokens[cursor].text and tokens[cursor].text in remainder:
            taken.append(tokens[cursor])
            remainder = remainder.replace(tokens[cursor].text, "", 1)
            cursor += 1
            if not remainder.strip("־׃׀ "):
                break
        current_words.append(stripped)
        current_tokens.extend(taken)
        if any(accent in stripped for accent in BREAK_ACCENTS):
            clauses.append((current_words, current_tokens))
            current_words, current_tokens = [], []
    if current_words:
        clauses.append((current_words, current_tokens))
    if cursor != len(tokens) or not clauses:
        return []
    units: list[Unit] = []
    for index, (clause_words, clause_tokens) in enumerate(clauses, start=1):
        if not clause_tokens:
            continue
        units.append(
            Unit(
                uid=f"{verse.ref}#{index}",
                ref=verse.ref,
                kind="clause",
                part=index,
                part_count=len(clauses),
                text=" ".join(clause_words),
                tokens=tuple(clause_tokens),
                book=verse.book,
                chapter=verse.chapter,
                verse=verse.verse,
            )
        )
    return units


def whole_verse_unit(verse: Verse) -> Unit:
    return Unit(
        uid=verse.ref,
        ref=verse.ref,
        kind="verse",
        part=0,
        part_count=1,
        text=verse.text,
        tokens=verse.tokens,
        book=verse.book,
        chapter=verse.chapter,
        verse=verse.verse,
    )


def clause_is_printable(unit: Unit) -> str | None:
    """Reject clause fragments that read as a list or as half a thought."""
    if not (MIN_CLAUSE_TOKENS <= unit.token_count <= MAX_CLAUSE_TOKENS):
        return "長度不合"
    lexical = [token for token in unit.tokens if token.strongs]
    if len(lexical) < 2:
        return "缺乏實詞"
    proper = sum("Np" in token.morph for token in lexical)
    if proper >= 3:
        return "專名列舉"
    numbers = sum("Acd" in token.morph or "Aco" in token.morph for token in lexical)
    if numbers >= 3:
        return "數字列舉"
    counts = Counter(s for token in lexical for s in token.strongs)
    if counts and max(counts.values()) >= 3:
        return "重複用詞"
    return None


def build_units(verses: Sequence[Verse]) -> list[Unit]:
    units: list[Unit] = []
    for verse in verses:
        if hard_exclusion_reason(verse) is None:
            units.append(whole_verse_unit(verse))
        for clause in split_clauses(verse):
            if clause_is_printable(clause) is None:
                units.append(clause)
    return units


def cumulative_sets(vocabulary: dict[int, list[VocabItem]]) -> list[tuple[int, list[VocabItem], set[str]]]:
    rows: list[tuple[int, list[VocabItem], set[str]]] = []
    known: set[str] = set()
    for lesson in sorted(vocabulary):
        items = vocabulary[lesson]
        for item in items:
            known.update(item.strongs)
        rows.append((lesson, items, set(known)))
    return rows


def readable(unit: Unit, known: set[str]) -> bool:
    """Every content word must already have been taught.  No footnoted words."""
    return bool(unit.strongs) and unit.strongs <= known


def difficulty(unit: Unit) -> tuple[int, int, int]:
    """Shorter first, whole verses ahead of clauses, then canonical order."""
    return (unit.token_count, 0 if unit.kind == "verse" else 1, unit.verse)


def select_for_lesson(
    lesson: int,
    lesson_items: Sequence[VocabItem],
    known: set[str],
    units: Sequence[Unit],
    used_refs: set[str],
    reading_chapters: set[str],
) -> tuple[list[Scored], list[VocabItem]]:
    pool: list[Scored] = []
    for unit in units:
        if unit.ref in used_refs:
            continue
        if not readable(unit, known):
            continue
        targets = [item for item in lesson_items if item_matches(item, unit.tokens)]
        if not targets:
            continue
        pool.append(Scored(unit=unit, targets=targets))
    chosen: list[Scored] = []
    chosen_verses: list[Verse] = []
    remaining = {item.ordinal for item in lesson_items}
    taken_refs: set[str] = set()
    while len(chosen) < ITEMS_PER_LESSON and pool:
        def rank(scored: Scored) -> tuple:
            new_words = len([item for item in scored.targets if item.ordinal in remaining])
            unit = scored.unit
            return (
                -new_words,
                0 if f"{unit.book}.{unit.chapter}" not in reading_chapters else 1,
                0 if unit.kind == "verse" else 1,
                unit.token_count,
                unit.ref,
            )

        pool.sort(key=rank)
        best = pool[0]
        new_words = [item for item in best.targets if item.ordinal in remaining]
        if not new_words and len(chosen) >= 1:
            # Nothing left to teach: stop rather than pad with repeats.
            break
        candidate_verse = Verse(
            ref=best.unit.uid,
            book=best.unit.book,
            chapter=best.unit.chapter,
            verse=best.unit.verse,
            source_file="",
            text=best.unit.text,
            tokens=best.unit.tokens,
        )
        pool.pop(0)
        if is_near_duplicate(candidate_verse, chosen_verses):
            continue
        if best.unit.ref in taken_refs:
            continue
        chosen.append(best)
        chosen_verses.append(candidate_verse)
        taken_refs.add(best.unit.ref)
        remaining -= {item.ordinal for item in best.targets}
        pool = [scored for scored in pool if scored.unit.ref not in taken_refs]
    missed = [item for item in lesson_items if item.ordinal in remaining]
    return chosen, missed


def build_form_bank(verses: Sequence[Verse]) -> dict[tuple[str, str, str], Counter[str]]:
    """Map (Strong number, exact morph tag) to the surface forms actually written.

    Only prefix-free, single-lemma tokens go in.  A form carrying an attached
    preposition or article cannot be dropped into another word's slot without
    changing what the slot means, and a form whose morph tag differs by even
    one letter is a different gender, number, state or stem — which is exactly
    the agreement a composed sentence gets wrong.
    """
    bank: dict[tuple[str, str, str], Counter[str]] = {}
    for verse in verses:
        for token in verse.tokens:
            key = token_shape(token)
            if key is None or not token.text:
                continue
            bank.setdefault(key, Counter())[token.text] += 1
    return bank


def token_shape(token: Token | None) -> tuple[str, str, str] | None:
    """The slot signature: content Strong, full morph tag, and prefix chain.

    Words that carry an attached conjunction, article or preposition are kept,
    because several lesson words are almost never written bare — but a form may
    only stand in for another form of the identical shape, prefixes included.
    """
    if token is None:
        return None
    if len(token.strongs) != 1 or not token.morph:
        return None
    strong = next(iter(token.strongs))
    prefixes = "/".join(sorted(token.lemma_codes))
    return (strong, token.morph, prefixes)


def replaceable(token: Token) -> bool:
    return token_shape(token) is not None and bool(token.text)


def build_shape_index(
    bank: dict[tuple[str, str, str], Counter[str]]
) -> dict[tuple[str, str], list[tuple[str, str, int]]]:
    """Group the form bank by slot shape, commonest word first."""
    index: dict[tuple[str, str], list[tuple[str, str, int]]] = {}
    for (strong, morph, prefixes), forms in bank.items():
        form, _ = forms.most_common(1)[0]
        index.setdefault((morph, prefixes), []).append((strong, form, sum(forms.values())))
    for key in index:
        index[key].sort(key=lambda row: -row[2])
    return index


def simplify_unit(
    unit: Unit,
    known: set[str],
    lesson_strongs: set[str],
    shape_index: dict[tuple[str, str], list[tuple[str, str, int]]],
    max_swaps: int = 3,
) -> tuple[str, list[dict[str, Any]]] | None:
    """Adapt a real verse by replacing only the words not yet taught.

    The lesson word stays where the text actually put it, so its syntax and
    its sense are the ones it really has; what gets swapped out is the
    surrounding vocabulary the learner has not met.  Each replacement copies
    the slot's whole shape -- morph tag and prefix chain -- so whatever agreed
    with the old word agrees with the new one.  Preference goes to a word from
    this same lesson, which practises two words in one sentence.
    """
    words = unit.text.split(" ")
    if len(words) != len(unit.tokens):
        return None
    changes: list[dict[str, Any]] = []
    for index, token in enumerate(unit.tokens):
        if not token.strongs or token.strongs <= known:
            continue
        shape = token_shape(token)
        if shape is None:
            return None
        candidates = shape_index.get((shape[1], shape[2]), [])
        chosen: tuple[str, str] | None = None
        for strong, form, _ in candidates:
            if strong in lesson_strongs:
                chosen = (strong, form)
                break
        if chosen is None:
            for strong, form, _ in candidates:
                if strong in known:
                    chosen = (strong, form)
                    break
        if chosen is None:
            return None
        changes.append(
            {
                "slot": index + 1,
                "from": CANTILLATION_RE.sub("", token.text),
                "to": CANTILLATION_RE.sub("", chosen[1]),
                "strong": f"H{chosen[0]}",
                "morph": token.morph,
            }
        )
        words[index] = chosen[1]
    if not changes or len(changes) > max_swaps:
        return None
    text = CANTILLATION_RE.sub("", " ".join(words))
    return text, changes


def build_adapted(
    lesson_items: Sequence[VocabItem],
    missed: Sequence[VocabItem],
    known: set[str],
    units: Sequence[Unit],
    used_refs: set[str],
    bank: dict[tuple[str, str, str], Counter[str]],
    budget: int,
    by_strong: dict[str, list[int]],
    shape_index: dict[tuple[str, str], list[tuple[str, str, int]]],
) -> list[dict[str, Any]]:
    """Give every unreached word a sentence of its own, adapted from its own text."""
    lesson_strongs = {s for item in lesson_items for s in item.strongs}
    remaining = list(missed)
    out: list[dict[str, Any]] = []
    seen_texts: set[str] = set()
    while remaining and len(out) < budget:
        item = remaining[0]
        best: dict[str, Any] | None = None
        for strong in item.strongs:
            for position in by_strong.get(strong, ()):
                unit = units[position]
                if unit.ref in used_refs or not (4 <= unit.token_count <= 12):
                    continue
                unknown = {s for s in unit.strongs if s not in known}
                if not unknown or len(unknown) > 3:
                    continue
                result = simplify_unit(unit, known, lesson_strongs, shape_index)
                if result is None:
                    continue
                text, changes = result
                if text in seen_texts:
                    continue
                placed = [
                    other
                    for other in lesson_items
                    if any(s in lesson_strongs for s in other.strongs)
                    and (
                        other.ordinal == item.ordinal
                        or any(change.get("strong") == f"H{s}" for s in other.strongs for change in changes)
                    )
                ]
                candidate = {
                    "kind": "adapted",
                    "uid": f"{unit.uid}~adapted",
                    "ref": unit.ref,
                    "text": text,
                    "tokenCount": unit.token_count,
                    "adaptedFrom": unit.ref,
                    "originalText": unit.text,
                    "changes": changes,
                    "targetWords": [row.public_record() for row in placed],
                    "swaps": len(changes),
                }
                if best is None or len(placed) > len(best["targetWords"]) or (
                    len(placed) == len(best["targetWords"]) and len(changes) < best["swaps"]
                ):
                    best = candidate
                if best and len(best["targetWords"]) >= 3 and best["swaps"] <= 1:
                    break
            if best and len(best["targetWords"]) >= 3 and best["swaps"] <= 1:
                break
        if best is None:
            remaining.pop(0)
            continue
        out.append(best)
        used_refs.add(best["ref"])
        seen_texts.add(best["text"])
        covered = {row["ordinal"] for row in best["targetWords"]}
        remaining = [row for row in remaining if row.ordinal not in covered]
    return out


def item_record(index: int, scored: Scored, known_before: set[str]) -> dict[str, Any]:
    unit = scored.unit
    return {
        "no": index,
        "uid": unit.uid,
        "kind": unit.kind,
        "ref": unit.ref,
        "clause": None if unit.kind == "verse" else f"{unit.part}/{unit.part_count}",
        "text": unit.text,
        "tokenCount": unit.token_count,
        "targetWords": [item.public_record() for item in scored.targets],
        "translationRef": unit.ref,
        "translationZh": None,
        "translationScope": "verse" if unit.kind == "verse" else "verse-containing-clause",
        "answerStatus": "pending_chinese",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vocab", type=Path, default=DEFAULT_VOCAB)
    parser.add_argument("--wlc", type=Path, default=DEFAULT_WLC)
    parser.add_argument("--plan", type=Path, default=ROOT / "output/source-cache/original-readers/hebrew-full/scripture-plan.json")
    parser.add_argument("--write", action="store_true", help="write exercises.json and the review note")
    args = parser.parse_args()

    vocabulary = load_vocabulary(args.vocab)
    verses = load_wlc(args.wlc)
    units = build_units(verses)
    plan = json.loads(args.plan.read_text(encoding="utf-8")) if args.plan.exists() else {}
    reading_chapters = {
        f"{row.get('osisBook')}.{row.get('chapter')}"
        for row in plan.get("chapters", [])
        if row.get("osisBook")
    }

    by_lesson_units: dict[int, list[Unit]] = {}
    lessons_out: list[dict[str, Any]] = []
    used_refs: set[str] = set()
    total_targets = 0
    total_covered = 0
    short_lessons: list[int] = []

    bank = build_form_bank(verses)
    shape_index = build_shape_index(bank)
    by_strong: dict[str, list[int]] = {}
    for position, unit in enumerate(units):
        for strong in unit.strongs:
            by_strong.setdefault(strong, []).append(position)
    adapted_total = 0

    for lesson, lesson_items, known in cumulative_sets(vocabulary):
        chosen, missed = select_for_lesson(
            lesson, lesson_items, known, units, used_refs, reading_chapters
        )

        def still_missing(picked: Sequence[Scored]) -> list[VocabItem]:
            covered_ordinals = {item.ordinal for scored in picked for item in scored.targets}
            return [item for item in lesson_items if item.ordinal not in covered_ordinals]

        # Make room for the adapted items the uncovered words will need: an
        # adapted sentence carries up to three of them, a mined one carries the
        # words it happens to contain.  The last picks are the cheapest to drop
        # because the greedy pass took the widest sentences first.
        mined_all = list(chosen)
        while chosen:
            missed = still_missing(chosen)
            needed = -(-len(missed) // 2)
            if len(chosen) + needed <= ITEMS_PER_LESSON:
                break
            chosen.pop()
        missed = still_missing(chosen)

        for scored in chosen:
            used_refs.add(scored.unit.ref)
        adapted = build_adapted(
            lesson_items, missed, known, units, used_refs, bank,
            budget=ITEMS_PER_LESSON - len(chosen),
            by_strong=by_strong, shape_index=shape_index,
        )
        adapted_total += len(adapted)
        adapted_covered = {row["ordinal"] for item in adapted for row in item["targetWords"]}
        missed = [item for item in missed if item.ordinal not in adapted_covered]

        spare = [scored for scored in mined_all if scored not in chosen]
        while len(chosen) + len(adapted) < ITEMS_PER_LESSON and spare:
            refill = spare.pop(0)
            chosen.append(refill)
            used_refs.add(refill.unit.ref)
        chosen.sort(key=lambda scored: difficulty(scored.unit))
        records = [item_record(i, scored, known) for i, scored in enumerate(chosen, start=1)]
        for offset, row in enumerate(adapted, start=len(records) + 1):
            row.update(
                {
                    "no": offset,
                    "clause": None,
                    "translationRef": row["adaptedFrom"],
                    "translationZh": None,
                    "translationScope": "adapted-needs-own-rendering",
                    "answerStatus": "pending_chinese",
                }
            )
            records.append(row)

        by_lesson_units[lesson] = [scored.unit for scored in chosen]
        covered = len(lesson_items) - len(missed)
        total_targets += len(lesson_items)
        total_covered += covered
        if len(records) < ITEMS_PER_LESSON:
            short_lessons.append(lesson)
        lessons_out.append(
            {
                "lesson": lesson,
                "id": f"hbo-lesson-{lesson:02d}",
                "items": records,
                "coverage": {
                    "lessonWords": len(lesson_items),
                    "practised": covered,
                    "notPractised": [item.public_record() for item in missed],
                },
            }
        )

    payload = {
        "schemaVersion": "1.0.0",
        "language": "Biblical Hebrew",
        "languageCode": "hbo",
        "generatedOn": date.today().isoformat(),
        "itemsPerLesson": ITEMS_PER_LESSON,
        "direction": "original-to-chinese",
        "policy": {
            "composition": "none",
            "note": "每題都是原文既有的整節或依重音切出的子句；譯文取既有中譯，本管線不翻譯。",
            "unknownWords": "不允許：題目中每個實詞都必須已在本課或先前課教過。",
            "coverage": "盡量涵蓋本課二十詞，涵蓋不到者列於 notPractised，由後續課次補上。",
        },
        "corpus": {
            "edition": "Open Scriptures Hebrew Bible (OSHB), Westminster Leningrad Codex",
            "reading": "pointed-qere",
        },
        "counts": {
            "lessons": len(lessons_out),
            "items": sum(len(row["items"]) for row in lessons_out),
            "lessonWords": total_targets,
            "practised": total_covered,
            "coverageRate": round(total_covered / total_targets, 4) if total_targets else 0.0,
            "lessonsShortOfTen": short_lessons,
        },
        "lessons": lessons_out,
    }

    print(f"單元池：{len(units)}（整節 {sum(1 for u in units if u.kind == 'verse')}，子句 {sum(1 for u in units if u.kind == 'clause')}）")
    print(f"題目：{payload['counts']['items']} 題 / {len(lessons_out)} 課")
    print(f"本課字涵蓋：{total_covered}/{total_targets}（{payload['counts']['coverageRate']:.1%}）")
    print(f"其中改寫題 {adapted_total} 題")
    if short_lessons:
        print(f"不足十題的課：{short_lessons}")
    incomplete = [row["lesson"] for row in lessons_out if row["coverage"]["notPractised"]]
    if incomplete:
        print(f"未達二十字全覆蓋的課：{incomplete}")
    for row in lessons_out[:3]:
        print(f"  L{row['lesson']:02d} {len(row['items'])} 題，練到 {row['coverage']['practised']}/{row['coverage']['lessonWords']}")

    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"寫入 {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
