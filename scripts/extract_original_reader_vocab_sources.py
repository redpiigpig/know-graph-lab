"""Extract ordered Hebrew and Greek vocabulary sources for the private readers."""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

import pdfplumber


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "output" / "source-cache" / "original-readers"
DATA_DIR = ROOT / "data" / "originalReaders" / "vocabulary"

BBH_VALUES = SOURCE_DIR / "bbh2-first-sheet-values.json"
MOUNCE_PDF = SOURCE_DIR / "mounce-bbg-flashcards-by-chapter.pdf"
MORPHHB_DIR = SOURCE_DIR / "morphhb-src" / "morphhb-master" / "wlc"
STRONGS_HEBREW = (
    SOURCE_DIR
    / "strongs-src"
    / "strongs-master"
    / "hebrew"
    / "strongs-hebrew-dictionary.js"
)
STRONGS_GREEK = (
    SOURCE_DIR
    / "strongs-src"
    / "strongs-master"
    / "greek"
    / "strongs-greek-dictionary.js"
)

HEBREW_CONSONANT = re.compile(r"[\u05D0-\u05EA]")
HEBREW_VOWEL = re.compile(r"[\u05B0-\u05BB\u05C7]")
HEBREW_SHUREQ = re.compile(r"\u05D5[\u0591-\u05AF]*\u05BC")
HEBREW_MARKS = re.compile(r"[\u0591-\u05C7]")
HEBREW_CANTILLATION = re.compile(r"[\u0591-\u05AF\u05BD]")
STRONG_NUMBER = re.compile(r"\d+")

HEBREW_CONSONANT_TRANSLITERATION = {
    "א": "ʾ",
    "ב": "ḇ",
    "ג": "g̅",
    "ד": "ḏ",
    "ה": "h",
    "ו": "w",
    "ז": "z",
    "ח": "ḥ",
    "ט": "ṭ",
    "י": "y",
    "כ": "ḵ",
    "ך": "ḵ",
    "ל": "l",
    "מ": "m",
    "ם": "m",
    "נ": "n",
    "ן": "n",
    "ס": "s",
    "ע": "ʿ",
    "פ": "p̄",
    "ף": "p̄",
    "צ": "ṣ",
    "ץ": "ṣ",
    "ק": "q",
    "ר": "r",
    "ש": "š",
    "ת": "ṯ",
}
HEBREW_DAGESH_TRANSLITERATION = {
    "ב": "b",
    "ג": "g",
    "ד": "d",
    "כ": "k",
    "ך": "k",
    "פ": "p",
    "ף": "p",
    "ת": "t",
}
HEBREW_VOWEL_TRANSLITERATION = {
    "\u05B1": "ĕ",
    "\u05B2": "ă",
    "\u05B3": "ŏ",
    "\u05B4": "i",
    "\u05B5": "ē",
    "\u05B6": "e",
    "\u05B7": "a",
    "\u05B8": "ā",
    "\u05B9": "ō",
    "\u05BA": "ō",
    "\u05BB": "u",
    "\u05C7": "o",
}

GREEK_TRANSLITERATION = {
    "α": "a",
    "β": "b",
    "γ": "g",
    "δ": "d",
    "ε": "e",
    "ζ": "z",
    "η": "ē",
    "θ": "th",
    "ι": "i",
    "κ": "k",
    "λ": "l",
    "μ": "m",
    "ν": "n",
    "ξ": "x",
    "ο": "o",
    "π": "p",
    "ρ": "r",
    "σ": "s",
    "ς": "s",
    "τ": "t",
    "υ": "u",
    "φ": "ph",
    "χ": "ch",
    "ψ": "ps",
    "ω": "ō",
}


def load_js_dictionary(path: Path) -> dict[str, dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    payload = text[text.index("{") : text.rindex("}") + 1]
    return json.loads(payload)


def normalize_hebrew(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = HEBREW_MARKS.sub("", text)
    return re.sub(r"[^\u05D0-\u05EA]", "", text)


def normalize_hebrew_variants(text: str) -> list[str]:
    variants = [
        normalize_hebrew(part)
        for part in re.split(r"\s*/\s*", text)
        if HEBREW_CONSONANT.search(part)
    ]
    return list(dict.fromkeys(variant for variant in variants if variant))


def vocalized_hebrew_key(text: str) -> str:
    """A cantillation-free key that still distinguishes pointed homographs."""
    text = unicodedata.normalize("NFD", text)
    text = HEBREW_CANTILLATION.sub("", text)
    return "".join(
        char
        for char in text
        if HEBREW_CONSONANT.fullmatch(char)
        or char in "\u05B0\u05B1\u05B2\u05B3\u05B4\u05B5\u05B6\u05B7\u05B8\u05B9\u05BA\u05BB\u05BC\u05C1\u05C2\u05C7"
    )


def _hebrew_clusters(word: str) -> list[tuple[str, set[str]]]:
    clusters: list[tuple[str, set[str]]] = []
    base = ""
    marks: set[str] = set()
    for char in unicodedata.normalize("NFD", word):
        if HEBREW_CONSONANT.fullmatch(char):
            if base:
                clusters.append((base, marks))
            base = char
            marks = set()
        elif base and "\u0591" <= char <= "\u05C7":
            if not HEBREW_CANTILLATION.fullmatch(char):
                marks.add(char)
    if base:
        clusters.append((base, marks))
    return clusters


def _hebrew_vowel_mark(marks: set[str]) -> str:
    return next(
        (
            mark
            for mark in (
                "\u05B1",
                "\u05B2",
                "\u05B3",
                "\u05B4",
                "\u05B5",
                "\u05B6",
                "\u05B7",
                "\u05B8",
                "\u05B9",
                "\u05BA",
                "\u05BB",
                "\u05C7",
                "\u05B0",
            )
            if mark in marks
        ),
        "",
    )


def _is_vocal_shewa(
    clusters: list[tuple[str, set[str]]], index: int
) -> bool:
    if index == 0:
        return True
    if index == len(clusters) - 1:
        return False
    previous_mark = _hebrew_vowel_mark(clusters[index - 1][1])
    next_mark = _hebrew_vowel_mark(clusters[index + 1][1])
    if previous_mark == "\u05B0":
        return True
    if next_mark == "\u05B0":
        return False
    if "\u05BC" in clusters[index][1]:
        return True
    if index == 1 and previous_mark == "\u05B8" and len(clusters) >= 3:
        return False
    return previous_mark in {"\u05B5", "\u05B8", "\u05B9", "\u05BA"}


def _is_hebrew_mater(
    clusters: list[tuple[str, set[str]]], index: int
) -> bool:
    base, marks = clusters[index]
    if base == "ו" and ("\u05B9" in marks or "\u05BA" in marks):
        return True
    if base == "ו" and "\u05BC" in marks and not _hebrew_vowel_mark(marks):
        return True
    if index == 0:
        return False
    previous_vowel = _hebrew_vowel_mark(clusters[index - 1][1])
    if base == "י" and not _hebrew_vowel_mark(marks) and previous_vowel in {
        "\u05B4",
        "\u05B5",
        "\u05B6",
    }:
        return True
    if (
        base == "ה"
        and index == len(clusters) - 1
        and "\u05BC" not in marks
        and not _hebrew_vowel_mark(marks)
        and previous_vowel in {"\u05B5", "\u05B6", "\u05B8", "\u05B9", "\u05BA"}
    ):
        return True
    return False


def transliterate_bbh_word(word: str) -> str:
    """Apply the BBH2 consonant/vowel transliteration conventions."""
    # BBH prints the common defective/qere spelling of Jerusalem without the
    # consonantal yod. Its classroom reading is still yərûšālayim.
    if normalize_hebrew(word) == "ירושלם":
        return "yərûšālayim"
    clusters = _hebrew_clusters(word)
    if not clusters:
        return word
    if normalize_hebrew(word) == "יהוה":
        return "yhwh"
    output: list[str] = []
    for index, (base, marks) in enumerate(clusters):
        vowel_mark = _hebrew_vowel_mark(marks)
        if base == "ו" and ("\u05B9" in marks or "\u05BA" in marks):
            output.append("ô")
            continue
        if base == "ו" and "\u05BC" in marks and not vowel_mark:
            output.append("û")
            continue
        if _is_hebrew_mater(clusters, index):
            continue

        if base == "ש":
            consonant = "ś" if "\u05C2" in marks else "š"
        elif "\u05BC" in marks and base in HEBREW_DAGESH_TRANSLITERATION:
            consonant = HEBREW_DAGESH_TRANSLITERATION[base]
        else:
            consonant = HEBREW_CONSONANT_TRANSLITERATION[base]

        is_mappiq_he = base == "ה" and "\u05BC" in marks
        if "\u05BC" in marks and not is_mappiq_he and index > 0:
            previous_vowel = _hebrew_vowel_mark(clusters[index - 1][1])
            if base not in HEBREW_DAGESH_TRANSLITERATION or previous_vowel not in {
                "",
                "\u05B0",
            }:
                consonant += consonant

        if vowel_mark == "\u05B0":
            vowel = "ə" if _is_vocal_shewa(clusters, index) else ""
        else:
            vowel = HEBREW_VOWEL_TRANSLITERATION.get(vowel_mark, "")
        if vowel_mark == "\u05B8":
            next_has_shewa = (
                index + 1 < len(clusters)
                and _hebrew_vowel_mark(clusters[index + 1][1]) == "\u05B0"
            )
            lexical_kol = normalize_hebrew(word) == "כל"
            lexical_qamets_hatuf = (
                index == 0
                and next_has_shewa
                and normalize_hebrew(word) in {"חכמה", "קרבן"}
            )
            if lexical_kol or lexical_qamets_hatuf:
                vowel = "o"

        if index + 1 < len(clusters) and _is_hebrew_mater(clusters, index + 1):
            next_base = clusters[index + 1][0]
            if next_base == "י":
                vowel = {"i": "î", "ē": "ê", "e": "ê"}.get(vowel, vowel)
            elif next_base == "ה":
                vowel = {"ā": "â", "ē": "ê", "e": "ê", "ō": "ô"}.get(
                    vowel, vowel
                )

        is_furtive_patah = (
            index == len(clusters) - 1
            and base in {"ח", "ע", "ה"}
            and vowel_mark == "\u05B7"
        )
        output.append((vowel + consonant) if is_furtive_patah else (consonant + vowel))
    return "".join(output)


def transliterate_bbh(text: str) -> str:
    parts = re.split(r"([\s\u05BE/,;()]+)", text)
    rendered: list[str] = []
    for part in parts:
        if not part:
            continue
        if HEBREW_CONSONANT.search(part):
            rendered.append(transliterate_bbh_word(part))
        else:
            rendered.append(part.replace("\u05BE", "-"))
    return "".join(rendered)


def infer_proper_name_types(gloss: str, *, explicit: bool = False) -> list[str]:
    if not explicit:
        return []
    lower = gloss.casefold()
    categories: list[str] = []

    def contains_any(terms: tuple[str, ...]) -> bool:
        return any(
            re.search(rf"(?<![a-z]){re.escape(term)}(?![a-z])", lower)
            for term in terms
        )

    if contains_any(("yahweh", "lord", "god", "deity", "divine title", "messiah")):
        categories.append("divine_name_or_title")
    if contains_any(
        (
            "city",
            "country",
            "territory",
            "river",
            "mountain",
            "region",
            "empire",
            "island",
            "province",
            "village",
            "place",
            "capital",
            "capitol",
            "jerusalem",
            "egypt",
            "babylon",
            "assyria",
            "canaan",
            "negev",
        )
    ):
        categories.append("place")
    if contains_any(
        (
            "tribe",
            "descendant",
            "people",
            "nation",
            "israelites",
            "gentile",
            "inhabitant",
        )
    ):
        categories.append("people_or_nation")
    if contains_any(
        (
            "son",
            "daughter",
            "brother",
            "father",
            "mother",
            "king",
            "leader",
            "patriarch",
            "prophet",
            "apostle",
            "israelite",
            "christian",
            "woman",
            "man",
            "moses",
            "pharaoh",
        )
    ):
        categories.append("person")
    if not categories:
        categories.append("proper_name")
    return list(dict.fromkeys(categories))


def gloss_has_named_usage(gloss: str) -> bool:
    excluded = {
        "Compare",
        "Feminine",
        "Masculine",
        "Plural",
        "Qal",
        "Hiphil",
        "Niphal",
        "Piel",
        "Pual",
        "Hithpael",
    }
    candidates = re.findall(
        r"(?:^|[,;])\s*(?:\([^)]*\)\s*)?([A-Z][a-z]{2,})\b", gloss
    )
    return any(candidate not in excluded for candidate in candidates)


def gloss_has_ethnic_or_geographic_name(gloss: str) -> bool:
    return bool(
        re.search(r"^\s*(?:a|an|the)\s+[A-Z][a-z]{2,}\b", gloss)
        or re.search(
            r"\b(?:inhabitant|descendant|tribe|territory|country|city|region|river|mountain)\s+of\s+[A-Z]",
            gloss,
        )
    )


def fully_pointed_hebrew(text: str) -> bool:
    words = re.split(r"[\s\u05BE/]+", text)
    hebrew_words = [word for word in words if HEBREW_CONSONANT.search(word)]
    if not hebrew_words:
        return False
    for word in hebrew_words:
        if normalize_hebrew(word) == "יהוה":
            continue
        clusters = _hebrew_clusters(word)
        if not clusters:
            return False
        for index, (base, marks) in enumerate(clusters):
            vowel = _hebrew_vowel_mark(marks)
            is_shureq = base == "ו" and "\u05BC" in marks and not vowel
            is_final = index == len(clusters) - 1
            previous_vowel = (
                _hebrew_vowel_mark(clusters[index - 1][1]) if index > 0 else ""
            )
            is_unpointed_aleph_after_vowel = (
                base == "א"
                and not vowel
                and previous_vowel in HEBREW_VOWEL_TRANSLITERATION
            )
            next_is_waw_vowel = (
                index + 1 < len(clusters)
                and clusters[index + 1][0] == "ו"
                and (
                    "\u05B9" in clusters[index + 1][1]
                    or "\u05BA" in clusters[index + 1][1]
                    or (
                        "\u05BC" in clusters[index + 1][1]
                        and not _hebrew_vowel_mark(clusters[index + 1][1])
                    )
                )
            )
            if (
                vowel
                or is_shureq
                or is_final
                or next_is_waw_vowel
                or is_unpointed_aleph_after_vowel
                or _is_hebrew_mater(clusters, index)
            ):
                continue
            # Internal consonants without a vowel or silent-shewa mark expose
            # partially pointed input (e.g. דָבר or שָלם).
            return False
    return True


def morphology_label(code: str) -> str:
    code = code.removeprefix("H")
    if code.startswith("Np"):
        return "proper_name"
    return {
        "N": "noun",
        "V": "verb",
        "A": "adjective",
        "P": "pronoun",
        "R": "preposition",
        "C": "conjunction",
        "D": "adverb",
        "T": "particle",
    }.get(code[:1], "other")


def count_morphhb_lemmas() -> tuple[
    Counter[str],
    dict[str, Counter[str]],
    dict[str, Counter[str]],
    dict[str, Counter[str]],
]:
    counts: Counter[str] = Counter()
    morphs: dict[str, Counter[str]] = defaultdict(Counter)
    surface_vocalized: dict[str, Counter[str]] = defaultdict(Counter)
    surface_unpointed: dict[str, Counter[str]] = defaultdict(Counter)
    for xml_path in sorted(MORPHHB_DIR.glob("*.xml")):
        for _event, elem in ElementTree.iterparse(xml_path, events=("end",)):
            if not elem.tag.endswith("w"):
                continue
            morph = elem.attrib.get("morph", "")
            if not morph.startswith("H"):
                elem.clear()
                continue
            lemma_parts = elem.attrib.get("lemma", "").split("/")
            morph_parts = morph.split("/")
            lexical_index = next(
                (
                    index
                    for index, part in enumerate(lemma_parts)
                    if STRONG_NUMBER.search(part)
                    and int(STRONG_NUMBER.search(part).group()) > 0
                ),
                None,
            )
            if lexical_index is None:
                elem.clear()
                continue
            strong = str(
                int(STRONG_NUMBER.search(lemma_parts[lexical_index]).group())
            )
            main_morph = (
                morph_parts[lexical_index]
                if lexical_index < len(morph_parts)
                else morph_parts[-1]
            )
            counts[strong] += 1
            morphs[strong][main_morph] += 1
            surface = (elem.text or "").strip()
            if surface:
                surface_vocalized[vocalized_hebrew_key(surface)][strong] += 1
                surface_unpointed[normalize_hebrew(surface)][strong] += 1
            elem.clear()
    return counts, morphs, surface_vocalized, surface_unpointed


def build_hebrew_vocabulary() -> list[dict[str, Any]]:
    payload = json.loads(BBH_VALUES.read_text(encoding="utf-8"))
    rows = payload["values"]
    headers = [str(value).strip() for value in rows[0]]
    column = {name: index for index, name in enumerate(headers)}

    counts, morphs, surface_vocalized, surface_unpointed = count_morphhb_lemmas()
    dictionary = load_js_dictionary(STRONGS_HEBREW)
    by_vocalized: dict[str, list[tuple[str, dict[str, str]]]] = defaultdict(list)
    by_unpointed: dict[str, list[tuple[str, dict[str, str]]]] = defaultdict(list)
    for strong_key, entry in dictionary.items():
        pointed_lemma = entry.get("lemma", "")
        if not pointed_lemma:
            continue
        by_vocalized[vocalized_hebrew_key(pointed_lemma)].append((strong_key, entry))
        by_unpointed[normalize_hebrew(pointed_lemma)].append((strong_key, entry))

    # BBH deliberately revisits seven identical pointed forms as distinct
    # lexemes/parts of speech. Their source-order slots are the stable way to
    # disambiguate them; frequency cannot decide between homographs.
    bbh_strong_by_source_order = {
        11: "H3389",  # Jerusalem, defective spelling/qere
        12: "H3389",  # Jerusalem, full spelling
        81: "H413",  # אֶל/אֶל־ to, toward
        94: "H4480",  # מִן / מִן־ from
        95: "H4605",  # מַעַל above, not H4604 treachery
        98: "H4687",  # plural of מִצְוָה
        109: "H2205",  # זָקֵן adjective/noun
        111: "H2896",  # טוֹב adjective
        130: "H7892",  # שִׁיר noun
        165: "H2004",  # הֵן pronoun
        178: "H2005",  # הֵן particle
        173: "H639",  # אַף nose/anger
        229: "H4193",  # מוֹת construct noun, death of
        283: "H2204",  # זָקֵן verb
        286: "H3513",  # כָּבֵד to be heavy/honored
        301: "H4191",  # מוּת to die
        325: "H637",  # אַף also/even
        344: "H1197",  # בָּעַר to burn
        360: "H2895",  # טוֹב verb
        362: "H7462",  # רָעָה to shepherd
        375: "H7999",  # שָׁלֵם to be complete
        400: "H2076",  # זָבַח to sacrifice
        317: "H6030",  # עָנָה answer
        384: "H2930",  # טָמֵא verb
        460: "H7843",  # שָׁחַת to ruin/destroy
        487: "H7891",  # שִׁיר verb
        496: "H6031",  # עָנָה afflict
        536: "H7650",  # שָׁבַע to swear
        538: "H1847",  # דַּעַת knowledge
        547: "H2931",  # טָמֵא adjective
    }
    bbh_pos_by_source_order = {
        58: "conjunction",
        80: "particle_or_preposition",
        81: "preposition",
        84: "preposition",
        88: "preposition",
        92: "preposition",
        94: "preposition",
        95: "adverb",
        101: "prepositional_phrase",
        109: "adjective",
        111: "adjective",
        116: "adverbial_phrase",
        130: "noun",
        141: "interrogative_particle",
        144: "conjunction_phrase",
        165: "pronoun",
        178: "particle",
        173: "noun",
        229: "noun",
        283: "verb",
        286: "verb",
        301: "verb",
        325: "particle",
        344: "verb",
        360: "verb",
        362: "verb",
        375: "verb",
        389: "verb",
        400: "verb",
        317: "verb",
        384: "verb",
        460: "verb",
        487: "verb",
        496: "verb",
        536: "verb",
        538: "noun",
        547: "adjective",
    }
    bbh_analysis_by_source_order = {
        80: ["H853", "H854"],  # object marker / with
        101: ["H5921", "H1697"],  # on account of + matter
        116: ["H5921", "H3651"],  # therefore: upon + so
        144: ["H3588", "H518"],  # but/except: for + if
        229: ["H4193", "H4194"],  # construct form / canonical death lexeme
    }
    bbh_frequency_strong_by_source_order = {
        # MorphHB indexes the construct form מוֹת under the canonical noun
        # H4194; Strong's also exposes exact-form H4193 without corpus counts.
        229: "H4194",
    }
    # A dictionary gloss often says "the name of N Israelites" or mentions a
    # territory incidentally.  That prose is not a reliable name-type parser,
    # so the confirmed people/place/nation distinctions are pinned here.
    hebrew_proper_name_types_by_strong: dict[str, list[str]] = {
        "H40": ["person"],
        "H85": ["person"],
        "H87": ["person"],
        "H223": ["person"],
        "H256": ["person"],
        "H452": ["person"],
        "H499": ["person"],
        "H558": ["person"],
        "H567": ["people_or_nation"],
        "H623": ["person", "people_or_nation"],
        "H635": ["person"],
        "H758": ["person", "place", "people_or_nation"],
        "H804": ["person", "place", "people_or_nation"],
        "H842": ["divine_name_or_title"],
        "H1130": ["person"],
        "H1141": ["person"],
        "H1390": ["place"],
        "H1537": ["place"],
        "H1568": ["person", "place"],
        "H1835": ["person", "place", "people_or_nation"],
        "H2001": ["person"],
        "H2148": ["person"],
        "H2275": ["person", "place"],
        "H2396": ["person"],
        "H2977": ["person"],
        "H3050": ["divine_name_or_title"],
        "H3058": ["person"],
        "H3063": ["person", "place", "people_or_nation"],
        "H3069": ["divine_name_or_title"],
        "H3077": ["person"],
        "H3083": ["person"],
        "H3092": ["person", "place"],
        "H3097": ["person"],
        "H3101": ["person"],
        "H3129": ["person"],
        "H3130": ["person"],
        "H3290": ["person"],
        "H3414": ["person"],
        "H3458": ["person"],
        "H3470": ["person"],
        "H3478": ["person", "people_or_nation"],
        "H3837": ["person", "place"],
        "H4080": ["person", "place", "people_or_nation"],
        "H4124": ["person", "place", "people_or_nation"],
        "H4519": ["person", "place", "people_or_nation"],
        "H5019": ["person"],
        "H5416": ["person"],
        "H5654": ["person"],
        "H5838": ["person"],
        "H5983": ["person", "place", "people_or_nation"],
        "H6002": ["person", "place", "people_or_nation"],
        "H6215": ["person", "people_or_nation"],
        "H6659": ["person"],
        "H6667": ["person"],
        "H7354": ["person"],
        "H7585": ["place"],
        "H7586": ["person"],
        "H7676": ["festival_or_sacred_time"],
        "H7706": ["divine_name_or_title"],
        "H8010": ["person"],
        "H8050": ["person"],
        "H8095": ["person", "people_or_nation"],
        "H8096": ["person"],
        "H8098": ["person"],
        "H8165": ["place", "people_or_nation"],
    }

    def gloss_tokens(text: str) -> set[str]:
        stop = {
            "and",
            "the",
            "with",
            "from",
            "into",
            "that",
            "this",
            "one",
            "all",
            "for",
            "being",
            "become",
        }
        tokens = set()
        for token in re.findall(r"[A-Za-z]+", text.casefold()):
            if len(token) < 3 or token in stop:
                continue
            if token.endswith("ies") and len(token) > 4:
                token = token[:-3] + "y"
            elif token.endswith("s") and len(token) > 3:
                token = token[:-1]
            tokens.add(token)
        return tokens

    def best_match(pointed: str, gloss: str) -> tuple[str, dict[str, str]] | None:
        evidence: dict[str, tuple[dict[str, str], int, int]] = {}

        def add_matches(
            matches: list[tuple[str, dict[str, str]]],
            evidence_weight: int,
            occurrence_count: int = 0,
        ) -> None:
            for strong_key, entry in matches:
                previous = evidence.get(strong_key)
                candidate = (entry, evidence_weight, occurrence_count)
                if previous is None or candidate[1:] > previous[1:]:
                    evidence[strong_key] = candidate

        alternatives = [
            item.strip()
            for item in re.split(r"\s*/\s*", pointed)
            if HEBREW_CONSONANT.search(item)
        ] or [pointed]
        for alternative in alternatives:
            vocalized_key = vocalized_hebrew_key(alternative)
            unpointed_key = normalize_hebrew(alternative)
            add_matches(by_vocalized.get(vocalized_key, []), 4)
            add_matches(by_unpointed.get(unpointed_key, []), 2)

            vocalized_surface = surface_vocalized.get(vocalized_key, Counter())
            for strong, occurrence_count in vocalized_surface.items():
                strong_key = f"H{strong}"
                if strong_key in dictionary:
                    add_matches(
                        [(strong_key, dictionary[strong_key])],
                        6,
                        occurrence_count,
                    )
            unpointed_surface = surface_unpointed.get(unpointed_key, Counter())
            for strong, occurrence_count in unpointed_surface.items():
                strong_key = f"H{strong}"
                if strong_key in dictionary:
                    add_matches(
                        [(strong_key, dictionary[strong_key])],
                        3,
                        occurrence_count,
                    )

        matches = [
            (strong_key, entry, evidence_weight, occurrence_count)
            for strong_key, (entry, evidence_weight, occurrence_count) in evidence.items()
        ]
        if not matches:
            return None
        source_tokens = gloss_tokens(gloss)

        def score(
            item: tuple[str, dict[str, str], int, int]
        ) -> tuple[int, int, int, int]:
            strong_key, entry, evidence_weight, occurrence_count = item
            dictionary_text = " ".join(
                (
                    entry.get("strongs_def", ""),
                    entry.get("kjv_def", ""),
                )
            )
            overlap = len(source_tokens & gloss_tokens(dictionary_text))
            strong_number = str(int(STRONG_NUMBER.search(strong_key).group()))
            return (
                evidence_weight,
                overlap,
                occurrence_count,
                counts.get(strong_number, 0),
            )

        selected = max(matches, key=score)
        if score(selected)[1] == 0 and len(matches) > 1:
            ranked = sorted(matches, key=score, reverse=True)
            if (
                score(ranked[0])[0] == score(ranked[1])[0]
                and score(ranked[0])[2:] == score(ranked[1])[2:]
            ):
                return None
        if score(selected)[1] == 0 and score(selected)[0] < 4:
            return None
        return selected[0], selected[1]

    output: list[dict[str, Any]] = []
    seen_source_signatures: dict[tuple[str, str], int] = {}
    seen_strongs: set[str] = set()
    for row in rows[1:]:
        source_pointed = str(row[column["Hebrew"]] or "").strip()
        if not HEBREW_CONSONANT.search(source_pointed):
            continue
        if not fully_pointed_hebrew(source_pointed):
            raise ValueError(
                f"BBH source contains an unpointed Hebrew item: {source_pointed}"
            )
        pointed = unicodedata.normalize("NFC", source_pointed)
        unpointed_variants = normalize_hebrew_variants(pointed)
        normalized = unpointed_variants[0] if unpointed_variants else ""
        if not normalized:
            continue
        gloss = str(row[column["English"]] or "").strip()
        source_order = int(row[column["Order"]])
        source_signature = (vocalized_hebrew_key(pointed), gloss.casefold())
        if source_signature in seen_source_signatures:
            output[seen_source_signatures[source_signature]]["sourceOrders"].append(
                source_order
            )
            continue
        seen_source_signatures[source_signature] = len(output)

        match = best_match(pointed, gloss)
        analysis_strongs = list(bbh_analysis_by_source_order.get(source_order, []))
        override_strong = bbh_strong_by_source_order.get(source_order)
        if override_strong:
            match = (override_strong, dictionary[override_strong])
        strong_key, entry = match if match else ("", {})
        strong_number = (
            str(int(STRONG_NUMBER.search(strong_key).group())) if strong_key else ""
        )
        frequency_strong_key = bbh_frequency_strong_by_source_order.get(
            source_order, strong_key
        )
        frequency_strong_number = (
            str(int(STRONG_NUMBER.search(frequency_strong_key).group()))
            if frequency_strong_key
            else ""
        )
        if strong_key and strong_key not in analysis_strongs:
            analysis_strongs.insert(0, strong_key)
        dominant_morph = (
            morphs[strong_number].most_common(1)[0][0]
            if strong_number and morphs[strong_number]
            else ""
        )
        part_of_speech = morphology_label(dominant_morph) if dominant_morph else ""
        part_of_speech = bbh_pos_by_source_order.get(source_order, part_of_speech)
        # The BBH row's gloss is authoritative here. An inflected common form
        # can be identical to a Strong's proper-name lemma (e.g. "eyes"), so
        # morphology alone must not relabel the textbook entry as a name.
        explicit_name_types = hebrew_proper_name_types_by_strong.get(strong_key)
        proper_name_usage = bool(explicit_name_types) or gloss_has_named_usage(gloss)
        proper_name_types = explicit_name_types or (
            infer_proper_name_types(gloss, explicit=True)
            if proper_name_usage
            else []
        )
        output.append(
            {
                "ordinal": len(output) + 1,
                "pointed": pointed,
                "sourcePointed": source_pointed,
                "unpointed": normalized,
                "unpointedVariants": unpointed_variants,
                "textbookTransliteration": transliterate_bbh(pointed),
                "transliterationSystem": "Pratico-Van Pelt BBH2",
                "transliterationStatus": "rule_generated_exception_review",
                "glossEn": gloss,
                "glossZh": "",
                "sourceType": "bbh2_order",
                "sourceChapter": int(row[column["Chapter"]]),
                "sourceOrder": source_order,
                "sourceOrders": [source_order],
                "itemKind": (
                    "bound_morpheme"
                    if source_order in {58, 84, 88, 92, 141}
                    else "multi_lexeme_phrase"
                    if source_order in {101, 116, 144}
                    else "lexeme"
                ),
                "frequency": (
                    counts.get(frequency_strong_number)
                    if frequency_strong_number
                    else None
                ),
                "frequencyStrong": frequency_strong_key,
                "strong": strong_key,
                "strongs": analysis_strongs,
                "partOfSpeech": part_of_speech,
                "isProperName": proper_name_usage,
                "properNameTypes": proper_name_types,
                "verification": (
                    "source_and_lexicon_matched" if match else "source_verified"
                ),
                "languageVariety": "biblical_hebrew",
            }
        )
        seen_strongs.update(analysis_strongs)

    candidates: list[dict[str, Any]] = []
    for strong, frequency in counts.most_common():
        strong_key = f"H{int(strong)}"
        entry = dictionary.get(strong_key)
        if not entry:
            continue
        pointed = unicodedata.normalize("NFC", entry.get("lemma", "").strip())
        normalized = normalize_hebrew(pointed)
        if (
            not normalized
            or strong_key in seen_strongs
            or not fully_pointed_hebrew(pointed)
        ):
            continue
        dominant_morph = morphs[strong].most_common(1)[0][0] if morphs[strong] else ""
        part_of_speech = morphology_label(dominant_morph)
        gloss = entry.get("strongs_def", "").strip()
        explicit_name_types = hebrew_proper_name_types_by_strong.get(strong_key)
        proper_name_usage = bool(explicit_name_types) or (
            part_of_speech == "proper_name"
            or gloss_has_named_usage(gloss)
            or gloss_has_ethnic_or_geographic_name(gloss)
        )
        candidates.append(
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
                "properNameTypes": (
                    explicit_name_types
                    or infer_proper_name_types(gloss, explicit=True)
                    if proper_name_usage
                    else []
                ),
                "verification": "lemma_frequency_verified",
                "languageVariety": (
                    "biblical_aramaic"
                    if "(Aramaic)" in entry.get("derivation", "")
                    else "biblical_hebrew"
                ),
            }
        )
        seen_strongs.add(strong_key)
        if len(output) + len(candidates) >= 1000:
            break

    output.extend(candidates)
    if len(output) != 1000:
        raise ValueError(f"Expected 1000 Hebrew items, found {len(output)}")

    for index, item in enumerate(output, 1):
        item["ordinal"] = index

    # Lesson size follows the textbook's own chapters rather than a fixed
    # quota; see scripts/assign_hebrew_lessons.py for the rule.
    from assign_hebrew_lessons import assign

    return assign(output)


def normalize_greek(text: str) -> str:
    text = text.replace("µ", "μ").replace("ϛ", "στ")
    text = unicodedata.normalize("NFD", text).casefold()
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^\u0370-\u03FF\u1F00-\u1FFF]", "", text)


def _greek_clusters(text: str) -> list[tuple[str, set[str], bool]]:
    clusters: list[tuple[str, set[str], bool]] = []
    base = ""
    marks: set[str] = set()
    uppercase = False
    for char in unicodedata.normalize("NFD", text.replace("µ", "μ")):
        folded = char.casefold()
        if folded in GREEK_TRANSLITERATION:
            if base:
                clusters.append((base, marks, uppercase))
            base = folded
            marks = set()
            uppercase = unicodedata.category(char) == "Lu"
        elif base and unicodedata.category(char) == "Mn":
            marks.add(char)
    if base:
        clusters.append((base, marks, uppercase))
    return clusters


def transliterate_mounce(text: str) -> str:
    """Mounce's standard/Erasmian Latin-letter reading form."""
    clusters = _greek_clusters(text)
    if not clusters:
        return text
    initial_rough = False
    for index, (base, marks, _uppercase) in enumerate(clusters[:2]):
        if "\u0314" in marks and base in {"α", "ε", "η", "ι", "ο", "υ", "ω"}:
            initial_rough = True
            break
        if base not in {"α", "ε", "η", "ι", "ο", "υ", "ω"}:
            break
        if index == 1:
            break

    output: list[str] = []
    for index, (base, marks, _uppercase) in enumerate(clusters):
        if base == "γ" and index + 1 < len(clusters):
            next_base = clusters[index + 1][0]
            rendered = "n" if next_base in {"γ", "κ", "χ", "ξ"} else "g"
        elif base == "ρ" and "\u0314" in marks:
            rendered = "rh"
        else:
            rendered = GREEK_TRANSLITERATION[base]
        if "\u0345" in marks:
            rendered += "i"
        output.append(rendered)
    result = ("h" if initial_rough else "") + "".join(output)
    if clusters[0][2] and result:
        result = result[0].upper() + result[1:]
    return result


def is_greek_proper_name(text: str) -> bool:
    for char in unicodedata.normalize("NFD", text):
        if char.casefold() in GREEK_TRANSLITERATION:
            return unicodedata.category(char) == "Lu"
    return False


def extract_mounce_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with pdfplumber.open(MOUNCE_PDF) as pdf:
        for page_number, page in enumerate(pdf.pages, 1):
            words = page.extract_words(
                x_tolerance=1,
                y_tolerance=2,
                keep_blank_chars=False,
                use_text_flow=False,
            )
            for sequence_band, chapter_band, word_band in (
                ((65, 112), (112, 160), (160, 300)),
                ((300, 365), (365, 405), (405, 555)),
            ):
                sequence_words = [
                    word
                    for word in words
                    if sequence_band[0] <= word["x0"] < sequence_band[1]
                    and word["text"].isdigit()
                    and word["top"] > 75
                ]
                for sequence_word in sequence_words:
                    top = sequence_word["top"]
                    # One long entry (no. 763) wraps around its sequence number;
                    # a seven-point band captures both halves without reaching
                    # the neighbouring 21-point rows.
                    line = [word for word in words if abs(word["top"] - top) <= 7.0]
                    chapter = next(
                        (
                            word["text"]
                            for word in line
                            if chapter_band[0] <= word["x0"] < chapter_band[1]
                            and word["text"].isdigit()
                        ),
                        "",
                    )
                    lexical = " ".join(
                        word["text"]
                        for word in sorted(line, key=lambda item: item["x0"])
                        if word_band[0] <= word["x0"] < word_band[1]
                    )
                    lexical = unicodedata.normalize("NFC", lexical.replace("µ", "μ")).strip()
                    if lexical:
                        rows.append(
                            {
                                "ordinal": int(sequence_word["text"]),
                                "bbgChapter": int(chapter) if chapter else None,
                                "printedEntry": lexical,
                                "sourcePage": page_number,
                            }
                        )
    rows.sort(key=lambda item: item["ordinal"])
    ordinals = [item["ordinal"] for item in rows]
    if ordinals != list(range(1, 1001)):
        missing = sorted(set(range(1, 1001)) - set(ordinals))
        duplicate = sorted(number for number, count in Counter(ordinals).items() if count > 1)
        raise ValueError(
            f"Mounce extraction is not contiguous: rows={len(rows)}, missing={missing[:20]}, duplicate={duplicate[:20]}"
        )
    return rows


def build_greek_vocabulary() -> list[dict[str, Any]]:
    dictionary = load_js_dictionary(STRONGS_GREEK)
    by_lemma: dict[str, list[tuple[str, dict[str, str]]]] = defaultdict(list)
    for strong, entry in dictionary.items():
        normalized = normalize_greek(entry.get("lemma", ""))
        if normalized:
            by_lemma[normalized].append((strong, entry))

    # The Strong's file contains accent/case-colliding lemmas.  Mounce's
    # printed accents, breathing marks, inflectional hints, and capitalization
    # disambiguate these entries; dictionary insertion order does not.
    mounce_strong_by_ordinal = {
        44: "G1519",   # εἰς, into/to (not εἷς, one)
        93: "G1487",   # εἰ, if (not εἶ, you are)
        95: "G1520",   # εἷς, one
        105: "G5101",  # τίς, who/what
        106: "G5100",  # τις, someone/something
        148: "G2228",  # ἤ, or/than
        154: "G4459",  # πῶς, how
        212: "G2590",  # καρπός, fruit (not Κάρπος, Carpus)
        284: "G3757",  # οὗ, where
        341: "G686",   # ἄρα, therefore/then
        349: "G4226",  # ποῦ, where
        489: "G4218",  # ποτέ, once/ever
        666: "G4219",  # πότε, when
        689: "G3376",  # μήν, μηνός, ὁ, month
        698: "G4735",  # στέφανος, crown (not Στέφανος, Stephen)
        732: "G5599",  # ὦ, O!
        811: "G4458",  # πώς, somehow
        839: "G1623",  # ἕκτος, sixth
    }

    # Proper-name types are pedagogical metadata, not a word search over a
    # dictionary definition.  For example, "the name of four Israelites"
    # describes John as a person; it does not turn Ἰωάννης into a nation name.
    mounce_proper_name_types_by_ordinal: dict[int, list[str]] = {
        5: ["place"],
        20: ["divine_name_or_title"],
        21: ["person"],
        22: ["person"],
        23: ["person"],
        24: ["person"],
        25: ["person"],
        26: ["person"],
        47: ["person", "divine_name_or_title"],
        65: ["person"],
        162: ["place"],
        209: ["place"],
        210: ["people_or_nation"],
        211: ["person", "people_or_nation"],
        239: ["people_or_nation"],
        281: ["place"],
        313: ["person"],
        364: ["person", "place", "people_or_nation"],
        370: ["person"],
        377: ["person"],
        428: ["person"],
        430: ["person"],
        480: ["person"],
        482: ["person"],
        496: ["person"],
        512: ["person"],
        517: ["person"],
        518: ["person"],
        538: ["place"],
        544: ["people_or_nation"],
        570: ["person"],
        597: ["person"],
        603: ["place"],
        636: ["person"],
        670: ["place"],
        674: ["place"],
        713: ["place"],
        751: ["place"],
        755: ["place"],
        781: ["place"],
        792: ["place"],
        796: ["person"],
        814: ["person"],
        864: ["people_or_nation"],
        875: ["person"],
        896: ["person"],
        897: ["people_or_nation"],
        906: ["person"],
        910: ["person"],
        918: ["place"],
        921: ["place"],
        934: ["person"],
        943: ["people_or_nation"],
        963: ["people_or_nation"],
        965: ["person"],
        966: ["person"],
    }

    output: list[dict[str, Any]] = []
    for row in extract_mounce_rows():
        printed = row["printedEntry"]
        headword = printed.split(",", 1)[0].strip()
        match_key = normalize_greek(headword)
        matches = by_lemma.get(match_key, [])
        override_strong = mounce_strong_by_ordinal.get(row["ordinal"])
        if override_strong:
            strong, entry = override_strong, dictionary[override_strong]
        else:
            strong, entry = matches[0] if matches else ("", {})
        gloss = entry.get("strongs_def", "").strip()
        explicit_name_types = mounce_proper_name_types_by_ordinal.get(
            row["ordinal"]
        )
        proper_name_usage = bool(explicit_name_types) or is_greek_proper_name(
            headword
        )
        output.append(
            {
                **row,
                "productionGroup": (row["ordinal"] - 1) // 50 + 1,
                "groupSlot": (row["ordinal"] - 1) % 50 + 1,
                "headword": headword,
                "lemma": entry.get("lemma", headword),
                "textbookTransliteration": transliterate_mounce(headword),
                "transliterationSystem": "Mounce standard Erasmian",
                "transliterationStatus": "rule_generated_from_official_table",
                "glossEn": gloss,
                "glossZh": "",
                "strong": strong,
                "isProperName": proper_name_usage,
                "properNameTypes": (
                    explicit_name_types
                    or infer_proper_name_types(gloss, explicit=True)
                    if proper_name_usage
                    else []
                ),
                "verification": "source_and_lexicon_matched" if entry else "source_verified_lexicon_pending",
            }
        )
    return output


def main() -> None:
    hebrew_transliteration_examples = {
        "סוּס": "sûs",
        "תּוֹרָה": "tôrâ",
        "הַתּוֹרָה": "hattôrâ",
        "רוּחַ": "rûaḥ",
        "חָכְמָה": "ḥoḵmâ",
        "קָרְבָּן": "qorbān",
        "כָּל": "kol",
        "יְהוָה": "yhwh",
        "יְרוּשָׁלַםִ": "yərûšālayim",
        "רֹאשׁ": "rōʾš",
        "צֹאן": "ṣōʾn",
        "לֹא": "lōʾ",
        "בּוֹא": "bôʾ",
        "מָצָא": "māṣāʾ",
        "קָרָא": "qārāʾ",
        "טָמֵא": "ṭāmēʾ",
        "בָּרָא": "bārāʾ",
    }
    greek_transliteration_examples = {
        "ἄγγελος": "angelos",
        "ἀπόστολος": "apostolos",
        "ὑπέρ": "huper",
        "Ἰησοῦς": "Iēsous",
    }
    for source, expected in hebrew_transliteration_examples.items():
        actual = transliterate_bbh(source)
        if actual != expected:
            raise ValueError(
                f"BBH transliteration regression for {source}: {actual} != {expected}"
            )
    for source, expected in greek_transliteration_examples.items():
        actual = transliterate_mounce(source)
        if actual != expected:
            raise ValueError(
                f"Mounce transliteration regression for {source}: {actual} != {expected}"
            )
    for source in ("דָּבָר", "שָׁלֵם", "סוּס", "יְהוָה", "יְרוּשָׁלַיִם"):
        if not fully_pointed_hebrew(source):
            raise ValueError(f"Fully pointed Hebrew rejected: {source}")
    for source in ("דָבר", "שָלם"):
        if fully_pointed_hebrew(source):
            raise ValueError(f"Partially pointed Hebrew accepted: {source}")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    hebrew = build_hebrew_vocabulary()
    greek = build_greek_vocabulary()
    (DATA_DIR / "hebrew-1000.json").write_text(
        json.dumps(hebrew, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (DATA_DIR / "greek-1000.json").write_text(
        json.dumps(greek, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "hebrew": {
                    "count": len(hebrew),
                    "bbh": sum(item["sourceType"] == "bbh2_order" for item in hebrew),
                    "extension": sum(
                        item["sourceType"] == "reader_frequency_extension" for item in hebrew
                    ),
                    "properNames": sum(item["isProperName"] for item in hebrew),
                },
                "greek": {
                    "count": len(greek),
                    "properNames": sum(item["isProperName"] for item in greek),
                    "matched": sum(
                        item["verification"] == "source_and_lexicon_matched" for item in greek
                    ),
                    "pending": sum(
                        item["verification"] != "source_and_lexicon_matched" for item in greek
                    ),
                },
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
