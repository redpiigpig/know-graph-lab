#!/usr/bin/env python3
"""Give every printed Japanese unit a whole-unit Traditional-Chinese rendering.

The word-by-word row says which word carries which meaning; it does not say what
the sentence means, and a reader who has only the gloss row is left to assemble
Japanese syntax out of a line of isolated Chinese words. Every other reader in
this series closes each unit with one whole-unit line, and the release contract
requires it.

Cached on the unit's own text, not on its id, so renumbering a lesson or
re-cutting a reading cannot pair a translation with someone else's sentence —
and a stopped run resumes.

    python -X utf8 scripts/translate_japanese_units.py --limit 40   # 試跑
    python -X utf8 scripts/translate_japanese_units.py              # 全書
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import original_reader_llm as llm
from translate_ebook_to_zh import _to_traditional as to_traditional

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/original-readers/japanese-full"
READINGS = CACHE / "readings.json"
OUTPUT = CACHE / "unit-sense.json"

BATCH = 8
KANA = re.compile(r"[ぁ-ゟァ-ヿ]")

PROMPT = """你是日文宗教學讀本的譯者。把下面 {count} 個段落各譯成**繁體中文**。

規矩：
- 一段一句到數句，忠實翻譯，不要摘要、不要加註、不要解釋。
- 一律譯成**白話**繁體中文；文語（舊字舊假名、聖書文語訳）也譯白話，不要譯成文言（不用「之乎者也」、不用「汝／爾」，第二人稱用「你／你們」）。只有萬葉集的和歌可以保留詩的語感。
- 聖經段落的專名與用語照和合本；「神の子」是「上帝的兒子」。
- 「云ふ」是「說」，譯文裡不要出現「雲」；「余」是「我」。
- 保留原有的專名；聖經人名地名用和合本／思高通行譯法。
- 只譯，不要附上日文原文，也不要出現日文假名。
- 譯不出來就回空字串，不要編。

只輸出 JSON 物件，鍵是題號字串，值是譯文：{{"1": "……", "2": "……"}}

{items}"""


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def signature(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def every_unit(readings: dict) -> list[tuple[str, str, str]]:
    """(hash, text, 出處) for every unit the book prints, readings and memory."""
    out: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    for volume in readings["volumes"]:
        for lesson in volume["lessons"]:
            ref = f"{lesson['author']}〈{lesson['title']}〉"
            for unit in lesson["units"] + lesson["memoryUnits"]:
                key = signature(unit["text"])
                if key in seen:
                    continue
                seen.add(key)
                out.append((key, unit["text"], ref))
    return out


def validate(text: str) -> str | None:
    """繁體是硬規則，不是偏好。

    模型（尤其掉到救急那一層時）會回簡體：第一次試跑十六段全是「从内在的意义」
    「污秽」「清净」。提示詞裡寫「繁體」擋不住，所以出口再過一次 opencc s2tw。
    """
    # 🚨 opencc s2tw 會把「云」（說）轉成「雲」、「余」（我）轉成「餘」——2026-09-23
    # 校對在成書裡抓到「如是雲爾」「雲曰」「餘輩」。這兩個字在譯文裡幾乎只會是
    # 文言的「說」與「我」，先護住再轉。
    text = (text or "").strip().replace("云", "").replace("余", "")
    text = to_traditional(text).replace("", "云").replace("", "余")
    if not text or KANA.search(text):
        return None
    return text


def ask(batch: list[tuple[str, str, str]]) -> dict[str, str]:
    items = "\n\n".join(
        f"{index}.（{ref}）\n{text}" for index, (_, text, ref) in enumerate(batch, start=1)
    )
    reply = llm.call_model(PROMPT.format(count=len(batch), items=items), max_tokens=4000)
    match = re.search(r"\{.*\}", reply or "", re.S)
    if not match:
        return {}
    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}
    out: dict[str, str] = {}
    for key, value in payload.items():
        if not key.strip().isdigit():
            continue
        index = int(key) - 1
        if 0 <= index < len(batch):
            zh = validate(str(value))
            if zh:
                out[batch[index][0]] = zh
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--batch", type=int, default=BATCH)
    args = parser.parse_args()

    readings = load(READINGS)
    done: dict[str, str] = load(OUTPUT) if OUTPUT.exists() else {}
    units = [row for row in every_unit(readings) if row[0] not in done]
    if args.limit:
        units = units[: args.limit]
    print(f"單元 {len(units):,} 待譯（已有 {len(done):,}）")

    batches = [units[i : i + args.batch] for i in range(0, len(units), args.batch)]
    for number, batch in enumerate(batches, start=1):
        got = ask(batch)
        if not got and len(batch) > 2:
            half = len(batch) // 2
            got = {**ask(batch[:half]), **ask(batch[half:])}
        done.update(got)
        OUTPUT.write_text(json.dumps(done, ensure_ascii=False, indent=0), encoding="utf-8")
        print(f"  批 {number}/{len(batches)}　{len(got)}/{len(batch)}　"
              f"累計 {len(done):,}　引擎 {llm.current_model()}")
    print(f"寫出 {OUTPUT.relative_to(ROOT)}：{len(done):,} 段")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
