#!/usr/bin/env python3
"""Fill the 127-word gap the textbook leaves, by frequency in this reader's own corpus.

《大家的日本語》初級 I＋II yields 1,873 course words once the proper names and
the textbook's own repeats come out — 127 short of the two volumes' 2,000. The
series' answer to exactly this situation is already written down: the Hebrew
reader follows BBH's order to chapter 35 and then extends "接語料頻率延伸".
Here the corpus is the one the second volume reads — the pre-war religious
studies of 内村鑑三, 姉崎正治, 津田左右吉, 和辻哲郎 and the rest.

The rule, so it can be re-run and audited:

* count every 自立語 (content word) in the corpus by its 基本形;
* drop what the textbook already teaches, matched on base form and on kana;
* drop proper nouns — they belong to the appendix, as they do in the textbook
  half of the list;
* drop anything appearing in fewer than three of the corpus's works, so a
  single author's tic does not become a card;
* take the commonest what is left, in order.

Every word it adds records ``source: corpus-frequency`` with its count and the
number of works it appears in, so the printed vocabulary can say which words are
the textbook's and which are this reader's.

    python -X utf8 scripts/extend_japanese_vocabulary.py            # 看清單
    python -X utf8 scripts/extend_japanese_vocabulary.py --write
"""

from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/original-readers/japanese-full"
MANIFEST = CACHE / "aozora/manifest.json"
FREQUENCY = CACHE / "corpus-frequency.json"
VOCAB = ROOT / "data/originalReaders/vocabulary/japanese-2000.json"

TARGET = 2000
MIN_WORKS = 3

# 自立語だけ。助詞・助動詞・記号は語彙にならないし、固有名詞は附錄に行く。
KEEP_POS = {"名詞", "動詞", "形容詞", "副詞", "連体詞", "接続詞", "感動詞"}
DROP_SUB = {"固有名詞", "数", "非自立", "接尾", "代名詞", "サ変接続", "接続詞的", "特殊"}

# 語料是戰前文章，用的是歷史假名遣：思ふ／考へる／ゐる 就是課本教的
# 思う／考える／いる。比對時要能看穿這一層，否則整批「新詞」其實是舊拼法。
HISTORICAL = str.maketrans({"ゐ": "い", "ゑ": "え", "ヰ": "イ", "ヱ": "エ"})

# 這些是課本第一課就教的機能語與最常見的動詞，語料裡自然名列前茅，但它們
# 是「已經會了」而不是「該學的下一批」。基本形與課本的ます形對不上，所以
# 光靠比對詞表擋不住，要明寫。
TOO_BASIC = {
    "する", "なる", "ない", "ある", "いる", "ゐる", "居る", "來る", "来る", "行く",
    "見る", "言う", "いう", "云う", "云ふ", "言ふ", "思う", "思ふ", "出る", "出す",
    "入る", "取る", "持つ", "知る", "出来る", "できる", "せる", "れる", "られる",
    "つて", "ふる", "さ", "こと", "もの", "ため", "とき", "ところ", "よう", "そう",
    "これ", "それ", "あれ", "どれ", "ここ", "そこ", "此", "其", "彼", "斯", "如く",
    "一つ", "二つ", "多い", "無い", "良い", "好い", "いい", "大きい", "小さい",
}


def counted() -> dict:
    """Corpus counts, computed once and cached — tokenising 433 works is slow."""

    if FREQUENCY.exists():
        return json.loads(FREQUENCY.read_text(encoding="utf-8"))

    from janome.tokenizer import Tokenizer

    tokenizer = Tokenizer()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    total: collections.Counter[str] = collections.Counter()
    works: collections.Counter[str] = collections.Counter()
    readings: dict[str, str] = {}
    surfaces: dict[str, collections.Counter] = {}

    for index, (work_id, item) in enumerate(sorted(manifest.items()), start=1):
        text = (ROOT / item["file"]).read_text(encoding="utf-8")
        here: set[str] = set()
        for token in tokenizer.tokenize(text):
            parts = token.part_of_speech.split(",")
            if parts[0] not in KEEP_POS or (len(parts) > 1 and parts[1] in DROP_SUB):
                continue
            base = token.base_form
            if base in ("*", "") or len(base) == 1 and base.isascii():
                continue
            if base in TOO_BASIC or base.translate(HISTORICAL) in TOO_BASIC:
                continue
            # 一個字的漢字詞多半是被切碎的詞素（言、其、此），不是詞。
            if len(base) == 1 and not base.isdigit():
                continue
            total[base] += 1
            here.add(base)
            # token.reading 是「表面形」的讀音（見る→みん），不是辭書形的讀音。
            # 拿它當假名欄會印出一個不存在的詞，所以辭書形要自己再斷一次。
            if base not in readings:
                heads = list(tokenizer.tokenize(base))
                reading = "".join(
                    t.reading if t.reading != "*" else t.surface for t in heads
                )
                readings[base] = reading
            surfaces.setdefault(base, collections.Counter())[parts[0]] += 1
        for base in here:
            works[base] += 1
        if index % 50 == 0:
            print(f"  … 已讀 {index}/{len(manifest)} 篇", flush=True)

    payload = {
        "schemaVersion": "1.0.0",
        "works": len(manifest),
        "distinctBaseForms": len(total),
        "counts": {
            base: {
                "count": count,
                "works": works[base],
                "reading": readings.get(base, ""),
                "pos": surfaces[base].most_common(1)[0][0],
            }
            for base, count in total.most_common()
            if count >= 3
        },
    }
    FREQUENCY.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    return payload


def katakana_to_hiragana(text: str) -> str:
    return "".join(
        chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in text
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    vocab = json.loads(VOCAB.read_text(encoding="utf-8"))
    entries = vocab["entries"]
    have_written = {e["kanji"] for e in entries if e["kanji"]}
    have_kana = {e["kana"] for e in entries}
    # 課本用ます形（休みます），語料給辭書形（休む）——不比對辭書形，
    # 課本教過的動詞會整批被當成新詞收進來。
    have_written |= {e["dictionaryForm"] for e in entries if e.get("dictionaryForm")}
    # 漢字詞幹：思ふ 與 思います 的共同部分是「思」，歷史假名遣就靠這一層擋。
    stems = {re.match(r"^[一-鿿]+", e["kanji"] or "").group(0)
             for e in entries if e["kanji"] and re.match(r"^[一-鿿]+", e["kanji"])}
    need = TARGET - len(entries)
    print(f"課內詞 {len(entries)}，還差 {need}")
    if need <= 0:
        print("已滿額，不必延伸")
        return 0

    payload = counted()
    print(f"語料 {payload['works']} 篇，出現三次以上的基本形 {len(payload['counts'])}")

    chosen = []
    for base, item in payload["counts"].items():
        if len(chosen) >= need:
            break
        if item["works"] < MIN_WORKS:
            continue
        reading = katakana_to_hiragana(item["reading"])
        if base in have_written or reading in have_kana or base in have_kana:
            continue
        if base.translate(HISTORICAL) in have_written:
            continue
        stem = re.match(r"^[一-鿿]+", base)
        if stem and stem.group(0) in stems and len(stem.group(0)) >= 1 and len(base) <= 4:
            continue
        chosen.append(
            {
                "kana": reading or base,
                "kanji": base if base != reading else "",
                "accentBreaks": [],
                "step": 1,
                "lesson": 0,
                "source": "corpus-frequency",
                "corpusCount": item["count"],
                "corpusWorks": item["works"],
            }
        )
    print(f"選出 {len(chosen)} 詞")
    for word in chosen[:25]:
        print(f'  {word["kanji"] or word["kana"]:<10} {word["kana"]:<12} '
              f'{word["corpusCount"]:>5} 次／{word["corpusWorks"]} 篇')

    if not args.write:
        print("（未寫入；加 --write）")
        return 0

    start = len(entries)
    per, per_volume = 20, 50
    for index, word in enumerate(chosen):
        position = start + index
        lesson_index = position // per
        entries.append(
            {
                **word,
                "ordinal": position + 1,
                "volume": lesson_index // per_volume + 1,
                "readerLesson": lesson_index % per_volume + 1,
                "lessonSlot": position % per + 1,
                "textbookLesson": 0,
            }
        )
    vocab["counts"]["course"] = len(entries)
    vocab["counts"]["corpusExtension"] = len(chosen)
    vocab["counts"]["shortfall"] = max(0, TARGET - len(entries))
    VOCAB.write_text(json.dumps(vocab, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已寫入；課內詞 {len(entries)}／{TARGET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
