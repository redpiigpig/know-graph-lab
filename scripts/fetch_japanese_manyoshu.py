#!/usr/bin/env python3
"""Fetch the 萬葉集 and cut it into lesson-sized readings, at its own seams.

The Japanese reader's classical track had everything but the 萬葉集: 青空文庫
carries 折口信夫's *studies* of it (万葉集研究, 万葉集の解題) and not one poem.
Japanese Wikisource carries 鹿持雅澄's 訓訂 text complete, twenty volumes, with
the poem numbers printed — which is what makes it usable here.

**A poem is never split.** The text numbers every 歌 (`0001␣籠もよ…`), and a
headnote (詞書) belongs to the poem it introduces, so a reading is a run of
whole poems with their headnotes and the reading records which numbers it holds
(「第 1–12 首」). The alternative — cutting at a character count — would end a
lesson in the middle of a 長歌, which is the failure this whole series keeps
guarding against.

鹿持雅澄 died in 1858, so the text itself is long out of copyright; the
transcription is Wikisource's, CC BY-SA 4.0, and that is recorded per file.

    python -X utf8 scripts/fetch_japanese_manyoshu.py            # 看計畫
    python -X utf8 scripts/fetch_japanese_manyoshu.py --write
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/original-readers/japanese-full/manyoshu"
MANIFEST = CACHE / "manifest.json"

API = "https://ja.wikisource.org/w/api.php"
HEADERS = {"User-Agent": "know-graph-lab private reader build (contact: redpiigpig)"}

BOOK = "万葉集 (鹿持雅澄訓訂)"
NUMERALS = [
    "一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
    "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
]

# 歌番號印在行首：`0001␣籠（こ）もよ…`。這是文本自己的接縫。
POEM = re.compile(r"^(\d{4})[　 ]", re.M)

MIN_CHARS, MAX_CHARS = 900, 2600

RIGHTS = {
    "text": "鹿持雅澄訓訂（1791–1858 卒，公有領域）",
    "transcription": "日本語版ウィキソース，CC BY-SA 4.0",
}


def extract(title: str) -> str | None:
    query = urllib.parse.urlencode(
        {"action": "query", "prop": "extracts", "explaintext": 1,
         "titles": title, "format": "json", "redirects": 1}
    )
    for attempt in range(4):
        try:
            request = urllib.request.Request(f"{API}?{query}", headers=HEADERS)
            payload = json.loads(urllib.request.urlopen(request, timeout=90).read().decode("utf-8"))
            for page in payload.get("query", {}).get("pages", {}).values():
                return None if "missing" in page else page.get("extract", "")
        except Exception:  # noqa: BLE001 - retried with backoff
            time.sleep(8 * (attempt + 1))
    return None


def poems(text: str) -> list[tuple[int, str]]:
    """The volume as (number, text) pairs, each poem carrying its own headnote.

    A span from one poem number to the next holds two things: the poem itself,
    and then the 詞書 introducing the *following* poem — headnotes introduce,
    they do not conclude. So the span is split at its first blank line: what is
    before belongs to this poem, what is after is handed down to the next.

    Getting this wrong the obvious way (slice the span, and *also* prepend its
    tail to the next poem) prints every headnote twice, which reads as a textual
    variant rather than as a bug.
    """

    marks = [(m.start(), int(m.group(1))) for m in POEM.finditer(text)]
    if not marks:
        return []
    rows: list[tuple[int, str]] = []
    carried = ""
    for index, (start, number) in enumerate(marks):
        end = marks[index + 1][0] if index + 1 < len(marks) else len(text)
        span = text[start:end]
        chunks = [chunk.strip() for chunk in span.split(chr(10) + chr(10))]
        body = chunks[0]
        following = (chr(10) * 2).join(chunk for chunk in chunks[1:] if chunk)
        rows.append((number, (carried + chr(10) + body).strip() if carried else body))
        carried = following
    return rows


def group(rows: list[tuple[int, str]]) -> list[dict]:
    """Consecutive poems packed into readings, never cutting one in half."""

    readings: list[dict] = []
    current: list[tuple[int, str]] = []
    size = 0
    for number, body in rows:
        if current and size + len(body) > MAX_CHARS:
            readings.append(
                {"first": current[0][0], "last": current[-1][0],
                 "poems": len(current), "text": "\n\n".join(b for _, b in current)}
            )
            current, size = [], 0
        current.append((number, body))
        size += len(body)
    if current and size >= MIN_CHARS // 2:
        readings.append(
            {"first": current[0][0], "last": current[-1][0],
             "poems": len(current), "text": "\n\n".join(b for _, b in current)}
        )
    return readings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--delay", type=float, default=6.0)
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    total_readings = 0

    for index, numeral in enumerate(NUMERALS, start=1):
        title = f"{BOOK}/巻第{numeral}"
        if any(key.startswith(f"manyoshu:{index}:") for key in manifest):
            continue
        text = extract(title)
        if not text:
            print(f"  ✗ 巻第{numeral}：抓不到")
            continue
        rows = poems(text)
        readings = group(rows)
        total_readings += len(readings)
        print(f"  ✓ 巻第{numeral}：{len(rows)} 首 → {len(readings)} 篇讀物（{len(text):,} 字）")
        if args.write:
            CACHE.mkdir(parents=True, exist_ok=True)
            for order, reading in enumerate(readings, start=1):
                path = CACHE / f"manyoshu_{index:02d}_{order:02d}.txt"
                path.write_text(reading["text"], encoding="utf-8")
                manifest[f"manyoshu:{index}:{order}"] = {
                    "titleZh": f"萬葉集 卷第{numeral}",
                    "extent": f"第 {reading['first']}–{reading['last']} 首（完整 {reading['poems']} 首）",
                    "chars": len(reading["text"]),
                    "poems": reading["poems"],
                    "file": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "sourceUrl": f"https://ja.wikisource.org/wiki/{urllib.parse.quote(title)}",
                    "rights": RIGHTS,
                }
            MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
        time.sleep(args.delay)

    if not args.write:
        print("（未寫入；加 --write）")
        return 0
    chars = sum(item["chars"] for item in manifest.values())
    print(f"合計 {len(manifest)} 篇讀物、{chars:,} 字")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
