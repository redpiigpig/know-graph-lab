#!/usr/bin/env python3
"""Export the Traditional-Chinese deuterocanonical text the Greek reader needs.

The four deuterocanonical chapters read Swete's Greek, and their Chinese
parallel is the 1933 Anglican deuterocanon (信望愛站「次經閱讀」version code
``c1933``, labelled 1933年聖公會出版) rather than 思高本, because the release
contract froze the Anglican tradition for these books.

The 1933 translation carries its own book names -- 多比傳, 猶滴傳, 所羅門智訓,
便西拉智訓 -- and its own versification, which does not always match Swete.
Both are recorded verbatim; the Greek-to-Chinese verse crosswalk is a separate,
reviewed step and is never faked by renumbering here.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "source-cache" / "original-readers" / "greek-full" / "deuterocanon-zh.json"

BASE = "https://bible.fhl.net/new/readsub.php"
VERSION_CODE = "c1933"
VERSION_NAME = "1933 年聖公會出版次經"
SOURCE_URL = "https://bible.fhl.net/new/readsub.html"
LICENSE_NOTE = (
    "1933 年譯本正文已逾著作權期間；數位化來自信望愛站 CBOL 計畫，"
    "依其版權宣告作非商業之私人研究使用，並保留出處。"
)

# reader chapter ref -> FHL book code, FHL book name, Catholic (思高) name
CHAPTERS: list[dict] = [
    {"ref": "TobS.1", "fhlBook": "比", "chapter": 1,
     "nameZh": "多比傳", "catholicNameZh": "多俾亞傳",
     "greekTradition": "Swete Tob(S)＝西奈抄本 GII"},
    {"ref": "Jdt.13", "fhlBook": "滴", "chapter": 13,
     "nameZh": "猶滴傳", "catholicNameZh": "友弟德傳",
     "greekTradition": "Swete Jdt"},
    {"ref": "Wis.7", "fhlBook": "所", "chapter": 7,
     "nameZh": "所羅門智訓", "catholicNameZh": "智慧篇",
     "greekTradition": "Swete Wis"},
    {"ref": "Sir.24", "fhlBook": "便", "chapter": 24,
     "nameZh": "便西拉智訓", "catholicNameZh": "德訓篇",
     "greekTradition": "Swete Sir"},
]

VERSE_RE = re.compile(
    r"<tr><td align=center><b>(?P<chapter>\d+):(?P<verse>\d+)</b>.*?</td><td[^>]*>(?P<text>.*?)</td>",
    re.S,
)


def fetch(fhl_book: str, chapter: int) -> str:
    query = urllib.parse.urlencode(
        {"VERSION1": VERSION_CODE, "TABFLAG": "1", "chineses": fhl_book, "chap": f"{chapter:03d}"}
    )
    request = urllib.request.Request(
        f"{BASE}?{query}", headers={"User-Agent": "private-authorized-original-reader/1.0"}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read().decode("utf-8", "replace")
    if "1933年聖公會出版" not in body:
        raise ValueError(f"{fhl_book} {chapter}：回應不是 1933 年聖公會版")
    return body


def parse(body: str, chapter: int) -> list[dict]:
    verses = []
    for match in VERSE_RE.finditer(body):
        if int(match.group("chapter")) != chapter:
            continue
        text = re.sub(r"<[^>]+>", "", match.group("text"))
        text = html.unescape(text).strip()
        if not text:
            raise ValueError(f"第 {match.group('verse')} 節抓到空白經文")
        verses.append({"verse": int(match.group("verse")), "text": text})
    if not verses:
        raise ValueError("這一章沒有抓到任何經節")
    numbers = [verse["verse"] for verse in verses]
    if numbers != sorted(set(numbers)):
        raise ValueError(f"節次重複或亂序：{numbers}")
    return verses


def main() -> None:
    parser = argparse.ArgumentParser(description="匯出希臘文讀本所需的 1933 聖公會次經中譯")
    parser.add_argument("--write", action="store_true", help="寫出 deuterocanon-zh.json")
    args = parser.parse_args()

    books = []
    total = 0
    for spec in CHAPTERS:
        verses = parse(fetch(spec["fhlBook"], spec["chapter"]), spec["chapter"])
        total += len(verses)
        books.append({**spec, "verseCount": len(verses), "verses": verses})
        print(f"  {spec['ref']:<10s} {spec['nameZh']} 第 {spec['chapter']} 章  {len(verses)} 節")
        time.sleep(1.0)

    payload = {
        "schemaVersion": "1.0.0",
        "generatedOn": date.today().isoformat(),
        "translation": {
            "versionCode": VERSION_CODE,
            "titleZh": VERSION_NAME,
            "publisher": "1933 年聖公會",
            "sourceUrl": SOURCE_URL,
            "licenseNote": LICENSE_NOTE,
            "useScope": "private-authorized",
        },
        "numberingNote": (
            "1933 年譯本自有書名與分節，與 Swete 希臘文不必然一致；"
            "希中逐節對照另行人工複核，本檔不重編節號。"
        ),
        "counts": {"chapters": len(books), "verses": total},
        "books": books,
    }

    print(f"  合計 {len(books)} 章、{total} 節")
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已寫出 {OUTPUT}")
    else:
        print("（未寫檔；加 --write 才會輸出）")


if __name__ == "__main__":
    main()
