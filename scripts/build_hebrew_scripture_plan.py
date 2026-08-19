#!/usr/bin/env python3
"""Build the fixed 25-chapter Biblical Hebrew reading plan from local WLC.

This builder intentionally stops before selecting the 100 memory verses.  The
memory layer must be chosen only after the final 50 x 20 vocabulary curriculum
is available, so that each lesson's two verses can be ranked by vocabulary
overlap instead of inheriting an unrelated earlier selection.

The running ``text`` field preserves the source-oriented layer used by the
existing schema: direct OSIS ``<w>`` elements are emitted in document order,
including unpointed ketiv spellings, while the corresponding pointed qere
remains traceable in the source OSIS variant note.  The reader assembly step
may subsequently choose qere for learner-facing display.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
WLC_DIR = (
    ROOT
    / "output"
    / "source-cache"
    / "original-readers"
    / "morphhb-src"
    / "morphhb-master"
    / "wlc"
)
OUTPUT_PATH = (
    ROOT
    / "output"
    / "source-cache"
    / "original-readers"
    / "hebrew-full"
    / "scripture-plan.json"
)

OSIS_NS = "http://www.bibletechnologies.net/2003/OSIS/namespace"
NS = {"osis": OSIS_NS}

SOURCE_NAME = "Open Scriptures Hebrew Bible (OSHB), Westminster Leningrad Codex text"
SOURCE_VERSION = "WLC 4.20"
SOURCE_URL = "https://github.com/openscriptures/morphhb"

HEBREW_LETTER_RE = re.compile(r"[\u05d0-\u05ea]")
NIQQUD_RE = re.compile(r"[\u05b0-\u05bc\u05c1\u05c2\u05c7]")
CANTILLATION_RE = re.compile(r"[\u0591-\u05af]")


@dataclass(frozen=True)
class ChapterSpec:
    ordinal: int
    book_code: str
    osis_book: str
    chapter: int
    title_zh: str
    title_he: str
    corpus_section: str
    genre: str
    difficulty: int

    @property
    def ref(self) -> str:
        return f"{self.osis_book}.{self.chapter}"


# User-approved order, from easier to harder.  Difficulty is a five-band
# compatibility field; ordinal records the exact 1-25 pedagogical rank.
CHAPTERS: tuple[ChapterSpec, ...] = (
    ChapterSpec(1, "ps", "Ps", 136, "詩篇136：祂的慈愛永遠長存", "תְּהִלִּים קל״ו", "Writings", "liturgical-hymn", 1),
    ChapterSpec(2, "ps", "Ps", 23, "詩篇23：上主是我的牧者", "תְּהִלִּים כ״ג", "Writings", "poetry-prayer", 1),
    ChapterSpec(3, "ps", "Ps", 1, "詩篇1：兩條道路", "תְּהִלִּים א׳", "Writings", "wisdom-poetry", 1),
    ChapterSpec(4, "1sam", "1Sam", 3, "撒母耳記上3：撒母耳蒙召", "שְׁמוּאֵל א׳ ג׳", "Prophets", "call-narrative", 1),
    ChapterSpec(5, "gen", "Gen", 12, "創世記12：亞伯蘭蒙召", "בְּרֵאשִׁית י״ב", "Torah", "patriarchal-narrative", 1),
    ChapterSpec(6, "gen", "Gen", 1, "創世記1：創造", "בְּרֵאשִׁית א׳", "Torah", "creation-narrative", 2),
    ChapterSpec(7, "deut", "Deut", 6, "申命記6：示瑪與愛上主", "דְּבָרִים ו׳", "Torah", "covenant-exhortation", 2),
    ChapterSpec(8, "exod", "Exod", 20, "出埃及記20：十誡", "שְׁמוֹת כ׳", "Torah", "covenant-law", 2),
    ChapterSpec(9, "exod", "Exod", 3, "出埃及記3：燃燒的荊棘", "שְׁמוֹת ג׳", "Torah", "call-narrative", 2),
    ChapterSpec(10, "gen", "Gen", 3, "創世記3：人類違命", "בְּרֵאשִׁית ג׳", "Torah", "primeval-narrative", 2),
    ChapterSpec(11, "ezek", "Ezek", 37, "以西結書37：枯骨復生", "יְחֶזְקֵאל ל״ז", "Prophets", "prophetic-vision", 3),
    ChapterSpec(12, "2sam", "2Sam", 7, "撒母耳記下7：大衛之約", "שְׁמוּאֵל ב׳ ז׳", "Prophets", "covenant-oracle", 3),
    ChapterSpec(13, "eccl", "Eccl", 3, "傳道書3：萬事都有定時", "קֹהֶלֶת ג׳", "Writings", "wisdom-poetry", 3),
    ChapterSpec(14, "ps", "Ps", 51, "詩篇51：悔罪禱告", "תְּהִלִּים נ״א", "Writings", "penitential-prayer", 3),
    ChapterSpec(15, "isa", "Isa", 6, "以賽亞書6：先知蒙召", "יְשַׁעְיָהוּ ו׳", "Prophets", "prophetic-call-vision", 3),
    ChapterSpec(16, "1kgs", "1Kgs", 18, "列王紀上18：迦密山的決斷", "מְלָכִים א׳ י״ח", "Prophets", "prophetic-narrative", 4),
    ChapterSpec(17, "lev", "Lev", 19, "利未記19：你們要聖潔", "וַיִּקְרָא י״ט", "Torah", "holiness-law", 4),
    ChapterSpec(18, "song", "Song", 2, "雅歌2：愛與春日", "שִׁיר הַשִּׁירִים ב׳", "Writings", "love-poetry", 4),
    ChapterSpec(19, "isa", "Isa", 53, "以賽亞書53：受苦的僕人", "יְשַׁעְיָהוּ נ״ג", "Prophets", "servant-poem", 4),
    ChapterSpec(20, "isa", "Isa", 9, "以賽亞書9：黑暗中的大光", "יְשַׁעְיָהוּ ט׳", "Prophets", "prophetic-oracle-poetry", 4),
    ChapterSpec(21, "prov", "Prov", 8, "箴言8：智慧的呼喚", "מִשְׁלֵי ח׳", "Writings", "wisdom-poetry", 5),
    ChapterSpec(22, "jer", "Jer", 31, "耶利米書31：歸回與新約", "יִרְמְיָהוּ ל״א", "Prophets", "prophetic-oracle-covenant", 5),
    ChapterSpec(23, "exod", "Exod", 15, "出埃及記15：海之歌", "שְׁמוֹת ט״ו", "Torah", "archaic-victory-song", 5),
    ChapterSpec(24, "job", "Job", 28, "約伯記28：智慧何處可尋", "אִיּוֹב כ״ח", "Writings", "wisdom-poetry", 5),
    ChapterSpec(25, "judg", "Judg", 5, "士師記5：底波拉之歌", "שֹׁפְטִים ה׳", "Prophets", "archaic-victory-song", 5),
)


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def relative_posix(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def clean_word(text: str | None) -> str:
    return (text or "").replace("/", "").strip()


def append_piece(output: str, piece: str, kind: str) -> str:
    """Reproduce the established source-text spacing convention."""

    if not piece:
        return output
    if kind == "word":
        if output and not output.endswith((" ", "־")):
            output += " "
        return output + piece
    if kind == "x-maqqef":
        return output.rstrip() + "־"
    if kind == "x-sof-pasuq":
        return output.rstrip() + "׃"
    if kind == "x-paseq":
        return output.rstrip() + " ׀"
    if kind in {"x-pe", "x-samekh"}:
        return output.rstrip() + " " + piece.strip()
    # No selected source currently uses another running-text segment type, but
    # preserving its literal text is safer than silently discarding it.
    if output and not output.endswith(" "):
        output += " "
    return output + piece.strip()


def qere_words(note: ET.Element) -> list[str]:
    return [
        clean_word(word.text)
        for word in note.findall("./osis:rdg[@type='x-qere']/osis:w", NS)
        if clean_word(word.text)
    ]


def extract_verse(
    verse_element: ET.Element,
    *,
    spec: ChapterSpec,
    source_file: str,
) -> tuple[dict, dict]:
    osis_id = verse_element.attrib.get("osisID", "")
    prefix = f"{spec.ref}."
    if not osis_id.startswith(prefix):
        raise ValueError(f"unexpected verse id in {spec.ref}: {osis_id!r}")
    verse_number = int(osis_id.removeprefix(prefix))

    output = ""
    word_count = 0
    ketiv_count = 0
    qere_count = 0
    unpointed_non_ketiv_count = 0
    qere_missing_niqqud_count = 0
    ketiv_without_qere_count = 0
    segment_types: set[str] = set()
    wrappers: set[str] = set()
    pending_ketiv = 0

    for child in list(verse_element):
        tag = local_name(child.tag)
        if tag == "w":
            word = clean_word(child.text)
            if not word:
                raise ValueError(f"empty direct word in {osis_id}")
            output = append_piece(output, word, "word")
            word_count += 1
            is_ketiv = child.attrib.get("type") == "x-ketiv"
            if is_ketiv:
                ketiv_count += 1
                pending_ketiv += 1
            elif HEBREW_LETTER_RE.search(word) and not NIQQUD_RE.search(word):
                unpointed_non_ketiv_count += 1
            continue

        if tag == "seg":
            segment_type = child.attrib.get("type", "")
            segment_types.add(segment_type or "unspecified")
            output = append_piece(output, child.text or "", segment_type)
            continue

        if tag == "note":
            qere = qere_words(child)
            if qere:
                qere_count += len(qere)
                qere_missing_niqqud_count += sum(
                    1 for word in qere if not NIQQUD_RE.search(word)
                )
                if pending_ketiv:
                    pending_ketiv -= 1
            continue

        wrappers.add(tag)

    ketiv_without_qere_count += pending_ketiv
    text = output.strip()
    verse = {
        "bookCode": spec.book_code,
        "osisBook": spec.osis_book,
        "chapter": spec.chapter,
        "verse": verse_number,
        "ref": osis_id,
        "source": SOURCE_NAME,
        "version": SOURCE_VERSION,
        "sourceFile": source_file,
        "sourceOsisId": osis_id,
        "wordCount": word_count,
        "text": text,
    }
    diagnostics = {
        "wordCount": word_count,
        "ketivWordCount": ketiv_count,
        "qereWordCount": qere_count,
        "unpointedNonKetivWordCount": unpointed_non_ketiv_count,
        "qereMissingNiqqudCount": qere_missing_niqqud_count,
        "ketivWithoutQereCount": ketiv_without_qere_count,
        "segmentTypes": segment_types,
        "wrappers": wrappers,
        "emptyText": int(not text),
        "missingHebrewLetter": int(not HEBREW_LETTER_RE.search(text)),
        "missingNiqqud": int(not NIQQUD_RE.search(text)),
        "missingCantillation": int(not CANTILLATION_RE.search(text)),
        "slashArtifact": int("/" in text),
    }
    return verse, diagnostics


def extract_chapter(spec: ChapterSpec) -> tuple[dict, Counter]:
    source_path = WLC_DIR / f"{spec.osis_book}.xml"
    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    source_file = relative_posix(source_path)
    xml_root = ET.parse(source_path).getroot()
    chapter_element = xml_root.find(f".//osis:chapter[@osisID='{spec.ref}']", NS)
    if chapter_element is None:
        raise ValueError(f"missing selected chapter {spec.ref} in {source_file}")

    verses: list[dict] = []
    totals: Counter = Counter()
    segment_types: set[str] = set()
    wrappers: set[str] = set()
    for verse_element in chapter_element.findall("./osis:verse", NS):
        verse, diagnostics = extract_verse(
            verse_element,
            spec=spec,
            source_file=source_file,
        )
        verses.append(verse)
        for key, value in diagnostics.items():
            if key == "segmentTypes":
                segment_types.update(value)
            elif key == "wrappers":
                wrappers.update(value)
            else:
                totals[key] += value

    verse_numbers = [verse["verse"] for verse in verses]
    if not verses:
        raise ValueError(f"selected chapter has no verses: {spec.ref}")
    if verse_numbers != list(range(1, len(verses) + 1)):
        raise ValueError(f"non-contiguous MT verse sequence in {spec.ref}: {verse_numbers}")

    chapter = {
        "ordinal": spec.ordinal,
        "lessonStart": spec.ordinal,
        "lessonEnd": spec.ordinal,
        "bookCode": spec.book_code,
        "osisBook": spec.osis_book,
        "chapter": spec.chapter,
        "ref": spec.ref,
        "titleZh": spec.title_zh,
        "titleHe": spec.title_he,
        "corpusSection": spec.corpus_section,
        "genre": spec.genre,
        "difficulty": spec.difficulty,
        "difficultyRank": spec.ordinal,
        "source": SOURCE_NAME,
        "version": SOURCE_VERSION,
        "sourceUrl": SOURCE_URL,
        "sourceFile": source_file,
        "sourceFileSha256": sha256_file(source_path),
        "verseCount": len(verses),
        "wordCount": totals["wordCount"],
        "ketivWordCount": totals["ketivWordCount"],
        "qereWordCount": totals["qereWordCount"],
        "memoryVerseNumbers": [],
        "observedSegmentTypes": sorted(segment_types),
        "observedWrappers": sorted(wrappers),
        "verses": verses,
    }
    return chapter, totals


def canonical_sha256(value: object) -> str:
    content = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256_bytes(content)


def build_plan() -> dict:
    expected_refs = [spec.ref for spec in CHAPTERS]
    if len(CHAPTERS) != 25 or len(set(expected_refs)) != 25:
        raise ValueError("fixed chapter specification must contain 25 unique refs")
    if [spec.ordinal for spec in CHAPTERS] != list(range(1, 26)):
        raise ValueError("chapter ordinals must be exactly 1..25")

    chapters: list[dict] = []
    validation_totals: Counter = Counter()
    for spec in CHAPTERS:
        chapter, totals = extract_chapter(spec)
        chapters.append(chapter)
        validation_totals.update(totals)

    actual_refs = [chapter["ref"] for chapter in chapters]
    if actual_refs != expected_refs or set(actual_refs) != set(expected_refs):
        raise ValueError(
            f"selected ref mismatch: expected={expected_refs!r}, actual={actual_refs!r}"
        )

    section_counts = Counter(chapter["corpusSection"] for chapter in chapters)
    difficulty_counts = Counter(str(chapter["difficulty"]) for chapter in chapters)
    source_checksums = {
        chapter["sourceFile"]: chapter["sourceFileSha256"] for chapter in chapters
    }
    chapter_content_sha256 = canonical_sha256(chapters)
    source_bundle_sha256 = canonical_sha256(source_checksums)

    fatal_keys = (
        "emptyText",
        "missingHebrewLetter",
        "missingNiqqud",
        "missingCantillation",
        "slashArtifact",
        "unpointedNonKetivWordCount",
        "qereMissingNiqqudCount",
        "ketivWithoutQereCount",
    )
    chapter_extraction_passed = all(validation_totals[key] == 0 for key in fatal_keys)
    if not chapter_extraction_passed:
        failures = {key: validation_totals[key] for key in fatal_keys if validation_totals[key]}
        raise ValueError(f"chapter extraction validation failed: {failures}")

    return {
        "schemaVersion": "1.0.0",
        "generatedOn": date.today().isoformat(),
        "status": "pending-vocabulary-overlap-selection",
        "language": "Biblical Hebrew",
        "languageCode": "hbo",
        "curriculum": {
            "lessonCount": 50,
            "vocabularyTarget": 1000,
            "fullChapterCount": 25,
            "memoryVerseTarget": 100,
            "memoryVerseCount": 0,
            "memoryVersesPerLesson": 2,
            "chapterAllocation": "One complete chapter is assigned to each of lessons 1-25 in the user-approved easier-to-harder order; lessons 26-50 contain prayers or articles.",
            "ordering": "Fixed user-approved pedagogical difficulty order; difficultyRank 1-25 preserves the exact sequence.",
        },
        "selectionPolicy": {
            "fixedChapterRefs": expected_refs,
            "chapterOrder": "User-approved easier-to-harder sequence; do not reorder automatically.",
            "memorySelection": "Pending. Select two unique MT verses for each of the 50 lessons only after the 20-word lesson vocabulary is fixed, maximizing lemma overlap while preserving complete, memorizable sense units.",
            "memorySelectionStatus": "pending-vocabulary-overlap-selection",
        },
        "source": {
            "name": SOURCE_NAME,
            "version": SOURCE_VERSION,
            "sourceUrl": SOURCE_URL,
            "morphologyRelease": "OSHB full morphology release 2018-12-14",
            "localPackageVersion": "morphhb 2.0.2",
            "license": "WLC text: Public Domain. OSHB lemma and morphology annotations: CC BY 4.0.",
            "refSystem": "Bible.MT",
            "extraction": "Running text rebuilt in document order from direct OSIS <w> and <seg> elements. Morphological slash separators were removed; maqaf, sof pasuq, paseq, and paragraph markers were retained. Source Unicode code-point order was preserved without normalization. The raw source-oriented layer retains direct ketiv spellings; pointed qere readings remain in the traceable OSIS variant notes for the learner-facing display layer.",
            "selectedSourceFileCount": len(source_checksums),
            "selectedSourceFilesSha256": source_checksums,
            "selectedSourceBundleSha256": source_bundle_sha256,
        },
        "summary": {
            "chapterCount": len(chapters),
            "fullChapterVerseCount": sum(chapter["verseCount"] for chapter in chapters),
            "fullChapterWordCount": sum(chapter["wordCount"] for chapter in chapters),
            "memoryLessonCount": 0,
            "memoryVerseCount": 0,
            "sectionCounts": dict(sorted(section_counts.items())),
            "difficultyCounts": dict(sorted(difficulty_counts.items())),
            "genesisChapterCount": sum(chapter["osisBook"] == "Gen" for chapter in chapters),
        },
        "validation": {
            "chapterCountExpected": 25,
            "chapterCountActual": len(chapters),
            "chapterRefsExpected": expected_refs,
            "chapterRefsActual": actual_refs,
            "chapterRefSetExact": set(actual_refs) == set(expected_refs),
            "chapterOrderExact": actual_refs == expected_refs,
            "lessonAllocationExact": all(
                chapter["lessonStart"] == chapter["ordinal"]
                and chapter["lessonEnd"] == chapter["ordinal"]
                for chapter in chapters
            ),
            "memorySelectionStatus": "pending-vocabulary-overlap-selection",
            "memoryLessonCountExpectedCurrent": 0,
            "memoryLessonCountActual": 0,
            "memoryVerseCountExpectedCurrent": 0,
            "memoryVerseCountActual": 0,
            "memoryVerseTargetAfterSelection": 100,
            "fullChapterVerseCount": sum(chapter["verseCount"] for chapter in chapters),
            "fullChapterWordCount": sum(chapter["wordCount"] for chapter in chapters),
            "emptyTextCount": validation_totals["emptyText"],
            "missingHebrewLetterCount": validation_totals["missingHebrewLetter"],
            "missingNiqqudCount": validation_totals["missingNiqqud"],
            "missingCantillationCount": validation_totals["missingCantillation"],
            "slashArtifactCount": validation_totals["slashArtifact"],
            "ketivWordCount": validation_totals["ketivWordCount"],
            "qereWordCount": validation_totals["qereWordCount"],
            "ketivWithoutQereCount": validation_totals["ketivWithoutQereCount"],
            "unpointedNonKetivWordCount": validation_totals["unpointedNonKetivWordCount"],
            "qereMissingNiqqudCount": validation_totals["qereMissingNiqqudCount"],
            "chapterContentSha256": chapter_content_sha256,
            "sourceBundleSha256": source_bundle_sha256,
            "passed": chapter_extraction_passed,
        },
        "chapters": chapters,
        "memoryLessons": [],
        "memoryVerses": [],
    }


def main() -> None:
    plan = build_plan()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(plan, ensure_ascii=False, indent=2) + "\n"
    OUTPUT_PATH.write_text(serialized, encoding="utf-8")

    # Reload and re-check the persisted artifact, including its content hashes.
    persisted = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    if persisted != plan:
        raise ValueError("persisted scripture plan did not round-trip exactly")
    if canonical_sha256(persisted["chapters"]) != persisted["validation"]["chapterContentSha256"]:
        raise ValueError("persisted chapter checksum mismatch")
    if canonical_sha256(persisted["source"]["selectedSourceFilesSha256"]) != persisted["validation"]["sourceBundleSha256"]:
        raise ValueError("persisted source bundle checksum mismatch")

    print(f"output={relative_posix(OUTPUT_PATH)}")
    print(f"chapters={persisted['summary']['chapterCount']}")
    print(f"verses={persisted['summary']['fullChapterVerseCount']}")
    print(f"words={persisted['summary']['fullChapterWordCount']}")
    print(f"ketiv={persisted['validation']['ketivWordCount']}")
    print(f"qere={persisted['validation']['qereWordCount']}")
    print(f"chapterContentSha256={persisted['validation']['chapterContentSha256']}")
    print(f"fileSha256={sha256_file(OUTPUT_PATH)}")


if __name__ == "__main__":
    main()
