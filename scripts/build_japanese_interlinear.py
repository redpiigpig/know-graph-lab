#!/usr/bin/env python3
"""Build the word-by-word Traditional-Chinese layer for the Japanese reader.

The other three readers gloss in context, a window of words at a time, because
Hebrew, Greek and Latin inflect so heavily that the same form means different
things in different sentences. Japanese does not work that way here: the reading
text is 115,584 morphemes but only 10,601 distinct lemmas, and the particles and
auxiliaries — a third of every page — are a closed class that no model needs to
be asked about. Glossing per lemma instead of per occurrence turns a 4,800-call
job into a 240-call one, and it buys the thing this series values more than
speed: the same word reads the same way on every page it appears.

Three sources, in this order:

1. **The reader's own 2,000-word vocabulary.** If a word is taught in a lesson
   table, the gloss row must say what the table said. Anything else prints two
   different Chinese meanings for one word in one book.
2. **The closed-class table below.** Particles and auxiliaries, modern and 文語.
   These are grammar, not vocabulary, and a model asked for 「が」in isolation
   will happily return a different answer each time.
3. **The model**, for whatever is left, batched by lemma with one real sentence
   from the text as context, cached so a stopped run resumes.

    python -X utf8 scripts/build_japanese_interlinear.py --limit 200   # 試跑
    python -X utf8 scripts/build_japanese_interlinear.py               # 全書
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from janome.tokenizer import Tokenizer

import original_reader_llm as llm

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/original-readers/japanese-full"
READINGS = CACHE / "readings.json"
VOCAB = ROOT / "data/originalReaders/vocabulary/japanese-2000.json"
GLOSSARY = CACHE / "interlinear-gloss.json"
OUTPUT = CACHE / "interlinear.json"

CLOSED_POS = {"助詞", "助動詞", "記号", "フィラー", "その他"}
KANA = re.compile(r"[ぁ-ゟァ-ヿー]")
LATIN = re.compile(r"[A-Za-z]")
BATCH = 40
GLOSS_MAX = 12

# 助詞與助動詞：現代語與文語一起收。文語那一批是合約附錄二點名要教的
# （き・けり・つ・ぬ・たり・り・べし・ず・む・らむ・けむ・なり），讀本正文裡
# 到處都是，交給模型只會每次答得不一樣。
CLOSED_CLASS = {
    "は": "（主題）", "が": "（主格）", "を": "（受格）", "に": "（方向·對象）",
    "へ": "（往）", "と": "（和·引語）", "で": "（在·以）", "から": "（從）",
    "まで": "（到）", "より": "（比·從）", "の": "（的）", "も": "（也）",
    "や": "（或·啊）", "か": "（嗎）", "ね": "（呢）", "よ": "（喔）",
    "な": "（呀·別）", "ぞ": "（強調）", "ば": "（若）", "ても": "（即使）",
    "けれど": "（可是）", "ので": "（因為）", "のに": "（卻）", "し": "（又）",
    "て": "（接續）", "たり": "（又…又／完成）", "ながら": "（一邊）",
    "ばかり": "（只·剛）", "だけ": "（只）", "など": "（等）", "こそ": "（正是）",
    "さえ": "（連）", "しか": "（只有）", "ずつ": "（各）", "とも": "（縱使）",
    "ど": "（雖）", "ども": "（雖然）", "つつ": "（一邊·持續）", "ゆゑ": "（因為）",
    "だ": "（是）", "です": "（是·敬）", "である": "（是）", "ます": "（敬體）",
    "た": "（過去）", "ない": "（不）", "ぬ": "（不·完成）", "ず": "（不）",
    "う": "（意志·推量）", "よう": "（推量·樣）", "らしい": "（似乎）",
    "そうだ": "（聽說·看來）", "べし": "（應當）", "べき": "（應當）",
    "まい": "（不會·不打算）", "たい": "（想）", "れる": "（被·可能·敬）",
    "られる": "（被·可能·敬）", "せる": "（使）", "させる": "（使）",
    "き": "（過去·親見）", "けり": "（過去·傳聞·詠嘆）", "つ": "（完成）",
    "り": "（完成·存續）", "む": "（推量·意志）", "らむ": "（現在推量）",
    "けむ": "（過去推量）", "なり": "（是·斷定）", "たし": "（想）",
    "ごとし": "（如同）", "しむ": "（使）", "る": "（被·自發）", "らる": "（被·可能）",
    "けむや": "（豈曾）", "まし": "（反實推量）", "めり": "（看來）",
    "なむ": "（強調·願）", "こそあれ": "（雖則）", "ものの": "（雖然）",
    "。": "", "、": "", "「": "", "」": "", "『": "", "』": "", "・": "",
    "（": "", "）": "", "！": "", "？": "", "…": "", "─": "", "ー": "",
}

PROMPT = """你是日文讀本的逐詞對譯編輯。下面是 {count} 個日文詞，每個附一句書中的例句。\
請逐詞給出**繁體中文**詞義。

規矩：
- 一個詞給一個意思，最多 {maxlen} 個中文字，不要加詞性標記、不要註解、不要拼音。
- 給的是這個詞在例句裡的意思；例句只是幫你判斷，不要翻譯例句。
- 漢語詞（如「宗教」「儀礼」）若中日同義，直接給對應的繁體寫法（儀礼→儀禮）。
- 動詞給辭書形的意思（「行く」→ 去），不要寫成「去了」。
- 專有名詞給通行中譯；沒有通行中譯就音譯。
- 全部用繁體中文，不可出現日文假名或英文。

只輸出 JSON 物件，鍵是題號字串，值是詞義：{{"1": "神", "2": "祭祀"}}

{items}"""


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def vocabulary_glosses() -> dict[str, str]:
    """The reader's own lesson tables win over anything a model says."""
    out: dict[str, str] = {}
    for entry in load(VOCAB)["entries"]:
        zh = (entry.get("glossZh") or "").strip()
        if not zh:
            continue
        for form in (entry.get("dictionaryForm"), entry.get("kanji"), entry.get("kana")):
            if form and form not in out:
                out[form] = zh
    return out


def tokenise(tokenizer: Tokenizer, text: str) -> list[dict]:
    tokens = []
    for token in tokenizer.tokenize(text):
        pos = token.part_of_speech.split(",")[0]
        base = token.base_form if token.base_form and token.base_form != "*" else token.surface
        tokens.append({"word": token.surface, "base": base, "pos": pos, "trailing": ""})
    return tokens


def needs_model(base: str, pos: str, vocab: dict[str, str]) -> bool:
    if pos in CLOSED_POS or base in CLOSED_CLASS or base in vocab:
        return False
    return bool(base.strip())


def validate(gloss: str) -> str | None:
    gloss = (gloss or "").strip().strip("。，,、 ")
    if not gloss:
        return None
    if len(gloss) > GLOSS_MAX or KANA.search(gloss) or LATIN.search(gloss):
        return None
    return gloss


def ask(items: list[tuple[str, str, str]]) -> dict[str, str]:
    """One batch: [(lemma, pos, example)] -> {lemma: 繁中}."""
    lines = "\n".join(
        f"{index}. {lemma}（{pos}）　例：{example[:40]}"
        for index, (lemma, pos, example) in enumerate(items, start=1)
    )
    prompt = PROMPT.format(count=len(items), maxlen=GLOSS_MAX, items=lines)
    reply = llm.call_model(prompt, max_tokens=2000)
    match = re.search(r"\{.*\}", reply or "", re.S)
    if not match:
        return {}
    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}
    out: dict[str, str] = {}
    for key, value in payload.items():
        if not key.strip().isdigit():
            continue
        index = int(key) - 1
        if 0 <= index < len(items):
            gloss = validate(str(value))
            if gloss:
                out[items[index][0]] = gloss
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=0, help="最多問幾個詞（試跑用）")
    parser.add_argument("--batch", type=int, default=BATCH)
    args = parser.parse_args()

    readings = load(READINGS)
    vocab = vocabulary_glosses()
    glossary: dict[str, str] = load(GLOSSARY) if GLOSSARY.exists() else {}
    tokenizer = Tokenizer()

    # 一次斷詞，之後都用這份；每個 lemma 記一句例句給模型判斷語境。
    units: dict[str, dict] = {}
    example: dict[str, str] = {}
    wanted: dict[str, str] = {}
    for volume in readings["volumes"]:
        for lesson in volume["lessons"]:
            groups = [("reading", lesson["units"]), ("memory", lesson["memoryUnits"])]
            for group, rows in groups:
                for index, unit in enumerate(rows, start=1):
                    unit_id = unit.get("id") or f"v{volume['volume']}-l{lesson['lesson']:02d}-m{index:03d}"
                    tokens = tokenise(tokenizer, unit["text"])
                    units[unit_id] = {
                        "ref": f"{lesson['title']}　{unit.get('label') or ''}".strip(),
                        "group": group,
                        "tokens": tokens,
                    }
                    for token in tokens:
                        key = f"{token['base']}|{token['pos']}"
                        if needs_model(token["base"], token["pos"], vocab) and key not in glossary:
                            wanted[key] = token["base"]
                            example.setdefault(key, unit["text"])

    todo = sorted(wanted)
    if args.limit:
        todo = todo[: args.limit]
    print(f"單元 {len(units):,}　需要問模型的詞 {len(wanted):,}"
          f"（本輪 {len(todo):,}，已快取 {len(glossary):,}）")

    batches = [todo[i : i + args.batch] for i in range(0, len(todo), args.batch)]
    answered = 0
    for number, batch in enumerate(batches, start=1):
        items = [(key.split("|")[0], key.split("|")[1], example[key]) for key in batch]
        got = ask(items)
        if not got and len(items) > 4:
            # 整批回空多半是輸出被截斷或格式跑掉，不是這些詞問不出來。對半再問一次
            # 就好，不必整批丟掉——丟掉的話那四十個詞會永遠留白。
            half = len(items) // 2
            got = {**ask(items[:half]), **ask(items[half:])}
            print(f"    · 批 {number} 整批回空，拆半重問拿到 {len(got)}")
        for key in batch:
            lemma = key.split("|")[0]
            if lemma in got:
                glossary[key] = got[lemma]
                answered += 1
        GLOSSARY.write_text(json.dumps(glossary, ensure_ascii=False, indent=0), encoding="utf-8")
        print(f"  批 {number}/{len(batches)}　收到 {len(got)}/{len(batch)}　"
              f"累計 {answered:,}　引擎 {llm.current_model()}")

    # 組裝：詞表 → 閉合詞類 → 模型。缺的就留白，不用別的語言或原文頂替。
    missing = 0
    for unit in units.values():
        for token in unit["tokens"]:
            key = f"{token['base']}|{token['pos']}"
            gloss = (
                vocab.get(token["base"])
                or CLOSED_CLASS.get(token["base"])
                or CLOSED_CLASS.get(token["word"])
                or glossary.get(key)
                or ""
            )
            if token["pos"] == "記号":
                gloss = ""
            elif not gloss:
                missing += 1
            token["glossZh"] = gloss
            token.pop("base", None)
            token.pop("pos", None)

    total = sum(len(unit["tokens"]) for unit in units.values())
    OUTPUT.write_text(
        json.dumps(
            {
                "schemaVersion": "1.0.0",
                "language": "Japanese",
                "languageCode": "ja",
                "engine": "詞表優先 → 閉合詞類表 → Gemini／NVIDIA",
                "count": len(units),
                "units": units,
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"寫出 {OUTPUT.relative_to(ROOT)}：{len(units):,} 單元、{total:,} 詞、"
          f"未有詞義 {missing:,}（{missing / total:.1%}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
