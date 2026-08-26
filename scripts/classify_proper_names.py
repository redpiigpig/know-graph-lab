#!/usr/bin/env python3
"""把九類專名分類寫進三種語言的附錄資料。

只加欄位（`category`、`categoryRoute`），不動任何既有欄位，所以三種語言可以分開
跑、也不會跟正在改排版的 session 撞在一起。

* **希臘** `greek-appendices.json` 的「人名、地名與國族」405 條
* **拉丁** `latin-appendices.json` 上冊 585 條、下冊 400 條
* **希伯來** `hebrew-proper-names.json` 119 條，以及 `hebrew-1000.json` 裡標了
  `isProperName` 的課內專名——希伯來原本就分好五類（人名／地名／民族與國名／
  神名與稱號／節期與聖日），這裡只把**人名**那一節再往下切。

判不出來的一律留在「其他人名」並記 `categoryRoute: ""`，不硬分。
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from proper_name_categories import Classifier, PLACE, NATION, DEITY, UNSORTED

ROOT = Path(__file__).resolve().parents[1]
V = ROOT / "data" / "originalReaders" / "vocabulary"
GREEK = V / "greek-appendices.json"
LATIN = V / "latin-appendices.json"
HEBREW_NAMES = V / "hebrew-proper-names.json"

# 希伯來既有的五類對到九類裡的哪一類；只有 person 需要再往下切。
HEBREW_TYPE_MAP = {
    "place": PLACE,
    "people_or_nation": NATION,
    "divine_name_or_title": DEITY,
    "festival_or_sacred_time": "節期與聖日",
}


def apply(entries: list[dict], classifier: Classifier, *, form_key: str,
          zh_key: str = "zh", english_key: str = "zhEnglish",
          kind_key: str = "kind", preset: str = "") -> collections.Counter:
    tally: collections.Counter = collections.Counter()
    for entry in entries:
        if preset:
            category, route = preset, "既有分類"
        else:
            category, route = classifier.classify(
                zh=entry.get(zh_key, "") or entry.get("glossZh", ""),
                form=entry.get(form_key) or entry.get("lemma") or entry.get("headword", ""),
                english=entry.get(english_key, "") or entry.get("name_english", ""),
                existing_kind=entry.get(kind_key, ""),
            )
        entry["category"] = category or UNSORTED
        entry["categoryRoute"] = route
        tally[entry["category"]] += 1
    return tally


def report(label: str, tally: collections.Counter) -> None:
    total = sum(tally.values())
    print(f"  {label}（{total} 條）")
    for name, count in tally.most_common():
        print(f"      {name}：{count}")


def do_greek(classifier: Classifier, write: bool) -> None:
    payload = json.loads(GREEK.read_text(encoding="utf-8"))
    table = payload["appendices"][0]
    tally = apply(table["entries"], classifier, form_key="headword")
    report("希臘 人名、地名與國族", tally)
    if write:
        GREEK.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"      已寫回 {GREEK.name}")


def do_latin(classifier: Classifier, write: bool) -> None:
    payload = json.loads(LATIN.read_text(encoding="utf-8"))
    for half in ("upper", "lower"):
        for key, table in payload[half].items():
            entries = table.get("entries") or []
            # 只有專名表要分類；數字、親屬、曆法那幾張本來就分好組了。
            if not any("名" in (table.get("title") or "") for _ in (0,)):
                continue
            if "專名" not in table["title"] and "人名" not in table["title"]:
                continue
            tally = apply(entries, classifier, form_key="headword")
            report(f"拉丁 {half}／{table['title']}", tally)
    if write:
        LATIN.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"      已寫回 {LATIN.name}")


def do_hebrew(classifier: Classifier, write: bool) -> None:
    payload = json.loads(HEBREW_NAMES.read_text(encoding="utf-8"))
    tally: collections.Counter = collections.Counter()
    for item in payload["items"]:
        types = item.get("properNameTypes") or []
        # 五類裡非人名的直接對過去，人名才往下切。
        mapped = next((HEBREW_TYPE_MAP[t] for t in types if t in HEBREW_TYPE_MAP), "")
        if mapped and "person" not in types:
            item["category"], item["categoryRoute"] = mapped, "既有 properNameTypes"
        else:
            category, route = classifier.classify(
                zh=item.get("glossZh", ""),
                form=item.get("unpointed") or item.get("pointed", ""),
                english=item.get("glossEn", ""),
                existing_kind="person" if "person" in types else "",
            )
            item["category"] = category or UNSORTED
            item["categoryRoute"] = route
        tally[item["category"]] += 1
    report("希伯來 專名", tally)
    if write:
        HEBREW_NAMES.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"      已寫回 {HEBREW_NAMES.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="替三種語言的專名分類")
    parser.add_argument("--language", choices=("grc", "la", "hbo", "all"), default="all")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--refresh-registers", action="store_true", help="重新上線抓登錄")
    args = parser.parse_args()

    from proper_name_categories import load_registers

    classifier = Classifier(load_registers(refresh=args.refresh_registers))
    if args.language in ("grc", "all"):
        do_greek(classifier, args.write)
    if args.language in ("la", "all"):
        do_latin(classifier, args.write)
    if args.language in ("hbo", "all"):
        do_hebrew(classifier, args.write)
    if not args.write:
        print("\n（未寫檔；加 --write 才會寫回）")


if __name__ == "__main__":
    main()
