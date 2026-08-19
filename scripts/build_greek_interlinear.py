#!/usr/bin/env python3
"""Build the word-by-word Traditional-Chinese layer for the Greek reader.

Every running-text unit gets one Chinese gloss per printed Greek word: the 25
Scripture chapters, the 100 memory verses, the 25 patristic readings and the
332 steps of the liturgy — about fifty thousand words in all.  A reading whose
Chinese is a single whole-verse rendering is not what this reader promises; the
learner needs to see which Greek word carries which meaning.

Three things make a run of this size survivable:

* the unit is the unit of work and of caching, so a stopped run resumes from
  wherever it got to rather than starting over;
* the gloss count must equal the token count, and a unit that comes back short
  is split and retried rather than accepted, because a model asked for thirty
  glosses will happily return twenty-eight;
* nothing is written unless it passes — no Greek left in a Chinese gloss, no
  Latin, no blanks.

Tokenisation follows the *printed* text, so the gloss row always lines up with
the row of Greek the reader actually shows.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import original_reader_llm as llm


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
SCRIPTURE_PLAN = CACHE / "scripture-plan.json"
PATRISTIC_PLAN = CACHE / "patristic-plan.json"
LITURGY = CACHE / "liturgy-chrysostom.json"
MEMORY = CACHE / "memory-verses.json"
OUTPUT = CACHE / "interlinear.json"

GREEK_RE = re.compile(r"[Ͱ-Ͽἀ-῿]")
LATIN_RE = re.compile(r"[A-Za-z]")
JSON_RE = re.compile(r"\{.*\}", re.S)
# Punctuation rides along with a word and is never glossed on its own.
TRAILING_RE = re.compile(r"^(?P<word>.*?)(?P<trailing>[·,.;:!?»\)\]]*)$")

WINDOW = 24

PROMPT = """你是新約希臘文的逐詞對譯編輯。下面是一個單元裡連續 {count} 個希臘文詞，\
請逐詞給出「在這個上下文裡」的繁體中文詞義。

單元出處：{ref}
單元全文（供判讀上下文，不必逐句翻譯）：
{context}

要逐詞對譯的詞（第 {start} 到第 {end} 個）：
{words}

規則：
1. 只回傳一個 JSON 物件，格式為 {{"glosses":[{{"index":1,"zh":"……"}}]}}。
2. 筆數與 index 必須與輸入完全相同，順序不變，不得遺漏或增加。
3. 每個詞給 1–6 個中文字的脈絡義；冠詞、連接詞、質詞也要給（例如 ὁ＝那、\
δέ＝而、γάρ＝因為），不可留空。
4. 動詞給該處的實際意思，不必標時態；介系詞依所配格位給義。
5. 專有名詞用繁體中文聖經與教會通行譯名。
6. 不要輸出希臘字母、不要輸出英文、不要在 JSON 之外寫任何字。
"""

WHOLE_PROMPT = """把下面這段希臘文譯成通順的繁體中文，只回傳譯文本身，不要加說明。

出處：{ref}
原文：
{text}
"""


def tokenise(text: str) -> list[dict]:
    """Split the printed text into the words the reader will see."""
    tokens = []
    for piece in unicodedata.normalize("NFC", text).split():
        match = TRAILING_RE.match(piece)
        word = match.group("word") if match else piece
        trailing = match.group("trailing") if match else ""
        if not GREEK_RE.search(word):
            # Editorial brackets and stray punctuation are not glossed, but they
            # stay in the row so the printed line is reproduced exactly.
            tokens.append({"word": piece, "trailing": "", "glossable": False})
            continue
        tokens.append({"word": word, "trailing": trailing, "glossable": True})
    return tokens


def units() -> list[dict]:
    """Every running-text unit the reader prints, in one flat list."""
    rows: list[dict] = []

    scripture = json.loads(SCRIPTURE_PLAN.read_text(encoding="utf-8"))
    for chapter in scripture["chapters"]:
        for verse in chapter["verses"]:
            rows.append(
                {
                    "id": f"scripture:{verse['ref']}",
                    "group": "scripture",
                    "ref": verse["ref"],
                    "text": verse["displayText"],
                    "needsWholeTranslation": chapter["corpus"] == "pseudepigrapha",
                }
            )

    memory = json.loads(MEMORY.read_text(encoding="utf-8"))
    for verse in memory["verses"]:
        rows.append(
            {
                "id": f"memory:{verse['ref']}",
                "group": "memory",
                "ref": verse["ref"],
                "text": verse["text"],
                "needsWholeTranslation": verse["corpus"] == "pseudepigrapha",
            }
        )

    patristic = json.loads(PATRISTIC_PLAN.read_text(encoding="utf-8"))
    for reading in patristic["readings"]:
        for segment in reading["segments"]:
            rows.append(
                {
                    "id": f"patristic:{reading['ordinal']}:{segment['ref']}",
                    "group": "patristic",
                    "ref": f"{reading['titleZh']} {segment['ref']}",
                    "text": segment["displayText"],
                    # None of these has a published Chinese translation, so each
                    # segment needs a whole-segment rendering as well.
                    "needsWholeTranslation": True,
                }
            )

    liturgy = json.loads(LITURGY.read_text(encoding="utf-8"))
    for step in liturgy["steps"]:
        rows.append(
            {
                "id": f"liturgy:{step['ordinal']}",
                "group": "liturgy",
                "ref": f"{step['sectionLabel']} 第 {step['ordinal']} 段",
                "text": step["displayText"],
                "needsWholeTranslation": True,
            }
        )

    # The same verse can be both a chapter verse and a memory verse; gloss once.
    seen: set[str] = set()
    unique = []
    for row in rows:
        key = row["text"]
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique


def load_cache() -> dict[str, dict]:
    if OUTPUT.exists():
        return json.loads(OUTPUT.read_text(encoding="utf-8")).get("units", {})
    return {}


def save_cache(cache: dict[str, dict]) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(
            {
                "schemaVersion": "1.0.0",
                "language": "New Testament Greek",
                "languageCode": "grc",
                "engine": llm.current_model(),
                "count": len(cache),
                "units": cache,
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
    if len(gloss) > 12:
        return f"過長（{len(gloss)} 字）"
    return None


def gloss_window(unit: dict, tokens: list[dict], start: int, end: int) -> dict[int, str]:
    words = "\n".join(
        f"{index + 1}. {tokens[index]['word']}" for index in range(start, end)
    )
    prompt = PROMPT.format(
        count=end - start,
        ref=unit["ref"],
        context=unit["text"][:1200],
        start=start + 1,
        end=end,
        words=words,
    )
    raw = llm.call_model(prompt, max_tokens=3000)
    match = JSON_RE.search(raw)
    if not match:
        raise ValueError(f"回應不是 JSON：{raw[:160]!r}")
    answers = {
        int(item["index"]): str(item.get("zh", "")).strip()
        for item in json.loads(match.group(0)).get("glosses", [])
        if str(item.get("index", "")).strip().isdigit()
    }
    expected = set(range(start + 1, end + 1))
    if set(answers) != expected:
        raise ValueError(f"index 不符：缺 {sorted(expected - set(answers))}")
    return answers


def gloss_unit(unit: dict) -> dict:
    tokens = tokenise(unit["text"])
    glossable = [index for index, token in enumerate(tokens) if token["glossable"]]
    answers: dict[int, str] = {}

    # A long unit is asked for in windows: a model given forty words at once
    # starts losing count, and a miscounted row is worse than a slow one.
    position = 0
    while position < len(glossable):
        window = glossable[position : position + WINDOW]
        start, end = window[0], window[-1] + 1
        try:
            answers.update(gloss_window(unit, tokens, start, end))
            position += len(window)
        except ValueError:
            if len(window) <= 4:
                raise
            half = len(window) // 2
            answers.update(gloss_window(unit, tokens, window[0], window[half - 1] + 1))
            position += half

    rows = []
    for index, token in enumerate(tokens):
        gloss = answers.get(index + 1, "") if token["glossable"] else ""
        if token["glossable"]:
            problem = validate(gloss)
            if problem:
                raise ValueError(f"{unit['ref']} 第 {index + 1} 詞：{problem}")
        rows.append({"word": token["word"], "trailing": token["trailing"], "glossZh": gloss})

    result = {"ref": unit["ref"], "group": unit["group"], "tokens": rows, "engine": llm.current_model()}
    if unit["needsWholeTranslation"]:
        whole = llm.call_model(
            WHOLE_PROMPT.format(ref=unit["ref"], text=unit["text"]), max_tokens=1500
        ).strip()
        if GREEK_RE.search(whole) or not whole:
            raise ValueError(f"{unit['ref']}：整段中譯不合格")
        result["translationZh"] = whole
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="建立希臘文讀本逐詞對譯層")
    parser.add_argument("--model", choices=sorted(llm.MODEL_CHAINS), default="sonnet")
    parser.add_argument("--group", choices=("scripture", "memory", "patristic", "liturgy"))
    parser.add_argument("--limit", type=int, default=0, help="只跑前 N 個單元（0＝全部）")
    args = parser.parse_args()

    llm.select_chain(args.model)
    cache = load_cache()
    all_units = units()
    pending = [unit for unit in all_units if unit["id"] not in cache]
    if args.group:
        pending = [unit for unit in pending if unit["group"] == args.group]
    if args.limit:
        pending = pending[: args.limit]

    total_tokens = sum(
        sum(1 for token in tokenise(unit["text"]) if token["glossable"]) for unit in all_units
    )
    print(f"單元 {len(all_units)} 個、可對譯詞 {total_tokens} 個；已完成 {len(cache)}，待補 {len(pending)}")

    done = failed = 0
    for index, unit in enumerate(pending, start=1):
        try:
            cache[unit["id"]] = gloss_unit(unit)
        except Exception as error:  # noqa: BLE001 - retried on the next run
            failed += 1
            print(f"  ✗ {index}/{len(pending)} {unit['ref']}：{error}", flush=True)
            continue
        done += 1
        save_cache(cache)
        if done % 10 == 0 or index == len(pending):
            print(f"  {index}/{len(pending)} 完成，累計 {len(cache)}／{len(all_units)}", flush=True)

    print(f"結束：完成 {done}，失敗 {failed}，累計 {len(cache)}／{len(all_units)}")


if __name__ == "__main__":
    main()
