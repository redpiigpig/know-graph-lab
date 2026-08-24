#!/usr/bin/env python3
"""Validate the shared structural contract of a complete reader master."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any


PLACEHOLDER = re.compile(r"TODO|TBD|placeholder|待補|待定|未填|source[_ -]?pending", re.I)
ASCII_LETTER = re.compile(r"[A-Za-z]")
HEBREW_LETTER = re.compile(r"[\u05D0-\u05EA]")
GREEK_LETTER = re.compile(r"[\u0370-\u03FF\u1F00-\u1FFF]")
LATIN_LETTER = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿĀ-ž]")
HEBREW_VOWEL_MARKS = {
    "\u05B0", "\u05B1", "\u05B2", "\u05B3", "\u05B4", "\u05B5",
    "\u05B6", "\u05B7", "\u05B8", "\u05B9", "\u05BA", "\u05BB",
    "\u05C7",
}
PROPER_NAME_TYPES = {
    "person", "place", "people_or_nation", "divine_name_or_title",
    "festival_or_sacred_time",
}
RELEASE_STATUSES = {
    "planned",
    "source_frozen",
    "vocabulary_complete",
    "content_complete_translation_pending",
    "content_complete_layout_pending",
    "content_complete_audio_pending",
    "print_qa_passed_audio_pending",
    "release_candidate",
    "complete_private_release",
}
HAGGADAH_KEYS = [
    "Kadesh", "Urchatz", "Karpas", "Yachatz", "Magid", "Rachtzah",
    "Motzi", "Matzah", "Maror", "Korech", "Shulchan Orech", "Tzafun",
    "Barech", "Hallel", "Nirtzah",
]
SHA256 = re.compile(r"[0-9a-f]{64}")


def fail(checks: list[dict[str, Any]], code: str, message: str, **details: Any) -> None:
    checks.append({"status": "FAIL", "code": code, "message": message, "details": details})


def passed(checks: list[dict[str, Any]], code: str, message: str, **details: Any) -> None:
    checks.append({"status": "PASS", "code": code, "message": message, "details": details})


def expect(
    checks: list[dict[str, Any]],
    condition: bool,
    code: str,
    message: str,
    **details: Any,
) -> None:
    (passed if condition else fail)(checks, code, message, **details)


def text_values(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from text_values(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from text_values(item)


def first_text(value: dict[str, Any], *keys: str) -> str:
    return next(
        (str(value.get(key) or "").strip() for key in keys if str(value.get(key) or "").strip()),
        "",
    )


def hebrew_words(text: str) -> list[str]:
    return [
        token.strip(".,;:!?()[]{}<>׳״'\"")
        for token in re.split(r"[\s\u05BE/]+", text)
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
    if base == "ו" and "\u05BC" in marks and not vowel:
        return True
    if index == 0:
        return False
    previous_vowel = vowel_mark(clusters[index - 1][1])
    if base == "ו" and not vowel and previous_vowel in {"\u05B9", "\u05BA"}:
        return True
    if base == "י" and not vowel and previous_vowel in {"\u05B4", "\u05B5", "\u05B6"}:
        return True
    if (
        base == "י" and not vowel and previous_vowel in {"\u05B7", "\u05B8"}
        and index + 1 == len(clusters) - 1 and clusters[index + 1][0] == "ו"
    ):
        return True
    return (
        base == "ה" and index == len(clusters) - 1 and "\u05BC" not in marks
        and not vowel and previous_vowel in {"\u05B5", "\u05B6", "\u05B8", "\u05B9", "\u05BA"}
    )


def is_fully_pointed_hebrew_word(word: str) -> bool:
    letters = "".join(
        char for char in unicodedata.normalize("NFD", word)
        if HEBREW_LETTER.fullmatch(char)
    )
    if letters == "יהוה" or len(letters) <= 1:
        return True
    clusters = hebrew_clusters(word)
    if not clusters:
        return False
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
        previous_vowel = vowel_mark(clusters[index - 1][1]) if index else None
        unpointed_aleph_after_vowel = base == "א" and not vowel and bool(previous_vowel)
        next_cluster = clusters[index + 1] if index + 1 < len(clusters) else None
        next_vowel = vowel_mark(next_cluster[1]) if next_cluster else None
        next_is_waw_vowel = bool(
            next_cluster and next_cluster[0] == "ו"
            and ("\u05B9" in next_cluster[1] or "\u05BA" in next_cluster[1]
                 or ("\u05BC" in next_cluster[1] and not next_vowel))
        )
        if vowel or is_shureq or is_final or next_is_waw_vowel or unpointed_aleph_after_vowel or is_hebrew_mater(clusters, index):
            continue
        return False
    return True


def vocabulary_form(item: dict[str, Any]) -> str:
    return first_text(item, "pointed", "canonical", "surface", "lemma")


def language_form_ok(item: dict[str, Any], language: str) -> bool:
    form = vocabulary_form(item)
    if not form or "\ufffd" in form or unicodedata.normalize("NFC", form) != form:
        return False
    if language == "hbo":
        words = hebrew_words(form)
        return bool(words) and all(is_fully_pointed_hebrew_word(word) for word in words)
    if language == "grc":
        return bool(GREEK_LETTER.search(form))
    return bool(LATIN_LETTER.search(form))


def select_volume(data: dict[str, Any], volume: int) -> dict[str, Any]:
    """One volume of a multi-volume master, presented as a single-volume one.

    A release may be one book or several.  Rather than teach every check about
    volumes, the volume being validated is lifted into the shape the checks
    already expect: its lessons become the master's lessons, its appendices join
    the shared ones, and the counts it must satisfy are recomputed from its own
    lessons.  A single-volume master is returned untouched.
    """
    volumes = data.get("volumes")
    if not volumes:
        if volume:
            raise SystemExit("這份主檔沒有分冊，不要給 --volume")
        return data
    if not volume:
        raise SystemExit(
            f"這份主檔分 {len(volumes)} 冊，須指定 --volume（1–{len(volumes)}）"
        )
    match = next((item for item in volumes if item.get("volume") == volume), None)
    if match is None:
        raise SystemExit(f"主檔沒有第 {volume} 冊")
    lessons = match.get("lessons") or []
    scripture = sum(
        1
        for lesson in lessons
        if (lesson.get("reading") or {}).get("kind") in {"bible_chapter", "scripture_chapter"}
    )
    vocabulary = [item for lesson in lessons for item in lesson.get("vocabulary") or []]
    memory = [
        item
        for lesson in lessons
        for item in (lesson.get("memoryUnits") or lesson.get("memoryVerses") or [])
    ]
    return {
        **data,
        "volumeTitle": match.get("title", ""),
        "lessons": lessons,
        "appendices": (data.get("appendices") or []) + (match.get("appendices") or []),
        "counts": {
            **(data.get("counts") or {}),
            "lessons": len(lessons),
            "vocabulary": len(vocabulary),
            "memoryUnits": len(memory),
            "bibleChapters": scripture,
            "prayersOrArticles": len(lessons) - scripture,
        },
    }


def validate(args: argparse.Namespace) -> dict[str, Any]:
    data = select_volume(json.loads(args.master.read_text(encoding="utf-8")), args.volume)
    checks: list[dict[str, Any]] = []
    required_top = {
        "schemaVersion", "languageCode", "privateUse", "releaseStatus",
        "printProfile", "counts", "textPolicy", "sources", "lessons",
        "appendices", "audio", "build",
    }
    missing_top = sorted(required_top - set(data))
    expect(
        checks,
        not missing_top
        and data.get("schemaVersion") in {"1.0.0", "2.0.0"}
        and data.get("languageCode") == args.language
        and data.get("privateUse") is True
        and data.get("releaseStatus") in RELEASE_STATUSES,
        "release-schema",
        "release schema, language, privacy scope, and status are explicit",
        missing=missing_top,
        schemaVersion=data.get("schemaVersion"),
        languageCode=data.get("languageCode"),
        releaseStatus=data.get("releaseStatus"),
    )
    print_profile = data.get("printProfile") or {}
    expect(
        checks,
        print_profile.get("trim") in {"JIS_B5", "B5"}
        and print_profile.get("widthMm") == 182
        and print_profile.get("heightMm") == 257
        and print_profile.get("mirroredMargins") is True,
        "print-profile",
        "print profile is explicit JIS B5 with mirrored margins",
        actual=print_profile,
    )
    lessons = data.get("lessons") or []
    expected_numbers = list(range(1, args.lessons + 1))
    expect(
        checks,
        len(lessons) == args.lessons
        and [lesson.get("lesson") for lesson in lessons] == expected_numbers,
        "lessons",
        "lesson count and order match the frozen contract",
        expected=args.lessons,
        actual=len(lessons),
    )

    vocabulary = [item for lesson in lessons for item in lesson.get("vocabulary") or []]
    vocabulary_ids = [str(item.get("id") or item.get("ordinal") or "") for item in vocabulary]
    if args.vocabulary_per_lesson:
        vocabulary_shape = all(
            len(lesson.get("vocabulary") or []) == args.vocabulary_per_lesson
            for lesson in lessons
        )
        expected_total = args.lessons * args.vocabulary_per_lesson
    else:
        # Uneven by design: every lesson must carry words, and the curriculum
        # total must be exact, but no two lessons need be the same size.
        vocabulary_shape = all(lesson.get("vocabulary") for lesson in lessons)
        expected_total = args.vocabulary_total
    vocabulary_ordinals = [item.get("ordinal") for item in vocabulary]
    slot_failures = [
        item.get("ordinal")
        for lesson in lessons
        for expected_slot, item in enumerate(lesson.get("vocabulary") or [], 1)
        if item.get("lesson") != lesson.get("lesson")
        or item.get("lessonSlot") != expected_slot
    ]
    expect(
        checks,
        vocabulary_shape
        and len(vocabulary) == expected_total
        and len(set(vocabulary_ids)) == len(vocabulary_ids)
        and all(vocabulary_ids),
        "vocabulary",
        "vocabulary count, lesson allocation, and identities are complete",
        actual=len(vocabulary),
        expected=expected_total,
        perLessonRule=(
            f"fixed {args.vocabulary_per_lesson}"
            if args.vocabulary_per_lesson
            else "uneven by design (textbook chapters)"
        ),
    )
    expect(
        checks,
        vocabulary_ordinals == list(range(1, len(vocabulary) + 1))
        and not slot_failures,
        "vocabulary-order",
        "vocabulary ordinals, lesson assignments, and lesson slots are continuous",
        failures=slot_failures[:30],
    )

    transliteration_failures = [
        item.get("id") or item.get("ordinal")
        for item in vocabulary
        if not str(
            item.get("textbookTransliteration")
            or item.get("transliteration")
            or item.get("phonetic")
            or ""
        ).strip()
    ]
    gloss_failures = [
        item.get("id") or item.get("ordinal")
        for item in vocabulary
        if not str(item.get("glossZh") or "").strip()
    ]
    language_form_failures = [
        item.get("id") or item.get("ordinal")
        for item in vocabulary
        if not language_form_ok(item, args.language)
    ]
    gloss_quality_failures = [
        item.get("id") or item.get("ordinal")
        for item in vocabulary
        if PLACEHOLDER.search(str(item.get("glossZh") or ""))
        or ASCII_LETTER.search(str(item.get("glossZh") or ""))
    ]
    proper_name_failures = [
        item.get("id") or item.get("ordinal")
        for item in vocabulary
        if (
            bool(item.get("isProperName"))
            != bool(item.get("properNameTypes") or [])
            or not set(item.get("properNameTypes") or []) <= PROPER_NAME_TYPES
        )
    ]
    expect(checks, not transliteration_failures, "transliteration", "every word has textbook-specific transliteration", failures=transliteration_failures[:30])
    expect(checks, not gloss_failures, "glosses", "every word has a reviewed Traditional-Chinese gloss", failures=gloss_failures[:30])
    expect(checks, not language_form_failures, "source-orthography", "every vocabulary form satisfies the selected language profile", failures=language_form_failures[:30])
    expect(checks, not gloss_quality_failures, "gloss-quality", "Traditional-Chinese glosses contain no placeholder or English leakage", failures=gloss_quality_failures[:30])
    expect(checks, not proper_name_failures, "proper-names", "proper-name flags and typed categories are consistent", failures=proper_name_failures[:30])

    memory = [
        item
        for lesson in lessons
        for item in (lesson.get("memoryUnits") or lesson.get("memoryVerses") or [])
    ]
    memory_ids = [str(item.get("ref") or item.get("id") or "") for item in memory]
    memory_shape = all(
        len(lesson.get("memoryUnits") or lesson.get("memoryVerses") or [])
        == args.memory_per_lesson
        for lesson in lessons
    )
    expect(
        checks,
        memory_shape
        and len(memory) == args.lessons * args.memory_per_lesson
        and len(set(memory_ids)) == len(memory_ids)
        and all(memory_ids),
        "memory",
        "memory units are complete and unique",
        actual=len(memory),
        unique=len(set(memory_ids)),
    )
    memory_quality_failures = [
        item.get("ref") or item.get("id")
        for item in memory
        if not first_text(item, "sourceText", "text", "displayText")
        or not str(item.get("translationZh") or "").strip()
        or "reviewed" not in first_text(item, "selectionReview", "reviewStatus").lower()
        or not first_text(item, "selectionReason", "reviewReason")
        or int(item.get("matchedCount") or len(item.get("matchedLessonVocabulary") or [])) < 1
    ]
    expect(
        checks,
        not memory_quality_failures,
        "memory-review",
        "memory units contain source text, RCUV translation, overlap evidence, and human review",
        failures=memory_quality_failures[:30],
    )

    scripture = [
        lesson for lesson in lessons
        if (lesson.get("reading") or {}).get("kind") in {"bible_chapter", "scripture_chapter"}
    ]
    non_scripture = [lesson for lesson in lessons if lesson not in scripture]
    expect(
        checks,
        len(scripture) == args.scripture_lessons
        and len(non_scripture) == args.lessons - args.scripture_lessons,
        "reading-allocation",
        "Scripture and non-Scripture lesson allocation matches the contract",
        scripture=len(scripture),
        nonScripture=len(non_scripture),
    )

    empty_readings = []
    empty_reading_segments = []
    for lesson in lessons:
        reading = lesson.get("reading") or {}
        segments = reading.get("segments") or reading.get("verses") or []
        text = str(reading.get("text") or "").strip()
        if not segments and not text:
            empty_readings.append(lesson.get("lesson"))
        for segment in segments:
            if not first_text(segment, "sourceText", "text", "displayText", "editorialPointedText"):
                empty_reading_segments.append(
                    segment.get("ref") or segment.get("id") or lesson.get("lesson")
                )
    expect(checks, not empty_readings, "readings", "every lesson contains a nonempty full reading", failures=empty_readings)
    expect(checks, not empty_reading_segments, "reading-segments", "every declared reading segment contains source text", failures=empty_reading_segments[:30])

    if scripture:
        source = ((data.get("sources") or {}).get("chineseBible") or {})
        expect(
            checks,
            source.get("versionCode") == args.chinese_bible_version
            and (not args.chinese_bible_variant or source.get("variant") == args.chinese_bible_variant)
            and source.get("useScope") == "private-authorized"
            and bool(source.get("snapshot"))
            and bool(SHA256.fullmatch(str(source.get("snapshotSha256") or ""))),
            "chinese-bible",
            "Traditional-Chinese Bible version, variant, private-use scope, and snapshot hash are explicit",
            actual=source,
        )
        chinese_failures = []
        crosswalk_failures = []
        for lesson in scripture:
            for segment in (lesson.get("reading") or {}).get("segments") or (lesson.get("reading") or {}).get("verses") or []:
                exempt = bool(
                    str(segment.get("translationNote") or "").strip()
                    or str((lesson.get("reading") or {}).get("translationPlan") or "")
                    == "self-translated"
                )
                if not str(segment.get("translationZh") or "").strip() and not exempt:
                    chinese_failures.append(segment.get("ref") or segment.get("id"))
                crosswalk = segment.get("translationCrosswalk") or {}
                if exempt:
                    continue
                if (
                    crosswalk.get("translationVersionCode") != args.chinese_bible_version
                    or not str(crosswalk.get("translationRef") or "").strip()
                    or not str(crosswalk.get("translationRange") or "").strip()
                ):
                    crosswalk_failures.append(segment.get("ref") or segment.get("id"))
        expect(checks, not chinese_failures, "chinese-parallels", "every Scripture segment has a Traditional-Chinese parallel", failures=chinese_failures[:30])
        expect(checks, not crosswalk_failures, "chinese-crosswalk", "every Scripture segment records its RCUV range crosswalk", failures=crosswalk_failures[:30])

    if args.language == "hbo":
        haggadah = data.get("haggadah") or next(
            (item for item in data.get("appendices") or [] if item.get("kind") == "haggadah"),
            {},
        )
        expect(
            checks,
            len(haggadah.get("steps") or []) == args.haggadah_steps,
            "haggadah",
            "Hebrew reader contains the complete ordered Haggadah flow",
            actual=len(haggadah.get("steps") or []),
        )
        steps = haggadah.get("steps") or []
        haggadah_segment_failures = [
            step.get("key")
            for step in steps
            if not (step.get("segments") or [])
            or any(
                not first_text(segment, "editorialPointedText", "text", "sourceText")
                for segment in step.get("segments") or []
            )
        ]
        expect(
            checks,
            [step.get("key") for step in steps] == HAGGADAH_KEYS
            and int(haggadah.get("pointingGapCount", -1)) == 0
            and not haggadah_segment_failures
            and any(item.get("kind") == "haggadah" for item in data.get("appendices") or []),
            "haggadah-content",
            "Haggadah has the traditional fifteen-step order, complete pointed segments, and appendix metadata",
            actualOrder=[step.get("key") for step in steps],
            failures=haggadah_segment_failures,
        )

    audio = data.get("audio") or {}
    tracks = audio.get("tracks") or []
    if audio.get("status") == "not_recorded":
        audio_ok = audio.get("recordedTrackCount") == 0 and not tracks and bool(audio.get("policy"))
    else:
        audio_ok = (
            audio.get("recordedTrackCount") == len(tracks)
            and bool(tracks)
            and all(
                first_text(track, "path")
                and SHA256.fullmatch(str(track.get("sha256") or ""))
                and track.get("reviewStatus") == "reviewed"
                and isinstance(track.get("cues"), list)
                for track in tracks
            )
        )
    expect(checks, audio_ok, "audio-state", "audio manifest truthfully represents missing or reviewed recordings", actual=audio)

    build = data.get("build") or {}
    input_hashes = build.get("inputsSha256") or {}
    expect(
        checks,
        bool(build.get("builder"))
        and bool(input_hashes)
        and all(SHA256.fullmatch(str(value)) for value in input_hashes.values()),
        "build-provenance",
        "build provenance records the builder and cryptographic hashes of every input layer",
        inputs=len(input_hashes),
    )

    counts = data.get("counts") or {}
    expect(
        checks,
        counts.get("lessons") == args.lessons
        and counts.get("vocabulary") == expected_total
        and (counts.get("memoryVerses") or counts.get("memoryUnits")) == args.lessons * args.memory_per_lesson
        and counts.get("bibleChapters") == args.scripture_lessons
        and counts.get("prayersOrArticles") == args.lessons - args.scripture_lessons,
        "declared-counts",
        "declared counts match the frozen release contract",
        actual=counts,
    )

    ATTRIBUTION_KEYS = {
        "source", "sourceUrl", "licenseNote", "note", "crossCheck", "reviewNote",
        "exclusionReason", "printedTextNote", "crossCheckNote", "translationNote",
        "numberingNote", "verseNumberingNote", "roleDerivationNote", "edition",
    }

    def scanned_text(value: Any, key: str | None = None):
        if key in ATTRIBUTION_KEYS:
            return
        if isinstance(value, str):
            yield value
        elif isinstance(value, dict):
            for child_key, child in value.items():
                yield from scanned_text(child, child_key)
        elif isinstance(value, list):
            for child in value:
                yield from scanned_text(child, key)

    placeholder_hits = [value[:120] for value in scanned_text(data) if PLACEHOLDER.search(value)]
    expect(checks, not placeholder_hits, "placeholders", "master contains no planning placeholders", failures=placeholder_hits[:30])

    summary = {
        status: sum(check["status"] == status for check in checks)
        for status in ("PASS", "FAIL")
    }
    return {
        "result": "PASS" if summary["FAIL"] == 0 else "FAIL",
        "master": str(args.master),
        "volume": args.volume or None,
        "volumeTitle": data.get("volumeTitle", ""),
        "summary": summary,
        "checks": checks,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", type=Path, required=True)
    parser.add_argument("--language", choices=("hbo", "grc", "la"), required=True)
    parser.add_argument("--lessons", type=int, default=50)
    # 0 means "the textbook decides": while the named textbook lasts a lesson
    # is a textbook chapter with that chapter's own count, so the sizes are
    # uneven by design and a fixed quota here would reject a correct master.
    parser.add_argument("--vocabulary-per-lesson", type=int, default=0)
    parser.add_argument("--vocabulary-total", type=int, default=1000)
    parser.add_argument("--memory-per-lesson", type=int, default=2)
    parser.add_argument("--scripture-lessons", type=int, default=25)
    parser.add_argument("--haggadah-steps", type=int, default=15)
    parser.add_argument("--chinese-bible-version", default="cuv2010")
    parser.add_argument("--chinese-bible-variant", default="RCUV2（上帝版）")
    parser.add_argument(
        "--volume",
        type=int,
        default=0,
        help="多冊主檔要驗哪一冊；單冊主檔不要給",
    )
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = validate(args)
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(serialized, encoding="utf-8")
    print(json.dumps({"result": result["result"], "summary": result["summary"]}, ensure_ascii=False))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
