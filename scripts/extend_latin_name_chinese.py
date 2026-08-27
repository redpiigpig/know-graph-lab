#!/usr/bin/env python3
"""Name the rest of the Vulgate's proper names, by printing more of the Chinese.

The appendix's Chinese comes from the Studium Biblicum edition's own underlining:
a Latin name's Chinese is whichever underlined name shares most of its verses.
That is evidence rather than recall, and it has one hard limit — it can only
reach names that occur in a chapter whose Chinese the reader has fetched. Fifty
chapters covered 53 of 585 names.

So this fetches more chapters. Not all of them: for each unnamed Latin name the
chapters where it actually occurs are known, and a greedy cover picks the
smallest set of chapters that reaches the most names. Saul needs one chapter of
Samuel, not the whole book.

Nothing here relaxes the alignment guards. A name still has to follow its
candidate through most of its verses, and the candidate still has to be rare
enough elsewhere to mean something. Names the enlarged corpus still cannot
settle keep an empty cell, and that is the correct state for them.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import latin_source_texts as L  # noqa: E402
import export_reader_sigao as sigao  # noqa: E402
from latin_lemmatiser import Lemmatiser  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
APPENDICES = ROOT / "data" / "originalReaders" / "vocabulary" / "latin-appendices.json"
EXTRA = CACHE / "sigao-extra-chapters.json"

# The whole Catholic canon, as the Studium Biblicum site numbers its folders.
# Titles are stems: the site's index writes 厄則克爾 where its chapter pages write
# 厄則克耳, and a check that cannot survive that gets loosened in a hurry.
BOOKS: dict[str, tuple[int, str]] = {
    "GEN": (3, "創世紀"), "EXO": (4, "出谷紀"), "LEV": (5, "肋未紀"),
    "NUM": (6, "戶籍紀"), "DEU": (7, "申命紀"), "JOS": (8, "若蘇厄"),
    "JDG": (9, "民長紀"), "RUT": (10, "盧德"), "1SA": (11, "撒慕爾紀上"),
    "2SA": (12, "撒慕爾"), "1KI": (13, "列王紀上"), "2KI": (14, "列王紀下"),
    "1CH": (15, "編年"), "2CH": (16, "編年"), "EZR": (17, "厄斯德拉"),
    "NEH": (18, "厄斯德拉"), "TOB": (19, "多俾亞傳"), "JDT": (20, "友弟德傳"),
    "EST": (21, "艾斯德爾"), "1MA": (22, "瑪加伯上"), "2MA": (23, "瑪加伯下"),
    "JOB": (25, "約伯傳"), "PSA": (26, "聖詠"), "PRO": (27, "箴言"),
    "ECC": (28, "訓道篇"), "SNG": (29, "雅歌"), "WIS": (30, "智慧篇"),
    "SIR": (31, "德訓篇"), "ISA": (33, "依撒意亞"), "JER": (34, "耶肋米亞"),
    "LAM": (35, "哀歌"), "BAR": (36, "巴路克"), "EZK": (37, "厄則克"),
    "DAN": (38, "達尼爾"), "HOS": (40, "歐瑟亞"), "JOL": (41, "岳厄爾"),
    "AMO": (42, "亞毛斯"), "OBA": (43, "亞北底亞"), "JON": (44, "約納"),
    "MIC": (45, "米該亞"), "NAM": (46, "納鴻"), "HAB": (47, "哈巴谷"),
    "ZEP": (48, "索福尼亞"), "HAG": (49, "哈蓋"), "ZEC": (50, "匝加利亞"),
    "MAL": (51, "瑪拉基亞"), "MAT": (54, "瑪竇福音"), "MRK": (55, "馬爾谷福音"),
    "LUK": (56, "路加福音"), "JHN": (57, "若望福音"), "ACT": (58, "宗徒大事錄"),
    "ROM": (60, "羅馬書"), "1CO": (61, "格林多前書"), "2CO": (62, "格林多後書"),
    "GAL": (63, "迦拉達書"), "EPH": (64, "厄弗所書"), "PHP": (65, "斐理伯書"),
    "COL": (66, "哥羅森書"), "1TH": (67, "得撒洛尼前書"), "2TH": (68, "得撒洛尼後書"),
    "1TI": (69, "弟茂德前書"), "2TI": (70, "弟茂德後書"), "TIT": (71, "弟鐸書"),
    "PHM": (72, "費肋孟書"), "HEB": (73, "希伯來書"), "JAS": (75, "雅各伯書"),
    "1PE": (76, "伯多祿前書"), "2PE": (77, "伯多祿後書"), "1JN": (78, "若望一書"),
    "2JN": (79, "若望二書"), "3JN": (80, "若望三書"), "JUD": (81, "猶達書"),
    "REV": (82, "默示錄"),
}

# The Chinese psalter follows the Hebrew numbering; the Latin follows the Greek.
PSALM_SHIFT = {(10, 112): 1, (113, 113): -1, (116, 145): -1}


def chinese_psalm(latin_chapter: int) -> int:
    for (low, high), shift in PSALM_SHIFT.items():
        if low <= latin_chapter <= high:
            return latin_chapter + shift
    return latin_chapter


def name_chapters(lm: Lemmatiser, wanted: set[str]) -> dict[str, Counter]:
    """Which chapters each wanted name appears in, and how often."""
    where: dict[str, Counter] = defaultdict(Counter)
    for ref, text in L.vulgate_verses().items():
        book, chapter, _ = ref.split(".")
        if book not in BOOKS:
            continue
        words = L.words(text)
        for position, word in enumerate(words):
            if not position or not word[:1].isupper():
                continue
            lemma = lm.lemma(word)
            key = L.fold(lemma) if lemma else L.fold(word)
            if key in wanted:
                where[key][(book, int(chapter))] += 1
    return where


def cover(where: dict[str, Counter], budget: int) -> list[tuple[str, int]]:
    """Greedy: take the chapter that newly reaches the most names, repeat."""
    remaining = dict(where)
    chosen: list[tuple[str, int]] = []
    while remaining and len(chosen) < budget:
        score: Counter = Counter()
        for name, chapters in remaining.items():
            for chapter, hits in chapters.items():
                # Weight by occurrences: a name that appears eight times in a
                # chapter is one the alignment can actually settle there.
                score[chapter] += hits
        if not score:
            break
        best = score.most_common(1)[0][0]
        chosen.append(best)
        remaining = {name: chapters for name, chapters in remaining.items()
                     if best not in chapters}
    return chosen


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=160, help="最多抓幾章")
    ap.add_argument("--pace", type=float, default=0.7)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    appendix = json.loads(APPENDICES.read_text(encoding="utf-8"))
    rows = appendix["upper"]["names"]["entries"]
    unnamed = {row["folded"] for row in rows if not row["zh"]}
    print(f"專名 {len(rows)}，其中無中文 {len(unnamed)}")

    lm = Lemmatiser()
    where = name_chapters(lm, unnamed)
    print(f"能在武加大裡定位到章的 {len(where)}")
    plan = cover(where, args.budget)
    print(f"選出 {len(plan)} 章來抓")

    store = json.loads(EXTRA.read_text(encoding="utf-8")) if EXTRA.exists() else {}
    fetched = failed = 0
    for book, chapter in plan:
        chinese_chapter = chinese_psalm(chapter) if book == "PSA" else chapter
        key = f"{book}.{chapter}"
        if key in store:
            continue
        directory, title = BOOKS[book]
        sigao.BOOKS[book] = (directory, title)
        try:
            page = sigao.fetch_chapter(book, chinese_chapter)
        except SystemExit as exc:
            failed += 1
            print(f"  略過 {key}：{exc}", flush=True)
            continue
        store[key] = {"chineseChapter": chinese_chapter, "verses": page["verses"]}
        fetched += 1
        if fetched % 20 == 0:
            EXTRA.write_text(json.dumps(store, ensure_ascii=False), encoding="utf-8")
            print(f"  已抓 {fetched}/{len(plan)}", flush=True)
        time.sleep(args.pace)

    EXTRA.write_text(json.dumps(store, ensure_ascii=False), encoding="utf-8")
    print(f"新增 {fetched} 章，失敗 {failed}，快取共 {len(store)} 章")
    if args.write:
        print("->", EXTRA.relative_to(ROOT))


if __name__ == "__main__":
    main()
