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
MASTER = CACHE / "greek-reader-two-volumes.json"

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
    # 第二次尼西亞大公會議的教規是連綿長句，切到句號時往往只剩一段子句。
    # 這兩則的本課生詞在該卷別處找不到更完整的句子，故保留並在此具名。
    "31:31#1": "第 31 課：語法上是子句而非完整句，該課生詞在本半冊沒有更完整的落點。",
    "31:217#1": "第 42 課：以名詞片語作結，不是完整句；該課生詞在本半冊沒有更完整的落點。",
}


def chinese_by_ref(volume: int) -> dict[str, str]:
    """Where the Chinese actually is: the master, not the selection.

    The selectors leave ``translationZh`` empty on purpose — the Chinese is
    resolved during assembly, out of 和合本修訂版, the 1933 deuterocanon or the
    self-translated interlinear layer, depending on the unit.  Checking the
    selection file for it would always find nothing.
    """
    if not MASTER.exists():
        raise FileNotFoundError(
            f"缺少主檔：{MASTER}；先跑 build_greek_reader_data.py --write"
        )
    master = json.loads(MASTER.read_text(encoding="utf-8"))
    found = next((item for item in master["volumes"] if item["volume"] == volume), None)
    if found is None:
        raise LookupError(f"主檔沒有第 {volume} 冊")
    return {
        unit["ref"]: str(unit.get("translationZh") or "")
        for lesson in found["lessons"]
        for unit in lesson["memoryUnits"]
    }


def review(path: Path, key: str, label: str, volume: int, write: bool) -> dict:
    chinese = chinese_by_ref(volume)
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
        if not chinese.get(unit["ref"], "").strip():
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

    review(VERSES, "verses", "上冊記憶經節", 1, args.write)
    review(SENTENCES, "sentences", "下冊記憶句", 2, args.write)
    for ref, note in KEPT_WITH_NOTE.items():
        print(f"    {ref:<14s} {note}")

    if args.write:
        print(f"已寫回 {VERSES}")
        print(f"已寫回 {SENTENCES}")
    else:
        print("（未寫檔；加 --write 才會更新）")


if __name__ == "__main__":
    main()
