#!/usr/bin/env python3
"""Assemble the Hebrew reader's four appendix reference tables.

Numerals, kinship terms and the calendar were never a category in the reader:
they landed wherever the textbook order and corpus frequency happened to put
them, so a learner could not look up "the months" or "the ordinals" anywhere.
The proper names had the opposite problem -- they were scattered through the
lesson vocabulary, which is why they have now been lifted out entirely.

Nothing here is authored free-hand.  Every pointed form is either taken from a
word already in the reader's own vocabulary master or pulled from the WLC text
itself, the transliteration comes from the reader's BBH2 rule engine, and the
frequency and first occurrence are counted from the corpus.  The five Babylonian
month names that never appear in the Masoretic Text are marked as such and carry
their own source note rather than being quietly presented as biblical.
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract_original_reader_vocab_sources import transliterate_bbh  # noqa: E402
from hebrew_appendix.lexicon import (  # noqa: E402
    attested_form,
    consonants,
    reference_zh,
    strongs_index,
    wlc_occurrences,
    wlc_surface_forms,
)

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data/originalReaders/vocabulary/hebrew-appendix-seed.json"
VOCAB = ROOT / "data/originalReaders/vocabulary/hebrew-1000.json"
NAMES = ROOT / "data/originalReaders/vocabulary/hebrew-proper-names.json"
GLOSSES = ROOT / "output/source-cache/original-readers/hebrew-full/hebrew-gloss-zh-reviewed-by-lemma.json"
OUTPUT = ROOT / "output/source-cache/original-readers/hebrew-full/appendix-tables.json"

NAME_TYPE_SECTIONS = [
    ("person", "人名"),
    ("place", "地名"),
    ("people_or_nation", "民族與國名"),
    ("divine_name_or_title", "神名與稱號"),
    ("festival_or_sacred_time", "節期與聖日"),
]


class Failure(Exception):
    pass


def resolve_form(
    strong: str | None,
    skeleton: str | None,
    pointed: str | None,
    label: str,
    form_source: str = "wlc",
) -> tuple[str, int]:
    """Return an attested pointed spelling plus how often the WLC writes it.

    ``form_source="lexicon"`` covers the handful of kinship words that the
    Masoretic Text only ever writes with a pronominal suffix -- חֲמוֹת, יָבָם and
    friends have no absolute occurrence to quote -- so their citation form comes
    from Strong's instead, and the row says so.
    """

    if form_source == "lexicon":
        if not strong:
            raise Failure(f"{label}：formSource=lexicon 仍需要 strong")
        lemma = unicodedata.normalize("NFC", strongs_index()[strong]["lemma"])
        if not lemma:
            raise Failure(f"{label}：Strong 詞典沒有 {strong} 的引用形")
        if wlc_surface_forms().get(strong):
            attested = any(
                consonants(form) == skeleton for form in wlc_surface_forms()[strong]
            )
            if attested:
                raise Failure(f"{label}：{strong} 在 WLC 有獨立形，不該標 formSource=lexicon")
        return lemma, 0
    if strong is None:
        if not pointed:
            raise Failure(f"{label}：沒有 strong 就必須自行給 pointed")
        return unicodedata.normalize("NFC", pointed), 0
    forms = wlc_surface_forms().get(strong, {})
    if pointed:
        pointed = unicodedata.normalize("NFC", pointed)
        count = forms.get(pointed)
        if not count:
            raise Failure(f"{label}：指定的附點形 {pointed} 未見於 WLC（{strong}）")
        return pointed, count
    if not skeleton:
        raise Failure(f"{label}：缺 skeleton")
    matches = [form for form in forms if consonants(form) == skeleton]
    if not matches:
        raise Failure(f"{label}：WLC 中找不到 {strong} 的 {skeleton} 寫法")
    if len({form for form in matches}) > 1:
        best = sorted(((forms[form], form) for form in matches), reverse=True)
        if best[0][0] == best[1][0]:
            raise Failure(f"{label}：{strong}／{skeleton} 有多個同頻寫法 {[f for _, f in best[:3]]}，請以 pointed 指定")
    form, count = max(((forms[form], form) for form in matches))[::-1]
    return form, count


def build_seed_tables(lesson_by_lemma: dict[tuple[str, str], int]) -> list[dict]:
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    index = strongs_index()
    counts, first = wlc_occurrences()
    tables = []
    for table in seed["tables"]:
        groups = []
        for group in table["groups"]:
            post_biblical = group.get("attestation") == "post_biblical"
            rows = []
            for entry in group["entries"]:
                label = f"{table['id']}/{group['id']}/{entry.get('value') or entry.get('order') or entry.get('skeleton')}"
                strong = entry.get("strong")
                if strong and strong not in index:
                    raise Failure(f"{label}：Strong 詞典查無 {strong}")
                if post_biblical and strong:
                    raise Failure(f"{label}：標為 post_biblical 就不該有 strong")
                row = {
                    "glossZh": entry["glossZh"],
                    "strong": strong,
                    "attestation": "post_biblical" if post_biblical else "masoretic_text",
                }
                for optional in ("value", "order", "note"):
                    if entry.get(optional):
                        row[optional] = entry[optional]
                if group["shape"] == "gender_pair":
                    for gender, key in (("masculine", "masculine"), ("feminine", "feminine")):
                        form, seen = resolve_form(
                            strong,
                            entry[key],
                            entry.get(f"{gender}Pointed"),
                            f"{label}/{gender}",
                            entry.get("formSource", "wlc"),
                        )
                        row[gender] = {
                            "pointed": form,
                            "transliteration": transliterate_bbh(form),
                            "wlcSpellingCount": seen,
                        }
                else:
                    form, seen = resolve_form(
                        strong,
                        entry.get("skeleton"),
                        entry.get("pointed"),
                        label,
                        entry.get("formSource", "wlc"),
                    )
                    row["pointed"] = form
                    row["transliteration"] = transliterate_bbh(form)
                    row["wlcSpellingCount"] = seen
                    if entry.get("formSource") == "lexicon":
                        row["formSource"] = "lexicon"
                if strong:
                    row["frequency"] = counts.get(strong, 0)
                    row["firstOccurrence"] = reference_zh(first.get(strong))
                    if not row["frequency"]:
                        raise Failure(f"{label}：{strong} 在 WLC 中沒有出現，卻標為經文用字")
                    key = next(
                        (
                            pair
                            for pair in lesson_by_lemma
                            if pair[0] == strong and pair[1] == row.get("pointed")
                        ),
                        None,
                    )
                    if key:
                        row["lesson"] = lesson_by_lemma[key]
                rows.append(row)
            assembled = {
                "id": group["id"],
                "titleZh": group["titleZh"],
                "shape": group["shape"],
            }
            for optional in ("note", "source"):
                if group.get(optional):
                    assembled[optional] = group[optional]
            assembled["entries"] = rows
            groups.append(assembled)
        tables.append(
            {
                "id": table["id"],
                "titleZh": table["titleZh"],
                "titleHe": table["titleHe"],
                "intro": table["intro"],
                "groups": groups,
                "entryCount": sum(len(group["entries"]) for group in groups),
            }
        )
    return tables


def build_name_table(lesson_by_lemma: dict[tuple[str, str], int]) -> dict:
    lifted = json.loads(NAMES.read_text(encoding="utf-8"))["items"]
    vocab = json.loads(VOCAB.read_text(encoding="utf-8"))
    glosses = {
        (item["strong"], item["pointed"]): item["glossZh"]
        for item in json.loads(GLOSSES.read_text(encoding="utf-8"))["items"]
    }
    counts, first = wlc_occurrences()

    pool: list[dict] = []
    for item in lifted:
        if not item.get("glossZh"):
            raise Failure(f"專名 {item['pointed']} 缺繁中義")
        pool.append({**item, "inLesson": None})
    for item in vocab:
        if item.get("isProperName"):
            gloss = glosses.get((item["strong"], item["pointed"]))
            if not gloss:
                raise Failure(f"課內專名 {item['pointed']} 缺繁中義")
            pool.append({**item, "glossZh": gloss, "inLesson": item["lesson"]})

    groups = []
    for type_key, title in NAME_TYPE_SECTIONS:
        rows = []
        for item in pool:
            if type_key not in (item.get("properNameTypes") or []):
                continue
            row = {
                "pointed": item["pointed"],
                "transliteration": item["textbookTransliteration"],
                "glossZh": item["glossZh"],
                "types": item["properNameTypes"],
                "strong": item["strong"],
                "frequency": counts.get(item["strong"], item.get("frequency") or 0),
                "firstOccurrence": reference_zh(first.get(item["strong"])),
            }
            if item["inLesson"]:
                row["lesson"] = item["inLesson"]
            rows.append(row)
        rows.sort(key=lambda row: (-row["frequency"], row["pointed"]))
        if not rows:
            raise Failure(f"專名分類「{title}」是空的")
        groups.append({"id": type_key, "titleZh": title, "shape": "name", "entries": rows})

    return {
        "id": "hbo-appendix-proper-names",
        "titleZh": "分類專名表",
        "titleHe": "שֵׁמוֹת פְּרָטִיִּים",
        "intro": (
            "人名、地名與民族國名已自五十課詞表移出，全部收在本表，按類分節、依出現次數排序，"
            "因此課文詞表與本表不重複。神名、稱號與安息日仍留在課內學習，本表一併收錄並標出所在課次。"
        ),
        "groups": groups,
        "entryCount": sum(len(group["entries"]) for group in groups),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="組裝希伯來讀本的四張附錄對照表")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    vocab = json.loads(VOCAB.read_text(encoding="utf-8"))
    lesson_by_lemma = {(item["strong"], item["pointed"]): item["lesson"] for item in vocab}

    tables = build_seed_tables(lesson_by_lemma)
    tables.append(build_name_table(lesson_by_lemma))

    document = {
        "schemaVersion": "1.0.0",
        "note": (
            "附錄對照表。附點形取自 WLC 實際經文或讀本詞表，音標由 BBH2 規則產生，"
            "出現次數與首次出現章節由 WLC 統計；不見於馬所拉經文者標 post_biblical 並註明來源。"
        ),
        "sources": {
            "text": "Open Scriptures Hebrew Bible / Westminster Leningrad Codex 4.20",
            "lexicon": "Strong's Concise Dictionary of the Words in the Hebrew Bible (1894, 公有領域)",
            "transliteration": "Pratico–Van Pelt, Basics of Biblical Hebrew 2/e 音標體例",
        },
        "tables": tables,
    }

    for table in tables:
        print(f"  {table['titleZh']}：{table['entryCount']} 條 / {len(table['groups'])} 節")
        for group in table["groups"]:
            print(f"      {group['titleZh']}  {len(group['entries'])}")
    print(f"  合計 {sum(table['entryCount'] for table in tables)} 條")

    if not args.write:
        print("（未寫檔；加 --write 才會輸出）")
        return
    OUTPUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已寫出 {OUTPUT}")


if __name__ == "__main__":
    try:
        main()
    except Failure as error:
        print(f"[FAIL] {error}", file=sys.stderr)
        sys.exit(1)
