#!/usr/bin/env python3
"""Gate the Greek reader's data master against its frozen contract.

希伯來有 ``qa_hebrew_full_reader.py``、拉丁有 ``verify_latin_reader.py``，而希臘
與日文一直只有 builder 內建的自檢——builder 只在「組不出來」的時候才會出聲，組得
出來的錯它一句話都不會說。這一支補上希臘那一半（日文見 ``verify_japanese_reader.py``）。

每一條檢查都對應一個「發生了也看不出來」的錯：

* 一課悄悄少一個詞、或多一個；
* 兩課共用同一則背誦句（重排之後最容易發生）；
* 讀文標著「全篇」而其實是節錄——本系列的停止條件之一；
* 節錄了卻沒寫範圍，讀者以為自己讀完了一整章；
* 逐詞對譯缺了某一段，排出來就是一段沒有中文的希臘文；
* 專名表裡有中文空著（允許，但要數得出來——正式課本不印記號，所以紙面上看不出）。

    python -X utf8 scripts/verify_greek_reader.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
MASTER = CACHE / "greek-reader-two-volumes.json"
INTERLINEAR = CACHE / "interlinear.json"

LESSONS = 50
PER_LESSON = 20
MEMORY_PER_LESSON = 2


def load(path: Path):
    if not path.exists():
        raise SystemExit(f"缺 {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    master = load(MASTER)
    interlinear = load(INTERLINEAR)["units"]
    problems: list[str] = []
    notes: list[str] = []

    volumes = master["volumes"]
    if len(volumes) != 2:
        problems.append(f"應為兩冊，實得 {len(volumes)}")

    blank_names = 0
    missing_gloss: list[str] = []
    for volume in volumes:
        label = volume["title"]
        lessons = volume["lessons"]
        if len(lessons) != LESSONS:
            problems.append(f"{label}：{len(lessons)} 課，應為 {LESSONS}")

        numbers = [row["lesson"] for row in lessons]
        if numbers != list(range(1, LESSONS + 1)):
            problems.append(f"{label}：課次不是 1–{LESSONS} 連號")

        memory_refs: Counter = Counter()
        for lesson in lessons:
            number = lesson["lesson"]
            words = lesson["vocabulary"]
            if len(words) != PER_LESSON:
                problems.append(f"{label}第 {number} 課：{len(words)} 詞，應為 {PER_LESSON}")
            if any(not (word.get("glossZh") or "").strip() for word in words):
                problems.append(f"{label}第 {number} 課：有詞沒有繁中詞義")

            units = lesson.get("memoryUnits") or []
            if len(units) != MEMORY_PER_LESSON:
                problems.append(
                    f"{label}第 {number} 課：背誦單元 {len(units)} 則，應為 {MEMORY_PER_LESSON}")
            for unit in units:
                memory_refs[str(unit.get("ref"))] += 1

            reading = lesson.get("reading") or {}
            parts = reading.get("verses") or reading.get("segments") or []
            if not parts:
                problems.append(f"{label}第 {number} 課：讀文是空的")
            completeness = reading.get("completeness")
            if completeness not in {"complete", "excerpt"}:
                problems.append(f"{label}第 {number} 課：讀文沒有標明完整或節錄")
            # 🚨 裁了卻標「全篇」是本系列的停止條件；標了節錄卻不寫範圍同樣不行。
            if completeness == "excerpt" and not (reading.get("extent") or "").strip():
                problems.append(f"{label}第 {number} 課：標為節錄卻沒有寫出範圍")

            # 讀文的每一段都要有逐詞對譯，否則排出來就是一段沒有中文的希臘文。
            # 🚨 鍵的形狀兩冊不同，而且是**猜不得**的：上冊是 scripture:<osis ref>
            # （scripture:1John.1.1），下冊是 patristic:<課次>:<段 ref>
            # （patristic:1:0.1）。第一版照直覺拼成 scripture:0.1，於是 487 段全部
            # 被報成缺——一支會亂叫的驗證器比沒有還糟。
            for part in parts:
                ref = part.get("ref")
                if not ref:
                    continue
                key = (f"scripture:{ref}" if volume["volume"] == 1
                       else f"patristic:{number}:{ref}")
                if key not in interlinear:
                    missing_gloss.append(key)

        duplicated = [ref for ref, count in memory_refs.items() if count > 1]
        if duplicated:
            problems.append(f"{label}：背誦單元重覆 {len(duplicated)} 則 {duplicated[:5]}")

    # 🚨 欄位名要照資料實際的樣子查。希臘附錄的中文在 `zh`，不是 `glossZh`——
    # 照 glossZh 查會把 625 筆全部報成未定，而其實只有少數幾筆是空的。一支會亂叫
    # 的驗證器比沒有還糟。
    for table in master.get("appendices", []) or []:
        for entry in table.get("entries", []) or []:
            if not (entry.get("zh") or entry.get("glossZh") or "").strip():
                blank_names += 1
    if blank_names:
        notes.append(f"專名表有 {blank_names} 筆中文未定（紙本留白，不印記號）")

    if missing_gloss:
        problems.append(f"讀文有 {len(missing_gloss)} 段沒有逐詞對譯，"
                        f"例：{missing_gloss[:3]}")

    counts = master["counts"]
    for key, want in (("lessons", 100), ("vocabulary", 2000), ("memoryUnits", 200)):
        if counts.get(key) != want:
            problems.append(f"counts.{key} = {counts.get(key)}，應為 {want}")

    for line in problems:
        print(f"  ✘ {line}")
    for line in notes:
        print(f"  [注意] {line}")
    if problems:
        print(f"\n{len(problems)} 項未通過")
        return 1
    print(f"\n全部硬性檢查通過；{len(notes)} 項待辦")
    return 0


if __name__ == "__main__":
    sys.exit(main())
