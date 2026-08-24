#!/usr/bin/env python3
"""Lift biblical proper names out of the 1,000-word list and backfill it.

Person, place and people/nation names now live in their own appendix table, so
carrying them inside the lesson vocabulary would print the same word twice.
This script removes exactly those, then continues the reader's existing
corpus-frequency rule deeper into the lexicon to refill the list to 1,000.

Divine names and titles stay in the lessons.  יְהוָה occurs 6,521 times and
אֱלֹהִים 2,600; they are core reading vocabulary rather than index entries, and
a Biblical Hebrew reader that omits them teaches nothing.  The appendix still
lists them, cross-referenced to the lesson that introduces each one.

The frequency rule is not reimplemented here — the extractor's own functions are
imported, so the backfill continues the very same ordering that produced the
original extension.
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract_original_reader_vocab_sources import (  # noqa: E402
    STRONGS_HEBREW,
    count_morphhb_lemmas,
    fully_pointed_hebrew,
    gloss_has_ethnic_or_geographic_name,
    gloss_has_named_usage,
    infer_proper_name_types,
    load_js_dictionary,
    morphology_label,
    normalize_hebrew,
    transliterate_bbh,
)

ROOT = Path(__file__).resolve().parents[1]
VOCAB_PATH = ROOT / "data/originalReaders/vocabulary/hebrew-1000.json"
LIFTED_PATH = ROOT / "data/originalReaders/vocabulary/hebrew-proper-names.json"
GLOSS_PATH = ROOT / "output/source-cache/original-readers/hebrew-full/hebrew-gloss-zh-reviewed-by-lemma.json"
TARGET = 1000

# Only these three types leave the lesson list; see the module docstring.
LIFTED_TYPES = {"person", "place", "people_or_nation"}

# Strong's prose ("the name of four places in Palestine") is not a name-type
# parser, and it also flags common nouns whose consonants happen to double as a
# personal name.  Every backfill candidate the heuristic calls a name must be
# decided here by hand: a type list lifts it to the appendix, None keeps it in
# the lessons as an ordinary word.  An undecided candidate fails the run.
BACKFILL_NAME_DECISIONS: dict[str, list[str] | None] = {
    "H8283": ["person"],          # שָׂרָה 撒拉
    "H8398": None,                # תֵּבֵל 世界（普通名詞，非地名）
    "H7414": ["place"],           # רָמָה 拉瑪
    "H4709": ["place"],           # מִצְפָּה 米斯巴
    "H8227": None,                # שָׁפָן 岩狸（動物，字典義非人名）
    "H3812": ["person"],          # לֵאָה 利亞
    "H3876": ["person"],          # לוֹט 羅得
    "H8123": ["person"],          # שִׁמְשׁוֹן 參孫
    "H7141": ["person"],          # קֹרַח 可拉
    "H274": ["person"],           # אֲחַזְיָה 亞哈謝
    "H3079": ["person"],          # יְהוֹיָקִים 約雅敬
    "H1391": ["place"],           # גִּבְעוֹן 基遍
    "H5511": ["person"],          # סִיחוֹן 西宏
    "H3157": ["person", "place"], # יִזְרְעֵאל 耶斯列
    "H3612": ["person"],          # כָּלֵב 迦勒
    "H2574": ["place"],           # חֲמָת 哈馬
    "H5514": ["place"],           # סִינַי 西奈
    "H4318": ["person"],          # מִיכָה 米迦
    "H2518": ["person"],          # חִלְקִיָּה 希勒家
    "H5680": ["people_or_nation"],# עִבְרִי 希伯來人
    "H1661": ["place"],           # גַּת 迦特
    "H5941": ["person"],          # עֵלִי 以利
    "H1840": ["person"],          # דָנִיֵּאל 但以理
    "H6955": ["person"],          # קְהָת 哥轄
    "H1436": ["person"],          # גְּדַּלְיָה 基大利
    "H7887": ["place"],           # שִׁילֹה 示羅
}


# A few words carry a name flag but are ordinary vocabulary in practice, and
# dropping them would leave the reader unable to say "human", "south" or "the
# underworld".  אָדָם alone occurs 552 times, overwhelmingly as the common noun;
# BBH2 teaches it as one.  They stay in the lessons and the appendix lists them
# under their name sense with the lesson cross-reference.
KEEP_IN_LESSONS = {
    "H120": "אָדָם 人／人類（552 次，主要為普通名詞）",
    "H5045": "נֶגֶב 南方／尼革夫（方位詞）",
    "H7585": "שְׁאוֹל 陰間（普通名詞，非地名）",
    "H2975": "יְאֹר 河渠／尼羅河（普通名詞）",
}


def is_lifted(entry: dict) -> bool:
    if entry["strong"] in KEEP_IN_LESSONS:
        return False
    return bool(LIFTED_TYPES.intersection(entry.get("properNameTypes") or []))


def build_backfill(seen_strongs: set[str], needed: int) -> list[dict]:
    counts, morphs, _, _ = count_morphhb_lemmas()
    dictionary = load_js_dictionary(STRONGS_HEBREW)
    picked: list[dict] = []
    undecided: list[tuple[str, str, str]] = []
    for strong, frequency in counts.most_common():
        if len(picked) >= needed:
            break
        strong_key = f"H{int(strong)}"
        if strong_key in seen_strongs:
            continue
        entry = dictionary.get(strong_key)
        if not entry:
            continue
        pointed = unicodedata.normalize("NFC", entry.get("lemma", "").strip())
        normalized = normalize_hebrew(pointed)
        if not normalized or not fully_pointed_hebrew(pointed):
            continue
        dominant_morph = morphs[strong].most_common(1)[0][0] if morphs[strong] else ""
        part_of_speech = morphology_label(dominant_morph)
        gloss = entry.get("strongs_def", "").strip()
        proper_name_usage = (
            part_of_speech == "proper_name"
            or gloss_has_named_usage(gloss)
            or gloss_has_ethnic_or_geographic_name(gloss)
        )
        types = infer_proper_name_types(gloss, explicit=True) if proper_name_usage else []
        if proper_name_usage:
            if strong_key not in BACKFILL_NAME_DECISIONS:
                undecided.append((strong_key, pointed, gloss[:70]))
                seen_strongs.add(strong_key)
                continue
            decision = BACKFILL_NAME_DECISIONS[strong_key]
            if decision is None:
                proper_name_usage, types = False, []
            else:
                # Skip the very names the appendix now owns; keep walking down.
                seen_strongs.add(strong_key)
                continue
        picked.append(
            {
                "pointed": pointed,
                "sourcePointed": pointed,
                "unpointed": normalized,
                "unpointedVariants": [normalized],
                "textbookTransliteration": transliterate_bbh(pointed),
                "transliterationSystem": "Pratico-Van Pelt BBH2",
                "transliterationStatus": "rule_generated_exception_review",
                "glossEn": gloss,
                "glossZh": "",
                "sourceType": "reader_frequency_extension",
                "sourceChapter": None,
                "sourceOrder": None,
                "sourceOrders": [],
                "itemKind": "lexeme",
                "frequency": frequency,
                "frequencyStrong": strong_key,
                "strong": strong_key,
                "strongs": [strong_key],
                "partOfSpeech": part_of_speech,
                "isProperName": proper_name_usage,
                "properNameTypes": types,
                "verification": "lemma_frequency_verified",
                "languageVariety": (
                    "biblical_aramaic"
                    if "(Aramaic)" in (entry.get("derivation") or "")
                    else "biblical_hebrew"
                ),
            }
        )
        seen_strongs.add(strong_key)
    if undecided:
        lines = chr(10).join(f"    {key} {form}  {gloss}" for key, form, gloss in undecided)
        raise ValueError(
            "以下遞補候選被判為專名但尚未人工定奪，請在 BACKFILL_NAME_DECISIONS 補上：" + chr(10) + lines
        )
    if len(picked) != needed:
        raise ValueError(f"頻率延伸不足：需要 {needed} 詞，只找到 {len(picked)}")
    return picked


def main() -> None:
    parser = argparse.ArgumentParser(description="把人名／地名／民族國名移出 1000 詞並往下遞補")
    parser.add_argument("--write", action="store_true", help="寫回詞彙主檔與專名檔")
    args = parser.parse_args()

    entries = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
    if len(entries) != TARGET:
        raise ValueError(f"詞彙主檔應有 {TARGET} 詞，實得 {len(entries)}")
    entries.sort(key=lambda item: item["ordinal"])

    lifted = [item for item in entries if is_lifted(item)]
    if not lifted:
        print("  詞表已無待移出的專名，先前已執行過；不重複遞補。")
        return
    kept = [item for item in entries if not is_lifted(item)]
    seen = {strong for item in entries for strong in item.get("strongs") or [item["strong"]]}
    backfill = build_backfill(set(seen), TARGET - len(kept))

    for item in kept:
        if item["strong"] in KEEP_IN_LESSONS:
            item["keptInLessons"] = KEEP_IN_LESSONS[item["strong"]]

    textbook = [item for item in kept if item["sourceType"] == "bbh2_order"]
    extension = [item for item in kept if item["sourceType"] != "bbh2_order"] + backfill
    rebuilt = textbook + extension
    for index, item in enumerate(rebuilt, start=1):
        item["ordinal"] = index

    frequencies = [item["frequency"] or 0 for item in extension]
    if frequencies != sorted(frequencies, reverse=True):
        raise ValueError("頻率延伸段未維持由高到低排序")

    print(f"  移出專名 {len(lifted)} 筆（人名／地名／民族國名）")
    print(f"  保留 {len(kept)} 筆，遞補 {len(backfill)} 筆")
    print(f"  遞補頻率區間 {backfill[0]['frequency']}–{backfill[-1]['frequency']} 次")
    print(f"  合計 {len(rebuilt)} 詞")

    remaining = [item for item in rebuilt if item.get("isProperName")]
    print(f"  課內仍保留的專名 {len(remaining)} 筆（神名／稱號、安息日與 {len(KEEP_IN_LESSONS)} 個普通名詞）")
    for item in rebuilt:
        if item["strong"] in KEEP_IN_LESSONS:
            print(f"      留課：{KEEP_IN_LESSONS[item['strong']]}")

    if not args.write:
        print("（未寫檔；加 --write 才會更新主檔）")
        return

    from assign_hebrew_lessons import assign

    assign(rebuilt)
    VOCAB_PATH.write_text(json.dumps(rebuilt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    gloss_index = {
        (item["strong"], item["pointed"]): item["glossZh"]
        for item in json.loads(GLOSS_PATH.read_text(encoding="utf-8"))["items"]
    }
    LIFTED_PATH.write_text(
        json.dumps(
            {
                "schemaVersion": "1.0.0",
                "note": "自 1000 詞課表移出的聖經專名，改由附錄「分類專名表」收錄。",
                "items": [
                    {**item, "glossZh": gloss_index.get((item["strong"], item["pointed"]), "")}
                    for item in lifted
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"已寫回 {VOCAB_PATH}")
    print(f"已寫出 {LIFTED_PATH}")


if __name__ == "__main__":
    main()
