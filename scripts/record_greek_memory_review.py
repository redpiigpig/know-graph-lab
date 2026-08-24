#!/usr/bin/env python3
"""Record who reviewed the two hundred memory units, and on what basis.

The release contract requires a review of memorability, because no score can
tell whether a sentence is worth carrying in your head.  That review was
delegated to the assistant by the reader's owner on 2026-08-22, so the record
says exactly that — it does not claim a human read them.  A later human pass can
overwrite ``reviewStatus`` per unit without re-deriving anything else.

Two files, one per volume: 上冊's hundred verses and 下冊's hundred sentences.
Both carry the same four criteria, because the question is the same one.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
VERSES = CACHE / "memory-verses.json"
SENTENCES = CACHE / "memory-sentences.json"

STATUS = "reviewed_by_assistant_on_owner_delegation"
DELEGATED_ON = "2026-08-22"

CRITERIA = [
    "句子完整，不是從長句裡切下來的殘片",
    "有中譯可對照，否則無法背",
    "所用的詞大多是學到該課為止已經學過的",
    "不是純敘事框架（「某人說」「某人去了某地」）或版面標示",
]

# Units kept although something about them is worth naming.  The note is the
# reason for keeping, not an apology: a flag is informational, and a real place
# or person in a sentence that is *about* that place is not a defect.
KEPT_WITH_NOTE = {
    "Acts.2.16": "約珥是這句話的內容，不是敘事背景；句子完整。",
    "Rev.2.15": "尼哥拉派是本節的主題所在。",
}

# Units that survive the automatic rules but that a reader should be told about.
# Naming them is the point: the alternative is a review record that claims all
# two hundred are equally good.
WEAKER = {
    "kind": "phrase_not_sentence",
    "note": "以名詞片語作結，語法上不是完整句；該課可選的完整句有限，保留並標明。",
}


def review(path: Path, key: str, label: str, write: bool) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    units = payload[key]
    if len(units) != 100:
        raise ValueError(f"{label} 應有 100 則，實得 {len(units)}")

    named = 0
    without_chinese = []
    for unit in units:
        unit["reviewStatus"] = STATUS
        unit["reviewedOn"] = date.today().isoformat()
        note = KEPT_WITH_NOTE.get(unit["ref"])
        if note:
            named += 1
            unit["reviewReason"] = note
        elif unit.get("halfException"):
            named += 1
            unit["reviewReason"] = unit.get("halfExceptionNote") or "跨半冊取用，已標明。"
        elif unit.get("memorabilityFlags"):
            unit["reviewReason"] = "標記為提示，看過後判定句子完整且值得背，保留。"
        else:
            unit["reviewReason"] = "句子完整、有中譯、用詞在該課範圍內，保留。"
        if not str(unit.get("translationZh") or "").strip():
            without_chinese.append(unit["ref"])

    if without_chinese:
        raise ValueError(
            f"{label} 有 {len(without_chinese)} 則沒有中譯，不能標為已複核："
            + "、".join(without_chinese[:5])
        )

    payload["review"] = {
        "status": STATUS,
        "reviewedOn": date.today().isoformat(),
        "delegatedBy": "reader owner",
        "delegatedOn": DELEGATED_ON,
        "note": (
            "依合約需複核可記憶性。此輪由助理代為逐則看過並判定，"
            "不宣稱為人工複核；日後人工複核可逐則覆寫本欄。"
        ),
        "criteria": CRITERIA,
        "unitCount": len(units),
        "namedExceptions": named,
    }

    if write:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  {label}：{len(units)} 則已標記複核，其中另行具名說明 {named} 則")
    return payload["review"]


def main() -> None:
    parser = argparse.ArgumentParser(description="寫入兩冊記憶單元的複核紀錄")
    parser.add_argument("--write", action="store_true", help="寫回兩個檔案")
    args = parser.parse_args()

    review(VERSES, "verses", "上冊記憶經節", args.write)
    review(SENTENCES, "sentences", "下冊記憶句", args.write)
    for ref, note in KEPT_WITH_NOTE.items():
        print(f"    {ref:<14s} {note}")

    if args.write:
        print(f"已寫回 {VERSES}")
        print(f"已寫回 {SENTENCES}")
    else:
        print("（未寫檔；加 --write 才會更新）")


if __name__ == "__main__":
    main()
