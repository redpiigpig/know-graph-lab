#!/usr/bin/env python3
"""從 Strong 詞典的釋義句判定一個聖經專名是地名、族名、人名還是神名。

為什麼要這一步：分類本來只靠幾份登錄（`place_names`、`biblical_people`…），可是那
幾份是**通論性**的——`place_names` 268 筆收的是馬爾堡、蘇美、安息帝國，聖經地理幾
乎不在裡面。結果撒瑪黎雅、赫貝龍、加里肋亞、貝特耳這些一望即知的地名全都落到
「待歸類」。希臘上冊 139 條、拉丁上冊 386 條就是這樣卡住的。

Strong 詞典本身給了憑據。它的釋義句有固定寫法：

    H1008 בֵּית־אֵל   "Beth-El, a place in Palestine"
    G1056 Γαλιλαία   "Galilæa (i.e. the heathen circle), a region of Palestine"
    H669  אֶפְרַיִם    "Ephrajim, a son of Joseph; also the tribe descended from him"

「a place in Palestine」「a region of」「a son of」「the name of N Israelites」是編
者的體例，不是散文。照這些片語判類是讀證據，不是猜。同一條裡出現兩種身分時（赫貝
龍既是地名也是兩個以色列人的名字）取**先出現**的那一個，因為 Strong 把主要義項寫
在前面。

對照的鍵走 KJV 英文名與拉丁轉寫，並且**只在折疊後的鍵在整部詞典裡只指向一種身分時
才採用**。一鍵多身分就放掉——寧可留在「待歸類」，也不要在紙本附錄上把人名印成地名。
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "output/source-cache/original-readers/strongs-src/strongs-master"
OUTPUT = ROOT / "output/source-cache/original-readers/strongs-name-kinds.json"

PLACE = "地名"
NATION = "民族與國名"
DEITY = "神名與稱號"
KING = "君王"
PERSON = "其他人名"

# 依序試；先中的算數。片語取自 Strong 的體例，不是自己造的說法。
PATTERNS: list[tuple[str, str]] = [
    (PLACE, r"\ba (?:place|city|town|village|region|district|province|country|"
            r"mountain|hill|river|stream|brook|valley|plain|island|lake|sea|"
            r"port|harbou?r|well|spring|pool|gate|tower|desert|wilderness)\b"),
    (PLACE, r"\bthe (?:capital|chief city|region|district|territory)\b"),
    (NATION, r"\b(?:a|the) (?:tribe|nation|people|clan|family|race|sect|dynasty)\b"),
    (NATION, r"\b(?:descendants? of|inhabitants? of|an inhabitant of)\b"),
    (NATION, r"\b(?:Israelites|Canaanites|Philistines|Egyptians|Edomites|Moabites)\b"),
    (DEITY, r"\b(?:an? (?:idol|god|goddess|deity)|the supreme God|a heathen deity)\b"),
    (KING, r"\ba (?:king|queen|emperor|pharaoh) of\b"),
    (PERSON, r"\b(?:an? (?:son|daughter|Israelite|Israelitess|Jew|Jewess|Christian|"
             r"patriarch|prophet|priest|eunuch|servant|man|woman)\b|"
             r"the name of|father of|mother of|wife of)"),
]


def load_dictionary(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    start = text.index("{")
    return json.loads(text[start : text.rindex("}") + 1])


def kind_of(definition: str) -> tuple[str, str]:
    """回傳 (身分, 命中的片語)。判不出來回 ("", "")。"""
    text = definition or ""
    best: tuple[int, str, str] = (len(text) + 1, "", "")
    for kind, pattern in PATTERNS:
        match = re.search(pattern, text, re.I)
        if match and match.start() < best[0]:
            best = (match.start(), kind, match.group(0))
    return best[1], best[2]


# Strong 的羅馬轉寫用 ôw／ûw／îy 標母音字母（mater lectionis）：Chebrôwn 讀作
# Chebron，Chebrîy 讀作 Chebri。不還原這個體例，希臘與拉丁的 Chebron 就永遠對不上
# 詞典裡的 Chebrôwn，多出來的那個 w 把整批 LXX 地名擋在門外。
MATRES = (("ôw", "ô"), ("ûw", "û"), ("îy", "î"), ("ōw", "ō"), ("ēy", "ē"))


def fold(text: str) -> str:
    """折疊成比對鍵：只留字母，I/J、U/V 同字，ae/oe 折成 e，y 折成 i。"""
    text = (text or "").lower()
    for digraph, replacement in MATRES:
        text = text.replace(digraph, replacement)
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z]", "", text)
    text = text.replace("ae", "e").replace("oe", "e")
    return text.replace("j", "i").replace("v", "u").replace("y", "i")


# 專名的字尾在各語言之間本來就會換：Galilee／Galilæa／Γαλιλαία、Hebron／Chebron。
# 把這些字尾削掉再比，才不會每個名字都因為語尾差一兩個字母而落空。
TAIL = re.compile(r"(?:us|um|os|on|as|es|is|im|ae|a|e|i|o|s|h)$")


def stem(text: str) -> str:
    folded = fold(text)
    if len(folded) <= 4:
        return folded
    trimmed = TAIL.sub("", folded)
    return trimmed if len(trimmed) >= 3 else folded


def build() -> dict:
    """兩層索引：完整字形一層，字幹一層，各自檢查唯一性。

    兩層要分開查唯一性，不能混在一起。地名與由它派生的族名在 Strong 裡是相鄰的兩
    條（H123 ʼĔdôm 厄東地 ／ H130 ʼĔdômîy 厄東人），完整字形本來分得開（edom ／
    edomi），一旦把族名的字幹 edom 也丟進同一層，地名那個鍵就變成「兩種身分」而
    整個被丟掉——本來對得上的反而查不到了。
    """
    exact: dict[str, set[str]] = {}
    loose: dict[str, set[str]] = {}
    evidence: dict[str, str] = {}
    counted = 0
    for name in ("hebrew/strongs-hebrew-dictionary.js", "greek/strongs-greek-dictionary.js"):
        for number, row in load_dictionary(SRC / name).items():
            kind, phrase = kind_of(row.get("strongs_def", ""))
            if not kind:
                continue
            counted += 1
            # KJV 的英文名、詞典自己的羅馬轉寫，都是可以跟拉丁／希臘轉寫對上的形。
            # kjv_def 常寫成「Beth-el, Bethel.」這種列舉，逐項拆開。
            forms = re.split(r"[,;]", row.get("kjv_def", "") or "")
            forms.append(row.get("xlit", "") or "")
            forms.append(row.get("translit", "") or "")
            for form in forms:
                for bucket, key in ((exact, fold(form)), (loose, stem(form))):
                    if len(key) < 3:
                        continue
                    bucket.setdefault(key, set()).add(kind)
                    evidence.setdefault(f"{key}|{kind}", f"{number} {phrase}")

    def resolve(bucket: dict[str, set[str]]) -> dict[str, str]:
        # 一鍵指向兩種身分就是沒有結論，放掉。
        return {key: next(iter(kinds)) for key, kinds in bucket.items() if len(kinds) == 1}

    kinds, stems = resolve(exact), resolve(loose)
    used = {**stems, **kinds}
    return {
        "schemaVersion": "2.0.0",
        "note": __doc__.strip().splitlines()[0],
        "definitionsRead": counted,
        "keysAmbiguous": (len(exact) - len(kinds)) + (len(loose) - len(stems)),
        "kinds": kinds,
        "stems": stems,
        "evidence": {key: evidence[f"{key}|{kind}"] for key, kind in used.items()},
    }


_CACHE: dict | None = None


# 拉丁附錄收的是文本裡的實際形，不是主格：Jordanem、Pharaonem、Levitarum、
# Jerosolymis、Philisthinorum。查詢時把格尾削掉再試一次。長的先試。
CASE_ENDINGS = ("orum", "arum", "ibus", "erum", "em", "am", "um", "os", "as",
                "es", "is", "ae", "us", "i", "o", "e", "a", "s")


def case_stems(text: str) -> list[str]:
    folded = fold(text)
    out = []
    for ending in CASE_ENDINGS:
        if folded.endswith(ending) and len(folded) - len(ending) >= 4:
            out.append(folded[: -len(ending)])
    return out


GREEK_RE = re.compile(r"[Ͱ-Ͽἀ-῿]")


def lookup(*forms: str) -> tuple[str, str]:
    """查一個專名的身分。給幾種寫法都可以，先中的算數。"""
    global _CACHE
    if _CACHE is None:
        _CACHE = json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else build()
    kinds, stems, evidence = _CACHE["kinds"], _CACHE["stems"], _CACHE["evidence"]
    expanded: list[str] = []
    for form in forms:
        if not form:
            continue
        expanded.append(form)
        if GREEK_RE.search(form):
            # 索引的鍵是拉丁字母，希臘原形直接折疊會全部落空；先轉寫再查。
            from greek_latin_name_bridge import to_latin
            expanded.append(to_latin(form))
    # 先全部試完整字形，再回頭試字幹。順序反過來的話，Χεβρὼν 的字幹會先撞上
    # 「赫貝龍人」那條族名，把地名判成族名——完整字形本來對得上地名。
    for form in expanded:
        key = fold(form)
        if len(key) >= 3 and key in kinds:
            return kinds[key], f"Strong 釋義：{evidence.get(key, '')}"
    for form in expanded:
        for key in [stem(form), *case_stems(form)]:
            # 字幹比對放寬了語尾，就得把長度守嚴一點：四五個字母的字幹在聖經專名裡
            # 常常同時是好幾個名字的開頭。
            if len(key) >= 6 and key in stems:
                return stems[key], f"Strong 釋義（字幹）：{evidence.get(key, '')}"
    return "", ""


def main() -> None:
    payload = build()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"讀了 {payload['definitionsRead']} 條有身分的釋義")
    print(f"完整字形鍵 {len(payload['kinds'])}、字幹鍵 {len(payload['stems'])}，"
          f"因一鍵多身分而放棄 {payload['keysAmbiguous']}")
    for probe in ("Samaria", "Hebron", "Galilaea", "Bethel", "Jordanem",
                  "Pharaonem", "Levitarum", "Χεβρὼν", "Γαβαὼν", "Ἐδώμ"):
        print(f"   {probe:<12}{lookup(probe)}")


if __name__ == "__main__":
    main()
