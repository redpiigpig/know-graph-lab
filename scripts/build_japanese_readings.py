#!/usr/bin/env python3
"""Turn the Japanese reader's reading plan into the readings themselves.

The plan says *which* passage each volume takes; it does not carry a single
character of the passage. This resolves every plan row back to the text it
names, cuts it into the units the page will print, and picks the two memory
sentences each lesson needs.

Three things it refuses to do, all of them ways the other three readers have
already gone wrong:

* **Cut at a character count.** Every unit ends where the text itself ends a
  unit — a verse, a poem, a sentence. Long paragraphs are grouped by sentence,
  never split mid-sentence.
* **Key on a position.** A unit's id carries volume, lesson and index for the
  page, but the interlinear layer caches on the text's own hash, so renumbering
  a lesson cannot pair a gloss with someone else's words.
* **Guess the lesson order.** The order is frozen here and stated in the output:
  each volume runs from its shortest reading to its longest. It is not the
  plan's score order, which is a sort output and moves whenever the corpus does.

    python -X utf8 scripts/build_japanese_readings.py
    python -X utf8 scripts/build_japanese_readings.py --write
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_japanese_reading_plan import divisions

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/original-readers/japanese-full"
PLAN = CACHE / "reading-plan.json"
AOZORA = CACHE / "aozora/manifest.json"
SCRIPTURE = CACHE / "scripture/manifest.json"
MANYOSHU = CACHE / "manyoshu/manifest.json"
VOCAB = ROOT / "data/originalReaders/vocabulary/japanese-2000.json"
OUTPUT = CACHE / "readings.json"

ORDER_RULE = "每冊五十篇按字數由少到多排；同字數按作者與篇名。分數是排序輸出，不當課次。"

# 維基文庫的文語文本把讀音寫成漢字後的括號假名（我（われ）は…）。那是注音層，
# 不是正文；逐詞對譯自己會給讀音，留著只會讓斷詞把「（われ）」當成三個詞。
RUBY = re.compile(r"(?<=[一-鿿])（[ぁ-ゟー]+）")
VERSE_NUMBER = re.compile(r"^\d{1,3}$")
POEM_NUMBER = re.compile(r"^(\d{4})　?(.*)$")
SENTENCE_END = re.compile(r"(?<=[。！？」』])")
UNIT_MAX = 90          # 一個對譯單元最多幾個字，超過就在句與句之間換單元
MEMORY_MIN, MEMORY_MAX = 15, 70


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def strip_ruby(text: str) -> str:
    return RUBY.sub("", text)


def aozora_body(text: str) -> str:
    """青空文庫的檔頭兩行是書名與作者，不是正文。"""
    lines = text.split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    return "\n".join(lines[2:]).strip() if len(lines) > 2 else text


def sentences(paragraph: str) -> list[str]:
    parts = [p.strip() for p in SENTENCE_END.split(paragraph) if p.strip()]
    return parts or ([paragraph.strip()] if paragraph.strip() else [])


def pack(paragraph: str) -> list[str]:
    """把一段拆成不超過 UNIT_MAX 字的句群，句子本身絕不切開。"""
    out: list[str] = []
    current = ""
    for sentence in sentences(paragraph):
        if current and len(current) + len(sentence) > UNIT_MAX:
            out.append(current)
            current = sentence
        else:
            current += sentence
    if current:
        out.append(current)
    return out


def units_from_prose(text: str) -> list[dict]:
    out: list[dict] = []
    for paragraph in [p.strip() for p in text.split("\n") if p.strip()]:
        for chunk in pack(strip_ruby(paragraph)):
            out.append({"label": "", "text": chunk})
    return out


def units_from_verses(text: str) -> list[dict]:
    """文語訳聖書：一行節號、一行經文。"""
    out: list[dict] = []
    label = ""
    for line in [l.strip() for l in text.split("\n") if l.strip()]:
        if VERSE_NUMBER.match(line):
            label = line
            continue
        for index, chunk in enumerate(pack(strip_ruby(line))):
            out.append({"label": label if index == 0 else "", "text": chunk})
        label = ""
    return out


def units_from_poems(text: str) -> list[dict]:
    """萬葉集：歌番號起一首，續行接上去；詞書自成一段。"""
    out: list[dict] = []
    for block in [b for b in text.split("\n\n") if b.strip()]:
        lines = [l.strip().replace("　", " ").strip() for l in block.split("\n") if l.strip()]
        match = POEM_NUMBER.match(lines[0]) if lines else None
        if match:
            body = " ".join([match.group(2)] + lines[1:]).strip()
            out.append({"label": match.group(1).lstrip("0"), "text": strip_ruby(body)})
        else:
            out.extend(units_from_prose("\n".join(lines)))
    return out


def resolve(row: dict, aozora: dict, scripture: dict, manyoshu: dict) -> tuple[str, list[dict]]:
    """The plan row's own text, cut into units by whatever divides that text."""
    work = str(row["workId"])
    if work in scripture:
        item = scripture[work]
        text = (ROOT / item["file"]).read_text(encoding="utf-8")
        kind = "verse" if item.get("group") == "bible" else "prose"
        return text, (units_from_verses(text) if kind == "verse" else units_from_prose(text))
    if work in manyoshu:
        text = (ROOT / manyoshu[work]["file"]).read_text(encoding="utf-8")
        return text, units_from_poems(text)
    if work in aozora:
        whole = (ROOT / aozora[work]["file"]).read_text(encoding="utf-8")
        if row["extent"] == "全文":
            body = aozora_body(whole)
        else:
            label = row["extent"].split("第", 1)[1].split("節", 1)[0].strip()
            spans = dict(divisions(whole))
            if label not in spans:
                raise SystemExit(
                    f"{work}〈{row['title']}〉：計畫寫的是「{row['extent']}」，"
                    f"但這篇現在切出來的節是 {list(spans)[:12]}。"
                    "節不見了就不要換一節頂替——那會印出一篇沒人選過的文章。"
                )
            body = spans[label]
            body = "\n".join(body.split("\n")[1:]).strip()  # 節號那一行不是正文
        return body, units_from_prose(body)
    raise SystemExit(f"{work}：三份 manifest 都沒有這一篇")


def lesson_words(entries: list[dict], volume: int, lesson: int) -> list[str]:
    forms = []
    for entry in entries:
        if entry["volume"] == volume and entry["readerLesson"] == lesson:
            forms += [f for f in (entry.get("kanji"), entry.get("kana"),
                                  entry.get("dictionaryForm")) if f]
    return forms


def memory_units(units: list[dict], words: list[str]) -> list[dict]:
    """兩句背誦，取自本課讀文自己的句子。

    合約要求背誦與讀文同樣是宗教學或宗教史的內容；從本課讀文裡挑，這一條就不必
    另外證明。挑的是完整句、長度適中、且用得上本課生詞的句子。
    """
    scored = []
    for unit in units:
        text = unit["text"].strip()
        if not (MEMORY_MIN <= len(text) <= MEMORY_MAX):
            continue
        if not text.endswith(("。", "」", "』", "！", "？")) and not unit["label"]:
            continue
        hits = sum(1 for form in words if form and form in text)
        # 太短與太長都難背；三十到五十字是一句能記住的長度。
        fit = 1.0 - abs(len(text) - 40) / 60
        scored.append((hits + fit, text, unit["label"]))
    scored.sort(key=lambda row: -row[0])
    picked: list[dict] = []
    for _, text, label in scored:
        if any(text == item["text"] for item in picked):
            continue
        picked.append({"label": label, "text": text})
        if len(picked) == 2:
            break
    return picked


def build() -> dict:
    plan = load(PLAN)
    aozora = load(AOZORA)
    scripture = load(SCRIPTURE)
    manyoshu = load(MANYOSHU)
    entries = load(VOCAB)["entries"]

    volumes = []
    for volume in plan["volumes"]:
        rows = sorted(volume["readings"], key=lambda r: (r["chars"], r["author"], r["title"]))
        lessons = []
        for number, row in enumerate(rows, start=1):
            body, units = resolve(row, aozora, scripture, manyoshu)
            words = lesson_words(entries, volume["volume"], number)
            for index, unit in enumerate(units, start=1):
                unit["id"] = f"v{volume['volume']}-l{number:02d}-u{index:03d}"
            lessons.append({
                "lesson": number,
                "workId": row["workId"],
                "title": row["title"],
                "author": row["author"],
                "orthography": row["orthography"],
                "extent": row["extent"],
                "sourceUrl": row["sourceUrl"],
                "chars": len(body),
                "units": units,
                "memoryUnits": memory_units(units, words),
            })
        volumes.append({
            "volume": volume["volume"],
            "register": volume["register"],
            "lessons": lessons,
        })
    return {
        "schemaVersion": "1.0.0",
        "orderRule": ORDER_RULE,
        "note": "讀文正文由 reading-plan.json 逐篇解析而來；單元邊界取自文本自己的分段。",
        "volumes": volumes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    data = build()
    problems = 0
    for volume in data["volumes"]:
        lessons = volume["lessons"]
        units = sum(len(l["units"]) for l in lessons)
        chars = sum(l["chars"] for l in lessons)
        short = [l["lesson"] for l in lessons if len(l["memoryUnits"]) < 2]
        empty = [l["lesson"] for l in lessons if not l["units"]]
        print(f"第{volume['volume']}冊：{len(lessons)} 課、{units:,} 單元、{chars:,} 字")
        print(f"    最長一課 {max(l['chars'] for l in lessons)} 字、"
              f"最短 {min(l['chars'] for l in lessons)} 字")
        if short:
            print(f"    ⚠ 背誦不足兩句：第 {short} 課")
            problems += len(short)
        if empty:
            print(f"    ✘ 沒有單元：第 {empty} 課")
            problems += len(empty)
    if args.write and not problems:
        OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"已寫入 {OUTPUT.relative_to(ROOT)}")
    elif args.write:
        print("有問題，沒有寫入。")
    else:
        print("（未寫入；加 --write）")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
