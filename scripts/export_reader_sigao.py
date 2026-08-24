#!/usr/bin/env python3
"""Fetch the Studium Biblicum Chinese for the upper volume's fifty chapters.

The owner chose 思高譯本 over 和合本修訂版 for this reader, and the reason is
structural rather than a preference: the Vulgate numbers its psalms the Greek
way, contains the deuterocanonical books, and names its people the way the
Catholic tradition names them.  Setting a Protestant edition beside it would
mean a crosswalk at every psalm, a gap at every deuterocanonical chapter, and
two different Chinese names for the same apostle.

信望愛 was tried first and abandoned for two reasons, both worth recording.  Its
思高 holding stops at the protocanonical books, so the five deuterocanonical
chapters this reader prints would have had to come from the 1933 Anglican
translation instead -- a second edition inside one volume, under Protestant book
names.  And its endpoint answers an unrecognised book with whatever it answered
last: ``chineses=多`` returns 弟鐸書 with status ``success``, and asking for
``engs=Gen`` returns Romans.  Nothing in the response says so.

So the text comes from the Studium Biblicum's own site, which carries the whole
Catholic canon in one edition.  Its pages put the verse number in one cell and
the verse in the next, mark section headings in their own row, underline proper
names, and hang cross-references off the right margin.  Each of those is lifted
into its own field rather than flattened into the verse or silently discarded --
the headings and cross-references are the edition's apparatus, not the
translation, and a reader that cannot tell them apart cannot be audited.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
PLAN = CACHE / "scripture-plan.json"
OUTPUT = CACHE / "sigao-zh.json"
RAW = CACHE / "sigao-cache.json"

BASE = "https://sbbible.dsbiblecentre.org"
VERSION_NAME = "思高譯本（思高聖經學會網上版）"
PUBLISHER = "思高聖經學會 Studium Biblicum O.F.M."
LICENSE_NOTE = (
    "思高譯本著作權屬思高聖經學會。本讀本為私人授權用途，"
    "逐章引用須經學會授權，不得再散布。"
)

# Vulgate book code -> the site's own directory number, with the title it must
# answer with.  The title is checked on every fetch because a wrong directory
# returns a perfectly valid page for the wrong book.  The expected titles are
# stems rather than full names: the site's index writes 厄則克爾 and its chapter
# pages write 厄則克耳, and a check that cannot survive that is a check that will
# be loosened in a hurry the first time it fires.
BOOKS = {
    "GEN": (3, "創世紀"), "EXO": (4, "出谷紀"), "DEU": (7, "申命紀"),
    "RUT": (10, "盧德"), "1KI": (13, "列王紀上"), "TOB": (19, "多俾亞傳"),
    "JDT": (20, "友弟德傳"), "2MA": (23, "瑪加伯下"), "JOB": (25, "約伯傳"),
    "PSA": (26, "聖詠"), "PRO": (27, "箴言"), "WIS": (30, "智慧篇"),
    "SIR": (31, "德訓篇"), "ISA": (33, "依撒意亞"), "JER": (34, "耶肋米亞"),
    "EZK": (37, "厄則克"), "DAN": (38, "達尼爾"), "JON": (44, "約納"),
    "MAT": (54, "瑪竇福音"), "MRK": (55, "馬爾谷福音"), "LUK": (56, "路加福音"),
    "JHN": (57, "若望福音"), "ACT": (58, "宗徒大事錄"), "ROM": (60, "羅馬書"),
    "1CO": (61, "格林多前書"), "GAL": (63, "迦拉達書"), "EPH": (64, "厄弗所書"),
    "PHP": (65, "斐理伯書"), "HEB": (73, "希伯來書"), "JAS": (75, "雅各伯書"),
    "1PE": (76, "伯多祿前書"), "1JN": (78, "若望一書"), "REV": (82, "默示錄"),
}

# The Vulgate follows the Greek psalter and the Studium Biblicum follows the
# Hebrew, so five of this reader's psalms sit one number apart.  The pairs are
# verified against the text rather than trusted: 22 must open with the shepherd.
PSALM_CROSSWALK = {22: 23, 50: 51, 90: 91, 129: 130}
PSALM_PROBE = {23: "牧", 51: "憐", 91: "至高", 130: "深淵"}

ROW_RE = re.compile(
    r"<tr[^>]*>\s*<td width=60>(?P<num>.*?)</td>\s*"
    r"<td width=440>(?P<text>.*?)</td>\s*"
    r"(?:<td width=100[^>]*>(?P<ref>.*?)</td>)?",
    re.S,
)
HEADING_RE = re.compile(r"<td width=500 colspan=2><b>(.*?)</b></td>", re.S)
TAG_RE = re.compile(r"<[^>]+>")
VERSE_NO_RE = re.compile(r"(\d+)\s*:\s*(\d+)")


def plain(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(TAG_RE.sub("", fragment))).strip()


def fetch_chapter(book: str, chapter: int) -> dict:
    directory, expected_title = BOOKS[book]
    url = f"{BASE}/part_1/{directory}/{chapter}.html"
    request = urllib.request.Request(
        url, headers={"User-Agent": "private-authorized-original-reader/1.0"}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read().decode("utf-8", "replace")

    title = plain(re.search(r"<title>(.*?)</title>", body, re.S).group(1))
    if expected_title not in title:
        raise SystemExit(f"要 {expected_title} 第 {chapter} 章，頁面卻是「{title}」：{url}")

    verses = []
    for match in ROW_RE.finditer(body):
        number = VERSE_NO_RE.search(plain(match.group("num")))
        if not number:
            continue
        text = match.group("text")
        names = [plain(n) for n in re.findall(r"<u>(.*?)</u>", text, re.S)]
        clean = plain(text)
        if not clean:
            raise SystemExit(f"{url} 第 {number.group(2)} 節是空的")
        verses.append({
            "verse": int(number.group(2)),
            "text": clean,
            "properNames": [n for n in names if n],
            "crossReference": plain(match.group("ref") or ""),
        })
    if not verses:
        raise SystemExit(f"{url} 沒有解析到經節")
    numbers = [v["verse"] for v in verses]
    if len(numbers) != len(set(numbers)):
        raise SystemExit(f"{url} 節次重複：{numbers}")
    # Out of order is not an error here.  This edition transposes verses where
    # its translators judged the received order corrupt -- Job 38 prints 38, 37
    # and then 40, 39 -- so the gate rejects duplicates and records transposition
    # rather than refusing the page.
    transposed = numbers != sorted(numbers)
    return {
        "url": url,
        "pageTitle": title,
        "sectionHeadings": [plain(h) for h in HEADING_RE.findall(body)],
        "verseOrderNote": "此版本調換節序，逐節對照時以節號為準" if transposed else "",
        "verses": verses,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--pace", type=float, default=1.0)
    args = ap.parse_args()

    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    cache = json.loads(RAW.read_text(encoding="utf-8")) if RAW.exists() else {}

    chapters = []
    for row in plan["chapters"]:
        book, latin_chapter = row["book"], row["chapter"]
        chinese_chapter = (PSALM_CROSSWALK.get(latin_chapter, latin_chapter)
                           if book == "PSA" else latin_chapter)
        key = f"{book}.{chinese_chapter}"
        if key not in cache:
            cache[key] = fetch_chapter(book, chinese_chapter)
            RAW.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
            time.sleep(args.pace)
        page = cache[key]

        if book == "PSA" and chinese_chapter in PSALM_PROBE:
            # The probe scans the whole psalm, not its opening: this edition
            # gives the superscription its own verse numbers, so the Miserere
            # does not reach the word 憐 until its third verse.
            whole = " ".join(v["text"] for v in page["verses"])
            if PSALM_PROBE[chinese_chapter] not in whole:
                raise SystemExit(
                    f"聖詠對照失敗：拉丁 {latin_chapter} 對到中文 {chinese_chapter}，"
                    f"但開頭沒有「{PSALM_PROBE[chinese_chapter]}」")

        note = ""
        if len(page["verses"]) != row["verses"]:
            note = f"拉丁 {row['verses']} 節，中文 {len(page['verses'])} 節，需逐節核對"
        chapters.append({
            "lesson": row["lesson"], "book": book, "latinChapter": latin_chapter,
            "chineseChapter": chinese_chapter, "title": row["title"],
            "note": row["note"], "sourceUrl": page["url"],
            "sectionHeadings": page["sectionHeadings"],
            "verseOrderNote": page.get("verseOrderNote", ""),
            "verseCount": len(page["verses"]), "latinVerseCount": row["verses"],
            "alignmentNote": note, "verses": page["verses"],
        })
        flag = f"  <-- {note}" if note else ""
        print(f"{row['lesson']:>3} {row['title']:<16s} 中文 {len(page['verses']):>3} 節"
              f"（拉丁 {row['verses']}）{flag}", flush=True)

    payload = {
        "schemaVersion": "1.0.0",
        "generatedOn": date.today().isoformat(),
        "translation": {
            "titleZh": VERSION_NAME, "publisher": PUBLISHER, "sourceUrl": BASE,
            "licenseNote": LICENSE_NOTE, "useScope": "private-authorized",
        },
        "psalmCrosswalk": {str(k): v for k, v in PSALM_CROSSWALK.items()},
        "chapters": chapters,
    }
    mismatched = [c for c in chapters if c["alignmentNote"]]
    print(f"共 {len(chapters)} 章；節數不一致 {len(mismatched)} 章")
    if args.write:
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        print("->", OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
