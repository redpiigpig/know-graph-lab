"""替國小英語一千字標詞性，寫回 `data/originalReaders/vocabulary/english-1000.json`。

2026-09-17 使用者：「甚麼叫做 We are hello.／I am thank. 小一的英文也不會是這樣啊」。
根因不是漏了哪幾句，是**做法**：真的國小講義是「固定句型 ＋ 詞性正確的詞槽」
（`I am ___.` 那個空格只能放形容詞或名詞），我卻讓模型自由造句，招呼語才會被
塞進形容詞的位置。詞表原本沒有詞性欄（單字卡印的那欄其實是主題名），所以生成端
只能一個字一個字禁——擋掉 hello 就換 `They are you.`，永遠打地鼠。

標法：
  1. 先用人工表把**會出事的那幾類**釘死（招呼語、代名詞、be 動詞、冠詞、連接詞…）。
     這些字數不多但全是地雷，交給模型反而不穩。
  2. 其餘交給模型分批標，每批都驗標籤在許可集合內。
  3. 🚨 一個字可能多詞性（work 名詞也動詞、OK 形容詞也感嘆詞）。存成陣列，
     判斷時只要「其中一個詞性合法」就放行，才不會把 `This is work.` 誤殺。

用法：
    python scripts/tag_english_pos.py --dry     # 只印，不寫回
    python scripts/tag_english_pos.py --write
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import build_english_course50 as gen  # noqa: E402

VOCAB = gen.VOCAB

# 許可的標籤。刻意壓到國小看得懂的粒度，不做完整詞類系統。
TAGS = {"noun", "verb", "adj", "adv", "pron", "prep", "conj",
        "det", "num", "interj", "phrase"}

# 🚨 人工釘死的那一批：全是「接錯位置就變成不是英文」的字。
# 模型標這些字會飄（把 hello 標成 noun、把 have 標成 adj 都出現過），
# 而它們正好是出事的來源，所以不交給模型。
MANUAL: dict[str, list[str]] = {
    # 招呼語與應答——這些永遠不能接在 be 動詞後面當補語
    "hello": ["interj"], "hi": ["interj"], "goodbye": ["interj"],
    "yes/yeah": ["interj"], "no": ["interj", "det"], "please": ["interj", "adv"],
    "sorry": ["adj", "interj"], "thank": ["verb"], "welcome": ["adj", "interj", "verb"],
    "good morning": ["phrase"], "good afternoon": ["phrase"],
    "good evening": ["phrase"], "good night": ["phrase"],
    "excuse": ["verb", "noun"],
    # 代名詞
    "I": ["pron"], "you": ["pron"], "he": ["pron"], "she": ["pron"],
    "it": ["pron"], "we": ["pron"], "they": ["pron"],
    "anyone/anybody": ["pron"], "everyone/everybody": ["pron"],
    "someone/somebody": ["pron"], "nobody": ["pron"],
    # 常被標錯的動詞
    "have": ["verb"], "make": ["verb"], "let": ["verb"], "get": ["verb"],
    "want": ["verb"], "keep": ["verb"], "stay": ["verb"], "become": ["verb"],
    # 形容詞（第一課的補語就靠這幾個）
    "fine": ["adj"], "sure": ["adj"], "OK": ["adj"],
}

PROMPT = """你是英語教材編輯，正在替國小一千字詞表標詞性。

只能用這些標籤：noun（名詞）／verb（動詞）／adj（形容詞）／adv（副詞）／
pron（代名詞）／prep（介系詞）／conj（連接詞）／det（限定詞、冠詞）／
num（數詞）／interj（感嘆詞、招呼語）／phrase（多字片語）

規矩：
- 一個字可能有多個詞性，例如 work 是 noun 也是 verb，就兩個都列。
  但只列**國小這個程度會用到**的，不要把冷僻用法也列進來。
- 招呼語（hello、hi、goodbye）標 interj，不要標 noun。
- 多字片語（good morning、pearl milk tea）標 phrase。
- 詞條寫成 `father/dad` 或 `apple(s)` 的，看主要那個形式。

只輸出 JSON，不要說明文字：
{{"words": [{{"en": "原字串（照抄）", "pos": ["noun"]}}]}}

要標的字（{n} 個）：
{words}
"""

BATCH = 40


def validate(payload, wanted: list[str]) -> list[str]:
    if not isinstance(payload, dict):
        return ["輸出不是物件"]
    rows = payload.get("words")
    if not isinstance(rows, list):
        return ["words 要是陣列"]
    got = {}
    for i, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            return [f"第 {i} 筆不是物件"]
        en, pos = row.get("en"), row.get("pos")
        if not isinstance(en, str) or not isinstance(pos, list) or not pos:
            return [f"第 {i} 筆的 en/pos 形狀不對"]
        bad = [p for p in pos if p not in TAGS]
        if bad:
            return [f"「{en}」用了不許可的標籤 {bad}；只能用 {sorted(TAGS)}"]
        got[en] = pos
    missing = [w for w in wanted if w not in got]
    if missing:
        return [f"漏標 {len(missing)} 個，例如「{missing[0]}」"]
    return []


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    gen.VERBOSE = args.verbose

    data = json.loads(VOCAB.read_text(encoding="utf-8"))
    entries = data["entries"]
    todo = [e["en"] for e in entries if e["en"] not in MANUAL]
    print(f"一千字裡 {len(MANUAL)} 個人工釘死，{len(todo)} 個交給模型")

    tagged: dict[str, list[str]] = dict(MANUAL)
    for start in range(0, len(todo), BATCH):
        chunk = todo[start:start + BATCH]
        payload, errs = gen.ask(
            PROMPT.format(n=len(chunk), words="\n".join(f"- {w}" for w in chunk)),
            lambda p, w=chunk: validate(p, w),
            attempts=4, stage=f"詞性 {start + 1}-{start + len(chunk)}")
        if payload is None:
            print(f"  ✗ {start + 1}-{start + len(chunk)}：{'；'.join(errs)}", flush=True)
            continue
        for row in payload["words"]:
            tagged.setdefault(row["en"], row["pos"])
        print(f"  ✓ {start + 1}-{start + len(chunk)}", flush=True)

    done = sum(1 for e in entries if e["en"] in tagged)
    print(f"\n標到 {done}/{len(entries)}")
    import collections
    spread = collections.Counter(p for e in entries for p in tagged.get(e["en"], []))
    print("  ", dict(spread.most_common()))

    if not args.write:
        print("\n（沒加 --write，詞表沒有動）")
        return
    for e in entries:
        pos = tagged.get(e["en"])
        if pos:
            e["pos"] = pos
    VOCAB.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8")
    print(f"\n已寫回 {VOCAB}")


if __name__ == "__main__":
    main()
