#!/usr/bin/env python3
"""從 OSHB（morphhb）逐詞標註推出希伯來單字卡要印的性、數與狀態。

詞表本身沒有性別欄位，卡片又非印不可（使用者要求名詞一律標陽性／陰性／陰陽性）。
用推的會錯：אֶ֫רֶץ、עִיר、יָד、נֶ֫פֶשׁ 都是陰性但沒有陰性字尾，דֶּ֫רֶךְ、רוּחַ 兩性都有。
所以跟希臘卡用 SBLGNT 標註同一個路數 —— 性別是希伯來聖經標註過的事實，不是從字尾猜的。

    python scripts/hebrew_card_grammar.py            # 只看統計
    python scripts/hebrew_card_grammar.py --write    # 寫出 hebrew-card-grammar.json

性別取該詞條全書標註的多數；兩性都達門檻（各佔 20% 以上且至少 5 次）才記陰陽性。
數與狀態則是**認這一張卡的字形**：אָבוֹת 是 אָב 的複數卡、עֵינַ֫יִם 是雙數卡、
אֲבִי 是附屬形卡，三張同一個 Strong 號，靠字形比對才分得開。
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WLC = ROOT / "output/source-cache/original-readers/morphhb-src/morphhb-master/wlc"
VOCAB = ROOT / "data/originalReaders/vocabulary/hebrew-1000.json"
OUTPUT = ROOT / "output/source-cache/flashcards/hebrew-card-grammar.json"

WORD = re.compile(r'<w [^>]*lemma="([^"]+)"[^>]*morph="([^"]+)"[^>]*>([^<]+)</w>')
# 重音與吟誦符號在同一個詞的不同出處會變，母音點不會；比對字形前一律去掉。
ACCENTS = {chr(c) for c in range(0x0591, 0x05B0)} | {"ֽ", "־", "׀", "׃", "׆"}
GENDER_ZH = {"m": "陽性", "f": "陰性", "b": "陰陽性"}
NUMBER_ZH = {"p": "複數", "d": "雙數"}
STATE_ZH = {"c": "附屬形"}


def bare(form: str) -> str:
    """去掉重音與連字號，只留子音與母音點。"""

    text = unicodedata.normalize("NFC", form)
    return "".join(ch for ch in text if ch not in ACCENTS).strip()


def strong_of(segment: str) -> str | None:
    digits = re.match(r"\d+", segment.strip())
    return f"H{int(digits.group(0))}" if digits else None


def scan() -> tuple[dict, dict]:
    """回傳 (每個 Strong 的性別計數, 每個 (Strong, 字形) 的數／狀態計數)。"""

    genders: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    forms: dict[tuple[str, str], collections.Counter] = collections.defaultdict(collections.Counter)
    for book in sorted(WLC.glob("*.xml")):
        for lemma, morph, surface in WORD.findall(book.read_text(encoding="utf-8")):
            lemma_parts = lemma.split("/")
            morph_parts = morph.lstrip("H").split("/")
            if len(lemma_parts) != len(morph_parts):
                continue
            # 一個 <w> 可能是「前綴＋詞」，只取名詞或形容詞那一段。
            surface_parts = surface.split("/")
            for index, (lemma_part, code) in enumerate(zip(lemma_parts, morph_parts)):
                if not (code.startswith("Nc") or code.startswith("A")):
                    continue
                strong = strong_of(lemma_part)
                if strong is None or len(code) < 4:
                    continue
                gender, number, state = code[2], code[3], code[4] if len(code) > 4 else ""
                if code.startswith("A"):
                    gender, number, state = code[1], code[2], code[3] if len(code) > 3 else ""
                if gender in GENDER_ZH:
                    genders[strong][gender] += 1
                if index < len(surface_parts):
                    forms[(strong, bare(surface_parts[index]))][(number, state)] += 1
    return genders, forms


def gender_label(counts: collections.Counter) -> str | None:
    """多數決；兩性都夠份量才記陰陽性，資料太少就留白。"""

    total = counts["m"] + counts["f"] + counts["b"]
    if total < 3:
        return None
    if counts["b"] * 2 >= total:
        return "陰陽性"
    minor = min(counts["m"], counts["f"])
    if minor >= 5 and minor * 5 >= total:
        return "陰陽性"
    return GENDER_ZH["m"] if counts["m"] >= counts["f"] else GENDER_ZH["f"]


def main() -> None:
    parser = argparse.ArgumentParser(description="希伯來單字卡的性、數、狀態")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    genders, forms = scan()
    vocab = json.loads(VOCAB.read_text(encoding="utf-8"))
    # 附屬形只在「同一個 Strong 號有兩張以上的卡」時才印 —— 那正是需要分辨的場合
    # （אָב／אָבוֹת／אֲבִי 三張）。單獨一張卡印「附屬形」只會讓人以為那不是字典形。
    shared = {s for s, n in collections.Counter(e["strong"] for e in vocab).items() if n > 1 and s}
    records: dict[str, dict] = {}
    missing_gender: list[str] = []

    for entry in vocab:
        strong, pointed = entry["strong"], entry["pointed"]
        record: dict[str, str] = {}
        if entry.get("partOfSpeech") == "noun" and strong:
            label = gender_label(genders.get(strong, collections.Counter()))
            if label:
                record["gender"] = label
            else:
                missing_gender.append(f"{strong} {pointed}")
        tally = forms.get((strong, bare(pointed)))
        if tally:
            (number, _state), _ = tally.most_common(1)[0]
            if number in NUMBER_ZH:
                record["number"] = NUMBER_ZH[number]
            # 附屬形只標「這個字形本身只當附屬形用」的卡（אֲבִי、פְּנֵי、כָּל־）。
            # 絕大多數單數名詞的絕對形與附屬形同形（אֶ֫רֶץ、יוֹם、מֶ֫לֶךְ），
            # 那種卡按出現次數多數決會被誤標成附屬形，而卡上印的是絕對形。
            total = sum(tally.values())
            construct = sum(n for (_, state), n in tally.items() if state == "c")
            absolute = sum(n for (_, state), n in tally.items() if state == "a")
            if strong in shared and construct >= total * 0.9 and absolute <= 3:
                record["state"] = STATE_ZH["c"]
        if record:
            records[f"{strong}|{pointed}"] = record

    nouns = [e for e in vocab if e.get("partOfSpeech") == "noun"]
    print(f"  名詞 {len(nouns)}，其中標到性別 {len(nouns) - len(missing_gender)}，留白 {len(missing_gender)}")
    print(f"  標到數／狀態：複數 {sum(1 for r in records.values() if r.get('number') == '複數')}、"
          f"雙數 {sum(1 for r in records.values() if r.get('number') == '雙數')}、"
          f"附屬形 {sum(1 for r in records.values() if r.get('state'))}")
    if missing_gender:
        print("  性別留白（OSHB 出現不足或非聖經希伯來文）：")
        for item in missing_gender[:20]:
            print(f"      {item}")

    if args.write:
        OUTPUT.write_text(
            json.dumps(
                {
                    "schemaVersion": "1.0.0",
                    "source": "OSHB / morphhb (WLC 逐詞標註)",
                    "note": "性別取全書標註多數；數與狀態認這張卡的字形。查無標註就留白，不用字尾推。",
                    "cards": records,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"\n已寫出 {OUTPUT}")
    else:
        print("\n（未寫檔；加 --write 才會輸出）")


if __name__ == "__main__":
    main()
