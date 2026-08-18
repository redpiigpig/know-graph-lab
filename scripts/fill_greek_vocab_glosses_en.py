#!/usr/bin/env python3
"""Fill the English glosses that the vocabulary master is still missing.

Nine entries carry a Strong number but no English definition, because the first
extraction pass took the gloss from a lexicon field that happened to be empty
for them.  Their identity is already settled, so the gloss is simply looked up
by Strong number — Dodson first, whose brief definitions read as glosses rather
than as Strong's etymological prose, then Strong's own definition.

Nothing else is touched.  Entries whose identity rests only on corpus evidence
(the five Textus-Receptus spelling divergences) are left alone: they have no
Strong number to look up, and inventing one is exactly what must not happen.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from verify_greek_vocab_lexicon import (
    DODSON_EDITION,
    STRONGS_EDITION,
    clean_gloss,
    load_dodson,
    load_strongs,
)


ROOT = Path(__file__).resolve().parents[1]
VOCAB = ROOT / "data" / "originalReaders" / "vocabulary" / "greek-1000.json"


def by_number(index: dict) -> dict[str, dict]:
    flat: dict[str, dict] = {}
    for matches in index.values():
        for number, entry in matches:
            flat.setdefault(number, entry)
    return flat


def main() -> None:
    parser = argparse.ArgumentParser(description="用 Strong 編號補齊缺漏的英文釋義")
    parser.add_argument("--write", action="store_true", help="寫回詞彙主檔")
    args = parser.parse_args()

    entries = json.loads(VOCAB.read_text(encoding="utf-8"))
    dodson = by_number(load_dodson())
    strongs = by_number(load_strongs())

    filled = skipped = 0
    for entry in entries:
        if entry.get("glossEn"):
            continue
        number = entry.get("strong")
        if not number:
            skipped += 1
            print(f"  – #{entry['ordinal']:>4d} {entry['printedEntry']} — 無 Strong 編號，維持空白")
            continue
        source = dodson.get(number)
        edition = DODSON_EDITION
        if not source:
            source = strongs.get(number)
            edition = STRONGS_EDITION
        gloss = clean_gloss(source) if source else ""
        if not gloss:
            skipped += 1
            print(f"  – #{entry['ordinal']:>4d} {entry['printedEntry']} — {number} 兩本詞典都沒有釋義")
            continue
        entry["glossEn"] = gloss
        entry.setdefault("lexiconResolution", {})["glossEdition"] = edition
        filled += 1
        print(f"  ✓ #{entry['ordinal']:>4d} L{entry['lesson']:>2d} {entry['printedEntry']:<28s} {number:<7s} {gloss[:52]}")

    remaining = sum(1 for e in entries if not e.get("glossEn"))
    print(f"  補入 {filled} 筆，略過 {skipped} 筆；仍無英文釋義 {remaining}／{len(entries)}")

    if args.write:
        VOCAB.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已寫回 {VOCAB}")
    else:
        print("（未寫檔；加 --write 才會更新主檔）")


if __name__ == "__main__":
    main()
