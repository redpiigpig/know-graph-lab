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
HEBREW_VOCAB = V / "hebrew-1000.json"
BRIDGE = V / "biblical-name-variants.json"
LEDGER = V / "proper-name-categories.json"

# 希伯來既有的五類對到九類裡的哪一類；只有 person 需要再往下切。
HEBREW_TYPE_MAP = {
    "place": PLACE,
    "people_or_nation": NATION,
    "divine_name_or_title": DEITY,
    "festival_or_sacred_time": "節期與聖日",
}


# 分類跑完另存一份「詞頭 -> 類別」的帳本。
#
# 為什麼要：`latin-appendices.json` 由另一條管線（build_latin_appendices.py）整檔
# 重生，重生一次 `category` 就整批不見，附錄印出來又變成沒有分節的一長串——而且是
# 靜靜地不見，因為檔案還在、欄位只是沒了。帳本讓「把分類補回去」變成離線、不用連
# 登錄、一秒跑完的一個指令（`--reapply`），而不是重跑整套判定。
LEDGER_NOTE = (
    "專名分類帳本：語言 -> 詞頭 -> {category, route}。分類本身由 "
    "scripts/classify_proper_names.py 判定；這份只是為了在附錄資料被上游管線整檔"
    "重生、category 欄整批消失時，能離線把分類補回去（--reapply）。"
)


def ledger_load() -> dict:
    if not LEDGER.exists():
        return {"schemaVersion": "1.0.0", "note": LEDGER_NOTE, "languages": {}}
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def ledger_record(ledger: dict, language: str, key: str, entry: dict) -> None:
    if not key:
        return
    ledger["languages"].setdefault(language, {})[key] = {
        "category": entry.get("category", ""),
        "route": entry.get("categoryRoute", ""),
    }


def ledger_save(ledger: dict) -> None:
    ledger["note"] = LEDGER_NOTE
    counts = {name: len(rows) for name, rows in ledger["languages"].items()}
    ledger["counts"] = counts
    LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"      帳本 {LEDGER.name}：" + "、".join(f"{k} {v}" for k, v in counts.items()))


def reapply(write: bool) -> None:
    """只把帳本裡記過的分類補回去，不重新判定，也不連登錄。"""
    ledger = ledger_load()["languages"]
    if not ledger:
        raise SystemExit(f"沒有帳本可用：{LEDGER}")

    def fill(entries: list[dict], language: str, key_of) -> tuple[int, int]:
        table = ledger.get(language, {})
        filled = missing = 0
        for entry in entries:
            if (entry.get("category") or "").strip():
                continue
            row = table.get(key_of(entry))
            if not row:
                missing += 1
                continue
            entry["category"], entry["categoryRoute"] = row["category"], row["route"]
            filled += 1
        return filled, missing

    greek = json.loads(GREEK.read_text(encoding="utf-8"))
    filled, missing = fill(greek["appendices"][0]["entries"], "grc",
                           lambda e: e.get("headword") or e.get("lemma", ""))
    print(f"  希臘：補回 {filled}，帳本沒有 {missing}")
    latin = json.loads(LATIN.read_text(encoding="utf-8"))
    for half in ("upper", "lower"):
        for table in latin[half].values():
            if "專名" not in table["title"] and "人名" not in table["title"]:
                continue
            filled, missing = fill(table["entries"], "la", lambda e: e["headword"])
            print(f"  拉丁 {half}／{table['title']}：補回 {filled}，帳本沒有 {missing}")
    hebrew = json.loads(HEBREW_NAMES.read_text(encoding="utf-8"))
    filled, missing = fill(hebrew["items"], "hbo",
                           lambda e: e.get("unpointed") or e.get("pointed", ""))
    print(f"  希伯來：補回 {filled}，帳本沒有 {missing}")

    if write:
        GREEK.write_text(json.dumps(greek, ensure_ascii=False, indent=2), encoding="utf-8")
        LATIN.write_text(json.dumps(latin, ensure_ascii=False, indent=2), encoding="utf-8")
        HEBREW_NAMES.write_text(json.dumps(hebrew, ensure_ascii=False, indent=2), encoding="utf-8")
        print("      已寫回三份附錄資料")
    else:
        print("\n（未寫檔；加 --write 才會寫回）")


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


def do_greek(classifier: Classifier, write: bool, ledger: dict) -> None:
    payload = json.loads(GREEK.read_text(encoding="utf-8"))
    table = payload["appendices"][0]
    tally = apply(table["entries"], classifier, form_key="headword")
    report("希臘 人名、地名與國族", tally)
    for entry in table["entries"]:
        ledger_record(ledger, "grc", entry.get("headword") or entry.get("lemma", ""), entry)
    if write:
        GREEK.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"      已寫回 {GREEK.name}")


def latin_bridge() -> dict[str, dict]:
    """拉丁字形 -> 希臘那邊已判好的分類。

    拉丁的中文是思高本、登錄收的是和合本，中文對不上；字形對得上，分類就跟著過來。
    """
    if not BRIDGE.exists():
        return {}
    payload = json.loads(BRIDGE.read_text(encoding="utf-8"))
    return {
        pair["latin"]: pair
        for pair in payload["pairs"]
        if pair.get("category") and pair["category"] != UNSORTED
    }


def do_latin(classifier: Classifier, write: bool, ledger: dict) -> None:
    payload = json.loads(LATIN.read_text(encoding="utf-8"))
    bridge = latin_bridge()
    for half in ("upper", "lower"):
        for key, table in payload[half].items():
            entries = table.get("entries") or []
            # 只有專名表要分類；數字、親屬、曆法那幾張本來就分好組了。
            if not any("名" in (table.get("title") or "") for _ in (0,)):
                continue
            if "專名" not in table["title"] and "人名" not in table["title"]:
                continue
            tally = apply(entries, classifier, form_key="headword")
            # 自己判不出來的，看希臘那邊有沒有同一個名字
            moved = 0
            for entry in entries:
                if entry["category"] != UNSORTED:
                    continue
                pair = bridge.get(entry["headword"])
                if not pair:
                    continue
                tally[UNSORTED] -= 1
                entry["category"] = pair["category"]
                entry["categoryRoute"] = "希臘↔拉丁字形橋"
                entry["zhProtestant"] = pair.get("zhProtestant", "")
                tally[entry["category"]] += 1
                moved += 1
            for entry in entries:
                ledger_record(ledger, "la", entry["headword"], entry)
            report(f"拉丁 {half}／{table['title']}", tally)
            if moved:
                print(f"      其中 {moved} 條由希臘側的分類經字形橋傳過來")
    if write:
        LATIN.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"      已寫回 {LATIN.name}")


def classify_hebrew_items(items: list[dict], classifier: Classifier) -> collections.Counter:
    tally: collections.Counter = collections.Counter()
    for item in items:
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
    return tally


def do_hebrew(classifier: Classifier, write: bool, ledger: dict) -> None:
    payload = json.loads(HEBREW_NAMES.read_text(encoding="utf-8"))
    report("希伯來 移出的專名", classify_hebrew_items(payload["items"], classifier))
    for item in payload["items"]:
        ledger_record(ledger, "hbo", item.get("unpointed") or item.get("pointed", ""), item)
    if write:
        HEBREW_NAMES.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"      已寫回 {HEBREW_NAMES.name}")

    # 課內留著的專名走同一套分類。附錄的分類表兩批一起收，只分一批的話同一節裡
    # 會一半有細類、一半沒有。
    vocab = json.loads(HEBREW_VOCAB.read_text(encoding="utf-8"))
    entries = vocab["entries"] if isinstance(vocab, dict) else vocab
    inline = [e for e in entries if e.get("isProperName")]
    report("希伯來 課內專名", classify_hebrew_items(inline, classifier))
    if write:
        HEBREW_VOCAB.write_text(json.dumps(vocab, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"      已寫回 {HEBREW_VOCAB.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="替三種語言的專名分類")
    parser.add_argument("--language", choices=("grc", "la", "hbo", "all"), default="all")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--refresh-registers", action="store_true", help="重新上線抓登錄")
    parser.add_argument("--reapply", action="store_true",
                        help="只從帳本把分類補回去，不重新判定（附錄被上游整檔重生後用）")
    args = parser.parse_args()

    if args.reapply:
        reapply(args.write)
        return

    from proper_name_categories import load_registers

    classifier = Classifier(load_registers(refresh=args.refresh_registers))
    ledger = ledger_load()
    if args.language in ("grc", "all"):
        do_greek(classifier, args.write, ledger)
    if args.language in ("la", "all"):
        do_latin(classifier, args.write, ledger)
    if args.language in ("hbo", "all"):
        do_hebrew(classifier, args.write, ledger)
    if args.write:
        ledger_save(ledger)
    else:
        print("\n（未寫檔；加 --write 才會寫回）")


if __name__ == "__main__":
    main()
