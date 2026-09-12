#!/usr/bin/env python3
"""Lemmatise the two Latin corpora the reader draws on, and say where each
lemma came from.

The Hebrew reader could verify a composed sentence straight out of the WLC
because every word there arrives with its Strong number already attached.
Latin has no such file: the Clementine Vulgate we print (``latVUC``) is plain
text, and the treebank that carries gold lemmata (``UD_Latin-PROIEL``) covers
only Jerome's New Testament -- 109,517 tokens against the Clementine's 607,266.
So the lemma has to be assigned here, once, and written down together with the
evidence for it.

Three layers, in a fixed order, and every token records which one answered:

1. **gold, by reference** -- the same verse in PROIEL contains the same written
   form, so the lemma is the one a human annotator gave that very token.  This
   is the only layer that knows the context; it reaches the New Testament.
2. **gold, by type** -- the form occurs in a gold treebank with exactly one
   lemma anywhere in it.  Unambiguous, but blind to context.
3. **form table** -- ``exactForms``/``foldedForms`` from the lexicons built off
   those treebanks.  These tables collapse ambiguity: a form that PROIEL tags
   two ways still gets one entry, so a token resolved here is flagged
   ``ambiguous`` when the treebank knows more than one lemma for it.

Anything the three layers cannot place is written out as ``unknown``, never
guessed.  Ten per cent of the Clementine lands there, nearly all of it Old
Testament proper names and sacrificial vocabulary that the New Testament never
uses -- an honest hole, not a silent one.

Enclitics are decided by the dictionary, one word at a time.  ``armaque`` is
``arma`` plus ``que`` and ``itaque`` is not ``ita`` plus ``que``, and no rule
about final letters can tell them apart; what tells them apart is that
``itaque`` is itself a word in the tables and ``armaque`` is not.  A form that
stands in the tables whole is never cut.

Orthography is folded for comparison only -- ``cælum``/``caelum``,
``ejus``/``eius``, ``vidit``/``uidit`` are the same word and must count as one.
What the file prints in ``surface`` is whatever the edition printed.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import latin_source_texts as L  # noqa: E402
from latin_lemmatiser import MEDIEVAL, REWRITES  # noqa: E402

CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
VOCABULARY = ROOT / "data" / "originalReaders" / "vocabulary" / "latin-2000.json"
READER = CACHE / "latin-reader-two-volumes.json"
LEXICON = CACHE / "latin-lexicon.json"
VULGATE_LEXICON = CACHE / "vulgate-lexicon.json"

TREEBANKS = {
    "proiel": CACHE / "UD_Latin-PROIEL-master",
    "ittb": CACHE / "UD_Latin-ITTB-master",
    "llct": CACHE / "UD_Latin-LLCT-master",
    "perseus": CACHE / "UD_Latin-Perseus-master",
    "udante": CACHE / "UD_Latin-UDante-master",
    "circse": CACHE / "UD_Latin-CIRCSE-master",
}

OUTPUT = {
    "vulgate": CACHE / "lemma-corpus-vulgate.json",
    "church": CACHE / "lemma-corpus-church.json",
}

# PROIEL names the New Testament books its own way; latVUC uses eBible's codes.
PROIEL_BOOK = {
    "MATT": "MAT", "MARK": "MRK", "LUKE": "LUK", "JOHN": "JHN", "ACTS": "ACT",
    "ROM": "ROM", "1COR": "1CO", "2COR": "2CO", "GAL": "GAL", "EPH": "EPH",
    "PHIL": "PHP", "COL": "COL", "1THESS": "1TH", "2THESS": "2TH",
    "1TIM": "1TI", "2TIM": "2TI", "TIT": "TIT", "PHILEM": "PHM", "HEB": "HEB",
    "JAS": "JAS", "1PET": "1PE", "2PET": "2PE", "1JOHN": "1JN", "2JOHN": "2JN",
    "3JOHN": "3JN", "JUDE": "JUD", "REV": "REV",
}

REF_RE = re.compile(r"Ref=([A-Z0-9]+)_(\d+)\.(\d+)")
# Latin letters only, across all four blocks a Latin text uses: ASCII, the
# Latin-1 accents and ligatures the Clementine prints (cælum, fœdus), and
# Latin Extended-A/B, where the macrons of the vocabulary's headwords live
# (ōrdō).  The narrower ``À-ÿ`` this started as cut ``ōrdō`` into ``rd``.
WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿĀ-ɏ]+")
ENTITY_RE = re.compile(r"&(?:[A-Za-z]+|#\d+);")

# Longest first: a form ending in -que must not be read as ending in -e.
ENCLITICS = ("que", "ve", "ne")

LAYER_CODE = {"gold": "G", "form": "F", "unknown": "U"}
VIA_CODE = {
    "proiel-ref": "R",
    "treebank-type": "T",
    "lexicon-exactForms": "E",
    "lexicon-foldedForms": "D",
    "enclitic-split": "C",
    "spelling-bridge": "B",
    "unresolved": "-",
}
TOKEN_FIELDS = ["surface", "lemma", "layer", "via", "enclitic"]


# ---------------------------------------------------------------------------
# pure helpers -- these are what scripts/tests/test_latin_exercises.py pins
# ---------------------------------------------------------------------------

def fold(word: str) -> str:
    """Comparison key: ligatures expanded, j/v levelled, accents and case gone.

    Only ever used to compare.  Nothing folded is printed back to the learner.
    """
    return L.fold(word)


def tokenise(text: str) -> list[str]:
    """The written words of a passage, spelled as the edition spells them.

    HTML entities are dropped first.  Eleven places in the lower volume's
    readings still carry ``&lt;h&gt;ymni`` -- the Latin Library's angle brackets
    around a letter the manuscript omits, escaped once too often somewhere
    upstream.  Left alone they hand the tagger two hapax words, ``lt`` and
    ``gt``, in the middle of a real one; removed, what is left is ``hymni``,
    which is the word.  This is a reading normalisation, not a repair: the
    reader's own file still prints what it prints.
    """
    return WORD_RE.findall(ENTITY_RE.sub("", text))


def split_enclitic(
    word: str, attested: Iterable[str], whole: Iterable[str] | None = None
) -> tuple[str, str] | None:
    """Decide whether a written word is host plus enclitic, by dictionary.

    ``itaque``, ``neque``, ``quisque``, ``denique``, ``atque``, ``utique`` all
    end in -que and none of them is a host plus an enclitic; ``armaque``,
    ``dixitque``, ``populusque`` all end in -que and all of them are.  The
    difference is not in the letters, it is in the lexicon: the first group are
    words, the second group are not.  So the first question asked is whether
    the whole form stands in the tables, and if it does the word is left alone.

    ``whole`` is the vocabulary consulted for "is this already a word"; it
    defaults to ``attested`` and is widened when the corpus being checked is
    narrower than the dictionary -- a word the Vulgate never happens to print
    must still not be cut in half.

    Returns ``(host_key, enclitic)`` as folded keys, or ``None``.
    """
    attested = attested if isinstance(attested, (set, frozenset)) else set(attested)
    known = attested if whole is None else (
        whole if isinstance(whole, (set, frozenset)) else set(whole)
    )
    key = fold(word)
    if key in known:
        return None
    for clitic in ENCLITICS:
        if key.endswith(clitic) and len(key) - len(clitic) >= 2:
            host = key[: -len(clitic)]
            if host in attested:
                return host, clitic
    return None


def bridge_spelling(key: str, folded_table: dict[str, str]) -> str | None:
    """Fifteen centuries spell one word several ways; land them on one entry.

    Every rewrite must hit something already in the table, so the bridge can
    only reach a word Jerome or the schoolmen actually wrote -- it cannot
    invent one.  Lifted from ``latin_lemmatiser`` so both readers share the
    same list rather than drifting apart.
    """
    swap = MEDIEVAL.get(key)
    if swap:
        candidate = fold(swap)
        if candidate in folded_table:
            return folded_table[candidate]
    for src, dst in REWRITES:
        if src and src in key:
            candidate = key.replace(src, dst)
            if candidate in folded_table:
                return folded_table[candidate]
    return None


TRIM = " \t\"'«»“”‘’—–-"


def clause_pieces(text: str) -> list[str]:
    """Cut a passage at the full stops the edition itself printed.

    Latin has no accent system marking clause ends the way the Masoretes' does,
    so the stops are the edition's.  Only the strong ones count here -- full
    stop, colon, semicolon, question and exclamation mark -- because those are
    where a Clementine editor ends a thought.  The comma is a phrase mark, and
    cutting on it produced things like ``et ad Saram``: three words, every one
    of them taught, and not a sentence.
    """
    pieces = [piece.strip(TRIM) for piece in re.split(r"[.;:?!]+", text)]
    return [piece for piece in pieces if tokenise(piece)]


def comma_pieces(text: str) -> list[str]:
    """The fallback cut, for a clause too long to print whole.

    Offered only when the strong-stop piece overruns; whether the result reads
    as a sentence is decided afterwards, by whether it has a verb in it.
    """
    pieces = [piece.strip(TRIM) for piece in re.split(r"[,]+", text)]
    return [piece for piece in pieces if tokenise(piece)]


# ---------------------------------------------------------------------------
# vocabulary
# ---------------------------------------------------------------------------

STEM_FLOOR = 6


class VocabEntry:
    """One of the two thousand words, with every key it can be matched by."""

    __slots__ = ("volume", "lesson", "ordinal", "headword", "forms", "pos",
                 "gloss_zh", "lemmas", "form_keys", "resolved", "phrase",
                 "headword_key", "credit_lemmas")

    def __init__(self, row: dict[str, Any], lemmas: set[str], form_keys: set[str]):
        self.volume = 1 if row.get("volume") == "上冊" else 2
        self.lesson = int(row["lesson"])
        self.ordinal = int(row["ordinal"])
        self.headword = row["headword"]
        self.forms = row.get("forms", "")
        self.pos = row.get("gram") or row.get("pos") or ""
        self.gloss_zh = row.get("glossZh", "")
        # ``in saecula``, ``grātiās agere``, ``aut . . aut``: a dozen entries
        # are phrases, and they must not be credited to the commonest word in
        # them.  Left alone, ``in saecula`` counts as practised by any sentence
        # containing ``in`` -- which is most of them -- and the twenty-word
        # coverage gate stops meaning anything.
        words = tokenise(self.headword.lstrip("-"))
        self.phrase = len(words) > 1
        self.headword_key = fold(words[0]) if len(words) == 1 else ""
        self.lemmas = set() if self.phrase else lemmas
        self.form_keys = form_keys
        self.resolved = bool(self.lemmas)
        # 🚨 同形異詞，拉丁版。`missa` 這條詞查形表會拿到兩個詞位——名詞
        # `missa`（彌撒）與動詞 `mitto` 的陰性完成分詞——於是「他差遣了」
        # 一句 `et misit in terram` 就把彌撒記成練到了。`festum` 會被人名
        # `Festus`（非斯都）記到，`nōn` 會被 `nonnullus` 記到。
        # 判準只有一條：折疊之後**等於詞頭本身**的詞位才算這一條詞。
        # `Angelus`→`angelus`、`Dominus`→`dominus` 只是大小寫，折疊後相等，
        # 照樣算；`mitto` vs `missa` 折疊後不等，擋掉。派生、詞源、專名變體
        # 一律不算——那是「同一個字根」，不是「同一個詞」。
        self.credit_lemmas = {
            lemma for lemma in self.lemmas if fold(lemma) == self.headword_key
        }

    @property
    def key(self) -> tuple[int, int]:
        return (self.volume, self.ordinal)

    @property
    def credit_keys(self) -> set[str]:
        """Written forms that may credit this entry when no lemma can.

        Used only where the lemma route is closed: the phrases, the Greek
        liturgical loans, and entries like ``ēlēctus``, ``optimus``, ``ait``
        and ``fore``, which teach one particular form of a word whose lemma is
        spelled differently.  Crediting those by lemma would mark ``optimus``
        practised by any ``bonus`` and ``fore`` by any ``est``.  Where a lemma
        does fit, it covers the inflections too and the form route adds
        nothing but a way to be wrong.
        """
        return set() if self.credit_lemmas else self.form_keys

    @property
    def written_keys(self) -> set[str]:
        """Exactly the forms this entry teaches, plus the corpus's spellings.

        A second credit route, tried after the lemma one and before the stem
        one.  The lemma route fails for a large part of this vocabulary —— not
        because the word is missing from the corpus but because the form there
        carries no lemma at all (``annuntio``, ``cœna``, ``Liturgia``) or
        carries another word's (``maior`` is lemmatised ``magnus``, ``missa``
        is lemmatised ``mitto``).  Ninety-one of the two thousand words were
        unreachable by lemma, and a coverage gate that demands all twenty words
        of a lesson cannot be met while any of them is unreachable.

        This route is safe where the derivation route was not.  What sank
        ``missa`` was reaching it through ``mitto``, so that ``et misit in
        terram`` practised 彌撒; here the written word has to be the taught form
        itself, and ``misit`` is not ``missa``.
        """
        keys: set[str] = set()
        for key in self.form_keys | ({self.headword_key} if self.headword_key else set()):
            keys |= spelling_variants(key)
        return keys

    @property
    def credit_stems(self) -> set[str]:
        """Prefixes long enough to credit an inflection the other routes miss.

        Third and last route.  ``annūntiō`` is in the corpus as
        ``annuntiavit`` with no lemma, and no principal part of it is written
        anywhere; only a stem reaches it.  The six-character floor is the one
        this series already learned to use: ``Χεβρὼν``'s five-letter stem
        ``chebr`` collided with a people and turned a place into them.  Four-
        and five-letter stems such as ``cena`` and ``missa`` therefore get no
        stem route at all, which is the intended trade —— they are exactly the
        short words whose prefixes belong to other words.
        """
        stems: set[str] = set()
        for key in self.written_keys:
            if len(key) >= STEM_FLOOR:
                stems.add(key)
        head = self.headword_key
        if head:
            # A verb is listed as its first person singular; its stem is what
            # is left when that ending comes off.
            for cut in (head[:-1], head[:-2]):
                if len(cut) >= STEM_FLOOR:
                    stems.add(cut)
        return stems

    def public_record(self) -> dict[str, Any]:
        return {
            "volume": self.volume,
            "lesson": self.lesson,
            "ordinal": self.ordinal,
            "headword": self.headword,
            "glossZh": self.gloss_zh,
            "lemmas": sorted(self.lemmas),
            "creditLemmas": sorted(self.credit_lemmas),
            "resolved": self.resolved,
            "phrase": self.phrase,
        }


ALT_SPLIT = re.compile(r"[,;()/]| \.\. | \. \. ")

# 課本的拼法與語料的拼法對不上時的詞首互換，逐條列出，不用規則。
#
# 與 `MEDIEVAL` 同一個道理，也同一個理由：想用一條 oe→e 一次解決，會連 coepi
# （開始）與 cepi（取得）都併成一個詞。差別只在 MEDIEVAL 對的是整個形，這裡
# 對的是**詞首**——課本教 cēna，克萊孟版每一個格都寫 cœ-，逐格列不完。
#
# 只換開頭、只換這幾條，兩個方向都認。每一條的驗證方式相同：那個拼法確實在
# 語料裡出現，而課本教的詞確實是同一個詞。
STEM_VARIANTS: tuple[tuple[str, str], ...] = (
    ("cen", "coen"),        # cēna／cēnāculum／cēnō，克萊孟版一律 cœ-
    ("cotidi", "quotidi"),  # cotidie／quotidie／cottidie 三種寫法並存
    ("cotidi", "cottidi"),
)


def spelling_variants(key: str) -> set[str]:
    """The folded keys this one may also be written as, itself included.

    Used by all three places that compare a written word with a taught one --
    the taught-words gate, the coverage credit and the reachability report --
    so that a word cannot be attested under one spelling and untaught under the
    other, which is a pair of conditions no sentence can satisfy at once.
    """
    out = {key}
    for left, right in STEM_VARIANTS:
        if key.startswith(left):
            out.add(right + key[len(left):])
        if key.startswith(right):
            out.add(left + key[len(right):])
    return out


def vocabulary_key_order(row: dict[str, Any]) -> list[str]:
    """Folded keys a vocabulary entry may legitimately be written as, in order.

    The headword carries macrons the corpus never prints (``ōrdō``), some
    entries are phrases (``grātiās agere``), some are bound stems (``-pleō``),
    and the ``forms`` field lists the principal parts.  All of them fold down
    to keys a corpus token can equal.

    Two kinds of thing in the ``forms`` field are not words and must not become
    keys.  ``ēlēctus, -a, -um`` lists adjective endings, and ``liturgia,
    liturgiae, f.`` names a gender.  Taken as words they made ``contrītus``
    resolve to the lemmas of ``a`` -- ``ad``, ``ab``, ``hic`` -- and
    ``liturgia`` resolve to the lemma ``f``.  A piece that opens with a hyphen
    is an ending; a one-letter piece of the ``forms`` field is an abbreviation.
    The headword's own letters are always kept, because ``ā`` and ``ē`` are
    one-letter words.

    Order matters: the caller walks these looking for the first that a treebank
    knows, and alphabetical order put the gender abbreviation first.
    """
    keys: list[str] = []

    def add(word: str) -> None:
        key = fold(word)
        if key and key not in keys:
            keys.append(key)

    for word in tokenise(row["headword"]):
        add(word)
    for piece in ALT_SPLIT.split(row.get("forms", "")):
        piece = piece.strip()
        if not piece or piece.startswith("-"):
            continue
        for word in tokenise(piece):
            if len(word) > 1:
                add(word)
    return keys


def vocabulary_keys(row: dict[str, Any]) -> set[str]:
    return set(vocabulary_key_order(row))


def load_vocabulary(path: Path = VOCABULARY, tagger: "Tagger | None" = None) -> list[VocabEntry]:
    """The two thousand lesson words, each pointed at the lemmas it can wear.

    ``treebankLemma`` is authoritative where the vocabulary file carries it --
    the lower volume's corpus-derived half does.  For the rest the headword is
    folded and looked up; a headword that is a phrase or a Greek liturgical
    loan (``Kyrie``, ``eléison``) resolves to no lemma at all and says so, so
    that coverage counted later is not quietly counted against a word the
    corpus cannot express.
    """
    rows = json.loads(path.read_text(encoding="utf-8"))["entries"]
    entries: list[VocabEntry] = []
    for row in rows:
        order = vocabulary_key_order(row)
        lemmas: set[str] = set()
        stated = row.get("treebankLemma")
        if stated:
            lemmas.add(stated)
        if tagger is not None and order:
            head_key = order[0]
            lemmas |= tagger.lemmas_for_headword(head_key)
            lemmas |= tagger.lemmas_for_key(head_key)
            if not lemmas:
                # In the order the entry writes them -- headword, then the
                # principal parts left to right.  Alphabetical order tried the
                # gender abbreviation first and resolved ``liturgia`` to the
                # lemma ``f``.
                for key in order[1:]:
                    lemmas |= tagger.lemmas_for_headword(key) | tagger.lemmas_for_key(key)
                    if lemmas:
                        break
        entries.append(VocabEntry(row, lemmas, set(order)))
    return entries


APPENDIX_TITLES = {
    "names": "專名（武加大）",
    "modernNames": "近現代專名",
    "numerals": "數字與度量衡",
    "kinship": "親屬稱謂",
    "calendar": "曆法與節期",
    "offices": "教會職分",
    "liturgical_year": "禮儀年",
    "documents": "文獻體裁",
    "scholastic": "經院術語",
}


def appendix_keys(path: Path = READER, volume: int = 1) -> dict[str, set[str]]:
    """Folded keys of everything the appendices teach outside the lesson slots.

    The contract for this reader says proper names are "appendix only; never a
    lesson slot", and the same is true of the numerals, the kinship table and
    the calendar.  A sentence built out of the lessons would therefore be
    rejected the moment it named Abraham, which is not what "no unknown words"
    is supposed to mean.  So the appendices count as taught -- and which
    appendix vouched for a word is kept, so a gate's report can say so.

    ``volume`` 2 inherits volume 1's appendices, the way its lessons inherit
    volume 1's vocabulary.
    """
    reader = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, set[str]] = {}
    for block in reader["volumes"]:
        if block["volume"] > volume:
            continue
        for name, table in block.get("appendices", {}).items():
            if name == "principalParts":
                continue  # the verbs themselves are lesson words already
            keys = out.setdefault(name, set())
            for row in table.get("entries", []):
                stated = row.get("folded")
                if stated:
                    keys.add(stated)
                for field in ("headword", "forms", "latin"):
                    for word in tokenise(str(row.get(field) or "")):
                        key = fold(word)
                        if key:
                            keys.add(key)
    return out


def cumulative_stems(
    entries: Sequence[VocabEntry], volume: int, lesson: int
) -> set[str]:
    """Stems of everything taught by this lesson, for the taught-words gate.

    The third route on the taught side, and it is asked only of a form the
    corpus gives no lemma at all.  ``collaudate`` is such a form: ``collaudō``
    is this lesson's word, the Vulgate writes the imperative, and nothing links
    the two -- so the gate called a correct sentence untaught.  Restricting the
    route to lemma-less forms keeps it from quietly admitting derivations where
    the lemma layer can actually speak.
    """
    return {
        stem
        for entry in entries
        if entry.volume < volume or (entry.volume == volume and entry.lesson <= lesson)
        for stem in entry.credit_stems
    }


def cumulative_vocabulary(
    entries: Sequence[VocabEntry], volume: int, lesson: int
) -> tuple[list[VocabEntry], set[str], set[str]]:
    """This lesson's twenty words, and everything taught up to and including it.

    The lower volume continues the upper one: a reader at volume two lesson
    three has met all thousand words of volume one.
    """
    taught = [
        entry
        for entry in entries
        if entry.volume < volume or (entry.volume == volume and entry.lesson <= lesson)
    ]
    target = [
        entry for entry in entries if entry.volume == volume and entry.lesson == lesson
    ]
    lemmas = {lemma for entry in taught for lemma in entry.lemmas}
    # ``written_keys`` rather than ``form_keys``: a word is taught in the
    # textbook's spelling and written in the corpus's, and a sentence that uses
    # the corpus's spelling of a word the lesson taught is not using an untaught
    # word.  Without this the gate accepted ``cœnam`` as attested and refused it
    # as never taught, which no sentence can satisfy at once.
    keys = {key for entry in taught for key in entry.written_keys}
    return target, lemmas, keys


# ---------------------------------------------------------------------------
# the tagger
# ---------------------------------------------------------------------------

def read_conllu(directory: Path) -> Iterator[list[str]]:
    for path in sorted(directory.glob("*.conllu")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line or line.startswith("#"):
                continue
            cols = line.split("\t")
            if len(cols) < 10 or "-" in cols[0] or "." in cols[0]:
                continue
            yield cols


class Tagger:
    """Assigns a lemma and records which layer gave it."""

    def __init__(self, gold: Sequence[str] = ("proiel",), with_refs: bool = True):
        self.gold_names = list(gold)
        self.type_index: dict[str, set[str]] = defaultdict(set)
        self.type_source: dict[str, str] = {}
        self.lemma_pos: dict[str, str] = {}
        self.proper: set[str] = set()
        self.gold_ref: dict[str, dict[str, str]] = defaultdict(dict)
        for name in self.gold_names:
            self._read_treebank(name, with_refs=with_refs and name == "proiel")
        lexicon = json.loads(LEXICON.read_text(encoding="utf-8"))
        vulgate = json.loads(VULGATE_LEXICON.read_text(encoding="utf-8"))
        # The Vulgate table wins where the two disagree: this reader's first
        # volume prints the Vulgate, so its reading of an ambiguous form is
        # the one the learner will meet.
        self.exact: dict[str, str] = {**lexicon["exactForms"], **vulgate["exactForms"]}
        self.folded: dict[str, str] = {**lexicon["foldedForms"], **vulgate["foldedForms"]}
        for table in (lexicon.get("pos", {}), vulgate.get("pos", {})):
            for lemma, tag in table.items():
                self.lemma_pos.setdefault(lemma, tag)
        self.proper |= {fold(name) for name in lexicon.get("properNames", [])}
        self.proper |= {fold(name) for name in vulgate.get("properNames", [])}
        self.attested: set[str] = set(self.folded) | {fold(k) for k in self.exact}
        self.attested |= set(self.type_index)
        self.lemma_by_fold: dict[str, set[str]] = defaultdict(set)
        for lemma in set(self.lemma_pos) | set(self.exact.values()) | set(self.folded.values()):
            self.lemma_by_fold[fold(lemma)].add(lemma)

    def _read_treebank(self, name: str, with_refs: bool) -> None:
        directory = TREEBANKS[name]
        if not directory.exists():
            raise SystemExit(f"樹庫缺檔：{directory}")
        for cols in read_conllu(directory):
            form, lemma, upos, misc = cols[1], cols[2], cols[3], cols[9]
            key = fold(form)
            if not key:
                continue
            self.type_index[key].add(lemma)
            self.type_source.setdefault(key, name)
            self.lemma_pos.setdefault(lemma, upos)
            if upos == "PROPN":
                self.proper.add(key)
            if not with_refs:
                continue
            found = REF_RE.search(misc)
            if found and found.group(1) in PROIEL_BOOK:
                ref = f"{PROIEL_BOOK[found.group(1)]}.{int(found.group(2))}.{int(found.group(3))}"
                self.gold_ref[ref].setdefault(key, lemma)

    # -- lookups ----------------------------------------------------------
    def lemmas_for_key(self, key: str) -> set[str]:
        """Every lemma a folded form is known to carry, gold first."""
        if key in self.type_index:
            return set(self.type_index[key])
        if key in self.folded:
            return {self.folded[key]}
        found = next((self.exact[k] for k in (key,) if k in self.exact), None)
        return {found} if found else set()

    def lemmas_for_headword(self, key: str) -> set[str]:
        """Lemmas whose own spelling is this key -- for reading a vocabulary list.

        Separate from ``lemmas_for_key`` because the two ask different
        questions.  A corpus token is looked up among *forms*; a headword is a
        *lemma*, and a lemma need not appear in the corpus in its citation
        form.  ``collaudo``, ``exsulto``, ``corrigo`` are all in the lexicon as
        lemmas and none of them is ever written as a first-person singular
        present, so looking them up among forms lost them.
        """
        found = self.lemma_by_fold.get(key)
        return set(found) if found else set()

    def is_proper(self, key: str) -> bool:
        return key in self.proper

    def is_verbal(self, lemmas: Iterable[str]) -> bool:
        """Does any reading of this word make it a verb?

        The test a mined fragment has to pass before it may be printed as a
        sentence.  Asked of every reading, not the chosen one, because the
        chosen one is a guess where a form is ambiguous and the question here
        is only whether a predicate is possible.
        """
        return any(self.lemma_pos.get(lemma) in {"VERB", "AUX"} for lemma in lemmas)

    def tag(self, surface: str, ref: str | None = None) -> dict[str, Any]:
        """One written word -> lemma, layer, route, and any enclitic cut off."""
        key = fold(surface)
        gold = self.gold_ref.get(ref, {}) if ref else {}
        if key in gold:
            return self._record(surface, gold[key], "gold", "proiel-ref", "")
        types = self.type_index.get(key)
        if types and len(types) == 1:
            return self._record(surface, next(iter(types)), "gold", "treebank-type", "")
        if surface in self.exact:
            return self._record(surface, self.exact[surface], "form", "lexicon-exactForms", "",
                                ambiguous=bool(types and len(types) > 1))
        if key in self.folded:
            return self._record(surface, self.folded[key], "form", "lexicon-foldedForms", "",
                                ambiguous=bool(types and len(types) > 1))
        cut = split_enclitic(surface, self.attested)
        if cut:
            host, clitic = cut
            host_types = self.type_index.get(host)
            lemma = (
                next(iter(host_types)) if host_types and len(host_types) == 1
                else self.folded.get(host)
            )
            if lemma:
                return self._record(surface, lemma, "form", "enclitic-split", clitic)
        bridged = bridge_spelling(key, self.folded)
        if bridged:
            return self._record(surface, bridged, "form", "spelling-bridge", "")
        return self._record(surface, "", "unknown", "unresolved", "")

    @staticmethod
    def _record(surface: str, lemma: str, layer: str, via: str, enclitic: str,
                ambiguous: bool = False) -> dict[str, Any]:
        return {
            "surface": surface,
            "lemma": lemma,
            "layer": layer,
            "via": via,
            "enclitic": enclitic,
            "ambiguous": ambiguous,
        }

    def lemma_set(self, token: dict[str, Any]) -> set[str]:
        """Every lemma the token might be, for gates that must not over-reject.

        A form two lemmas share -- the Hebrew reader was bitten by exactly this
        with ``כָּבֵד`` -- passes the taught-words gate if either lemma has been
        taught, and the ambiguity is reported rather than resolved here.
        """
        key = fold(token["surface"])
        lemmas = set(self.type_index.get(key, ()))
        if token["lemma"]:
            lemmas.add(token["lemma"])
        if token["enclitic"]:
            lemmas.add(token["enclitic"])
        return lemmas


# ---------------------------------------------------------------------------
# corpora
# ---------------------------------------------------------------------------

def vulgate_units() -> list[dict[str, Any]]:
    """Every verse of the Clementine text, footnotes already dropped."""
    units: list[dict[str, Any]] = []
    for ref, text in L.vulgate_verses().items():
        book, chapter, verse = ref.split(".")
        units.append(
            {
                "id": ref,
                "ref": ref,
                "book": book,
                "chapter": int(chapter),
                "verse": int(verse),
                "text": text,
            }
        )
    return units


def church_units() -> list[dict[str, Any]]:
    """The lower volume's fifty readings, exactly as the reader prints them.

    Not the whole Latin Library cache: what belongs in this corpus is the text
    the learner will actually meet, which is the excerpt the reading plan cut,
    and which already carries its Chinese block by block.
    """
    reader = json.loads(READER.read_text(encoding="utf-8"))
    lower = next(volume for volume in reader["volumes"] if volume["volume"] == 2)
    units: list[dict[str, Any]] = []
    for lesson in lower["lessons"]:
        for index, block in enumerate(lesson.get("reading", []), start=1):
            latin = (block.get("latin") or "").strip()
            if not latin:
                continue
            units.append(
                {
                    "id": f"L{lesson['lesson']:02d}#{index}",
                    "ref": lesson["title"],
                    "lesson": lesson["lesson"],
                    "block": index,
                    "blockCount": len(lesson["reading"]),
                    "text": latin,
                    "chinese": (block.get("zh") or "").strip(),
                }
            )
    return units


def tag_units(units: Sequence[dict[str, Any]], tagger: Tagger, use_ref: bool) -> dict[str, Any]:
    layers: Counter[str] = Counter()
    routes: Counter[str] = Counter()
    ambiguous = 0
    unknown_forms: Counter[str] = Counter()
    form_index: dict[str, dict[str, Any]] = {}
    out: list[dict[str, Any]] = []
    for unit in units:
        rows: list[list[str]] = []
        for surface in tokenise(unit["text"]):
            token = tagger.tag(surface, unit.get("ref") if use_ref else None)
            layers[token["layer"]] += 1
            routes[token["via"]] += 1
            ambiguous += 1 if token["ambiguous"] else 0
            if token["layer"] == "unknown":
                unknown_forms[surface] += 1
            key = fold(surface)
            slot = form_index.setdefault(key, {"count": 0, "surfaces": [], "lemmas": []})
            slot["count"] += 1
            if surface not in slot["surfaces"] and len(slot["surfaces"]) < 6:
                slot["surfaces"].append(surface)
            if token["lemma"] and token["lemma"] not in slot["lemmas"]:
                slot["lemmas"].append(token["lemma"])
            rows.append(
                [
                    surface,
                    token["lemma"],
                    LAYER_CODE[token["layer"]],
                    VIA_CODE[token["via"]],
                    token["enclitic"],
                ]
            )
        out.append({**unit, "tokens": rows})
    return {
        "units": out,
        "layers": dict(layers),
        "routes": dict(routes),
        "ambiguous": ambiguous,
        "unknownForms": unknown_forms,
        "formIndex": form_index,
    }


def build(corpus: str, tagger: Tagger) -> dict[str, Any]:
    if corpus == "vulgate":
        units = vulgate_units()
        source = {
            "edition": "eBible.org latVUC, Clementine Vulgate (USFX)",
            "note": "Glossa Ordinaria footnotes dropped before any verse was recorded.",
            "gold": "UD_Latin-PROIEL, Jerome's Vulgate sentences (New Testament only)",
        }
        tagged = tag_units(units, tagger, use_ref=True)
    else:
        units = church_units()
        source = {
            "edition": "latin-reader-two-volumes.json 下冊五十篇讀物（The Latin Library／repo 拉中對照）",
            "note": "讀物即下冊實際印出的節錄，中文逐段已附。",
            "gold": "UD_Latin-PROIEL + ITTB + LLCT，僅型別層（教會文獻無逐節對位）",
        }
        tagged = tag_units(units, tagger, use_ref=False)
    tokens = sum(tagged["layers"].values())
    payload = {
        "schemaVersion": "1.0.0",
        "corpus": corpus,
        "generatedOn": date.today().isoformat(),
        "source": source,
        "goldTreebanks": tagger.gold_names,
        "tokenFields": TOKEN_FIELDS,
        "layerLegend": {code: name for name, code in LAYER_CODE.items()},
        "viaLegend": {code: name for name, code in VIA_CODE.items()},
        "counts": {
            "units": len(tagged["units"]),
            "tokens": tokens,
            "layers": tagged["layers"],
            "routes": tagged["routes"],
            "ambiguousForms": tagged["ambiguous"],
            "distinctForms": len(tagged["formIndex"]),
            "distinctUnknownForms": len(tagged["unknownForms"]),
        },
        "topUnknownForms": [
            {"surface": surface, "count": count}
            for surface, count in tagged["unknownForms"].most_common(40)
        ],
        "formIndex": tagged["formIndex"],
        "units": tagged["units"],
    }
    return payload


def report(payload: dict[str, Any]) -> None:
    counts = payload["counts"]
    tokens = counts["tokens"] or 1
    print(f"語料 {payload['corpus']}：{counts['units']} 單元，{counts['tokens']} token")
    for layer in ("gold", "form", "unknown"):
        n = counts["layers"].get(layer, 0)
        print(f"  {layer:8s} {n:7d}  {n / tokens:6.2%}")
    for via, n in sorted(counts["routes"].items(), key=lambda row: -row[1]):
        print(f"    ├ {via:20s} {n:7d}")
    print(f"  同形異詞（型別層有兩個以上詞位）{counts['ambiguousForms']} token")
    print(f"  不同字形 {counts['distinctForms']}，其中查無詞位 {counts['distinctUnknownForms']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", choices=["vulgate", "church", "both"], default="both")
    parser.add_argument("--write", action="store_true", help="寫出 lemma-corpus-*.json")
    args = parser.parse_args()

    targets = ["vulgate", "church"] if args.corpus == "both" else [args.corpus]
    for corpus in targets:
        gold = ("proiel",) if corpus == "vulgate" else ("proiel", "ittb", "llct")
        tagger = Tagger(gold=gold, with_refs=True)
        payload = build(corpus, tagger)
        report(payload)
        if args.write:
            path = OUTPUT[corpus]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            size = path.stat().st_size / 1_048_576
            print(f"  寫入 {path.relative_to(ROOT)}（{size:.1f} MB）")


if __name__ == "__main__":
    main()
