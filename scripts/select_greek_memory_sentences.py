#!/usr/bin/env python3
"""挑選下冊的一百個記憶句，每課兩句。

上冊的記憶單元是經節，取自那一課所讀的經卷；下冊沒有節號，讀的是教父文獻與教會
文獻，所以記憶單元改取**句子**——由讀文的段落按希臘文標點切開，每句都必須自己站
得住，不是從長句中截下的半截。

與上冊同一條半冊規則：第 1–25 課取教父文獻的句子，第 26–50 課取教會文獻與禮儀文
本的句子，跟那一課所讀的文獻同一批語料。這是本檔自行定下的設計，尚未經作者確認，
交接文件已註明。

比對先把印刷字形查通用希臘文詞位表還原成詞位，查不到才退回去重音折疊的字形。只比
字形是不夠的：ἀναμιμνήσκωμεν 與詞表裡的 ἀναμιμνήσκω 一個字母都對不上，第一版只用
字形，一句平均命中一兩詞，有八課湊不滿兩句。每個候選的分數與落選理由都寫出來，
人工複核才有東西可看。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from verify_greek_vocab_lexicon import fold


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
VOCAB = ROOT / "data" / "originalReaders" / "vocabulary" / "greek-2000.json"
PLAN = CACHE / "patristic-plan.json"
KOINE_LEXICON = CACHE / "koine-lexicon.json"
OUTPUT = CACHE / "memory-sentences.json"
CANDIDATES_OUT = CACHE / "memory-sentence-candidates.json"

VOLUME = 2
LESSON_COUNT = 50
PER_LESSON = 2
PATRISTIC_LESSON_LAST = 25

MIN_WORDS = 4
MAX_WORDS = 20

GREEK_RE = re.compile(r"[Ͱ-Ͽἀ-῿]")
NUMERAL_RE = re.compile(r"\d")
BRACKET_RE = re.compile(r"[\[\]]")
# Greek sentence punctuation: the full stop, the raised dot that does duty for
# both colon and semicolon, and the semicolon that is the question mark.
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.·;;!])\s+")
TRAILING_RE = re.compile(r"^[\s·,;:—–\-]+|[\s]+$")

PATRISTIC_CATEGORIES = {"apostolic-father", "greek-father"}

# The same reasoning as the verse selector: divine names carry no narrative
# weight, so they are not counted towards the proper-name penalty.
DIVINE_FOLDED = {
    fold(name)
    for name in (
        "θεός", "θεοῦ", "θεῷ", "θεόν", "κύριος", "κυρίου", "κυρίῳ", "κύριον", "κύριε",
        "χριστός", "χριστοῦ", "χριστῷ", "χριστόν", "ἰησοῦς", "ἰησοῦ", "ἰησοῦν",
        "πνεῦμα", "πνεύματος", "πνεύματι", "πατήρ", "πατρός", "πατρί", "πατέρα",
        "υἱός", "υἱοῦ", "υἱῷ", "υἱόν",
    )
}

# A sentence that opens with a connective alone, or that is only a rubric or a
# reference formula, is not memorable however well it scores.
RUBRIC_MARKERS = ("ΤΟ ΑΚΟΥΤΕ", "Ἦχος", "ᾨδὴ", "Καταβασία", "Ὁ Χορὸς", "Ὁ Ἱερεὺς")


def load_vocabulary() -> dict[int, list[dict]]:
    payload = json.loads(VOCAB.read_text(encoding="utf-8"))
    by_lesson: dict[int, list[dict]] = {}
    for entry in payload["entries"]:
        if entry.get("volume") != VOLUME:
            continue
        by_lesson.setdefault(entry["lesson"], []).append(entry)
    if sorted(by_lesson) != list(range(1, LESSON_COUNT + 1)):
        raise ValueError(f"下冊應有 {LESSON_COUNT} 課詞彙，實得 {len(by_lesson)} 課")
    return by_lesson


def lesson_half(lesson: int) -> str:
    return "patristic" if lesson <= PATRISTIC_LESSON_LAST else "church-document"


def reading_half(reading: dict) -> str:
    return "patristic" if reading["category"] in PATRISTIC_CATEGORIES else "church-document"


def greek_words(text: str) -> list[str]:
    return [word for word in text.split() if GREEK_RE.search(word)]


_LEXICON: dict | None = None


def _lexicon() -> dict:
    """The Koine lemma index built from the tagged New Testament and Septuagint.

    Matching printed forms against dictionary headwords letter by letter finds
    almost nothing — ἀναμιμνήσκωμεν is not ἀναμιμνήσκω — so a first pass on the
    surface alone came back with one or two hits per sentence and left eight
    lessons unable to fill their two slots.  The same lexicon that resolved the
    vocabulary list resolves the sentence's words here.
    """
    global _LEXICON
    if _LEXICON is None:
        if not KOINE_LEXICON.exists():
            raise FileNotFoundError(
                f"缺少通用希臘文詞位表：{KOINE_LEXICON}；先跑 build_greek_koine_lexicon.py --write"
            )
        _LEXICON = json.loads(KOINE_LEXICON.read_text(encoding="utf-8"))
    return _LEXICON


def word_keys(word: str) -> set[str]:
    """The folded surface plus every Koine lemma that form can belong to."""
    bare = word.strip(".,·;:!?—–()«»’'\"")
    folded = fold(bare)
    keys = {folded} if folded else set()
    lexicon = _lexicon()
    lemmas = lexicon["exactForms"].get(bare) or lexicon["forms"].get(folded) or []
    for lemma in lemmas:
        candidate = fold(lemma)
        if candidate:
            keys.add(candidate)
    return keys


def sentences_of(text: str) -> list[str]:
    parts = []
    for part in SENTENCE_SPLIT_RE.split(unicodedata.normalize("NFC", text)):
        part = TRAILING_RE.sub("", part).strip()
        if part:
            parts.append(part)
    return parts


def sentence_pool() -> list[dict]:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    pool: list[dict] = []
    for reading in plan["readings"]:
        half = reading_half(reading)
        for segment in reading["segments"]:
            for index, sentence in enumerate(sentences_of(segment["displayText"]), start=1):
                words = greek_words(sentence)
                if not (MIN_WORDS <= len(words) <= MAX_WORDS):
                    continue
                if NUMERAL_RE.search(sentence) or BRACKET_RE.search(sentence):
                    continue
                if any(marker in sentence for marker in RUBRIC_MARKERS):
                    continue
                keys: set[str] = set()
                for word in words:
                    keys |= word_keys(word)
                pool.append(
                    {
                        "ref": f"{reading['ordinal']}:{segment['ref']}#{index}",
                        "readingOrdinal": reading["ordinal"],
                        "readingLesson": reading["lesson"],
                        "readingTitleZh": reading["titleZh"],
                        "category": reading["category"],
                        "half": half,
                        "segmentRef": segment["ref"],
                        "sentenceIndex": index,
                        "wordCount": len(words),
                        "text": sentence,
                        "keys": keys,
                        "properNames": sum(
                            1
                            for position, word in enumerate(words)
                            if position
                            and word[:1].isupper()
                            and not words[position - 1].endswith(("·", ".", ";", ";", "!"))
                            and fold(word.strip(".,·;:!?—–()«»’")) not in DIVINE_FOLDED
                        ),
                    }
                )
    return pool


def score(candidate: dict, lesson_keys: set[str], known_keys: set[str]) -> dict:
    matched = candidate["keys"] & lesson_keys
    known = candidate["keys"] & known_keys
    coverage = len(known) / max(len(candidate["keys"]), 1)
    length_fit = 1.0 - abs(candidate["wordCount"] - 11) / 14
    value = len(matched) * 3.0 + coverage * 4.0 + length_fit
    flags: list[str] = []
    if candidate["wordCount"] <= 5:
        flags.append("very_short")
        value -= 0.5
    names = candidate["properNames"]
    if names:
        flags.append("proper_names")
        value -= 0.7 * min(names, 3)
    # A sentence taken from the lesson's own reading is worth a little more:
    # the learner meets it twice in the same week.
    if candidate["readingLesson"] == candidate.get("_lesson"):
        flags.append("from_this_lesson")
        value += 1.0
    return {
        "matchCount": len(matched),
        "matchedTerms": sorted(matched),
        "knownCoverage": round(coverage, 3),
        "lengthFit": round(length_fit, 3),
        "memorabilityFlags": flags,
        "score": round(value, 3),
    }


def select(by_lesson: dict[int, list[dict]], pool: list[dict]) -> tuple[list[dict], list[dict]]:
    chosen: list[dict] = []
    used_refs: set[str] = set()
    used_texts: set[str] = set()
    review_rows: list[dict] = []

    lesson_key_sets: dict[int, set[str]] = {}
    for lesson in range(1, LESSON_COUNT + 1):
        keys: set[str] = set()
        for entry in by_lesson.get(lesson, []):
            keys |= {fold(entry["headword"]), fold(entry["lemma"])}
        keys.discard("")
        lesson_key_sets[lesson] = keys

    known_keys: set[str] = set()
    for lesson in range(1, LESSON_COUNT + 1):
        known_keys |= lesson_key_sets[lesson]
        lesson_keys = lesson_key_sets[lesson]
        half = lesson_half(lesson)
        scored = []
        for candidate in pool:
            if candidate["ref"] in used_refs or candidate["text"] in used_texts:
                continue
            if candidate["half"] != half:
                continue
            if not candidate["keys"] & lesson_keys:
                continue
            candidate["_lesson"] = lesson
            scored.append((score(candidate, lesson_keys, known_keys), candidate))
        scored.sort(key=lambda pair: pair[0]["score"], reverse=True)
        review_rows.append(
            {
                "lesson": lesson,
                "half": half,
                "candidatesConsidered": len(scored),
                "top": [
                    {"ref": c["ref"], "titleZh": c["readingTitleZh"], **s} for s, c in scored[:8]
                ],
            }
        )

        taken = 0
        for sentence_score, candidate in scored:
            if taken >= PER_LESSON:
                break
            if candidate["text"] in used_texts:
                continue
            used_refs.add(candidate["ref"])
            used_texts.add(candidate["text"])
            taken += 1
            chosen.append(
                {
                    "lesson": lesson,
                    "slot": taken,
                    "half": half,
                    "ref": candidate["ref"],
                    "readingOrdinal": candidate["readingOrdinal"],
                    "readingLesson": candidate["readingLesson"],
                    "readingTitleZh": candidate["readingTitleZh"],
                    "category": candidate["category"],
                    "segmentRef": candidate["segmentRef"],
                    "matchMethod": "koine-lemma",
                    "wordCount": candidate["wordCount"],
                    "text": candidate["text"],
                    "translationZh": "",
                    "reviewStatus": "pending_human_review",
                    **sentence_score,
                }
            )
    return chosen, review_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="挑選希臘文讀本下冊的 100 個記憶句")
    parser.add_argument("--write", action="store_true", help="寫出 memory-sentences.json")
    args = parser.parse_args()

    by_lesson = load_vocabulary()
    pool = sentence_pool()
    print(f"候選句池 {len(pool)} 句")
    chosen, review = select(by_lesson, pool)

    per_lesson = Counter(item["lesson"] for item in chosen)
    short = [lesson for lesson in range(1, LESSON_COUNT + 1) if per_lesson[lesson] < PER_LESSON]
    category_counts = Counter(item["category"] for item in chosen)
    same_lesson = sum(1 for item in chosen if item["readingLesson"] == item["lesson"])

    for item in chosen[:6]:
        print(
            f"  第 {item['lesson']:>2d} 課 slot{item['slot']}  {item['ref']:<18s}"
            f" 命中 {item['matchCount']} 詞  {item['text'][:56]}"
        )
    print(f"  ...共 {len(chosen)} 句")
    print(f"  分類分佈 {dict(category_counts)}")
    print(f"  取自本課讀文者 {same_lesson} 句")
    if short:
        print(f"  ⚠ 湊不滿兩句的課次：{short}")

    payload = {
        "schemaVersion": "1.0.0",
        "language": "Koine Greek",
        "languageCode": "grc",
        "volume": VOLUME,
        "volumeTitle": "下冊《教父文獻與希臘教會文獻》",
        "corpusByHalf": {
            "1-25": "patristic",
            "26-50": "church-document",
        },
        "designNote": (
            "下冊的記憶單元是句子而非經節：教父與教會文獻沒有節號，"
            "改以希臘文標點切句，每句須自成一句。半冊規則與上冊一致，"
            "但「兩句該與該課讀文有何關係」尚未經作者裁定，暫定同半冊即可、"
            "取自本課讀文者加分。"
        ),
        "target": LESSON_COUNT * PER_LESSON,
        "selected": len(chosen),
        "perLesson": PER_LESSON,
        "matchMethod": "koine-lemma：字形先查通用希臘文詞位表還原詞位，查不到才用折疊字形",
        "categoryCounts": dict(category_counts),
        "fromOwnReading": same_lesson,
        "lessonsShort": short,
        "reviewNote": "全部標 pending_human_review；依約定須人工複核可記憶性後才可定案。",
        "sentences": chosen,
    }

    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已寫出 {OUTPUT}")
        CANDIDATES_OUT.write_text(
            json.dumps({"schemaVersion": "1.0.0", "lessons": review}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"已寫出 {CANDIDATES_OUT}")
    else:
        print("（未寫檔；加 --write 才會輸出）")


if __name__ == "__main__":
    main()
