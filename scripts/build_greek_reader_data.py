#!/usr/bin/env python3
"""Assemble the one master file the Greek reader is built from.

Everything downstream — print, web, audio, QA — reads this file and nothing
else, so the parts have to meet here exactly once: the two volumes of fifty
lessons with their vocabulary and memory units, 上冊's fifty Scripture chapters,
下冊's fifty patristic and church readings, the five vocabulary appendices, the
Chrysostom liturgy appendix, and the Chinese that goes beside each of them.

The build fails rather than emitting a master with a hole in it.  A lesson
without its two memory verses, a chapter whose Chinese is missing, a reading
labelled complete without an extent, a count that disagrees with the contract —
each of those stops the build, because a master that is 98% assembled looks
exactly like a finished one to every step that comes after it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
VOCAB = ROOT / "data" / "originalReaders" / "vocabulary" / "greek-2000.json"
APPENDICES = ROOT / "data" / "originalReaders" / "vocabulary" / "greek-appendices.json"

SCRIPTURE_PLAN = CACHE / "scripture-plan.json"
PATRISTIC_PLAN = CACHE / "patristic-plan.json"
LITURGY = CACHE / "liturgy-chrysostom.json"
MEMORY = CACHE / "memory-verses.json"
MEMORY_SENTENCES = CACHE / "memory-sentences.json"
RCUV = CACHE / "RCUV2010.json"
DEUTERO_ZH = CACHE / "deuterocanon-zh.json"
GLOSSES = CACHE / "greek-2000-gloss-zh-by-lemma.json"
OUTPUT = CACHE / "greek-reader-two-volumes.json"

LESSON_COUNT = 50
WORDS_PER_LESSON = 20
MEMORY_PER_LESSON = 2
VOCAB_TARGET = 2000
# Per volume: 上冊 has a hundred memory verses, 下冊 a hundred memory sentences.
MEMORY_TARGET = 100
CHAPTER_COUNT = 50
READING_COUNT = 50
NT_LESSON_LAST = 25
PATRISTIC_LESSON_LAST = 25

VOLUME_ONE_HALVES = {True: "新約（Mounce 課程詞表）", False: "希臘文舊約（七十士譯本詞頻）"}
VOLUME_TWO_HALVES = {True: "教父文獻詞頻", False: "希臘教會文獻與禮儀詞頻"}


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path: Path, optional: bool = False):
    if not path.exists():
        if optional:
            return None
        raise FileNotFoundError(f"缺少建置輸入：{path}")
    return json.loads(path.read_text(encoding="utf-8"))


def psalm_to_mt(chapter: int, verse: int | None):
    from export_reader_rcuv2010_greek import psalm_crosswalk

    return psalm_crosswalk(chapter, verse)


def target_reference(book: str, chapter: int, verse: int | None):
    """The one shared crosswalk, so the master and the export agree by construction."""
    from export_reader_rcuv2010_greek import target_reference as shared

    return shared(book, chapter, verse)


def chinese_index(rcuv: dict) -> dict[tuple[str, int, int], str]:
    index: dict[tuple[str, int, int], str] = {}
    for book in rcuv["books"]:
        for chapter in book["chapters"]:
            for verse in chapter["verses"]:
                for number in range(verse["verse"], verse["verseEnd"] + 1):
                    index[(book["code"], chapter["chapter"], number)] = verse["text"]
    return index


def chinese_for(book: str, chapter: int, verse: int, index, offset: int = 0) -> str:
    target_chapter, target_verse, _ = target_reference(book, chapter, verse)
    if book == "Ps" and target_verse is not None:
        target_verse -= offset
        if target_verse is not None and target_verse < 1:
            # A superscription verse has no numbered Chinese counterpart; the
            # Chinese heading is carried separately by the chapter, not here.
            return ""
    return index.get((book, target_chapter, target_verse or verse), "")


def psalm_offset_for(book: str, chapter: int, greek_verse_count: int, rcuv: dict) -> tuple[int, str]:
    """Read the superscription offset off the two editions' verse counts."""
    if book != "Ps":
        return 0, ""
    from export_reader_rcuv2010_greek import psalm_verse_offset

    target_chapter, _, _ = psalm_to_mt(chapter, None)
    for entry in rcuv["books"]:
        if entry["code"] != "Ps":
            continue
        for chinese in entry["chapters"]:
            if chinese["chapter"] != target_chapter:
                continue
            mt_count = max(verse["verseEnd"] for verse in chinese["verses"])
            return psalm_verse_offset(greek_verse_count, mt_count)
    return 0, ""


def deuterocanon_index(payload: dict) -> tuple[dict[tuple[str, int, int], str], dict[tuple[str, int], int]]:
    """Chinese deuterocanon by reference, plus each chapter's verse count.

    The count is what makes the pairing safe: the 1933 Anglican edition
    versifies these books its own way, so a chapter is only paired verse by
    verse when both editions agree on how many verses it has.
    """
    index: dict[tuple[str, int, int], str] = {}
    counts: dict[tuple[str, int], int] = {}
    for book in payload["books"]:
        osis = book["ref"].split(".")[0]
        counts[(osis, book["chapter"])] = book["verseCount"]
        for verse in book["verses"]:
            index[(osis, book["chapter"], verse["verse"])] = verse["text"]
    return index, counts


# In the Greek manuscript order that Swete prints, Sirach 30:25-33:16a and
# 33:16b-36:10 are transposed relative to the Hebrew, Syriac and Latin order that
# modern translations restore.  Verse numbers in that block therefore point at
# different text in the two traditions even when the chapters have the same
# number of verses, which is how Swete's "ὁ φοβούμενος Κύριον οὐ μὴ
# εὐλαβηθήσεται" ended up beside the Chinese for a verse about table manners.
SIRACH_TRANSPOSED_CHAPTERS = range(30, 37)

# The reader's Tobit is the Sinaiticus recension (GII); the 1933 Anglican
# translation follows the shorter GI / Vulgate tradition.  The two diverge in
# content, not merely in numbering, so only the chapter whose alignment has
# actually been checked verse by verse is paired.  Chapter 14 has the same
# verse count in both and still says something entirely different.
TOBIT_VERIFIED_CHAPTERS = {1}


def deuterocanon_text(
    book: str, chapter: int, verse: int, greek_verse_count: int, index, counts
) -> tuple[str, str]:
    """Return (chinese, note).  An unmatched versification yields no Chinese."""
    if book == "TobS" and chapter not in TOBIT_VERIFIED_CHAPTERS:
        return "", (
            "本讀本的多比傳用西奈抄本（GII），1933 年譯本循較短的 GI／武加大傳統，"
            "兩者內容不同傳本，節號不可互指；僅第 1 章經逐節核對後對照。"
        )
    if book == "Sir" and chapter in SIRACH_TRANSPOSED_CHAPTERS:
        return "", (
            "德訓篇 30–36 章在希臘抄本次序與復原次序之間整塊錯位，"
            "Swete 依抄本、1933 年譯本依復原次序，節號不可互指，中譯待人工對照。"
        )
    chinese_count = counts.get((book, chapter))
    if chinese_count is None:
        return "", "1933 年聖公會本未匯入本章，中譯待補。"
    if chinese_count != greek_verse_count:
        return "", (
            f"1933 年聖公會本本章 {chinese_count} 節，Swete 希臘文 {greek_verse_count} 節，"
            "兩版分節不一致，逐節對照須人工處理，不以節號硬配。"
        )
    return index.get((book, chapter, verse), ""), ""


def deutero_greek_verse_count(book: str, chapter: int) -> int:
    """How many verses Swete prints for a deuterocanonical chapter."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import greek_source_texts as sources

    try:
        return len(sources.load_chapter(book, chapter))
    except (LookupError, KeyError, FileNotFoundError):
        return -1


def psalm_offset_for_memory(chapter: int, rcuv: dict, scripture: dict) -> tuple[int, str]:
    """Superscription offset for a psalm a memory verse was drawn from.

    Where the Septuagint merges or splits a psalm the two editions differ by far
    more than a heading, and no offset is correct.  Say so and withhold the
    Chinese rather than printing a line that belongs to another verse.
    """
    count = deutero_greek_verse_count("Ps", chapter)
    if count < 0:
        return 0, ""
    try:
        return psalm_offset_for("Ps", chapter, count, rcuv)
    except LookupError as error:
        return -1, f"七十士與馬所拉本此篇分合不同，逐節對照須人工處理（{error}）。"


def volume_counts(lessons: list[dict]) -> dict:
    return {
        "lessons": len(lessons),
        "vocabulary": sum(len(lesson["vocabulary"]) for lesson in lessons),
        "vocabularyGlossedZh": sum(
            1 for lesson in lessons for word in lesson["vocabulary"] if word["glossZh"]
        ),
        "memoryUnits": sum(len(lesson["memoryUnits"]) for lesson in lessons),
        "readings": sum(1 for lesson in lessons if lesson["reading"]),
    }


def build_volume_one(
    words_by_lesson, memory, scripture, rcuv, zh, zh_deutero, zh_deutero_counts,
    greek_counts, interlinear, glosses, problems,
) -> list[dict]:
    """上冊: fifty lessons, each a chapter and two memory verses."""
    by_lesson_memory: dict[int, list[dict]] = {}
    for verse in memory["verses"]:
        by_lesson_memory.setdefault(verse["lesson"], []).append(verse)
    chapters_by_lesson = {chapter["lesson"]: chapter for chapter in scripture["chapters"]}

    lessons = []
    for number in range(1, LESSON_COUNT + 1):
        words = sorted(words_by_lesson.get(number, []), key=lambda item: item["lessonSlot"])
        if len(words) != WORDS_PER_LESSON:
            problems.append(f"上冊第 {number} 課有 {len(words)} 詞，應為 {WORDS_PER_LESSON}")
        verses = sorted(by_lesson_memory.get(number, []), key=lambda item: item["slot"])
        if len(verses) != MEMORY_PER_LESSON:
            problems.append(
                f"上冊第 {number} 課的記憶單元有 {len(verses)} 節，應為 {MEMORY_PER_LESSON}"
            )

        memory_rows = []
        for verse in verses:
            translation = verse.get("translationZh") or ""
            if not translation:
                if verse["corpus"] in {"new-testament", "septuagint"}:
                    # Psalms need the superscription offset as well as the
                    # chapter crosswalk; without it the Chinese sits one verse
                    # below the Greek for every psalm with a numbered heading.
                    offset = 0
                    if verse["book"] == "Ps":
                        offset, note = psalm_offset_for_memory(
                            verse["chapter"], rcuv, scripture
                        )
                        if note:
                            verse["translationNote"] = note
                    translation = (
                        ""
                        if offset < 0
                        else chinese_for(
                            verse["book"], verse["chapter"], verse["verse"], zh, offset
                        )
                    )
                elif verse["corpus"] == "deuterocanonical":
                    greek_count = greek_counts.get(
                        (verse["book"], verse["chapter"]),
                        deutero_greek_verse_count(verse["book"], verse["chapter"]),
                    )
                    translation, note = deuterocanon_text(
                        verse["book"], verse["chapter"], verse["verse"],
                        greek_count, zh_deutero, zh_deutero_counts,
                    )
                    if note:
                        verse["translationNote"] = note
                if not translation:
                    unit = interlinear.get(f"memory:{verse['ref']}") or {}
                    translation = unit.get("translationZh", "")
            memory_rows.append(
                {
                    **verse,
                    "kind": "verse",
                    "translationZh": translation,
                    "matchedCount": verse.get("matchCount", 0),
                    "selectionReason": (
                        f"命中本課生詞 {verse.get('matchCount', 0)} 個，"
                        f"累積已學覆蓋率 {verse.get('knownCoverage', 0)}，"
                        f"{verse['wordCount']} 詞，比對方式 {verse['matchMethod']}"
                    ),
                }
            )

        reading = chapters_by_lesson.get(number)
        if reading is None:
            problems.append(f"上冊第 {number} 課沒有讀文")
        else:
            reading = {**reading, "kind": "scripture_chapter"}

        lessons.append(
            {
                "volume": 1,
                "lesson": number,
                "id": f"grc-v1-lesson-{number:02d}",
                "title": f"上冊第 {number} 課",
                "vocabularySource": VOLUME_ONE_HALVES[number <= NT_LESSON_LAST],
                "vocabularyCount": len(words),
                "vocabulary": vocabulary_rows(words, glosses),
                "memoryUnits": memory_rows,
                "reading": reading,
            }
        )
    return lessons


def build_volume_two(
    words_by_lesson, sentences, patristic, interlinear, glosses, problems,
) -> list[dict]:
    """下冊: fifty lessons, each a reading and two memory sentences."""
    by_lesson_sentences: dict[int, list[dict]] = {}
    for sentence in sentences["sentences"]:
        by_lesson_sentences.setdefault(sentence["lesson"], []).append(sentence)
    readings_by_lesson = {reading["lesson"]: reading for reading in patristic["readings"]}

    lessons = []
    for number in range(1, LESSON_COUNT + 1):
        words = sorted(words_by_lesson.get(number, []), key=lambda item: item["lessonSlot"])
        if len(words) != WORDS_PER_LESSON:
            problems.append(f"下冊第 {number} 課有 {len(words)} 詞，應為 {WORDS_PER_LESSON}")
        chosen = sorted(by_lesson_sentences.get(number, []), key=lambda item: item["slot"])
        if len(chosen) != MEMORY_PER_LESSON:
            problems.append(
                f"下冊第 {number} 課的記憶單元有 {len(chosen)} 句，應為 {MEMORY_PER_LESSON}"
            )

        memory_rows = []
        for sentence in chosen:
            translation = sentence.get("translationZh") or ""
            if not translation:
                # 下冊's readings have no published Chinese at all, so the whole
                # sentence rendering comes from the interlinear layer, which
                # keys these units by their own reference.
                unit = interlinear.get(f"sentence:{sentence['ref']}") or {}
                translation = unit.get("translationZh", "")
            memory_rows.append(
                {
                    **sentence,
                    "kind": "sentence",
                    "translationZh": translation,
                    "matchedCount": sentence.get("matchCount", 0),
                    "selectionReason": (
                        f"命中本課生詞 {sentence.get('matchCount', 0)} 個，"
                        f"累積已學覆蓋率 {sentence.get('knownCoverage', 0)}，"
                        f"{sentence['wordCount']} 詞，出自〈{sentence['readingTitleZh']}〉"
                    ),
                }
            )

        reading = readings_by_lesson.get(number)
        if reading is None:
            problems.append(f"下冊第 {number} 課沒有讀文")
        else:
            reading = {**reading, "kind": "patristic_reading"}

        lessons.append(
            {
                "volume": 2,
                "lesson": number,
                "id": f"grc-v2-lesson-{number:02d}",
                "title": f"下冊第 {number} 課",
                "vocabularySource": VOLUME_TWO_HALVES[number <= PATRISTIC_LESSON_LAST],
                "vocabularyCount": len(words),
                "vocabulary": vocabulary_rows(words, glosses),
                "memoryUnits": memory_rows,
                "reading": reading,
            }
        )
    return lessons


def vocabulary_rows(words: list[dict], glosses: dict[str, dict]) -> list[dict]:
    rows = []
    for word in words:
        # Keyed by lemma, never by ordinal: lifting the proper names into the
        # appendix renumbered the whole list, and an ordinal-keyed gloss layer
        # would shift every meaning by one without raising anything.
        gloss = glosses.get(word["lemma"], {}).get("glossZh", "")
        rows.append(
            {
                "id": f"grc-vocab-v{word['volume']}-{word['ordinal']:04d}",
                "volume": word["volume"],
                "ordinal": word["ordinal"],
                "corpus": word["corpus"],
                "lesson": word["lesson"],
                "lessonSlot": word["lessonSlot"],
                "slot": word["lessonSlot"],
                "printedEntry": word.get("printedEntry") or word["lemma"],
                "headword": word["headword"],
                "lemma": word["lemma"],
                "transliteration": word.get("textbookTransliteration", ""),
                "textbookTransliteration": word.get("textbookTransliteration", ""),
                "transliterationSystem": word.get("transliterationSystem", ""),
                "transliterationStatus": word.get("transliterationStatus", ""),
                "glossEn": word.get("glossEn", ""),
                "glossZh": gloss,
                # Written back by scripts/backfill_greek_pos.py; Hebrew and Latin
                # both print a 詞類 column and this is where Greek's comes from.
                "pos": word.get("pos", ""),
                "strong": word.get("strong", ""),
                "frequency": word.get("frequency", 0),
                "withinKoine": word.get("withinKoine", True),
                "isProperName": word.get("isProperName", False),
                "properNameTypes": word.get("properNameTypes", []),
                "verification": word["verification"],
            }
        )
    return rows


def attach_chapter_chinese(scripture, rcuv, zh, zh_deutero, zh_deutero_counts, interlinear) -> int:
    """Chinese for 上冊's fifty chapters, verse by verse.  Returns the miss count."""
    missing = 0
    for chapter in scripture["chapters"]:
        try:
            offset, offset_note = psalm_offset_for(
                chapter["osisBook"], chapter["chapter"], chapter["verseCount"], rcuv
            )
        except LookupError as error:
            offset, offset_note = -1, f"逐節對照須人工處理（{error}）。"
        if offset_note:
            chapter["verseNumberingNote"] = offset_note
        for verse in chapter["verses"]:
            if chapter["corpus"] in {"new-testament", "septuagint"}:
                verse["translationZh"] = (
                    ""
                    if offset < 0
                    else chinese_for(
                        chapter["osisBook"], chapter["chapter"], verse["verse"], zh, offset
                    )
                )
                target_chapter, target_verse, _ = target_reference(
                    chapter["osisBook"], chapter["chapter"], verse["verse"]
                )
                if chapter["osisBook"] == "Ps" and target_verse is not None:
                    target_verse -= offset
                verse["translationCrosswalk"] = {
                    "translationVersionCode": "cuv2010",
                    "translationRef": f"{chapter['osisBook']}.{target_chapter}.{target_verse}",
                    "translationRange": str(target_verse),
                }
                if not verse["translationZh"]:
                    if offset < 0:
                        verse["translationNote"] = offset_note
                    elif offset and verse["verse"] <= offset:
                        verse["translationNote"] = "七十士標題節，中文本不編號"
            elif chapter["corpus"] == "deuterocanonical":
                verse["translationZh"], note = deuterocanon_text(
                    chapter["osisBook"], chapter["chapter"], verse["verse"],
                    chapter["verseCount"] + len(chapter.get("absentVerses") or []),
                    zh_deutero, zh_deutero_counts,
                )
                if note:
                    verse["translationNote"] = note
                verse["translationCrosswalk"] = {
                    "translationVersionCode": "cuv2010",
                    "translationRef": f"{chapter['osisBook']}.{chapter['chapter']}.{verse['verse']}",
                    "translationRange": str(verse["verse"]),
                    "translationSource": "1933 年聖公會出版次經（非 RCUV）",
                }
            else:
                unit = interlinear.get(f"scripture:{verse['ref']}") or {}
                verse["translationZh"] = unit.get("translationZh", "")
                if verse["translationZh"]:
                    verse["translationNote"] = "偽經無中文聖經，此為自譯。"
            if (
                not verse["translationZh"]
                and chapter["corpus"] != "pseudepigrapha"
                and not verse.get("translationNote")
            ):
                missing += 1
                print(f"    缺中文 {chapter['ref']}:{verse['verse']}")
    return missing


def attach_reading_chinese(patristic, interlinear) -> int:
    """Chinese for 下冊's fifty readings.  Every segment is self-translated."""
    missing = 0
    for reading in patristic["readings"]:
        for segment in reading["segments"]:
            unit = interlinear.get(f"patristic:{reading['ordinal']}:{segment['ref']}") or {}
            segment["translationZh"] = unit.get("translationZh", "")
            if segment["translationZh"]:
                segment["translationNote"] = "無權威中譯，此為自譯。"
            else:
                missing += 1
    return missing


def build(strict: bool = True) -> dict:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

    vocabulary = load(VOCAB)["entries"]
    scripture = load(SCRIPTURE_PLAN)
    patristic = load(PATRISTIC_PLAN)
    liturgy = load(LITURGY)
    memory = load(MEMORY)
    sentences = load(MEMORY_SENTENCES)
    rcuv = load(RCUV)
    deutero = load(DEUTERO_ZH)
    appendices = load(APPENDICES)
    glosses = (load(GLOSSES, optional=True) or {}).get("glosses", {})
    interlinear = (load(CACHE / "interlinear.json", optional=True) or {}).get("units", {})

    problems: list[str] = []

    if len(vocabulary) != VOCAB_TARGET:
        problems.append(f"詞彙 {len(vocabulary)} 筆，應為 {VOCAB_TARGET}")
    if len(scripture["chapters"]) != CHAPTER_COUNT:
        problems.append(f"章目 {len(scripture['chapters'])} 章，應為 {CHAPTER_COUNT}")
    if len(patristic["readings"]) != READING_COUNT:
        problems.append(f"下冊讀文 {len(patristic['readings'])} 篇，應為 {READING_COUNT}")
    if len(memory["verses"]) != MEMORY_TARGET:
        problems.append(f"上冊記憶單元 {len(memory['verses'])} 節，應為 {MEMORY_TARGET}")
    if len(sentences["sentences"]) != MEMORY_TARGET:
        problems.append(f"下冊記憶單元 {len(sentences['sentences'])} 句，應為 {MEMORY_TARGET}")

    zh = chinese_index(rcuv)
    zh_deutero, zh_deutero_counts = deuterocanon_index(deutero)

    greek_counts: dict[tuple[str, int], int] = {}
    for chapter in scripture["chapters"]:
        greek_counts[(chapter["osisBook"], chapter["chapter"])] = chapter["verseCount"]

    words_by_volume: dict[int, dict[int, list[dict]]] = {1: {}, 2: {}}
    for entry in vocabulary:
        volume = entry.get("volume")
        if volume not in words_by_volume:
            problems.append(f"詞條 {entry['lemma']} 沒有冊別")
            continue
        words_by_volume[volume].setdefault(entry["lesson"], []).append(entry)

    # A word whose Chinese never arrived is the one failure that looks like
    # success downstream: the row prints, just empty.
    ungloss = [entry["lemma"] for entry in vocabulary if not glosses.get(entry["lemma"], {}).get("glossZh")]
    if ungloss:
        problems.append(f"{len(ungloss)} 筆詞彙沒有繁體中文詞義（例：{'、'.join(ungloss[:5])}）")

    volume_one = build_volume_one(
        words_by_volume[1], memory, scripture, rcuv, zh, zh_deutero, zh_deutero_counts,
        greek_counts, interlinear, glosses, problems,
    )
    volume_two = build_volume_two(
        words_by_volume[2], sentences, patristic, interlinear, glosses, problems,
    )

    chapter_zh_missing = attach_chapter_chinese(
        scripture, rcuv, zh, zh_deutero, zh_deutero_counts, interlinear
    )
    if chapter_zh_missing:
        problems.append(f"{chapter_zh_missing} 個經節在應有中譯的語料裡查不到中文")

    reading_zh_missing = attach_reading_chinese(patristic, interlinear)
    if reading_zh_missing:
        problems.append(
            f"{reading_zh_missing} 個下冊讀文段落尚無中譯（逐段自譯層 interlinear.json 待跑）"
        )

    glossed = sum(1 for entry in vocabulary if glosses.get(entry["lemma"], {}).get("glossZh"))
    counts = {
        "volumes": 2,
        "lessons": len(volume_one) + len(volume_two),
        "vocabulary": len(vocabulary),
        "vocabularyGlossedZh": glossed,
        "memoryUnits": len(memory["verses"]) + len(sentences["sentences"]),
        "scriptureChapters": len(scripture["chapters"]),
        "patristicReadings": len(patristic["readings"]),
        "appendixTables": len(appendices["appendices"]),
        "appendixEntries": sum(len(item["entries"]) for item in appendices["appendices"]),
        "liturgySteps": liturgy["summary"]["stepCount"],
        "scriptureWords": scripture["summary"]["wordCount"],
        "patristicWords": patristic["summary"]["wordCount"],
        "liturgyWords": liturgy["summary"]["wordCount"],
    }
    counts["totalRunningWords"] = (
        counts["scriptureWords"] + counts["patristicWords"] + counts["liturgyWords"]
    )

    if glossed < VOCAB_TARGET:
        # "vocabulary_complete" would claim the two thousand words are finished;
        # the narrowest true state while the gloss layer is short is this one.
        status = "source_frozen"
    elif reading_zh_missing or chapter_zh_missing:
        status = "content_complete_translation_pending"
    else:
        status = "content_complete_layout_pending"

    master = {
        "schemaVersion": "2.0.0",
        "title": "通用希臘文原文讀本",
        "subtitle": (
            "兩冊・一百課・二千詞・二百則背誦・五十章經文・"
            "五十篇教父與希臘教會文獻・金口若望事奉聖禮全文"
        ),
        "language": "Koine Greek",
        "languageCode": "grc",
        "privateUse": True,
        "releaseStatus": status,
        "generatedOn": date.today().isoformat(),
        "textbook": "William D. Mounce, Basics of Biblical Greek Grammar（上冊新約部分）",
        "counts": counts,
        "textPolicy": {
            "newTestament": "SBLGNT（MorphGNT 分析）；顯示層剝除校勘記號，原文層保留",
            "septuagintAndBeyond": "Swete 劍橋本 1909–1930；方括號補字一律保留",
            "chineseBible": "《和合本修訂版》（2010）RCUV2（上帝版）",
            "chineseDeuterocanon": "1933 年聖公會出版次經",
            "chinesePseudepigrapha": "自譯，逐段標「自譯」",
            "psalmNumbering": "七十士編號一律經對照表換算成馬所拉編號後才取中文",
            "jeremiahNumbering": "七十士耶利米書自第 26 章起與馬所拉本章號不同，一律經同一張對照表換算",
            "churchDocuments": "教規彙編與頌歌取自希臘文維基文庫錄入本，逐份記修訂版本號與雜湊",
        },
        "printProfile": {
            "preset": "JIS_B5_READER",
            "trim": "JIS_B5",
            "widthMm": 182,
            "heightMm": 257,
            "mirroredMargins": True,
            "openingPattern": "recto-start",
            "marginTopMm": 20,
            "marginBottomMm": 22,
            "marginInsideMm": 22,
            "marginOutsideMm": 16,
        },
        "sources": {
            "scripture": {
                "newTestament": scripture["sources"]["newTestament"],
                "septuagintAndBeyond": scripture["sources"]["septuagintAndBeyond"],
            },
            "chineseBible": {
                "versionCode": rcuv["translation"]["versionCode"],
                "titleZh": rcuv["translation"]["titleZh"],
                "variant": rcuv["translation"]["variant"],
                "publisher": rcuv["translation"]["publisher"],
                "useScope": rcuv["translation"]["useScope"],
                "snapshot": str(RCUV.relative_to(ROOT)).replace("\\", "/"),
                "snapshotSha256": sha256_of(RCUV),
            },
            "chineseDeuterocanon": {
                "versionCode": deutero["translation"]["versionCode"],
                "titleZh": deutero["translation"]["titleZh"],
                "useScope": deutero["translation"]["useScope"],
                "snapshot": str(DEUTERO_ZH.relative_to(ROOT)).replace("\\", "/"),
                "snapshotSha256": sha256_of(DEUTERO_ZH),
            },
            "patristic": {
                "note": (
                    "逐篇記於 patristic-plan.json；使徒教父、First1KGreek、repo 信經檔、"
                    "希臘文維基文庫教規與頌歌、GOARCH 禮儀五系。"
                ),
            },
            "vocabulary": {
                "textbook": "William D. Mounce, Basics of Biblical Greek Grammar",
                "snapshot": str(VOCAB.relative_to(ROOT)).replace("\\", "/"),
                "snapshotSha256": sha256_of(VOCAB),
            },
        },
        "volumes": [
            {
                "volume": 1,
                "slug": "grc-vol-1",
                "title": "上冊《新約與七十士譯本》",
                "subtitle": "五十課・一千詞・一百節背誦・五十章完整經文",
                "memoryUnitKind": "verse",
                "corpusByHalf": {"1-25": "新約", "26-50": "希臘文舊約（七十士譯本、次經、偽經）"},
                "counts": volume_counts(volume_one),
                "lessons": volume_one,
                "appendices": [],
            },
            {
                "volume": 2,
                "slug": "grc-vol-2",
                "title": "下冊《教父文獻與希臘教會文獻》",
                "subtitle": "五十課・一千詞・一百句背誦・五十篇讀文・金口若望事奉聖禮全文",
                "memoryUnitKind": "sentence",
                "corpusByHalf": {"1-25": "教父文獻", "26-50": "希臘教會文獻與禮儀文本"},
                "counts": volume_counts(volume_two),
                "lessons": volume_two,
                "appendices": [
                    {
                        "kind": "divine-liturgy",
                        "key": "divine-liturgy-chrysostom",
                        "title": liturgy["title"],
                        "titleGrc": liturgy["titleGrc"],
                        "stepCount": liturgy["summary"]["stepCount"],
                        "sectionCount": liturgy["summary"]["sectionCount"],
                        "placement": liturgy["placement"],
                        "steps": liturgy["steps"],
                    }
                ],
            },
        ],
        "appendices": [
            {
                "kind": "vocabulary-table",
                "key": f"appendix-{index}",
                "title": table["title"],
                "note": table.get("note", ""),
                "entryCount": len(table["entries"]),
                "entries": table["entries"],
            }
            for index, table in enumerate(appendices["appendices"], start=1)
        ],
        "audio": {
            "status": "not_recorded",
            "recordedTrackCount": 0,
            "tracks": [],
            "profile": "Mounce 標準 Erasmian；拜占庭讀音另立音軌，不混錄",
            "policy": "沒有真實錄音就不顯示播放鍵；TTS 不算數",
        },
        "build": {
            "builder": "scripts/build_greek_reader_data.py",
            "inputsSha256": {
                path.name: sha256_of(path)
                for path in [
                    VOCAB, SCRIPTURE_PLAN, PATRISTIC_PLAN, LITURGY, MEMORY,
                    MEMORY_SENTENCES, RCUV, DEUTERO_ZH, APPENDICES,
                ]
            },
        },
        "openProblems": problems,
    }

    if problems and strict:
        for problem in problems:
            print(f"  ✗ {problem}")
        raise SystemExit("組裝未通過：先修好上列問題再寫檔")
    return master


def main() -> None:
    parser = argparse.ArgumentParser(description="組裝希臘文讀本主檔（兩冊）")
    parser.add_argument("--write", action="store_true", help="寫出主檔")
    parser.add_argument("--report-only", action="store_true", help="即使有問題也不中斷，只列出")
    args = parser.parse_args()

    master = build(strict=not args.report_only)
    counts = master["counts"]
    print(f"  狀態 {master['releaseStatus']}")
    for key, value in counts.items():
        print(f"    {key:<24s} {value}")
    for volume in master["volumes"]:
        print(f"  {volume['title']} {volume['counts']}")
    if master["openProblems"]:
        print("  未解問題：")
        for problem in master["openProblems"]:
            print(f"    ✗ {problem}")

    if args.write:
        OUTPUT.write_text(json.dumps(master, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已寫出 {OUTPUT}")
    else:
        print("（未寫檔；加 --write 才會輸出）")


if __name__ == "__main__":
    main()
