#!/usr/bin/env python3
"""Gate the Japanese reader's data master against its frozen contract.

四本讀本原本只有希伯來（``qa_hebrew_full_reader.py``）與拉丁
（``verify_latin_reader.py``）有各自的發行驗證器；希臘與日文只有 builder 內建的
自檢，而 builder 只在「組不出來」的時候才出聲。這一支補上日文那一半
（希臘見 ``verify_greek_reader.py``）。

每一條檢查都對應一個「發生了也看不出來」的錯：

* 一課悄悄少一個詞、或多一個；
* 兩課共用同一則背誦句；
* 讀文裁過卻沒寫範圍，讀者以為自己讀完了一整篇；
* 讀文的段落沒有逐詞對譯，排出來就是一段沒有中文的日文；
* 整句中譯缺段（分場記號與章節序號不算，那幾段本來就沒有東西可譯）；
* 詞表或對譯層混進簡體字。

🚨 日文的新字體（国・学・会・点）不是簡體字。不扣掉這四個，四百多頁乾淨的頁面
會被報成有簡體。

    python -X utf8 scripts/verify_japanese_reader.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "japanese-full"
READINGS = CACHE / "readings.json"
INTERLINEAR = CACHE / "interlinear.json"
SENSE = CACHE / "unit-sense.json"
EXERCISES = CACHE / "exercise-set.json"
VOCAB = ROOT / "data" / "originalReaders" / "vocabulary" / "japanese-2000.json"

LESSONS = 50
PER_LESSON = 20
MEMORY_PER_LESSON = 2

SIMPLIFIED = "们这个说国学见为变时关发会讲现实点样两员题长门问间东车马鸟语书图"
SHINJITAI = "国学会点"
SIMPLIFIED_ONLY = "".join(ch for ch in SIMPLIFIED if ch not in SHINJITAI)

# 這幾段是原文自己的分場記號與章節序號，沒有東西可譯。
UNTRANSLATABLE = {"＊", "×", "１", "２", "一", "二", "三"}


def load(path: Path):
    if not path.exists():
        raise SystemExit(f"缺 {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    readings = load(READINGS)
    interlinear = load(INTERLINEAR)["units"]
    # 🚨 整句中譯是照**文字的雜湊**接的，不是照 unit id——課次會動、切段會重切，
    # 照序號接會把某一句的譯文配到另一句底下。驗的時候要用同一把鑰匙。
    senses = load(SENSE)
    exercises = load(EXERCISES)
    vocabulary = load(VOCAB)["entries"]

    def sense_key(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    problems: list[str] = []
    notes: list[str] = []

    volumes = readings["volumes"]
    if len(volumes) != 2:
        problems.append(f"應為兩冊，實得 {len(volumes)}")

    # 🚨 分組要用 readerLesson，不是 lesson。`lesson` 是《大家的日本語》的課本章次
    # （一章可能對到讀本的一課半），`readerLesson` 才是讀本自己的課次。第一版拿
    # `lesson` 分組，於是第二冊每一課都被報成「30 詞、36 詞、127 詞」——那不是資料
    # 壞了，是我拿錯鑰匙。本系列的老坑：別拿課次編號當鍵。
    by_lesson: dict[tuple[int, int], list[dict]] = {}
    for entry in vocabulary:
        by_lesson.setdefault((entry["volume"], entry["readerLesson"]), []).append(entry)

    simplified_hits: Counter = Counter()
    missing_gloss: list[str] = []
    missing_sense: list[str] = []

    for volume in volumes:
        number_of_volume = volume["volume"]
        lessons = volume["lessons"]
        if len(lessons) != LESSONS:
            problems.append(f"第 {number_of_volume} 冊：{len(lessons)} 課，應為 {LESSONS}")
        if [row["lesson"] for row in lessons] != list(range(1, LESSONS + 1)):
            problems.append(f"第 {number_of_volume} 冊：課次不是 1–{LESSONS} 連號")

        memory_texts: Counter = Counter()
        for lesson in lessons:
            key = (number_of_volume, lesson["lesson"])
            words = by_lesson.get(key, [])
            if len(words) != PER_LESSON:
                problems.append(f"第 {number_of_volume} 冊第 {lesson['lesson']} 課："
                                f"{len(words)} 詞，應為 {PER_LESSON}")
            for word in words:
                for ch in SIMPLIFIED_ONLY:
                    if ch in (word.get("glossZh") or ""):
                        simplified_hits[ch] += 1

            units = lesson.get("memoryUnits") or []
            if len(units) != MEMORY_PER_LESSON:
                problems.append(f"第 {number_of_volume} 冊第 {lesson['lesson']} 課："
                                f"背誦單元 {len(units)} 則，應為 {MEMORY_PER_LESSON}")
            for unit in units:
                memory_texts[unit.get("text", "")] += 1

            if not lesson.get("units"):
                problems.append(f"第 {number_of_volume} 冊第 {lesson['lesson']} 課：讀文是空的")
            # 裁過就要寫出範圍。
            if "節錄" in (lesson.get("extent") or "") and "／" not in lesson["extent"] \
                    and "段" not in lesson["extent"]:
                problems.append(f"第 {number_of_volume} 冊第 {lesson['lesson']} 課："
                                "標為節錄卻沒有寫出範圍")

            for unit in lesson["units"]:
                uid = unit["id"]
                if uid not in interlinear:
                    missing_gloss.append(uid)
                text = unit.get("text", "").strip()
                if sense_key(unit["text"]) not in senses and text not in UNTRANSLATABLE:
                    missing_sense.append(uid)

        duplicated = [t for t, count in memory_texts.items() if count > 1]
        if duplicated:
            problems.append(f"第 {number_of_volume} 冊：背誦句重覆 {len(duplicated)} 則")

    if missing_gloss:
        problems.append(f"讀文有 {len(missing_gloss)} 段沒有逐詞對譯，例：{missing_gloss[:3]}")
    if missing_sense:
        # 分母講清楚：整句中譯的缺口曾經因為分母算錯而出現「817／813」。
        total = sum(len(l["units"]) for v in volumes for l in v["lessons"])
        notes.append(f"整句中譯缺 {len(missing_sense)}／{total} 段（已扣掉分場記號與章節序號），"
                     f"例：{missing_sense[:3]}")
    if simplified_hits:
        problems.append(f"詞義裡有簡體字：{dict(simplified_hits)}")

    if exercises.get("itemsPerLesson") != 10:
        problems.append(f"練習題每課應為 10 題，主檔寫 {exercises.get('itemsPerLesson')}")
    short = [row["lesson"] for row in exercises["lessons"] if len(row["items"]) != 10]
    if short:
        problems.append(f"練習題不足十題的課：{short[:10]}")

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
