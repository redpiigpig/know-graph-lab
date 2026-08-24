#!/usr/bin/env python3
"""Whitaker's WORDS as a dictionary register for the Latin reader.

The treebanks give a lemma but never a dictionary entry.  A reader that prints
``cardinalis`` alone has not taught the word: Latin vocabulary is learned as
principal parts, and the lower volume's thousand words arrive from corpus
frequency with nothing but a bare lemma attached.  Collins supplies them for the
upper volume; this supplies them for the lower one.

WORDS stores stems rather than dictionary forms -- ``voc voc vocav vocat`` for
``voco, vocare, vocavi, vocatus`` -- and reassembles the entry at display time
from the part-of-speech codes.  That reassembly is ported here from Whitaker's
own ``Support_Utils.Dictionary_Form``, so the principal parts this reader prints
are the ones his dictionary prints, rather than paradigms guessed from a lemma's
ending.  Guessing would be wrong exactly where it matters: the irregular verbs
and third-declension nouns that church Latin is full of.

Two of Whitaker's flag columns are worth as much as the definitions.  AGE marks
how late a word is, and AREA marks what field it belongs to; a word flagged
``E`` in AREA is ecclesiastical, which is how this reader can tell that
``dioecesis`` is church vocabulary and ``domus`` is not, without anyone writing
that list by hand.

The data is Whitaker's, given freely for any use.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import latin_source_texts as L  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DICTLINE = (ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
            / "whitakers-words-master" / "DICTLINE.GEN")

AGE = {
    "X": "不限", "A": "古體", "B": "早期", "C": "古典", "D": "晚期",
    "E": "後古典（教父期）", "F": "中世紀", "G": "經院／文藝復興", "H": "近代",
}
AREA = {
    "X": "", "A": "農業", "B": "生物", "D": "戲劇音樂", "E": "教會宗教",
    "G": "文法修辭", "L": "法律", "P": "詩體", "S": "科學", "T": "技術",
    "W": "軍事", "Y": "神話",
}
FREQ = {
    "X": "", "A": "極常用", "B": "常用", "C": "普通", "D": "較少",
    "E": "罕見", "F": "極罕", "I": "銘文", "M": "塗鴉", "N": "普林尼",
}


@dataclass
class Entry:
    stems: tuple[str, str, str, str]
    pos: str
    codes: list[str]
    age: str
    area: str
    geo: str
    freq: str
    source: str
    definition: str
    form: str = ""
    lemma: str = ""
    variants: tuple[str, ...] = field(default_factory=tuple)

    @property
    def ecclesiastical(self) -> bool:
        return self.area == "E" or self.age in {"E", "F", "G"}


def _add(stem: str, ending: str) -> str:
    return (stem + ending).strip() if stem and stem != "zzz" else ""


def _int(codes: list[str], index: int, default: int = 0) -> int:
    try:
        return int(codes[index])
    except (IndexError, ValueError):
        return default


def noun_form(stems, codes) -> list[str]:
    which, var = _int(codes, 0), _int(codes, 1)
    s1, s2 = stems[0], stems[1]
    if which == 1:
        table = {1: ("a", "ae"), 6: ("e", "es"), 7: ("es", "ae"), 8: ("as", "ae")}
        nom, gen = table.get(var, ("a", "ae"))
    elif which == 2:
        table = {1: ("us", "i"), 2: ("um", "i"), 3: ("", "i"), 4: ("us", "(i)"),
                 5: ("us", ""), 6: ("os", "i"), 7: ("", "yos/i"), 8: ("on", "i"),
                 9: ("us", "i")}
        nom, gen = table.get(var, ("us", "i"))
        # Variant 4 takes its nominative from the gender column, and neuters
        # are most of it: concilium, officium, iudicium all sit here, and
        # ignoring the gender turns every one of them into a false -us noun.
        if var == 4 and len(codes) > 2 and codes[2] == "N":
            nom = "um"
    elif which == 3:
        nom, gen = "", "os/is" if var in (7, 9) else "is"
    elif which == 4:
        table = {1: ("us", "us"), 2: ("u", "us"), 3: ("us", "u"), 4: ("", "u")}
        nom, gen = table.get(var, ("us", "us"))
    elif which == 5:
        nom, gen = "es", "ei"
    else:
        return [_add(s1, "")]
    return [_add(s1, nom), _add(s2, gen)]


def adjective_form(stems, codes) -> list[str]:
    which, var = _int(codes, 0), _int(codes, 1)
    degree = codes[2] if len(codes) > 2 else "POS"
    s1, s2 = stems[0], stems[1]
    if degree == "COMP":
        return [_add(s1, "or"), _add(s1, "or"), _add(s1, "us")]
    if degree == "SUPER":
        return [_add(s1, "mus"), _add(s1, "ma"), _add(s1, "mum")]
    if which == 1:
        table = {1: ("us", "a", "um"), 2: ("", "a", "um"), 3: ("us", "a", "um"),
                 4: ("", "a", "um"), 5: ("us", "a", "ud")}
        m, f, n = table.get(var, ("us", "a", "um"))
        return [_add(s1, m), _add(s2, f), _add(s2, n)]
    if which == 3:
        if var == 1:
            return [_add(s1, ""), _add(s2, "is")]
        if var == 2:
            return [_add(s1, "is"), _add(s2, "is"), _add(s2, "e")]
        if var == 3:
            return [_add(s1, ""), _add(s2, "is"), _add(s2, "e")]
        return [_add(s1, ""), _add(s2, "os")]
    if which == 2:
        return [_add(s1, "e")] if var == 1 else [_add(s1, "es")]
    return [_add(s1, "")]


def verb_form(stems, codes) -> list[str]:
    which, var = _int(codes, 0), _int(codes, 1)
    kind = codes[2] if len(codes) > 2 else "X"
    s1, s2, s3, s4 = stems

    if kind == "DEP":
        if which == 1:
            parts = [_add(s1, "or"), _add(s2, "ari")]
        elif which == 2:
            parts = [_add(s1, "eor"), _add(s2, "eri")]
        else:
            parts = [_add(s1, "or"), _add(s2, "iri" if var == 4 else "i")]
        return parts + [_add(s4, "us sum")]
    if kind == "PERFDEF":
        return [_add(s3, "i"), _add(s3, "isse"), _add(s4, "us")]

    if which == 2:
        first = _add(s1, "eo")
    elif which == 5:
        first = _add(s1, "um")
    elif (which, var) == (7, 2):
        first = _add(s1, "am")
    else:
        first = _add(s1, "o")

    if which == 1:
        second = _add(s2, "are")
    elif which == 2:
        second = _add(s2, "ere")
    elif which == 3:
        endings = {2: "re", 3: "ieri" if s2.strip() == "f" else "eri", 4: "ire"}
        second = _add(s2, endings.get(var, "ere"))
    elif which == 5:
        second = _add(s2, "esse") if var == 1 else _add(s1, "e")
    elif which == 6:
        second = _add(s2, "re" if var == 1 else "le")
    elif which == 7:
        second = _add(s2, "se") if var == 3 else ""
    elif which == 8:
        second = _add(s2, {1: "are", 2: "ere", 3: "ere", 4: "ire"}.get(var, "ere"))
    else:
        second = ""

    if kind == "SEMIDEP":
        rest = [_add(s3, "i"), _add(s4, "us sum")]
    elif (which, var) == (5, 1):
        rest = [_add(s3, "i"), _add(s4, "urus")]
    elif which in (8, 9):
        rest = []
    else:
        rest = [_add(s3, "i"), _add(s4, "us")]
    return [p for p in [first, second, *rest] if p]


def numeral_form(stems, codes) -> list[str]:
    which, var = _int(codes, 0), _int(codes, 1)
    sort = codes[2] if len(codes) > 2 else "X"
    s1 = stems[0]
    if sort == "CARD" and which == 1:
        table = {1: ("us", "a", "um"), 2: ("o", "ae", "o"),
                 3: ("es", "es", "ia"), 4: ("i", "ae", "a")}
        m, f, n = table.get(var, ("us", "a", "um"))
        return [_add(s1, m), _add(s1, f), _add(s1, n)]
    return [_add(s1, "")]


def pronoun_form(stems, codes) -> list[str]:
    which, var = _int(codes, 0), _int(codes, 1)
    s1, s2 = stems[0], stems[1]
    if which == 3:
        return [_add(s1, "ic"), _add(s1, "aec"), _add(s1, "oc" if var == 1 else "uc")]
    if which == 4:
        if var == 1:
            return [_add(s1, "s"), _add(s2, "a"), _add(s1, "d")]
        return [_add(s1, "dem"), _add(s2, "adem"), _add(s1, "dem")]
    if which == 6:
        return [_add(s1, "e"), _add(s1, "a"), _add(s1, "ud" if var == 1 else "um")]
    return [_add(s1, "")]


BUILDERS = {
    "N": noun_form,
    "ADJ": adjective_form,
    "V": verb_form,
    "NUM": numeral_form,
    "PRON": pronoun_form,
}


def parse_line(line: str) -> Entry | None:
    line = line.rstrip("\r\n")
    if len(line) < 110:
        return None
    stems = tuple((line[i:i + 19]).strip() for i in (0, 19, 38, 57))
    pos = line[76:83].strip()
    codes = line[83:100].split()
    flags = line[100:110].split()
    if len(flags) < 5:
        flags += ["X"] * (5 - len(flags))
    definition = line[110:].strip().rstrip(";")
    if not stems[0] or not pos:
        return None
    entry = Entry(stems, pos, codes, flags[0], flags[1], flags[2], flags[3],
                  flags[4], definition)
    builder = BUILDERS.get(pos)
    parts = builder(stems, codes) if builder else [stems[0]]
    parts = [p for p in parts if p]
    entry.form = ", ".join(parts)
    entry.lemma = parts[0] if parts else stems[0]
    entry.variants = tuple(parts)
    return entry


def load() -> list[Entry]:
    entries = []
    for line in DICTLINE.read_text(encoding="latin-1").splitlines():
        entry = parse_line(line)
        if entry:
            entries.append(entry)
    return entries


def index_by_lemma(entries: list[Entry]) -> dict[str, list[Entry]]:
    """Fold the headword so treebank spelling and WORDS spelling can meet."""
    index: dict[str, list[Entry]] = {}
    for entry in entries:
        if not entry.lemma:
            continue
        index.setdefault(L.fold(entry.lemma), []).append(entry)
    return index


if __name__ == "__main__":
    data = load()
    print(f"WORDS 詞條 {len(data):,}")
    by_lemma = index_by_lemma(data)
    print(f"詞頭 {len(by_lemma):,}")
    for probe in ("voco", "cardinalis", "sum", "dioecesis", "episcopus", "fero", "res"):
        hits = by_lemma.get(L.fold(probe), [])
        if not hits:
            print(f"  {probe}: 查無")
            continue
        best = hits[0]
        print(f"  {probe}: {best.form}  [{best.pos} {AGE.get(best.age,'')}"
              f"{'/' + AREA[best.area] if AREA.get(best.area) else ''}] {best.definition[:60]}")
