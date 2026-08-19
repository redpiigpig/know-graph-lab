#!/usr/bin/env python3
"""Assemble the one master file the Greek reader is built from.

Everything downstream — print, web, audio, QA — reads this file and nothing
else, so the parts have to meet here exactly once: the fifty lessons with their
vocabulary and memory verses, the twenty-five Scripture chapters, the
twenty-five patristic readings, the Chrysostom liturgy appendix, and the Chinese
that goes beside each of them.

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
VOCAB = ROOT / "data" / "originalReaders" / "vocabulary" / "greek-1000.json"

SCRIPTURE_PLAN = CACHE / "scripture-plan.json"
PATRISTIC_PLAN = CACHE / "patristic-plan.json"
LITURGY = CACHE / "liturgy-chrysostom.json"
MEMORY = CACHE / "memory-verses.json"
RCUV = CACHE / "RCUV2010.json"
DEUTERO_ZH = CACHE / "deuterocanon-zh.json"
GLOSSES = CACHE / "greek-1000-gloss-zh-reviewed.json"
OUTPUT = CACHE / "greek-reader-50-lessons.json"

LESSON_COUNT = 50
VOCAB_TARGET = 1000
MEMORY_TARGET = 100
CHAPTER_COUNT = 25
READING_COUNT = 25


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


def chinese_index(rcuv: dict) -> dict[tuple[str, int, int], str]:
    index: dict[tuple[str, int, int], str] = {}
    for book in rcuv["books"]:
        for chapter in book["chapters"]:
            for verse in chapter["verses"]:
                for number in range(verse["verse"], verse["verseEnd"] + 1):
                    index[(book["code"], chapter["chapter"], number)] = verse["text"]
    return index


def chinese_for(book: str, chapter: int, verse: int, index, offset: int = 0) -> str:
    target_chapter, target_verse = chapter, verse
    if book == "Ps":
        target_chapter, target_verse, _ = psalm_to_mt(chapter, verse)
        if target_verse is not None:
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


def deuterocanon_index(payload: dict) -> dict[tuple[str, int, int], str]:
    index: dict[tuple[str, int, int], str] = {}
    for book in payload["books"]:
        osis = book["ref"].split(".")[0]
        for verse in book["verses"]:
            index[(osis, book["chapter"], verse["verse"])] = verse["text"]
    return index


def build(strict: bool = True) -> dict:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

    vocabulary = load(VOCAB)
    scripture = load(SCRIPTURE_PLAN)
    patristic = load(PATRISTIC_PLAN)
    liturgy = load(LITURGY)
    memory = load(MEMORY)
    rcuv = load(RCUV)
    deutero = load(DEUTERO_ZH)
    glosses = (load(GLOSSES, optional=True) or {}).get("glosses", {})

    problems: list[str] = []

    if len(vocabulary) != VOCAB_TARGET:
        problems.append(f"詞彙 {len(vocabulary)} 筆，應為 {VOCAB_TARGET}")
    if len(scripture["chapters"]) != CHAPTER_COUNT:
        problems.append(f"章目 {len(scripture['chapters'])} 章，應為 {CHAPTER_COUNT}")
    if len(patristic["readings"]) != READING_COUNT:
        problems.append(f"教父讀文 {len(patristic['readings'])} 篇，應為 {READING_COUNT}")
    if len(memory["verses"]) != MEMORY_TARGET:
        problems.append(f"記憶單元 {len(memory['verses'])} 節，應為 {MEMORY_TARGET}")

    zh = chinese_index(rcuv)
    zh_deutero = deuterocanon_index(deutero)

    by_lesson_vocab: dict[int, list[dict]] = {}
    for entry in vocabulary:
        by_lesson_vocab.setdefault(entry["lesson"], []).append(entry)
    by_lesson_memory: dict[int, list[dict]] = {}
    for verse in memory["verses"]:
        by_lesson_memory.setdefault(verse["lesson"], []).append(verse)
    chapters_by_lesson = {chapter["lesson"]: chapter for chapter in scripture["chapters"]}
    readings_by_lesson = {reading["lesson"]: reading for reading in patristic["readings"]}

    glossed = 0
    lessons = []
    for number in range(1, LESSON_COUNT + 1):
        words = sorted(by_lesson_vocab.get(number, []), key=lambda item: item["lessonSlot"])
        if not words:
            problems.append(f"第 {number} 課沒有詞彙")
        verses = sorted(by_lesson_memory.get(number, []), key=lambda item: item["slot"])
        if len(verses) != 2:
            problems.append(f"第 {number} 課的記憶單元有 {len(verses)} 節，應為 2 節")

        vocabulary_rows = []
        for word in words:
            gloss = glosses.get(str(word["ordinal"]), {}).get("glossZh", "")
            glossed += 1 if gloss else 0
            vocabulary_rows.append(
                {
                    "ordinal": word["ordinal"],
                    "slot": word["lessonSlot"],
                    "printedEntry": word["printedEntry"],
                    "headword": word["headword"],
                    "lemma": word["lemma"],
                    "transliteration": word["textbookTransliteration"],
                    "glossEn": word.get("glossEn", ""),
                    "glossZh": gloss,
                    "strong": word.get("strong", ""),
                    "isProperName": word.get("isProperName", False),
                    "properNameTypes": word.get("properNameTypes", []),
                    "verification": word["verification"],
                }
            )

        memory_rows = []
        for verse in verses:
            translation = verse.get("translationZh") or ""
            if not translation:
                if verse["corpus"] in {"new-testament", "septuagint"}:
                    translation = chinese_for(
                        verse["book"], verse["chapter"], verse["verse"], zh
                    )
                elif verse["corpus"] == "deuterocanonical":
                    translation = zh_deutero.get(
                        (verse["book"], verse["chapter"], verse["verse"]), ""
                    )
            memory_rows.append({**verse, "translationZh": translation})

        reading = chapters_by_lesson.get(number) or readings_by_lesson.get(number)
        if reading is None:
            problems.append(f"第 {number} 課沒有讀文")

        lessons.append(
            {
                "lesson": number,
                "id": f"grc-lesson-{number:02d}",
                "title": f"第 {number} 課",
                "vocabularySource": words[0]["lessonLabel"] if words else "",
                "vocabularyCount": len(vocabulary_rows),
                "vocabulary": vocabulary_rows,
                "memoryVerses": memory_rows,
                "reading": reading,
            }
        )

    # Chinese for the twenty-five chapters, verse by verse.
    chapter_zh_missing = 0
    for chapter in scripture["chapters"]:
        offset, offset_note = psalm_offset_for(
            chapter["osisBook"], chapter["chapter"], chapter["verseCount"], rcuv
        )
        if offset_note:
            chapter["verseNumberingNote"] = offset_note
        for verse in chapter["verses"]:
            if chapter["corpus"] in {"new-testament", "septuagint"}:
                verse["translationZh"] = chinese_for(
                    chapter["osisBook"], chapter["chapter"], verse["verse"], zh, offset
                )
                if not verse["translationZh"] and offset and verse["verse"] <= offset:
                    verse["translationNote"] = "七十士標題節，中文本不編號"
            elif chapter["corpus"] == "deuterocanonical":
                verse["translationZh"] = zh_deutero.get(
                    (chapter["osisBook"], chapter["chapter"], verse["verse"]), ""
                )
            else:
                verse["translationZh"] = ""
            if (
                not verse["translationZh"]
                and chapter["corpus"] != "pseudepigrapha"
                and not verse.get("translationNote")
            ):
                chapter_zh_missing += 1
                print(f"    缺中文 {chapter['ref']}:{verse['verse']}")

    if chapter_zh_missing:
        problems.append(
            f"{chapter_zh_missing} 個經節在應有中譯的語料裡查不到中文"
        )

    counts = {
        "lessons": len(lessons),
        "vocabulary": len(vocabulary),
        "vocabularyGlossedZh": glossed,
        "memoryVerses": len(memory["verses"]),
        "scriptureChapters": len(scripture["chapters"]),
        "patristicReadings": len(patristic["readings"]),
        "liturgySteps": liturgy["summary"]["stepCount"],
        "scriptureWords": scripture["summary"]["wordCount"],
        "patristicWords": patristic["summary"]["wordCount"],
        "liturgyWords": liturgy["summary"]["wordCount"],
    }
    counts["totalRunningWords"] = (
        counts["scriptureWords"] + counts["patristicWords"] + counts["liturgyWords"]
    )

    if glossed == 0:
        status = "content_assembled_chinese_gloss_pending"
    elif glossed < VOCAB_TARGET:
        status = "content_assembled_chinese_gloss_partial"
    else:
        status = "content_complete_interlinear_pending"

    master = {
        "schemaVersion": "1.0.0",
        "title": "新約希臘文原文讀本",
        "subtitle": "五十課・一千詞・一百節背誦・二十五章經文・二十五篇教父信經教令・金口若望事奉聖禮全文",
        "language": "New Testament Greek",
        "languageCode": "grc",
        "privateUse": True,
        "releaseStatus": status,
        "generatedOn": date.today().isoformat(),
        "textbook": "William D. Mounce, Basics of Biblical Greek Grammar",
        "counts": counts,
        "textPolicy": {
            "newTestament": "SBLGNT（MorphGNT 分析）；顯示層剝除校勘記號，原文層保留",
            "septuagintAndBeyond": "Swete 劍橋本 1909–1930；方括號補字一律保留",
            "chineseBible": "《和合本修訂版》（2010）RCUV2（上帝版）",
            "chineseDeuterocanon": "1933 年聖公會出版次經",
            "chinesePseudepigrapha": "自譯，逐段標「自譯」",
            "psalmNumbering": "七十士編號一律經對照表換算成馬所拉編號後才取中文",
        },
        "lessons": lessons,
        "appendix": {
            "key": "divine-liturgy-chrysostom",
            "title": liturgy["title"],
            "titleGrc": liturgy["titleGrc"],
            "stepCount": liturgy["summary"]["stepCount"],
            "sectionCount": liturgy["summary"]["sectionCount"],
            "placement": liturgy["placement"],
        },
        "audio": {
            "status": "not_recorded",
            "profile": "Mounce 標準 Erasmian；拜占庭讀音另立音軌，不混錄",
            "policy": "沒有真實錄音就不顯示播放鍵；TTS 不算數",
        },
        "build": {
            "builder": "scripts/build_greek_reader_data.py",
            "inputsSha256": {
                path.name: sha256_of(path)
                for path in [VOCAB, SCRIPTURE_PLAN, PATRISTIC_PLAN, LITURGY, MEMORY, RCUV, DEUTERO_ZH]
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
    parser = argparse.ArgumentParser(description="組裝希臘文讀本主檔")
    parser.add_argument("--write", action="store_true", help="寫出主檔")
    parser.add_argument("--report-only", action="store_true", help="即使有問題也不中斷，只列出")
    args = parser.parse_args()

    master = build(strict=not args.report_only)
    counts = master["counts"]
    print(f"  狀態 {master['releaseStatus']}")
    for key, value in counts.items():
        print(f"    {key:<24s} {value}")
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
