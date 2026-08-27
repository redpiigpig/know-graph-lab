#!/usr/bin/env python3
"""Read《大家的日本語》's own lesson order off the public per-lesson word pages.

The Japanese reader follows the same rule as the Hebrew, Greek and Latin ones:
the named textbook's order governs the sequence and is never invented. The
textbook itself is not in this checkout, so the order is reconstructed from
u-biq's per-lesson pages (`tango01.html` … `tango50.html`), which print each
lesson's words in the book's own order, marked STEP 1 (重要度の高い単語) and
STEP 2, with the pitch accent shown by where the page breaks each word into
spans. That reconstruction is a fact about a third-party page, not about the
book, so it is recorded as such and printed in the colophon.

What this gets: lesson, order within the lesson, kana, kanji where the page
gives one, STEP, and the pitch-accent break positions. What it does not get:
meanings. Those are glossed afterwards, in Traditional Chinese, the same way
the other three readers gloss theirs.

    python -X utf8 scripts/fetch_minna_vocabulary.py --lessons 1-50 --write
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/original-readers/japanese-full"
RAW = CACHE / "u-biq"
OUTPUT = CACHE / "minna-lesson-order.json"

BASE = "https://kyoan.u-biq.org/tango{:02d}.html"
HEADERS = {"User-Agent": "know-graph-lab private reader build (contact: redpiigpig)"}

# 頁面用 <span> 切開重音位置，所以標籤要留到最後才拆。
TAG = re.compile(r"<[^>]+>")
KANJI_NOTE = re.compile(r"\[([^\]]+)\]")
KANA = re.compile(r"^[ぁ-ゖァ-ヺー・～ 　]+$")


def fetch(lesson: int, refresh: bool) -> str:
    RAW.mkdir(parents=True, exist_ok=True)
    cached = RAW / f"tango{lesson:02d}.html"
    if cached.exists() and not refresh:
        return cached.read_text(encoding="utf-8")
    request = urllib.request.Request(BASE.format(lesson), headers=HEADERS)
    # The page is Shift_JIS and says so only in a meta tag.
    html = urllib.request.urlopen(request, timeout=60).read().decode("shift_jis", "replace")
    cached.write_text(html, encoding="utf-8")
    time.sleep(1.0)
    return html


def strip_scripts(html: str) -> str:
    html = re.sub(r"<script.*?</script>", "", html, flags=re.S)
    return re.sub(r"<style.*?</style>", "", html, flags=re.S)


def parse(lesson: int, html: str) -> list[dict]:
    """The word lines of one lesson, in the page's order."""

    body = strip_scripts(html)
    # STEP 1 / STEP 2 divide the lesson; anything before the first STEP is the
    # page's own furniture.
    parts = re.split(r"STEP\s*([12])", body)
    words: list[dict] = []
    for index in range(1, len(parts) - 1, 2):
        step = int(parts[index])
        for raw in parts[index + 1].split("\n"):
            line = raw.strip()
            if not line or "<" not in line:
                continue
            # A word line is spans of kana, optionally followed by [漢字].
            plain = TAG.sub("", line).replace("&nbsp;", " ").strip()
            if not plain or plain.startswith("http"):
                continue
            note = KANJI_NOTE.search(plain)
            kanji = note.group(1) if note else ""
            kana = KANJI_NOTE.sub("", plain).strip()
            # Example sentences carry 。 or 、 and are not words; so are the
            # page's headings, which are not kana at all.
            if not kana or "。" in kana or "、" in kana:
                continue
            if not KANA.match(kana):
                continue
            if len(kana) > 18:
                continue
            # The accent is where the page breaks the word: 「きょ|うし」.
            breaks = [
                len(TAG.sub("", chunk))
                for chunk in re.findall(r">([^<]*)<", line)
                if chunk.strip()
            ]
            words.append(
                {
                    "lesson": lesson,
                    "step": step,
                    "kana": kana,
                    "kanji": kanji,
                    "accentBreaks": breaks,
                }
            )
    # The page prints each word once in the list and again inside the example
    # sentences; the sentences were filtered out above, but a word can still
    # repeat across STEP blocks.
    seen: set[tuple[str, str]] = set()
    unique = []
    for word in words:
        identity = (word["kana"], word["kanji"])
        if identity in seen:
            continue
        seen.add(identity)
        word["ordinal"] = len(unique) + 1
        unique.append(word)
    return unique


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lessons", default="1-50", help="例 1-50 或 1,2,3")
    parser.add_argument("--refresh", action="store_true", help="重抓，不用本機快取")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    if "-" in args.lessons:
        start, end = (int(part) for part in args.lessons.split("-"))
        lessons = range(start, end + 1)
    else:
        lessons = [int(part) for part in args.lessons.split(",")]

    collected: list[dict] = []
    for lesson in lessons:
        words = parse(lesson, fetch(lesson, args.refresh))
        print(f"  第 {lesson:>2} 課：{len(words):>3} 詞")
        collected.extend(words)

    print(f"合計 {len(collected)} 詞")
    if not args.write:
        print("（未寫入；加 --write）")
        return 0

    CACHE.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(
            {
                "schemaVersion": "1.0.0",
                "note": (
                    "《大家的日本語》各課詞序，取自 u-biq「みんなの日本語の単語」"
                    "逐課頁面。這是第三方頁面對課本順序的整理，不是課本本身；"
                    "版權頁須照實註明。詞義另行補繁體中文。"
                ),
                "source": BASE.format(0).replace("tango00", "tango{NN}"),
                "retrieved": "2026-08-27",
                "counts": {"lessons": len(list(lessons)), "words": len(collected)},
                "words": collected,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"已寫入 {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
