"""Shared lookups for the Hebrew reader's appendix tables.

Everything here reads a frozen local source: Strong's Hebrew dictionary for the
citation form, the Westminster Leningrad Codex for attestation and frequency,
and the reader's own BBH2 transliteration rules.  Nothing is generated from a
model, so an entry that cannot be verified fails loudly instead of shipping.
"""

from __future__ import annotations

import re
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STRONGS = ROOT / "output/source-cache/original-readers/strongs-src/strongs-master/hebrew/StrongHebrewG.xml"
WLC_DIR = ROOT / "output/source-cache/original-readers/morphhb-src/morphhb-master/wlc"
OSIS = "{http://www.bibletechnologies.net/2003/OSIS/namespace}"

# WLC books in Tanakh order, so "first occurrence" means the first one a reader
# meets, not the first filename alphabetically.
WLC_ORDER = [
    "Gen", "Exod", "Lev", "Num", "Deut",
    "Josh", "Judg", "1Sam", "2Sam", "1Kgs", "2Kgs",
    "Isa", "Jer", "Ezek",
    "Hos", "Joel", "Amos", "Obad", "Jonah", "Mic", "Nah", "Hab", "Zeph", "Hag", "Zech", "Mal",
    "Ps", "Prov", "Job", "Song", "Ruth", "Lam", "Eccl", "Esth", "Dan", "Ezra", "Neh", "1Chr", "2Chr",
]

BOOK_ZH = {
    "Gen": "創世記", "Exod": "出埃及記", "Lev": "利未記", "Num": "民數記", "Deut": "申命記",
    "Josh": "約書亞記", "Judg": "士師記", "1Sam": "撒母耳記上", "2Sam": "撒母耳記下",
    "1Kgs": "列王紀上", "2Kgs": "列王紀下", "Isa": "以賽亞書", "Jer": "耶利米書",
    "Ezek": "以西結書", "Hos": "何西阿書", "Joel": "約珥書", "Amos": "阿摩司書",
    "Obad": "俄巴底亞書", "Jonah": "約拿書", "Mic": "彌迦書", "Nah": "那鴻書",
    "Hab": "哈巴谷書", "Zeph": "西番雅書", "Hag": "哈該書", "Zech": "撒迦利亞書",
    "Mal": "瑪拉基書", "Ps": "詩篇", "Prov": "箴言", "Job": "約伯記", "Song": "雅歌",
    "Ruth": "路得記", "Lam": "耶利米哀歌", "Eccl": "傳道書", "Esth": "以斯帖記",
    "Dan": "但以理書", "Ezra": "以斯拉記", "Neh": "尼希米記",
    "1Chr": "歷代志上", "2Chr": "歷代志下",
}


@lru_cache(maxsize=1)
def strongs_index() -> dict[str, dict]:
    """Map ``H<n>`` to the dictionary's citation form, xlit and definitions."""

    index: dict[str, dict] = {}
    for _, element in ET.iterparse(STRONGS, events=("end",)):
        if element.tag != f"{OSIS}div" or element.get("type") != "entry":
            continue
        head = element.find(f"{OSIS}w")
        if head is None or not head.get("ID"):
            continue
        senses = [item.text or "" for item in element.iterfind(f"{OSIS}list/{OSIS}item")]
        explanation = element.find(f'{OSIS}note[@type="explanation"]')
        index[head.get("ID")] = {
            "strong": head.get("ID"),
            "lemma": head.get("lemma") or "",
            "xlit": head.get("xlit") or "",
            "morph": head.get("morph") or "",
            "senses": senses,
            "explanation": "".join(explanation.itertext()).strip() if explanation is not None else "",
        }
        element.clear()
    return index


def _lemma_strongs(value: str) -> list[str]:
    """Split a WLC ``lemma`` attribute into the Strong numbers it carries.

    WLC writes prefixes as ``b/7225`` and homograph suffixes as ``1254 a``; both
    are stripped so a plain ``H7225`` lookup matches.
    """

    out = []
    for part in value.split("/"):
        digits = re.match(r"\s*(\d+)", part)
        if digits:
            out.append("H" + str(int(digits.group(1))))
    return out


@lru_cache(maxsize=1)
def wlc_occurrences() -> tuple[Counter, dict[str, tuple[str, int, int]]]:
    """Return (frequency per Strong number, first Tanakh-order occurrence)."""

    counts: Counter = Counter()
    first: dict[str, tuple[str, int, int]] = {}
    for book in WLC_ORDER:
        path = WLC_DIR / f"{book}.xml"
        for _, verse in ET.iterparse(path, events=("end",)):
            if verse.tag != f"{OSIS}verse":
                continue
            osis_id = verse.get("osisID") or ""
            parts = osis_id.split(".")
            if len(parts) != 3:
                verse.clear()
                continue
            chapter, number = int(parts[1]), int(parts[2])
            for word in verse.iterfind(f"{OSIS}w"):
                for strong in _lemma_strongs(word.get("lemma") or ""):
                    counts[strong] += 1
                    first.setdefault(strong, (book, chapter, number))
            verse.clear()
    return counts, first


def reference_zh(place: tuple[str, int, int] | None) -> str:
    if not place:
        return ""
    book, chapter, verse = place
    return f"{BOOK_ZH.get(book, book)} {chapter}:{verse}"


CANTILLATION_RE = re.compile(r"[֑-ֽֿ֯׀׃׆]")
NIQQUD_RE = re.compile(r"[ְ-ׇּׁׂ]")
MAQAF = "־"
DAGESH = "ּ"


def strip_cantillation(text: str) -> str:
    """Drop cantillation and maqqef, then put the remaining marks in canonical order.

    The WLC writes the shin dot before the vowel under the same letter, which is
    the opposite of Unicode's canonical ordering; without NFC a hand-typed form
    never matches the corpus spelling even when they are the same word.
    """

    return unicodedata.normalize("NFC", CANTILLATION_RE.sub("", text).replace(MAQAF, ""))


def consonants(text: str) -> str:
    return NIQQUD_RE.sub("", strip_cantillation(text))



def _first_cluster_marks(text: str) -> str:
    """Return the combining marks attached to a word's first consonant."""

    marks = []
    for index, character in enumerate(unicodedata.normalize("NFC", text)):
        if index == 0:
            continue
        if unicodedata.category(character) == "Mn":
            marks.append(character)
        else:
            break
    return "".join(marks)


def _drop_first_dagesh(text: str) -> str:
    """Remove a dagesh on the first consonant, keeping every other mark."""

    normalized = unicodedata.normalize("NFC", text)
    out = []
    removed = False
    for index, character in enumerate(normalized):
        if index and not removed and character == DAGESH and unicodedata.category(character) == "Mn":
            removed = True
            continue
        if index and unicodedata.category(character) != "Mn":
            out.append(normalized[index:])
            break
        out.append(character)
    return "".join(out)


@lru_cache(maxsize=1)
def wlc_surface_forms() -> dict[str, Counter]:
    """Attested WLC spellings per Strong number, cantillation removed.

    Only whole words are collected: a WLC token whose ``lemma`` carries a
    prefix (``d/8064``) is skipped, so the result holds the word as it stands
    on its own rather than with an article or conjunction fused to it.
    """

    standalone: dict[str, Counter] = {}
    prefixed: dict[str, Counter] = {}
    for book in WLC_ORDER:
        for _, word in ET.iterparse(WLC_DIR / f"{book}.xml", events=("end",)):
            if word.tag != f"{OSIS}w":
                continue
            lemma = (word.get("lemma") or "").strip()
            text = (word.text or "").strip()
            if not text:
                word.clear()
                continue
            # WLC segments a prefixed word in both fields: lemma "b/435" against
            # text "בְּ/אֱלוּל".  Words such as the month names or חָמוֹת almost
            # never stand unprefixed, so taking only bare tokens would leave them
            # with no attested spelling at all.  The base word is the last
            # segment; prefixes are always written before it.
            lemma_parts = lemma.split("/")
            text_parts = text.split("/")
            if len(lemma_parts) == len(text_parts):
                base = _lemma_strongs(lemma_parts[-1])
                if len(base) == 1:
                    tier = standalone if len(text_parts) == 1 else prefixed
                    tier.setdefault(base[0], Counter())[strip_cantillation(text_parts[-1])] += 1
            word.clear()
    # Some words never stand alone in the corpus: the ordinals 七/八/九 and the
    # month names only ever follow the article.  Those occurrences are still the
    # word's biblical spelling, except that the article doubles the first
    # consonant — הַשְּׁבִיעִי carries a dagesh that שְׁבִיעִי does not.  Drop that
    # one dagesh, and only when the dictionary's citation form lacks it, so a
    # root dagesh is never removed.
    for strong, counts in prefixed.items():
        if strong in standalone:
            continue
        lemma = strongs_index().get(strong, {}).get("lemma", "")
        if DAGESH in _first_cluster_marks(lemma):
            standalone[strong] = counts
            continue
        cleaned: Counter = Counter()
        for form, count in counts.items():
            cleaned[strip_cantillation(_drop_first_dagesh(form))] += count
        standalone[strong] = cleaned
    return standalone


def attested_form(strong: str, skeleton: str) -> tuple[str, int]:
    """Return the commonest WLC spelling of ``strong`` whose consonants match.

    ``skeleton`` is the unpointed spelling being asked for, which is how the
    two genders of a Hebrew numeral are told apart without hand-typing niqqud.
    """

    forms = wlc_surface_forms().get(strong, Counter())
    matches = [(count, form) for form, count in forms.items() if consonants(form) == skeleton]
    if not matches:
        return "", 0
    count, form = max(matches)
    return form, count
