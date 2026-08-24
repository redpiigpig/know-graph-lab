#!/usr/bin/env python3
"""Three-layer lemmatiser for ecclesiastical Latin, in a fixed order.

Layer one is the Vulgate itself as PROIEL tagged it.  Layer two is a bridge
from Clementine and later church spelling back to that inventory.  Layer three
is nothing: a token the first two layers cannot resolve is left uncounted and
reported, never guessed.

The bridge exists because the same word is spelled several ways across the
fifteen centuries this reader covers.  Jerome's text as PROIEL prints it has
Israhel and eius; the Clementine edition prints Israël and ejus; a scholastic
manuscript tradition prints michi for mihi and nuncius for nuntius.  These are
not different words and must not become different vocabulary entries.

Every rewrite is checked against the Vulgate inventory before it is accepted,
so the bridge can only ever land on a word Jerome actually used -- it cannot
invent one.  The Greek reader's bridge was written the same way after an
unchecked rewrite produced headwords for words that do not exist.

Enclitics are handled here too.  Latin writes ``dixitque`` as one word, and
without stripping the ``-que`` the corpus reports a hapax for every verb in
narrative prose.  The stripped form has to be in the inventory for the strip to
count, which keeps ``quisque`` and ``namque`` intact -- those are words in their
own right, not host plus enclitic.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import latin_source_texts as L  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LEXICON = ROOT / "output" / "source-cache" / "original-readers" / "latin-full" / "latin-lexicon.json"

ENCLITICS = ("que", "ve", "ne")

# Applied to the folded key, so j/v/ligatures/accents are already gone.
REWRITES = (
    ("h", ""),           # Israhel / Israel, Hierusalem / Ierusalem
    ("ci", "ti"),        # nuncius / nuntius
    ("ti", "ci"),
    ("mpn", "mn"),       # sompnus / somnus
    ("y", "i"),          # ymnus / imnus
    ("ae", "e"),         # celum / caelum, both directions
    ("e", "ae"),
    ("ph", "f"),
    ("mich", "mih"),     # michi / mihi
)

# Spellings a scribe used for a word Jerome spells differently.  These are
# named one by one rather than derived, because the rules that would generate
# them (qu -> c, oe -> e) also destroy real words: qui would become ci.
MEDIEVAL = {
    "quum": "cum", "coelum": "caelum", "coeli": "caeli", "nichil": "nihil",
    "michi": "mihi", "sompnus": "somnus", "ymnus": "hymnus",
    "foelix": "felix", "charitas": "caritas", "christianus": "christianus",
    "sanctimonia": "sanctimonia", "quidquid": "quisquis",
}

ROMAN = re.compile(r"^[IVXLCDM]+$")


class Lemmatiser:
    def __init__(self) -> None:
        data = json.loads(LEXICON.read_text(encoding="utf-8"))
        self.exact: dict[str, str] = data["exactForms"]
        self.folded: dict[str, str] = data["foldedForms"]
        self.registers: dict[str, dict] = data["registers"]
        self.formRegister: dict[str, str] = data["formRegister"]
        self.pos: dict[str, str] = data["pos"]
        self.names: dict[str, str] = data["properNames"]
        self.routes: dict[str, int] = {"exact": 0, "folded": 0, "bridge": 0, "enclitic": 0}

    # -- layer two ---------------------------------------------------------
    def _bridge(self, key: str) -> str | None:
        for src, dst in REWRITES:
            if src and src in key:
                candidate = key.replace(src, dst)
                if candidate in self.folded:
                    return self.folded[candidate]
        return None

    def _strip_enclitic(self, key: str) -> str | None:
        for clitic in ENCLITICS:
            if len(key) > len(clitic) + 2 and key.endswith(clitic):
                stem = key[: -len(clitic)]
                if stem in self.folded:
                    return self.folded[stem]
        return None

    # -- entry point -------------------------------------------------------
    def lemma(self, word: str) -> str | None:
        if word in self.exact:
            self.routes["exact"] += 1
            return self.exact[word]
        key = L.fold(word)
        if key in self.folded:
            self.routes["folded"] += 1
            return self.folded[key]
        swap = MEDIEVAL.get(key)
        if swap and L.fold(swap) in self.folded:
            self.routes["bridge"] += 1
            return self.folded[L.fold(swap)]
        found = self._strip_enclitic(key)
        if found:
            self.routes["enclitic"] += 1
            return found
        found = self._bridge(key)
        if found:
            self.routes["bridge"] += 1
            return found
        return None

    @staticmethod
    def is_word(token: str) -> bool:
        """Reject what is printed in a Latin text but is not Latin vocabulary."""
        if len(token) < 2:
            return False
        if ROMAN.match(token):
            return False
        return True
