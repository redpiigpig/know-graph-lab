#!/usr/bin/env python3
"""繁體中文詞義層：兩冊制兩千詞（greek-2000.json）。

主檔 ``greek-2000.json`` 只管次序、課次與詞形，``glossZh`` 一律留空；中文詞義
另存一層，**以 lemma 為鍵**。交接文件已經記過這個教訓：專名抽到附錄之後整份
詞表重新編號，用序號當鍵的詞義層會整批錯開一位而且不會報錯。

舊的一千詞詞義層（``greek-1000-gloss-zh-reviewed.json``，以序號為鍵）先按 lemma
搬過來，能對上的直接沿用已審過的譯法，其餘才交給語言模型。引擎順序照全案標準
Gemini → NVIDIA → Haiku，由 ``original_reader_llm`` 決定。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import original_reader_llm as llm
from verify_greek_vocab_lexicon import clean_gloss, load_dodson


ROOT = Path(__file__).resolve().parents[1]
VOCAB = ROOT / "data" / "originalReaders" / "vocabulary" / "greek-2000.json"
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
LEGACY = CACHE / "greek-1000-gloss-zh-reviewed.json"
LEGACY_VOCAB = ROOT / "data" / "originalReaders" / "vocabulary" / "greek-1000.json"
OUTPUT = CACHE / "greek-2000-gloss-zh-by-lemma.json"

BATCH_SIZE = 20
UNPRODUCTIVE_PASS_LIMIT = 3
JSON_RE = re.compile(r"\{.*\}", re.S)
GREEK_RE = re.compile(r"[Ͱ-Ͽἀ-῿]")
LATIN_RE = re.compile(r"[A-Za-z]")

CORPUS_LABEL = {
    "new-testament": "新約希臘文（Mounce《Basics of Biblical Greek Grammar》課程詞表）",
    "septuagint": "七十士譯本希臘文（Swete 1909–1930 版詞頻）",
    "patristic": "教父文獻與希臘教會文獻（使徒教父、First1KGreek、信經、金口若望禮儀）",
}

PROMPT = """你是通用希臘文（Koine）詞典的繁體中文編輯。下面是《{corpus}》第 {lesson} 課的 {count} 筆詞條，請逐筆給出精準的繁體中文詞義。

規則：
1. 只回傳一個 JSON 物件，格式為 {{"items":[{{"key":"...","glossZh":"……"}}]}}。
2. 筆數與 key 與輸入完全相同，順序不變，不得遺漏或增加；key 原樣抄回。
3. 依 printedEntry 判讀詞類：名詞看冠詞與屬格，動詞看主要形式，介系詞要標明所配格位（例如「（配所有格）從…出來」）。
4. 一般詞列主要義與必要分義，用「；」分隔，通常不超過 24 個中文字；不要寫成整句解釋，也不要抄英文。
5. 詞義以通用希臘文的用法為準，不要給古典希臘文才有的義項；教會文獻專門詞（如禮儀、職分、教義用語）用教會通行的繁體中文術語。
6. 專有名詞（人名、地名、民族名、神名）用繁體中文聖經與教會通行譯名，且以下定名為準：Ἰησοῦς＝耶穌、Χριστός＝基督、Ἰωάννης＝約翰、Πέτρος＝彼得、Ἱεροσόλυμα／Ἰερουσαλήμ＝耶路撒冷、Γαλιλαία＝加利利、Ἰουδαῖος＝猶太人、Κλήμης＝革利免、Ἰουστῖνος＝猶斯定。若該詞同時有普通義，兩義都列。
7. 不要輸出希臘字母，不要輸出英文，不要輸出 Strong 編號，不要在 JSON 之外寫任何字。

輸入：
{payload}
"""


def load_entries() -> list[dict]:
    payload = json.loads(VOCAB.read_text(encoding="utf-8"))
    entries = payload["entries"]
    if len(entries) != 2000:
        raise ValueError(f"詞彙主檔應有 2000 詞，實得 {len(entries)}")
    missing = [item for item in entries if not item.get("lesson")]
    if missing:
        raise ValueError(f"{len(missing)} 筆尚未分課，先跑 build_greek_vocabulary_2000.py --write")
    return entries


def load_cache() -> dict[str, dict]:
    if OUTPUT.exists():
        payload = json.loads(OUTPUT.read_text(encoding="utf-8"))
        return dict(payload.get("glosses", {}))
    return {}


def legacy_by_lemma() -> dict[str, dict]:
    """已審過的一千詞詞義，改用 lemma 當鍵。"""
    if not (LEGACY.exists() and LEGACY_VOCAB.exists()):
        return {}
    old = json.loads(LEGACY_VOCAB.read_text(encoding="utf-8"))
    layer = json.loads(LEGACY.read_text(encoding="utf-8")).get("glosses", {})
    out: dict[str, dict] = {}
    for entry in old:
        record = layer.get(str(entry["ordinal"]))
        if not record or not record.get("glossZh", "").strip():
            continue
        out[entry["lemma"]] = {
            "glossZh": record["glossZh"],
            "printedEntry": entry.get("printedEntry", ""),
            "engine": record.get("engine", ""),
            "source": "greek-1000-gloss-zh-reviewed",
        }
    return out


def save_cache(glosses: dict[str, dict]) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(
            {
                "schemaVersion": "2.0.0",
                "language": "Koine Greek",
                "languageCode": "grc",
                "note": (
                    "greek-2000.json 的繁體中文詞義編輯層，以 lemma 為鍵。"
                    "主檔的 glossZh 一律留空，以免課程次序被語言模型改寫；"
                    "用序號當鍵會在專名抽出附錄後整批錯開一位，故不採用。"
                ),
                "engine": llm.current_model(),
                "count": len(glosses),
                "glosses": dict(sorted(glosses.items())),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def validate(gloss: str) -> str | None:
    if not gloss.strip():
        return "空白"
    if GREEK_RE.search(gloss):
        return "含希臘字母"
    if LATIN_RE.search(gloss):
        return "含拉丁字母"
    if len(gloss) > 40:
        return f"過長（{len(gloss)} 字）"
    return None


_dodson_by_number: dict[str, dict] = {}


def dodson_brief(strong: str) -> str:
    global _dodson_by_number
    if not strong:
        return ""
    if not _dodson_by_number:
        for matches in load_dodson().values():
            for number, entry in matches:
                _dodson_by_number.setdefault(number, entry)
    entry = _dodson_by_number.get(strong)
    return clean_gloss(entry) if entry else ""


def gloss_batch(batch: list[dict]) -> dict[str, str]:
    payload = json.dumps(
        [
            {
                "key": item["lemma"],
                "printedEntry": item.get("printedEntry") or item["lemma"],
                "transliteration": item.get("textbookTransliteration", ""),
                "glossEn": dodson_brief(item.get("strong", "")) or item.get("glossEn", ""),
                "frequency": item.get("frequency", 0),
            }
            for item in batch
        ],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    prompt = PROMPT.format(
        corpus=CORPUS_LABEL.get(batch[0]["corpus"], batch[0]["corpus"]),
        lesson=batch[0]["lesson"],
        count=len(batch),
        payload=payload,
    )
    raw = llm.call_model(prompt, max_tokens=4000)
    match = JSON_RE.search(raw)
    if not match:
        raise ValueError(f"回應不是 JSON：{raw[:200]!r}")
    items = json.loads(match.group(0)).get("items", [])
    answers = {str(item.get("key")): str(item.get("glossZh", "")).strip() for item in items}
    expected = {item["lemma"] for item in batch}
    if set(answers) != expected:
        raise ValueError(f"詞條不符：缺 {len(expected - set(answers))} 筆")
    return answers


def main() -> None:
    parser = argparse.ArgumentParser(description="建立希臘文兩千詞繁體中文詞義層")
    parser.add_argument("--model", choices=sorted(llm.MODEL_CHAINS), default="auto")
    parser.add_argument("--limit", type=int, default=0, help="只跑前 N 批（0＝全部）")
    parser.add_argument("--no-legacy", action="store_true", help="不從舊詞義層搬")
    args = parser.parse_args()

    llm.select_chain(args.model)
    entries = load_entries()
    glosses = load_cache()

    if not args.no_legacy:
        legacy = legacy_by_lemma()
        moved = 0
        for item in entries:
            if item["lemma"] in glosses:
                continue
            record = legacy.get(item["lemma"])
            if not record:
                continue
            glosses[item["lemma"]] = {
                **record,
                "lesson": item["lesson"],
                "volume": item["volume"],
                "printedEntry": item.get("printedEntry") or item["lemma"],
            }
            moved += 1
        if moved:
            save_cache(glosses)
            print(f"從已審過的一千詞詞義層沿用 {moved} 筆", flush=True)

    pending = [item for item in entries if item["lemma"] not in glosses]
    print(f"已完成 {len(glosses)}／2000；待補 {len(pending)}", flush=True)
    if not pending:
        print("全部完成。")
        return

    batches: list[list[dict]] = []
    by_lesson: dict[tuple[int, int], list[dict]] = {}
    for item in pending:
        by_lesson.setdefault((item["volume"], item["lesson"]), []).append(item)
    for key in sorted(by_lesson):
        items = by_lesson[key]
        for start in range(0, len(items), BATCH_SIZE):
            batches.append(items[start : start + BATCH_SIZE])
    if args.limit:
        batches = batches[: args.limit]

    rejected = 0
    queue = list(batches)
    total = len(batches)
    unproductive_passes = 0
    while queue and unproductive_passes < UNPRODUCTIVE_PASS_LIMIT:
        requeued: list[list[dict]] = []
        progressed = False
        for index, batch in enumerate(queue, start=1):
            head = batch[0]
            label = f"第 {head['volume']} 冊第 {head['lesson']} 課"
            try:
                answers = gloss_batch(batch)
            except Exception as error:  # noqa: BLE001 - 重排隊，不丟掉
                print(f"  第 {index}/{len(queue)} 批（{label}）失敗，改排隊重試：{error}", flush=True)
                requeued.append(batch)
                continue
            progressed = True
            accepted = 0
            for item in batch:
                gloss = answers[item["lemma"]]
                problem = validate(gloss)
                if problem:
                    rejected += 1
                    print(f"    退回 {item['printedEntry']}：{problem}", flush=True)
                    continue
                glosses[item["lemma"]] = {
                    "glossZh": gloss,
                    "lesson": item["lesson"],
                    "volume": item["volume"],
                    "printedEntry": item.get("printedEntry") or item["lemma"],
                    "engine": llm.current_model(),
                    "source": "llm",
                }
                accepted += 1
            save_cache(glosses)
            print(
                f"  第 {index}/{len(queue)} 批（{label}）收 {accepted}/{len(batch)}；"
                f"累計 {len(glosses)}／2000",
                flush=True,
            )

        queue = requeued
        unproductive_passes = 0 if progressed else unproductive_passes + 1
        if queue:
            print(
                f"  本輪結束，剩 {len(queue)}/{total} 批待補"
                f"（連續 {unproductive_passes} 輪無進度）",
                flush=True,
            )

    if queue:
        print(f"停在剩 {len(queue)} 批：額度連續 {UNPRODUCTIVE_PASS_LIMIT} 輪都沒放出來，改天再跑即可續傳")
    print(f"結束：{len(glosses)}／2000 完成，本輪退回 {rejected} 筆")


if __name__ == "__main__":
    main()
