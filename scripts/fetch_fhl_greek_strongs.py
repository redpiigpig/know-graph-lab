#!/usr/bin/env python3
"""Get a Strong number for every Greek New Testament lemma, from 信望愛's qp.php.

The hover on /scripture shows Chinese from two places: this project's own
reviewed vocabulary, and — since the owner obtained private-use authorisation on
2026-08-28 — 信望愛's Chinese Strong dictionary. Hebrew joins the two on the
Strong number OSHB already carries. **Greek has no such number**: MorphGNT tags
lemmas, not Strong's, so the dictionary cannot be reached for the 13% of Greek
word instances this project has not glossed itself.

`qp.php` answers exactly that, one verse at a time: for each word it returns the
Strong number (`sn`) beside the word itself. What this keeps is the
**lemma → Strong** correspondence and nothing else — not their parsing (MorphGNT
has it), not their Chinese (the dictionary has it), not the verse text. The
result is a join key of a few thousand pairs rather than a copy of their text.

It stops early on purpose: once a full pass of a book adds no new lemma the book
is done, because a Strong number learned in Matthew is the same one in Mark.

    python -X utf8 scripts/fetch_fhl_greek_strongs.py --limit 40
    python -X utf8 scripts/fetch_fhl_greek_strongs.py --write
"""

from __future__ import annotations

import argparse
import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MORPHOLOGY = ROOT / "output/source-cache/scripture/morphology/greek.json"
OUT = ROOT / "output/source-cache/scripture/greek-lemma-strong.json"

API = "https://bible.fhl.net/json/qp.php"
HEADERS = {"User-Agent": "know-graph-lab private study build (contact: redpiigpig)"}

AUTHORISATION = {
    "source": "信望愛全球資訊網 bible.fhl.net JSON API（qp.php 逐詞字彙分析）",
    "grantedBy": "站方授權（使用者 2026-08-28 告知已取得，限私人使用）",
    "kept": "只留 lemma→Strong 的對應，不存其詞形分析、中文或經文",
}

# 書卷代號要用該站的 engs；本專案的形態層用的是 OSIS 代號。
ENGS = {
    "Matt": "Matt",
    "Mark": "Mark",
    "Luke": "Luke",
    "John": "John",
    "Acts": "Acts",
    "Rom": "Rom",
    "1Cor": "1 Cor",
    "2Cor": "2 Cor",
    "Gal": "Gal",
    "Eph": "Eph",
    "Phil": "Phil",
    "Col": "Col",
    "1Thess": "1 Thess",
    "2Thess": "2 Thess",
    "1Tim": "1 Tim",
    "2Tim": "2 Tim",
    "Titus": "Titus",
    "Phlm": "Philem",
    "Heb": "Heb",
    "Jas": "James",
    "1Pet": "1 Pet",
    "2Pet": "2 Pet",
    "1John": "1 John",
    "2John": "2 John",
    "3John": "3 John",
    "Jude": "Jude",
    "Rev": "Rev"
}


def fold(text: str) -> str:
    """Compare Greek without accents: the two sides breathe differently."""

    return "".join(
        c for c in unicodedata.normalize("NFD", text) if not unicodedata.combining(c)
    ).lower()


def verses() -> list[tuple[str, int, int, list[str]]]:
    data = json.loads(MORPHOLOGY.read_text(encoding="utf-8"))["byVerse"]
    rows = []
    for ref, words in data.items():
        book, chapter, verse = ref.rsplit(".", 2)
        if book not in ENGS:
            continue
        rows.append((book, int(chapter), int(verse), [w["lemma"] for w in words]))
    return sorted(rows, key=lambda row: (row[0], row[1], row[2]))


def fetch(book: str, chapter: int, verse: int) -> list[dict]:
    query = urllib.parse.urlencode({"engs": ENGS[book], "chap": chapter, "sec": verse, "gb": 0})
    request = urllib.request.Request(f"{API}?{query}", headers=HEADERS)
    payload = json.loads(urllib.request.urlopen(request, timeout=60).read().decode("utf-8"))
    if payload.get("status") != "success":
        # 代號寫錯時站上回 "Fail:engs error!"。把它當成沒事、照樣把這一節標成
        # 做完，就是先前十二節跑完什麼都沒學到卻回報成功的那個坑。
        raise ValueError(f"站上回覆 {payload.get('status')!r}")
    return payload.get("record", [])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--delay", type=float, default=0.7)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    store = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {
        "schemaVersion": "1.0.0",
        "authorisation": AUTHORISATION,
        "note": "希臘文詞位對 Strong 編號；MorphGNT 只標詞位，這一層是為了接上中文字典。",
        "done": [],
        "lemmas": {},
    }
    store["authorisation"] = AUTHORISATION
    lemmas: dict[str, str] = store["lemmas"]
    done = set(store["done"])

    rows = [row for row in verses() if f"{row[0]}.{row[1]}.{row[2]}" not in done]
    if args.limit:
        rows = rows[: args.limit]
    print(f"新約 {len(verses())} 節，已處理 {len(done)}，本輪 {len(rows)}；已知詞位 {len(lemmas)}")

    if not args.write:
        print("（未下載；加 --write）")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    added = failed = 0
    for index, (book, chapter, verse, our_lemmas) in enumerate(rows, start=1):
        # 這一節的詞位若全都已知，就不必問了——省下的是別人的伺服器。
        if all(fold(lemma) in lemmas for lemma in our_lemmas):
            done.add(f"{book}.{chapter}.{verse}")
            continue
        try:
            records = fetch(book, chapter, verse)
        except Exception as error:  # noqa: BLE001 - re-runnable
            failed += 1
            if failed % 20 == 1:
                print(f"  ✗ {book} {chapter}:{verse}：{error}")
            time.sleep(args.delay * 3)
            continue
        for record in records:
            number = re.sub(r"\D", "", str(record.get("sn") or ""))
            word = (record.get("orig") or record.get("word") or "").strip()
            if not number or not word or " " in word:
                continue
            key = fold(word)
            if key not in lemmas:
                lemmas[key] = f"{int(number):05d}"
                added += 1
        done.add(f"{book}.{chapter}.{verse}")
        if index % 100 == 0:
            store["done"] = sorted(done)
            OUT.write_text(json.dumps(store, ensure_ascii=False), encoding="utf-8")
            print(f"  … {index}／{len(rows)}（詞位 {len(lemmas)}，本輪新增 {added}）", flush=True)
        time.sleep(args.delay)

    store["done"] = sorted(done)
    OUT.write_text(json.dumps(store, ensure_ascii=False), encoding="utf-8")
    print(f"完成：詞位 {len(lemmas)}（本輪新增 {added}），失敗 {failed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
