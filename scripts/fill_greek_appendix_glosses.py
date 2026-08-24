#!/usr/bin/env python3
"""補齊四張策展附錄的繁體中文詞義。

專名附錄的中文另有來源（詞庫、信望愛、中文聖經對位），由
``fill_greek_appendix_names.py`` 與 ``align_greek_names_chinese.py`` 處理，本檔
不碰它。這裡管的是數字與度量衡、親屬稱謂、曆法與節期、教會職分與禮儀用語這四張
策展表。

順序有意義：**課文詞義優先**。這四張表是課程的交叉索引，同一個詞若已經在某一課
教過，附錄就該印那一課教的譯法，否則同一個 εἷς 在讀本裡會有兩個說法。查不到的才
交給語言模型，並記下 ``zhSource`` 供覆核。
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
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
APPENDICES = ROOT / "data" / "originalReaders" / "vocabulary" / "greek-appendices.json"
GLOSSES = CACHE / "greek-2000-gloss-zh-by-lemma.json"

NAME_APPENDIX = "人名、地名與國族"
BATCH_SIZE = 20
JSON_RE = re.compile(r"\{.*\}", re.S)
GREEK_RE = re.compile(r"[Ͱ-Ͽἀ-῿]")
LATIN_RE = re.compile(r"[A-Za-z]")

PROMPT = """你是通用希臘文（Koine）詞典的繁體中文編輯。下面是讀本附錄《{title}》的 {count} 筆詞條，請逐筆給出精準的繁體中文詞義。

規則：
1. 只回傳一個 JSON 物件，格式為 {{"items":[{{"key":"...","zh":"……"}}]}}。
2. 筆數與 key 與輸入完全相同，順序不變，不得遺漏或增加；key 原樣抄回。
3. 詞義以通用希臘文與教會希臘文的用法為準，不要給古典希臘文才有的義項。
4. 本表是《{title}》，請給該範疇下的意思：{focus}
5. 一般以 2–12 個中文字為度，必要時用「；」分列兩義；不要寫成整句解釋。
6. 教會專門詞用教會通行的繁體中文術語（例如職分、禮儀、節期的固定譯名）。
7. 不要輸出希臘字母，不要輸出英文，不要在 JSON 之外寫任何字。

輸入：
{payload}
"""

FOCUS = {
    "數字與度量衡": "基數、序數、倍數、幣制、長度與容量單位。",
    "親屬稱謂": "血親、姻親與家族內的稱呼。",
    "曆月與節期": "月份、節期、時辰與曆法用語。",
    "曆法與節期": "月份、節期、時辰與曆法用語。",
    "教會職分與禮儀用語": "聖職與職分名稱、禮儀行動、禮儀器物與頌詞名目。",
}


def load_glosses() -> dict[str, str]:
    if not GLOSSES.exists():
        raise FileNotFoundError(
            f"缺少詞義層：{GLOSSES}；先跑 build_greek_vocab_glosses_2000.py --write"
        )
    payload = json.loads(GLOSSES.read_text(encoding="utf-8"))
    return {
        lemma: record.get("glossZh", "")
        for lemma, record in payload["glosses"].items()
        if record.get("glossZh", "").strip()
    }


def validate(text: str) -> str | None:
    if not text.strip():
        return "空白"
    if GREEK_RE.search(text):
        return "含希臘字母"
    if LATIN_RE.search(text):
        return "含拉丁字母"
    if len(text) > 30:
        return f"過長（{len(text)} 字）"
    return None


def gloss_batch(title: str, batch: list[dict]) -> dict[str, str]:
    payload = json.dumps(
        [{"key": item["lemma"], "group": item.get("group", "")} for item in batch],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    prompt = PROMPT.format(
        title=title,
        focus=FOCUS.get(title, "該表所屬範疇的意思。"),
        count=len(batch),
        payload=payload,
    )
    raw = llm.call_model(prompt, max_tokens=3000)
    match = JSON_RE.search(raw)
    if not match:
        raise ValueError(f"回應不是 JSON：{raw[:160]!r}")
    answers = {
        str(item.get("key")): str(item.get("zh", "")).strip()
        for item in json.loads(match.group(0)).get("items", [])
    }
    expected = {item["lemma"] for item in batch}
    if set(answers) != expected:
        raise ValueError(f"詞條不符：缺 {len(expected - set(answers))} 筆")
    return answers


def main() -> None:
    parser = argparse.ArgumentParser(description="補齊策展附錄的繁體中文詞義")
    parser.add_argument("--write", action="store_true", help="寫回 greek-appendices.json")
    parser.add_argument("--model", choices=sorted(llm.MODEL_CHAINS), default="auto")
    parser.add_argument("--lesson-only", action="store_true", help="只從課文詞義層搬，不叫模型")
    args = parser.parse_args()

    llm.select_chain(args.model)
    payload = json.loads(APPENDICES.read_text(encoding="utf-8"))
    lesson_glosses = load_glosses()

    from_lessons = 0
    from_model = 0
    rejected = 0

    for table in payload["appendices"]:
        title = table["title"]
        if title == NAME_APPENDIX:
            continue
        pending: list[dict] = []
        for entry in table["entries"]:
            if entry.get("zh", "").strip():
                continue
            gloss = lesson_glosses.get(entry["lemma"], "")
            if gloss:
                entry["zh"] = gloss
                entry["zhSource"] = "課文詞義層（greek-2000-gloss-zh-by-lemma）"
                from_lessons += 1
                continue
            pending.append(entry)
        print(f"  {title}：課文補 {len(table['entries']) - len(pending)} 筆，待補 {len(pending)} 筆")

        if args.lesson_only or not pending:
            continue
        for start in range(0, len(pending), BATCH_SIZE):
            batch = pending[start : start + BATCH_SIZE]
            try:
                answers = gloss_batch(title, batch)
            except Exception as error:  # noqa: BLE001
                print(f"    第 {start // BATCH_SIZE + 1} 批失敗：{error}", flush=True)
                continue
            for entry in batch:
                text = answers[entry["lemma"]]
                problem = validate(text)
                if problem:
                    rejected += 1
                    print(f"    退回 {entry['lemma']}：{problem}", flush=True)
                    continue
                entry["zh"] = text
                entry["zhSource"] = f"語言模型（{llm.current_model()}），待人工複核"
                from_model += 1

    remaining = sum(
        1
        for table in payload["appendices"]
        if table["title"] != NAME_APPENDIX
        for entry in table["entries"]
        if not entry.get("zh", "").strip()
    )
    print(f"  課文沿用 {from_lessons} 筆、模型補 {from_model} 筆、退回 {rejected} 筆、仍缺 {remaining} 筆")

    if args.write:
        APPENDICES.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已寫回 {APPENDICES}")
    else:
        print("（未寫檔；加 --write 才會輸出）")


if __name__ == "__main__":
    main()
