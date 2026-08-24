#!/usr/bin/env python3
"""下冊教規彙編與禮儀頌歌的讀取層。

來源由 ``fetch_greek_church_documents.py`` 凍結在
``sources/church-documents/*.wiki``（希臘文維基文庫的原始 wikitext）。這裡只負責
把 wikitext 還原成可印的希臘文段落，不上網、不改字。

兩種版式，分開處理而不是靠猜：

* **教規** —— ``==Κανὼν Α'==`` 之類的標題把全文切成一條一條，標題本身是希臘數字，
  轉成阿拉伯數字當作段落編號，所以「第 47 條」在讀本裡永遠指得回原文的第 47 條。
* **頌歌** —— 沒有條號，只有 ``:`` 起首的詩行或 ``<poem>`` 區塊；逐行編號。

wikitext 的清理一律走同一條路徑：模板、註解、參考、標記全部拿掉，內部連結只留
顯示文字。留下的必須是希臘文，否則寧可整行丟掉也不印進讀本。
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
CHURCH_DIR = CACHE / "sources" / "church-documents"

GREEK_RE = re.compile(r"[Ͱ-Ͽἀ-῿]")

WIKISOURCE_EDITION = "Ἑλληνικὴ Βικιθήκη（希臘文維基文庫）錄入本"
WIKISOURCE_LICENSE = (
    "條文為古代教會文獻，已逾著作權期間；維基文庫錄入與編排採 CC BY-SA 4.0，"
    "私人授權使用並標明出處。"
)

# Greek alphabetic numerals, including the two-letter ΣΤ' that stands for six
# and the obsolete letters the system still uses for 6, 90 and 900.
_NUMERAL_VALUES = {
    "α": 1, "β": 2, "γ": 3, "δ": 4, "ε": 5, "ϛ": 6, "ζ": 7, "η": 8, "θ": 9,
    "ι": 10, "κ": 20, "λ": 30, "μ": 40, "ν": 50, "ξ": 60, "ο": 70, "π": 80, "ϟ": 90,
    "ρ": 100, "σ": 200, "τ": 300, "υ": 400, "φ": 500, "χ": 600, "ψ": 700, "ω": 800, "ϡ": 900,
}


def greek_numeral(text: str) -> int:
    """Read a Greek alphabetic numeral such as ``ΙΑ'`` or ``ΣΤ'`` as an integer."""
    cleaned = unicodedata.normalize("NFD", text.strip())
    cleaned = "".join(c for c in cleaned if not unicodedata.combining(c))
    cleaned = cleaned.replace("ʹ", "").replace("΄", "").replace("'", "").replace("’", "")
    cleaned = cleaned.strip().lower()
    if not cleaned:
        raise ValueError(f"空的希臘數字：{text!r}")
    # ΣΤ is six written with two letters; taken letter by letter it would come
    # out as 200 + 300, which is why it is matched before the loop.
    cleaned = cleaned.replace("στ", "ϛ")
    total = 0
    for character in cleaned:
        if character == "ς":
            character = "ϛ"
        value = _NUMERAL_VALUES.get(character)
        if value is None:
            raise ValueError(f"{text!r} 不是希臘數字（{character!r} 無對應值）")
        total += value
    return total


class Segment(NamedTuple):
    ref: str
    text: str


_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
_REF_RE = re.compile(r"<ref\b[^>]*>.*?</ref>|<ref\b[^>]*/>", re.S | re.I)
_TAG_RE = re.compile(r"<[^>]+>")
# A category or file link is metadata, not text.  Left to the ordinary link
# rule it becomes a printed line — "Κατηγορία:Θρησκευτικά κείμενα" turned up as
# the closing verse of the Great Doxology.
_META_LINK_RE = re.compile(
    r"\[\[\s*(?:Κατηγορία|Category|Αρχείο|Εικόνα|File|Image)\s*:[^\]]*\]\]", re.I
)
_LINK_RE = re.compile(r"\[\[(?:[^\]|]*\|)?([^\]|]*)\]\]")
_EXTLINK_RE = re.compile(r"\[(?:https?|//)\S+\s+([^\]]*)\]")
_QUOTES_RE = re.compile(r"'{2,}")


# Templates that wrap the text rather than describe it.  Deleting these along
# with the rest would delete the document: the whole Akathist sits inside a
# single ``{{block center|<poem>…</poem>}}``, and stripping it left three stray
# header rows where 370 lines of hymn should have been.
_WRAPPER_TEMPLATES = {"block center", "center", "poem", "κέντρο", "στοίχιση"}


def _strip_templates(text: str) -> str:
    """Drop ``{{...}}``, but keep the contents of the wrappers listed above.

    Written as a scan rather than a regex because templates nest, and the
    header template of a Wikisource page routinely contains several others.
    """
    out: list[str] = []
    # Each open template records where its body began and whether it is a
    # wrapper whose body should survive.
    stack: list[tuple[int, bool]] = []
    index = 0
    while index < len(text):
        if text.startswith("{{", index):
            end = text.find("|", index + 2)
            close = text.find("}}", index + 2)
            name = ""
            if end != -1 and (close == -1 or end < close):
                name = text[index + 2 : end].strip().lower()
            stack.append((len(out), name in _WRAPPER_TEMPLATES))
            index += 2
            if name in _WRAPPER_TEMPLATES and end != -1:
                index = end + 1
            continue
        if text.startswith("}}", index) and stack:
            stack.pop()
            index += 2
            continue
        if not stack or stack[-1][1]:
            out.append(text[index])
        index += 1
    return "".join(out)


def strip_wikitext(text: str) -> str:
    text = _COMMENT_RE.sub(" ", text)
    text = _REF_RE.sub(" ", text)
    text = _strip_templates(text)
    text = _META_LINK_RE.sub(" ", text)
    text = _LINK_RE.sub(r"\1", text)
    text = _EXTLINK_RE.sub(r"\1", text)
    text = _TAG_RE.sub(" ", text)
    text = _QUOTES_RE.sub("", text)
    return text


def _clean_line(line: str) -> str:
    line = strip_wikitext(line)
    line = line.lstrip(":*# ").strip()
    return re.sub(r"\s+", " ", line).strip()


def _read(stem: str) -> str:
    """Frozen wikitext with the whole-document markup already removed.

    Templates, comments and footnotes have to go before the text is split into
    lines: the page header is a template spread over a dozen lines, and cleaning
    line by line leaves its parameter rows behind as if they were hymn verses
    ("| τίτλος = Ακάθιστος ύμνος").
    """
    path = CHURCH_DIR / f"{stem}.wiki"
    if not path.exists():
        raise FileNotFoundError(
            f"缺少凍結的教會文獻來源：{path}；先跑 fetch_greek_church_documents.py --write"
        )
    body = unicodedata.normalize("NFC", path.read_text(encoding="utf-8"))
    body = _COMMENT_RE.sub(" ", body)
    body = _REF_RE.sub(" ", body)
    body = _META_LINK_RE.sub(" ", body)
    return _strip_templates(body)


_HEADING_RE = re.compile(r"^==+\s*(?:Κανὼν|Κανών|Κανόνας)\s+([^=]+?)\s*==+\s*$", re.M)

# Several of these pages print the Pedalion's commentary under each canon, and
# it is Nicodemus writing in Katharevousa — "Ὄχι μόνον…", "νά μὴ γίνωνται…" —
# not the ancient canon.  Taken as canon text it put modern Greek into a Koine
# reader.  The heading is set letter-spaced, so the pattern allows the spaces.
_COMMENTARY_RE = re.compile(
    r"^\s*[ἘΕE]\s*ρ\s*μ\s*η\s*ν\s*ε\s*ί\s*α\s*[.·:]?\s*$", re.M
)


def load_canons(stem: str, first: int = 0, last: int = 0) -> list[Segment]:
    """One segment per canon, numbered as the collection numbers it."""
    body = _read(stem)
    matches = list(_HEADING_RE.finditer(body))
    if not matches:
        raise LookupError(f"{stem}：找不到任何條號標題")
    segments: list[Segment] = []
    commented = 0
    for index, match in enumerate(matches):
        number = greek_numeral(match.group(1))
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        block = body[start:end]
        commentary = _COMMENTARY_RE.search(block)
        if commentary:
            block = block[: commentary.start()]
            commented += 1
        text = " ".join(
            part for part in (_clean_line(line) for line in block.splitlines()) if part
        )
        text = re.sub(r"\s+", " ", text).strip()
        if not text or not GREEK_RE.search(text):
            raise ValueError(f"{stem} 第 {number} 條沒有希臘文正文")
        if first and not (first <= number <= last):
            continue
        segments.append(Segment(str(number), text))
    if not segments:
        raise LookupError(f"{stem}：第 {first}–{last} 條不存在")
    numbers = [int(segment.ref) for segment in segments]
    if numbers != sorted(numbers):
        raise ValueError(f"{stem}：條號不是遞增的，來源可能被改動過")
    LAST_COMMENTARY_COUNT[stem] = commented
    return segments


# How many canons of the last-loaded collection carried a commentary block that
# was cut away.  Recorded so the reading can say so rather than the removal
# being invisible.
LAST_COMMENTARY_COUNT: dict[str, int] = {}


def canon_count(stem: str) -> int:
    return len(load_canons(stem))


def load_hymn(stem: str) -> list[Segment]:
    """One segment per printed line of a hymn, in order."""
    body = _read(stem)
    segments: list[Segment] = []
    for line in body.splitlines():
        text = _clean_line(line)
        if not text or not GREEK_RE.search(text):
            continue
        # A bare heading line inside a hymn ("ΟΙ ΟΙΚΟΙ") is a rubric, not a
        # sung line, but it belongs to the printed text, so it is kept and
        # simply numbered with everything else rather than silently dropped.
        segments.append(Segment(str(len(segments) + 1), text))
    if not segments:
        raise LookupError(f"{stem}：清理後沒有任何希臘文行")
    return segments


def word_count(segments: list[Segment]) -> int:
    return sum(len([w for w in segment.text.split() if GREEK_RE.search(w)]) for segment in segments)
