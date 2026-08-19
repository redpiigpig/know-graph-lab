#!/usr/bin/env python3
"""Build the 25-chapter plan for the 50-lesson New Testament Greek reader.

The approved split is 13 New Testament chapters, 6 LXX canonical chapters, 4
deuterocanonical chapters and 2 pseudepigraphal chapters, laid out in one fixed
easier-to-harder order so that lessons 1-25 each carry exactly one complete
chapter.  Lessons 26-50 carry the 25 patristic/creed/decree readings.

Two text layers are written for every verse, and never collapsed:

* ``sourceText`` -- the frozen edition exactly as printed, including SBLGNT
  apparatus sigla and Swete's editorial brackets;
* ``displayText`` -- the learner-facing row, with apparatus sigla removed.

Removing a siglum is recorded per verse, so a later audit can prove that the
display layer only ever dropped editorial marks and never a Greek word.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import greek_source_texts as sources


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
OUTPUT = CACHE / "scripture-plan.json"

LESSON_COUNT = 50
CHAPTER_COUNT = 25
VOCABULARY_TARGET = 1000
MEMORY_TARGET = 100

# Both frozen editions reproduce apparatus markers inside the printed text —
# MorphGNT attaches them to SBLGNT words, and Swete's database even indexes a
# bare marker as its own "word".  They are editorial, never Greek, and are
# stripped only in the display layer.  Swete's square brackets are *not* listed
# here: they mark restored text in a damaged manuscript and stay visible.
APPARATUS_SIGLA = "⸀⸁⸂⸃⸄⸅⸆⸇⸈⸉⸊⸋⸌⸍"
SIGLA_RE = re.compile(f"[{APPARATUS_SIGLA}]")
GREEK_LETTER_RE = re.compile(r"[Ͱ-Ͽἀ-῿]")

# corpus / osisBook / chapter / difficulty / titleZh / titleGrc / genre / notes
CHAPTERS: list[dict] = [
    {"corpus": "new-testament", "osisBook": "1John", "chapter": 1, "difficulty": 1,
     "titleZh": "約翰一書 1：生命之道、光與認罪", "titleGrc": "Ἰωάννου Αʹ 1",
     "genre": "epistle", "goals": ["掌握關係代名詞鏈與條件句", "追蹤光／暗、真理／謊言的語義對比"]},
    {"corpus": "new-testament", "osisBook": "Mark", "chapter": 1, "difficulty": 1,
     "titleZh": "馬可福音 1：宣告、呼召與醫治", "titleGrc": "Κατὰ Μᾶρκον 1",
     "genre": "narrative", "goals": ["辨認敘事中的歷史現在式與 εὐθύς", "分析分詞與主要動詞的事件鏈"]},
    {"corpus": "new-testament", "osisBook": "Mark", "chapter": 4, "difficulty": 2,
     "titleZh": "馬可福音 4：撒種比喻與平靜風浪", "titleGrc": "Κατὰ Μᾶρκον 4",
     "genre": "parable", "goals": ["辨認比喻中的條件與目的表達", "比較反覆詞彙在解釋段中的功能"]},
    {"corpus": "new-testament", "osisBook": "Matt", "chapter": 6, "difficulty": 2,
     "titleZh": "馬太福音 6：施捨、祈禱、禁食與憂慮", "titleGrc": "Κατὰ Μαθθαῖον 6",
     "genre": "discourse", "goals": ["熟記主禱文全篇", "分辨命令語氣的禁止式與勸勉式"]},
    {"corpus": "new-testament", "osisBook": "Matt", "chapter": 5, "difficulty": 2,
     "titleZh": "馬太福音 5：八福與律法詮釋", "titleGrc": "Κατὰ Μαθθαῖον 5",
     "genre": "discourse", "goals": ["掌握八福的形容詞子句結構", "追蹤「你們聽見…我卻告訴你們」的對句"]},
    {"corpus": "new-testament", "osisBook": "John", "chapter": 1, "difficulty": 2,
     "titleZh": "約翰福音 1：序言、見證與首批門徒", "titleGrc": "Κατὰ Ἰωάννην 1",
     "genre": "narrative", "goals": ["分析 ἦν、ἐγένετο 與 λόγος 的句法角色", "區分序言詩性段落與敘事段落"]},
    {"corpus": "septuagint", "osisBook": "Gen", "chapter": 1, "difficulty": 2,
     "titleZh": "創世記 1 LXX：創造秩序", "titleGrc": "Γένεσις 1",
     "genre": "narrative", "goals": ["觀察七十士譯本的希伯來式句法", "熟悉 καὶ ἐγένετο 的循環結構"]},
    {"corpus": "septuagint", "osisBook": "Gen", "chapter": 22, "difficulty": 2,
     "titleZh": "創世記 22 LXX：亞伯拉罕受試驗", "titleGrc": "Γένεσις 22",
     "genre": "narrative", "goals": ["追蹤敘事對話的稱謂與重複", "辨認不定詞與分詞的時間關係"]},
    {"corpus": "septuagint", "osisBook": "Exod", "chapter": 3, "difficulty": 2,
     "titleZh": "出埃及記 3 LXX：荊棘、呼召與神名", "titleGrc": "Ἔξοδος 3",
     "genre": "narrative", "goals": ["處理 ἐγώ εἰμι ὁ ὤν 的譯名問題", "比較神名譯法與新約引用"]},
    {"corpus": "septuagint", "osisBook": "Ps", "chapter": 22, "difficulty": 2,
     "titleZh": "詩篇 22 LXX（MT 23）：主是牧者", "titleGrc": "Ψαλμὸς ΚΒʹ",
     "genre": "psalm", "mtChapter": 23,
     "goals": ["熟悉 LXX 與 MT 詩篇編號差", "辨認詩體平行句"]},
    {"corpus": "new-testament", "osisBook": "1Cor", "chapter": 13, "difficulty": 2,
     "titleZh": "哥林多前書 13：愛的頌歌", "titleGrc": "Πρὸς Κορινθίους Αʹ 13",
     "genre": "hymn", "goals": ["分析假設語氣條件句", "辨認名詞化形容詞與抽象名詞"]},
    {"corpus": "new-testament", "osisBook": "Phil", "chapter": 2, "difficulty": 3,
     "titleZh": "腓立比書 2：基督頌與共同生活", "titleGrc": "Πρὸς Φιλιππησίους 2",
     "genre": "hymn", "goals": ["拆解基督頌的分詞鏈", "辨認 ἵνα 子句的目的與結果"]},
    {"corpus": "new-testament", "osisBook": "Acts", "chapter": 2, "difficulty": 3,
     "titleZh": "使徒行傳 2：五旬節、彼得講論與群體生活", "titleGrc": "Πράξεις 2",
     "genre": "narrative-speech", "goals": ["追蹤講論中的舊約引文", "分辨敘事與講論的語域差異"]},
    {"corpus": "new-testament", "osisBook": "Jas", "chapter": 1, "difficulty": 3,
     "titleZh": "雅各書 1：試煉、智慧、言語與實踐", "titleGrc": "Ἰακώβου 1",
     "genre": "wisdom-epistle", "goals": ["辨認智慧文學式的鏈接論證", "掌握命令語氣的勸勉功能"]},
    {"corpus": "new-testament", "osisBook": "Rev", "chapter": 21, "difficulty": 3,
     "titleZh": "啟示錄 21：新天、新地與新耶路撒冷", "titleGrc": "Ἀποκάλυψις 21",
     "genre": "apocalyptic", "goals": ["處理啟示錄特有的不合語法搭配", "辨認異象敘事的時態選擇"]},
    {"corpus": "septuagint", "osisBook": "Ps", "chapter": 50, "difficulty": 3,
     "titleZh": "詩篇 50 LXX（MT 51）：憐憫與更新", "titleGrc": "Ψαλμὸς Νʹ",
     "genre": "psalm", "mtChapter": 51,
     "goals": ["辨認悔罪詩的祈求語氣", "熟悉拜占庭日課常用經句"]},
    {"corpus": "septuagint", "osisBook": "Isa", "chapter": 6, "difficulty": 3,
     "titleZh": "以賽亞書 6 LXX：寶座、聖哉與差遣", "titleGrc": "Ἠσαίας 6",
     "genre": "prophetic-vision", "goals": ["比較 LXX 與 MT 的差異句", "辨認三聖頌在禮儀中的位置"]},
    {"corpus": "deuterocanonical", "osisBook": "TobS", "chapter": 1, "difficulty": 3,
     "titleZh": "多俾亞傳 1（西奈抄本 GII）：流亡中的虔敬", "titleGrc": "Τωβείθ 1 (S)",
     "genre": "narrative", "goals": ["辨認第一人稱敘事的時態鏈", "認識多俾亞傳兩種希臘文本傳統"]},
    {"corpus": "deuterocanonical", "osisBook": "Jdt", "chapter": 13, "difficulty": 3,
     "titleZh": "友弟德傳 13：行動、凱旋與祝福", "titleGrc": "Ἰουδείθ 13",
     "genre": "narrative", "goals": ["追蹤緊湊敘事的分詞連鎖", "辨認祝福套語的句型"]},
    {"corpus": "new-testament", "osisBook": "Rom", "chapter": 8, "difficulty": 4,
     "titleZh": "羅馬書 8：聖靈、受苦與盼望", "titleGrc": "Πρὸς Ῥωμαίους 8",
     "genre": "argument", "goals": ["拆解長句的主從結構", "辨認 γάρ／οὖν／ἄρα 的論證推進"]},
    {"corpus": "new-testament", "osisBook": "Heb", "chapter": 1, "difficulty": 4,
     "titleZh": "希伯來書 1：子與天使", "titleGrc": "Πρὸς Ἑβραίους 1",
     "genre": "argument", "goals": ["辨認修辭性的文言句式", "追蹤連續舊約引文的來源"]},
    {"corpus": "deuterocanonical", "osisBook": "Sir", "chapter": 24, "difficulty": 4,
     "titleZh": "德訓篇 24：智慧、創造與妥拉", "titleGrc": "Σοφία Σειράχ 24",
     "genre": "wisdom-poetry", "goals": ["辨認智慧自述體的第一人稱詩句", "比較與約翰福音序言的關係"]},
    {"corpus": "deuterocanonical", "osisBook": "Wis", "chapter": 7, "difficulty": 5,
     "titleZh": "智慧篇 7：智慧的本性與祈求", "titleGrc": "Σοφία Σαλωμῶνος 7",
     "genre": "wisdom-poetry", "goals": ["處理希臘化哲學語彙", "辨認長串形容詞列舉句"]},
    {"corpus": "pseudepigrapha", "osisBook": "PssSol", "chapter": 17, "difficulty": 5,
     "titleZh": "所羅門詩篇 17：大衛之子與彌賽亞盼望", "titleGrc": "Ψαλμοὶ Σαλωμῶντος 17",
     "genre": "psalm", "goals": ["辨認第二聖殿時期的彌賽亞語彙", "比較與新約君王稱號的用法"]},
    {"corpus": "pseudepigrapha", "osisBook": "1En", "chapter": 1, "difficulty": 5,
     "titleZh": "以諾一書 1（希臘文）：神顯審判之言", "titleGrc": "Ἑνώχ 1",
     "genre": "apocalyptic-oracle", "goals": ["核對猶大書 14–15 的直接引用", "處理殘卷方括號補字"]},
]

CORPUS_LABELS = {
    "new-testament": "新約",
    "septuagint": "七十士譯本（正典）",
    "deuterocanonical": "次經",
    "pseudepigrapha": "偽經",
}

TRANSLATION_POLICY = {
    "new-testament": "cuv2010",
    "septuagint": "cuv2010",
    "deuterocanonical": "hkskh-deuterocanon",
    "pseudepigrapha": "self-translated",
}


def strip_sigla(text: str) -> str:
    return re.sub(r"\s{2,}", " ", SIGLA_RE.sub("", text)).strip()


def build_chapter(spec: dict, ordinal: int) -> dict:
    verses = sources.load_chapter(spec["osisBook"], spec["chapter"])
    metadata = sources.source_metadata(spec["osisBook"])
    verse_rows = []
    absent_verses = []
    sigla_verses = 0
    sigla_tokens = 0
    for verse in verses:
        # Sirach 24:18 and 24:24 are Greek II expansions that Swete's primary
        # text does not print, so the versification allocates them a number and
        # no words.  Emitting an empty verse would ship a blank line dressed as
        # Scripture; the gap is recorded on the chapter instead.
        if not "".join(token.text for token in verse.tokens).strip():
            absent_verses.append(
                {
                    "verse": verse.verse,
                    "ref": verse.ref,
                    "note": "本節在此版本無正文（Swete 未收的增補節），故不列入讀文。",
                }
            )
            continue
        display = strip_sigla(verse.text)
        had_sigla = display != verse.text
        sigla_verses += 1 if had_sigla else 0
        greek_tokens = [token for token in verse.tokens if GREEK_LETTER_RE.search(token.text)]
        sigla_tokens += len(verse.tokens) - len(greek_tokens)
        row = {
            "osisBook": verse.osis_book,
            "chapter": verse.chapter,
            "verse": verse.verse,
            "ref": verse.ref,
            "wordCount": len(greek_tokens),
            "sourceText": verse.text,
            "displayText": display,
            "apparatusSiglaRemoved": had_sigla,
        }
        if greek_tokens and greek_tokens[0].lemma:
            row["lemmas"] = [token.lemma for token in greek_tokens]
        if len(display.split()) != len(greek_tokens):
            raise ValueError(
                f"{verse.ref}: 顯示層 {len(display.split())} 詞 ≠ 希臘文詞 "
                f"{len(greek_tokens)}，剝除校勘記號時掉字"
            )
        verse_rows.append(row)

    source_words = sum(row["wordCount"] for row in verse_rows)

    chapter = {
        "ordinal": ordinal,
        "lesson": ordinal,
        "corpus": spec["corpus"],
        "corpusLabel": CORPUS_LABELS[spec["corpus"]],
        "osisBook": spec["osisBook"],
        "chapter": spec["chapter"],
        "ref": f"{spec['osisBook']}.{spec['chapter']}",
        "titleZh": spec["titleZh"],
        "titleGrc": spec["titleGrc"],
        "genre": spec["genre"],
        "difficulty": spec["difficulty"],
        "difficultyRank": ordinal,
        "learningGoals": spec["goals"],
        "translationPlan": TRANSLATION_POLICY[spec["corpus"]],
        "verseCount": len(verse_rows),
        "wordCount": source_words,
        "absentVerses": absent_verses,
        "verseWithSiglaCount": sigla_verses,
        "editorialSiglaTokenCount": sigla_tokens,
        "memoryVerseNumbers": [],
        "verses": verse_rows,
        **metadata,
    }
    if "mtChapter" in spec:
        chapter["mtChapter"] = spec["mtChapter"]
        chapter["numberingNote"] = (
            f"七十士譯本第 {spec['chapter']} 篇＝馬所拉本第 {spec['mtChapter']} 篇；"
            "中文對照走同一份編號對照表。"
        )
    return chapter


def build_plan() -> dict:
    if len(CHAPTERS) != CHAPTER_COUNT:
        raise ValueError(f"章目應為 {CHAPTER_COUNT} 章，實得 {len(CHAPTERS)}")
    refs = [f"{spec['osisBook']}.{spec['chapter']}" for spec in CHAPTERS]
    if len(set(refs)) != len(refs):
        raise ValueError("章目有重複")

    chapters = [build_chapter(spec, index) for index, spec in enumerate(CHAPTERS, start=1)]
    corpus_counts: dict[str, int] = {}
    for chapter in chapters:
        corpus_counts[chapter["corpus"]] = corpus_counts.get(chapter["corpus"], 0) + 1
    expected = {"new-testament": 13, "septuagint": 6, "deuterocanonical": 4, "pseudepigrapha": 2}
    if corpus_counts != expected:
        raise ValueError(f"語料配額不符：應為 {expected}，實得 {corpus_counts}")

    return {
        "schemaVersion": "1.0.0",
        "generatedOn": date.today().isoformat(),
        "status": "chapters-frozen-memory-selection-pending",
        "language": "New Testament Greek",
        "languageCode": "grc",
        "curriculum": {
            "lessonCount": LESSON_COUNT,
            "textbook": "William D. Mounce, Basics of Biblical Greek Grammar",
            "vocabularyTarget": VOCABULARY_TARGET,
            "fullChapterCount": CHAPTER_COUNT,
            "memoryVerseTarget": MEMORY_TARGET,
            "memoryVerseCount": 0,
            "memoryVersesPerLesson": 2,
            "chapterAllocation": (
                "第 1–25 課各配一章完整經文，依核可的由易而難次序；"
                "第 26–50 課配 25 篇教父文獻、信經與教令。"
            ),
            "corpusAllocation": expected,
        },
        "selectionPolicy": {
            "fixedChapterRefs": refs,
            "chapterOrder": "使用者核可的由易而難次序，不得自動重排。",
            "memorySelection": "先鎖定課次詞彙，再依重疊度與完整句評分，最後人工複核。",
        },
        "sources": {
            "newTestament": {
                "edition": sources.SBLGNT_EDITION,
                "versionCode": sources.SBLGNT_VERSION,
                "sourceUrl": sources.SBLGNT_URL,
                "license": "SBLGNT EULA（私人授權）；MorphGNT 標註 CC BY-SA 3.0",
            },
            "septuagintAndBeyond": {
                "edition": sources.SWETE_EDITION,
                "versionCode": sources.SWETE_VERSION,
                "sourceUrl": sources.SWETE_URL,
                "license": "Swete 正文公有領域；數位詞庫 GPL-3.0，僅作本機建置輸入",
                "note": (
                    "同一版本涵蓋七十士譯本、全部次經、所羅門詩篇與希臘文以諾一書；"
                    "不採 Rahlfs（CCAT 數位版需簽署使用聲明，且無希臘文以諾書）。"
                ),
            },
        },
        "textLayers": {
            "sourceText": "凍結版本原樣，含 SBLGNT 校勘記號與 Swete 方括號補字",
            "displayText": "僅剝除 SBLGNT 校勘記號的學習者版；Swete 方括號一律保留",
        },
        "summary": {
            "chapterCount": len(chapters),
            "verseCount": sum(chapter["verseCount"] for chapter in chapters),
            "wordCount": sum(chapter["wordCount"] for chapter in chapters),
            "corpusCounts": corpus_counts,
            "difficultyCounts": {
                str(level): sum(1 for c in chapters if c["difficulty"] == level)
                for level in sorted({c["difficulty"] for c in chapters})
            },
        },
        "chapters": chapters,
        "memoryLessons": [],
        "memoryVerses": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="建立希臘文讀本 25 章計畫")
    parser.add_argument("--write", action="store_true", help="寫出 scripture-plan.json")
    args = parser.parse_args()

    plan = build_plan()
    summary = plan["summary"]
    for chapter in plan["chapters"]:
        print(
            f"  {chapter['ordinal']:02d}  {chapter['corpusLabel']:<12s}"
            f"{chapter['ref']:<12s} {chapter['verseCount']:>3d} 節 "
            f"{chapter['wordCount']:>4d} 詞  難度{chapter['difficulty']}  {chapter['titleZh']}"
        )
    print(
        f"  合計 {summary['chapterCount']} 章、{summary['verseCount']} 節、"
        f"{summary['wordCount']} 詞；語料分配 {summary['corpusCounts']}"
    )

    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已寫出 {OUTPUT}")
    else:
        print("（未寫檔；加 --write 才會輸出）")


if __name__ == "__main__":
    main()
