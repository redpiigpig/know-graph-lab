#!/usr/bin/env python3
"""Publish the printed flashcard decks as data the website can flip through.

The five lesson decks and three appendix decks exist as A4 duplex PDFs; this
takes the *same* card list — same builder, same picture map, same part-of-speech
resolution — and writes it as JSON plus the artwork the cards use, so the online
deck cannot drift from the printed one. Anything that changes a printed card
changes the online card on the next run of this script and nowhere else.

What it writes:

* ``public/content/flashcards/<deck>.json`` — the cards, and the deck's own
  counts so the page never has to compute them;
* ``public/flashcards-art/<file>.svg`` — only the artwork actually used, which
  is 877 files of the 4,565 OpenMoji ships.

OpenMoji is CC BY-SA 4.0 and the attribution travels with the data rather than
living only in a page template, because whoever copies this JSON somewhere else
needs to carry the licence with it.

    python -X utf8 scripts/export_flashcards_web.py --write
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_OUT = ROOT / "public/content/flashcards"
ART_OUT = ROOT / "public/flashcards-art"

TITLES = {
    "hbo": ("聖經希伯來文", "hbo", "課內詞卡"),
    "grc1": ("通用希臘文・上冊", "grc", "課內詞卡"),
    "grc2": ("通用希臘文・下冊", "grc", "課內詞卡"),
    "lat1": ("教會拉丁文・上冊", "la", "課內詞卡"),
    "lat2": ("教會拉丁文・下冊", "la", "課內詞卡"),
    "hbo-appendix": ("聖經希伯來文・附錄", "hbo", "附錄卡"),
    "grc-appendix": ("通用希臘文・附錄", "grc", "附錄卡"),
    "lat-appendix": ("教會拉丁文・附錄", "la", "附錄卡"),
}

LICENCE = {
    "artwork": "OpenMoji 17.0.0",
    "licence": "CC BY-SA 4.0",
    "url": "https://openmoji.org",
}


def builder():
    spec = importlib.util.spec_from_file_location(
        "build_flashcards", ROOT / "scripts/build_flashcards.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    module = builder()
    used: set[Path] = set()
    summary = []

    for deck, (title, language, kind) in TITLES.items():
        cards = module.load_cards(module.DECKS[deck])
        rows = []
        for card in cards:
            art = Path(card["picture"]).name if card.get("picture") else ""
            if card.get("picture"):
                used.add(Path(card["picture"]))
            rows.append(
                {
                    "front": card["headword"],
                    "zh": card["glossZh"],
                    "pos": card.get("pos", ""),
                    "lesson": str(card.get("lesson", "")),
                    "art": art,
                }
            )
        lessons = sorted({row["lesson"] for row in rows if row["lesson"]},
                         key=lambda value: (len(value), value))
        summary.append((deck, title, len(rows), sum(1 for r in rows if r["art"])))
        if args.write:
            DATA_OUT.mkdir(parents=True, exist_ok=True)
            (DATA_OUT / f"{deck}.json").write_text(
                json.dumps(
                    {
                        "deck": deck,
                        "title": title,
                        "language": language,
                        "kind": kind,
                        "counts": {
                            "cards": len(rows),
                            "withArt": sum(1 for row in rows if row["art"]),
                        },
                        "lessons": lessons,
                        "artwork": LICENCE,
                        "cards": rows,
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

    for deck, title, count, art in summary:
        print(f"  {deck:<14} {title:<18} {count:>5} 張，有圖 {art}")
    print(f"用到的圖檔 {len(used)} 個")

    if not args.write:
        print("（未寫入；加 --write）")
        return 0

    ART_OUT.mkdir(parents=True, exist_ok=True)
    copied = 0
    for path in sorted(used):
        target = ART_OUT / path.name
        if target.exists() and target.stat().st_size == path.stat().st_size:
            continue
        shutil.copy2(path, target)
        copied += 1
    index = {
        "generatedFrom": "scripts/build_flashcards.py（與紙本同一份卡表）",
        "artwork": LICENCE,
        "decks": [
            {"deck": deck, "title": title, "cards": count, "withArt": art}
            for deck, title, count, art in summary
        ],
    }
    (DATA_OUT / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"圖檔複製 {copied} 個 → {ART_OUT.relative_to(ROOT)}")
    print(f"卡表寫入 {DATA_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
