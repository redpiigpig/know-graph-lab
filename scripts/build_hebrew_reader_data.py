"""Assemble the complete 50-lesson Hebrew reader data set.

This builder joins four independently auditable source layers:

* 1,000 pointed vocabulary entries in the Pratico–Van Pelt ordering;
* 25 complete WLC chapters and 100 WLC memory verses;
* 25 complete Hebrew prayers/articles;
* the complete Passover Haggadah flow as a back-matter appendix.

No source text is silently repaired here.  The assembler rejects missing or
partly pointed lesson readings so the book generator cannot turn a planning
record into apparent finished content.
"""

from __future__ import annotations

import json
import hashlib
import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

from rcuv2010_reader import (
    load_rcuv_snapshot,
    translation_entry_for_mt,
    translation_for_mt,
)


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "hebrew-full"
VOCAB_PATH = ROOT / "data" / "originalReaders" / "vocabulary" / "hebrew-1000.json"
GLOSS_PATH = CACHE / "hebrew-1000-gloss-zh-reviewed.json"
SCRIPTURE_PATH = CACHE / "scripture-plan.json"
CHINESE_BIBLE_PATH = CACHE / "RCUV2010.json"
PRAYERS_PATH = CACHE / "prayers-articles.json"
HAGGADAH_PATH = CACHE / "haggadah-full.json"
OUTPUT_PATH = CACHE / "hebrew-reader-50-lessons.json"


CHINESE_BOOK_NAMES = {
    "gen": "Genesis",
    "exod": "Exodus",
    "lev": "Leviticus",
    "num": "Numbers",
    "deut": "Deuteronomy",
    "judg": "Judges",
    "josh": "Joshua",
    "ruth": "Ruth",
    "1sam": "I Samuel",
    "2sam": "II Samuel",
    "1kgs": "I Kings",
    "2kgs": "II Kings",
    "1chr": "I Chronicles",
    "2chr": "II Chronicles",
    "ezra": "Ezra",
    "neh": "Nehemiah",
    "esth": "Esther",
    "job": "Job",
    "ps": "Psalms",
    "prov": "Proverbs",
    "eccl": "Ecclesiastes",
    "song": "Song of Solomon",
    "isa": "Isaiah",
    "jer": "Jeremiah",
    "ezek": "Ezekiel",
    "dan": "Daniel",
    "hos": "Hosea",
    "joel": "Joel",
    "amos": "Amos",
    "obad": "Obadiah",
    "jonah": "Jonah",
    "mic": "Micah",
    "nah": "Nahum",
    "hab": "Habakkuk",
    "zeph": "Zephaniah",
    "hag": "Haggai",
    "zech": "Zechariah",
    "mal": "Malachi",
    "lam": "Lamentations",
}

HEBREW_LETTER = re.compile(r"[\u05D0-\u05EA]")
HEBREW_VOWEL_MARKS = {
    "\u05B0", "\u05B1", "\u05B2", "\u05B3", "\u05B4", "\u05B5",
    "\u05B6", "\u05B7", "\u05B8", "\u05B9", "\u05BA", "\u05BB",
    "\u05C7",
}
OSIS_NS = "http://www.bibletechnologies.net/2003/OSIS/namespace"
_WLC_CACHE: dict[Path, dict[str, str]] = {}
_PSALM_MT_COUNTS: dict[int, int] | None = None


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hebrew_words(text: str) -> list[str]:
    return [
        token.strip(".,;:!?()[]{}<>׳״'\"")
        for token in re.split(r"[\s\u05BE]+", text)
        if HEBREW_LETTER.search(token)
    ]


def hebrew_clusters(word: str) -> list[tuple[str, set[str]]]:
    clusters: list[tuple[str, set[str]]] = []
    current_base = ""
    current_marks: set[str] = set()
    for character in unicodedata.normalize("NFD", word):
        if HEBREW_LETTER.fullmatch(character):
            if current_base:
                clusters.append((current_base, current_marks))
            current_base = character
            current_marks = set()
            continue
        codepoint = ord(character)
        if current_base and 0x0591 <= codepoint <= 0x05C7 and not 0x0591 <= codepoint <= 0x05AF:
            current_marks.add(character)
    if current_base:
        clusters.append((current_base, current_marks))
    return clusters


def vowel_mark(marks: set[str]) -> str | None:
    return next((mark for mark in HEBREW_VOWEL_MARKS if mark in marks), None)


def is_hebrew_mater(clusters: list[tuple[str, set[str]]], index: int) -> bool:
    base, marks = clusters[index]
    vowel = vowel_mark(marks)
    if base == "ו" and ("\u05B9" in marks or "\u05BA" in marks):
        return True
    # Shureq is waw + dagesh; a dagesh on another consonant is not a vowel.
    if base == "ו" and "\u05BC" in marks and not vowel:
        return True
    if index == 0:
        return False
    previous_vowel = vowel_mark(clusters[index - 1][1])
    if base == "ו" and not vowel and previous_vowel in {"\u05B9", "\u05BA"}:
        return True
    if (
        base == "ו"
        and not vowel
        and index >= 2
        and clusters[index - 1][0] == "א"
        and not vowel_mark(clusters[index - 1][1])
        and vowel_mark(clusters[index - 2][1]) in {"\u05B9", "\u05BA"}
    ):
        return True
    if base == "י" and not vowel and previous_vowel in {"\u05B4", "\u05B5", "\u05B6"}:
        return True
    # Pronominal -ָיו / -ַיו writes an unpointed yod before final waw.
    if (
        base == "י"
        and not vowel
        and previous_vowel in {"\u05B7", "\u05B8"}
        and index + 1 == len(clusters) - 1
        and clusters[index + 1][0] == "ו"
    ):
        return True
    return (
        base == "ה"
        and index == len(clusters) - 1
        and "\u05BC" not in marks
        and not vowel
        and previous_vowel in {"\u05B5", "\u05B6", "\u05B8", "\u05B9", "\u05BA"}
    )


def is_fully_pointed_hebrew_word(word: str) -> bool:
    letters = "".join(character for character in unicodedata.normalize("NFD", word) if HEBREW_LETTER.fullmatch(character))
    # Traditional divine-name spelling is intentionally exceptional.
    if letters == "יהוה":
        return True
    # Standalone paragraph signs and sacred-name abbreviations are not words.
    if len(letters) <= 1:
        return True
    clusters = hebrew_clusters(word)
    if not clusters:
        return False
    # WLC also attaches fully pointed conjunctions/prepositions to the
    # traditional four-letter divine name (for example וַיהוָה).  Validate the
    # prefix normally, then preserve the established exceptional spelling.
    divine_name_start = len(clusters) - 4 if letters.endswith("יהוה") else None
    divine_abbreviation_start = len(clusters) - 2 if letters.endswith("יי") else None
    for index, (base, marks) in enumerate(clusters):
        if divine_name_start is not None and index >= divine_name_start:
            continue
        if divine_abbreviation_start is not None and index >= divine_abbreviation_start:
            continue
        vowel = vowel_mark(marks)
        is_shureq = base == "ו" and "\u05BC" in marks and not vowel
        is_final = index == len(clusters) - 1
        previous_vowel = vowel_mark(clusters[index - 1][1]) if index > 0 else None
        unpointed_aleph_after_vowel = base == "א" and not vowel and bool(previous_vowel)
        next_cluster = clusters[index + 1] if index + 1 < len(clusters) else None
        next_vowel = vowel_mark(next_cluster[1]) if next_cluster else None
        next_is_waw_vowel = bool(
            next_cluster
            and next_cluster[0] == "ו"
            and (
                "\u05B9" in next_cluster[1]
                or "\u05BA" in next_cluster[1]
                or ("\u05BC" in next_cluster[1] and not next_vowel)
            )
        )
        if (
            vowel
            or is_shureq
            or is_final
            or next_is_waw_vowel
            or unpointed_aleph_after_vowel
            or is_hebrew_mater(clusters, index)
        ):
            continue
        return False
    return True


def assert_pointed_running_text(text: str, label: str) -> None:
    if not text.strip():
        raise ValueError(f"empty Hebrew running text: {label}")
    missing = []
    for word in hebrew_words(text):
        if not is_fully_pointed_hebrew_word(word):
            missing.append(word)
    if missing:
        raise ValueError(
            f"unpointed Hebrew in {label}: {', '.join(missing[:8])}"
        )


def assert_masoretic_source_text(text: str, label: str) -> None:
    """Verify that every WLC display word belongs to its pointed source layer.

    The stricter pedagogical cluster test is deliberately not used here:
    canonical WLC forms such as הִוא and יִשָּׂשכָר contain historically written
    consonants without an independent shewa.  They are fully Masoretic, not
    modern unpointed Hebrew.  This gate instead rejects any whole orthographic
    word that has lost all vowel information after ketiv/qere normalization.
    """

    if not text.strip():
        raise ValueError(f"empty Masoretic running text: {label}")
    missing: list[str] = []
    for word in hebrew_words(text):
        normalized = unicodedata.normalize("NFD", word)
        letters = "".join(ch for ch in normalized if HEBREW_LETTER.fullmatch(ch))
        has_vowel = any(ch in HEBREW_VOWEL_MARKS for ch in normalized)
        has_shureq = any(
            base == "ו" and "\u05BC" in marks and not vowel_mark(marks)
            for base, marks in hebrew_clusters(word)
        )
        if has_vowel or has_shureq or len(letters) <= 1 or letters.endswith("יהוה"):
            continue
        missing.append(word)
    if missing:
        raise ValueError(
            f"word without Masoretic vocalization in {label}: {', '.join(missing[:8])}"
        )


def chinese_bible_index(payload: dict) -> tuple[dict[tuple[str, int, int], dict], dict]:
    # Compatibility wrapper retained for callers/tests that imported this
    # builder before the crosswalk moved to the shared strict module.
    del payload
    return load_rcuv_snapshot(CHINESE_BIBLE_PATH)


def chinese_book_name(book_code: str) -> str:
    normalized = book_code.strip().lower()
    if normalized not in CHINESE_BOOK_NAMES:
        raise ValueError(f"unsupported Chinese Bible book code: {book_code}")
    return CHINESE_BOOK_NAMES[normalized]


def chinese_translation_for(
    zh_index: dict[tuple[str, int, int], dict],
    book_name: str,
    chapter: int,
    verse: int,
) -> str:
    global _PSALM_MT_COUNTS
    if _PSALM_MT_COUNTS is None:
        _PSALM_MT_COUNTS = {}
        for reference in wlc_qere_verses(
            "output/source-cache/original-readers/morphhb-src/morphhb-master/wlc/Ps.xml"
        ):
            _, psalm, mt_verse = reference.split(".")
            _PSALM_MT_COUNTS[int(psalm)] = max(
                _PSALM_MT_COUNTS.get(int(psalm), 0), int(mt_verse)
            )
    return translation_for_mt(
        zh_index,
        book_name,
        chapter,
        verse,
        mt_psalm_counts=_PSALM_MT_COUNTS,
    )


def chinese_translation_entry_for(
    zh_index: dict[tuple[str, int, int], dict],
    book_name: str,
    chapter: int,
    verse: int,
) -> dict:
    chinese_translation_for(zh_index, book_name, chapter, verse)
    return translation_entry_for_mt(
        zh_index,
        book_name,
        chapter,
        verse,
        mt_psalm_counts=_PSALM_MT_COUNTS,
    )


def _clean_wlc_word(text: str) -> str:
    return text.replace("/", "").strip()


def _append_wlc_piece(output: str, piece: str, kind: str) -> str:
    if not piece:
        return output
    if kind == "word":
        if output and not output.endswith((" ", "־")):
            output += " "
        return output + piece
    if kind == "maqqef":
        return output.rstrip() + "־"
    if kind == "sof-pasuq":
        return output.rstrip() + "׃"
    if kind == "paseq":
        return output.rstrip() + " ׀"
    return output


def wlc_qere_verses(source_file: str) -> dict[str, str]:
    """Read WLC verses for display, choosing the pointed qere over ketiv.

    MorphHB stores ketiv as an unpointed direct ``w`` and its pointed qere in
    the following variant note.  A learner's running text must not print both,
    so this display layer uses qere while the original ketiv remains preserved
    in ``scripture-plan.json`` and the source OSIS file.
    """

    path = (ROOT / source_file).resolve()
    if path in _WLC_CACHE:
        return _WLC_CACHE[path]
    root = ET.parse(path).getroot()
    verses: dict[str, str] = {}
    for verse in root.findall(f".//{{{OSIS_NS}}}verse"):
        osis_id = verse.attrib.get("osisID", "")
        output = ""
        for child in list(verse):
            tag = child.tag.rsplit("}", 1)[-1]
            if tag == "w":
                if child.attrib.get("type") == "x-ketiv":
                    continue
                output = _append_wlc_piece(output, _clean_wlc_word(child.text or ""), "word")
                continue
            if tag == "note" and child.attrib.get("type") == "variant":
                qere = child.find(
                    f"./{{{OSIS_NS}}}rdg[@type='x-qere']/{{{OSIS_NS}}}w"
                )
                if qere is not None:
                    output = _append_wlc_piece(output, _clean_wlc_word(qere.text or ""), "word")
                continue
            if tag == "seg":
                segment_type = child.attrib.get("type", "")
                kind = {
                    "x-maqqef": "maqqef",
                    "x-sof-pasuq": "sof-pasuq",
                    "x-paseq": "paseq",
                }.get(segment_type)
                if kind:
                    output = _append_wlc_piece(output, child.text or "", kind)
        verses[osis_id] = output.strip()
    _WLC_CACHE[path] = verses
    return verses


def enrich_scripture(chapters: list[dict], zh_index: dict) -> list[dict]:
    enriched = []
    for chapter in chapters:
        book_name = chinese_book_name(chapter["bookCode"])
        verses = []
        pointed_qere = wlc_qere_verses(chapter["sourceFile"])
        for verse in chapter["verses"]:
            source_text = verse["text"]
            text = pointed_qere.get(verse["ref"], "")
            if not text:
                raise ValueError(f"missing WLC qere display text: {verse['ref']}")
            assert_masoretic_source_text(text, verse["ref"])
            key = (book_name, int(chapter["chapter"]), int(verse["verse"]))
            translation = chinese_translation_entry_for(zh_index, *key)
            if not translation.get("text"):
                raise ValueError(f"missing Chinese Bible verse: {key}")
            verses.append(
                {
                    **verse,
                    "sourceTextKetivLayer": source_text,
                    "text": text,
                    "displayReading": "pointed-qere",
                    "translationZh": translation["text"],
                    "translationCrosswalk": {
                        key: value for key, value in translation.items() if key != "text"
                    },
                }
            )
        enriched.append({**chapter, "verses": verses})
    return enriched


def assemble() -> dict:
    vocabulary = load(VOCAB_PATH)
    glosses = load(GLOSS_PATH)["items"]
    scripture = load(SCRIPTURE_PATH)
    prayers = load(PRAYERS_PATH)
    haggadah = load(HAGGADAH_PATH)
    zh_index, zh_translation = chinese_bible_index(load(CHINESE_BIBLE_PATH))

    if len(vocabulary) != 1000 or [v["ordinal"] for v in vocabulary] != list(range(1, 1001)):
        raise ValueError("vocabulary is not exactly ordinals 1..1000")
    if len(glosses) != 1000 or [g["ordinal"] for g in glosses] != list(range(1, 1001)):
        raise ValueError("Chinese gloss layer is not exactly ordinals 1..1000")
    gloss_by_ordinal = {entry["ordinal"]: entry["glossZh"].strip() for entry in glosses}
    vocabulary = [
        {**entry, "glossZh": gloss_by_ordinal[entry["ordinal"]]}
        for entry in vocabulary
    ]
    if any(not item["glossZh"] for item in vocabulary):
        raise ValueError("one or more Chinese vocabulary glosses are empty")

    chapters = enrich_scripture(scripture["chapters"], zh_index)
    display_verses = {
        verse["ref"]: verse
        for chapter in chapters
        for verse in chapter["verses"]
    }
    memory = []
    for item in scripture["memoryVerses"]:
        book_name = chinese_book_name(item["bookCode"])
        # Always resolve against the frozen RCUV2010 snapshot.  Never preserve
        # an older translation embedded by a previous selector run.
        translation = chinese_translation_entry_for(
            zh_index,
            book_name,
            int(item["chapter"]),
            int(item["verse"]),
        )
        if not translation.get("text"):
            raise ValueError(f"missing memory-verse Chinese translation: {item['ref']}")
        display = display_verses.get(item["ref"])
        display_text = display["text"] if display else item.get("text", "")
        assert_masoretic_source_text(display_text, item["ref"])
        memory.append(
            {
                **item,
                "sourceTextKetivLayer": item.get("sourceTextKetivLayer", item.get("text", "")),
                "text": display_text,
                "displayReading": "pointed-qere",
                "translationZh": translation["text"],
                "translationCrosswalk": {
                    key: value for key, value in translation.items() if key != "text"
                },
            }
        )

    prayer_items = prayers["items"]
    if len(prayer_items) != 25:
        raise ValueError(f"expected 25 prayers/articles, got {len(prayer_items)}")
    for item in prayer_items:
        if not item.get("text", "").strip():
            raise ValueError(f"empty prayer/article: {item.get('id')}")
        if item.get("fullPointingStatus") not in {
            "source_pointed_complete",
            "editorial_pointed_complete",
        }:
            raise ValueError(f"prayer/article pointing incomplete: {item.get('id')}")
        assert_pointed_running_text(item["text"], item["id"])

    if int(haggadah.get("pointingGapCount", -1)) != 0:
        raise ValueError(
            f"Haggadah still has {haggadah.get('pointingGapCount')} pointing gaps"
        )
    for step in haggadah["steps"]:
        assert_pointed_running_text(step["text"], f"Haggadah {step.get('key')}")

    lessons = []
    for lesson_number in range(1, 51):
        lesson_vocab = [entry for entry in vocabulary if int(entry["lesson"]) == lesson_number]
        lesson_memory = [entry for entry in memory if int(entry["lesson"]) == lesson_number]
        if not lesson_vocab or len(lesson_memory) != 2:
            raise ValueError(
                f"lesson {lesson_number}: vocab={len(lesson_vocab)}, memory={len(lesson_memory)}"
            )
        if lesson_number <= 25:
            reading = {"kind": "bible_chapter", **chapters[lesson_number - 1]}
            title = reading["titleZh"]
        else:
            reading = {"kind": "prayer_or_article", **prayer_items[lesson_number - 26]}
            title = reading["title_zh"]
        lessons.append(
            {
                "lesson": lesson_number,
                "id": f"hbo-lesson-{lesson_number:02d}",
                "title": title,
                "vocabulary": lesson_vocab,
                "memoryVerses": lesson_memory,
                "reading": reading,
                "audioRoute": f"/original-readers/hbo/lesson-{lesson_number:02d}",
            }
        )

    return {
        "schemaVersion": "1.0.0",
        "title": "聖經希伯來文原文讀本",
        "subtitle": "五十課・一千詞・一百節背誦・二十五章・二十五篇禱文與文章",
        "language": "Biblical Hebrew / Mishnaic Hebrew",
        "languageCode": "hbo",
        "privateUse": True,
        "releaseStatus": "content_complete_audio_pending",
        "printProfile": {
            "preset": "compact_reference_guide",
            "openingPattern": "editorial_cover",
            "trim": "JIS_B5",
            "widthMm": 182,
            "heightMm": 257,
            "marginTopMm": 18,
            "marginBottomMm": 20,
            "marginInsideMm": 24,
            "marginOutsideMm": 17,
            "mirroredMargins": True,
        },
        "counts": {
            "lessons": len(lessons),
            "vocabulary": sum(len(lesson["vocabulary"]) for lesson in lessons),
            "memoryVerses": sum(len(lesson["memoryVerses"]) for lesson in lessons),
            "bibleChapters": sum(lesson["reading"]["kind"] == "bible_chapter" for lesson in lessons),
            "prayersOrArticles": sum(lesson["reading"]["kind"] == "prayer_or_article" for lesson in lessons),
            "haggadahSteps": len(haggadah["steps"]),
        },
        "textPolicy": {
            "biblicalText": "WLC 4.20 with niqqud and cantillation retained",
            "prayerText": "source pointing retained; editorial pointing is explicitly sourced",
            "transliteration": "Pratico–Van Pelt BBH2 textbook system",
            "modernUnpointedSubstitution": "prohibited",
        },
        "lessons": lessons,
        "haggadah": haggadah,
        "appendices": [
            {
                "id": "hbo-haggadah",
                "kind": "haggadah",
                "titleZh": haggadah["title"],
                "titleHe": haggadah["title_he"],
                "stepCount": len(haggadah["steps"]),
                "segmentCount": sum(
                    len(step.get("segments", [])) for step in haggadah["steps"]
                ),
                "status": "editorial_pointed_complete",
            }
        ],
        "audio": {
            "status": "not_recorded",
            "recordedTrackCount": 0,
            "profile": "biblical-masoretic-pedagogical-bbh2",
            "tracks": [],
            "policy": "不使用現代希伯來語 TTS 冒充聖經希伯來文；校訂錄音完成前不顯示播放按鈕。",
        },
        "build": {
            "builder": "scripts/build_hebrew_reader_data.py",
            "inputsSha256": {
                str(path.relative_to(ROOT)).replace("\\", "/"): sha256_file(path)
                for path in (
                    VOCAB_PATH,
                    GLOSS_PATH,
                    SCRIPTURE_PATH,
                    CHINESE_BIBLE_PATH,
                    PRAYERS_PATH,
                    HAGGADAH_PATH,
                )
            },
            "downstream": {
                "docx": "output/original-readers/hebrew-original-reader-50-lessons.docx",
                "pdf": "output/original-readers/hebrew-original-reader-50-lessons.pdf",
                "qaReport": "output/qa/original-readers/hebrew-full/qa-report-final.json",
            },
        },
        "sources": {
            "scripture": scripture["source"],
            "chineseBible": {
                **zh_translation,
                "rights": "© 香港聖經公會；私人授權使用",
                "snapshot": str(CHINESE_BIBLE_PATH.relative_to(ROOT)).replace("\\", "/"),
                "snapshotSha256": sha256_file(CHINESE_BIBLE_PATH),
            },
            "prayers": prayers["sourceNotes"],
            "vocabulary": "BBH2 authorized ordering plus verified frequency extension",
        },
    }


def main() -> None:
    payload = assemble()
    OUTPUT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload["counts"], ensure_ascii=False))
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
