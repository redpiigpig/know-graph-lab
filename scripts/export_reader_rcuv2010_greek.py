#!/usr/bin/env python3
"""Export the RCUV2010 Chinese the Greek reader needs, with one numbering crosswalk.

The reader's Chinese parallel comes from three places and they must not be
confused: 《和合本修訂版》（2010）for the New Testament and the canonical
Septuagint chapters, the 1933 Anglican deuterocanon for Tobit/Judith/Wisdom/
Sirach, and my own translation for the pseudepigrapha.  This script covers only
the first.

The hard part is the Psalms.  The reader follows Swete, whose numbering is the
Septuagint's, while the Chinese Bible follows the Masoretic numbering, and the
two diverge by one over most of the Psalter because the Septuagint joins MT 9
and 10 into a single psalm and later splits MT 116 and 147.  Every reference is
therefore routed through one crosswalk here rather than being adjusted ad hoc at
each call site — LXX 22 is MT 23, LXX 50 is MT 51, and LXX 9:27 is MT 10:6.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import time
import urllib.request
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
SCRIPTURE_PLAN = CACHE / "scripture-plan.json"
MEMORY = CACHE / "memory-verses.json"
OUTPUT = CACHE / "RCUV2010.json"

OFFICIAL_BASE = "https://rcuv.hkbs.org.hk/bb/info/RCUV2"
VERSION_CODE = "cuv2010"
VARIANT = "RCUV2（上帝版）"

# The reader's OSIS-style book codes mapped to the codes the official site uses.
BOOK_CODES = {
    "Gen": "GEN", "Exod": "EXO", "Ps": "PSA", "Isa": "ISA",
    "Matt": "MAT", "Mark": "MRK", "Luke": "LUK", "John": "JHN", "Acts": "ACT",
    "Rom": "ROM", "1Cor": "1CO", "2Cor": "2CO", "Gal": "GAL", "Eph": "EPH",
    "Phil": "PHP", "Col": "COL", "1Thess": "1TH", "2Thess": "2TH",
    "1Tim": "1TI", "2Tim": "2TI", "Titus": "TIT", "Phlm": "PHM", "Heb": "HEB",
    "Jas": "JAS", "1Pet": "1PE", "2Pet": "2PE", "1John": "1JN", "2John": "2JN",
    "3John": "3JN", "Jude": "JUD", "Rev": "REV",
}

BOOK_NAMES_ZH = {
    "Gen": "創世記", "Exod": "出埃及記", "Ps": "詩篇", "Isa": "以賽亞書",
    "Matt": "馬太福音", "Mark": "馬可福音", "Luke": "路加福音", "John": "約翰福音",
    "Acts": "使徒行傳", "Rom": "羅馬書", "1Cor": "哥林多前書", "2Cor": "哥林多後書",
    "Gal": "加拉太書", "Eph": "以弗所書", "Phil": "腓立比書", "Col": "歌羅西書",
    "1Thess": "帖撒羅尼迦前書", "2Thess": "帖撒羅尼迦後書", "1Tim": "提摩太前書",
    "2Tim": "提摩太後書", "Titus": "提多書", "Phlm": "腓利門書", "Heb": "希伯來書",
    "Jas": "雅各書", "1Pet": "彼得前書", "2Pet": "彼得後書", "1John": "約翰一書",
    "2John": "約翰二書", "3John": "約翰三書", "Jude": "猶大書", "Rev": "啟示錄",
}


def psalm_crosswalk(lxx_chapter: int, lxx_verse: int | None) -> tuple[int, int | None, str]:
    """Map a Septuagint psalm reference to the Masoretic one the Chinese uses."""
    if lxx_chapter <= 8:
        return lxx_chapter, lxx_verse, "同號"
    if lxx_chapter == 9:
        # The Septuagint runs MT 9 and MT 10 together as one psalm.
        if lxx_verse is not None and lxx_verse >= 22:
            return 10, lxx_verse - 21, "七十士第 9 篇後半＝馬所拉第 10 篇"
        return 9, lxx_verse, "七十士第 9 篇前半＝馬所拉第 9 篇"
    if 10 <= lxx_chapter <= 112:
        return lxx_chapter + 1, lxx_verse, "七十士較馬所拉少一號"
    if lxx_chapter == 113:
        return 114, lxx_verse, "七十士第 113 篇＝馬所拉第 114–115 篇，逐節對照須人工複核"
    if lxx_chapter in (114, 115):
        return 116, lxx_verse, "七十士第 114–115 篇合為馬所拉第 116 篇，逐節對照須人工複核"
    if 116 <= lxx_chapter <= 145:
        return lxx_chapter + 1, lxx_verse, "七十士較馬所拉少一號"
    if lxx_chapter in (146, 147):
        return 147, lxx_verse, "七十士第 146–147 篇合為馬所拉第 147 篇，逐節對照須人工複核"
    if 148 <= lxx_chapter <= 150:
        return lxx_chapter, lxx_verse, "同號"
    raise LookupError(f"詩篇 {lxx_chapter} 不在馬所拉本內（七十士第 151 篇無中譯）")


def target_reference(book: str, chapter: int, verse: int | None) -> tuple[int, int | None, str]:
    if book == "Ps":
        return psalm_crosswalk(chapter, verse)
    return chapter, verse, "同號"


def clean(value: str) -> str:
    value = re.sub(r"<sup\b[^>]*>.*?</sup>", "", value, flags=re.S | re.I)
    value = re.sub(r"<br\s*/?\s*>", "", value, flags=re.I)
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def blocks(markup: str, tag: str) -> list[str]:
    pattern = re.compile(rf"<{tag}\b[^>]*>(.*?)</{tag}>", re.S | re.I)
    return [text for text in (clean(m.group(1)) for m in pattern.finditer(markup)) if text]


def fetch_chapter(book: str, chapter: int) -> dict:
    url = f"{OFFICIAL_BASE}/{BOOK_CODES[book]}/{chapter}/"
    request = urllib.request.Request(
        url, headers={"User-Agent": "private-authorized-original-reader/1.0"}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read().decode("utf-8", "replace")
    first = body.find("<")
    if first < 0:
        raise ValueError(f"{book} {chapter}：回應沒有 HTML")
    metadata = body[:first].strip()
    if not metadata.startswith("RCUV2|和合本2010"):
        raise ValueError(f"{book} {chapter}：版本標頭不是 RCUV2（{metadata[:40]}）")
    markup = body[first:]
    markers = list(re.finditer(r"<b>(\d+)(?:\s*[-–]\s*(\d+))?</b>", markup))
    verses = []
    for index, marker in enumerate(markers):
        start = marker.end()
        end = markers[index + 1].start() if index + 1 < len(markers) else len(markup)
        text = "".join(blocks(markup[start:end], "span")).strip()
        if not text:
            raise ValueError(f"{book} {chapter}:{marker.group(1)} 抓到空白經文")
        verses.append(
            {
                "verse": int(marker.group(1)),
                "verseEnd": int(marker.group(2) or marker.group(1)),
                "text": text,
            }
        )
    if not verses:
        raise ValueError(f"{book} {chapter}：沒有抓到任何經節")
    return {
        "verses": verses,
        "superscriptions": blocks(markup, "h6"),
        "sectionHeadings": blocks(markup, "h3"),
        "sourceUrl": url,
        "responseSha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
    }


def required() -> tuple[dict[str, set[int]], list[dict]]:
    plan = json.loads(SCRIPTURE_PLAN.read_text(encoding="utf-8"))
    memory = json.loads(MEMORY.read_text(encoding="utf-8"))
    wanted: dict[str, set[int]] = {}
    crosswalk: list[dict] = []

    def add(book: str, chapter: int, verse: int | None, origin: str) -> None:
        if book not in BOOK_CODES:
            return
        target_chapter, target_verse, note = target_reference(book, chapter, verse)
        wanted.setdefault(book, set()).add(target_chapter)
        if note != "同號":
            crosswalk.append(
                {
                    "origin": origin,
                    "greekRef": f"{book}.{chapter}" + (f".{verse}" if verse else ""),
                    "chineseRef": f"{book}.{target_chapter}"
                    + (f".{target_verse}" if target_verse else ""),
                    "note": note,
                }
            )

    for chapter in plan["chapters"]:
        if chapter["corpus"] in {"new-testament", "septuagint"}:
            add(chapter["osisBook"], chapter["chapter"], None, f"章目 {chapter['ref']}")
    for verse in memory["verses"]:
        if verse["corpus"] in {"new-testament", "septuagint"}:
            add(verse["book"], verse["chapter"], verse["verse"], f"記憶單元 {verse['ref']}")
    return wanted, crosswalk


def main() -> None:
    parser = argparse.ArgumentParser(description="匯出希臘文讀本所需的 RCUV2010 中文")
    parser.add_argument("--write", action="store_true", help="寫出 RCUV2010.json")
    args = parser.parse_args()

    wanted, crosswalk = required()
    total_chapters = sum(len(chapters) for chapters in wanted.values())
    print(f"需要 {len(wanted)} 卷、{total_chapters} 章；編號對照 {len(crosswalk)} 筆")

    books = []
    verse_units = 0
    for book in sorted(wanted):
        chapters = []
        for chapter in sorted(wanted[book]):
            payload = fetch_chapter(book, chapter)
            verse_units += len(payload["verses"])
            chapters.append({"chapter": chapter, **payload})
            print(f"  {BOOK_NAMES_ZH[book]} {chapter}：{len(payload['verses'])} 節")
            time.sleep(0.2)
        books.append({"code": book, "nameZh": BOOK_NAMES_ZH[book], "chapters": chapters})

    payload = {
        "schemaVersion": "1.0.0",
        "generatedOn": date.today().isoformat(),
        "translation": {
            "versionCode": VERSION_CODE,
            "titleZh": "和合本修訂版（2010）",
            "variant": VARIANT,
            "publisher": "香港聖經公會",
            "sourceUrl": "https://rcuv.hkbs.org.hk/",
            "useScope": "private-authorized",
        },
        "scope": "只涵蓋新約與七十士正典章節；次經走 1933 聖公會本，偽經自譯。",
        "numberingCrosswalk": {
            "rule": "七十士詩篇編號一律經本檔的對照函式換算成馬所拉編號後才取中文。",
            "entries": crosswalk,
        },
        "counts": {"books": len(books), "chapters": total_chapters, "verseUnits": verse_units},
        "books": books,
    }

    print(f"  合計 {len(books)} 卷、{total_chapters} 章、{verse_units} 節")
    for entry in crosswalk[:8]:
        print(f"    對照 {entry['greekRef']} → {entry['chineseRef']}（{entry['note']}）")

    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已寫出 {OUTPUT}")
    else:
        print("（未寫檔；加 --write 才會輸出）")


if __name__ == "__main__":
    main()
