#!/usr/bin/env python3
"""Work out a Greek headword's part of speech, or admit that it cannot.

The Greek vocabulary master carries no part-of-speech field, but a Greek
dictionary entry encodes one anyway: ``ἄγγελος, -ου, ὁ`` names its article,
``ἀγαθός, -ή, -όν`` shows three terminations, and a verb is cited in the first
person. Where the form is silent the Chinese gloss usually is not — the reader's
own glosses write ``（配屬格）`` for a preposition and end an adjective in 「的」.

Anything those rules cannot settle returns an empty string and the card prints
no part of speech. A blank line on a flashcard costs nothing; a wrong label is
learned as fact.
"""

from __future__ import annotations

import re

ARTICLES = {"ὁ", "ἡ", "τό", "οἱ", "αἱ", "τά", "ὅ"}
VERB_ENDING = re.compile(r"(ω|ῶ|ομαι|οῦμαι|άομαι|έομαι|μαι|μι)$")

# The commonest function words in Koine, which no ending betrays.  Keyed by the
# lemma exactly as the vocabulary master writes it.
FUNCTION_WORDS: dict[str, str] = {
    # 介系詞
    "ἐν": "介系詞", "εἰς": "介系詞", "ἐκ (ἐξ)": "介系詞", "ἐκ": "介系詞", "ἀπό": "介系詞",
    "διά": "介系詞", "μετά": "介系詞", "παρά": "介系詞", "πρός": "介系詞", "ὑπό": "介系詞",
    "ἐπί": "介系詞", "περί": "介系詞", "σύν": "介系詞", "ὑπέρ": "介系詞", "κατά": "介系詞",
    "ἀντί": "介系詞", "πρό": "介系詞", "ἄνευ": "介系詞", "ἐνώπιον": "介系詞", "χωρίς": "介系詞",
    "ἕως": "介系詞", "ἄχρι": "介系詞", "μέχρι": "介系詞", "ἔμπροσθεν": "介系詞",
    "ὀπίσω": "介系詞", "ἔξω": "介系詞", "ἐγγύς": "介系詞", "πλήν": "介系詞",
    # 連接詞
    "καί": "連接詞", "δέ": "連接詞", "ἀλλά": "連接詞", "γάρ": "連接詞", "ὅτι": "連接詞",
    "ἵνα": "連接詞", "ὡς": "連接詞", "ἐάν": "連接詞", "εἰ": "連接詞", "εἰ μή": "連接詞",
    "ὥστε": "連接詞", "οὖν": "連接詞", "οὐδέ": "連接詞", "μηδέ": "連接詞", "οὔτε": "連接詞",
    "μήτε": "連接詞", "ἤ": "連接詞", "καθώς": "連接詞", "ὅπως": "連接詞", "ὅταν": "連接詞",
    "ὅτε": "連接詞", "τε": "連接詞", "διό": "連接詞", "ἄρα": "連接詞", "εἴτε": "連接詞",
    "ἐπεί": "連接詞", "ἐπειδή": "連接詞", "πρίν": "連接詞", "μέντοι": "連接詞",
    # 質詞與否定
    "οὐ (οὐκ": "質詞", "οὐ": "質詞", "οὐκ": "質詞", "οὐχ": "質詞", "μή": "質詞",
    "ἄν": "質詞", "μέν": "質詞", "γε": "質詞", "ἰδού": "質詞", "ἴδε": "質詞",
    "ἀμήν": "質詞", "ναί": "質詞", "οὐχί": "質詞", "μήτι": "質詞", "ἆρα": "質詞",
    # 副詞
    "νῦν": "副詞", "ἤδη": "副詞", "ὧδε": "副詞", "ἐκεῖ": "副詞", "πάλιν": "副詞",
    "εὐθύς": "副詞", "τότε": "副詞", "πῶς": "副詞", "ποῦ": "副詞", "πότε": "副詞",
    "οὕτως": "副詞", "σφόδρα": "副詞", "λίαν": "副詞", "ἔτι": "副詞", "οὐκέτι": "副詞",
    "μᾶλλον": "副詞", "μόνον": "副詞", "ἅμα": "副詞", "εὐθέως": "副詞", "ταχύ": "副詞",
    # 代名詞
    "ἐγώ": "代名詞", "σύ": "代名詞", "ἡμεῖς": "代名詞", "ὑμεῖς": "代名詞",
    "αὐτός": "代名詞", "οὗτος": "代名詞", "ἐκεῖνος": "代名詞", "ὅς": "代名詞",
    "τίς": "代名詞", "τὶς": "代名詞", "ἀλλήλων": "代名詞", "ἑαυτοῦ": "代名詞",
    "οὐδείς": "代名詞", "μηδείς": "代名詞", "ἐμός": "代名詞", "σός": "代名詞",
    "ἡμέτερος": "代名詞", "ὑμέτερος": "代名詞", "μοῦ": "代名詞", "ὅστις": "代名詞",
    "ὅδε": "代名詞",
    # 數詞
    "εἷς": "數詞", "δύο": "數詞", "τρεῖς": "數詞", "τέσσαρες": "數詞", "πέντε": "數詞",
    "ἕξ": "數詞", "ἑπτά": "數詞", "ὀκτώ": "數詞", "ἐννέα": "數詞", "δέκα": "數詞",
    "ἑκατόν": "數詞", "χίλιοι": "數詞", "μυρίας": "數詞",
}

PREPOSITION_HINT = re.compile(r"（配(屬格|賓格|所有格|與格|處格)")

# Adverbs are the one open class Greek marks in the ending itself.
ADVERB_ENDING = re.compile(r"(ως|θεν|οτε|ποτε|άκις)$")

# Verbs the lexicon cites in a form no ending rule recognises: the copula and
# its tenses, the perfects used as presents, and the impersonals.
IRREGULAR_VERBS = {
    "εἰμί", "ἦν", "ἔσομαι", "εἶπεν", "εἶπον", "ἔφη", "φημί", "οἶδα", "δεῖ",
    "ἀπεκρίθη", "ἔξεστι", "ἔξεστιν", "χρή", "ἰδεῖν", "εἰδέναι", "ἐστίν", "εἰσίν",
}


def greek_part_of_speech(entry: dict, gloss_zh: str = "") -> str:
    """Return a Chinese part-of-speech label, or "" when the form is ambiguous."""

    lemma = (entry.get("lemma") or "").strip()
    printed = (entry.get("printedEntry") or "").strip()

    if lemma in FUNCTION_WORDS:
        return FUNCTION_WORDS[lemma]
    if entry.get("isProperName"):
        return "專名"

    raw_parts = [part.strip() for part in printed.split(",")]
    # Some entries write the article as "-ὁ"; the dash is formatting, not form.
    parts = [part.lstrip("-").strip() for part in raw_parts]
    if len(parts) > 1 and parts[-1] in ARTICLES:
        return "名詞"
    if len(raw_parts) >= 3 and all(part.startswith("-") for part in raw_parts[1:]):
        return "形容詞"

    if PREPOSITION_HINT.search(gloss_zh):
        return "介系詞"

    if lemma in IRREGULAR_VERBS or VERB_ENDING.search(lemma):
        return "動詞"
    if ADVERB_ENDING.search(lemma):
        return "副詞"

    senses = [sense for sense in gloss_zh.split("；") if sense]
    if senses and all(sense.endswith("的") for sense in senses):
        return "形容詞"

    return ""
