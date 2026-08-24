#!/usr/bin/env python3
"""Two memory units per lesson: a hundred for each volume.

A memory unit has to satisfy two things at once that pull against each other.
It must be worth memorising -- a whole thought, not a fragment, and preferably a
line the reader will meet again in the office or the Mass. And it must be
readable *now*, using the words this lesson and the lessons before it have
taught, or the reader memorises a sound rather than a sentence.

So candidates are scored on cumulative coverage against the running vocabulary,
and every unit is assigned to the earliest lesson whose cumulative words cover
it. That ordering is what makes the reader gradable: lesson three's units use
lesson three's Latin.

Four kinds of verse are rejected outright, and each of them was found in the
Vulgate while writing this. Genealogies and censuses are lists, not sentences,
and would teach nothing but the ablative of number. Fragments that end mid-
clause -- Jerome's verse divisions cut across sentences constantly -- are not
memorable units. Verses that repeat an earlier choice almost word for word
crowd out real ones. And a verse whose Chinese is missing cannot be reviewed,
so it cannot be chosen.

The upper volume draws from the fifty printed chapters, so every unit already
has its Studium Biblicum parallel; the lower volume draws from the fifty church
readings, where the Latin is in hand and the Chinese status is recorded per
reading rather than assumed.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import latin_source_texts as L  # noqa: E402
from latin_lemmatiser import Lemmatiser  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
VOCABULARY = ROOT / "data" / "originalReaders" / "vocabulary" / "latin-2000.json"
SCRIPTURE = CACHE / "scripture-plan.json"
SIGAO = CACHE / "sigao-zh.json"
CHURCH = CACHE / "church-plan.json"
OUTPUT = CACHE / "memory-units.json"
REVIEW = CACHE / "memory-selection-review.md"

PER_LESSON = 2
LESSONS = 50

UNKNOWN_ALLOWANCE = 0.15

# Lesson one knows twenty words.  Whatever it memorises is going to be short
# -- Deus caritas est, Verbum caro factum est -- and a five-word floor rules
# every one of those out.
MIN_WORDS = 3
MAX_WORDS = 26

# A verse that is mostly a name and a number is a census line, whatever book it
# sits in; the genealogies are the clearest case but not the only one.
NUMERAL_WORDS = {
    "unus", "duo", "tres", "quattuor", "quinque", "sex", "septem", "octo",
    "novem", "decem", "viginti", "triginta", "quadraginta", "quinquaginta",
    "sexaginta", "septuaginta", "octoginta", "nonaginta", "centum", "mille",
    "annus", "filius", "genuit",
}

# Jerome's verse divisions cut across sentences, so a candidate has to look like
# a whole one: begin with a capital and end on a stop.
OPENS = re.compile(r"^[\[\(]?[A-ZĀĒĪŌŪ]")
CLOSES = re.compile(r"[.!?][\]\)]?$")

# The repository's church documents carry their citation apparatus inline --
# "LEO XIII, Litterae Officio sanctissimo, 22 dec." parses as a sentence and
# reads as gibberish.  Digits, runs of capitals and bracketed numbers mark it.
APPARATUS_SHAPE = re.compile(r"\d|[A-Z]{3,}|\[|\]")


def sentence_shape(text: str) -> bool:
    stripped = text.strip()
    return bool(OPENS.match(stripped) and CLOSES.search(stripped))


def bag(text: str, lm: Lemmatiser) -> list[str]:
    out = []
    for word in L.words(text):
        if not lm.is_word(word):
            continue
        lemma = lm.lemma(word)
        out.append(L.fold(lemma) if lemma else L.fold(word))
    return out


def census_like(lemmas: list[str], lm: Lemmatiser) -> bool:
    if not lemmas:
        return True
    numerals = sum(1 for l in lemmas if l in NUMERAL_WORDS)
    names = sum(1 for l in lemmas if l in lm.names)
    return (numerals + names) / len(lemmas) > 0.45


def similar(candidate: list[str], chosen: list[list[str]]) -> bool:
    """Reject a near-duplicate of something already chosen."""
    current = set(candidate)
    for other in chosen:
        overlap = len(current & set(other))
        if overlap >= 0.7 * min(len(current), len(other)) and overlap >= 4:
            return True
    return False


def cumulative_vocabulary(entries: list[dict], volume: str) -> list[set[str]]:
    """Words available at each lesson, accumulated from lesson one.

    The second volume starts from the first volume's thousand, not from zero.
    A reader opening 下冊 has finished 上冊; counting et, sum and qui as unknown
    there made almost every patristic sentence unreadable and cut the lower
    volume's memory units to two.
    """
    per_lesson: dict[int, set[str]] = {}
    for entry in entries:
        if entry["volume"] != volume:
            continue
        per_lesson.setdefault(entry["lesson"], set()).add(L.fold(entry["headword"]))
    running: set[str] = set()
    if volume == "下冊":
        running |= {L.fold(e["headword"]) for e in entries if e["volume"] == "上冊"}
    out = []
    for lesson in range(1, LESSONS + 1):
        running |= per_lesson.get(lesson, set())
        out.append(set(running))
    return out


def choose(candidates: list[dict], cumulative: list[set[str]], lm: Lemmatiser,
           max_words: int = MAX_WORDS, require_chinese: bool = True) -> list[dict]:
    """Assign two units to each lesson, earliest lesson that can read them."""
    for row in candidates:
        row["lemmas"] = bag(row["text"], lm)
    scored = []
    for row in candidates:
        lemmas = row["lemmas"]
        if not (MIN_WORDS <= len(lemmas) <= max_words):
            continue
        if not sentence_shape(row["text"]):
            continue
        if census_like(lemmas, lm):
            continue
        if require_chinese and not row.get("zh"):
            continue
        if APPARATUS_SHAPE.search(row["text"]):
            continue
        # A sentence the lemmatiser cannot mostly read is not Latin prose: it is
        # a reference, a heading, or a fragment of another language.
        resolved = sum(1 for w in L.words(row["text"]) if lm.lemma(w))
        if resolved < 0.8 * max(len(L.words(row["text"])), 1):
            continue
        # The earliest lesson that can nearly read it.  Demanding every lemma
        # be taught is a threshold no verse clears: the Vulgate has some eight
        # thousand lemmas and this reader teaches two thousand, so requiring
        # total coverage produced forty-two units out of a hundred.  One or two
        # words a reader must look up is what a memory verse is for.
        needed = [l for l in lemmas if l not in lm.names]
        budget = max(1, round(len(needed) * UNKNOWN_ALLOWANCE))
        earliest = None
        for index, available in enumerate(cumulative, start=1):
            if sum(1 for l in needed if l not in available) <= budget:
                earliest = index
                break
        if earliest is None:
            continue
        coverage = sum(1 for l in needed if l in cumulative[-1]) / max(len(needed), 1)
        scored.append({**row, "lesson": earliest, "coverage": round(coverage, 3)})

    # Readability runs one way only: a unit readable at lesson three is still
    # readable at lesson thirty, but not the reverse.  So each lesson draws from
    # every pool up to and including its own, preferring the most demanding
    # candidates it can now handle.  Filling each lesson only from its own pool
    # front-loads the whole book -- the first attempt put every good verse in the
    # first twenty-four lessons and left the rest empty.
    available: dict[int, list[dict]] = {}
    for row in sorted(scored, key=lambda r: (-r["lesson"], -len(r["lemmas"]))):
        available.setdefault(row["lesson"], []).append(row)

    chosen: list[dict] = []
    taken: list[list[str]] = []
    for lesson in range(1, LESSONS + 1):
        picked = 0
        for earliest in range(lesson, 0, -1):
            pool = available.get(earliest, [])
            while pool and picked < PER_LESSON:
                row = pool.pop(0)
                if similar(row["lemmas"], taken):
                    continue
                taken.append(row["lemmas"])
                record = {k: v for k, v in row.items() if k != "lemmas"}
                record["readableFrom"] = earliest
                record["lesson"] = lesson
                chosen.append(record)
                picked += 1
            if picked == PER_LESSON:
                break
    return chosen


def scripture_candidates() -> list[dict]:
    plan = json.loads(SCRIPTURE.read_text(encoding="utf-8"))
    chinese = json.loads(SIGAO.read_text(encoding="utf-8"))
    zh_by_ref = {}
    for chapter in chinese["chapters"]:
        for verse in chapter["verses"]:
            zh_by_ref[(chapter["book"], chapter["latinChapter"], verse["verse"])] = verse["text"]
    chapters = L.vulgate_chapters()
    rows = []
    for row in plan["chapters"]:
        verses = chapters[(row["book"], row["chapter"])]
        for number, text in verses.items():
            rows.append({
                "ref": f"{row['book']} {row['chapter']}:{number}",
                "title": row["title"], "text": text,
                "zh": zh_by_ref.get((row["book"], row["chapter"], number), ""),
                "fromLesson": row["lesson"],
            })
    return rows


def church_candidates() -> list[dict]:
    plan = json.loads(CHURCH.read_text(encoding="utf-8"))
    rows = []
    for reading in plan["readings"]:
        # Only the Latin Library texts.  The repository's curial documents keep
        # their footnote citations inline -- "Dei genetricis, Hom." and "Quam
        # Apostoli sententiam S." both parse as sentences -- so splitting them
        # yields references rather than Latin worth memorising.  They can be
        # readmitted once the apparatus is stripped, not before.
        if reading["sourceKind"] != "file":
            continue
        path = ROOT / reading["sourcePath"]
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            sentence = re.sub(r"\s+", " ", sentence).strip()
            if not sentence:
                continue
            rows.append({
                "ref": reading["latinTitle"], "title": reading["title"],
                "text": sentence,
                # The lower volume's Chinese is per reading, not per sentence, so
                # a sentence is offered for selection only when its reading has a
                # translation to check it against.
                "zh": "",
                "chineseParallel": reading["chineseParallel"],
                "fromLesson": reading["lesson"],
            })
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    lm = Lemmatiser()
    vocab = json.loads(VOCABULARY.read_text(encoding="utf-8"))["entries"]

    upper = choose(scripture_candidates(), cumulative_vocabulary(vocab, "上冊"), lm)
    # The lower volume's sentences run far longer than a Vulgate verse, and only
    # twenty-seven of its fifty readings have a Chinese parallel yet.  Selecting
    # only from those twenty-seven would pick the memory units for the whole
    # volume out of the modern curial half; the Chinese status travels with each
    # unit instead, to be filled when the reading is translated.
    lower = choose(church_candidates(), cumulative_vocabulary(vocab, "下冊"), lm,
                   max_words=38, require_chinese=False)

    payload = {
        "schemaVersion": "1.0.0",
        "generatedOn": date.today().isoformat(),
        "perLesson": PER_LESSON,
        "counts": {"上冊": len(upper), "下冊": len(lower)},
        "上冊": upper,
        "下冊": lower,
    }
    for volume, rows in (("上冊", upper), ("下冊", lower)):
        sizes = Counter(r["lesson"] for r in rows)
        short = [l for l in range(1, LESSONS + 1) if sizes.get(l, 0) < PER_LESSON]
        print(f"{volume}：{len(rows)}/{LESSONS * PER_LESSON} 句"
              f"{'；不足的課 ' + str(short[:8]) if short else ''}")
    print()
    for row in upper[:6]:
        print(f"  上 L{row['lesson']:>2} {row['ref']:<12s} {row['text'][:60]}")
    for row in lower[:4]:
        print(f"  下 L{row['lesson']:>2} {row['title'][:10]:<12s} {row['text'][:60]}")

    if args.write:
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        lines = ["# 記憶單元選句待覆核", "",
                 "每課兩句，指派到「累計詞彙足以讀懂它」的最早一課。",
                 "以下每句都需人工確認：是否成句、是否值得背、中文是否對得上。", ""]
        for volume in ("上冊", "下冊"):
            lines.append(f"## {volume}")
            lines.append("")
            for row in payload[volume]:
                borrowed = f"（借自第 {row['borrowedFrom']} 課池）" if row.get("borrowedFrom") else ""
                lines.append(f"- **第 {row['lesson']} 課**{borrowed} `{row['ref']}` — {row['text']}")
                if row.get("zh") and row["zh"] != "reading-has-chinese":
                    lines.append(f"  - 思高：{row['zh']}")
            lines.append("")
        REVIEW.write_text("\n".join(lines), encoding="utf-8")
        print("->", OUTPUT.relative_to(ROOT))
        print("->", REVIEW.relative_to(ROOT))


if __name__ == "__main__":
    main()
