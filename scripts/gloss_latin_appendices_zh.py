#!/usr/bin/env python3
"""替拉丁讀本附錄那幾張表補繁體中文。

問題是在紙上看到的：附錄的〈數字、羅馬數字與度量衡〉〈親屬稱謂〉〈羅馬曆、月份與
聖經節期〉幾張表，右欄印的是**英文**。這幾張表建的時候只帶了 Whitaker 的英文釋
義，而印表的程式寫成 `zh or glossZh or glossEn`——沒有中文就退到英文，於是一本繁
體中文讀本的附錄裡整頁 `first, foremost` `mother's brother` `the day before the
Kalends`。退而求其次的預設值在資料缺的時候會把缺口藏起來。

補的順序有先後，因為便宜且可靠的來源要先用完：

1. **先用五十課詞表已審過的中文**。附錄的詞有一半以上本來就在課內出現過，
   `numerals` 81 條裡有 19 條、`principalParts` 841 條裡有 490 條都是。同一個詞在
   課內與附錄讀起來必須一樣，所以這一步不只是省 token，本身就是正確性。
2. **剩下的才問模型**，沿用 `gloss_latin_vocabulary_zh.py` 那一套：帶著英文釋義去
   翻譯而不是憑空回想，教會語域先給教會義，並套同一份 `CATHOLIC_TERMS` 修正——
   模型講基督宗教時預設用新教中文（教皇、使徒、上帝），而這本書的對頁是思高本。

〈人名、地名、民族與國名〉不在這裡：那張表的中文走思高本逐節對齊，是證據不是翻
譯，不能讓模型插手。〈近現代教廷拉丁〉那 400 條也不碰——那張表混進了 `Psal`、
`Latine`、`Cardinalis` 這類縮寫與普通名詞，該重做的是表本身。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gloss_latin_vocabulary_zh import (  # noqa: E402
    BATCH,
    CATHOLIC_TERMS,
    batch_prompt,
    flaws,
    parse,
)
import original_reader_llm as llm  # noqa: E402
import latin_source_texts as L  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
V = ROOT / "data" / "originalReaders" / "vocabulary"
APPENDICES = V / "latin-appendices.json"
VOCABULARY = V / "latin-2000.json"
CACHE = (ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
         / "appendix-gloss-zh.json")

# 要補的表。names 走思高對齊、modernNames 整張待重做，兩張都不在內。
TABLES = [
    ("upper", "numerals"), ("upper", "kinship"), ("upper", "calendar"),
    ("upper", "principalParts"),
    ("lower", "offices"), ("lower", "liturgical_year"),
    ("lower", "documents"), ("lower", "scholastic"),
]


def fold(text: str) -> str:
    """比對鍵：去長音符號、I/J 與 U/V 同字。詞表寫 amīcus，附錄寫 amicus。"""
    text = unicodedata.normalize("NFD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z]", "", text).replace("j", "i").replace("v", "u")


def lesson_glosses() -> dict[str, str]:
    entries = json.loads(VOCABULARY.read_text(encoding="utf-8"))["entries"]
    glosses: dict[str, str] = {}
    for entry in entries:
        gloss = (entry.get("glossZh") or "").strip()
        if gloss:
            glosses.setdefault(fold(entry["headword"]), gloss)
    return glosses


def load_cache() -> dict:
    return json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}


def save_cache(cache: dict) -> None:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="補拉丁附錄各表的繁體中文")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="只問模型前 N 條")
    parser.add_argument("--engine", default="auto")
    args = parser.parse_args()

    if args.engine != "auto":
        llm.select_chain(args.engine)

    payload = json.loads(APPENDICES.read_text(encoding="utf-8"))
    reused = lesson_glosses()
    cache = load_cache()

    pending: list[dict] = []
    from_lessons = 0
    from_cache = 0
    for half, key in TABLES:
        for entry in payload[half][key]["entries"]:
            if (entry.get("zh") or "").strip():
                continue
            headword = entry["headword"]
            cached = cache.get(headword)
            if cached:
                entry["zh"], entry["zhRoute"] = cached["zh"], cached["route"]
                from_cache += 1
                continue
            gloss = reused.get(fold(headword))
            if gloss:
                entry["zh"] = gloss
                entry["zhRoute"] = "五十課詞表"
                cache[headword] = {"zh": gloss, "route": "五十課詞表"}
                from_lessons += 1
                continue
            pending.append(entry)

    print(f"  由課內詞表補 {from_lessons}，由快取補 {from_cache}，待問模型 {len(pending)}")
    if args.limit:
        pending = pending[: args.limit]

    done = 0
    rejected = 0
    for start in range(0, len(pending), BATCH):
        chunk = pending[start : start + BATCH]
        try:
            rows = parse(llm.call_model(batch_prompt(chunk), max_tokens=4000))
        except Exception as error:                       # noqa: BLE001
            print(f"      批次 {start // BATCH + 1} 失敗：{error}", flush=True)
            time.sleep(10)
            continue
        # 模型常把整行字典形回抄回來（問 ambō 回「ambō, ambōnis, m.」），也常掉長音
        # 符號。用折疊後的詞頭比對，並且連逗號前那一段也一起索引，否則每一批都會
        # 靜靜掉幾條、然後永遠重試同一個詞。
        by_head: dict[str, str] = {}
        for row in rows:
            echoed = (row.get("headword") or "").strip()
            gloss = (row.get("zh") or "").strip()
            for variant in (echoed, echoed.split(",")[0]):
                folded = L.fold(variant.strip())
                if folded:
                    by_head.setdefault(folded, gloss)
        engine = llm.current_model()
        for entry in chunk:
            headword = entry["headword"]
            gloss = CATHOLIC_TERMS.get(headword) or by_head.get(L.fold(headword), "")
            problem = flaws(headword, gloss)
            if problem:
                rejected += 1
                continue
            route = "catholic-usage" if headword in CATHOLIC_TERMS else engine
            entry["zh"], entry["zhRoute"] = gloss, route
            cache[headword] = {"zh": gloss, "route": route}
            done += 1
        print(f"      {min(start + BATCH, len(pending))}/{len(pending)}"
              f"　引擎 {engine}", flush=True)
        if args.write:
            save_cache(cache)
    if rejected:
        print(f"      本輪退回 {rejected} 條")

    for half, key in TABLES:
        entries = payload[half][key]["entries"]
        have = sum(1 for entry in entries if (entry.get("zh") or "").strip())
        print(f"  {half}/{key}：{have}/{len(entries)}")

    if args.write:
        save_cache(cache)
        APPENDICES.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  已寫回 {APPENDICES.name}（模型新補 {done} 條）")
    else:
        print("\n（未寫檔；加 --write 才會寫回）")


if __name__ == "__main__":
    main()
