#!/usr/bin/env python3
"""Switch third-person pronouns that refer to God from 「他」 to 「祂」.

This cannot be a blanket substitution.  Of the 846 singular 「他」 glosses in the
reader, many belong to Pharaoh, Eli, Laban or the Canaanite kings — turning
those into 「祂」 would be worse than leaving the inconsistency.  Plural 「他們」
never refers to God in these texts and is left untouched.

So each affected unit is shown to the model with its full Hebrew text and its
whole-sentence Chinese, and the model reports only which of the listed token
positions have God as their referent.  Nothing else about the gloss changes:
the replacement is a single character swap on the positions it names, so a
wrong answer can only mis-set a pronoun, never rewrite a meaning.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("interlinear", ROOT / "scripts" / "build_hebrew_interlinear.py")
INTERLINEAR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INTERLINEAR)

MASTER = INTERLINEAR.OUTPUT
SINGULAR = re.compile(r"他(?!們)")

PROMPT = """下面是一段聖經希伯來文（或猶太禮文）的逐詞對譯。其中幾個詞的繁中詞義含有第三人稱「他」。

請判斷每一個標號的「他」指的是不是**上帝／耶和華**（含對上帝的稱呼，如「主」「至聖者」）。
- 指上帝 → 列入 divine
- 指人（法老、以利、拉班、摩西、迦南諸王、某個人…）、指物、或指集合名詞 → 不要列入

原文：{text}
整段意思：{sense}

要判斷的詞：
{items}

只輸出 JSON，不要其他文字：{{"divine":[標號, ...]}}
若全部都不是指上帝，輸出 {{"divine":[]}}"""


def affected(unit: dict[str, Any]) -> list[int]:
    return [index for index, token in enumerate(unit["tokens"]) if SINGULAR.search(token["glossZh"])]


def judge(unit: dict[str, Any], sense: str) -> list[int]:
    indexes = affected(unit)
    items = "\n".join(
        f"{position}. {unit['tokens'][index]['word']} ＝ {unit['tokens'][index]['glossZh']}"
        for position, index in enumerate(indexes, start=1)
    )
    raw = INTERLINEAR.call_model(PROMPT.format(text=unit["text"], sense=sense or "（無）", items=items))
    text = re.sub(r"^```[a-zA-Z]*\n?|\n?```$", "", raw.strip())
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ValueError("回應不含 JSON")
    chosen = json.loads(match.group(0)).get("divine", [])
    return [indexes[value - 1] for value in chosen if isinstance(value, int) and 1 <= value <= len(indexes)]


def main() -> None:
    parser = argparse.ArgumentParser(description="把指涉上帝的「他」改成「祂」")
    parser.add_argument("--model", choices=sorted(INTERLINEAR.MODEL_CHAINS), default="gemini")
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    INTERLINEAR._model_chain = INTERLINEAR.MODEL_CHAINS[args.model]
    INTERLINEAR._model = INTERLINEAR._model_chain[0]

    master = json.loads(MASTER.read_text(encoding="utf-8"))
    units = [unit for unit in master["units"].values() if affected(unit)]
    print(f"{len(units)} 個單元含單數「他」，共 {sum(len(affected(u)) for u in units)} 處", flush=True)

    lock = threading.Lock()
    changed = 0
    failures: list[str] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(judge, unit, unit.get("senseZh", "")): unit for unit in units}
        for future in as_completed(futures):
            unit = futures[future]
            try:
                divine = future.result()
            except Exception as error:  # noqa: BLE001 - report and continue
                failures.append(f"{unit['id']}：{type(error).__name__}")
                continue
            with lock:
                for index in divine:
                    token = unit["tokens"][index]
                    updated = SINGULAR.sub("祂", token["glossZh"])
                    if updated != token["glossZh"]:
                        changed += 1
                        if args.write:
                            token["glossZh"] = updated

    print(f"判定為指上帝並改寫：{changed} 處；失敗 {len(failures)} 個單元", flush=True)
    for line in failures[:10]:
        print(f"  {line}", flush=True)
    if args.write:
        MASTER.write_text(json.dumps(master, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已寫回 {MASTER}", flush=True)
    else:
        print("（未寫檔；加 --write 才更新）", flush=True)


if __name__ == "__main__":
    main()
