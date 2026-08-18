#!/usr/bin/env python3
"""Build the reviewed Traditional-Chinese gloss layer for the 1,000 Greek words.

``greek-1000.json`` is authoritative for order, printed entry, Mounce
transliteration and lesson assignment; it ships with ``glossZh`` empty and must
stay that way.  This script writes a *separate* editorial layer keyed by
ordinal, so the frozen curriculum file is never rewritten by a language model.

Every entry is glossed in the context of its own lesson, with the printed
dictionary entry (which carries the article, genitive and principal parts) in
front of the model, so a noun's gender and a verb's aspect stem inform the
Chinese wording.  Proper names follow the project's translation glossary rather
than a transliteration invented per batch.

The cache is written after each batch, so an interrupted run resumes.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import original_reader_llm as llm


ROOT = Path(__file__).resolve().parents[1]
VOCAB = ROOT / "data" / "originalReaders" / "vocabulary" / "greek-1000.json"
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
OUTPUT = CACHE / "greek-1000-gloss-zh-reviewed.json"

BATCH_SIZE = 20
JSON_RE = re.compile(r"\{.*\}", re.S)
GREEK_RE = re.compile(r"[Ͱ-Ͽἀ-῿]")
LATIN_RE = re.compile(r"[A-Za-z]")

PROMPT = """你是新約希臘文詞典的繁體中文編輯。下面是 William D. Mounce《Basics of Biblical Greek Grammar》\
課程詞表第 {lesson} 課（{lesson_label}）的 {count} 筆詞條，請逐筆給出精準的繁體中文詞義。

規則：
1. 只回傳一個 JSON 物件，格式為 {{"items":[{{"ordinal":1,"glossZh":"……"}}]}}。
2. 筆數、ordinal 與輸入完全相同，順序不變，不得遺漏或增加。
3. 依 printedEntry 判讀詞類：名詞看冠詞與屬格，動詞看主要形式，介系詞要標明所配格位\
（例如「（配所有格）從…出來」）。
4. 一般詞列主要義與必要分義，用「；」分隔，通常不超過 24 個中文字；\
不要寫成整句解釋，也不要抄英文。
5. 專有名詞（人名、地名、民族名、神名）用繁體中文聖經與教會通行譯名，\
且以下定名為準：Ἰησοῦς＝耶穌、Χριστός＝基督、Ἰωάννης＝約翰、Πέτρος＝彼得、\
Ἱεροσόλυμα／Ἰερουσαλήμ＝耶路撒冷、Γαλιλαία＝加利利、Ἰουδαῖος＝猶太人、\
Κλήμης＝革利免、Ἰουστῖνος＝猶斯定。若該詞同時有普通義，兩義都列。
6. 不要輸出希臘字母，不要輸出英文，不要輸出 Strong 編號，不要在 JSON 之外寫任何字。

輸入：
{payload}
"""


def load_entries() -> list[dict]:
    entries = json.loads(VOCAB.read_text(encoding="utf-8"))
    if len(entries) != 1000:
        raise ValueError(f"詞彙主檔應有 1000 詞，實得 {len(entries)}")
    missing = [item for item in entries if "lesson" not in item]
    if missing:
        raise ValueError("詞彙主檔尚未分課，先跑 scripts/assign_greek_lessons.py --write")
    return entries


def load_cache() -> dict[str, dict]:
    if OUTPUT.exists():
        payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
        return {str(key): value for key, value in payload.get("glosses", {}).items()}
    return {}


def save_cache(glosses: dict[str, dict]) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(
            {
                "schemaVersion": "1.0.0",
                "language": "New Testament Greek",
                "languageCode": "grc",
                "note": (
                    "greek-1000.json 的繁體中文詞義編輯層；主檔的 glossZh 一律留空，"
                    "以免課程次序被語言模型改寫。"
                ),
                "engine": llm.current_model(),
                "count": len(glosses),
                "glosses": dict(sorted(glosses.items(), key=lambda pair: int(pair[0]))),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def validate(gloss: str, entry: dict) -> str | None:
    if not gloss.strip():
        return "空白"
    if GREEK_RE.search(gloss):
        return "含希臘字母"
    if LATIN_RE.search(gloss):
        return "含拉丁字母"
    if len(gloss) > 40:
        return f"過長（{len(gloss)} 字）"
    return None


def gloss_batch(batch: list[dict]) -> dict[str, str]:
    payload = json.dumps(
        [
            {
                "ordinal": item["ordinal"],
                "printedEntry": item["printedEntry"],
                "transliteration": item.get("textbookTransliteration", ""),
                "glossEn": item.get("glossEn", ""),
                "isProperName": item.get("isProperName", False),
            }
            for item in batch
        ],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    prompt = PROMPT.format(
        lesson=batch[0]["lesson"],
        lesson_label=batch[0].get("lessonLabel", ""),
        count=len(batch),
        payload=payload,
    )
    raw = llm.call_model(prompt, max_tokens=4000)
    match = JSON_RE.search(raw)
    if not match:
        raise ValueError(f"回應不是 JSON：{raw[:200]!r}")
    items = json.loads(match.group(0)).get("items", [])
    answers = {str(item.get("ordinal")): str(item.get("glossZh", "")).strip() for item in items}
    expected = {str(item["ordinal"]) for item in batch}
    if set(answers) != expected:
        raise ValueError(f"ordinal 不符：缺 {sorted(expected - set(answers))}")
    return answers


def main() -> None:
    parser = argparse.ArgumentParser(description="建立希臘文 1000 詞繁體中文詞義層")
    parser.add_argument("--model", choices=sorted(llm.MODEL_CHAINS), default="sonnet")
    parser.add_argument("--limit", type=int, default=0, help="只跑前 N 批（0＝全部）")
    args = parser.parse_args()

    llm.select_chain(args.model)
    entries = load_entries()
    glosses = load_cache()
    pending = [item for item in entries if str(item["ordinal"]) not in glosses]
    print(f"已完成 {len(glosses)}／1000；待補 {len(pending)}", flush=True)
    if not pending:
        print("全部完成。")
        return

    # Batch inside one lesson so the model always sees a coherent vocabulary set.
    batches: list[list[dict]] = []
    by_lesson: dict[int, list[dict]] = {}
    for item in pending:
        by_lesson.setdefault(item["lesson"], []).append(item)
    for lesson in sorted(by_lesson):
        items = by_lesson[lesson]
        for start in range(0, len(items), BATCH_SIZE):
            batches.append(items[start : start + BATCH_SIZE])
    if args.limit:
        batches = batches[: args.limit]

    rejected = 0
    for index, batch in enumerate(batches, start=1):
        lesson = batch[0]["lesson"]
        try:
            answers = gloss_batch(batch)
        except Exception as error:  # noqa: BLE001 - a failed batch is retried next run
            print(f"  第 {index}/{len(batches)} 批（第 {lesson} 課）失敗：{error}", flush=True)
            continue
        accepted = 0
        for item in batch:
            gloss = answers[str(item["ordinal"])]
            problem = validate(gloss, item)
            if problem:
                rejected += 1
                print(f"    退回 #{item['ordinal']} {item['printedEntry']}：{problem}", flush=True)
                continue
            glosses[str(item["ordinal"])] = {
                "glossZh": gloss,
                "lesson": item["lesson"],
                "printedEntry": item["printedEntry"],
                "engine": llm.current_model(),
            }
            accepted += 1
        save_cache(glosses)
        print(
            f"  第 {index}/{len(batches)} 批（第 {lesson} 課）收 {accepted}/{len(batch)}；"
            f"累計 {len(glosses)}／1000",
            flush=True,
        )

    print(f"結束：{len(glosses)}／1000 完成，本輪退回 {rejected} 筆")


if __name__ == "__main__":
    main()
