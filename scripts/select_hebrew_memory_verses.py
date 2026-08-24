#!/usr/bin/env python3
"""Select two vocabulary-aligned Biblical Hebrew memory verses per lesson.

The selector reads the local Open Scriptures Hebrew Bible (MorphHB/WLC) and
the 50 x 20 vocabulary curriculum.  Matching is by Strong/lemma identity, not
by surface spelling, so inflected forms count.  The displayed text follows the
pointed Qere reading: Ketiv tokens are omitted whenever a Qere is supplied.

The command is deliberately dry-run by default.  Pass ``--write`` only after
the chapter plan has been approved.
"""

from __future__ import annotations

import argparse
import bisect
import heapq
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from rcuv2010_reader import load_rcuv_snapshot, translation_for_mt


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VOCAB = ROOT / "data/originalReaders/vocabulary/hebrew-1000.json"
DEFAULT_PLAN = ROOT / "output/source-cache/original-readers/hebrew-full/scripture-plan.json"
DEFAULT_WLC = ROOT / "output/source-cache/original-readers/morphhb-src/morphhb-master/wlc"
DEFAULT_CHINESE = ROOT / "output/source-cache/original-readers/hebrew-full/RCUV2010.json"
DEFAULT_CANDIDATES = ROOT / "output/source-cache/original-readers/hebrew-full/memory-candidates.json"
DEFAULT_REVIEW = ROOT / "output/source-cache/original-readers/hebrew-full/memory-selection-review.md"
OSIS_NS = "{http://www.bibletechnologies.net/2003/OSIS/namespace}"
HEBREW_LETTER_RE = re.compile(r"[\u05d0-\u05ea]")
NIQQUD_RE = re.compile(r"[\u05b0-\u05bc\u05c1\u05c2\u05c7]")
CANTILLATION_RE = re.compile(r"[\u0591-\u05af]")
STRONG_RE = re.compile(r"\d+")

# MorphHB represents these bound morphemes symbolically in a slash-separated
# lemma (rather than with a Strong number).
BOUND_LEMMA_CODES = {
    "ו": {"c"},
    "ב": {"b"},
    "כ": {"k"},
    "ל": {"l"},
    "ה": {"h"},
}

APPROVED_CHAPTERS = (
    "Ps.136", "Ps.23", "Ps.1", "1Sam.3", "Gen.12",
    "Gen.1", "Deut.6", "Exod.20", "Exod.3", "Gen.3",
    "Ezek.37", "2Sam.7", "Eccl.3", "Ps.51", "Isa.6",
    "1Kgs.18", "Lev.19", "Song.2", "Isa.53", "Isa.9",
    "Prov.8", "Jer.31", "Exod.15", "Job.28", "Judg.5",
)

# Human-reviewed final selections.  Each pair was checked in Hebrew and RCUV2010
# for semantic self-containment and suitability for repeated memorization.
REVIEWED_SELECTIONS: dict[int, tuple[str, str]] = {
    1: ("Deut.15.15", "Deut.7.8"),
    2: ("Gen.24.48", "Job.42.15"),
    3: ("Zech.8.9", "1Sam.1.3"),
    4: ("Gen.1.28", "Ps.146.6"),
    5: ("Deut.6.25", "1Kgs.8.23"),
    6: ("Ps.25.8", "Ps.37.16"),
    7: ("Ps.99.9", "Jonah.3.8"),
    8: ("Isa.43.10", "Ps.44.5"),
    9: ("Ps.23.4", "Ezra.9.15"),
    10: ("Ps.96.7", "Ps.136.25"),
    11: ("Deut.30.19", "Ps.56.14"),
    12: ("Mal.2.6", "Job.1.21"),
    13: ("1Kgs.8.39", "Prov.20.12"),
    14: ("1Sam.25.35", "Jonah.1.3"),
    15: ("Ps.17.6", "Isa.55.3"),
    16: ("Eccl.9.18", "Ps.119.48"),
    17: ("Prov.29.14", "Ps.51.8"),
    18: ("Prov.28.1", "Ps.52.9"),
    19: ("Jer.31.13", "Amos.3.3"),
    20: ("Ezek.18.9", "Job.38.33"),
    21: ("Prov.18.21", "Jer.15.20"),
    22: ("Ps.98.1", "Joel.2.26"),
    23: ("Ps.106.1", "Prov.28.13"),
    24: ("Prov.23.23", "Ps.119.86"),
    25: ("Job.19.25", "Prov.4.13"),
    26: ("Prov.24.5", "Ps.71.18"),
    27: ("Isa.33.6", "1Sam.2.1"),
    28: ("Deut.19.15", "Ruth.1.7"),
    29: ("Exod.12.18", "Job.42.12"),
    30: ("Ps.80.3", "2Chr.29.30"),
    31: ("Obad.1.8", "Judg.10.11"),
    32: ("2Sam.1.23", "Esth.4.14"),
    33: ("1Sam.3.20", "Hab.3.6"),
    34: ("Prov.29.5", "2Chr.20.20"),
    35: ("Gen.12.6", "Job.29.16"),
    36: ("Ps.119.111", "Job.5.17"),
    37: ("Deut.16.14", "Ps.100.4"),
    38: ("Ps.119.3", "Deut.26.7"),
    39: ("Isa.65.17", "Isa.40.26"),
    40: ("Ps.111.10", "Isa.60.19"),
    41: ("Ps.105.45", "Deut.32.4"),
    42: ("Ps.68.19", "1Kgs.8.50"),
    43: ("Isa.49.13", "Ps.13.6"),
    44: ("Ps.1.1", "Prov.3.3"),
    45: ("Ps.13.2", "Ps.98.3"),
    46: ("Ezek.16.42", "Ps.71.22"),
    47: ("Ps.10.18", "Isa.51.3"),
    48: ("Isa.42.23", "Ps.143.1"),
    49: ("Hos.11.4", "Deut.31.12"),
    50: ("Ps.107.30", "Mic.4.4"),
}

# Sections whose literary purpose is enumeration rather than a complete,
# memorable utterance.  Narrative or poetic verses elsewhere are still judged
# individually by morphology and clause completeness below.
LIST_CHAPTERS: dict[str, set[int]] = {
    "Gen": {5, 10, 36},
    "Exod": set(range(25, 32)) | set(range(35, 41)),
    "Num": {1, 2, 3, 4, 7, 26, 31, 33, 34},
    "Josh": {12, 13, 15, 16, 17, 18, 19, 20, 21},
    "1Kgs": {4, 7},
    "1Chr": set(range(1, 10)) | set(range(23, 28)),
    "2Chr": {2, 3, 4},
    "Ezra": {2},
    "Neh": {3, 7, 10, 11, 12},
}

FUNCTION_POS = {
    "article", "conjunction", "conjunction_phrase", "direct_object_marker",
    "interrogative_particle", "particle", "preposition", "prepositional_phrase",
    "relative_particle",
}
FINITE_VERB_RE = re.compile(r"V.[piwvjhi]")
NUMBER_MORPH_RE = re.compile(r"(?:^|/)H?A[cgo]")

CHINESE_BOOK_NAMES = {
    "Gen": "Genesis", "Exod": "Exodus", "Lev": "Leviticus", "Num": "Numbers",
    "Deut": "Deuteronomy", "Josh": "Joshua", "Judg": "Judges", "Ruth": "Ruth",
    "1Sam": "I Samuel", "2Sam": "II Samuel", "1Kgs": "I Kings", "2Kgs": "II Kings",
    "1Chr": "I Chronicles", "2Chr": "II Chronicles", "Ezra": "Ezra", "Neh": "Nehemiah",
    "Esth": "Esther", "Job": "Job", "Ps": "Psalms", "Prov": "Proverbs",
    "Eccl": "Ecclesiastes", "Song": "Song of Solomon", "Isa": "Isaiah",
    "Jer": "Jeremiah", "Lam": "Lamentations", "Ezek": "Ezekiel", "Dan": "Daniel",
    "Hos": "Hosea", "Joel": "Joel", "Amos": "Amos", "Obad": "Obadiah",
    "Jonah": "Jonah", "Mic": "Micah", "Nah": "Nahum", "Hab": "Habakkuk",
    "Zeph": "Zephaniah", "Hag": "Haggai", "Zech": "Zechariah", "Mal": "Malachi",
}

POETIC_WISDOM_BOOKS = {"Ps", "Prov", "Job", "Eccl", "Song"}
PROPHETIC_BOOKS = {"Isa", "Jer", "Lam", "Ezek", "Hos", "Joel", "Amos", "Obad", "Jonah", "Mic", "Nah", "Hab", "Zeph", "Hag", "Zech", "Mal"}
MEMORABLE_LEMMAS = {
    "1288": "祝福", "2617": "慈愛", "530": "信實", "3444": "救恩",
    "7965": "平安", "2451": "智慧", "998": "聰明", "3374": "敬畏",
    "8451": "訓誨／律法", "4687": "誡命", "6662": "公義",
    "3034": "稱謝／讚美", "1984": "讚美", "6419": "祈禱", "7812": "敬拜",
    "3176": "盼望", "539": "相信／堅定", "2142": "記念",
}
TECHNICAL_OR_VIOLENT_LEMMAS = {
    "4191": "死亡敘述", "2026": "殺戮", "2719": "刀劍", "4421": "戰爭",
    "5221": "擊殺", "2076": "宰祭牲", "5930": "燔祭", "2403": "贖罪祭",
    "1320": "祭肉／肉", "1818": "血", "8313": "焚燒", "6999": "獻香／煙祭",
}


@dataclass(frozen=True)
class VocabItem:
    ordinal: int
    lesson: int
    pointed: str
    lemma: str
    strongs: tuple[str, ...]
    item_kind: str
    is_proper: bool
    proper_types: tuple[str, ...]
    bound_codes: frozenset[str]
    part_of_speech: str

    @property
    def is_function(self) -> bool:
        return self.item_kind == "bound_morpheme" or self.part_of_speech in FUNCTION_POS

    def public_record(self) -> dict[str, Any]:
        return {
            "ordinal": self.ordinal,
            "pointed": self.pointed,
            "lemma": self.lemma,
            "strongs": [f"H{s}" for s in self.strongs],
            "isProperName": self.is_proper,
            "properNameTypes": list(self.proper_types),
        }


@dataclass(frozen=True)
class Token:
    text: str
    lemma_raw: str
    strongs: frozenset[str]
    lemma_codes: frozenset[str]
    morph: str


@dataclass(frozen=True)
class Verse:
    ref: str
    book: str
    chapter: int
    verse: int
    source_file: str
    text: str
    tokens: tuple[Token, ...]

    @property
    def tie_key(self) -> tuple[str, int, int]:
        return (self.book, self.chapter, self.verse)


@dataclass
class ScoredVerse:
    verse: Verse
    matched: list[VocabItem]
    matched_weight: float
    known_coverage: float
    score: float
    selection_reason: str


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def strong_numbers(value: Any) -> tuple[str, ...]:
    """Return stable bare numeric Strong IDs from any curriculum representation."""
    values: list[str] = []
    if isinstance(value, list):
        values.extend(str(item) for item in value)
    elif value not in (None, ""):
        values.append(str(value))
    result: list[str] = []
    for raw in values:
        for number in STRONG_RE.findall(raw):
            normalized = str(int(number))
            if normalized not in result:
                result.append(normalized)
    return tuple(result)


def load_vocabulary(path: Path) -> dict[int, list[VocabItem]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if len(raw) != 1000:
        raise ValueError(f"Vocabulary must contain exactly 1000 entries, found {len(raw)}")
    lessons: dict[int, list[VocabItem]] = {lesson: [] for lesson in range(1, 51)}
    for item in raw:
        lesson = int(item["lesson"])
        unpointed = str(item.get("unpointed") or "")
        strongs = strong_numbers(item.get("strongs") or item.get("strong"))
        bound_codes = frozenset(BOUND_LEMMA_CODES.get(unpointed, set())) if not strongs else frozenset()
        lessons[lesson].append(
            VocabItem(
                ordinal=int(item["ordinal"]),
                lesson=lesson,
                pointed=str(item.get("pointed") or item.get("sourcePointed") or unpointed),
                lemma=(f"H{strongs[0]}" if strongs else unpointed),
                strongs=strongs,
                item_kind=str(item.get("itemKind") or "lexeme"),
                is_proper=bool(item.get("isProperName")),
                proper_types=tuple(item.get("properNameTypes") or ()),
                bound_codes=bound_codes,
                part_of_speech=str(item.get("partOfSpeech") or ""),
            )
        )
    for lesson, entries in lessons.items():
        entries.sort(key=lambda x: x.ordinal)
        if len(entries) != 20:
            raise ValueError(f"Lesson {lesson} must contain 20 entries, found {len(entries)}")
    return lessons


def _clean_word(text: str | None) -> str:
    return (text or "").replace("/", "").strip()


def _token_from_element(elem: ET.Element) -> Token:
    lemma_raw = elem.get("lemma", "")
    lemma_parts = tuple(part.strip() for part in lemma_raw.split("/") if part.strip())
    return Token(
        text=_clean_word(elem.text),
        lemma_raw=lemma_raw,
        strongs=frozenset(strong_numbers(lemma_raw)),
        lemma_codes=frozenset(part for part in lemma_parts if not STRONG_RE.search(part)),
        morph=elem.get("morph", ""),
    )


def _append_word(parts: list[str], word: str) -> None:
    if not word:
        return
    if parts and not parts[-1].endswith((" ", "־")):
        parts.append(" ")
    parts.append(word)


def _append_segment(parts: list[str], elem: ET.Element) -> None:
    segment = (elem.text or "").strip()
    seg_type = elem.get("type", "")
    if not segment or seg_type in {"x-pe", "x-samekh"}:
        return
    if seg_type == "x-maqqef" or segment == "־":
        while parts and parts[-1] == " ":
            parts.pop()
        parts.append("־")
    elif seg_type == "x-sof-pasuq" or segment == "׃":
        while parts and parts[-1] == " ":
            parts.pop()
        parts.append("׃")
    elif seg_type == "x-paseq" or segment == "׀":
        if parts and not parts[-1].endswith(" "):
            parts.append(" ")
        parts.extend(["׀", " "])


def _walk_reading(elem: ET.Element, parts: list[str], tokens: list[Token]) -> None:
    """Walk direct OSIS content, selecting Qere and suppressing Ketiv."""
    for child in list(elem):
        name = local_name(child.tag)
        if name == "w":
            if child.get("type") == "x-ketiv":
                continue
            token = _token_from_element(child)
            if token.text:
                tokens.append(token)
                _append_word(parts, token.text)
        elif name == "seg":
            _append_segment(parts, child)
        elif name == "note":
            for rdg in child.iter(f"{OSIS_NS}rdg"):
                if rdg.get("type") == "x-qere":
                    _walk_reading(rdg, parts, tokens)
        else:
            _walk_reading(child, parts, tokens)


def is_strictly_pointed(tokens: Sequence[Token], text: str) -> bool:
    if not tokens or not CANTILLATION_RE.search(text) or not text.rstrip().endswith("׃"):
        return False
    for token in tokens:
        letters = HEBREW_LETTER_RE.findall(token.text)
        if not letters:
            continue
        # Single-letter bound particles may rely on a dot/shewa; all longer
        # orthographic words must carry an explicit Masoretic vowel sign.
        if not NIQQUD_RE.search(token.text):
            return False
    return True


def load_wlc(wlc_dir: Path) -> list[Verse]:
    verses: list[Verse] = []
    xml_files = sorted(path for path in wlc_dir.glob("*.xml") if path.name != "VerseMap.xml")
    if not xml_files:
        raise FileNotFoundError(f"No WLC XML files found under {wlc_dir}")
    for path in xml_files:
        root = ET.parse(path).getroot()
        for elem in root.iter(f"{OSIS_NS}verse"):
            ref = elem.get("osisID", "")
            ref_parts = ref.rsplit(".", 2)
            if len(ref_parts) != 3 or not ref_parts[1].isdigit() or not ref_parts[2].isdigit():
                continue
            parts: list[str] = []
            tokens: list[Token] = []
            _walk_reading(elem, parts, tokens)
            text = "".join(parts).strip()
            if not is_strictly_pointed(tokens, text):
                continue
            verses.append(
                Verse(
                    ref=ref,
                    book=ref_parts[0],
                    chapter=int(ref_parts[1]),
                    verse=int(ref_parts[2]),
                    source_file=str(path.relative_to(ROOT)).replace("\\", "/"),
                    text=text,
                    tokens=tuple(tokens),
                )
            )
    if len(verses) < 20_000:
        raise ValueError(f"Strict pointed-Qere corpus unexpectedly small: {len(verses)} verses")
    return verses


def _phrase_matches(item: VocabItem, tokens: Sequence[Token]) -> bool:
    """Match a multi-lexeme entry in order, allowing one intervening token."""
    needed = list(item.strongs)
    if not needed:
        return False
    for start, token in enumerate(tokens):
        if needed[0] not in token.strongs:
            continue
        cursor = start + 1
        complete = True
        for strong in needed[1:]:
            found = next(
                (index for index in range(cursor, min(len(tokens), cursor + 3)) if strong in tokens[index].strongs),
                None,
            )
            if found is None:
                complete = False
                break
            cursor = found + 1
        if complete:
            return True
    return False


def item_matches(item: VocabItem, tokens: Sequence[Token]) -> bool:
    if item.item_kind == "multi_lexeme_phrase":
        return _phrase_matches(item, tokens)
    if item.strongs:
        return any(bool(set(item.strongs) & token.strongs) for token in tokens)
    if item.bound_codes:
        return any(bool(item.bound_codes & token.lemma_codes) for token in tokens)
    return False


def chapter_map(plan: dict[str, Any]) -> dict[int, str]:
    """Map lessons 1-25 to the 25 approved chapters in difficulty order."""
    # This explicit order is authoritative even during the short interval in
    # which another process may still be rebuilding scripture-plan.json.
    return {lesson: ref for lesson, ref in enumerate(APPROVED_CHAPTERS, start=1)}


def score_verse(
    verse: Verse,
    matched: list[VocabItem],
    known_coverage: float,
    preferred_chapter: str | None,
    min_tokens: int = 6,
    max_tokens: int = 24,
) -> ScoredVerse | None:
    token_count = len(verse.tokens)
    if token_count < min_tokens or token_count > max_tokens:
        return None
    matched_weight = sum(0.22 if item.is_function else 1.12 if item.is_proper else 1.0 for item in matched)
    content_matches = sum(not item.is_function for item in matched)
    function_matches = len(matched) - content_matches
    proper_matches = sum(item.is_proper for item in matched)

    lexical_tokens = [token for token in verse.tokens if token.strongs]

    # Content-word matches dominate.  Function words contribute, but cannot by
    # themselves make a fragment outrank a coherent verse with one more lexeme.
    score = content_matches * 100.0 + function_matches * 18.0
    score += proper_matches * 2.2
    score += known_coverage * 14.0

    length_distance = abs(token_count - 13)
    score += max(0.0, 8.0 - length_distance * 0.65)
    if preferred_chapter and f"{verse.book}.{verse.chapter}" == preferred_chapter:
        score += 2.5

    finite_count = sum(bool(FINITE_VERB_RE.search(token.morph)) for token in verse.tokens)
    score += min(finite_count, 2) * 2.5
    if verse.tokens and ("834" in verse.tokens[0].strongs or "3588" in verse.tokens[0].strongs):
        score -= 2.0  # mild penalty for an initially dependent clause

    reason_bits = [f"本課新詞{len(matched)}個（實詞{content_matches}、虛詞{function_matches}）"]
    if any(item.is_proper for item in matched):
        reason_bits.append("含本課專名")
    reason_bits.append(f"累積已學詞覆蓋{known_coverage:.0%}")
    if preferred_chapter and f"{verse.book}.{verse.chapter}" == preferred_chapter:
        reason_bits.append("出自本課完整章")
    reason_bits.append(f"長度{token_count}詞")
    return ScoredVerse(verse, matched, matched_weight, known_coverage, score, "；".join(reason_bits))


def hard_exclusion_reason(verse: Verse) -> str | None:
    """Reject enumerations and morphologically incomplete fragments."""
    if verse.chapter in LIST_CHAPTERS.get(verse.book, set()):
        return "族譜／人口／官員／貢物／器材清單章段"
    token_count = len(verse.tokens)
    if token_count < 6:
        return "過短或題記"
    if token_count > 24:
        return "過長"
    lexical = [token for token in verse.tokens if token.strongs]
    finite_count = sum(bool(FINITE_VERB_RE.search(token.morph)) for token in verse.tokens)
    proper_count = sum("Np" in token.morph or "/Np" in token.morph for token in lexical)
    number_count = sum(bool(NUMBER_MORPH_RE.search(token.morph)) for token in lexical)
    if lexical and proper_count / len(lexical) >= 0.42 and finite_count == 0:
        return "專名列舉"
    if number_count >= 3 and finite_count == 0:
        return "數字／人口／貢物列舉"
    strong_counts = Counter(strong for token in lexical for strong in token.strongs)
    if finite_count == 0 and strong_counts and max(strong_counts.values()) >= 3:
        return "重複名詞清單"
    if finite_count == 0:
        nominal_signal = any(
            token.morph.startswith(("HP", "HA"))
            or bool(token.strongs & {"369", "3426", "3808", "408"})
            for token in lexical
        )
        poetic_nominal = verse.book in {"Ps", "Job", "Prov", "Song", "Eccl"} and len(lexical) >= 5
        if not nominal_signal and not poetic_nominal:
            return "缺少完整謂述"
    return None


def lemma_counter(verse: Verse) -> Counter[str]:
    return Counter(strong for token in verse.tokens for strong in token.strongs)


def is_near_duplicate(verse: Verse, accepted: Sequence[Verse]) -> bool:
    current = lemma_counter(verse)
    if not current:
        return False
    for prior in accepted:
        other = lemma_counter(prior)
        if current == other:
            return True
        intersection = sum((current & other).values())
        union = sum((current | other).values())
        if union and intersection / union >= 0.82 and abs(sum(current.values()) - sum(other.values())) <= 2:
            return True
    return False


def load_chinese_translation(path: Path) -> dict[str, str]:
    """Load strict RCUV2010 and map its numbering to WLC/MT references."""
    if not path.exists():
        return {}
    index, _ = load_rcuv_snapshot(path)
    wanted = {name: code for code, name in CHINESE_BOOK_NAMES.items()}
    translations: dict[str, str] = {}
    for (book_name, chapter, verse), record in index.items():
        code = wanted.get(book_name)
        if code:
            translations[f"{code}.{chapter}.{verse}"] = str(record.get("text") or "")

    # Derive every Psalm offset from the complete local WLC counts.
    psalm_counts: dict[int, int] = {}
    ps_path = DEFAULT_WLC / "Ps.xml"
    if ps_path.exists():
        ps_root = ET.parse(ps_path).getroot()
        for chapter in ps_root.iter(f"{OSIS_NS}chapter"):
            chapter_ref = chapter.get("osisID", "")
            if not chapter_ref.startswith("Ps."):
                continue
            chapter_number = int(chapter_ref.split(".")[1])
            mt_count = sum(1 for _ in chapter.iter(f"{OSIS_NS}verse"))
            psalm_counts[chapter_number] = mt_count
        for chapter_number, mt_count in psalm_counts.items():
            for mt_verse in range(1, mt_count + 1):
                chinese = translation_for_mt(
                    index,
                    "Psalms",
                    chapter_number,
                    mt_verse,
                    mt_psalm_counts=psalm_counts,
                )
                if chinese:
                    translations[f"Ps.{chapter_number}.{mt_verse}"] = chinese

    # Explicit non-Psalm MT/common-Protestant numbering differences.
    for mt_verse in range(1, 21):
        chinese = translation_for_mt(index, "Isaiah", 9, mt_verse)
        if chinese:
            translations[f"Isa.9.{mt_verse}"] = chinese
    for mt_verse in range(1, 11):
        chinese = translation_for_mt(index, "Hosea", 14, mt_verse)
        if chinese:
            translations[f"Hos.14.{mt_verse}"] = chinese
    return translations


def canonical_memorability(verse: Verse) -> dict[str, Any]:
    """Transparent literary proxy for human review, not a canon judgment."""
    score = 0.0
    positives: list[str] = []
    negatives: list[str] = []
    if verse.book == "Ps":
        score += 20
        positives.append("詩篇禱告／讚美體裁")
    elif verse.book == "Prov":
        score += 19
        positives.append("箴言格言體裁")
    elif verse.book == "Deut":
        score += 12
        positives.append("申命記勸勉／盟約體裁")
    elif verse.book in PROPHETIC_BOOKS:
        score += 10
        positives.append("先知宣告／應許體裁")
    elif verse.book in {"Job", "Eccl"}:
        score += 9
        positives.append("智慧文學體裁")
    elif verse.book == "Song":
        score += 7
        positives.append("詩歌體裁")

    strongs = {strong for token in verse.tokens for strong in token.strongs}
    for strong, label in MEMORABLE_LEMMAS.items():
        if strong in strongs:
            score += 4
            positives.append(label)
    for strong, label in TECHNICAL_OR_VIOLENT_LEMMAS.items():
        if strong in strongs:
            score -= 7
            negatives.append(label)

    finite_count = sum(bool(FINITE_VERB_RE.search(token.morph)) for token in verse.tokens)
    if 1 <= finite_count <= 3:
        score += 4
        positives.append("句法自足")
    elif finite_count >= 6:
        score -= 3
        negatives.append("敘事動作密集")

    # Narrative logistics are grammatically complete but seldom good first
    # choices for memorization.  This penalty merely orders review candidates.
    narrative_logistics = len(strongs & {"3212", "935", "3947", "5414", "7971", "6965"})
    if verse.book not in POETIC_WISDOM_BOOKS | PROPHETIC_BOOKS and narrative_logistics >= 3:
        score -= 6
        negatives.append("行程／操作性敘事")

    if score >= 22:
        tier = "high"
    elif score >= 10:
        tier = "medium"
    else:
        tier = "low"
    rationale = "；".join(positives[:4]) or "一般敘事／律例候選"
    if negatives:
        rationale += "；降權：" + "、".join(negatives[:4])
    return {
        "score": round(score, 2),
        "tier": tier,
        "positiveSignals": positives,
        "negativeSignals": negatives,
        "rationale": rationale,
    }


def _match_lesson_items(verse: Verse, lesson_vocab: Sequence[VocabItem]) -> list[VocabItem]:
    matched = [item for item in lesson_vocab if item_matches(item, verse.tokens)]
    return sorted(matched, key=lambda item: item.ordinal)


def build_candidate_review(
    verses: Sequence[Verse],
    lessons: dict[int, list[VocabItem]],
    plan: dict[str, Any],
    translations: dict[str, str],
    per_lesson: int = 15,
) -> dict[str, Any]:
    preferred = chapter_map(plan)
    excluded: Counter[str] = Counter()
    exclusion_by_ref: dict[str, str] = {}
    eligible: list[Verse] = []
    for verse in verses:
        reason = hard_exclusion_reason(verse)
        if reason:
            excluded[reason] += 1
            exclusion_by_ref[verse.ref] = reason
        eligible.append(verse)

    first_learned: dict[str, int] = {}
    for lesson, lesson_vocab in lessons.items():
        for item in lesson_vocab:
            for strong in item.strongs:
                first_learned.setdefault(strong, lesson)
    thresholds_by_ref: dict[str, tuple[int, ...]] = {}
    for verse in eligible:
        thresholds_by_ref[verse.ref] = tuple(
            sorted(
                min((first_learned.get(strong, 51) for strong in token.strongs), default=51)
                for token in verse.tokens
                if token.strongs
            )
        )

    review_lessons: list[dict[str, Any]] = []
    for lesson in range(1, 51):
        by_strong: dict[str, list[VocabItem]] = {}
        by_code: dict[str, list[VocabItem]] = {}
        phrases: list[VocabItem] = []
        for item in lessons[lesson]:
            if item.item_kind == "multi_lexeme_phrase":
                phrases.append(item)
            elif item.strongs:
                for strong in item.strongs:
                    by_strong.setdefault(strong, []).append(item)
            else:
                for code in item.bound_codes:
                    by_code.setdefault(code, []).append(item)
        pool: list[tuple[float, ScoredVerse, dict[str, Any]]] = []
        for verse in eligible:
            matched_by_ordinal: dict[int, VocabItem] = {}
            for token in verse.tokens:
                for strong in token.strongs:
                    for item in by_strong.get(strong, ()):
                        matched_by_ordinal[item.ordinal] = item
                for code in token.lemma_codes:
                    for item in by_code.get(code, ()):
                        matched_by_ordinal[item.ordinal] = item
            for item in phrases:
                if _phrase_matches(item, verse.tokens):
                    matched_by_ordinal[item.ordinal] = item
            matched = sorted(matched_by_ordinal.values(), key=lambda item: item.ordinal)
            if not matched:
                continue
            thresholds = thresholds_by_ref[verse.ref]
            coverage = bisect.bisect_right(thresholds, lesson) / len(thresholds) if thresholds else 0.0
            scored = score_verse(verse, matched, coverage, preferred.get(lesson), min_tokens=1, max_tokens=100)
            if scored is None:
                continue
            canonical = canonical_memorability(verse)
            review_score = scored.score + float(canonical["score"]) * 2.5
            if verse.ref in exclusion_by_ref:
                review_score -= 120.0
            if len(matched) < 2:
                review_score -= 150.0
            pool.append((review_score, scored, canonical))
        pool.sort(
            key=lambda row: (
                -row[0], -len([item for item in row[1].matched if not item.is_function]),
                -len(row[1].matched), -row[1].known_coverage, row[1].verse.tie_key,
            )
        )

        chosen: list[tuple[float, ScoredVerse, dict[str, Any]]] = []
        used_refs: set[str] = set()
        for max_per_book, max_per_chapter in ((2, 1), (3, 2), (99, 99)):
            book_counts = Counter(row[1].verse.book for row in chosen)
            chapter_counts = Counter(f"{row[1].verse.book}.{row[1].verse.chapter}" for row in chosen)
            for row in pool:
                verse = row[1].verse
                chapter_ref = f"{verse.book}.{verse.chapter}"
                if verse.ref in used_refs:
                    continue
                if book_counts[verse.book] >= max_per_book or chapter_counts[chapter_ref] >= max_per_chapter:
                    continue
                if max_per_book < 99 and is_near_duplicate(verse, [item[1].verse for item in chosen]):
                    continue
                chosen.append(row)
                used_refs.add(verse.ref)
                book_counts[verse.book] += 1
                chapter_counts[chapter_ref] += 1
                if len(chosen) >= per_lesson:
                    break
            if len(chosen) >= per_lesson:
                break
        if len(chosen) < per_lesson:
            raise ValueError(f"Candidate diversity gate failed for lesson {lesson}: {len(chosen)}")

        records: list[dict[str, Any]] = []
        for rank, (review_score, scored, canonical) in enumerate(chosen[:per_lesson], start=1):
            verse = scored.verse
            warnings = []
            if verse.ref in exclusion_by_ref:
                warnings.append(exclusion_by_ref[verse.ref])
            if len(scored.matched) < 2:
                warnings.append("本課詞僅命中1個（僅供人工例外評估）")
            records.append(
                {
                    "rank": rank,
                    "ref": verse.ref,
                    "text": verse.text,
                    "translationZh": translations.get(verse.ref) or None,
                    "translationZh": (translations or {}).get(verse.ref, ""),
                "matchedLessonVocabulary": [item.public_record() for item in scored.matched],
                    "matchedCount": len(scored.matched),
                    "matchedContentCount": sum(not item.is_function for item in scored.matched),
                    "knownCoverage": round(scored.known_coverage, 4),
                    "vocabularyScore": round(scored.score, 4),
                    "reviewScore": round(review_score, 4),
                    "selectionReason": scored.selection_reason,
                    "canonicalMemorability": canonical,
                    "hardExclusionWarning": "；".join(warnings) or None,
                    "sourceFile": verse.source_file,
                    "displayReading": "pointed-qere",
                }
            )
        strict_records = [record for record in records if not record["hardExclusionWarning"]]
        fallback_records = [record for record in records if record["hardExclusionWarning"]]
        review_lessons.append(
            {
                "lesson": lesson,
                "preferredChapterRef": preferred.get(lesson),
                "candidateCount": len(records),
                "strictCandidateCount": len(strict_records),
                "fallbackCandidateCount": len(fallback_records),
                "strictCandidates": strict_records,
                "fallbackCandidates": fallback_records,
            }
        )

    total = sum(row["candidateCount"] for row in review_lessons)
    if len(review_lessons) != 50 or total < 50 * per_lesson:
        raise ValueError("50-lesson / 15-candidate review gate failed")
    below_two = sum(
        candidate["matchedCount"] < 2
        for row in review_lessons
        for candidate in row["strictCandidates"] + row["fallbackCandidates"]
    )
    return {
        "schemaVersion": "1.0.0",
        "purpose": "Human review pool; these candidates do not overwrite scripture-plan memory selections.",
        "selectionStatus": "not-final",
        "source": plan.get("source") or {},
        "policy": {
            "minimumPerLesson": per_lesson,
            "matching": "MorphHB Strong/lemma identity, inflected forms included; pointed Qere display only.",
            "diversity": "First pass max 2 candidates per book and 1 per chapter; relaxed only if needed; near-duplicate lemma sets excluded.",
            "canonicalMemorability": "Transparent review proxy prioritizing Psalms, Proverbs, Deuteronomy, prophetic promises, wisdom, blessings, praise and prayer; penalizing death lists, warfare logistics and technical sacrificial handling.",
        },
        "summary": {
            "lessonCount": len(review_lessons),
            "candidateCount": total,
            "translationAvailableCount": sum(
                bool(candidate["translationZh"])
                for row in review_lessons
                for candidate in row["strictCandidates"] + row["fallbackCandidates"]
            ),
            "matchedCountBelow2": below_two,
            "hardExclusions": dict(sorted(excluded.items())),
        },
        "lessons": review_lessons,
    }


def _human_selection_reason(candidate: dict[str, Any]) -> str:
    matched = candidate["matchedLessonVocabulary"]
    terms = "、".join(f"{item['pointed']}（#{item['ordinal']}）" for item in matched)
    canonical = candidate.get("canonicalMemorability") or {}
    rationale = canonical.get("rationale") or "完整、可獨立理解的經句"
    if candidate["matchedCount"] < 2:
        return (
            f"人工可背性例外：本課僅直接命中1詞 {terms}，但本節是語意完整、經典且適合反覆背誦的經句"
            f"（{rationale}）；故優先於命中較多但屬名單、祭牲技術、戰爭操作或語意殘句的候選。"
        )
    return (
        f"人工審閱：本節語意可獨立成立，適合反覆背誦，並命中本課{candidate['matchedCount']}詞：{terms}。"
        f"在詞彙重合、累積覆蓋與可背性之間取平衡（{rationale}）。"
    )


def apply_reviewed_selection(
    plan: dict[str, Any],
    candidates: dict[str, Any],
    corpus: Sequence[Verse],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    if set(REVIEWED_SELECTIONS) != set(range(1, 51)):
        raise ValueError("Human-reviewed mapping must cover lessons 1-50")
    candidate_lessons = {int(row["lesson"]): row for row in candidates["lessons"]}
    verse_by_ref = {verse.ref: verse for verse in corpus}
    source = plan.get("source") or {}
    memory_lessons: list[dict[str, Any]] = []
    flat: list[dict[str, Any]] = []
    accepted: list[Verse] = []
    review_lines = [
        "# 希伯來文背誦經文人工審閱定稿",
        "",
        "本表為50課、每課2節的人工可背性定稿。詞彙命中以 MorphHB Strong／lemma 身分計算；屈折形式視為同一詞元。母音與重音採 WLC 的 pointed Qere 顯示。",
        "",
    ]
    for lesson in range(1, 51):
        lesson_pool = candidate_lessons[lesson]
        pool = {
            candidate["ref"]: candidate
            for candidate in lesson_pool["strictCandidates"] + lesson_pool["fallbackCandidates"]
        }
        rows: list[dict[str, Any]] = []
        review_lines.extend([f"## 第{lesson}課", ""])
        for slot, ref in enumerate(REVIEWED_SELECTIONS[lesson], start=1):
            if ref not in pool:
                raise ValueError(f"Reviewed selection {ref} is not in lesson {lesson} candidate pool")
            candidate = pool[ref]
            verse = verse_by_ref.get(ref)
            if verse is None:
                raise ValueError(f"Reviewed selection missing from pointed-Qere corpus: {ref}")
            if any(prior.ref == ref for prior in accepted):
                raise ValueError(f"Duplicate reviewed selection: {ref}")
            if is_near_duplicate(verse, accepted):
                raise ValueError(f"Near-duplicate lemma set in reviewed selection: {ref}")
            accepted.append(verse)
            book, chapter, verse_number = ref.rsplit(".", 2)
            reason = _human_selection_reason(candidate)
            record = {
                "lesson": lesson,
                "slot": slot,
                "bookCode": book,
                "osisBook": book,
                "chapter": int(chapter),
                "verse": int(verse_number),
                "ref": ref,
                "source": source.get("name", "Open Scriptures Hebrew Bible (OSHB)"),
                "version": source.get("version", "WLC 4.20"),
                "sourceFile": candidate["sourceFile"],
                "sourceOsisId": ref,
                "displayReading": "pointed-qere",
                "text": candidate["text"],
                "translationZh": candidate.get("translationZh"),
                "matchedLessonVocabulary": candidate["matchedLessonVocabulary"],
                "matchedCount": candidate["matchedCount"],
                "matchedContentCount": candidate.get("matchedContentCount"),
                "knownCoverage": candidate["knownCoverage"],
                "score": candidate["reviewScore"],
                "canonicalMemorability": candidate["canonicalMemorability"],
                "selectionReview": "human-reviewed-memorability",
                "selectionReason": reason,
            }
            rows.append(record)
            flat.append(record.copy())
            matched_md = "、".join(
                f"{item['pointed']}（#{item['ordinal']}）" for item in candidate["matchedLessonVocabulary"]
            )
            review_lines.extend(
                [
                    f"### {slot}. {ref}",
                    "",
                    f"- 原文：{candidate['text']}",
                    f"- 繁中：{candidate.get('translationZh') or '本機版本無對應分節譯文'}",
                    f"- 本課命中：{candidate['matchedCount']}詞；{matched_md}",
                    f"- 累積已學詞覆蓋：{candidate['knownCoverage']:.1%}",
                    f"- 審閱理由：{reason}",
                    "",
                ]
            )
        memory_lessons.append(
            {
                "lesson": lesson,
                "preferredChapterRef": chapter_map(plan).get(lesson),
                "selectionReview": "human-reviewed-memorability",
                "verses": rows,
            }
        )

    if len(flat) != 100 or len({row["ref"] for row in flat}) != 100:
        raise ValueError("Reviewed 100-unique gate failed")
    if any(len(row["verses"]) != 2 for row in memory_lessons):
        raise ValueError("Reviewed 50x2 gate failed")
    selected_refs = {row["ref"] for row in flat}
    for lesson in candidates["lessons"]:
        for candidate in lesson["strictCandidates"] + lesson["fallbackCandidates"]:
            candidate["selectedFinal"] = candidate["ref"] in selected_refs and candidate["ref"] in REVIEWED_SELECTIONS[int(lesson["lesson"])]
    candidates["selectionStatus"] = "human-reviewed-final-linked"
    candidates["summary"]["finalSelectionCount"] = len(flat)
    candidates["summary"]["finalSelectionMatchedCountBelow2"] = sum(row["matchedCount"] < 2 for row in flat)
    candidates["finalSelectionRefsByLesson"] = {
        str(lesson): list(refs) for lesson, refs in REVIEWED_SELECTIONS.items()
    }
    return memory_lessons, flat, "\n".join(review_lines).rstrip() + "\n"


def select_memory_verses(
    verses: Sequence[Verse],
    lessons: dict[int, list[VocabItem]],
    plan: dict[str, Any],
    translations: Mapping[str, str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], Counter[str]]:
    preferred = chapter_map(plan)
    excluded: Counter[str] = Counter()
    eligible: list[Verse] = []
    for verse in verses:
        reason = hard_exclusion_reason(verse)
        if reason:
            excluded[reason] += 1
        else:
            eligible.append(verse)
    first_learned: dict[str, int] = {}
    for lesson, lesson_vocab in lessons.items():
        for item in lesson_vocab:
            for strong in item.strongs:
                first_learned.setdefault(strong, lesson)
    known_thresholds: dict[str, tuple[int, ...]] = {}
    for verse in verses:
        thresholds = []
        for token in verse.tokens:
            if not token.strongs:
                continue
            thresholds.append(min((first_learned.get(s, 51) for s in token.strongs), default=51))
        known_thresholds[verse.ref] = tuple(sorted(thresholds))

    ranked: dict[int, list[ScoredVerse]] = {}

    relaxed: dict[int, list[ScoredVerse]] = {}
    for lesson in range(1, 51):
        by_strong: dict[str, list[VocabItem]] = {}
        by_code: dict[str, list[VocabItem]] = {}
        phrases: list[VocabItem] = []
        for item in lessons[lesson]:
            if item.item_kind == "multi_lexeme_phrase":
                phrases.append(item)
            elif item.strongs:
                for strong in item.strongs:
                    by_strong.setdefault(strong, []).append(item)
            else:
                for code in item.bound_codes:
                    by_code.setdefault(code, []).append(item)

        def candidates(min_matches: int = 2) -> Iterable[ScoredVerse]:
            for verse in eligible:
                matched_by_ordinal: dict[int, VocabItem] = {}
                for token in verse.tokens:
                    for strong in token.strongs:
                        for item in by_strong.get(strong, ()):
                            matched_by_ordinal[item.ordinal] = item
                    for code in token.lemma_codes:
                        for item in by_code.get(code, ()):
                            matched_by_ordinal[item.ordinal] = item
                for item in phrases:
                    if _phrase_matches(item, verse.tokens):
                        matched_by_ordinal[item.ordinal] = item
                matched = sorted(matched_by_ordinal.values(), key=lambda item: item.ordinal)
                if len(matched) < min_matches:
                    continue
                thresholds = known_thresholds[verse.ref]
                coverage = bisect.bisect_right(thresholds, lesson) / len(thresholds) if thresholds else 0.0
                candidate = score_verse(verse, matched, coverage, preferred.get(lesson))
                if candidate is not None:
                    yield candidate

        sort_key = lambda row: (
            -row.score,
            -len(row.matched),
            -row.known_coverage,
            abs(len(row.verse.tokens) - 13),
            row.verse.tie_key,
        )
        # Only 100 references can be consumed globally; retaining the best 500
        # per lesson is sufficient for collision resolution and avoids sorting
        # the entire 20k+ verse corpus fifty times.
        ranked[lesson] = sorted(
            heapq.nsmallest(500, candidates(), key=sort_key),
            key=sort_key,
        )
        # The last lessons carry the rarest words in the curriculum, and for some
        # of them no verse in the Hebrew Bible contains two of the twenty at
        # once.  Rather than fail the release or quietly pad the lesson with an
        # unrelated verse, keep a single-match tier and mark what it is.
        relaxed[lesson] = sorted(
            heapq.nsmallest(500, candidates(min_matches=1), key=sort_key),
            key=sort_key,
        )

    used: set[str] = set()
    single_match_lessons: set[int] = set()
    accepted_verses: list[Verse] = []
    selected: dict[int, list[ScoredVerse]] = {lesson: [] for lesson in range(1, 51)}
    # Round-robin slots stop early lessons from consuming both of a later
    # lesson's strongest candidates before that lesson gets a first choice.
    for _slot in range(2):
        for lesson in range(1, 51):
            def acceptable(row: ScoredVerse) -> bool:
                if row.verse.ref in used or is_near_duplicate(row.verse, accepted_verses):
                    return False
                content = [item for item in row.matched if not item.is_function]
                proper_dependent = len(content) == 2 and all(item.is_proper for item in content)
                already_has_proper_dependent = any(
                    len([item for item in prior.matched if not item.is_function]) == 2
                    and all(item.is_proper for item in prior.matched if not item.is_function)
                    for prior in selected[lesson]
                )
                return not (proper_dependent and already_has_proper_dependent)

            choice = next((row for row in ranked[lesson] if acceptable(row)), None)
            if choice is None:
                choice = next((row for row in relaxed[lesson] if acceptable(row)), None)
                if choice is not None:
                    single_match_lessons.add(lesson)
            if choice is None:
                raise ValueError(f"No unique candidate remains for lesson {lesson}")
            selected[lesson].append(choice)
            used.add(choice.verse.ref)
            accepted_verses.append(choice.verse)

    if len(used) != 100:
        raise ValueError(f"Unique memory-verse gate failed: expected 100, found {len(used)}")

    source = plan.get("source") or {}
    memory_lessons: list[dict[str, Any]] = []
    flat: list[dict[str, Any]] = []
    for lesson in range(1, 51):
        rows: list[dict[str, Any]] = []
        for slot, scored in enumerate(selected[lesson], start=1):
            verse = scored.verse
            record = {
                "lesson": lesson,
                "slot": slot,
                "bookCode": verse.book,
                "osisBook": verse.book,
                "chapter": verse.chapter,
                "verse": verse.verse,
                "ref": verse.ref,
                "source": source.get("name", "Open Scriptures Hebrew Bible (OSHB)"),
                "version": source.get("version", "WLC 4.20"),
                "sourceFile": verse.source_file,
                "sourceOsisId": verse.ref,
                "displayReading": "pointed-qere",
                "text": verse.text,
                "translationZh": (translations or {}).get(verse.ref, ""),
                "matchedLessonVocabulary": [item.public_record() for item in scored.matched],
                "matchedCount": len(scored.matched),
                "matchedWeightedCount": round(scored.matched_weight, 2),
                "knownCoverage": round(scored.known_coverage, 4),
                "score": round(scored.score, 4),
                "selectionReason": scored.selection_reason,
            }
            rows.append(record)
            flat.append(record.copy())
        if len(rows) != 2:
            raise ValueError(f"Two-verses-per-lesson gate failed for lesson {lesson}")
        memory_lessons.append(
            {
                "lesson": lesson,
                "preferredChapterRef": preferred.get(lesson),
                "verses": rows,
            }
        )
    return memory_lessons, flat, excluded


def update_plan(plan: dict[str, Any], memory_lessons: list[dict[str, Any]], flat: list[dict[str, Any]]) -> None:
    plan["memoryLessons"] = memory_lessons
    plan["memoryVerses"] = flat
    summary = plan.setdefault("summary", {})
    summary["memoryLessonCount"] = len(memory_lessons)
    summary["memoryVerseCount"] = len(flat)
    validation = plan.setdefault("validation", {})
    validation.update(
        {
            "memoryLessonCountExpected": 50,
            "memoryLessonCountActual": len(memory_lessons),
            "memoryVersesPerLessonExpected": 2,
            "memoryVerseCountExpected": 100,
            "memoryVerseCountActual": len(flat),
            "duplicateMemoryRefCount": len(flat) - len({row["ref"] for row in flat}),
        }
    )
    validation["passed"] = (
        len(memory_lessons) == 50
        and len(flat) == 100
        and validation["duplicateMemoryRefCount"] == 0
        and all(len(row["verses"]) == 2 for row in memory_lessons)
    )


def print_report(memory_lessons: Sequence[dict[str, Any]], corpus_size: int, excluded: Counter[str]) -> None:
    flat = [verse for lesson in memory_lessons for verse in lesson["verses"]]
    verse_buckets = Counter("0" if row["matchedCount"] == 0 else "1" if row["matchedCount"] == 1 else "2+" for row in flat)
    lesson_buckets = Counter()
    for lesson in memory_lessons:
        unique_ordinals = {
            vocab["ordinal"]
            for row in lesson["verses"]
            for vocab in row["matchedLessonVocabulary"]
        }
        count = len(unique_ordinals)
        lesson_buckets["0" if count == 0 else "1" if count == 1 else "2+"] += 1
    print(f"strict_pointed_qere_corpus={corpus_size}")
    print(f"memory_lessons={len(memory_lessons)} memory_verses={len(flat)} unique_refs={len({row['ref'] for row in flat})}")
    print(f"verse_match_distribution 0={verse_buckets['0']} 1={verse_buckets['1']} 2+={verse_buckets['2+']}")
    print(f"lesson_unique_match_distribution 0={lesson_buckets['0']} 1={lesson_buckets['1']} 2+={lesson_buckets['2+']}")
    print("hard_exclusions " + " | ".join(f"{reason}={count}" for reason, count in sorted(excluded.items())))
    for lesson in memory_lessons:
        descriptions = []
        for row in lesson["verses"]:
            ordinals = ",".join(str(item["ordinal"]) for item in row["matchedLessonVocabulary"]) or "-"
            descriptions.append(
                f"{row['ref']} matches={row['matchedCount']}[{ordinals}] known={row['knownCoverage']:.0%} score={row['score']:.2f}"
            )
        print(f"L{lesson['lesson']:02d}: " + " | ".join(descriptions))


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vocabulary", type=Path, default=DEFAULT_VOCAB)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--wlc-dir", type=Path, default=DEFAULT_WLC)
    parser.add_argument("--chinese", type=Path, default=DEFAULT_CHINESE)
    parser.add_argument("--output", type=Path, help="Output plan path; defaults to --plan")
    parser.add_argument("--write", action="store_true", help="Write updated memoryLessons/memoryVerses")
    parser.add_argument("--write-candidates", action="store_true", help="Write the human-review candidate pool without changing the plan")
    parser.add_argument("--candidate-output", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--apply-reviewed-selection", action="store_true", help="Apply the explicit human-reviewed 50x2 selection to the plan")
    parser.add_argument("--review-output", type=Path, default=DEFAULT_REVIEW)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    lessons = load_vocabulary(args.vocabulary)
    verses = load_wlc(args.wlc_dir)
    if args.apply_reviewed_selection:
        candidates = json.loads(args.candidate_output.read_text(encoding="utf-8"))
        memory_lessons, flat, review_md = apply_reviewed_selection(plan, candidates, verses)
        update_plan(plan, memory_lessons, flat)
        plan.setdefault("selectionPolicy", {})["memorySelection"] = (
            "Human-reviewed memorability: vocabulary overlap is prioritized but not absolute; "
            "lists, census data, sacrificial handling, semantic fragments and near-duplicates are rejected."
        )
        plan["validation"].update(
            {
                "humanReviewedMemoryVerseCount": len(flat),
                "memoryVerseMatchedCountBelow2": sum(row["matchedCount"] < 2 for row in flat),
                "selectionReview": "human-reviewed-memorability",
            }
        )
        args.plan.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        args.candidate_output.write_text(json.dumps(candidates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        args.review_output.write_text(review_md, encoding="utf-8")
        print(
            f"reviewed_lessons={len(memory_lessons)} reviewed_verses={len(flat)} "
            f"unique_refs={len({row['ref'] for row in flat})} "
            f"matched_lt2={sum(row['matchedCount'] < 2 for row in flat)}"
        )
        print(f"wrote_plan={args.plan}")
        print(f"wrote_candidates={args.candidate_output}")
        print(f"wrote_review={args.review_output}")
        return 0
    if args.write_candidates:
        review = build_candidate_review(verses, lessons, plan, load_chinese_translation(args.chinese))
        args.candidate_output.parent.mkdir(parents=True, exist_ok=True)
        args.candidate_output.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(
            f"candidate_lessons={review['summary']['lessonCount']} "
            f"candidates={review['summary']['candidateCount']} "
            f"translations={review['summary']['translationAvailableCount']} "
            f"matched_lt2={review['summary']['matchedCountBelow2']}"
        )
        print(f"wrote_candidates={args.candidate_output}")
        return 0
    # The plan file is what the web reader and the print master read memory
    # verses from, so the Chinese has to be attached here and not only in the
    # assembled master; without it every verse renders with a blank translation.
    memory_lessons, flat, excluded = select_memory_verses(
        verses, lessons, plan, load_chinese_translation(args.chinese)
    )
    update_plan(plan, memory_lessons, flat)
    print_report(memory_lessons, len(verses), excluded)
    if args.write:
        output = args.output or args.plan
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"wrote={output}")
    else:
        print("dry_run=true (no files written; pass --write after chapter approval)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
