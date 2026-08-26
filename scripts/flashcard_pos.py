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

import collections
import re
from pathlib import Path

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
    # 冠詞。定冠詞的詞典形是三個性別（ὁ, ἡ, τό），詞尾規則會把最後那個 τό 當成
    # 名詞的性別標記，於是把冠詞本身判成名詞。
    "ὁ": "冠詞",
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


# What neither the tagged New Testament nor the citation form settles: the
# Septuagint and patristic words the SBLGNT never uses, read one at a time.
# Nouns dominate because a bare Septuagint headword carries no article, which is
# the cue the citation-form rule needs.
EXTRA_LEXICON: dict[str, str] = {
    "κριός": "名詞",
    "πεδίον": "名詞",
    "πρόσταγμα": "名詞",
    "σκῦλον": "名詞",
    "χειμάρρους": "名詞",
    "στέαρ": "名詞",
    "ὁλοκαύτωσις": "名詞",
    "τραυματίας": "名詞",
    "διάψαλμα": "名詞",
    "αἴξ": "名詞",
    "συνάντησις": "名詞",
    "σίκλος": "名詞",
    "λάκκος": "名詞",
    "σπονδή": "名詞",
    "δρυμός": "名詞",
    "ἐπίσκεψις": "名詞",
    "ἁγίασμα": "名詞",
    "κάρπωμα": "名詞",
    "παράταξις": "名詞",
    "περισπόριον": "名詞",
    "εὖρος": "名詞",
    "ἐπιτήδευμα": "名詞",
    "χίμαρος": "名詞",
    "ἐπιστήμη": "名詞",
    "σταθμός": "名詞",
    "πετεινός": "名詞",
    "ὁμόνοια": "名詞",
    "σχισμή": "名詞",
    "ὄργανον": "名詞",
    "κάλλος": "名詞",
    "τρόπαιον": "名詞",
    "ἀγαθότης": "名詞",
    "παραφυάς": "名詞",
    "ἰδέα": "名詞",
    "πτελέα": "名詞",
    "ἔδεσμα": "名詞",
    "φορά": "名詞",
    "γνώρισμα": "名詞",
    "ἀκακία": "名詞",
    "σύγγραμμα": "名詞",
    "ἀθεότης": "名詞",
    "συγγραφεύς": "名詞",
    "χρῶμα": "名詞",
    "ἀμέλεια": "名詞",
    "τριάς": "名詞",
    "πρᾳότης": "名詞",
    "σύμβολον": "名詞",
    "προαίρεσις": "名詞",
    "αὐθάδεια": "名詞",
    "ἀντίψυχος": "名詞",
    "πολυτέλεια": "名詞",
    "ἰτέα": "名詞",
    "τύραννος": "名詞",
    "ξίφος": "名詞",
    "ὑπάρχοντα": "名詞",
    "στρατία": "名詞",
    "εὐταξία": "名詞",
    "καταφθορά": "名詞",
    "ποικιλία": "名詞",
    "διαφορά": "名詞",
    "ἀκολουθία": "名詞",
    "πλημμέλημα": "名詞",
    "κατάληψις": "名詞",
    "κίνησις": "名詞",
    "συμφορά": "名詞",
    "ἀθλητής": "名詞",
    "φροντίς": "名詞",
    "βλάβη": "名詞",
    "δημιουργία": "名詞",
    "αὔρα": "名詞",
    "δίαιτα": "名詞",
    "ἐξήγησις": "名詞",
    "σύστασις": "名詞",
    "βορά": "名詞",
    "κόρη": "名詞",
    "βιβλάριον": "名詞",
    "σέ": "代名詞",
    "ὑμῶν": "代名詞",
    "ἡμῶν": "代名詞",
    "σοί": "代名詞",
    "μέ": "代名詞",
    "μοι": "代名詞",
    "ὑμῖν": "代名詞",
    "ὑμᾶς": "代名詞",
    "ἡμᾶς": "代名詞",
    "ἐμοῦ": "代名詞",
    "ἡμῖν": "代名詞",
    "ἐμέ": "代名詞",
    "ἐμοί": "代名詞",
    "πότερος": "代名詞",
    "ὅσπερ": "代名詞",
    "εἴκοσι": "數詞",
    "τεσσαράκοντα": "數詞",
    "αιλαμ": "專名",
    "σαβαώθ": "專名",
    "πλείων": "形容詞",
    "ἀμφότερος": "形容詞",
    "ἐνώπιος": "形容詞",
    "σύμπας": "形容詞",
    "ἀκόλουθος": "形容詞",
    "ῥᾴδιος": "形容詞",
    "πρότερον": "副詞",
    "λοιπόν": "副詞",
    "ἥττον": "副詞",
    "πάνυ": "副詞",
    "ἔνθα": "副詞",
    "ἐνταῦθα": "副詞",
    "οὐδαμοῦ": "副詞",
    "τοι": "質詞",
    "γοῦν": "質詞",
    "ἅτε": "連接詞",
    "ιν": "連接詞",
    "συνόχωκα": "動詞",
    "προεῖπον": "動詞",
    "ἐπεῖδον": "動詞",
    "ἐξεῖπον": "動詞",
}

PREPOSITION_HINT = re.compile(r"（配(屬格|賓格|所有格|與格|處格)")

# Adverbs are the one open class Greek marks in the ending itself.  Match the
# accented spellings too: καλῶς carries a circumflex, and a pattern written with
# a bare omega silently never matches it.
ADVERB_ENDING = re.compile(r"([ωώῶ]ς|θεν|[οό]τε|ποτε|[αά]κις)$")

# Verbs the lexicon cites in a form no ending rule recognises: the copula and
# its tenses, the perfects used as presents, and the impersonals.
IRREGULAR_VERBS = {
    "εἰμί", "ἦν", "ἔσομαι", "εἶπεν", "εἶπον", "ἔφη", "φημί", "οἶδα", "δεῖ",
    "ἀπεκρίθη", "ἔξεστι", "ἔξεστιν", "χρή", "ἰδεῖν", "εἰδέναι", "ἐστίν", "εἰσίν",
}


# The New Testament is tagged word by word, so for anything the SBLGNT
# contains the part of speech is a recorded fact rather than an inference from
# the citation form.  The Septuagint and patristic sources carry no such tags,
# which is why the rules below still have work to do.
MORPHGNT_DIR = (
    Path(__file__).resolve().parents[1]
    / "output/source-cache/original-readers/greek-full/sources/sblgnt"
)

MORPHGNT_LABELS = {
    "N-": "名詞",
    "V-": "動詞",
    "A-": "形容詞",
    "D-": "副詞",
    "C-": "連接詞",
    "P-": "介系詞",
    "X-": "質詞",
    "I-": "感嘆詞",
    "RA": "冠詞",
    "RP": "代名詞",
    "RD": "代名詞",
    "RI": "代名詞",
    "RR": "代名詞",
}

_MORPHGNT: dict[str, str] | None = None


def morphgnt_part_of_speech(lemma: str) -> str:
    """The tag the SBLGNT gives this lemma most often, or an empty string.

    A lemma tagged two ways — ``ἔξω`` as both adverb and preposition — takes the
    commoner tag rather than being refused: both labels are true of the word, and
    the card has room for one.
    """
    global _MORPHGNT
    if _MORPHGNT is None:
        tally: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
        if MORPHGNT_DIR.is_dir():
            for path in sorted(MORPHGNT_DIR.glob("*-morphgnt.txt")):
                for line in path.read_text(encoding="utf-8").splitlines():
                    columns = line.split()
                    if len(columns) >= 7:
                        tally[columns[6]][columns[1]] += 1
        _MORPHGNT = {
            lemma_: MORPHGNT_LABELS[counter.most_common(1)[0][0]]
            for lemma_, counter in tally.items()
            if counter.most_common(1)[0][0] in MORPHGNT_LABELS
        }
    return _MORPHGNT.get(lemma, "")


def greek_part_of_speech(entry: dict, gloss_zh: str = "") -> str:
    """Return a Chinese part-of-speech label, or "" when the form is ambiguous."""

    lemma = (entry.get("lemma") or "").strip()
    printed = (entry.get("printedEntry") or "").strip()

    if lemma in FUNCTION_WORDS:
        return FUNCTION_WORDS[lemma]
    if lemma in EXTRA_LEXICON:
        return EXTRA_LEXICON[lemma]
    if entry.get("isProperName"):
        return "專名"

    raw_parts = [part.strip() for part in printed.split(",")]
    # Some entries write the article as "-ὁ"; the dash is formatting, not form.
    parts = [part.lstrip("-").strip() for part in raw_parts]
    if len(parts) > 1 and parts[-1] in ARTICLES:
        return "名詞"
    if len(raw_parts) >= 3 and all(part.startswith("-") for part in raw_parts[1:]):
        return "形容詞"

    tagged = morphgnt_part_of_speech(lemma)
    if tagged:
        return tagged

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
