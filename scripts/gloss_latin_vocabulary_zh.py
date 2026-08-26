#!/usr/bin/env python3
"""Traditional-Chinese glosses for the reader's two thousand words.

Every entry reaches this script already carrying its dictionary form and an
English definition -- Collins's for the upper volume, Whitaker's for the lower --
so the model is asked to render a gloss that already exists rather than to recall
a word it may not know.  That is the difference between translating and guessing,
and for a fifth-century word like ``dioecesis`` it is the whole difference.

Each entry also carries its register.  A word Whitaker flags ecclesiastical is
glossed as the church uses it, not as Cicero did: ``ordo`` in this reader is 聖秩
before it is 次序, and ``confessio`` is 認信／告明 before it is 承認.  Without that
flag the lower volume would come back reading like a classical dictionary.

Results are cached per headword, so a run that stops on quota resumes instead of
restarting, and each cached gloss records which engine produced it.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import opencc  # noqa: E402

import original_reader_llm as llm  # noqa: E402
import latin_source_texts as L  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
VOCABULARY = ROOT / "data" / "originalReaders" / "vocabulary" / "latin-2000.json"
CACHE = (ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
         / "gloss-zh.json")

BATCH = 20

PROMPT = """你是教會拉丁文讀本的繁體中文釋義編輯。以下是若干拉丁詞條，每條給了
字典形式、英文釋義，有些另標了語域。

請為每條寫出**繁體中文**釋義，規則：

1. 只用繁體中文，不得出現簡體字、日文或英文。
2. 釋義要精確簡潔，以「、」分隔義項，最多三個義項，全長不超過二十字。
3. 標了「教會語域」的詞，必須先給教會／禮儀／神學上的意思，古典義若要保留放後面。
   例：ordo 先寫「聖秩、品級」而非「次序」；confessio 先寫「認信、告明」。
4. 動詞用中文動詞對譯，不要寫成「……的行為」這種名詞化說法。
5. 介系詞、連接詞要寫出它在句中的功能，例如 cum 寫「與、同；當……時」。
6. 遇到專有名詞（人名、地名、神名）請給**思高譯本**的譯名，例如 Jēsus 寫「耶穌」、
   Moyses 寫「梅瑟」、Joannes 寫「若望」；不確定就輸出空字串，不要自創音譯。
7. 不確定就給最保守的核心義，不要臆造罕見義。

輸出 JSON 陣列，每個元素 {"headword": 原樣照抄, "zh": 繁體中文釋義}，
不要 markdown 圍欄，不要任何說明文字。

詞條：
"""


def batch_prompt(rows: list[dict]) -> str:
    lines = []
    for row in rows:
        marks = []
        if row.get("ecclesiastical"):
            marks.append("教會語域")
        if row.get("age"):
            marks.append(row["age"])
        tag = f"（{'／'.join(marks)}）" if marks else ""
        lines.append(f'- {row["headword"]}{tag}｜{row.get("forms", "")}｜{row.get("glossEn", "")}')
    return PROMPT + "\n".join(lines)


def parse(text: str) -> list[dict]:
    text = text.strip()
    fence = chr(96) * 3
    if text.startswith(fence):
        text = text.split(chr(10), 1)[-1]
    if text.endswith(fence):
        text = text.rsplit(chr(10), 1)[0]
    return json.loads(text.strip())


# Detecting simplified characters by listing them is a trap: half the
# characters on any hand-written list -- 向, 志, 台, 后 -- are identical in
# both scripts, and the filter then rejects perfectly good Traditional
# Chinese. 「向、趨向；為了」 was thrown away ten times over for containing 向.
# Converting and comparing is exact.
_S2T = opencc.OpenCC('s2t')

# Characters whose s2t rewrite is a Taiwan-standard variant, not evidence of
# simplified text.  The one that matters most here is 祢: OpenCC rewrites it to
# 禰, but 祢 is the Catholic second-person honorific for God and appears in
# almost every prayer this project translates -- 「願祢受讚頌」 is the title of one
# of its readings.  Rejecting it as simplified threw away good translations and
# retried them for ever.  台 is the same kind of case, and 号 deliberately is not:
# that one really is simplified.
# Derived from the translations that passed, not guessed: these are the
# characters s2t rewrites inside text a reviewer accepted as Traditional.
# 祢 leads by a wide margin -- it is the honorific for God -- then 群, 里,
# 台, 峰, 凶, 床, 升.
TAIWAN_VARIANTS = {"台", "床", "群", "峰", "祢", "里", "后", "余", "咸",
                   "凶", "升", "布", "冢", "臺"}


def has_simplified(text: str) -> bool:
    converted = _S2T.convert(text)
    if converted == text:
        return False
    if len(converted) != len(text):
        return True
    # A variant character passes only while the rest of the line is clean; a line
    # that also contains a real simplified form is still rejected.
    return any(before != after and before not in TAIWAN_VARIANTS
               for before, after in zip(text, converted))


LATIN_LEAK = re.compile(r"[A-Za-z]{3,}")


def flaws(headword: str, zh: str) -> str:
    if not zh.strip():
        return "空白"
    if has_simplified(zh):
        return "含簡體字"
    if LATIN_LEAK.search(zh):
        return "殘留拉丁／英文"
    if len(zh) > 28:
        return "過長"
    return ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="只處理前 N 個未完成詞條")
    ap.add_argument("--engine", default="auto")
    args = ap.parse_args()

    if args.engine != "auto":
        llm.select_chain(args.engine)

    data = json.loads(VOCABULARY.read_text(encoding="utf-8"))
    entries = data["entries"]
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}

    pending = [e for e in entries if e["headword"] not in cache]
    if args.limit:
        pending = pending[: args.limit]
    print(f"詞條 {len(entries)}；已有釋義 {len(cache)}；待處理 {len(pending)}")

    rejected = 0
    for start in range(0, len(pending), BATCH):
        chunk = pending[start:start + BATCH]
        try:
            answer = parse(llm.call_model(batch_prompt(chunk), max_tokens=4000))
        except Exception as exc:  # noqa: BLE001
            print(f"  批次 {start // BATCH + 1} 失敗：{exc}", flush=True)
            time.sleep(10)
            continue
        # Match on the folded headword.  The model echoes the word back without
        # its macrons often enough that an exact-string match loses a tenth of
        # every batch -- and loses it silently, since the entry simply stays
        # unglossed and gets retried forever.
        # Index both what was asked and what the model tends to echo.  Asked
        # about ambō it answers with the whole dictionary line, "ambō, ambōnis,
        # m.", and a lookup on the bare headword alone then finds nothing and
        # retries the same word for ever.
        by_head: dict[str, str] = {}
        for row in answer:
            echoed = (row.get("headword") or "").strip()
            zh = (row.get("zh") or "").strip()
            for variant in (echoed, echoed.split(",")[0]):
                folded = L.fold(variant.strip())
                if folded:
                    by_head.setdefault(folded, zh)
        engine = llm.current_model()
        for entry in chunk:
            zh = by_head.get(L.fold(entry["headword"]), "")
            problem = flaws(entry["headword"], zh)
            if problem:
                rejected += 1
                continue
            cache[entry["headword"]] = {"zh": zh, "engine": engine}
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  {min(start + BATCH, len(pending))}/{len(pending)}  "
              f"累計 {len(cache)}  引擎 {engine}", flush=True)

    missing = [e["headword"] for e in entries if e["headword"] not in cache]
    print(f"完成 {len(cache)}/{len(entries)}；本輪退回 {rejected}；仍缺 {len(missing)}")
    if missing[:10]:
        print("  缺:", ", ".join(missing[:10]))

    if args.write:
        for entry in entries:
            hit = cache.get(entry["headword"])
            entry["glossZh"] = hit["zh"] if hit else ""
            entry["glossEngine"] = hit["engine"] if hit else ""
        VOCABULARY.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        print("->", VOCABULARY.relative_to(ROOT))


if __name__ == "__main__":
    main()
