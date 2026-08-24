#!/usr/bin/env python3
"""Give the appendix of names their Chinese, from the site's own registers.

Four hundred names is too many to render by hand and far too many to invent.
The site already rules on Chinese names in two places, and both outrank anything
decided here: the 翻譯定名 glossary for church and classical figures, and
``biblical_people`` for everyone in scripture.  This script's whole job is to
route each Greek name to whichever register covers it, and to say plainly which
names no register covers rather than filling the gap with a guess.

Three routes, in order of how much they can be trusted:

    詞庫    the glossary keys on the Greek itself, so a hit is exact.
    英文名  Strong's names the New Testament's Greek in English, and
            ``biblical_people`` names the same people in Chinese; the English is
            the hinge.  Ambiguity is resolved by refusing it - two Chinese names
            for one English name means the match is dropped, not guessed.
    音譯    for the Septuagint's names, which Strong's never saw, the Greek is
            transliterated and matched against the same table.  This is the
            weakest route, so its results are marked for review.

Whatever survives all three unmatched is left empty and listed.  A later pass -
by a person, or by the gloss pipeline with a person checking it - can fill those,
and every entry records which route named it so that judgement stays possible.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from verify_greek_vocab_lexicon import fold


ROOT = Path(__file__).resolve().parents[1]
APPENDICES = ROOT / "data" / "originalReaders" / "vocabulary" / "greek-appendices.json"
STRONGS = (ROOT / "output" / "source-cache" / "original-readers" / "strongs-src" /
           "strongs-master" / "greek" / "strongs-greek-dictionary.js")

# Greek to Latin letters, the way Strong's and the standard English Bibles
# transliterate Septuagint names.  Digraphs first, since order decides.
TRANSLITERATION = [
    ("ου", "u"), ("αι", "ai"), ("ει", "ei"), ("οι", "oi"), ("υι", "ui"),
    ("αυ", "au"), ("ευ", "eu"), ("ηυ", "eu"),
    ("γγ", "ng"), ("γκ", "nk"), ("γχ", "nch"),
    ("θ", "th"), ("φ", "ph"), ("χ", "ch"), ("ψ", "ps"), ("ξ", "x"),
    ("α", "a"), ("β", "b"), ("γ", "g"), ("δ", "d"), ("ε", "e"), ("ζ", "z"),
    ("η", "e"), ("ι", "i"), ("κ", "k"), ("λ", "l"), ("μ", "m"), ("ν", "n"),
    ("ο", "o"), ("π", "p"), ("ρ", "r"), ("σ", "s"), ("τ", "t"), ("υ", "y"),
    ("ω", "o"),
]

# Endings Greek adds to Semitic names, which the English forms drop.
GREEK_ENDINGS = ("os", "es", "as", "on", "us", "is", "ou", "e", "s")


def latinise(greek: str) -> set[str]:
    """English spellings a Bible might use for this Greek name.

    The Septuagint's names never reached Strong's, which indexes the New
    Testament only, so Ἰωάβ and Ναβουχοδονοσόρ have to be recognised through
    their English forms instead.  Greek and English took the same Hebrew names
    by different roads, and the divergences are regular:

        Ἰω- Ἰα- Ἰε-   became Jo- Ja- Je-      (Ἰωάβ, Joab)
        χ             became h                 (Ἀχαάβ, Ahab)
        -ίας          became -iah              (Ἀζαρίας, Azariah)

    So each name is spelled out every way those rules allow, and the caller
    matches on all of them; a name is only accepted when exactly one person in
    the register answers to any of them.
    """
    base = fold(greek)
    for source, target in TRANSLITERATION:
        base = base.replace(source, target)
    base = re.sub(r"[^a-z]", "", base)
    if not base:
        return set()

    spellings = {base}
    if base[:1] == "i" and base[1:2] in "aeou":
        spellings.add("j" + base[1:])
    for spelling in list(spellings):
        if "ch" in spelling:
            spellings.add(spelling.replace("ch", "h"))
        if spelling.endswith("ias"):
            spellings.add(spelling[:-3] + "iah")
        if spelling.endswith("as"):
            spellings.add(spelling[:-2] + "ah")
        if spelling.endswith(("os", "es", "us", "on", "ou")):
            spellings.add(spelling[:-2])
        if spelling.endswith("s"):
            spellings.add(spelling[:-1])
    return spellings


def english_keys(name: str) -> set[str]:
    """Spellings an English Bible might use for one name, loosely compared.

    English Bibles are not consistent about doubled letters, terminal h, or the
    vowels in Semitic names, so comparison happens on a squeezed skeleton:
    Nebuchadnezzar and Nabuchodonosor collapse to the same key, and so do
    Sarah and Sara.
    """
    base = re.sub(r"[^a-z]", "", name.lower())
    if not base:
        return set()
    keys = {base}
    squeezed = re.sub(r"(.)\1+", r"\1", base)
    keys.add(squeezed)
    for key in list(keys):
        if key.endswith("h"):
            keys.add(key[:-1])
    return {key for key in keys if len(key) >= 3}


FHL_CACHE = (ROOT / "output" / "source-cache" / "original-readers" / "greek-full" /
             "fhl-strongs-zh.json")
FHL_URL = "https://bible.fhl.net/json/sd.php"

# The part-of-speech line names the kind outright.
FHL_KINDS = (("地名", "place"), ("人名", "person"), ("專有名詞", "person"))


def fhl_chinese(numbers: dict[str, str]) -> dict[str, dict]:
    """信望愛's Chinese Strong's dictionary, one entry per number.

    This is the register that covers what ``biblical_people`` cannot: Αἴγυπτος,
    Βαβυλών, Ἰσραήλ are places and peoples, not people, and no genealogy table
    holds them.  信望愛 gives all of them a Traditional-Chinese headword and,
    on its part-of-speech line, says whether the name is a person's or a place's.

    Entries are cached on disk, because this is several hundred requests against
    someone else's server and the answers do not change.
    """
    import time

    import requests
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    cache = json.loads(FHL_CACHE.read_text(encoding="utf-8")) if FHL_CACHE.exists() else {}
    wanted = sorted({number for number in numbers.values() if number not in cache})
    for index, number in enumerate(wanted, 1):
        try:
            response = requests.get(
                FHL_URL, params={"N": "0", "k": number.lstrip("G"), "gb": "0"},
                timeout=30, verify=False,
            )
            record = (response.json().get("record") or [{}])[0]
            cache[number] = record.get("dic_text", "")
        except Exception as error:                      # noqa: BLE001 - report, continue
            print(f"    G{number} 取用失敗：{type(error).__name__}")
            cache[number] = ""
        if index % 25 == 0:
            print(f"    已取 {index}/{len(wanted)}")
        time.sleep(0.35)                                # be a good guest
    if wanted:
        FHL_CACHE.parent.mkdir(parents=True, exist_ok=True)
        FHL_CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")

    parsed: dict[str, dict] = {}
    for number, text in cache.items():
        if not text:
            continue
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        kind = ""
        for label, value in FHL_KINDS:
            if any(label in line for line in lines[1:3]):
                kind = value
                break
        # Two shapes.  Most name entries print the headword on its own line after
        # the 欽定本 tally - 「埃及 = "雙峽之地"」.  The rest have no such line and
        # open the numbered definition with the name instead - 「1) 巴比倫．為…」.
        chinese = ""
        after = False
        for line in lines:
            if line.startswith("欽定本"):
                after = True
                continue
            if not after:
                continue
            numbered = re.match(r"^\d+\)\s*(.+)$", line)
            if numbered:
                candidate = re.match(r"^([一-鿿‧·]{2,8})", numbered.group(1))
                # A definition that opens with 「一個」「指」「位於」 is describing the
                # thing, not naming it; those are left for another route.
                if candidate and not re.match(r"^(一個|一位|指|位於|在|為|即)",
                                              candidate.group(1)):
                    chinese = candidate.group(1).rstrip("的地人").strip() or candidate.group(1)
                    if len(chinese) < 2:
                        chinese = candidate.group(1)
                break
            match = re.match(r"^([一-鿿‧·]{1,12})(?:\s*=|\s*\"|$)", line)
            if match:
                chinese = match.group(1)
                break
        if chinese:
            parsed[number] = {"zh": chinese, "kind": kind}
    return parsed


# Strong's indexes the Textus Receptus, which spells several names differently
# from the editions this reader prints.  Where the difference is a single letter
# the bridge below finds it; where it is more than that, it is listed here.
TR_SPELLINGS = {
    "μωυσησ": "μωσευσ",        # Μωϋσῆς / Μωσεύς
    "μωυσης": "μωσευσ",
    "ιωαννησ": "ιωαννησ",
    "ιεροσολυμα": "ιεροσολυμα",
}


def bridge(key: str, index: dict[str, str]) -> str | None:
    """The Strong's number for a name this reader spells its own way.

    Δαυίδ against Strong's Δαβίδ, Σαλωμών against Σολομών: one letter apart, and
    unambiguous once the comparison allows for it.  A near match is only accepted
    when exactly one candidate is that close, so the bridge never picks between
    two names.
    """
    if key in index:
        return index[key]
    aliased = TR_SPELLINGS.get(key)
    if aliased and aliased in index:
        return index[aliased]
    close = [
        candidate for candidate in index
        if len(candidate) == len(key)
        and sum(a != b for a, b in zip(candidate, key)) == 1
    ]
    return index[close[0]] if len(close) == 1 else None


def strongs_numbers() -> dict[str, str]:
    """Greek headword to its Strong's number."""
    raw = STRONGS.read_text(encoding="utf-8")
    data = json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
    numbers: dict[str, str] = {}
    for number, row in data.items():
        headword = row.get("lemma") or row.get("unicode") or ""
        if headword:
            numbers.setdefault(fold(headword), number)
    return numbers


def load_strongs() -> dict[str, str]:
    """Greek headword to the English name Strong's gives it."""
    raw = STRONGS.read_text(encoding="utf-8")
    data = json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
    names: dict[str, str] = {}
    for row in data.values():
        headword = row.get("lemma") or row.get("unicode") or ""
        english = row.get("kjv_def") or row.get("strongs_def") or ""
        if not headword or not english:
            continue
        # "Juda(-h, -s); Jude" and "also an Israelite:--Jacob" both hide the name
        # among editorial furniture; take the first bare capitalised word.
        english = english.split(":--")[-1]
        match = re.search(r"\b([A-Z][a-zA-Z]{2,})\b", english)
        if match:
            names.setdefault(fold(headword), match.group(1))
    return names


def load_registers() -> tuple[dict, dict]:
    """The two Chinese registers: biblical people, and the naming glossary."""
    import requests
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    url, key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not (url and key):
        raise SystemExit("需要 SUPABASE_URL 與 SUPABASE_SERVICE_ROLE_KEY 才能讀詞庫")
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}

    people: dict[str, set] = defaultdict(set)
    offset = 0
    while True:
        response = requests.get(
            f"{url}/rest/v1/biblical_people",
            params={"select": "name_zh,name_en", "limit": "500", "offset": str(offset)},
            headers=headers, timeout=60,
        )
        response.raise_for_status()
        rows = response.json()
        for row in rows:
            english, chinese = (row.get("name_en") or ""), (row.get("name_zh") or "")
            if english and chinese:
                # Disambiguators such as 「比拉（比珥之子）」 are for the genealogy,
                # not for a vocabulary list; the bare name is what gets printed.
                bare = re.sub(r"（.*?）", "", chinese).strip()
                for candidate in english_keys(english):
                    people[candidate].add(bare)
        if len(rows) < 500:
            break
        offset += 500

    glossary: dict[str, dict] = {}
    for table, kind in (("theologians", "person"), ("place_names", "place"),
                        ("deities", "deity"), ("official_titles", "office")):
        response = requests.get(
            f"{url}/rest/v1/{table}",
            params={"select": "name_original,name_recommended", "limit": "5000"},
            headers=headers, timeout=60,
        )
        response.raise_for_status()
        for row in response.json():
            original = (row.get("name_original") or "").strip()
            chinese = (row.get("name_recommended") or "").strip()
            if original and chinese:
                glossary.setdefault(fold(original), {"zh": chinese, "kind": kind,
                                                     "table": table})
    return people, glossary


def resolve(people: dict[str, set], keys: set[str]) -> tuple[str, bool]:
    """One Chinese name for these English spellings, or nothing.

    Several distinct people can share an English name, and the table then holds
    several Chinese names for it.  There is no way to tell from a word list which
    is meant, so the match is dropped: an empty cell is honest, a coin toss is not.
    """
    found: set[str] = set()
    for key in keys:
        found |= people.get(key, set())
    if len(found) == 1:
        return found.pop(), False
    return "", bool(found)


def main() -> None:
    parser = argparse.ArgumentParser(description="替附錄專名補上中文")
    parser.add_argument("--write", action="store_true", help="寫回 greek-appendices.json")
    args = parser.parse_args()

    payload = json.loads(APPENDICES.read_text(encoding="utf-8"))
    names = payload["appendices"][0]["entries"]
    strongs = load_strongs()
    numbers = strongs_numbers()
    people, glossary = load_registers()
    for entry in names:
        found = (bridge(fold(entry["lemma"]), numbers)
                 or bridge(fold(entry["headword"]), numbers))
        if found:
            entry["strong"] = found
    wanted = {entry["headword"]: entry["strong"]
              for entry in names if entry.get("strong")}
    print(f"  專名中 Strong 有號者 {len(wanted)}，向信望愛取中文…")
    fhl = fhl_chinese(wanted)
    print(f"  信望愛回覆可用中文 {len(fhl)} 筆")
    print(f"  Strong 的希臘詞頭 {len(strongs)} 筆、"
          f"聖經人物英文鍵 {len(people)} 筆、詞庫希臘原文 {len(glossary)} 筆")

    tally = defaultdict(int)
    for entry in names:
        headword, lemma = entry["headword"], entry["lemma"]

        known = glossary.get(fold(lemma)) or glossary.get(fold(headword))
        if known:
            entry.update(zh=known["zh"], zhSource=known["table"],
                         zhRoute="詞庫", kind=known["kind"] or entry.get("kind", ""))
            tally["詞庫"] += 1
            continue

        number = entry.get("strong")
        record = fhl.get(number) if number else None
        if record:
            entry.update(zh=record["zh"], zhSource="信望愛 Strong 中文字典",
                         zhRoute="信望愛", strong=number,
                         kind=record["kind"] or entry.get("kind", ""))
            tally["信望愛"] += 1
            continue

        english = strongs.get(fold(lemma)) or strongs.get(fold(headword))
        if english:
            chinese, ambiguous = resolve(people, english_keys(english))
            if chinese:
                entry.update(zh=chinese, zhSource="biblical_people",
                             zhRoute="英文名", zhEnglish=english)
                tally["英文名"] += 1
                continue
            entry["zhEnglish"] = english
            if ambiguous:
                entry["zhNote"] = f"同名者不只一人（{english}），未擇一"
                tally["同名未決"] += 1
                continue

        spellings = set()
        for spelling in latinise(headword) | latinise(lemma):
            spellings |= english_keys(spelling)
        chinese, ambiguous = resolve(people, spellings)
        if chinese:
            entry.update(zh=chinese, zhSource="biblical_people", zhRoute="音譯",
                         zhReview="音譯比對所得，須複核")
            tally["音譯"] += 1
            continue
        if ambiguous:
            entry["zhNote"] = "音譯比對到多個同名者，未擇一"
            tally["同名未決"] += 1
            continue
        tally["未定"] += 1

    named = sum(1 for entry in names if entry.get("zh"))
    print(f"  {len(names)} 個專名中已定名 {named}，未定 {len(names) - named}")
    for route, count in sorted(tally.items(), key=lambda pair: -pair[1]):
        print(f"    {route:<10s} {count}")

    unresolved = [e["headword"] for e in names if not e.get("zh")]
    print(f"  未定名者前 30：{'、'.join(unresolved[:30])}")

    payload["appendices"][0]["namingPolicy"] = (
        "中文一律取自既有名冊，不自行擬名。優先序：站上「翻譯定名」詞庫（教父與古典名，"
        "以希臘原文為鍵）→ 信望愛中文 Strong 字典（新約所見人名地名國族，並據其詞性行"
        "判定人名或地名）→ 由 Strong 英文名接 biblical_people → 希臘拼寫轉寫後比對。"
        "zhRoute 記錄該筆循哪條路徑定名；「音譯」者須複核。"
        "同一英文名對到多個中文名時不擇一，寧留空。"
    )
    if args.write:
        APPENDICES.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                              encoding="utf-8")
        print(f"已寫回 {APPENDICES}")
    else:
        print("（未寫檔；加 --write 才會寫回）")


if __name__ == "__main__":
    main()
