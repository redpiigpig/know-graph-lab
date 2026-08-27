#!/usr/bin/env python3
"""Fetch 信望愛's Chinese Strong's dictionary, with the owner's authorisation.

The /scripture hover shows every word's parsing from local data, but its Chinese
meaning only for what this project has glossed itself — 87% of Greek word
instances and 78% of Hebrew, and those percentages are of *instances*, so the
rarer a word is the likelier the popup is blank. The owner obtained
authorisation on 2026-08-28 for private use of 信望愛's dictionary, which closes
that gap: `sd.php` returns the Chinese entry for any Strong number.

    N=0 希臘, N=1 希伯來; k = the Strong number as five digits, no letter prefix.

Two things this stores and one it does not. It stores the **first line** of the
entry (the headword, transliteration and grammatical note) and the **numbered
senses**, because that is what a hover popup can show. It does not store the
concordance statistics or the cross-reference apparatus, which belong to the
site and would make this a mirror of their database rather than a gloss layer.

The authorisation is recorded in the file, and it is **private use**: this data
must not be republished, and the /scripture page that reads it is behind the
same login as the rest of the site.

    python -X utf8 scripts/fetch_fhl_strong_dictionary.py --language greek --limit 20
    python -X utf8 scripts/fetch_fhl_strong_dictionary.py --write
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/source-cache/scripture/fhl-strong-dictionary.json"
MORPHOLOGY = ROOT / "output/source-cache/scripture/morphology"

API = "https://bible.fhl.net/json/sd.php"
HEADERS = {"User-Agent": "know-graph-lab private study build (contact: redpiigpig)"}

AUTHORISATION = {
    "source": "信望愛全球資訊網 bible.fhl.net JSON API（sd.php 原文字典）",
    "grantedBy": "站方授權（使用者 2026-08-28 告知已取得，限私人使用）",
    "scope": "私人研讀用；不得轉載、不得公開散布，讀取頁面須維持登入保護",
}

# 條目開頭是「編號 拉丁轉寫 {音標}」，接著文法說明，再接欽定本統計，最後才是
# 分項義。統計那一段對滑過去看一眼的人沒有用，也是最像「照抄人家資料庫」的
# 部分，所以不留。
SENSE = re.compile(r"^\s*(\d+[a-z]?\))\s*(.+)$")


def strong_numbers(language: str) -> list[str]:
    """Every Strong number the site's own text actually uses.

    Taken from this project's morphology layer rather than from 1..9999: asking
    for numbers no verse contains is a few thousand pointless requests against
    somebody else's server.
    """

    path = MORPHOLOGY / f"{language}.json"
    if not path.exists():
        raise SystemExit(f"缺 {path}；先跑 build_scripture_morphology.py")
    data = json.loads(path.read_text(encoding="utf-8"))
    numbers: set[str] = set()
    for words in data["byVerse"].values():
        for word in words:
            raw = word.get("strong") or ""
            digits = re.sub(r"\D", "", raw)
            if digits:
                numbers.add(f"{int(digits):05d}")
                continue
            # 希臘那邊 morphology 不帶 Strong，靠 lemma 對不上號——這一批留給
            # 既有的詞表，不在這裡硬湊。
    return sorted(numbers)


def greek_numbers() -> list[str]:
    """Greek Strong numbers, taken from the reader's own vocabulary and Dodson.

    MorphGNT tags lemmas, not Strong numbers, so the Greek side has to come from
    somewhere else: the reader's 2,000-word vocabulary carries both.
    """

    path = ROOT / "output/source-cache/original-readers/greek-full/greek-reader-two-volumes.json"
    numbers: set[str] = set()
    if path.exists():
        master = json.loads(path.read_text(encoding="utf-8"))
        for volume in master["volumes"]:
            for lesson in volume["lessons"]:
                for word in lesson["vocabulary"]:
                    digits = re.sub(r"\D", "", word.get("strong") or "")
                    if digits:
                        numbers.add(f"{int(digits):05d}")
    return sorted(numbers)


def fetch(language: str, number: str) -> dict | None:
    query = f"?N={0 if language == 'greek' else 1}&k={number}&gb=0"
    request = urllib.request.Request(API + query, headers=HEADERS)
    payload = json.loads(urllib.request.urlopen(request, timeout=60).read().decode("utf-8"))
    if payload.get("status") != "success" or not payload.get("record"):
        return None
    record = payload["record"][0]
    # sn 00000 是「查無此號」的預設條目，不是資料。
    if str(record.get("sn", "")).strip("0") == "":
        return None
    text = (record.get("dic_text") or "").replace("\r", "")
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    senses = []
    for line in lines:
        found = SENSE.match(line)
        if found:
            senses.append(f"{found.group(1)} {found.group(2)}")
    return {
        "sn": record["sn"],
        "orig": record.get("orig", ""),
        "head": lines[0] if lines else "",
        "senses": senses[:8],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=("greek", "hebrew", "both"), default="both")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--delay", type=float, default=0.7)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    store = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {
        "schemaVersion": "1.0.0",
        "authorisation": AUTHORISATION,
        "entries": {},
    }
    store["authorisation"] = AUTHORISATION
    entries = store["entries"]

    plan: list[tuple[str, str]] = []
    for language in ("greek", "hebrew") if args.language == "both" else (args.language,):
        numbers = greek_numbers() if language == "greek" else strong_numbers(language)
        plan.extend((language, number) for number in numbers)
    todo = [(l, n) for l, n in plan if f"{l[0].upper()}{n}" not in entries]
    if args.limit:
        todo = todo[: args.limit]
    print(f"要查 {len(plan)} 個編號，已有 {len(entries)}，本輪 {len(todo)}")

    if not args.write:
        print("（未下載；加 --write）")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    done = missing = failed = 0
    for language, number in todo:
        key = f"{language[0].upper()}{number}"
        try:
            record = fetch(language, number)
        except Exception as error:  # noqa: BLE001 - re-runnable
            failed += 1
            if failed % 20 == 1:
                print(f"  ✗ {key}：{error}")
            time.sleep(args.delay * 3)
            continue
        if record is None:
            missing += 1
        else:
            entries[key] = record
            done += 1
        if (done + missing) % 100 == 0:
            OUT.write_text(json.dumps(store, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"  … {done + missing}／{len(todo)}（收到 {done}）", flush=True)
        time.sleep(args.delay)

    OUT.write_text(json.dumps(store, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"完成：新增 {done}，站上查無 {missing}，失敗 {failed}；累計 {len(entries)} 條")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
