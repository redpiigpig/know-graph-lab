#!/usr/bin/env python3
"""Build the word-by-word Traditional-Chinese layer for the Latin reader.

Hebrew has one (1,091 units) and Greek has one (4,543 units); Latin shipped
without one, so its lessons print the Latin and a whole-line Chinese beneath
and never show which Latin word carries which meaning. That is the one layer
the release contract requires and this reader does not have.

Unlike the Greek builder, which gathers its units from five separate plan
files, this one reads the assembled master. Every line the book prints is
already there as a ``{latin, zh}`` row — lesson readings, memory units and the
terminal Mass — so the gloss row is guaranteed to line up with the row of Latin
the reader actually shows, and a renumbered lesson cannot silently pair a gloss
row with someone else's text.

Three things make a run of this size survivable, all borrowed from the Greek
builder because they were learned the hard way there:

* the unit is the unit of work and of caching, so a stopped run resumes;
* gloss count must equal token count, and a short answer is re-asked in halves
  rather than accepted — a model given forty words will return thirty-eight;
* nothing is written unless it passes: no Latin letters left in a Chinese
  gloss, no blanks, nothing over twelve characters.

    python -X utf8 scripts/build_latin_interlinear.py --workers 6
    python -X utf8 scripts/build_latin_interlinear.py --group memory --limit 20
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import threading
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import original_reader_llm as llm

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
MASTER = CACHE / "latin-reader-two-volumes.json"
OUTPUT = CACHE / "interlinear.json"

LATIN_RE = re.compile(r"[A-Za-zĀ-ſ]")
JSON_RE = re.compile(r"\{.*\}", re.S)
TRAILING_RE = re.compile(r"^(?P<word>.*?)(?P<trailing>[,.;:!?»\)\]]*)$")
# V. and R. mark who says the line; they are printed but they are not words.
RUBRIC_RE = re.compile(r"^[VR]\.$")

WINDOW = 24
UNPRODUCTIVE_PASS_LIMIT = 3

PROMPT = """你是教會拉丁文的逐詞對譯編輯。下面是一個單元裡連續 {count} 個拉丁文詞，\
請逐詞給出「在這個上下文裡」的繁體中文詞義。

單元出處：{ref}
單元全文（供判讀上下文，不必逐句翻譯）：
{context}

要逐詞對譯的詞（第 {start} 到第 {end} 個）：
{words}

規則：
1. 只回傳一個 JSON 物件，格式為 {{"glosses":[{{"index":1,"zh":"……"}}]}}。
2. 筆數與 index 必須與輸入完全相同，順序不變，不得遺漏或增加。
3. 每個詞給 1–6 個中文字的脈絡義；連接詞、質詞、介系詞也要給\
（例如 et＝和、autem＝而、enim＝因為、in＝在），不可留空。
4. 動詞給該處的實際意思，不必標時態；介系詞依所配格位給義。
5. 專有名詞用思高譯本的譯名（若望、瑪利亞、伯多祿、聖神），不要用新教譯名。
6. 不要輸出拉丁字母、不要輸出英文、不要在 JSON 之外寫任何字。
"""


def tokenise(text: str) -> list[dict]:
    """Split the printed line into the words the reader will see."""

    tokens = []
    for piece in unicodedata.normalize("NFC", text).split():
        match = TRAILING_RE.match(piece)
        word = match.group("word") if match else piece
        trailing = match.group("trailing") if match else ""
        glossable = bool(LATIN_RE.search(word)) and not RUBRIC_RE.match(piece)
        if not glossable:
            tokens.append({"word": piece, "trailing": "", "glossable": False})
            continue
        tokens.append({"word": word, "trailing": trailing, "glossable": True})
    return tokens


def units() -> list[dict]:
    """Every printed Latin line in the book, in one flat list."""

    master = json.loads(MASTER.read_text(encoding="utf-8"))
    rows: list[dict] = []
    for volume in master["volumes"]:
        for lesson in volume["lessons"]:
            key = f"v{volume['volume']}-{lesson['lesson']}"
            for index, row in enumerate(lesson["reading"], start=1):
                rows.append(
                    {
                        "id": f"reading:{key}:{index}",
                        "group": "reading",
                        "ref": f"{volume['name']}第 {lesson['lesson']} 課・{lesson['title']} 第 {index} 段",
                        "text": row["latin"],
                    }
                )
            for index, unit in enumerate(lesson["memoryUnits"], start=1):
                rows.append(
                    {
                        "id": f"memory:{key}:{index}",
                        "group": "memory",
                        "ref": f"{volume['name']}第 {lesson['lesson']} 課・{unit.get('ref', '')}",
                        "text": unit["text"],
                    }
                )
    for index, segment in enumerate(master["terminal"]["segments"], start=1):
        rows.append(
            {
                "id": f"terminal:{index}",
                "group": "terminal",
                "ref": f"常年期主日彌撒經文 第 {index} 段",
                "text": segment["latin"],
            }
        )
    return [row for row in rows if any(t["glossable"] for t in tokenise(row["text"]))]


def signature(text: str) -> str:
    return "".join(t["word"] + t["trailing"] for t in tokenise(text))


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
                "language": "Ecclesiastical Latin",
                "languageCode": "la",
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
    if LATIN_RE.search(gloss):
        return "含拉丁字母"
    if len(gloss) > 12:
        return f"過長（{len(gloss)} 字）"
    return None


def gloss_window(unit: dict, tokens: list[dict], start: int, end: int) -> dict[int, str]:
    words = "\n".join(f"{i + 1}. {tokens[i]['word']}" for i in range(start, end))
    raw = llm.call_model(
        PROMPT.format(
            count=end - start,
            ref=unit["ref"],
            context=unit["text"][:1200],
            start=start + 1,
            end=end,
            words=words,
        ),
        max_tokens=3000,
    )
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
    glossable = [i for i, token in enumerate(tokens) if token["glossable"]]
    answers: dict[int, str] = {}

    position = 0
    while position < len(glossable):
        window = glossable[position : position + WINDOW]
        try:
            answers.update(gloss_window(unit, tokens, window[0], window[-1] + 1))
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
    return {"ref": unit["ref"], "group": unit["group"], "tokens": rows, "engine": llm.current_model()}


def main() -> None:
    parser = argparse.ArgumentParser(description="建立教會拉丁文讀本逐詞對譯層")
    parser.add_argument("--model", choices=sorted(llm.MODEL_CHAINS), default="auto")
    parser.add_argument("--group", choices=("reading", "memory", "terminal"))
    parser.add_argument("--limit", type=int, default=0, help="只跑前 N 個單元（0＝全部）")
    parser.add_argument("--workers", type=int, default=6, help="同時處理幾個單元")
    args = parser.parse_args()

    llm.select_chain(args.model)
    cache = load_cache()
    all_rows = units()

    # A cached row is only good while the Latin under it is unchanged.
    stale = 0
    for unit in all_rows:
        record = cache.get(unit["id"])
        if record is None:
            continue
        cached = "".join(t["word"] + t["trailing"] for t in record["tokens"])
        if cached != signature(unit["text"]):
            del cache[unit["id"]]
            stale += 1
    if stale:
        print(f"原文已改，作廢舊對譯 {stale} 個單元", flush=True)

    # The liturgy repeats whole lines and 「R. Amen.」 appears dozens of times,
    # so a line whose Latin is already glossed under another id is copied
    # rather than paid for again.
    by_text = {}
    for entry in cache.values():
        by_text.setdefault("".join(t["word"] + t["trailing"] for t in entry["tokens"]), entry)
    seen: dict[str, dict] = {}
    unique: list[dict] = []
    for unit in all_rows:
        key = signature(unit["text"])
        if key in seen:
            continue
        seen[key] = unit
        unique.append(unit)

    recovered = 0
    for unit in unique:
        if unit["id"] in cache:
            continue
        source = by_text.get(signature(unit["text"]))
        if source is None:
            continue
        cache[unit["id"]] = {**source, "ref": unit["ref"], "group": unit["group"]}
        recovered += 1
    if recovered:
        save_cache(cache)
        print(f"沿用字面相同的既有對譯 {recovered} 個單元", flush=True)

    pending = [unit for unit in unique if unit["id"] not in cache]
    if args.group:
        pending = [unit for unit in pending if unit["group"] == args.group]
    if args.limit:
        pending = pending[: args.limit]

    total = sum(sum(1 for t in tokenise(u["text"]) if t["glossable"]) for u in unique)
    print(
        f"印出的行 {len(all_rows)}，去重後 {len(unique)} 個單元、可對譯詞 {total} 個；"
        f"已完成 {len(cache)}，待補 {len(pending)}",
        flush=True,
    )

    done = failed = 0
    unproductive = 0
    lock = threading.Lock()
    from concurrent.futures import ThreadPoolExecutor

    while pending and unproductive < UNPRODUCTIVE_PASS_LIMIT:
        requeued: list[dict] = []
        progressed = False
        print(f"  本輪 {len(pending)} 個單元待補", flush=True)

        def run(unit: dict) -> None:
            nonlocal done, failed, progressed
            try:
                result = gloss_unit(unit)
            except Exception as error:  # noqa: BLE001 - re-queued, not discarded
                with lock:
                    failed += 1
                    requeued.append(unit)
                    if failed % 25 == 1:
                        print(f"  ✗ {unit['ref']}：{error}", flush=True)
                return
            with lock:
                cache[unit["id"]] = result
                done += 1
                progressed = True
                if done % 50 == 0:
                    save_cache(cache)
                    print(f"  … 已完成 {done}（本輪剩 {len(pending) - done}）", flush=True)

        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            list(pool.map(run, pending))

        save_cache(cache)
        unproductive = 0 if progressed else unproductive + 1
        pending = requeued

    save_cache(cache)
    print(f"完成 {done}，退回 {len(pending)}，累計快取 {len(cache)} 個單元")
    if pending:
        print("（沒跑完的重跑一次即可，已完成的不會重做）")


if __name__ == "__main__":
    main()
