#!/usr/bin/env python3
"""Correct the interlinear layer's Hebrew function words from OSHB morphology.

Two error classes survive any prompt wording because they need grammatical
information the model has to infer:

* ``אֵת``/``אֶת`` is both the untranslatable direct-object marker and the
  preposition "with".  A gloss of 「與」 on the marker is simply wrong, and the
  first Haiku pass produced 214 of them against 149 correct ones.
* The definite article ``הַ`` is not a demonstrative.  Chinese needs no word for
  it, yet 421 tokens came back as 「這天」「這水」.  Genuine demonstratives
  (``הַזֶּה``) must keep 「這」, and for a few time words the article really does
  mean "this/today", so those are left alone.

OSHB tags every word: ``To`` = object marker, ``R`` = preposition, ``Td`` =
article, ``Pd`` = demonstrative.  That settles both cases without a model.
Scripture only — the prayers and the Haggadah have no morphological layer.
"""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "hebrew-full"
WLC = CACHE.parent / "morphhb-src" / "morphhb-master" / "wlc"
MASTER = CACHE / "interlinear.json"
OSIS_NS = {"osis": "http://www.bibletechnologies.net/2003/OSIS/namespace"}

CANTILLATION = re.compile(r"[֑-֯]")
NIQQUD = re.compile(r"[ְ-ׇּׁׂ]")
OBJECT_MARKER = "（受詞記號）"

# With these nouns the article genuinely carries "this / today / tonight", so a
# leading 「這」 is not an error.
TIME_WORDS = {"יום", "לילה", "שנה", "פעם", "בקר", "ערב", "שבת", "חדש"}


def consonants(text: str) -> str:
    return NIQQUD.sub("", CANTILLATION.sub("", text)).replace("־", "").strip()


def verse_morphs(book: str) -> dict[str, list[tuple[str, str]]]:
    """(surface, morph) per word, keyed by verse ref."""
    tree = ET.parse(WLC / f"{book}.xml")
    output: dict[str, list[tuple[str, str]]] = {}
    for verse in tree.iter(f"{{{OSIS_NS['osis']}}}verse"):
        ref = verse.get("osisID") or ""
        if not ref:
            continue
        words = []
        for word in verse.findall(f"{{{OSIS_NS['osis']}}}w"):
            surface = "".join(word.itertext()).replace("/", "").strip()
            words.append((surface, word.get("morph", "")))
        if words:
            output[ref] = words
    return output


def corrected_gloss(token: dict, morph: str, gloss: str) -> str | None:
    """Return a corrected gloss, or None to leave it as it is."""
    parts = morph.removeprefix("H").split("/")
    has_conjunction = parts and parts[0] == "C"

    # אֹתָם / אֶתְכֶם carry a pronominal suffix: the marker still has to be
    # translated ("them", "you"), so only the bare marker may be replaced.
    has_suffix = any(part.startswith("Sp") for part in parts)
    if "To" in parts and not has_suffix:
        want = f"並{OBJECT_MARKER}" if has_conjunction else OBJECT_MARKER
        return None if gloss == want else want

    if "Td" in parts and not any(part.startswith("Pd") for part in parts):
        if gloss.startswith("這") and len(gloss) > 1:
            if consonants(token["word"]).lstrip("הו") in TIME_WORDS:
                return None
            # 「這些木頭」 must lose both characters; stripping only 「這」 would
            # leave the dangling measure word 「些」.
            stripped = gloss[2:] if gloss.startswith("這些") else gloss[1:]
            stripped = stripped.lstrip("…")
            return stripped or None
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="用 OSHB 詞法標記校正逐詞對譯的虛詞")
    parser.add_argument("--write", action="store_true", help="寫回主檔")
    args = parser.parse_args()

    master = json.loads(MASTER.read_text(encoding="utf-8"))
    units = master["units"]
    books = {
        unit["ref"].split(".")[0]
        for unit in units.values()
        if unit["kind"] in ("bible_verse", "memory_verse")
    }
    morphs: dict[str, list[tuple[str, str]]] = {}
    for book in sorted(books):
        morphs.update(verse_morphs(book))

    changed = Counter()
    skipped: list[str] = []
    for unit in units.values():
        if unit["kind"] not in ("bible_verse", "memory_verse"):
            continue
        words = morphs.get(unit["ref"])
        tokens = unit["tokens"]
        if not words or len(words) != len(tokens):
            skipped.append(unit["ref"])
            continue
        for token, (surface, morph) in zip(tokens, words):
            # Qere spellings differ from the ketiv in the morphology file; only
            # correct where the two layers clearly describe the same word.
            if consonants(surface) != consonants(token["word"]):
                continue
            fixed = corrected_gloss(token, morph, token["glossZh"].strip())
            if fixed is not None and fixed != token["glossZh"]:
                changed[(token["glossZh"], fixed)] += 1
                if args.write:
                    token["glossZh"] = fixed

    total = sum(changed.values())
    print(f"可校正 {total} 個詞義；對不上詞法層而略過 {len(skipped)} 節")
    for (before, after), count in changed.most_common(15):
        print(f"  「{before}」→「{after}」 ×{count}")
    if args.write:
        MASTER.write_text(json.dumps(master, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已寫回 {MASTER}")
    else:
        print("（未寫檔；加 --write 才更新）")


if __name__ == "__main__":
    main()
