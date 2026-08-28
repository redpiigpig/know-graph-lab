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


GREEK_SLOTS = [
    (0, "人稱", GREEK_PERSON), (1, "時態", GREEK_TENSE), (2, "語態", GREEK_VOICE),
    (3, "語氣", GREEK_MOOD), (4, "格", GREEK_CASE), (5, "數", GREEK_NUMBER),
    (6, "性", GREEK_GENDER), (7, "級", GREEK_DEGREE),
]


def greek_features(code: str) -> list[dict]:
    """MorphGNT 的八格，一格一列，帶欄名。

    原本只回傳「主格單數陰性」這樣一串——讀得懂的人才讀得懂。使用者要的是
    每一項都寫出來：格是格、數是數、性是性。
    """

    rows = []
    for index, label, table in GREEK_SLOTS:
        if index < len(code):
            value = table.get(code[index])
            if value:
                rows.append({"label": label, "value": value})
    return rows


def greek_parsing(code: str) -> str:
    """同樣的內容串成一行，給不想展開的地方用。"""

    return "".join(item["value"] for item in greek_features(code))


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
                    "features": [{"label": "詞性", "value": GREEK_POS.get(pos, pos)}]
                    + greek_features(parse),
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


PREFIX_PARTS = {"R": "介系詞", "C": "連接詞", "T": "冠詞／質詞"}


def hebrew_features(segments: list[str]) -> list[dict]:
    """OSHB 的碼，一項一列，帶欄名。

    希伯來一個「字」常是好幾個語素：介系詞＋冠詞＋名詞＋人稱詞尾。所以前綴與
    詞尾各自列出來，實詞的語幹、時態、人稱、性、數、狀態再逐項列——使用者要的
    是「詞性、格、性、數」都寫出來，不是一串看得懂才看得懂的黏著標記。
    """

    rows: list[dict] = []
    head_seen = False
    for segment in segments:
        if not segment:
            continue
        part = segment[0]
        rest = segment[1:]
        if part in PREFIX_PARTS and not head_seen:
            rows.append({"label": "前綴", "value": HEBREW_PARTICLE.get(rest[:1], PREFIX_PARTS[part])})
            continue
        if part == "S":
            # 跳過類別碼（p 代名詞／d 指示／h 冠詞）再讀人稱性數。
            body = rest[1:] if rest[:1] in ("p", "d", "h") else rest
            rows.append({"label": "詞尾", "value": _affix(body) or "人稱詞尾"})
            continue
        head_seen = True
        rows.append({"label": "詞性", "value": HEBREW_PART.get(part, part)})
        if part == "V":
            if rest[:1] in HEBREW_STEM:
                rows.append({"label": "語幹", "value": HEBREW_STEM[rest[:1]]})
            if rest[1:2] in HEBREW_ASPECT:
                rows.append({"label": "時態", "value": HEBREW_ASPECT[rest[1:2]]})
            # 限定動詞是人稱性數；分詞與不定詞是性數狀態。
            finite = rest[1:2] not in ("r", "s", "a", "c")
            rows.extend(_named(rest[2:], ("人稱", "性", "數") if finite else ("性", "數", "狀態")))
        elif part == "N":
            if rest[:1] in ("g", "p"):
                rows.append({"label": "類別", "value": "專有名詞"})
            rows.extend(_named(rest[1:], ("性", "數", "狀態")))
        elif part == "T":
            rows.append({"label": "類別", "value": HEBREW_PARTICLE.get(rest[:1], "質詞")})
        else:
            rows.extend(_named(rest, ("人稱", "性", "數")))
    return rows


def _named(code: str, labels: tuple[str, ...]) -> list[dict]:
    """按位置讀，不要按查表順序讀。

    OSHB 的碼是定位的：名詞是「性數狀態」，限定動詞是「人稱性數」。若改成
    「哪張表查得到就算哪一項」，`Ncmsc` 末尾的 c 會先在性別表裡命中「通性」，
    於是 בְּנוֹ 印成「陽性單數通性」——實際上那個 c 是附屬式。
    """

    tables = {
        "人稱": HEBREW_PERSON, "性": HEBREW_GENDER,
        "數": HEBREW_NUMBER, "狀態": HEBREW_STATE,
    }
    rows = []
    for char, label in zip(code, labels):
        value = tables[label].get(char)
        if value:
            rows.append({"label": label, "value": value})
    return rows


def _affix(code: str) -> str:
    return "".join(item["value"] for item in _named(code, ("人稱", "性", "數")))


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
                        "features": hebrew_features(segments),
                        "code": morph,
                    }
                )
            if words:
                verses[ref] = words
    return verses


def fold(text: str) -> str:
    """比對希臘詞位時把重音折掉：兩邊的送氣與重音標法不一致。"""

    import unicodedata

    return "".join(
        c for c in unicodedata.normalize("NFD", text) if not unicodedata.combining(c)
    ).lower()


def glossary() -> tuple[dict[str, dict], dict[str, dict], dict[str, dict]]:
    """The Chinese this project has already reviewed, keyed for lookup.

    Greek by lemma (the reader's 2,000 words), Hebrew by Strong number (its
    1,000). Nothing else is invented: a word this project has not glossed shows
    its parsing and its lemma and an empty meaning, which is the honest state.
    Filling the rest means either translating them here or licensing a Chinese
    lexicon — a decision, not a default.
    """

    greek: dict[str, dict] = {}
    path = ROOT / "output/source-cache/original-readers/greek-full/greek-reader-two-volumes.json"
    if path.exists():
        master = json.loads(path.read_text(encoding="utf-8"))
        for volume in master["volumes"]:
            for lesson in volume["lessons"]:
                for word in lesson["vocabulary"]:
                    greek.setdefault(
                        word["lemma"],
                        {"zh": word.get("glossZh", ""), "en": word.get("glossEn", "")},
                    )

    hebrew: dict[str, dict] = {}
    # 信望愛的中文原文字典（使用者 2026-08-28 取得私人使用授權）。本專案自己
    # 覆核過的詞義仍然優先——那是為這幾本讀本寫的、跟讀本印出來的一致；字典
    # 補的是覆核不到的那一半，尤其是罕用字。
    fhl_path = ROOT / "output/source-cache/scripture/fhl-strong-dictionary.json"
    fhl: dict[str, dict] = {}
    if fhl_path.exists():
        for key, entry in json.loads(fhl_path.read_text(encoding="utf-8"))["entries"].items():
            senses = entry.get("senses") or []
            if senses:
                # 只取分項義的前三條，一個 hover 卡片放不下整條字典。
                fhl[key] = {"zh": "；".join(s.split(") ", 1)[-1] for s in senses[:3])}

    # 覆核過的希伯來詞義在組好的主檔裡，不在 vocabulary/hebrew-1000.json——
    # 那一份的 glossZh 是空的，照它查會得到零筆而且不會報錯。
    path = ROOT / "output/source-cache/original-readers/hebrew-full/hebrew-reader-50-lessons.json"
    if path.exists():
        master = json.loads(path.read_text(encoding="utf-8"))
        words = [w for lesson in master["lessons"] for w in lesson["vocabulary"]]
        for entry in words:
            for number in entry.get("strongs") or ([entry["strong"]] if entry.get("strong") else []):
                digits = re.sub(r"\D", "", str(number))
                if digits:
                    hebrew.setdefault(
                        f"H{int(digits):04d}",
                        {"zh": entry.get("glossZh", ""), "en": entry.get("glossEn", "")},
                    )
    return greek, hebrew, fhl


def split_by_book(language: str, verses: dict[str, list[dict]]) -> None:
    """One file per book, so a chapter view loads a megabyte and not sixty."""

    greek_gloss, hebrew_gloss, fhl = glossary()
    strong_path = ROOT / "output/source-cache/scripture/greek-lemma-strong.json"
    greek_strongs = (
        json.loads(strong_path.read_text(encoding="utf-8"))["lemmas"]
        if strong_path.exists() else {}
    )
    books: dict[str, dict[str, list[dict]]] = {}
    glossed = 0
    for ref, words in verses.items():
        book = ref.rsplit(".", 2)[0]
        for word in words:
            found = (
                greek_gloss.get(word["lemma"])
                if language == "greek"
                else hebrew_gloss.get(word.get("strong", ""))
            )
            if found and found.get("en"):
                word["en"] = found["en"]
            if found and found.get("zh"):
                word["zh"] = found["zh"]
                word["zhSource"] = "reader"
                glossed += 1
                continue
            # 覆核過的詞義沒有這一個字，才查信望愛字典。
            strong = word.get("strong") or ""
            if not strong and language == "greek":
                # MorphGNT 標詞位不標 Strong，字典因此接不上；這張對照表就是
                # 為了接上它建的（scripts/fetch_fhl_greek_strongs.py）。
                number = greek_strongs.get(fold(word["lemma"]))
                strong = f"G{number}" if number else ""
                if strong:
                    word["strong"] = strong
            key = strong if strong else ""
            if key.startswith("H"):
                key = f"H{int(key[1:]):05d}" if key[1:].isdigit() else key
            entry = fhl.get(key)
            if entry and entry.get("zh"):
                word["zh"] = entry["zh"]
                word["zhSource"] = "fhl"
                glossed += 1
        books.setdefault(book, {})[ref] = words

    folder = OUT / "books"
    folder.mkdir(parents=True, exist_ok=True)
    for book, chapters in books.items():
        (folder / f"{book}.json").write_text(
            json.dumps({"book": book, "language": language, "byVerse": chapters}, ensure_ascii=False),
            encoding="utf-8",
        )
    total = sum(len(w) for w in verses.values())
    print(f"  分卷 {len(books)} 檔；有中文詞義的詞 {glossed}／{total}"
          f"（{glossed * 100 // max(total, 1)}%）")


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
            split_by_book(language, verses)
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
