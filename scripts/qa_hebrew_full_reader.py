"""Final, independent QA gate for the complete Hebrew original reader.

The gate is deliberately independent from both content assemblers and the
DOCX builder.  It can run in two phases:

* ``--phase preflight`` validates all available source/master data and records
  missing master/DOCX/PDF artifacts as PENDING.
* ``--phase final`` requires the master JSON, DOCX, and PDF and treats every
  missing artifact as a failing release gate.

The machine-readable report is written under ``output/qa``.  This script never
repairs content or document artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import unicodedata
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable
from xml.etree import ElementTree as ET

from rcuv2010_reader import (
    load_rcuv_snapshot,
    translation_entry_for_mt,
    translation_for_mt,
)


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "hebrew-full"
DEFAULT_MASTER = CACHE / "hebrew-reader-50-lessons.json"
DEFAULT_DOCX = ROOT / "output" / "original-readers" / "hebrew-original-reader-50-lessons.docx"
DEFAULT_PDF = ROOT / "output" / "original-readers" / "hebrew-original-reader-50-lessons.pdf"
DEFAULT_REPORT = ROOT / "output" / "qa" / "original-readers" / "hebrew-full" / "qa-report.json"
VOCAB_PATH = ROOT / "data" / "originalReaders" / "vocabulary" / "hebrew-1000.json"
NAMES_PATH = ROOT / "data" / "originalReaders" / "vocabulary" / "hebrew-proper-names.json"
GLOSS_PATH = CACHE / "hebrew-gloss-zh-reviewed-by-lemma.json"
SCRIPTURE_PATH = CACHE / "scripture-plan.json"
PRAYERS_PATH = CACHE / "prayers-articles.json"
HAGGADAH_PATH = CACHE / "haggadah-full.json"
RCUV_PATH = CACHE / "RCUV2010.json"
WLC_PSALMS_PATH = (
    ROOT / "output" / "source-cache" / "original-readers" /
    "morphhb-src" / "morphhb-master" / "wlc" / "Ps.xml"
)

BOOK_TO_CHINESE_SOURCE_NAME = {
    "Gen": "Genesis", "gen": "Genesis", "Exod": "Exodus", "exod": "Exodus",
    "Lev": "Leviticus", "lev": "Leviticus", "Num": "Numbers", "num": "Numbers",
    "Deut": "Deuteronomy", "deut": "Deuteronomy", "Josh": "Joshua", "josh": "Joshua",
    "Judg": "Judges", "judg": "Judges", "Ruth": "Ruth", "ruth": "Ruth",
    "1Sam": "I Samuel", "1sam": "I Samuel", "2Sam": "II Samuel", "2sam": "II Samuel",
    "1Kgs": "I Kings", "1kgs": "I Kings", "2Kgs": "II Kings", "2kgs": "II Kings",
    "1Chr": "I Chronicles", "1chr": "I Chronicles", "2Chr": "II Chronicles", "2chr": "II Chronicles",
    "Ezra": "Ezra", "ezra": "Ezra", "Neh": "Nehemiah", "neh": "Nehemiah",
    "Esth": "Esther", "esth": "Esther", "Job": "Job", "job": "Job",
    "Ps": "Psalms", "ps": "Psalms", "Prov": "Proverbs", "prov": "Proverbs",
    "Eccl": "Ecclesiastes", "eccl": "Ecclesiastes", "Song": "Song of Solomon", "song": "Song of Solomon",
    "Isa": "Isaiah", "isa": "Isaiah", "Jer": "Jeremiah", "jer": "Jeremiah",
    "Lam": "Lamentations", "lam": "Lamentations", "Ezek": "Ezekiel", "ezek": "Ezekiel",
    "Dan": "Daniel", "dan": "Daniel", "Hos": "Hosea", "hos": "Hosea",
    "Joel": "Joel", "joel": "Joel", "Amos": "Amos", "amos": "Amos",
    "Obad": "Obadiah", "obad": "Obadiah", "Jonah": "Jonah", "jonah": "Jonah",
    "Mic": "Micah", "mic": "Micah", "Nah": "Nahum", "nah": "Nahum",
    "Hab": "Habakkuk", "hab": "Habakkuk", "Zeph": "Zephaniah", "zeph": "Zephaniah",
    "Hag": "Haggai", "hag": "Haggai", "Zech": "Zechariah", "zech": "Zechariah",
    "Mal": "Malachi", "mal": "Malachi",
}

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{W_NS}}}"
HEBREW_LETTER = re.compile(r"[\u05D0-\u05EA]")
HEBREW_MARK = re.compile(r"[\u0591-\u05C7]")
HEBREW_VOWEL = re.compile(r"[\u05B0-\u05BB\u05C7]")
HEBREW_ACCENT = re.compile(r"[\u0591-\u05AF]")
CJK = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF]")
ASCII_WORD = re.compile(r"[A-Za-z]")
# U+25A1 is intentionally used as the printable empty checkbox in the lesson
# completion lists.  It is only suspicious outside the ``□ 1.``-style pattern;
# U+FFFD and U+25AF are always treated as substitution/missing-glyph markers.
REPLACEMENT_GLYPHS = {"\uFFFD", "\u25AF"}
GENERIC_PLACEHOLDERS = re.compile(
    r"待翻|待依|某詞|TODO|placeholder|未定|未知|"
    r"^(?:地名|行動|物件|狀態|專名|人名|顏色|度量單位|詞義)$",
    re.IGNORECASE,
)

# Unambiguous simplified-only forms that should not occur in zh-Hant fields.
# 「后」 is deliberately absent: it is a genuine traditional character (王后、
# 皇后) that only doubles as the simplified form of 後, so banning it outright
# rejects correct Traditional Chinese.
SIMPLIFIED_ONLY = set(
    "宾标语复数处为这发进与东业国门义术词觉头万产总个开变听边导观达远冲决仅严营击获习钟龙丰划赶现应让"
)

EXPECTED_COUNTS = {
    "lessons": 50,
    "vocabulary": 1000,
    "memoryVerses": 100,
    "bibleChapters": 25,
    "prayersOrArticles": 25,
    "haggadahSteps": 15,
    "haggadahSegments": 199,
    "properNames": 135,
}

# A release-stable gold list for all proper-name headwords, keyed by
# ``strong|pointed`` rather than by position: the names moved out of the lesson
# list into their own appendix, which renumbered every ordinal.  Values are
# required fragments rather than full glosses so useful explanatory text may be
# refined without silently changing the conventional biblical name.
PROPER_NAME_GOLD: dict[str, tuple[str, ...]] = {
    "H120|אָדָם": ("亞當",),
    "H430|אֱלֹהִים": ("神",),
    "H410|אֵל": ("神",),
    "H3478|יִשְׂרָאֵל": ("以色列",),
    "H3389|יְרוּשָׁלַ֫םִ": ("耶路撒冷",),
    "H3389|יְרוּשָׁלַ֫יִם": ("耶路撒冷",),
    "H3068|יְהוָה": ("耶和華",),
    "H4714|מִצְרַ֫יִם": ("埃及",),
    "H4872|מֹשֶׁה": ("摩西",),
    "H6547|פַּרְעֹה": ("法老",),
    "H136|אֲדֹנָי": ("主",),
    "H7676|שַׁבָּת": ("安息日",),
    "H1167|בַּ֫עַל": ("巴力",),
    "H5045|נֶ֫גֶב": ("尼革夫",),
    "H4899|מָשִׁיחַ": ("彌賽亞",),
    "H1732|דָּוִד": ("大衛",),
    "H3063|יְהוּדָה": ("猶大",),
    "H7586|שָׁאוּל": ("掃羅",),
    "H3290|יַעֲקֹב": ("雅各",),
    "H175|אַהֲרוֹן": ("亞倫",),
    "H3069|יְהֹוִה": ("耶和華",),
    "H8010|שְׁלֹמֹה": ("所羅門",),
    "H6430|פְּלִשְׁתִּי": ("非利士人",),
    "H3881|לֵוִיִּי": ("利未人",),
    "H894|בָּבֶל": ("巴比倫",),
    "H3091|יְהוֹשׁוּעַ": ("約書亞",),
    "H3130|יוֹסֵף": ("約瑟",),
    "H3383|יַרְדֵּן": ("約旦河",),
    "H4124|מוֹאָב": ("摩押",),
    "H669|אֶפְרַיִם": ("以法蓮",),
    "H85|אַבְרָהָם": ("亞伯拉罕",),
    "H1144|בִּנְיָמִין": ("便雅憫",),
    "H6726|צִיּוֹן": ("錫安",),
    "H804|אַשּׁוּר": ("亞述",),
    "H3414|יִרְמְיָה": ("耶利米",),
    "H4519|מְנַשֶּׁה": ("瑪拿西",),
    "H3097|יוֹאָב": ("約押",),
    "H1008|בֵּית־אֵל": ("伯特利",),
    "H8050|שְׁמוּאֵל": ("撒母耳",),
    "H1568|גִּלְעָד": ("基列",),
    "H758|אֲרָם": ("亞蘭",),
    "H2396|חִזְקִיָּה": ("希西家",),
    "H53|אֲבִישָׁלוֹם": ("押沙龍",),
    "H8111|שֹׁמְרוֹן": ("撒馬利亞",),
    "H3327|יִצְחָק": ("以撒",),
    "H5983|עַמּוֹן": ("亞捫",),
    "H3379|יָרׇבְעָם": ("耶羅波安",),
    "H123|אֱדֹם": ("以東",),
    "H6215|עֵשָׂו": ("以掃",),
    "H3667|כְּנַעַן": ("迦南",),
    "H256|אַחְאָב": ("亞哈",),
    "H567|אֱמֹרִי": ("亞摩利人",),
    "H3092|יְהוֹשָׁפָט": ("約沙法",),
    "H1035|בֵּית לֶחֶם": ("伯利恆",),
    "H3778|כַּשְׂדִּי": ("迦勒底人",),
    "H3064|יְהוּדִי": ("猶太人",),
    "H1168|בַּעַל": ("巴力",),
    "H3083|יְהוֹנָתָן": ("約拿單",),
    "H4713|מִצְרִי": ("埃及人",),
    "H3669|כְּנַעַנִי": ("迦南人",),
    "H7205|רְאוּבֵן": ("呂便",),
    "H1410|גָּד": ("迦得",),
    "H499|אֶלְעָזָר": ("以利亞撒",),
    "H2275|חֶבְרוֹן": ("希伯崙",),
    "H452|אֵלִיָּה": ("以利亞",),
    "H3844|לְבָנוֹן": ("黎巴嫩",),
    "H1835|דָּן": ("但",),
    "H884|בְּאֵר שֶׁבַע": ("別是巴",),
    "H40|אֲבִימֶלֶךְ": ("亞比米勒",),
    "H7585|שְׁאוֹל": ("陰間",),
    "H2975|יְאֹר": ("尼羅河", "底格里斯河",),
    "H3878|לֵוִי": ("利未",),
    "H6667|צִדְקִיָּה": ("西底家",),
    "H7927|שְׁכֶם": ("示劍",),
    "H74|אַבְנֵר": ("押尼珥",),
    "H87|אַבְרָם": ("亞伯蘭",),
    "H1109|בִּלְעָם": ("巴蘭",),
    "H1316|בָּשָׁן": ("巴珊",),
    "H5019|נְבוּכַדְנֶאצַּר": ("尼布甲尼撒",),
    "H4782|מׇרְדְּכַי": ("末底改",),
    "H4080|מִדְיָן": ("米甸",),
    "H3058|יֵהוּא": ("耶戶",),
    "H609|אָסָא": ("亞撒",),
    "H477|אֱלִישָׁע": ("以利沙",),
    "H347|אִיּוֹב": ("約伯",),
    "H3405|יְרִיחוֹ": ("耶利哥",),
    "H3837|לָבָן": ("拉班",),
    "H635|אֶסְתֵּר": ("以斯帖",),
    "H2001|הָמָן": ("哈曼",),
    "H2977|יֹאשִׁיָּה": ("約西亞",),
    "H6659|צָדוֹק": ("撒督",),
    "H5321|נַפְתָּלִי": ("拿弗他利",),
    "H3077|יְהוֹיָדָע": ("耶何耶大",),
    "H7346|רְחַבְעָם": ("羅波安",),
    "H1130|בֶּן־הֲדַד": ("便哈達",),
    "H3050|יָהּ": ("耶",),
    "H3458|יִשְׁמָעֵאל": ("以實瑪利",),
    "H5838|עֲזַרְיָה": ("亞撒利雅",),
    "H2850|חִתִּי": ("赫人",),
    "H7706|שַׁדַּי": ("全能者",),
    "H3101|יוֹאָשׁ": ("約阿施",),
    "H7354|רָחֵל": ("拉結",),
    "H5146|נֹחַ": ("挪亞",),
    "H623|אָסָף": ("亞薩",),
    "H2074|זְבוּלוּן": ("西布倫",),
    "H1834|דַּמֶּשֶׂק": ("大馬士革",),
    "H8095|שִׁמְעוֹן": ("西緬",),
    "H3129|יוֹנָתָן": ("約拿單",),
    "H8096|שִׁמְעִי": ("示每",),
    "H836|אָשֵׁר": ("亞設",),
    "H1390|גִּבְעָה": ("基比亞",),
    "H1111|בָּלָק": ("巴勒",),
    "H3448|יִשַׁי": ("耶西",),
    "H5416|נָתָן": ("拿單",),
    "H1141|בְּנָיָה": ("比拿雅",),
    "H1053|בֵּית שֶׁמֶשׁ": ("伯示麥",),
    "H6865|צֹר": ("推羅",),
    "H2983|יְבוּסִי": ("耶布斯人",),
    "H271|אָחָז": ("亞哈斯",),
    "H8098|שְׁמַעְיָה": ("示瑪雅",),
    "H2148|זְכַרְיָה": ("撒迦利亞",),
    "H1537|גִּלְגָּל": ("吉甲",),
    "H558|אֲמַצְיָה": ("亞瑪謝",),
    "H5654|עֹבֵד אֱדוֹם": ("俄別以東",),
    "H842|אֲשֵׁרָה": ("亞舍拉",),
    "H5857|עַי": ("艾城",),
    "H6002|עֲמָלֵק": ("亞瑪力",),
    "H8165|שֵׂעִיר": ("西珥",),
    "H7157|קִרְיַת יְעָרִים": ("基列耶琳",),
    "H3470|יְשַׁעְיָה": ("以賽亞",),
    "H4847|מְרָרִי": ("米拉利",),
    "H223|אוּרִיָּה": ("烏利亞",),
    "H5467|סְדֹם": ("所多瑪",),
    "H1439|גִּדְעוֹן": ("基甸",),
    "H2809|חֶשְׁבּוֹן": ("希實本",),
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def has_replacement_glyph(text: str) -> bool:
    without_checkboxes = re.sub(r"□\s*\d+\.", "", text)
    return any(glyph in without_checkboxes for glyph in REPLACEMENT_GLYPHS) or "□" in without_checkboxes


def simplified_chars(text: str) -> list[str]:
    return sorted(set(text) & SIMPLIFIED_ONLY)


def hebrew_words(text: str) -> list[str]:
    return [
        token
        for token in re.split(r"[\s\u05BE.,;:!?()\[\]{}<>׳״'\"/]+", text)
        if HEBREW_LETTER.search(token)
    ]


def unpointed_words(text: str) -> list[str]:
    failures: list[str] = []
    for token in hebrew_words(text):
        decomposed = unicodedata.normalize("NFD", token)
        letters = "".join(character for character in decomposed if HEBREW_LETTER.fullmatch(character))
        if len(letters) <= 1 or letters in {"יהוה", "יי"}:
            continue
        has_vowel = bool(HEBREW_VOWEL.search(decomposed))
        clusters = []
        current = ""
        marks = ""
        for character in decomposed:
            if HEBREW_LETTER.fullmatch(character):
                if current:
                    clusters.append((current, marks))
                current, marks = character, ""
            elif current and 0x0591 <= ord(character) <= 0x05C7:
                marks += character
        if current:
            clusters.append((current, marks))
        has_shureq = any(base == "ו" and "\u05BC" in marks for base, marks in clusters)
        if not has_vowel and not has_shureq:
            failures.append(token)
    return failures


def is_zh_hant_field(text: str, *, forbid_ascii: bool = False) -> bool:
    if not isinstance(text, str) or not text.strip() or not CJK.search(text):
        return False
    if has_replacement_glyph(text) or GENERIC_PLACEHOLDERS.search(text):
        return False
    if simplified_chars(text):
        return False
    if forbid_ascii and ASCII_WORD.search(text):
        return False
    return True


@dataclass
class Gate:
    phase: str
    checks: list[dict[str, Any]] = field(default_factory=list)

    def add(self, status: str, code: str, message: str, **details: Any) -> None:
        self.checks.append(
            {
                "status": status,
                "code": code,
                "message": message,
                **({"details": details} if details else {}),
            }
        )

    def expect(self, condition: bool, code: str, message: str, **details: Any) -> None:
        self.add("PASS" if condition else "FAIL", code, message, **details)

    def artifact_missing(self, code: str, path: Path) -> None:
        status = "PENDING" if self.phase == "preflight" else "FAIL"
        self.add(status, code, f"artifact is not available: {path}", path=str(path))

    def guard(self, code: str, function: Callable[[], None]) -> None:
        try:
            function()
        except Exception as error:  # independent QA must report, not hide, parser errors
            self.add("FAIL", code, f"QA check raised {type(error).__name__}: {error}")

    def summary(self) -> dict[str, int]:
        return {
            status: sum(check["status"] == status for check in self.checks)
            for status in ("PASS", "FAIL", "PENDING", "WARN")
        }


def validate_vocabulary_sources(gate: Gate) -> tuple[list[dict], dict[int, dict]]:
    vocab = load_json(VOCAB_PATH)
    gloss_payload = load_json(GLOSS_PATH)
    glosses = gloss_payload.get("items", [])
    gate.expect(
        len(vocab) == 1000 and [item.get("ordinal") for item in vocab] == list(range(1, 1001)),
        "source.vocabulary.ordinals",
        "source vocabulary contains exact ordinals 1..1000",
        actual=len(vocab),
    )
    gloss_by_lemma = {f"{item['strong']}|{item['pointed']}": item.get("glossZh", "") for item in glosses}
    gate.expect(
        len(glosses) == 1000 and len(gloss_by_lemma) == 1000,
        "source.glosses.lemma_keys",
        "reviewed zh-Hant gloss layer holds exactly 1,000 uniquely keyed lemmas",
        actual=len(gloss_by_lemma),
    )
    for item in vocab:
        item["glossZh"] = gloss_by_lemma.get(f"{item['strong']}|{item['pointed']}", "")
    gate.expect(
        all(item["glossZh"] for item in vocab),
        "source.glosses.coverage",
        "every headword resolves to a reviewed Traditional-Chinese gloss",
        failures=[item["pointed"] for item in vocab if not item["glossZh"]][:30],
    )
    lesson_groups: dict[int, list[dict]] = {}
    for item in vocab:
        lesson_groups.setdefault(int(item.get("lesson", -1)), []).append(item)
    gate.expect(
        sorted(lesson_groups) == list(range(1, 51))
        and all(items for items in lesson_groups.values()),
        "source.vocabulary.lessons",
        "source vocabulary is exactly 50 lessons of 20 words",
        lessonSizes={str(key): len(value) for key, value in lesson_groups.items()},
    )
    pointed_failures = [item["ordinal"] for item in vocab if unpointed_words(item.get("pointed", ""))]
    translit_failures = [
        item["ordinal"]
        for item in vocab
        if not str(item.get("textbookTransliteration", "")).strip()
        or HEBREW_LETTER.search(str(item.get("textbookTransliteration", "")))
        or has_replacement_glyph(str(item.get("textbookTransliteration", "")))
        or "Pratico-Van Pelt BBH2" not in str(item.get("transliterationSystem", ""))
    ]
    zh_failures = [
        item["ordinal"]
        for item in vocab
        if not is_zh_hant_field(item.get("glossZh", ""), forbid_ascii=True)
    ]
    gate.expect(not pointed_failures, "source.vocabulary.pointing", "all 1,000 headwords retain niqqud", failures=pointed_failures[:30])
    gate.expect(not translit_failures, "source.vocabulary.transliteration", "all 1,000 headwords have Pratico–Van Pelt BBH2 transliteration", failures=translit_failures[:30])
    gate.expect(not zh_failures, "source.vocabulary.zh_hant", "all 1,000 glosses are non-placeholder Traditional Chinese with no English leakage", failures=zh_failures[:30])

    # The inventory is now split: person/place/nation names live in the appendix
    # file, and only divine names plus a few words that read as ordinary
    # vocabulary stay in the lessons.  Both halves are checked together so the
    # 135 verified Chinese names cannot be lost by moving one of them.
    lifted_names = load_json(NAMES_PATH)["items"]
    in_lessons = [item for item in vocab if item.get("isProperName")]
    inventory = in_lessons + lifted_names
    lemma_keys = {f"{item['strong']}|{item['pointed']}" for item in inventory}

    type_failures = [item["pointed"] for item in inventory if not item.get("properNameTypes")]
    gold_failures: list[dict[str, Any]] = []
    for item in inventory:
        key = f"{item['strong']}|{item['pointed']}"
        expected = PROPER_NAME_GOLD.get(key)
        gloss = item.get("glossZh", "")
        if not expected or any(fragment not in gloss for fragment in expected):
            gold_failures.append({"lemma": key, "expected": expected, "actual": gloss})

    lifted_types = {"person", "place", "people_or_nation"}
    leaked = [
        item["pointed"]
        for item in in_lessons
        if lifted_types.intersection(item.get("properNameTypes") or []) and not item.get("keptInLessons")
    ]

    gate.expect(len(inventory) == 135, "source.proper_names.count", "proper-name inventory contains exactly 135 entries across lessons and appendix", actual=len(inventory))
    gate.expect(len(lemma_keys) == len(inventory), "source.proper_names.unique", "no proper name is listed twice", actual=len(lemma_keys))
    gate.expect(len(PROPER_NAME_GOLD) == 135, "source.proper_names.gold_count", "gold list covers all 135 proper names", actual=len(PROPER_NAME_GOLD))
    gate.expect(not type_failures, "source.proper_names.types", "every proper name records person/place/people/divine type metadata", failures=type_failures)
    gate.expect(not gold_failures, "source.proper_names.conventional_zh", "all proper names retain conventional Traditional-Chinese biblical forms", failures=gold_failures[:30])
    gate.expect(not leaked, "source.proper_names.lifted", "no person, place or nation name is still taking a lesson slot", failures=leaked)
    return vocab, {int(item["ordinal"]): item for item in vocab}


def validate_memory_metadata(
    gate: Gate,
    memory: list[dict],
    vocab_by_ordinal: dict[int, dict],
    code_prefix: str,
) -> None:
    refs = [str(item.get("ref", "")).strip() for item in memory]
    pairs = [(item.get("lesson"), item.get("slot")) for item in memory]
    gate.expect(
        len(memory) == 100 and len(set(refs)) == 100 and all(refs),
        f"{code_prefix}.unique",
        "memory corpus contains exactly 100 unique verse references",
        count=len(memory), unique=len(set(refs)),
    )
    gate.expect(
        len(set(pairs)) == 100
        and all(sum(int(item.get("lesson", -1)) == lesson for item in memory) == 2 for lesson in range(1, 51)),
        f"{code_prefix}.lesson_slots",
        "every lesson has exactly two unique memory slots",
        uniqueSlots=len(set(pairs)),
    )
    metadata_failures: list[dict[str, Any]] = []
    total_hits = 0
    for item in memory:
        lesson = int(item.get("lesson", -1))
        hits = item.get("matchedLessonVocabulary")
        if not isinstance(hits, list):
            metadata_failures.append({"ref": item.get("ref"), "error": "matchedLessonVocabulary missing"})
            continue
        total_hits += len(hits)
        expected_range = range((lesson - 1) * 20 + 1, lesson * 20 + 1)
        if item.get("matchedCount") != len(hits):
            metadata_failures.append({"ref": item.get("ref"), "error": "matchedCount mismatch"})
        if not isinstance(item.get("knownCoverage"), (int, float)) or not 0 <= float(item["knownCoverage"]) <= 1:
            metadata_failures.append({"ref": item.get("ref"), "error": "knownCoverage invalid"})
        if not str(item.get("selectionReason", "")).strip():
            metadata_failures.append({"ref": item.get("ref"), "error": "selectionReason missing"})
        hit_ordinals: list[int] = []
        for hit in hits:
            try:
                ordinal = int(hit["ordinal"])
            except Exception:
                metadata_failures.append({"ref": item.get("ref"), "error": "hit ordinal invalid"})
                continue
            hit_ordinals.append(ordinal)
            source = vocab_by_ordinal.get(ordinal)
            if ordinal not in expected_range or not source:
                metadata_failures.append({"ref": item.get("ref"), "error": f"hit {ordinal} is outside lesson {lesson}"})
                continue
            if hit.get("pointed") != source.get("pointed"):
                metadata_failures.append({"ref": item.get("ref"), "error": f"hit {ordinal} pointed form mismatch"})
            if not hit.get("strongs") and not hit.get("lemma"):
                metadata_failures.append({"ref": item.get("ref"), "error": f"hit {ordinal} lacks lexical identity"})
            if bool(hit.get("isProperName")) != bool(source.get("isProperName")):
                metadata_failures.append({"ref": item.get("ref"), "error": f"hit {ordinal} proper-name flag mismatch"})
        if len(hit_ordinals) != len(set(hit_ordinals)):
            metadata_failures.append({"ref": item.get("ref"), "error": "duplicate hit ordinal"})
    gate.expect(
        not metadata_failures and total_hits > 0,
        f"{code_prefix}.vocabulary_hit_metadata",
        "all 100 memory verses carry internally consistent lesson-vocabulary hit metadata",
        totalHits=total_hits, failures=metadata_failures[:40],
    )


def validate_source_corpora(gate: Gate, vocab_by_ordinal: dict[int, dict]) -> None:
    scripture = load_json(SCRIPTURE_PATH)
    chapters = scripture.get("chapters", [])
    memory = scripture.get("memoryVerses", [])
    chapter_refs = [item.get("ref") for item in chapters]
    complete_failures: list[dict[str, Any]] = []
    accent_failures: list[str] = []
    pointing_failures: list[str] = []
    for chapter in chapters:
        verses = chapter.get("verses", [])
        verse_numbers = [int(verse.get("verse", -1)) for verse in verses]
        if len(verses) != int(chapter.get("verseCount", -1)) or len(set(verse_numbers)) != len(verses):
            complete_failures.append({"ref": chapter.get("ref"), "expected": chapter.get("verseCount"), "actual": len(verses)})
        for verse in verses:
            text = verse.get("text", "")
            # This source-oriented chapter layer deliberately preserves the
            # unpointed ketiv beside its pointed qere.  Its producer records a
            # token-level audit; the learner-facing master is independently
            # checked below after it has selected the pointed qere reading.
            if not HEBREW_VOWEL.search(text):
                pointing_failures.append(str(verse.get("ref")))
            if not HEBREW_ACCENT.search(text):
                accent_failures.append(str(verse.get("ref")))
    gate.expect(len(chapters) == 25 and len(set(chapter_refs)) == 25, "source.scripture.chapter_count", "scripture source contains 25 unique complete chapters", actual=len(chapters))
    gate.expect(not complete_failures, "source.scripture.chapter_completeness", "each selected chapter contains its declared complete verse set", failures=complete_failures)
    source_audit = scripture.get("validation", {})
    pointing_audit_ok = all(
        source_audit.get(key) == 0
        for key in (
            "missingNiqqudCount",
            "unpointedNonKetivWordCount",
            "qereMissingNiqqudCount",
            "ketivWithoutQereCount",
        )
    )
    gate.expect(
        not pointing_failures and pointing_audit_ok,
        "source.scripture.niqqud",
        "all biblical verses retain Masoretic vocalization, with unpointed tokens limited to audited ketiv readings",
        failures=pointing_failures[:30],
        ketivWordCount=source_audit.get("ketivWordCount"),
        qereWordCount=source_audit.get("qereWordCount"),
        unpointedNonKetivWordCount=source_audit.get("unpointedNonKetivWordCount"),
        qereMissingNiqqudCount=source_audit.get("qereMissingNiqqudCount"),
    )
    gate.expect(not accent_failures, "source.scripture.cantillation", "all biblical verses retain cantillation marks", failures=accent_failures[:30])
    validate_memory_metadata(gate, memory, vocab_by_ordinal, "source.memory")

    prayers = load_json(PRAYERS_PATH)
    items = prayers.get("items", [])
    prayer_failures: list[dict[str, Any]] = []
    for item in items:
        text = item.get("text", "")
        if not text.strip() or unpointed_words(text):
            prayer_failures.append({"id": item.get("id"), "error": "empty or unpointed text"})
        if item.get("fullPointingStatus") not in {"source_pointed_complete", "editorial_pointed_complete"}:
            prayer_failures.append({"id": item.get("id"), "error": "pointing status incomplete"})
        if not is_zh_hant_field(str(item.get("title_zh", ""))):
            prayer_failures.append({"id": item.get("id"), "error": "title_zh invalid"})
        if not is_zh_hant_field(str(item.get("summaryZh", ""))):
            prayer_failures.append({"id": item.get("id"), "error": "summaryZh invalid"})
    gate.expect(len(items) == 25 and not prayer_failures, "source.prayers.complete", "25 prayers/articles are nonempty, pointed, and carry Traditional-Chinese title/summary", actual=len(items), failures=prayer_failures[:30])

    validate_haggadah(gate, load_json(HAGGADAH_PATH), "source.haggadah")


def validate_haggadah(gate: Gate, haggadah: dict, code_prefix: str) -> None:
    steps = haggadah.get("steps", [])
    segments = [segment for step in steps for segment in step.get("segments", [])]
    ids = [segment.get("id") for segment in segments]
    step_ordinals = [step.get("ordinal") for step in steps]
    pointing_failures: list[str] = []
    structure_failures: list[str] = []
    for step in steps:
        step_segments = step.get("segments", [])
        ordinals = [segment.get("ordinal") for segment in step_segments]
        if (
            not all(isinstance(value, int) and value > 0 for value in ordinals)
            or ordinals != sorted(ordinals)
            or len(ordinals) != len(set(ordinals))
        ):
            structure_failures.append(str(step.get("key")))
        if unpointed_words(step.get("text", "")):
            pointing_failures.append(str(step.get("key")))
        if not is_zh_hant_field(str(step.get("title_zh", ""))):
            structure_failures.append(f"{step.get('key')}:title_zh")
    gate.expect(
        len(steps) == 15
        and step_ordinals == list(range(1, 16))
        and haggadah.get("stepCount") == 15,
        f"{code_prefix}.steps",
        "Haggadah contains the ordered 15-step Seder flow",
        actual=len(steps),
    )
    gate.expect(
        len(segments) == 199
        and haggadah.get("segmentCount") == 199
        and len(set(ids)) == 199
        and all(ids),
        f"{code_prefix}.segments",
        "Haggadah contains exactly 199 uniquely identified segments",
        actual=len(segments), unique=len(set(ids)),
    )
    gate.expect(
        not structure_failures,
        f"{code_prefix}.structure",
        "Haggadah step ordinals and traceable, increasing source-segment ordinals plus Traditional-Chinese titles are valid",
        failures=structure_failures,
    )
    gate.expect(
        haggadah.get("pointingGapCount") == 0 and not pointing_failures,
        f"{code_prefix}.pointing",
        "Haggadah running text has no pointing gaps",
        failures=pointing_failures,
    )


def _wlc_psalm_counts() -> dict[int, int]:
    root = ET.parse(WLC_PSALMS_PATH).getroot()
    namespace = "{http://www.bibletechnologies.net/2003/OSIS/namespace}"
    counts: dict[int, int] = {}
    for chapter in root.iter(f"{namespace}chapter"):
        reference = chapter.get("osisID", "")
        if reference.startswith("Ps."):
            counts[int(reference.split(".")[1])] = sum(
                1 for _ in chapter.iter(f"{namespace}verse")
            )
    return counts


def validate_rcuv_snapshot(gate: Gate, master: dict) -> None:
    index, metadata = load_rcuv_snapshot(RCUV_PATH)
    psalm_counts = _wlc_psalm_counts()
    records: list[dict[str, Any]] = []
    chapter_records: list[dict[str, Any]] = []
    memory_records: list[dict[str, Any]] = []
    for lesson in master.get("lessons", []):
        reading = lesson.get("reading") or {}
        if reading.get("kind") == "bible_chapter":
            for verse in reading.get("verses") or []:
                record = {
                    "ref": verse.get("ref"),
                    "book": reading.get("osisBook") or reading.get("bookCode"),
                    "chapter": verse.get("chapter"),
                    "verse": verse.get("verse"),
                    "actual": verse.get("translationZh"),
                    "crosswalk": verse.get("translationCrosswalk"),
                    "layer": "chapter",
                }
                records.append(record)
                chapter_records.append(record)
        for verse in lesson.get("memoryVerses") or []:
            record = {
                "ref": verse.get("ref"),
                "book": verse.get("osisBook") or verse.get("bookCode"),
                "chapter": verse.get("chapter"),
                "verse": verse.get("verse"),
                "actual": verse.get("translationZh"),
                "crosswalk": verse.get("translationCrosswalk"),
                "layer": "memory",
            }
            records.append(record)
            memory_records.append(record)

    failures: list[dict[str, Any]] = []
    for record in records:
        book_name = BOOK_TO_CHINESE_SOURCE_NAME.get(str(record["book"]))
        if not book_name:
            failures.append({"ref": record["ref"], "error": "unsupported book code"})
            continue
        expected_entry = translation_entry_for_mt(
            index,
            book_name,
            int(record["chapter"]),
            int(record["verse"]),
            mt_psalm_counts=psalm_counts,
        )
        expected = expected_entry.get("text") or ""
        if not expected or str(record["actual"]) != expected:
            failures.append({
                "ref": record["ref"],
                "layer": record["layer"],
                "expected": expected,
                "actual": record["actual"],
            })
            continue
        crosswalk = record.get("crosswalk") or {}
        for key in (
            "translationVersionCode", "translationVariant", "translationRef",
            "translationRange", "combinedVerseRange", "superscriptionIncluded",
        ):
            if crosswalk.get(key) != expected_entry.get(key):
                failures.append({
                    "ref": record["ref"],
                    "layer": record["layer"],
                    "error": f"crosswalk mismatch: {key}",
                    "expected": expected_entry.get(key),
                    "actual": crosswalk.get(key),
                })
                break

    plan = load_json(SCRIPTURE_PATH)
    plan_translation_failures: list[dict[str, Any]] = []
    for verse in plan.get("memoryVerses") or []:
        book_name = BOOK_TO_CHINESE_SOURCE_NAME.get(
            str(verse.get("osisBook") or verse.get("bookCode"))
        )
        expected = translation_for_mt(
            index,
            str(book_name or ""),
            int(verse.get("chapter") or 0),
            int(verse.get("verse") or 0),
            mt_psalm_counts=psalm_counts,
        ) if book_name else ""
        if not expected or verse.get("translationZh") != expected:
            plan_translation_failures.append({
                "ref": verse.get("ref"),
                "expected": expected,
                "actual": verse.get("translationZh"),
            })

    unique_refs = {str(record["ref"]) for record in records}
    gate.expect(
        metadata.get("versionCode") == "cuv2010"
        and metadata.get("variant") == "RCUV2（上帝版）",
        "source.rcuv2010.metadata",
        "Traditional-Chinese source is explicitly RCUV2010 RCUV2（上帝版）",
        actual=metadata,
    )
    # The unique-reference total is derived, not frozen: it is the union of the
    # 25 fixed chapters and the 100 memory verses, and it shifts whenever the
    # memory verses land inside or outside those chapters.
    expected_unique = len({str(record["ref"]) for record in chapter_records} | {str(record["ref"]) for record in memory_records})
    gate.expect(
        len(chapter_records) == 614
        and len(memory_records) == 100
        and len(unique_refs) == expected_unique
        and not failures,
        "source.rcuv2010.crosswalk",
        f"all 614 chapter positions and 100 memory verses ({expected_unique} unique MT refs) exactly match the frozen RCUV2010 crosswalk",
        chapterPositions=len(chapter_records),
        memoryPositions=len(memory_records),
        uniqueRefs=len(unique_refs),
        failures=failures[:40],
    )
    gate.expect(
        not plan_translation_failures,
        "source.rcuv2010.memory-plan",
        "the persisted 100-verse review plan contains the same frozen RCUV2010 text",
        failures=plan_translation_failures[:40],
    )



REFERENCE_TABLE_IDS = (
    "hbo-appendix-numerals",
    "hbo-appendix-kinship",
    "hbo-appendix-calendar",
    "hbo-appendix-proper-names",
)


def validate_reference_tables(gate: Gate, master: dict) -> None:
    """Check the four appendix tables the reader ships behind the Haggadah."""

    payload = master.get("referenceTables") or {}
    tables = payload.get("tables") or []
    gate.expect(
        tuple(table.get("id") for table in tables) == REFERENCE_TABLE_IDS,
        "master.reference_tables.present",
        "master carries the numeral, kinship, calendar and proper-name tables in order",
        actual=[table.get("id") for table in tables],
    )

    empty_groups: list[str] = []
    blank_gloss: list[str] = []
    unpointed: list[str] = []
    for table in tables:
        for group in table.get("groups") or []:
            entries = group.get("entries") or []
            if not entries:
                empty_groups.append(str(group.get("id")))
            for entry in entries:
                if not str(entry.get("glossZh", "")).strip():
                    blank_gloss.append(f"{group.get('id')}/{entry.get('pointed', '')}")
                pointed = entry.get("pointed") or (entry.get("masculine") or {}).get("pointed") or ""
                if pointed and unpointed_words(pointed):
                    unpointed.append(pointed)
    gate.expect(not empty_groups, "master.reference_tables.groups", "no appendix section is empty", failures=empty_groups)
    gate.expect(not blank_gloss, "master.reference_tables.zh_hant", "every appendix row carries a Traditional-Chinese meaning", failures=blank_gloss[:30])
    gate.expect(not unpointed, "master.reference_tables.pointing", "every appendix headword keeps full niqqud", failures=unpointed[:30])

    calendar = next((table for table in tables if table.get("id") == "hbo-appendix-calendar"), {})
    post = next(
        (group for group in calendar.get("groups") or [] if group.get("id") == "babylonian-months-post"),
        {},
    )
    entries = post.get("entries") or []
    gate.expect(
        len(entries) == 5
        and all(entry.get("attestation") == "post_biblical" for entry in entries)
        and bool(str(post.get("source", "")).strip()),
        "master.reference_tables.post_biblical",
        "the five months absent from the Masoretic Text stay labelled and sourced",
        actual=[entry.get("glossZh") for entry in entries],
    )

def validate_master(gate: Gate, master_path: Path, vocab_by_ordinal: dict[int, dict]) -> dict | None:
    if not master_path.exists():
        gate.artifact_missing("master.present", master_path)
        return None
    data = load_json(master_path)
    lessons = data.get("lessons", [])
    lesson_numbers = [lesson.get("lesson") for lesson in lessons]
    lesson_ids = [lesson.get("id") for lesson in lessons]
    gate.expect(
        len(lessons) == 50
        and lesson_numbers == list(range(1, 51))
        and len(set(lesson_ids)) == 50
        and all(lesson_ids),
        "master.lessons",
        "master JSON contains ordered, uniquely identified lessons 1..50",
        actual=len(lessons),
    )

    all_vocab: list[dict] = []
    all_memory: list[dict] = []
    lesson_failures: list[dict[str, Any]] = []
    reading_kinds: list[str] = []
    chapter_failures: list[str] = []
    prayer_failures: list[str] = []
    for lesson in lessons:
        number = int(lesson.get("lesson", -1))
        vocab = lesson.get("vocabulary", [])
        memory = lesson.get("memoryVerses", [])
        all_vocab.extend(vocab)
        all_memory.extend(memory)
        # Lesson size follows the textbook chapter, so only continuity of the
        # global ordinals is invariant, not a fixed count per lesson.
        ordinals = [item.get("ordinal") for item in vocab]
        contiguous = bool(ordinals) and ordinals == list(range(ordinals[0], ordinals[0] + len(ordinals)))
        if not contiguous or len(memory) != 2:
            lesson_failures.append({"lesson": number, "vocabulary": len(vocab), "memory": len(memory)})
        reading = lesson.get("reading", {})
        kind = reading.get("kind")
        reading_kinds.append(kind)
        if number <= 25:
            verses = reading.get("verses", [])
            if kind != "bible_chapter" or not verses or len(verses) != int(reading.get("verseCount", -1)):
                chapter_failures.append(str(lesson.get("id")))
            for verse in verses:
                if unpointed_words(verse.get("text", "")) or not HEBREW_ACCENT.search(verse.get("text", "")):
                    chapter_failures.append(str(verse.get("ref")))
                if not is_zh_hant_field(str(verse.get("translationZh", ""))):
                    chapter_failures.append(f"{verse.get('ref')}:translationZh")
        else:
            if kind != "prayer_or_article" or not reading.get("text", "").strip() or unpointed_words(reading.get("text", "")):
                prayer_failures.append(str(lesson.get("id")))
            if not is_zh_hant_field(str(reading.get("title_zh", ""))) or not is_zh_hant_field(str(reading.get("summaryZh", ""))):
                prayer_failures.append(f"{lesson.get('id')}:zh")

    gate.expect(not lesson_failures, "master.lesson_payloads", "every lesson contains a contiguous run of vocabulary items and two memory verses", failures=lesson_failures)
    vocab_ordinals = [item.get("ordinal") for item in all_vocab]
    gate.expect(len(all_vocab) == 1000 and vocab_ordinals == list(range(1, 1001)), "master.vocabulary", "master contains each of the 1,000 vocabulary entries exactly once", actual=len(all_vocab))
    gate.expect(not chapter_failures and reading_kinds[:25] == ["bible_chapter"] * 25, "master.bible_chapters", "lessons 1–25 contain 25 complete pointed/cantillated chapters with zh-Hant translations", failures=chapter_failures[:40])
    gate.expect(not prayer_failures and reading_kinds[25:] == ["prayer_or_article"] * 25, "master.prayers", "lessons 26–50 contain 25 complete pointed prayers/articles with zh-Hant metadata", failures=prayer_failures[:40])
    validate_memory_metadata(gate, all_memory, vocab_by_ordinal, "master.memory")

    translit_failures = [
        item.get("ordinal") for item in all_vocab
        if not str(item.get("textbookTransliteration", "")).strip()
        or "Pratico-Van Pelt BBH2" not in str(item.get("transliterationSystem", ""))
    ]
    zh_failures = [item.get("ordinal") for item in all_vocab if not is_zh_hant_field(str(item.get("glossZh", "")), forbid_ascii=True)]
    proper = [item for item in all_vocab if item.get("isProperName")]
    gate.expect(not translit_failures, "master.transliteration", "master retains BBH2 textbook transliteration for every vocabulary item", failures=translit_failures[:30])
    gate.expect(not zh_failures, "master.zh_hant_glosses", "master retains reviewed Traditional-Chinese glosses", failures=zh_failures[:30])
    gate.expect(
        len(proper) == 16,
        "master.proper_names",
        "master keeps only the divine names, the sabbath and the four common nouns in the lessons",
        actual=len(proper),
    )
    validate_reference_tables(gate, data)

    counts = data.get("counts", {})
    declared_count_keys = {
        "lessons",
        "vocabulary",
        "memoryVerses",
        "bibleChapters",
        "prayersOrArticles",
        "haggadahSteps",
    }
    count_failures = {
        key: {"expected": expected, "actual": counts.get(key)}
        for key, expected in EXPECTED_COUNTS.items()
        if key in declared_count_keys and counts.get(key) != expected
    }
    gate.expect(not count_failures, "master.declared_counts", "master declared counts agree with the release contract", failures=count_failures)
    profile = data.get("printProfile", {})
    gate.expect(
        profile.get("trim") == "JIS_B5"
        and math.isclose(float(profile.get("widthMm", 0)), 182, abs_tol=0.1)
        and math.isclose(float(profile.get("heightMm", 0)), 257, abs_tol=0.1)
        and profile.get("mirroredMargins") is True,
        "master.print_profile",
        "master declares JIS B5 182×257 mm with mirrored margins",
        actual=profile,
    )
    gate.expect(data.get("privateUse") is True, "master.private_use", "master remains explicitly marked for private use")
    chinese_source = (data.get("sources") or {}).get("chineseBible") or {}
    legacy_markers = ("ChiUn", "官話和合本", "cuv1919")
    all_chinese = [
        str(verse.get("translationZh", ""))
        for lesson in lessons
        for verse in (
            lesson.get("memoryVerses", [])
            + (lesson.get("reading", {}).get("verses", []) if lesson.get("reading", {}).get("kind") == "bible_chapter" else [])
        )
    ]
    gate.expect(
        chinese_source.get("versionCode") == "cuv2010"
        and chinese_source.get("variant") == "RCUV2（上帝版）"
        and "和合本修訂版" in str(chinese_source.get("titleZh", ""))
        and all(all(marker not in value for marker in legacy_markers) for value in all_chinese),
        "master.chinese_bible_version",
        "every Bible translation is sourced from the explicit RCUV2010 RCUV2（上帝版） snapshot with no legacy ChiUn fallback",
        actual=chinese_source,
    )
    validate_rcuv_snapshot(gate, data)
    validate_haggadah(gate, data.get("haggadah", {}), "master.haggadah")
    return data


def _xml_text(root: ET.Element) -> str:
    return "".join(node.text or "" for node in root.iter(f"{W}t"))


def validate_docx(gate: Gate, docx_path: Path, master: dict | None) -> None:
    if not docx_path.exists():
        gate.artifact_missing("docx.present", docx_path)
        return
    with zipfile.ZipFile(docx_path) as archive:
        names = set(archive.namelist())
        required_parts = {"word/document.xml", "word/settings.xml", "word/styles.xml"}
        gate.expect(required_parts <= names, "docx.package", "DOCX contains required WordprocessingML parts", missing=sorted(required_parts - names))
        document = ET.fromstring(archive.read("word/document.xml"))
        settings = ET.fromstring(archive.read("word/settings.xml"))

    text = _xml_text(document)
    bad_glyphs = sorted(set(text) & REPLACEMENT_GLYPHS)
    unexpected_squares = len(re.findall(r"□(?!\s*\d+\.)", text))
    gate.expect(
        not bad_glyphs and unexpected_squares == 0,
        "docx.glyphs",
        "DOCX text contains no replacement/missing-glyph characters (intentional numbered checkboxes allowed)",
        glyphs=bad_glyphs,
        unexpectedSquares=unexpected_squares,
    )
    gate.expect(document.find(f".//{W}altChunk") is None, "docx.altchunk", "DOCX has no unresolved altChunk content")

    expected_w = round(182 / 25.4 * 1440)
    expected_h = round(257 / 25.4 * 1440)
    section_failures: list[dict[str, Any]] = []
    sections = document.findall(f".//{W}sectPr")
    for index, section in enumerate(sections, 1):
        page = section.find(f"{W}pgSz")
        if page is None:
            section_failures.append({"section": index, "error": "pgSz missing"})
            continue
        width = int(page.attrib.get(f"{W}w", 0))
        height = int(page.attrib.get(f"{W}h", 0))
        if abs(width - expected_w) > 3 or abs(height - expected_h) > 3:
            section_failures.append({"section": index, "width": width, "height": height})
    mirror = settings.find(f".//{W}mirrorMargins") is not None
    gate.expect(bool(sections) and not section_failures and mirror, "docx.jis_b5", "all DOCX sections are JIS B5 with mirrored margins", sections=len(sections), failures=section_failures, mirrorMargins=mirror)

    table_failures: list[dict[str, Any]] = []
    tables = document.findall(f".//{W}tbl")
    for index, table in enumerate(tables, 1):
        props = table.find(f"{W}tblPr")
        layout = props.find(f"{W}tblLayout") if props is not None else None
        width_node = props.find(f"{W}tblW") if props is not None else None
        indent = props.find(f"{W}tblInd") if props is not None else None
        grid = table.find(f"{W}tblGrid")
        columns = grid.findall(f"{W}gridCol") if grid is not None else []
        try:
            table_width = int(width_node.attrib[f"{W}w"]) if width_node is not None else 0
            column_widths = [int(node.attrib[f"{W}w"]) for node in columns]
        except (KeyError, ValueError):
            table_width, column_widths = 0, []
        errors = []
        if layout is None or layout.attrib.get(f"{W}type") != "fixed":
            errors.append("tblLayout is not fixed")
        if width_node is None or width_node.attrib.get(f"{W}type") != "dxa" or table_width <= 0:
            errors.append("tblW is not positive dxa")
        if indent is None or indent.attrib.get(f"{W}type") != "dxa":
            errors.append("tblInd is missing/not dxa")
        if not column_widths or sum(column_widths) != table_width:
            errors.append(f"tblGrid sum {sum(column_widths)} != tblW {table_width}")
        cell_widths = table.findall(f".//{W}tcPr/{W}tcW")
        if not cell_widths or any(node.attrib.get(f"{W}type") != "dxa" or int(node.attrib.get(f"{W}w", 0)) <= 0 for node in cell_widths):
            errors.append("one or more tcW values are missing/non-positive/non-dxa")
        if errors:
            table_failures.append({"table": index, "errors": errors})
    gate.expect(len(tables) >= 50 and not table_failures, "docx.table_geometry", "all DOCX tables use fixed, internally exact dxa geometry with tblInd", tables=len(tables), failures=table_failures[:40])

    key_texts = [
        "聖經希伯來文原文讀本",
        "來源與成品檢核",
        "分類專名表",
        "數字：基數、序數與分數",
        "親屬稱謂",
        "曆法：月名、節期與時間單位",
        "第1–25課為25個完整聖經章",
        "第26–50課為25篇完整禱文或文章",
        "蒙悅納與結語",
        "禱文、拉比文章與 Haggadah",
    ]
    if master and master.get("haggadah", {}).get("steps"):
        key_texts.append(str(master["haggadah"]["steps"][-1].get("title_he", "")))
    missing_key_texts = [value for value in key_texts if value and value not in text]
    gate.expect(not missing_key_texts, "docx.key_text", "DOCX contains cover, terminal Haggadah, indices, and final source-check text", missing=missing_key_texts)


def _pdf_object(value: Any) -> Any:
    return value.get_object() if hasattr(value, "get_object") else value


def _font_record(font: Any) -> tuple[str, bool, str]:
    font = _pdf_object(font)
    subtype = str(font.get("/Subtype", ""))
    base = str(font.get("/BaseFont", "")).lstrip("/")
    descriptor = None
    if subtype == "/Type0":
        descendants = _pdf_object(font.get("/DescendantFonts", []))
        if descendants:
            descendant = _pdf_object(descendants[0])
            base = str(descendant.get("/BaseFont", base)).lstrip("/")
            descriptor = _pdf_object(descendant.get("/FontDescriptor")) if descendant.get("/FontDescriptor") else None
    elif font.get("/FontDescriptor"):
        descriptor = _pdf_object(font.get("/FontDescriptor"))
    embedded = subtype == "/Type3" or bool(
        descriptor and any(descriptor.get(key) is not None for key in ("/FontFile", "/FontFile2", "/FontFile3"))
    )
    return base, embedded, subtype



def _drawn_font_names(pdf_path: Path) -> set[str]:
    """Return the base names of fonts that actually render at least one glyph."""

    try:
        import pdfplumber
    except ImportError:
        return set()
    names: set[str] = set()
    with pdfplumber.open(pdf_path) as document:
        for page in document.pages:
            for character in page.chars:
                names.add(str(character.get("fontname") or ""))
            page.close()
    return names


def validate_pdf(gate: Gate, pdf_path: Path, min_pages: int) -> None:
    if not pdf_path.exists():
        gate.artifact_missing("pdf.present", pdf_path)
        return
    try:
        from pypdf import PdfReader
    except Exception as error:
        gate.add("FAIL", "pdf.pypdf", f"pypdf is required for final PDF QA: {error}")
        return
    reader = PdfReader(str(pdf_path))
    pages = reader.pages
    size_failures: list[dict[str, Any]] = []
    extracted: list[str] = []
    font_records: dict[str, dict[str, Any]] = {}
    for index, page in enumerate(pages, 1):
        width_mm = float(page.mediabox.width) / 72 * 25.4
        height_mm = float(page.mediabox.height) / 72 * 25.4
        if not (math.isclose(width_mm, 182, abs_tol=0.3) and math.isclose(height_mm, 257, abs_tol=0.3)):
            size_failures.append({"page": index, "widthMm": round(width_mm, 3), "heightMm": round(height_mm, 3)})
        try:
            extracted.append(page.extract_text() or "")
        except Exception as error:
            extracted.append("")
            gate.add("FAIL", "pdf.text_extract_exception", f"page {index} text extraction failed: {error}")
        resources = _pdf_object(page.get("/Resources", {}))
        fonts = _pdf_object(resources.get("/Font", {})) if resources else {}
        for resource_name, font in (fonts or {}).items():
            base, embedded, subtype = _font_record(font)
            key = f"{resource_name}:{base}:{subtype}"
            font_records.setdefault(key, {"resource": str(resource_name), "baseFont": base, "subtype": subtype, "embedded": embedded, "pages": []})
            font_records[key]["pages"].append(index)

    gate.expect(len(pages) >= min_pages, "pdf.page_count", f"PDF has at least {min_pages} pages, preventing a truncated full reader", actual=len(pages))
    gate.expect(not size_failures, "pdf.jis_b5", "every PDF page is JIS B5 182×257 mm", failures=size_failures[:40])

    drawn_font_names = _drawn_font_names(pdf_path)
    fonts = list(font_records.values())
    unembedded = [record for record in fonts if not record["embedded"]]
    font_names = [record["baseFont"] for record in fonts]
    # A fallback font matters only if it actually renders a glyph.  LibreOffice
    # registers Tahoma as a page resource on every page of this book without
    # drawing a single character in it, and failing on the declaration alone
    # blocks a release over nothing.
    forbidden_pattern = re.compile(r"MSGothic|MS.?Gothic|Tahoma|Calibri", re.I)
    declared_forbidden = [name for name in font_names if forbidden_pattern.search(name)]
    forbidden = sorted({name for name in declared_forbidden if name in drawn_font_names})
    gate.expect(
        not (set(declared_forbidden) - set(forbidden)),
        "pdf.fallback_declared_unused",
        "fallback fonts appear only as unused page resources",
        declared=sorted(set(declared_forbidden)),
    )
    has_hebrew_font = any(re.search(r"Hebrew", name, re.I) for name in font_names)
    has_cjk_font = any(re.search(r"MingLiU|NotoSansTC|NotoSerifCJK|SourceHan|MSung|MHei", name, re.I) for name in font_names)
    gate.expect(bool(fonts) and not unembedded, "pdf.fonts_embedded", "every PDF font resource is embedded", fonts=fonts, unembedded=unembedded)
    gate.expect(has_hebrew_font and has_cjk_font and not forbidden, "pdf.font_families", "PDF contains embedded Hebrew and Traditional-Chinese font families without known fallback fonts", fontNames=font_names, forbidden=forbidden, hasHebrew=has_hebrew_font, hasCjk=has_cjk_font)

    nonempty_pages = sum(bool(re.sub(r"\s+", "", text)) for text in extracted)
    all_text = "\n".join(extracted)
    ratio = nonempty_pages / len(pages) if pages else 0
    key_texts = ("聖經希伯來文原文讀本", "來源與成品檢核", "分類專名表", "數字：基數、序數與分數", "蒙悅納與結語")
    missing = [value for value in key_texts if value not in all_text]
    gate.expect(
        ratio >= 0.98
        and len(HEBREW_LETTER.findall(all_text)) >= 1000
        and len(CJK.findall(all_text)) >= 1000
        and not missing
        and not has_replacement_glyph(all_text),
        "pdf.text_layer",
        "PDF has a searchable Hebrew/Traditional-Chinese text layer through the terminal matter",
        nonemptyPages=nonempty_pages,
        pageCount=len(pages),
        nonemptyRatio=round(ratio, 4),
        hebrewCharacters=len(HEBREW_LETTER.findall(all_text)),
        cjkCharacters=len(CJK.findall(all_text)),
        missingKeyTexts=missing,
    )


def existing_inputs(paths: Iterable[Path]) -> list[dict[str, Any]]:
    result = []
    for path in paths:
        record: dict[str, Any] = {"path": str(path), "exists": path.exists()}
        if path.exists():
            record.update({"bytes": path.stat().st_size, "sha256": sha256(path)})
        result.append(record)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("preflight", "final"), default="preflight")
    parser.add_argument("--master", type=Path, default=DEFAULT_MASTER)
    parser.add_argument("--docx", type=Path, default=DEFAULT_DOCX)
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--min-pdf-pages", type=int, default=200)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    gate = Gate(args.phase)
    paths = [VOCAB_PATH, GLOSS_PATH, SCRIPTURE_PATH, PRAYERS_PATH, HAGGADAH_PATH, args.master, args.docx, args.pdf]
    for required in paths[:5]:
        if not required.exists():
            gate.add("FAIL", "source.missing", f"required source is missing: {required}")

    vocab_by_ordinal: dict[int, dict] = {}
    if all(path.exists() for path in paths[:2]):
        def check_vocabulary() -> None:
            nonlocal vocab_by_ordinal
            _vocab, vocab_by_ordinal = validate_vocabulary_sources(gate)
        gate.guard("source.vocabulary.exception", check_vocabulary)
    if vocab_by_ordinal and all(path.exists() for path in (SCRIPTURE_PATH, PRAYERS_PATH, HAGGADAH_PATH)):
        gate.guard("source.corpora.exception", lambda: validate_source_corpora(gate, vocab_by_ordinal))

    master: dict | None = None
    if vocab_by_ordinal:
        def check_master() -> None:
            nonlocal master
            master = validate_master(gate, args.master.resolve(), vocab_by_ordinal)
        gate.guard("master.exception", check_master)
    else:
        gate.artifact_missing("master.blocked", args.master.resolve())
    gate.guard("docx.exception", lambda: validate_docx(gate, args.docx.resolve(), master))
    gate.guard("pdf.exception", lambda: validate_pdf(gate, args.pdf.resolve(), args.min_pdf_pages))

    summary = gate.summary()
    result = "FAIL" if summary["FAIL"] else ("PENDING" if summary["PENDING"] else "PASS")
    report = {
        "schemaVersion": "1.0.0",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "phase": args.phase,
        "result": result,
        "releaseGatePassed": result == "PASS",
        "summary": summary,
        "contract": EXPECTED_COUNTS,
        "inputs": existing_inputs(paths),
        "checks": gate.checks,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": result, "summary": summary, "report": str(args.report)}, ensure_ascii=False))
    return 1 if summary["FAIL"] else (2 if args.phase == "final" and summary["PENDING"] else 0)


if __name__ == "__main__":
    raise SystemExit(main())
