#!/usr/bin/env python3
"""Find, and optionally repair, Simplified Chinese that leaked into the readers.

Every Chinese string these four readers print is meant to be Traditional. Some
of it is not: the word-by-word glosses and the whole-sentence translations were
produced by a model, and when the model's fallback layer answered in Simplified
the answer was stored as given.  It reaches the page looking perfectly normal —
「因为」 under a Latin word, a whole paragraph of 「我从士麦那向你们问安」 under a
Greek sentence — and nothing in the render checks would ever notice.

Two rules this file exists to keep:

* **Detection is by character, never by round-tripping OpenCC.** Converting a
  string and comparing it with itself calls 祢 (the reverential 你) Simplified,
  and this series has already published one report built on that mistake. The
  test here is a list of characters that exist only as simplifications.
* **Japanese shinjitai are not Simplified Chinese.** 国・学・会・点 are the
  ordinary Japanese spellings of 國・學・會・點 and fill the Japanese reader's
  own text. They are excluded there, and only there.

Repair converts with OpenCC ``s2tw``, and only the strings that actually carry
one of those characters — a string already Traditional is never sent through,
so the converter cannot "fix" what was already right.

    python -X utf8 scripts/fix_reader_simplified_zh.py          # 只報告
    python -X utf8 scripts/fix_reader_simplified_zh.py --write
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers"

SIMPLIFIED = set("们这个说国学见为变时关发会讲现实点样两员题长门问间东车马鸟语书图")
SHINJITAI = set("国学会点")

# Which files hold printed Chinese, and which keys in them are that Chinese.
# Narrow on purpose: the corpus files also contain 个, but there it is inside a
# Japanese sentence being quoted, not a gloss anyone reads as Chinese.
FILES: tuple[tuple[str, str], ...] = (
    ("greek-full", "greek-reader-two-volumes.json"),
    ("greek-full", "interlinear.json"),
    ("latin-full", "interlinear.json"),
    ("japanese-full", "interlinear.json"),
    ("japanese-full", "interlinear-gloss.json"),
    ("hebrew-full", "interlinear.json"),
)
ZH_KEYS = {"glossZh", "translationZh", "senseZh", "zh", "chinese", "chineseZh", "titleZh"}


def is_japanese(folder: str) -> bool:
    return folder.startswith("japanese")


def offenders(text: str, folder: str) -> set[str]:
    wanted = SIMPLIFIED - (SHINJITAI if is_japanese(folder) else set())
    return wanted & set(text)


# 着／著 都是正體，但一本書只能用一種。四本讀本合計 2,227 個「著」對 7 個「着」，
# 所以房子的寫法是「著」，那 7 個是漏網的，不是另一種主張。
def normalise_zhe(text: str) -> str:
    return text.replace("着", "著")


def walk(node: Any, folder: str, convert, found: list[tuple[str, str, str]]) -> Any:
    """Rewrite every Chinese-bearing string that carries a Simplified character."""
    if isinstance(node, dict):
        out = {}
        for key, value in node.items():
            if key in ZH_KEYS and isinstance(value, str) and (
                offenders(value, folder) or "着" in value
            ):
                fixed = normalise_zhe(convert(value))
                found.append((key, value, fixed))
                out[key] = fixed
            else:
                out[key] = walk(value, folder, convert, found)
        return out
    if isinstance(node, list):
        return [walk(item, folder, convert, found) for item in node]
    return node


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    if args.write:
        import opencc  # noqa: PLC0415

        converter = opencc.OpenCC("s2tw")
        convert = converter.convert
    else:
        def convert(text: str) -> str:
            return text

    worst = 0
    for folder, name in FILES:
        path = CACHE / folder / name
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        found: list[tuple[str, str, str]] = []
        repaired = walk(payload, folder, convert, found)
        if not found:
            print(f"✔ {folder}/{name}")
            continue
        worst = 1
        print(f"✘ {folder}/{name}：{len(found)} 條中文含簡體字")
        for key, before, after in found[:4]:
            print(f"    {key}: {before[:46]}")
            if args.write:
                print(f"    {'':>{len(key)}}  → {after[:46]}")
        if args.write:
            path.write_text(json.dumps(repaired, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"    已改寫 {path.relative_to(ROOT)}")
    if not args.write and worst:
        print("（未寫入；加 --write）")
    return worst if not args.write else 0


if __name__ == "__main__":
    sys.exit(main())
