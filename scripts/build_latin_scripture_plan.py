#!/usr/bin/env python3
"""The upper volume's fifty complete Vulgate chapters, ordered by difficulty.

Twenty-five chapters of the New Testament, then twenty-five of the Old, one per
lesson, each of them entire.  The two halves are ordered separately on purpose:
a reader is not asked to take the Vulgate Old Testament's Hebraic syntax in
lesson three merely because that chapter happens to be short.

Which chapters they are is a curated decision -- the canon has to be covered,
the psalms that the office actually sings have to be there, and the
deuterocanonical books that make this a Catholic reader rather than a Protestant
one have to appear.  What is *computed* is the order, from two things that can
be measured on the frozen text: how much of the chapter's vocabulary the reader
has already been taught, and how long its sentences run.  An unknown-word rate
is the honest proxy for difficulty here, and it is honest only because the
vocabulary it is measured against is the reader's own.

The Vulgate numbers many psalms differently from the Hebrew, so every chapter
whose number shifts carries both numbers and the Chinese side is fetched by the
number its own edition uses, never by the Latin one.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import latin_source_texts as L  # noqa: E402
from latin_lemmatiser import Lemmatiser  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
VOCABULARY = ROOT / "data" / "originalReaders" / "vocabulary" / "latin-2000.json"
OUTPUT = CACHE / "scripture-plan.json"

# (Vulgate book, Vulgate chapter, 思高 book name, Chinese title, note)
# The Chinese book names are the Studium Biblicum ones, because that is the
# edition printed alongside; Protestant names are not mixed in.
NEW_TESTAMENT = [
    ("1JN", 1, "若一", "若望一書 1"),
    ("MRK", 1, "谷", "馬爾谷福音 1"),
    ("MRK", 4, "谷", "馬爾谷福音 4"),
    ("MAT", 6, "瑪", "瑪竇福音 6"),
    ("MAT", 5, "瑪", "瑪竇福音 5"),
    ("JHN", 1, "若", "若望福音 1"),
    ("1CO", 13, "格前", "格林多前書 13"),
    ("LUK", 2, "路", "路加福音 2"),
    ("LUK", 15, "路", "路加福音 15"),
    ("JHN", 15, "若", "若望福音 15"),
    ("PHP", 2, "斐", "斐理伯書 2"),
    ("ACT", 2, "宗", "宗徒大事錄 2"),
    ("JAS", 1, "雅", "雅各伯書 1"),
    ("REV", 21, "默", "默示錄 21"),
    ("ROM", 12, "羅", "羅馬書 12"),
    ("GAL", 5, "迦", "迦拉達書 5"),
    ("1PE", 2, "伯前", "伯多祿前書 2"),
    ("EPH", 2, "弗", "厄弗所書 2"),
    ("LUK", 24, "路", "路加福音 24"),
    ("ROM", 8, "羅", "羅馬書 8"),
    ("HEB", 1, "希", "希伯來書 1"),
    ("JHN", 17, "若", "若望福音 17"),
    ("ACT", 17, "宗", "宗徒大事錄 17"),
    ("1CO", 15, "格前", "格林多前書 15"),
    ("REV", 1, "默", "默示錄 1"),
]

# The Vulgate psalm number is given first because that is what the Latin page
# prints; the Hebrew number follows for anyone holding a Protestant Bible.
OLD_TESTAMENT = [
    ("GEN", 1, "創", "創世紀 1", ""),
    ("GEN", 3, "創", "創世紀 3", ""),
    ("GEN", 22, "創", "創世紀 22", ""),
    ("EXO", 3, "出", "出谷紀 3", ""),
    ("EXO", 20, "出", "出谷紀 20", ""),
    ("DEU", 6, "申", "申命紀 6", ""),
    ("RUT", 1, "盧", "盧德傳 1", ""),
    ("1KI", 19, "列上", "列王紀上 19", ""),
    ("PSA", 22, "詠", "聖詠 22", "希伯來編號 23"),
    ("PSA", 50, "詠", "聖詠 50", "希伯來編號 51"),
    ("PSA", 90, "詠", "聖詠 90", "希伯來編號 91"),
    ("PSA", 129, "詠", "聖詠 129", "希伯來編號 130"),
    ("PRO", 8, "箴", "箴言 8", ""),
    ("JOB", 38, "約", "約伯傳 38", ""),
    ("ISA", 6, "依", "依撒意亞 6", ""),
    ("ISA", 53, "依", "依撒意亞 53", ""),
    ("JER", 31, "耶", "耶肋米亞 31", ""),
    ("EZK", 37, "則", "厄則克耳 37", ""),
    ("DAN", 3, "達", "達尼爾 3", "含次經增補的三青年讚歌"),
    ("JON", 2, "約納", "約納 2", ""),
    ("TOB", 1, "多", "多俾亞傳 1", "次經／第二正典"),
    ("JDT", 13, "友", "友弟德傳 13", "次經／第二正典"),
    ("WIS", 7, "智", "智慧篇 7", "次經／第二正典"),
    ("SIR", 24, "德", "德訓篇 24", "次經／第二正典"),
    ("2MA", 7, "加下", "瑪加伯下 7", "次經／第二正典"),
]


PER_HALF = 25
assert len(NEW_TESTAMENT) == PER_HALF, len(NEW_TESTAMENT)
assert len(OLD_TESTAMENT) == PER_HALF, len(OLD_TESTAMENT)


def score(book: str, chapter: int, chapters, lm: Lemmatiser, taught: set[str]) -> dict:
    verses = chapters.get((book, chapter))
    if not verses:
        raise SystemExit(f"武加大缺 {book} {chapter}")
    tokens: list[str] = []
    lengths: list[int] = []
    for text in verses.values():
        words = [w for w in L.words(text) if lm.is_word(w)]
        tokens.extend(words)
        lengths.append(len(words))
    known = 0
    names = 0
    for word in tokens:
        lemma = lm.lemma(word)
        if lemma and lemma in lm.names:
            names += 1
        elif lemma and L.fold(lemma) in taught:
            known += 1
    total = max(len(tokens), 1)
    # Names are neither known nor unknown: they are looked up in the appendix,
    # so counting them as unknown would make the genealogies look like the
    # hardest Latin in the Bible when they are the easiest.
    coverage = (known + names) / total
    return {
        "verses": len(verses),
        "words": len(tokens),
        "coverage": round(coverage, 4),
        "nameShare": round(names / total, 4),
        "meanVerseWords": round(statistics.mean(lengths), 1) if lengths else 0.0,
        "difficulty": round((1 - coverage) * 100 + statistics.mean(lengths) / 4, 2),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    lm = Lemmatiser()
    taught: set[str] = set()
    if VOCABULARY.exists():
        data = json.loads(VOCABULARY.read_text(encoding="utf-8"))
        taught = {
            L.fold(entry["headword"])
            for entry in data["entries"]
            if entry["volume"] == "上冊"
        }
    if not taught:
        print("[!] 尚無上冊詞表，難度只反映句長")

    chapters = L.vulgate_chapters()

    def build(rows, corpus):
        out = []
        for row in rows:
            book, chapter, zh_book, title = row[0], row[1], row[2], row[3]
            note = row[4] if len(row) > 4 else ""
            out.append({
                "book": book, "chapter": chapter, "corpus": corpus,
                "zhBook": zh_book, "title": title, "note": note,
                **score(book, chapter, chapters, lm, taught),
            })
        out.sort(key=lambda r: r["difficulty"])
        return out

    nt = build(NEW_TESTAMENT, "新約")
    ot = build(OLD_TESTAMENT, "舊約與第二正典")
    plan = nt + ot
    for index, row in enumerate(plan, start=1):
        row["lesson"] = index

    payload = {
        "schemaVersion": "1.0.0",
        "generatedOn": date.today().isoformat(),
        "volume": "上冊",
        "edition": {
            "latin": "Biblia Sacra Vulgata Clementina, eBible.org latVUC transcription",
            "chinese": "思高譯本（思高聖經學會），信望愛站 version ofm",
        },
        "counts": {
            "chapters": len(plan),
            "verses": sum(r["verses"] for r in plan),
            "words": sum(r["words"] for r in plan),
        },
        "chapters": plan,
    }
    print(f"上冊 {len(plan)} 章；{payload['counts']['verses']:,} 節；"
          f"{payload['counts']['words']:,} 詞")
    for row in plan:
        flag = "新" if row["corpus"] == "新約" else "舊"
        print(f"{row['lesson']:>3} {flag} {row['title']:<16s} {row['verses']:>3}節 "
              f"{row['words']:>5}詞  覆蓋 {row['coverage']*100:>5.1f}%  難度 {row['difficulty']:>6.2f}"
              f"  {row['note']}")
    if args.write:
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        print("->", OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
