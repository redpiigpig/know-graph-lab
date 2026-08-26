#!/usr/bin/env python3
"""Assemble the one master the Latin reader's surfaces all read.

Print, web and audio must not each re-derive the book from the plans, or they
drift: a lesson that reads Exodus 3 in the DOCX and John 17 online is a bug
nobody notices until someone holds both. So the plans, the vocabulary, the
Chinese, the memory units and the appendices are joined here exactly once, and
every surface slices this file.

Nothing is computed that a builder already computed. If a count looks wrong in
this file, the master upstream of it is wrong, and correcting it here would hide
that.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import latin_source_texts as L  # noqa: E402
import build_latin_full_reader as R  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
OUTPUT = CACHE / "latin-reader-two-volumes.json"

LITURGY_NOTE = "禮儀經文的固定對答採教會通行本文，其餘為自譯；付印前請對照《感恩祭典》核對"

VOLUME_META = [
    {"volume": 1, "slug": "vol1", "name": "上冊", "title": "武加大譯本",
     "blurb": "十篇禮儀短經，四十章完整武加大經文，中文並列思高譯本。"},
    {"volume": 2, "slug": "vol2", "name": "下冊", "title": "從教父到教廷",
     "blurb": "五十篇教父、中世紀與教廷文獻，終卷為常年期主日彌撒經文全文。"},
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    vocabulary = R.load(R.VOCABULARY)["entries"]
    memory = R.load(R.MEMORY, {"上冊": [], "下冊": []})
    appendices = R.load(R.APPENDICES, {})
    liturgy = R.load(R.LITURGY, {})
    translated = R.load(R.READINGS_ZH, {"units": {}})
    readings = {"上冊": R.upper_readings(), "下冊": R.lower_readings()}

    volumes = []
    for meta in VOLUME_META:
        name = meta["name"]
        words = [e for e in vocabulary if e["volume"] == name]
        units = memory.get(name, [])
        lessons = []
        for number in range(1, 51):
            reading = readings[name].get(number, {"title": "", "pairs": [], "note": ""})
            lesson_words = [e for e in words if e["lesson"] == number]
            lesson_units = [u for u in units if u["lesson"] == number]
            lessons.append({
                "lesson": number,
                "title": reading["title"],
                "note": reading["note"],
                "vocabulary": [{
                    "headword": e["headword"], "forms": e.get("forms", ""),
                    "pos": R.short_pos(e), "glossZh": e.get("glossZh", ""),
                    "glossEn": e.get("glossEn", ""),
                    "ecclesiastical": bool(e.get("ecclesiastical")),
                    "attested": e.get("attested", True),
                } for e in lesson_words],
                "memoryUnits": [{
                    "ref": u.get("ref", ""), "text": u["text"],
                    "zh": "" if u.get("zh") in (None, "reading-has-chinese") else u.get("zh", ""),
                    "readableFrom": u.get("readableFrom", number),
                } for u in lesson_units],
                "reading": [{"latin": latin, "zh": zh} for latin, zh in reading["pairs"]],
                "readingWords": sum(len(L.words(latin)) for latin, _ in reading["pairs"]),
            })
        volumes.append({
            **meta,
            "counts": {
                "words": len(words),
                "memoryUnits": len(units),
                "readingWords": sum(l["readingWords"] for l in lessons),
                "lessonsMissingMemory": [l["lesson"] for l in lessons
                                         if len(l["memoryUnits"]) < 2],
            },
            "lessons": lessons,
            "appendices": appendices.get("upper" if meta["volume"] == 1 else "lower", {}),
        })

    ordo = translated["units"].get("ordo:missa", {})
    gaps = R.gap_fill()
    payload = {
        "schemaVersion": "1.0.0",
        "generatedOn": date.today().isoformat(),
        "title": "教會拉丁文原文讀本",
        "pronunciation": "羅馬式教會發音",
        "colophon": [{"label": label, "text": text} for label, text in R.COLOPHON],
        "volumes": volumes,
        "terminal": {
            "title": "常年期主日彌撒經文",
            "latinTitle": "Ordo Missae, tempus per annum",
            "belongsTo": 2,
            "extent": liturgy.get("ordoMissae", {}).get("extent", ""),
            "translationNote": ordo.get("translationNote", "") or LITURGY_NOTE,
            "chineseStatus": "needs-received-text" if not ordo else "self-translated",
            "segments": [{"latin": s["latin"][0], "zh": s["zh"][0]}
                         for s in ordo.get("segments", [])] or
                        [{"latin": line, "zh": gaps.get(f"terminal:{index}", "")}
                         for index, line
                         in enumerate(liturgy.get("ordoMissae", {}).get("lines", []))],
        },
    }
    for volume in volumes:
        counts = volume["counts"]
        print(f"{volume['name']}：{counts['words']} 詞、{counts['memoryUnits']} 記憶單元、"
              f"讀本 {counts['readingWords']:,} 詞")
    print(f"終卷彌撒經文 {len(payload['terminal']['segments'])} 段")
    if args.write:
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        print("->", OUTPUT.relative_to(ROOT), f"{OUTPUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
