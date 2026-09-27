#!/usr/bin/env python3
"""Check the seven composed sentences of a Latin lesson against the corpus.

The Latin counterpart of ``compose_hebrew_sentences.py``, and deliberately the
same three gates, because the specification is one specification for four
readers:

1. every written form must actually occur in the corpus this volume draws on --
   the Clementine Vulgate for the upper volume, the fifty church readings as
   well for the lower one.  An inflection nobody wrote is refused;
2. every word must already have been taught -- this lesson's twenty, every
   earlier lesson's, and the appendices, which is where this reader puts the
   proper names, the numerals, the kinship terms and the calendar;
3. the ten items of a lesson must between them use all twenty of its words.

What the gates cannot certify is syntax and sense.  A sentence that passes is
machine-checked, not correct, and the owner reads every one.

Latin's own traps, none of which the Hebrew gate had to meet:

* **Enclitics.** ``armaque`` is ``arma`` plus ``que``; ``itaque`` is not
  ``ita`` plus ``que``.  Nothing in the letters distinguishes them, so the
  decision is the dictionary's: a form that is itself a word is never cut.
  The Hebrew gate had the mirror image of this bug -- ``אֶת־הָאָדָם`` is two
  words written as one, and not splitting it failed whole correct sentences.
* **Orthography.** ``cælum``/``caelum``, ``ejus``/``eius``, ``uidit``/``vidit``
  are one word in three dresses.  All comparison happens on a folded key.
* **Printing.** Folding is for comparison only.  Everything this script prints
  back -- the sentence, the rejected word, the corpus's own spelling of it --
  is the original, ligatures and all.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

from pathlib import Path
from typing import Any, Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_latin_lemma_corpus import (  # noqa: E402
    OUTPUT as CORPUS_FILES,
    cumulative_stems,
    spelling_variants,

    Tagger,
    appendix_keys,
    cumulative_vocabulary,
    fold,
    load_vocabulary,
    split_enclitic,
    tokenise,
)

CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
COMPOSED = CACHE / "composed-sentences.json"

# 擁有者 2026-09-16 的裁定：**「已教過」不再是退回的理由**。
# 「按照程度來看，簡單的都可以先練習，沒有限制一定要本課教過的才行。」
# 一個詞排在第幾課是難度排序的結果，不是它本身難不難；把課次當成硬牆，會讓
# 一課的二十個詞裡有幾個永遠寫不進任何句子（拉丁 86、希臘 6、日文 34），
# 而那些缺口補不起來的理由是排序，不是語言。
#
# 這一關沒有刪掉，只是不再擋人：`untaught` 仍照實記錄哪些詞超出本課進度，
# 供日後要標注或分級時取用；`passed` 不再看它。語料那一關（第一道）沒有動——
# 捏一個語料裡不存在的形，仍然是錯的。
MIN_WORDS = 3
MAX_WORDS = 8
ITEMS_PER_LESSON = 10


class Corpus:
    """The attested forms of one or more tagged corpora, folded for lookup."""

    def __init__(self, names: Sequence[str]):
        self.names = list(names)
        self.forms: dict[str, dict[str, Any]] = {}
        self.units: dict[str, int] = {}
        for name in self.names:
            path = CORPUS_FILES[name]
            if not path.exists():
                raise SystemExit(
                    f"缺 {path.name}，先跑 scripts/build_latin_lemma_corpus.py --write"
                )
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.units[name] = payload["counts"]["units"]
            for key, row in payload["formIndex"].items():
                slot = self.forms.setdefault(key, {"count": 0, "surfaces": [], "lemmas": []})
                slot["count"] += row["count"]
                for surface in row["surfaces"]:
                    if surface not in slot["surfaces"]:
                        slot["surfaces"].append(surface)
                for lemma in row["lemmas"]:
                    if lemma not in slot["lemmas"]:
                        slot["lemmas"].append(lemma)

    @property
    def keys(self) -> set[str]:
        return set(self.forms)

    def attested(self, key: str) -> bool:
        return key in self.forms

    def spelling(self, key: str) -> str:
        """How the corpus itself writes this form -- for the report, verbatim."""
        row = self.forms.get(key)
        return row["surfaces"][0] if row and row["surfaces"] else ""

    def lemmas(self, key: str) -> set[str]:
        row = self.forms.get(key)
        return set(row["lemmas"]) if row else set()


def word_reading(word: str, corpus: Corpus, tagger: Tagger) -> dict[str, Any]:
    """Resolve one written word into the one or two words it actually spells.

    ``parts`` is why this returns a list rather than a lemma: ``armaque`` is two
    words and the taught-words gate has to hold for both of them.  Checking the
    pair together would let the enclitic vouch for its host -- ``-que`` is
    taught in lesson one, so every noun in Latin would pass from lesson one
    onward as long as it had ``que`` stuck to it.
    """
    key = fold(word)
    if corpus.attested(key):
        parts = [{
            "key": key,
            "lemmas": corpus.lemmas(key) | tagger.lemmas_for_key(key),
            "spelling": corpus.spelling(key),
        }]
        return {"word": word, "key": key, "attested": True, "enclitic": "", "parts": parts}
    cut = split_enclitic(word, corpus.keys, whole=corpus.keys | tagger.attested)
    if cut:
        host, clitic = cut
        parts = [
            {
                "key": host,
                "lemmas": corpus.lemmas(host) | tagger.lemmas_for_key(host),
                "spelling": corpus.spelling(host),
            },
            {"key": clitic, "lemmas": {clitic}, "spelling": clitic},
        ]
        return {"word": word, "key": key, "attested": True, "enclitic": clitic, "parts": parts}
    return {"word": word, "key": key, "attested": False, "enclitic": "", "parts": []}


def part_is_taught(
    part: dict[str, Any],
    taught_lemmas: set[str],
    taught_keys: set[str],
    taught_stems: Iterable[str] = (),
) -> bool:
    # The spelling variants are asked only after the plain comparison fails:
    # the corpus writes ``cœnam`` for a word the textbook teaches as ``cēna``,
    # and without this the gate calls that form attested and untaught at once --
    # a pair no sentence can satisfy.
    if part["lemmas"] & taught_lemmas:
        return True
    if part["key"] in taught_keys:
        return True
    if spelling_variants(part["key"]) & taught_keys:
        return True
    # Last, and only for a form the corpus gives no lemma at all: ``collaudate``
    # is an inflection of this lesson's own ``collaudō`` that nothing in the
    # corpus links back to it.  Where a lemma exists this route stays shut, so
    # it cannot quietly admit a derivation of a taught word as taught.
    if not part["lemmas"]:
        return any(part["key"].startswith(stem) for stem in taught_stems)
    return False


def _looks_like_verb_entry(entry: Any) -> bool:
    """A crude POS test read from the vocabulary's own ``forms`` field.

    This vocabulary carries no clean part-of-speech column for verbs (``gram``
    is filled in for prepositions, conjunctions, adverbs… and left blank for
    nouns and verbs alike). But a verb's second principal part is always its
    infinitive, and nothing else in this vocabulary's ``forms`` field ends
    that way: ``flectō, flectere, flexī, flexus`` / ``cōnor, cōnārī, —,
    cōnātus sum``. Good enough to separate "this headword is a verb" from
    "this headword is not", which is all the fallback below needs.
    """
    pieces = [p.strip() for p in re.split(r"[,;]", getattr(entry, "forms", "") or "") if p.strip()]
    if len(pieces) < 2:
        return False
    inf = fold(pieces[1])
    return inf.endswith("re") or inf.endswith("ri")


def verb_stems_of(entries: Iterable[Any]) -> set[str]:
    """Stems of every verb-looking entry, for the predicate gate's fallback.

    Built once per run and passed into ``verify``/``has_predicate``.
    """
    stems: set[str] = set()
    for entry in entries:
        if _looks_like_verb_entry(entry):
            stems |= getattr(entry, "credit_stems", set())
    return stems


def has_predicate(
    readings: Sequence[dict[str, Any]],
    tagger: Tagger,
    verb_stems: Iterable[str] | None = None,
) -> bool:
    """Does the sentence carry at least one finite verb (2026-09-27 gate)?

    Added after the 2026-09-25 grammar review: 404 of 720 composed sentences
    were severe, and the largest single category was word-heaps with no
    predicate at all -- three or four nouns and adverbs in different cases,
    readable as nothing.  ``est``/``sunt`` themselves are ordinary finite verbs
    in the treebanks, so a noun sentence with an explicit copula already
    satisfies this without any special case for it; what this catches is the
    noun-phrase-as-sentence the report calls out.

    Checked first against ``Tagger.finite_keys``, which is blind to context
    the same way ``is_verbal`` already is -- a form ambiguous between finite
    and non-finite counts as having a predicate if any treebank occurrence
    tagged it finite.

    ``verb_stems`` is a second, narrower route for a form the six treebanks
    never saw at all: ``collaudāte`` is imperative plural of this reader's own
    ``collaudō`` and is attested in the Vulgate/church corpus, but has zero
    occurrences in any UD Latin treebank, so ``finite_keys`` has no evidence
    for it one way or the other. Falling back to "this word's stem belongs to
    a vocabulary entry whose forms field is a verb's" only fires when the word
    carries **no lemma at all** (a treebank that had seen the form even once,
    tagged as a participle or infinitive, would have given it one, and that
    lemma-bearing case is deliberately left to the strict route only) -- so it
    cannot turn a real infinitive or participle into a false predicate.
    """
    for row in readings:
        for part in row["parts"]:
            if tagger.is_finite_key(part["key"]):
                return True
            if not part["lemmas"] and verb_stems:
                if any(part["key"].startswith(stem) for stem in verb_stems):
                    return True
    return False


def person_number_conflict(
    readings: Sequence[dict[str, Any]], tagger: Tagger
) -> tuple[list[str], list[str]]:
    """Finite verbs in one sentence whose person/number cannot agree.

    A proxy for "two verbs must share a subject" (2026-09-25 review, §2): most
    of the ``et``-spliced pairs the review flagged as ungrammatical turn out to
    disagree in person or number -- ``perfecisti et pervenit`` (2sg + 3sg),
    ``collegerunt et descripsit`` (3pl + 3sg).  Only raised when every finite
    verb in the sentence has *known* person/number evidence and their sets
    share nothing in common; a form attested only via the lexicon tables (no
    treebank occurrence, hence no feature evidence) is silently excused rather
    than treated as a mismatch, because absence of evidence is not evidence of
    disagreement.

    Returns two lists, not one: *all* conflicting keys (reported always), and
    the subset actually treated as an error. A bare 3rd-vs-3rd mismatch --
    ``Dominus verbum tradidit et discipuli receperunt`` -- is completely
    ordinary Latin: two different, explicitly named subjects, each with its
    own verb. Latin has no other way to say that, and this checker cannot
    parse which noun goes with which verb, so it cannot tell that case apart
    from a genuine dangling ``et``-splice by number alone. Person 1 or 2 is
    different: those persons have no noun to name them (nothing reads
    "Petrus" as filling in for "I"), so ``incipiam et resurget`` (1sg + 3sg)
    with no first-person noun anywhere is not a reading choice, it is a
    contradiction. Blocking is therefore narrowed to a mismatch that involves
    person 1 or 2; a 3rd-vs-3rd number clash is still recorded so the note
    field can say why coverage looks the way it does, but does not fail the
    sentence on its own.
    """
    finite_keys = [
        part["key"]
        for row in readings
        for part in row["parts"]
        if tagger.is_finite_key(part["key"])
    ]
    pn_sets = [tagger.person_number_for(key) for key in finite_keys]
    known = [(key, pn) for key, pn in zip(finite_keys, pn_sets) if pn]
    if len(known) < 2:
        return [], []
    common: set[tuple[str, str]] | None = None
    for _, pn in known:
        common = pn if common is None else (common & pn)
    if common:
        return [], []
    all_conflicts = [key for key, _ in known]
    involves_1_or_2 = any(
        person in {"1", "2"} for _, pn in known for person, _ in pn
    )
    return all_conflicts, (all_conflicts if involves_1_or_2 else [])


def target_mismatch(
    readings: Sequence[dict[str, Any]],
    targets: Iterable[str],
    entries_by_headword: dict[str, list[Any]] | None,
) -> list[str]:
    """Declared ``targets`` whose headword no word in the sentence actually is.

    2026-09-25 review, §5: ``ne fugerem`` is a form of ``fugiō`` (flee), and the
    draft declared it practised ``fugō`` (drive out) -- attested, taught, and
    simply the wrong verb.  Nothing upstream checks the draft's own claim about
    itself; ``practised()`` recomputes coverage independently for the printed
    book, but a human or model reading only the ``targets`` field would never
    see the mismatch.  This reads the same ``credit_lemmas``/``credit_keys``
    rule the coverage gate uses, so a target only ever counts as matched for
    the reason the book would also count it matched.
    """
    if not entries_by_headword:
        return []
    seen_lemmas: set[str] = set()
    seen_keys: set[str] = set()
    for row in readings:
        for part in row["parts"]:
            seen_lemmas |= part["lemmas"]
            seen_keys.add(part["key"])
    bad: list[str] = []
    for target in targets:
        key = fold(target)
        candidates = entries_by_headword.get(key)
        if not candidates:
            continue  # not a recognised headword (phrase piece, enclitic, "et" …): nothing to check
        matched = False
        for entry in candidates:
            if getattr(entry, "phrase", False):
                if entry.credit_keys <= seen_keys:
                    matched = True
                    break
                continue
            # Lemma route, then the entry's own written forms -- never the stem
            # route. The stem route is exactly what let ``speciosum`` credit
            # ``speciō`` and ``triumphabit`` credit ``triumphus`` in the vocabulary
            # build: both share a six-letter prefix with a derived word that is
            # not them. ``practised()`` keeps that fallback because some words
            # are only reachable through it; a target declaration has no such
            # excuse -- the author is claiming a specific word was used, and a
            # prefix match is not evidence of that.
            if entry.credit_lemmas & seen_lemmas:
                matched = True
                break
            if entry.written_keys & seen_keys:
                matched = True
                break
        if not matched:
            bad.append(target)
    return bad


# 全書字例統一的正字法：ae→æ、oe→œ 連字，字首 i+母音→j（Iesus→Jesus、
# Ianuarii→Januarii），少數前綴＋iacio/iungo 族複合詞的詞中 i→j
# （obiectum→objectum、adiectivum→adjectivum、coniunctio→conjunctio）。
# 只處理這份報告列出、確認安全的形——見 references/latin-reader-contract.md
# 對 STEM_VARIANTS 的同一警告：規則寫太寬會連好字都吃掉。
_AE_RE = re.compile(r"ae", re.IGNORECASE)
_OE_RE = re.compile(r"oe", re.IGNORECASE)
_INITIAL_J_RE = re.compile(r"^([Ii])([aeiouyAEIOUY])")
_MIDWORD_J_RE = re.compile(
    r"(?<=[bcdfgklmnpqrstvxzBCDFGKLMNPQRSTVXZ])([Ii])(?=(?:ect|ic|unct|ung|unx))"
)


def _swap_ae_oe(word: str) -> str:
    def ae(match: "re.Match[str]") -> str:
        return "Æ" if match.group(0)[0].isupper() else "æ"

    def oe(match: "re.Match[str]") -> str:
        return "Œ" if match.group(0)[0].isupper() else "œ"

    word = _AE_RE.sub(ae, word)
    word = _OE_RE.sub(oe, word)
    return word


def _swap_j(word: str) -> str:
    def to_j(match: "re.Match[str]") -> str:
        return "J" if match.group(1) == "I" else "j"

    word = _INITIAL_J_RE.sub(lambda m: to_j(m) + m.group(2), word)
    word = _MIDWORD_J_RE.sub(to_j, word)
    return word


def normalize_orthography(sentence: str, tagger: Tagger) -> str:
    """Print form: æ/œ ligatures, j for consonantal i, mid-sentence lowercase.

    2026-09-25 review, §6: about eighty of the 720 composed sentences printed
    ``ae``/``i`` where the rest of the book prints ``æ``/``j``, or carried a
    capital the corpus happened to print (``Ascendit et Descendit`` mid-
    sentence).  「句中非專名一律小寫」: every word but the first and any
    proper name keeps whatever case ``normalize`` gives it; the sentence-
    initial word is capitalised regardless of what the corpus wrote, and every
    other non-proper word is lowercased.  Comparison against the corpus is
    unaffected because ``fold()`` already collapses all of ae/æ, oe/œ, i/j and
    case -- this only changes what gets printed, never what gets checked.
    """
    words = tokenise(sentence)
    if not words:
        return sentence
    out: list[str] = []
    for index, word in enumerate(words):
        spelled = _swap_j(_swap_ae_oe(word))
        if index == 0:
            spelled = spelled[:1].upper() + spelled[1:] if spelled else spelled
        elif not tagger.is_proper(fold(word)):
            spelled = spelled.lower()
        out.append(spelled)
    # Re-assemble keeping the original punctuation/whitespace skeleton: replace
    # words positionally in the original string rather than joining with plain
    # spaces, so a sentence ending "…familia." keeps its full stop.
    result = sentence
    for original, replacement in zip(words, out):
        if original == replacement:
            continue
        result = re.sub(re.escape(original), replacement, result, count=1)
    return result


def verify(
    sentence: str,
    corpus: Corpus,
    tagger: Tagger,
    taught_lemmas: set[str],
    taught_keys: set[str],
    taught_stems: Iterable[str] = (),
    targets: Iterable[str] | None = None,
    entries_by_headword: dict[str, list[Any]] | None = None,
    verb_stems: Iterable[str] | None = None,
    check_predicate: bool = True,
) -> dict[str, Any]:
    """Gates one and two, on one sentence.  Everything reported is verbatim.

    ``check_predicate`` gates the 2026-09-27 additions (predicate presence,
    person/number agreement) and defaults on for the composed sentences these
    were written for. A quoted anchor is a fragment of real Vulgate or
    church Latin cut by ``build_latin_exercises.py`` at a clause boundary,
    and a periodic sentence's subordinate clauses are routinely a
    participial or prepositional phrase with no finite verb of their own --
    grammatical in context, not a defect to flag. Turning the same checks on
    quoted items in the lower volume rejected the *majority* of its mined
    anchors this way, which is a real finding about the anchor miner, not
    something this composed-sentence gate should silently paper over by
    reporting the anchor as failing.
    """
    words = tokenise(sentence)
    readings = [word_reading(word, corpus, tagger) for word in words]
    unattested = [row["word"] for row in readings if not row["attested"]]
    untaught: list[str] = []
    for row in readings:
        if not row["attested"]:
            continue
        if not all(
            part_is_taught(part, taught_lemmas, taught_keys, taught_stems)
            for part in row["parts"]
        ):
            untaught.append(row["word"])
    length_ok = MIN_WORDS <= len(words) <= MAX_WORDS
    if check_predicate:
        predicate_ok = has_predicate(readings, tagger, verb_stems)
        pn_conflicts, pn_conflicts_blocking = person_number_conflict(readings, tagger)
    else:
        predicate_ok = True
        pn_conflicts, pn_conflicts_blocking = [], []
    mismatched_targets = target_mismatch(readings, targets or (), entries_by_headword)
    return {
        "words": len(words),
        "unattested": unattested,
        "untaught": untaught,
        "enclitics": [
            {"word": row["word"], "enclitic": row["enclitic"]}
            for row in readings if row["enclitic"]
        ],
        "lemmas": sorted({
            lemma for row in readings for part in row["parts"] for lemma in part["lemmas"]
        }),
        "lengthOk": length_ok,
        "hasPredicate": predicate_ok,
        # Always reported in full; only the person-1/2 subset blocks (see
        # `person_number_conflict`'s docstring for why a bare 3rd-vs-3rd
        # mismatch is not on its own evidence of a dangling ``et``).
        "personNumberConflict": pn_conflicts,
        "targetMismatch": mismatched_targets,
        # 「已教過」不再擋人（見檔頭 2026-09-16 的裁定）；untaught 照記不照擋。
        # 2026-09-27 加三條硬閘：有述語、限定動詞人稱數一致（僅第一／第二人稱
        # 牽涉時才擋）、宣稱的標題詞真的在句中——這三條正是 2026-09-25 覆核
        # 報告指出機械閘看不見的病灶。
        "passed": (
            not unattested
            and length_ok
            and predicate_ok
            and not pn_conflicts_blocking
            and not mismatched_targets
        ),
    }


def practised(
    sentences: Iterable[str], targets: Sequence[Any], corpus: Corpus, tagger: Tagger
) -> dict[int, list[str]]:
    """Gate three: which of the lesson's twenty words the set actually uses.

    A word counts as practised when a sentence carries one of its lemmas, or --
    for the entries no treebank lemma fits, the phrases and the Greek
    liturgical loans such as ``Kyrie eléison`` -- when the written form itself
    appears.  Counting those by lemma would mark them permanently
    unpractisable.

    "One of its lemmas" means one that folds to the headword.  ``missa`` is
    also how ``mitto`` writes a participle, and without that restriction
    ``et misit in terram`` practises 彌撒.
    """
    seen_lemmas: set[str] = set()
    seen_keys: set[str] = set()
    for sentence in sentences:
        for word in tokenise(sentence):
            for part in word_reading(word, corpus, tagger)["parts"]:
                seen_lemmas |= part["lemmas"]
                seen_keys.add(part["key"])
    hits: dict[int, list[str]] = {}
    for entry in targets:
        if getattr(entry, "phrase", False):
            # A phrase is practised only when all of it is there.
            if entry.credit_keys <= seen_keys:
                hits[entry.ordinal] = sorted(entry.credit_keys)
            continue
        # Three routes, strictest first, and the first that answers wins.  One
        # route was not enough: ninety-one of the two thousand words carry a
        # lemma no corpus form does, and a lesson containing one of them could
        # never reach twenty-of-twenty however it was written.
        by_lemma = sorted(entry.credit_lemmas & seen_lemmas)
        if by_lemma:
            hits[entry.ordinal] = by_lemma
            continue
        by_form = sorted(entry.written_keys & seen_keys)
        if by_form:
            hits[entry.ordinal] = by_form
            continue
        by_stem = sorted(
            key for key in seen_keys
            if any(key.startswith(stem) for stem in entry.credit_stems)
        )
        if by_stem:
            hits[entry.ordinal] = by_stem
    return hits


def corpora_for(volume: int) -> list[str]:
    """Which corpus a volume's sentences are checked against: both, either way.

    This used to be the Vulgate alone for the upper volume, on the reasoning
    that the volume prints the Vulgate and nothing else.  That reasoning was
    about what the volume *reads*; the gate is asking something else — did
    anyone ever write this form, or did the sentence invent it.  For a
    vocabulary that comes from Collins and an upper corpus that is Jerome, the
    narrow scope put fifty of the thousand words out of reach permanently:
    pāpa, liturgia, apostolicus, catholicus, episcopālis, psalmista — church
    Latin, absent from the Vulgate, and printed at length in this very reader's
    lower volume.  Forty-nine of those fifty are attested once the church corpus
    counts, and none of them is a word the learner has no business meeting.

    So the scope is the whole reader's corpus.  Gate one is unchanged in what it
    refuses — a form nobody wrote is still refused — only in where it looks.
    """
    return ["vulgate", "church"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lesson", type=int, required=True)
    parser.add_argument("--volume", type=int, default=1, choices=[1, 2])
    parser.add_argument(
        "--check",
        type=Path,
        required=True,
        help='待驗檔，格式 {"lesson": n, "volume": 1, '
             '"sentences": [{"latin": "…", "chinese": "…"}]}',
    )
    parser.add_argument("--write", action="store_true", help="寫出 composed-sentences.json")
    args = parser.parse_args()

    payload = json.loads(args.check.read_text(encoding="utf-8"))
    volume = int(payload.get("volume", args.volume))
    lesson = int(payload.get("lesson", args.lesson))
    if lesson != args.lesson:
        raise SystemExit(f"檔案寫的是第 {lesson} 課，指令說的是第 {args.lesson} 課")
    sentences = payload.get("sentences", [])

    corpus = Corpus(corpora_for(volume))
    tagger = Tagger(gold=("proiel",) if volume == 1 else ("proiel", "ittb", "llct"))
    entries = load_vocabulary(tagger=tagger)
    targets, taught_lemmas, taught_keys = cumulative_vocabulary(entries, volume, lesson)
    taught_stems = cumulative_stems(entries, volume, lesson)
    appendix = appendix_keys(volume=volume)
    appendix_all: set[str] = set()
    for keys in appendix.values():
        appendix_all |= keys
    taught_keys = taught_keys | appendix_all

    # 標題詞閘要問「這個字真的是這個標題詞」，所以要用全書兩千詞（不是只有
    # 這一課或累積到這一課的），因為草稿的 targets 欄位可以宣稱任何一個
    # 已印在書裡的詞。以 headword_key 為鍵；少數同形異詞（liber、mundus、
    # occido……）鍵到一個以上的詞條，逐一比對再判定。
    entries_by_headword: dict[str, list[Any]] = {}
    for entry in entries:
        if entry.headword_key:
            entries_by_headword.setdefault(entry.headword_key, []).append(entry)
    verb_stems = verb_stems_of(entries)

    print(f"第 {volume} 冊第 {lesson} 課，{len(sentences)} 句")
    print(f"語料 {'＋'.join(corpus.names)}：{len(corpus.forms)} 種字形")
    print(f"已教：{len(taught_lemmas)} 個詞位、{len(taught_keys)} 種字形"
          f"（含附錄 {len(appendix_all)}）")

    rows: list[dict[str, Any]] = []
    for index, row in enumerate(sentences, start=1):
        latin = row.get("latin", "")
        report = verify(
            latin, corpus, tagger, taught_lemmas, taught_keys, taught_stems,
            targets=row.get("targets"), entries_by_headword=entries_by_headword,
            verb_stems=verb_stems,
        )
        rows.append({**row, "verification": report})
        mark = "通過" if report["passed"] else "退回"
        print(f"{index:2d} [{mark}] {latin}")
        print(f"     {row.get('chinese', '')}")
        if report["unattested"]:
            print(f"     ✗ 語料查無此形：{'、'.join(report['unattested'])}")
        if report["untaught"]:
            print(f"     ✗ 尚未教過：{'、'.join(report['untaught'])}")
        if not report["lengthOk"]:
            print(f"     ✗ 長度 {report['words']} 詞，規格是 {MIN_WORDS}–{MAX_WORDS} 詞")
        if not report["hasPredicate"]:
            print("     ✗ 沒有限定動詞（也讀不出省略 est／sunt 的名詞句）")
        if report["personNumberConflict"]:
            print(f"     ✗ 限定動詞人稱／數不一致：{'、'.join(report['personNumberConflict'])}")
        if report["targetMismatch"]:
            print(f"     ✗ 宣稱練到卻對不上詞形：{'、'.join(report['targetMismatch'])}")
        for hit in report["enclitics"]:
            print(f"     · 附著詞：{hit['word']} ＝ 主詞 ＋ -{hit['enclitic']}")

    hits = practised([row.get("latin", "") for row in sentences], targets, corpus, tagger)
    missing = [entry for entry in targets if entry.ordinal not in hits]
    passed = sum(1 for row in rows if row["verification"]["passed"])
    print(f"\n通過機器驗證 {passed}/{len(rows)} 句")
    print(f"本課二十詞練到 {len(hits)}/{len(targets)}")
    if missing:
        print("  未練到：" + "、".join(
            f"{entry.headword}{'（詞位未對上語料）' if not entry.resolved else ''}"
            for entry in missing
        ))
    if len(rows) != ITEMS_PER_LESSON:
        print(f"  注意：一課應為 {ITEMS_PER_LESSON} 題，此檔 {len(rows)} 題"
              "（引用題另由 build_latin_exercises.py 產出）")

    if args.write:
        COMPOSED.parent.mkdir(parents=True, exist_ok=True)
        COMPOSED.write_text(
            json.dumps(
                {
                    "volume": volume,
                    "lesson": lesson,
                    "author": payload.get("author", "hand-written"),
                    "corpora": corpus.names,
                    "sentences": rows,
                    "coverage": {
                        "lessonWords": len(targets),
                        "practised": len(hits),
                        "notPractised": [entry.public_record() for entry in missing],
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"寫入 {COMPOSED.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
