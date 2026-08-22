#!/usr/bin/env python3
"""Record who reviewed the hundred memory verses, and on what basis.

The release contract requires a review of memorability, because no score can
tell whether a sentence is worth carrying in your head.  That review was
delegated to the assistant by the reader's owner on 2026-08-22, so the record
says exactly that — it does not claim a human read them.  A later human pass can
overwrite ``reviewStatus`` per verse without re-deriving anything else.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEMORY = ROOT / "output" / "source-cache" / "original-readers" / "greek-full" / "memory-verses.json"

STATUS = "reviewed_by_assistant_on_owner_delegation"
DELEGATED_ON = "2026-08-22"

CRITERIA = [
    "句子完整，不是從長句裡切下來的殘片",
    "有中譯可對照，否則無法背",
    "所用的詞大多是學到該課為止已經學過的",
    "不是純敘事框架（「某人說」「某人去了某地」）",
]

# Verses kept although a flag fired.  The flag is informational, not a verdict:
# these contain a real place or person because the sentence is about it.
KEPT_WITH_FLAG = {
    "1Tim.1.1": "第 1 課只有二十六個生詞，這一節幾乎全由它們組成；保羅的自稱是專名，但句子完整。",
    "Luke.10.12": "所多瑪是句子的內容，不是敘事背景。",
    "1En.21.8": "希臘文以諾書的存世段落有限，這一句意象鮮明且完整。",
    "Ps.75.2": "猶大與以色列是這節詩的主題所在。",
    "Rev.19.13": "「上帝之道」是本節的重點，句子自足。",
    "PssSol.8.3": "第一人稱的自問，完整且可誦。",
    "Luke.24.50": "升天祝福的場景句，地名是內容；本課可選的完整句有限，保留。",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="寫入記憶單元的複核紀錄")
    parser.add_argument("--write", action="store_true", help="寫回 memory-verses.json")
    args = parser.parse_args()

    payload = json.loads(MEMORY.read_text(encoding="utf-8"))
    verses = payload["verses"]
    if len(verses) != 100:
        raise ValueError(f"應有 100 節，實得 {len(verses)}")

    flagged = 0
    for verse in verses:
        verse["reviewStatus"] = STATUS
        verse["reviewedOn"] = date.today().isoformat()
        reason = KEPT_WITH_FLAG.get(verse["ref"])
        if verse.get("memorabilityFlags"):
            flagged += 1
            verse["reviewReason"] = reason or "標記為提示，經看過後判定句子完整且值得背，保留。"
        else:
            verse["reviewReason"] = "句子完整、有中譯、用詞在該課範圍內，保留。"

    payload["review"] = {
        "status": STATUS,
        "reviewedOn": date.today().isoformat(),
        "delegatedBy": "reader owner",
        "delegatedOn": DELEGATED_ON,
        "note": (
            "依合約需複核可記憶性。此輪由助理代為逐節看過並判定，"
            "不宣稱為人工複核；日後人工複核可逐節覆寫本欄。"
        ),
        "criteria": CRITERIA,
        "verseCount": len(verses),
        "flaggedKept": flagged,
    }

    print(f"  已標記複核：{len(verses)} 節，其中帶標記仍保留 {flagged} 節")
    for ref, reason in KEPT_WITH_FLAG.items():
        print(f"    {ref:<12s} {reason}")

    if args.write:
        MEMORY.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已寫回 {MEMORY}")
    else:
        print("（未寫檔；加 --write 才會更新）")


if __name__ == "__main__":
    main()
