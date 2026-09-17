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

import reader_page_budget as budget

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


CLOSERS = "」』）)〉》】］"


def reunite_closers(chunks: list[str]) -> list[str]:
    """把跑到下一段開頭的收尾標點搬回前一段。

    🚨 切點在「。！？」』」之後，所以「…だもの。」」會在句號處先斷一次，收尾的
    「」」自成一片；剛好落在單元邊界時，讀本上就印出孤零零一行「」」。全書四處
    （另外三處是以「）」開頭的行）。

    修的是結果不是切點。改切點的版本試過：不在句末標點後面緊跟的收尾標點處斷，
    孤兒是沒了，卻把「…一層端厳な、「仏」」切成獨立一段——因為那個「」」是詞中
    的引號不是句末，而句中的「（？）」括號同樣分不出來。切點規則動一下，全書段落
    的分配就跟著重排，中譯是照文字雜湊接的，會整批脫鉤。這裡只搬標點，其他段落
    的邊界一個字都不動。
    """
    out: list[str] = []
    for chunk in chunks:
        lead = len(chunk) - len(chunk.lstrip(CLOSERS))
        if lead and out:
            out[-1] += chunk[:lead]
            chunk = chunk[lead:]
        if chunk:
            out.append(chunk)
    return out


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
    return reunite_closers(out)


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
    # 🚨 背誦要的是「一句」，不是「一段」。這裡的 unit 是段落，動輒兩三百字，
    # 落不進三十到五十字那個區間；第二冊第 15 課節選後只剩三段正文（65／208／370
    # 字），照段落挑就只有一句合格。先切成句子，候選才是真的句子。
    # 🚨 先拿整段當候選，湊不滿才切句。整句中譯是照**段落**的文字雜湊接上去的，
    # 背誦句一旦變成段落的子字串就接不到中譯——改成一律切句那次，一百一十八句
    # 背誦的中譯就這樣沒了，而且書照排、稽核照過。
    candidates: list[tuple[str, str]] = [
        (unit["text"].strip(), unit.get("label", "")) for unit in units
    ]
    sentence_level: list[tuple[str, str]] = []
    for unit in units:
        label = unit.get("label", "")
        for piece in sentences(unit["text"]):
            piece = piece.strip()
            if piece and piece != unit["text"].strip():
                sentence_level.append((piece, label))

    def gather(low: int, high: int) -> list[tuple[float, str, str]]:
        rows = []
        for text, unit_label in candidates:
            text = text.strip()
            if not (low <= len(text) <= high):
                continue
            if not text.endswith(("。", "」", "』", "！", "？")) and not unit_label:
                continue
            hits = sum(1 for form in words if form and form in text)
            # 太短與太長都難背；三十到五十字是一句能記住的長度。
            fit = 1.0 - abs(len(text) - 40) / 60
            rows.append((hits + fit, text, unit_label))
        rows.sort(key=lambda row: -row[0])
        return rows

    scored = gather(MEMORY_MIN, MEMORY_MAX)
    # 🚨 讀文改成節錄之後（上限 900 字元）候選池跟著縮小，第 15 課就湊不出兩句
    # 落在三十到五十字那個區間的。湊不滿時放寬長度限制再挑一次——比起讓一課少
    # 一句背誦，或為了這一課把讀文留長，放寬長度是代價最小的。
    if len(scored) < 2:
        # 整段湊不滿（第二冊第 15 課節選後只剩三段正文，65／208／370 字，只有一段
        # 落在區間內），才把段落切成句子來挑。這些句子沒有現成的整句中譯。
        candidates = sentence_level
        scored += [row for row in gather(MEMORY_MIN, MEMORY_MAX) if row not in scored]
    if len(scored) < 2:
        scored += [row for row in gather(MEMORY_MIN // 2, MEMORY_MAX * 2)
                   if row not in scored]
    picked: list[dict] = []
    for _, text, label in scored:
        if any(text == item["text"] for item in picked):
            continue
        picked.append({"label": label, "text": text})
        if len(picked) == 2:
            break
    return picked


# 一課的讀文能收多長，由共用的版面預算決定：scripts/reader_page_budget.py。
# 那裡不是一個詞數上限，而是一個量出來的版面模型——「這麼長、這麼多單元，排出來
# 會不會超過八頁」。單元數那一項不能省：同樣五百詞，分五段與分五十段厚度差很多。
#
# 擁有者 2026-09-17：「一課最多不能超過 8 頁」「大約抓個 500-800 字左右就好」
# 「但要是自然段落的選集喔，不要是語意沒講完就中斷」。所以裁的單位是文本自己的
# 分段（節、段、章），不是詞數切點。

def clip_units(units: list[dict], extent: str) -> tuple[list[dict], str]:
    """超過上限就從篇首連續取整段；回傳（段落、範圍說明）。

    🚨 一定要在指派 unit["id"] 與挑 memoryUnits 之前裁。id 在裁之後補就不會跳號，
    背誦句也會自動只從讀者讀得到的段落裡挑——希臘那一輪是先挑後裁，五十四則背誦
    句指向被砍掉的段落，書上照印，只是出處不存在。
    """
    def weight(unit: dict) -> int:
        return len(unit["text"])

    total = sum(weight(unit) for unit in units)
    if budget.fits("ja", total, len(units)):
        return units, extent
    kept = budget.clip(units, weight, "ja")
    # 🚨 裁過就不能再說「完整」。來源的 extent 寫的是「第 四 節（完整，共 7 節）」，
    # 在後面接一句「節錄前 7／8 段」的話，同一行會同時宣告完整與節錄——書上印出來
    # 就是這樣，兩句話互相打架，而讀者只能猜哪一句是真的。
    #
    # 課首那行出處說明與課名同區，寫長了會佔掉兩行、把生詞表推到下半頁——二十個
    # 詞就跨頁。所以這一行要短：字數在同一行末尾已經印過，這裡只講範圍。
    base = extent.replace("（完整，", "（").replace("（完整）", "").replace("完整，", "").strip()
    note = f"節錄前 {len(kept)}／{len(units)} 段"
    return kept, f"{base}　{note}" if base else note


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
            units, extent = clip_units(units, row["extent"])
            words = lesson_words(entries, volume["volume"], number)
            for index, unit in enumerate(units, start=1):
                unit["id"] = f"v{volume['volume']}-l{number:02d}-u{index:03d}"
            lessons.append({
                "lesson": number,
                "workId": row["workId"],
                "title": row["title"],
                "author": row["author"],
                "orthography": row["orthography"],
                "extent": extent,
                "sourceUrl": row["sourceUrl"],
                "chars": sum(len(unit["text"]) for unit in units),
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
