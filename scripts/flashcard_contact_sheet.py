#!/usr/bin/env python3
"""把候選配圖排成一張 contact sheet，人眼看過再決定要不要用。

OpenMoji 的名字不等於圖：`wedding` 是帶十字架的教堂、`tap` 是手指點擊不是水龍
頭、`assembly group` 是大人牽小孩。這些光讀名字看不出來，印在卡上就是教錯。
新增 override 後、重建牌組前跑這支，看圖比對一遍。

    python scripts/flashcard_contact_sheet.py --names "x-ray" "delete" "wedding"
    python scripts/flashcard_contact_sheet.py --deck hbo --sample 48

圖檔順序＝參數順序（`--deck` 則照詞表順序），對照 stdout 印出的編號清單看。
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MAPS = {
    "hbo": ROOT / "output/source-cache/flashcards/hebrew-card-images.json",
    "grc1": ROOT / "output/source-cache/flashcards/greek-card-images.json",
    "grc2": ROOT / "output/source-cache/flashcards/greek-card-images.json",
    "lat1": ROOT / "output/source-cache/flashcards/latin-card-images.json",
    "lat2": ROOT / "output/source-cache/flashcards/latin-card-images.json",
}
COLUMNS = 8
CELL = 110


def matcher():
    """借希伯來 matcher 的 OpenMoji 載入與檔名解析，不重寫一份。"""

    spec = importlib.util.spec_from_file_location(
        "match_flashcard_images", ROOT / "scripts/match_flashcard_images.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ensure_openmoji()
    return module


def main() -> None:
    parser = argparse.ArgumentParser(description="配圖 contact sheet")
    parser.add_argument("--names", nargs="*", default=[], help="OpenMoji 本名，空白隔開")
    parser.add_argument("--deck", choices=sorted(MAPS), help="改抽某副牌現有的配圖")
    parser.add_argument("--sample", type=int, default=48, help="--deck 時取樣張數")
    parser.add_argument("--out", default=str(ROOT / "output/flashcards/contact-sheet.png"))
    args = parser.parse_args()

    module = matcher()
    by_name = module.load_openmoji()
    entries: list[tuple[str, Path]] = []

    for name in args.names:
        found = by_name.get(name.lower())
        path = module.image_path(found["hexcode"]) if found else None
        if path is None:
            raise SystemExit(f"查無此圖：{name!r}")
        entries.append((name, path))

    if args.deck:
        images = json.loads(MAPS[args.deck].read_text(encoding="utf-8"))["images"]
        items = list(images.items())
        step = max(1, len(items) // args.sample)
        for key, record in items[::step][: args.sample]:
            path = module.image_path(record["hexcode"])
            if path:
                entries.append((f"{key} {record['glossZh']}", path))

    if not entries:
        raise SystemExit("沒有要看的圖：給 --names 或 --deck")

    rows = (len(entries) + COLUMNS - 1) // COLUMNS
    sheet = Image.new("RGB", (COLUMNS * CELL, rows * CELL), "white")
    for index, (label, path) in enumerate(entries):
        art = Image.open(path).convert("RGBA").resize((CELL - 10, CELL - 10))
        cell = Image.new("RGBA", art.size, "white")
        cell.alpha_composite(art)
        sheet.paste(cell.convert("RGB"), ((index % COLUMNS) * CELL + 5, (index // COLUMNS) * CELL + 5))
        print(f"  {index + 1:>3}. {label}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(f"\n{len(entries)} 張，每列 {COLUMNS} 張 → {out}")


if __name__ == "__main__":
    main()
