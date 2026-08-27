#!/usr/bin/env python3
"""Per-word parsing for the original-language columns of /scripture.

The owner asked for what 信望愛 does: hover a Greek or Hebrew word and see its
Chinese meaning, its part of speech, and its parsing — case, number, gender for
a noun; stem, aspect and person for a Hebrew verb. Both halves of that already
sit in this checkout and neither needs anybody's permission:

* **Greek** — MorphGNT's tagging of the SBLGNT
  (`…/greek-full/sources/sblgnt`), one line per word: a book-chapter-verse
  key, a part-of-speech code, an eight-character parsing code, the word as
  printed, and its lemma.
* **Hebrew** — OSHB/morphhb's tagging of the Westminster Leningrad Codex
  (`…/morphhb-src/morphhb-master/wlc`), one `<w>` per word carrying a
  Strong-number lemma and a morph code, both segmented by `/` where a word
  carries prefixes: `b/7225`, `HR/Ncfsa` is a preposition plus a feminine
  singular noun.

This turns both into one shape — a verse is a list of words, a word carries
`text`, `lemma`, `strong`, `pos` and `parsing`, all in Traditional Chinese —
and leaves the Chinese *meaning* to whatever register covers it, because that
is a separate question with a separate answer per language.

    python -X utf8 scripts/build_scripture_morphology.py --language greek --limit 2
    python -X utf8 scripts/build_scripture_morphology.py --write
"""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SBLGNT = ROOT / "output/source-cache/original-readers/greek-full/sources/sblgnt"
WLC = ROOT / "output/source-cache/original-readers/morphhb-src/morphhb-master/wlc"
OUT = ROOT / "output/source-cache/scripture/morphology"

# ── 希臘文 ────────────────────────────────────────────────────────────────
GREEK_POS = {
    "N-": "名詞", "V-": "動詞", "A-": "形容詞", "D-": "副詞", "C-": "連接詞",
    "P-": "介系詞", "X-": "質詞", "I-": "感嘆詞", "RA": "冠詞", "RP": "人稱代名詞",
    "RD": "指示代名詞", "RI": "疑問／不定代名詞", "RR": "關係代名詞",
}
GREEK_PERSON = {"1": "第一人稱", "2": "第二人稱", "3": "第三人稱"}
GREEK_TENSE = {"P": "現在", "I": "未完成", "F": "未來", "A": "簡單過去", "X": "完成", "Y": "過去完成"}
GREEK_VOICE = {"A": "主動", "M": "關身", "P": "被動"}
GREEK_MOOD = {"I": "直說", "D": "命令", "S": "假設", "O": "祈願", "N": "不定詞", "P": "分詞"}
GREEK_CASE = {"N": "主格", "G": "屬格", "D": "與格", "A": "受格", "V": "呼格"}
GREEK_NUMBER = {"S": "單數", "P": "複數"}
GREEK_GENDER = {"M": "陽性", "F": "陰性", "N": "中性"}
GREEK_DEGREE = {"C": "比較級", "S": "最高級"}


def greek_parsing(code: str) -> str:
    """MorphGNT's eight characters, read left to right, in Chinese."""

    slots = [
        (0, GREEK_PERSON), (1, GREEK_TENSE), (2, GREEK_VOICE), (3, GREEK_MOOD),
        (4, GREEK_CASE), (5, GREEK_NUMBER), (6, GREEK_GENDER), (7, GREEK_DEGREE),
    ]
    parts = []
    for index, table in slots:
        if index < len(code):
            label = table.get(code[index])
            if label:
                parts.append(label)
    return "".join(parts)


def greek_books() -> dict[str, list[dict]]:
    """Every SBLGNT word, keyed 'Matt.1.1'."""

    # MorphGNT names its files 61-Mt-morphgnt.txt; the OSIS book code is what
    # the rest of this project keys on, so map once here rather than everywhere.
    codes = {
        "Mt": "Matt", "Mk": "Mark", "Lk": "Luke", "Jn": "John", "Ac": "Acts",
        "Ro": "Rom", "1Co": "1Cor", "2Co": "2Cor", "Ga": "Gal", "Eph": "Eph",
        "Php": "Phil", "Col": "Col", "1Th": "1Thess", "2Th": "2Thess",
        "1Ti": "1Tim", "2Ti": "2Tim", "Tit": "Titus", "Phm": "Phlm", "Heb": "Heb",
        "Jas": "Jas", "1Pe": "1Pet", "2Pe": "2Pet", "1Jn": "1John", "2Jn": "2John",
        "3Jn": "3John", "Jud": "Jude", "Re": "Rev",
    }
    verses: dict[str, list[dict]] = {}
    for path in sorted(SBLGNT.glob("*-morphgnt.txt")):
        short = path.name.split("-")[1]
        book = codes.get(short, short)
        for line in path.read_text(encoding="utf-8").splitlines():
            fields = line.split()
            if len(fields) < 7:
                continue
            key, pos, parse, text, word, normalised, lemma = fields[:7]
            ref = f"{book}.{int(key[2:4])}.{int(key[4:6])}"
            verses.setdefault(ref, []).append(
                {
                    "text": text,
                    "lemma": lemma,
                    "pos": GREEK_POS.get(pos, pos),
                    "parsing": greek_parsing(parse),
                    "code": parse,
                }
            )
    return verses


# ── 希伯來文 ──────────────────────────────────────────────────────────────
# OSHB 的 morph 碼：語言字母（H）之後，每個語素一段，用 / 分開。
HEBREW_PART = {
    "A": "形容詞", "C": "連接詞", "D": "副詞", "N": "名詞", "P": "代名詞",
    "R": "介系詞", "S": "詞尾", "T": "質詞", "V": "動詞",
}
HEBREW_NOUN_TYPE = {"c": "普通", "g": "專有", "p": "專有"}
HEBREW_STEM = {
    "q": "Qal", "N": "Niphal", "p": "Piel", "P": "Pual", "h": "Hiphil",
    "H": "Hophal", "t": "Hithpael", "o": "Polel", "O": "Polal", "r": "Poel",
}
HEBREW_ASPECT = {
    "p": "完成", "q": "敘述式", "i": "未完成", "w": "連續未完成", "h": "勸告式",
    "j": "祈使式", "v": "命令", "r": "主動分詞", "s": "被動分詞",
    "a": "不定詞絕對", "c": "不定詞附屬",
}
HEBREW_PERSON = {"1": "第一人稱", "2": "第二人稱", "3": "第三人稱"}
HEBREW_GENDER = {"m": "陽性", "f": "陰性", "b": "通性", "c": "通性"}
HEBREW_NUMBER = {"s": "單數", "p": "複數", "d": "雙數"}
HEBREW_STATE = {"a": "絕對式", "c": "附屬式", "d": "強調式"}
HEBREW_PARTICLE = {
    "a": "感嘆詞", "d": "定冠詞", "e": "疑問詞", "i": "間投詞",
    "j": "指示詞", "m": "指示詞", "n": "否定詞", "o": "受詞記號", "r": "關係詞",
}


def hebrew_segment(code: str) -> str:
    """One morpheme's code, in Chinese. Returns '' for what it cannot read."""

    if not code:
        return ""
    part = HEBREW_PART.get(code[0], "")
    rest = code[1:]
    if code[0] == "V":
        labels = [part]
        if rest[:1] in HEBREW_STEM:
            labels.append(HEBREW_STEM[rest[:1]])
        if rest[1:2] in HEBREW_ASPECT:
            labels.append(HEBREW_ASPECT[rest[1:2]])
        for char in rest[2:]:
            for table in (HEBREW_PERSON, HEBREW_GENDER, HEBREW_NUMBER, HEBREW_STATE):
                if char in table:
                    labels.append(table[char])
                    break
        return "".join(labels)
    if code[0] == "N":
        labels = [part]
        if rest[:1] in HEBREW_NOUN_TYPE:
            labels.append(HEBREW_NOUN_TYPE[rest[:1]] if rest[0] != "c" else "")
        for char in rest[1:]:
            for table in (HEBREW_GENDER, HEBREW_NUMBER, HEBREW_STATE):
                if char in table:
                    labels.append(table[char])
                    break
        return "".join(label for label in labels if label)
    if code[0] == "T":
        return HEBREW_PARTICLE.get(rest[:1], part)
    if code[0] in ("A", "P", "S"):
        labels = [part]
        for char in rest:
            for table in (HEBREW_PERSON, HEBREW_GENDER, HEBREW_NUMBER, HEBREW_STATE):
                if char in table:
                    labels.append(table[char])
                    break
        return "".join(labels)
    return part


CONTENT_PARTS = ("V", "N", "A", "D", "P")


def head_part(segments: list[str]) -> str:
    """The part of speech of the word itself, not of its prefixes or suffix."""

    for segment in segments:
        if segment[:1] in CONTENT_PARTS:
            return HEBREW_PART.get(segment[0], "")
    return HEBREW_PART.get(segments[-1][:1], "") if segments else ""


def hebrew_books() -> dict[str, list[dict]]:
    """Every WLC word, keyed 'Gen.1.1'."""

    namespace = {"osis": "http://www.bibletechnologies.net/2003/OSIS/namespace"}
    verses: dict[str, list[dict]] = {}
    for path in sorted(WLC.glob("*.xml")):
        tree = ET.parse(path)
        for verse in tree.iter():
            if not verse.tag.endswith("verse") or "osisID" not in verse.attrib:
                continue
            ref = verse.attrib["osisID"]
            words = []
            for word in verse:
                if not word.tag.endswith("w"):
                    continue
                text = "".join(word.itertext())
                morph = (word.attrib.get("morph") or "").lstrip("H")
                lemma = word.attrib.get("lemma") or ""
                segments = morph.split("/")
                # 詞素與 Strong 編號一段一段對齊；前綴（介系詞、冠詞、連接詞）
                # 各有自己的編號字母，真正的字頭是最後那個數字。
                numbers = re.findall(r"\d+", lemma)
                words.append(
                    {
                        "text": text,
                        "lemma": lemma,
                        "strong": f"H{int(numbers[-1]):04d}" if numbers else "",
                        # 詞性看實詞語素：介系詞、連接詞、冠詞是前綴，人稱詞尾
                        # 是後綴，兩邊都不是這個字的詞性。רֹעִי 是「牧養」的分詞
                        # 加我的詞尾，詞性是動詞而不是詞尾。
                        "pos": head_part(segments),
                        "parsing": "＋".join(
                            label for label in (hebrew_segment(s) for s in segments) if label
                        ),
                        "code": morph,
                    }
                )
            if words:
                verses[ref] = words
    return verses


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=("greek", "hebrew", "both"), default="both")
    parser.add_argument("--limit", type=int, default=0, help="只印前 N 節看看")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    for language in (("greek", "hebrew") if args.language == "both" else (args.language,)):
        verses = greek_books() if language == "greek" else hebrew_books()
        words = sum(len(v) for v in verses.values())
        print(f"{language}：{len(verses)} 節、{words} 個詞")
        for ref in list(verses)[: args.limit]:
            print(f"  {ref}")
            for word in verses[ref]:
                print(f"    {word['text']:<20} {word['lemma']:<16} {word['pos']:<8} {word['parsing']}")
        if args.write:
            OUT.mkdir(parents=True, exist_ok=True)
            path = OUT / f"{language}.json"
            path.write_text(
                json.dumps(
                    {
                        "schemaVersion": "1.0.0",
                        "language": language,
                        "source": (
                            "MorphGNT / SBLGNT" if language == "greek"
                            else "OSHB / morphhb（Westminster Leningrad Codex）"
                        ),
                        "verses": len(verses),
                        "words": words,
                        "byVerse": verses,
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            print(f"  已寫入 {path.relative_to(ROOT)}（{path.stat().st_size / 1_000_000:.1f} MB）")
    if not args.write:
        print("（未寫入；加 --write）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
