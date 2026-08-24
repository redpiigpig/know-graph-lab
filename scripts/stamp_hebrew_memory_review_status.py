#!/usr/bin/env python3
"""Record honestly how each memory verse in the plan was chosen.

The reader's original 100 memory verses were hand-reviewed against the old
lesson vocabulary.  Lifting the proper names out of the word list moved every
lesson's contents, and only 51 of those verses still fall in any lesson's
candidate pool at all, so the reviewed 50x2 pairing could not be carried over.
The plan was therefore rebuilt by the scorer, and this script stamps the result
rather than letting the file keep claiming a review that no longer applies.

A verse that survived from the reviewed set keeps ``human_reviewed``; everything
else is ``pending_human_review`` and needs a pass before the reader ships.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "output/source-cache/original-readers/hebrew-full/scripture-plan.json"
REVIEW = ROOT / "output/source-cache/original-readers/hebrew-full/memory-selection-review.md"
SELECTOR = ROOT / "scripts/select_hebrew_memory_verses.py"


def previously_reviewed_refs() -> set[str]:
    """Read the reviewed 50x2 mapping still recorded in the selector."""

    source = SELECTOR.read_text(encoding="utf-8")
    start = source.index("REVIEWED_SELECTIONS")
    block = source[start : source.index("\n}\n", start) + 3]
    namespace: dict[str, object] = {}
    exec(block.replace("REVIEWED_SELECTIONS: dict[int, tuple[str, str]] =", "REVIEWED_SELECTIONS ="), namespace)
    return {ref for pair in namespace["REVIEWED_SELECTIONS"].values() for ref in pair}


def main() -> None:
    parser = argparse.ArgumentParser(description="標記背誦經文的審閱狀態")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    reviewed = previously_reviewed_refs()
    carried = 0
    for verse in plan["memoryVerses"]:
        status = "human_reviewed" if verse["ref"] in reviewed else "pending_human_review"
        verse["reviewStatus"] = status
        carried += status == "human_reviewed"
    for lesson in plan["memoryLessons"]:
        for verse in lesson.get("verses", []):
            verse["reviewStatus"] = "human_reviewed" if verse["ref"] in reviewed else "pending_human_review"

    pending = len(plan["memoryVerses"]) - carried
    plan.setdefault("selectionPolicy", {})["memorySelection"] = (
        "詞彙命中與累積覆蓋率評分自動選出，硬性排除專名列舉、人口貢物清單、族譜章段、"
        "缺謂述的殘句、過短過長與近似重複。專名移出詞表後原人工定稿的配對已不適用，"
        f"其中 {carried} 節沿用先前已審閱的經文，其餘 {pending} 節待人工審閱。"
    )
    plan.setdefault("validation", {}).update(
        {
            "memoryVerseReview": "pending_human_review" if pending else "human-reviewed-memorability",
            "memoryVerseCarriedFromReviewed": carried,
            "memoryVersePendingReview": pending,
        }
    )
    plan["status"] = "content_complete_memory_review_pending" if pending else plan.get("status", "")

    lines = [
        "# 希伯來文背誦經文審閱狀態",
        "",
        "專名自五十課詞表移出後，各課詞彙全面更動，原本人工定稿的 50×2 配對已無法沿用"
        f"（100 節中只有 51 節仍落在任一課的候選池內）。本表為評分器重選的結果：{carried} 節"
        f"沿用先前已審閱的經文，{pending} 節待審。",
        "",
        "| 課 | 節次 | 經文 | 命中本課詞 | 審閱狀態 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for verse in plan["memoryVerses"]:
        label = "已審閱" if verse["reviewStatus"] == "human_reviewed" else "待審閱"
        lines.append(
            f"| {verse['lesson']} | {verse['slot']} | {verse['ref']} | {verse.get('matchedCount', '')} | {label} |"
        )

    print(f"  沿用已審閱 {carried} 節，待審閱 {pending} 節")
    if not args.write:
        print("（未寫檔；加 --write 才會更新計畫與審閱表）")
        return
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REVIEW.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"已寫回 {PLAN}")
    print(f"已寫出 {REVIEW}")


if __name__ == "__main__":
    main()
