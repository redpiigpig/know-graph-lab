#!/usr/bin/env python3
"""Gloss the Japanese reader's 1,873 course words in Traditional Chinese.

The u-biq pages that gave us《大家的日本語》's lesson order give kana, kanji and
pitch accent but no meanings at all, so every gloss in this reader is written
here. Four fields per word, and each is asked for because a Chinese-speaking
reader of Japanese scholarship needs it:

* ``glossZh``  the reader's main gloss, Traditional Chinese;
* ``glossEn``  the row that reaches the English-language literature;
* ``pos``      名詞／動詞／い形容詞／な形容詞／副詞… — Japanese hides its part of
  speech in the citation form, and 「きれい」 being a な形容詞 rather than an
  い形容詞 is exactly the kind of thing a learner gets wrong for years;
* ``dictionaryForm`` the 辞書形 of a verb. The textbook cites verbs in ます形
  （休みます）because that is what it teaches first; a dictionary, and every
  text this reader goes on to read, uses 休む. Both are printed.

The gate rejects a gloss that is empty, that leaks kana or Latin letters into
the Chinese, or that gives a 辞書形 not ending in an う-row kana — a model asked
for a dictionary form will occasionally hand back the ます form it was given.

    python -X utf8 scripts/gloss_japanese_vocabulary.py --limit 40
    python -X utf8 scripts/gloss_japanese_vocabulary.py --write
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
VOCAB = ROOT / "data/originalReaders/vocabulary/japanese-2000.json"
CACHE = ROOT / "output/source-cache/original-readers/japanese-full/gloss-zh.json"

KANA_RE = re.compile(r"[ぁ-ゖァ-ヺー]")
LATIN_RE = re.compile(r"[A-Za-z]")
HAN_RE = re.compile(r"[一-鿿]")
U_ROW = "うくぐすずつづぬふぶぷむゆるぐ"

POS_ALLOWED = {
    "名詞", "動詞", "い形容詞", "な形容詞", "副詞", "助詞", "助動詞",
    "接続詞", "感嘆詞", "連体詞", "接頭辭", "接尾辭", "數詞", "表現",
}

PROMPT = """你是日文讀本的詞義編輯，讀者是中文母語的宗教學研究者。

下面每一筆是《大家的日本語》某一課的生詞，給了假名與漢字寫法。請逐筆給出四個欄位。

規則：
1. 只回傳一個 JSON 物件：{{"words":[{{"index":1,"zh":"…","en":"…","pos":"…","dict":"…"}}]}}
2. 筆數、index、順序與輸入完全相同。
3. zh＝繁體中文詞義，1–8 個字，多義用「、」隔開，最多三義。不要解釋、不要注音。
4. en＝英文詞義，2–6 個詞。
5. pos＝下列之一：名詞／動詞／い形容詞／な形容詞／副詞／助詞／助動詞／接続詞／\
感嘆詞／連体詞／接頭辭／接尾辭／數詞／表現。
6. dict＝動詞的辭書形（休みます→休む、来ます→来る、します→する）；\
不是動詞就給空字串。
7. 中文一律繁體，不要簡體字，不要出現假名或英文。

詞：
{items}
"""


ITEM_RE = re.compile(
    r'"index"\s*:\s*(\d+)\s*,\s*"zh"\s*:\s*"(.*?)"\s*,\s*"en"\s*:\s*"(.*?)"\s*,'
    r'\s*"pos"\s*:\s*"(.*?)"\s*(?:,\s*"dict"\s*:\s*"(.*?)")?',
    re.S,
)


def parse_words(raw: str) -> dict[int, dict]:
    """Read the reply whether or not it is strict JSON.

    英文欄裡的撇號與括號常讓 json.loads 讀不動整批；欄位本身讀得出來，
    為了一個引號把二十個詞丟掉只是再付一次錢。
    """

    block = re.search(r"\{.*\}", raw, re.S)
    if block:
        try:
            payload = json.loads(block.group(0))
            answers = {
                int(item["index"]): item
                for item in payload.get("words", [])
                if str(item.get("index", "")).strip().isdigit()
            }
            if answers:
                return answers
        except (ValueError, TypeError, AttributeError):
            pass
    return {
        int(index): {"index": int(index), "zh": zh, "en": en, "pos": pos, "dict": dictionary or ""}
        for index, zh, en, pos, dictionary in ITEM_RE.findall(raw)
    }


def load_cache() -> dict:
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8")).get("words", {})
    return {}


def save_cache(cache: dict) -> None:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(
        json.dumps(
            {
                "schemaVersion": "1.0.0",
                "engine": llm.current_model(),
                "note": "《大家的日本語》課內詞的繁中／英文詞義、品詞與辭書形，本讀本自撰。",
                "count": len(cache),
                "words": cache,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def key_of(entry: dict) -> str:
    return f'{entry["kana"]}|{entry["kanji"]}'


def problems(entry: dict, answer: dict) -> list[str]:
    found = []
    zh = answer.get("zh", "").strip()
    en = answer.get("en", "").strip()
    pos = answer.get("pos", "").strip()
    dictionary = answer.get("dict", "").strip()

    if not zh:
        found.append("中文空白")
    elif KANA_RE.search(zh) or LATIN_RE.search(zh):
        found.append("中文夾了假名或英文")
    elif len(zh) > 14:
        found.append(f"中文過長（{len(zh)}）")
    if not en or HAN_RE.search(en) or KANA_RE.search(en):
        found.append("英文空白或夾了漢字假名")
    if pos not in POS_ALLOWED:
        found.append(f"品詞不在清單內：{pos!r}")
    if pos == "動詞":
        if not dictionary:
            found.append("動詞缺辭書形")
        elif dictionary.endswith("ます"):
            found.append("辭書形還是ます形")
        elif dictionary[-1] not in U_ROW and not dictionary.endswith(("る", "く", "う", "つ", "ぬ", "ぶ", "む", "す", "ぐ")):
            found.append(f"辭書形不以う段結尾：{dictionary}")
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="寫回詞表")
    parser.add_argument("--model", choices=sorted(llm.MODEL_CHAINS), default="auto")
    parser.add_argument("--batch", type=int, default=20)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    llm.select_chain(args.model)

    vocab = json.loads(VOCAB.read_text(encoding="utf-8"))
    entries = vocab["entries"]
    cache = load_cache()
    pending = [e for e in entries if key_of(e) not in cache]
    if args.limit:
        pending = pending[: args.limit]
    print(f"課內詞 {len(entries)}，已有詞義 {len(cache)}，待補 {len(pending)}")

    rejected = 0
    for start in range(0, len(pending), args.batch):
        chunk = pending[start : start + args.batch]
        items = "\n".join(
            f'{i + 1}. {e["kana"]}' + (f'（{e["kanji"]}）' if e["kanji"] else "")
            for i, e in enumerate(chunk)
        )
        try:
            raw = llm.call_model(PROMPT.format(items=items), max_tokens=2600)
        except Exception as error:  # noqa: BLE001 - re-runnable
            print(f"  ✗ 第 {start + 1}–{start + len(chunk)} 批：{error}")
            continue
        answers = parse_words(raw)
        if not answers:
            print(f"  ✗ 第 {start + 1}–{start + len(chunk)} 批：回應讀不出 index")
            continue
        for index, entry in enumerate(chunk, start=1):
            answer = answers.get(index)
            if not answer:
                continue
            bad = problems(entry, answer)
            if bad:
                rejected += 1
                if rejected % 20 == 1:
                    print(f"  ✗ {entry['kana']}：{'；'.join(bad)}")
                continue
            cache[key_of(entry)] = {
                "glossZh": answer["zh"].strip(),
                "glossEn": answer["en"].strip(),
                "pos": answer["pos"].strip(),
                "dictionaryForm": answer.get("dict", "").strip(),
                "engine": llm.current_model(),
            }
        save_cache(cache)
        print(f"  … {min(start + args.batch, len(pending))}/{len(pending)}（累計 {len(cache)}）", flush=True)

    print(f"已有詞義 {len(cache)}／{len(entries)}，本輪退回 {rejected}")

    if not args.write:
        print("（未寫回詞表；加 --write）")
        return 0

    filled = 0
    for entry in entries:
        found = cache.get(key_of(entry))
        if not found:
            continue
        entry.update(
            {
                "glossZh": found["glossZh"],
                "glossEn": found["glossEn"],
                "pos": found["pos"],
                "dictionaryForm": found["dictionaryForm"],
            }
        )
        filled += 1
    vocab["counts"]["glossed"] = filled
    VOCAB.write_text(json.dumps(vocab, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已寫回 {VOCAB.relative_to(ROOT)}：{filled} 筆有詞義")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
