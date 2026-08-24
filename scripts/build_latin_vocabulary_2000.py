#!/usr/bin/env python3
"""Assemble the reader's two thousand words: Collins first, corpus second.

The upper volume's thousand words are Collins's, in Collins's order.  That order
is not a frequency ranking and must not be re-sorted into one: the primer
introduces missa, papa and ecclesia in its first unit because they are what a
church Latin reader meets first, not because they outrank et and sum.  A
frequency list would bury them and teach a different language.

The lower volume's thousand are what Collins does not reach, ranked by how often
they occur in the corpus that volume actually prints: the fathers and the
medieval writers for its first half, the modern curia and the liturgy for its
second.  Splitting the count by half matters.  Counted together, the twentieth
century's six hundred thousand words would swamp the fathers, and the first half
would quietly end up teaching curial vocabulary.

Proper names never occupy a lesson slot in either volume.  The Greek reader
established that rule after finding twenty-eight of them inside Mounce's first
five hundred; the same rule is applied to Collins here, the freed slots are
backfilled from further down his order, and the names go to the appendix.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import latin_source_texts as L  # noqa: E402
from latin_lemmatiser import Lemmatiser  # noqa: E402
import latin_dictionary as W  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
COLLINS_PAGES = CACHE / "collins-pages"
CHURCH = CACHE / "latin-church"
OUTPUT = ROOT / "data" / "originalReaders" / "vocabulary" / "latin-2000.json"
NAMES_OUT = ROOT / "data" / "originalReaders" / "vocabulary" / "latin-proper-names.json"

LESSONS_PER_VOLUME = 50
WORDS_PER_LESSON = 20
VOLUME_WORDS = LESSONS_PER_VOLUME * WORDS_PER_LESSON

# Citation apparatus prints inside these documents but is not Latin vocabulary.
APPARATUS = {
    "cfr", "cf", "ibid", "ib", "loc", "cit", "op", "n", "nn", "pp", "p",
    "matth", "marc", "luc", "ioan", "joan", "rom", "cor", "gal", "eph", "phil",
    "col", "thess", "tim", "tit", "philem", "hebr", "iac", "petr", "apoc",
    "gen", "ex", "lev", "num", "deut", "ios", "iud", "reg", "par", "esd",
    "tob", "iudith", "esth", "iob", "ps", "psal", "prov", "eccle", "cant",
    "sap", "eccli", "is", "ier", "lam", "bar", "ez", "dan", "os", "ioel",
    "am", "abd", "ion", "mich", "nah", "hab", "soph", "agg", "zach", "mal",
    "mach", "act", "epist", "litt", "alloc", "enc", "const", "decr", "can",
    "aas", "pl", "pg", "ss", "sq", "sqq", "vol", "ed", "seq", "cap", "art",
    "lib", "tit", "sess", "par", "num", "col", "fol",
    "a", "d", "s", "t", "v", "l", "c", "i", "ii", "iii", "iv", "vi", "x",
}

# Encyclical folders are named 20c-john-paul-ii, so the century is a prefix.
MODERN_GROUPS = re.compile(r"^(1[6-9]c|2[01]c)(-|$)|^(trent|vatican-i|vatican-ii)$")

# The Latin Library wraps its texts in English navigation, and the modern curial
# files carry vatican.va URLs.  Neither is Latin, and a few English words are
# also Latin words (sum, in, me, a), so the contamination has to be dropped by
# line rather than left to fail lookup one token at a time.
ENGLISH = {
    "the", "and", "of", "to", "in", "for", "with", "from", "this", "that",
    "page", "library", "classics", "christian", "medieval", "index", "back",
    "translated", "text", "notes", "by", "or", "be", "is", "are", "was",
}
NOISE = re.compile(r"https?://|www\.|\.html|\.com|@")


def latin_line(line: str) -> bool:
    if NOISE.search(line):
        return False
    tokens = [w.lower() for w in L.words(line)]
    if not tokens:
        return False
    english = sum(1 for w in tokens if w in ENGLISH)
    return english / len(tokens) < 0.34


MACRONS = set("ĀĒĪŌŪȲāēīōūȳ")


def macron_count(text: str) -> int:
    return sum(1 for ch in text if ch in MACRONS)


UNIT_LEAK = re.compile(r"\s*\(\d{1,2}\)\s*$")


def headword_of(raw: str, forms: str) -> str:
    """Reduce a dictionary line to the word it is filed under.

    The OCR sometimes returns the whole entry in the headword field, and it does
    so most often exactly where it matters: Collins prints the closed-class words
    as several nominatives rather than nominative-plus-genitive, so ``qui, quae,
    quod`` and ``quis, quid`` arrive whole.  Left alone, the commonest relative
    pronoun in Latin is absent from the reader and shows up instead as an
    untaught word in the second volume.

    A phrase without commas is a real Collins entry -- ``in aeternum``,
    ``grātiās agere``, ``aut . . aut`` -- and is kept as it stands.
    """
    head = (raw or forms or "").strip()
    if "," in head:
        head = head.split(",", 1)[0].strip()
    # A stray space inside a word: OCR reads dirigō as "dirig ō".
    head = re.sub(r"(?<=[A-Za-zĀĒĪŌŪȲāēīōūȳ]) (?=[A-Za-zĀĒĪŌŪȲāēīōūȳ]{1,2}$)", "", head)
    return head


def strip_marks(word: str) -> str:
    text = unicodedata.normalize("NFD", word)
    return "".join(ch for ch in text if not unicodedata.combining(ch))


# Capitalisation alone does not identify a name in this textbook.  Collins
# capitalises the nationality adjectives (Rōmānus, Jūdaeus, Nazarēnus), the
# liturgical common nouns (Pascha, Kyrie, Sabaōth, Evangelium, Lēvīta), and God.
# Sending those to the appendix would leave the reader without Deus -- the second
# commonest word in the Vulgate -- and without any way to say "Roman".
#
# The appendix holds names of people, places and peoples.  It does not hold God,
# it does not hold adjectives, and it does not hold common nouns.  There are only
# twenty-nine capitalised entries in the whole primer, so the exceptions are
# named here rather than inferred by a rule that would misfire on some of them.
TAUGHT_THOUGH_CAPITALISED = {
    "deus", "christus", "jesus", "iesus",      # God and the names of God
    "evangelium", "pascha", "kyrie", "sabaoth", "levita",  # liturgical vocabulary
}

ADJECTIVE_FORMS = re.compile(r"-a,\s*-um|,\s*-a,\s*-um|-is,\s*-e")


def is_name(entry: dict) -> bool:
    """A person, a place or a people -- not every capitalised headword."""
    if not strip_marks(entry["headword"])[:1].isupper():
        return False
    if strip_marks(entry["headword"]).lower() in TAUGHT_THOUGH_CAPITALISED:
        return False
    if ADJECTIVE_FORMS.search(entry.get("forms", "")):
        return False
    return True


def attested(word: str, lm: Lemmatiser, words_index) -> bool:
    """Is this a Latin word at all?

    The primer's back matter wraps its definitions across column breaks, and the
    OCR occasionally reads the continuation as a new entry: ``finis`` runs on to
    "boundary; pl., territory, district" and ``boundary`` arrives looking like a
    headword with a unit number attached.  A word that neither corpus attests and
    no dictionary knows is not a word this reader should teach.
    """
    # Enclitics and phrases are real Collins entries that no lemma index holds:
    # -que and -ne are written attached to the next word, and in aeternum,
    # grātiās agere and aut . . aut are taught as units.  Only a bare single
    # word has to prove itself.
    if word.startswith("-") or " " in word or "." in word:
        return True
    key = L.fold(word)
    if key in words_index:
        return True
    return key in lm.folded or word in lm.exact


def load_collins(lm, words_index) -> tuple[list[dict], list[dict], list[str]]:
    """Return (teaching entries in Collins order, proper names, rejected)."""
    pages = sorted(COLLINS_PAGES.glob("page-*.json"))
    if not pages:
        raise SystemExit("Collins 詞表尚未 OCR")
    raw: list[dict] = []
    for page in pages:
        raw.extend(json.loads(page.read_text(encoding="utf-8")))

    seen: dict[str, dict] = {}
    for entry in raw:
        head = (entry.get("headword") or "").strip()
        unit = entry.get("unit")
        if not head or unit is None:
            continue
        exercise_only = isinstance(unit, str) and str(unit).upper().startswith("E")
        try:
            unit_no = int(str(unit).lstrip("Ee")) if exercise_only else int(unit)
        except (TypeError, ValueError):
            continue
        forms = (entry.get("forms") or head).strip()
        key = unicodedata.normalize("NFC", headword_of(head, forms))
        if not key:
            continue
        record = {
            "headword": key,
            "forms": forms,
            "gram": (entry.get("gram") or "").strip(),
            "glossEn": UNIT_LEAK.sub("", (entry.get("gloss") or "").strip()),
            "unit": unit_no,
            "exerciseOnly": exercise_only,
            "under": (entry.get("under") or "").strip(),
        }
        # Two entries that fold to the same headword may be a real pair or one
        # entry read twice.  Latin keeps genuine homographs that only a macron
        # separates -- occīdō "kill" beside occidō "set", praedicō "proclaim"
        # beside praedīcō "foretell" -- and the contract says to preserve them.
        # What tells them apart is the rest of the line: real homographs have
        # different principal parts, while a doubled entry has the same ones
        # written once with macrons and once without.
        # Fold the whole line, headword included.  Keying on the raw headword
        # keeps usque and ūsque apart, which is the doubling this is meant to
        # collapse; the principal parts alone already separate the real pairs.
        key = L.fold(forms)
        prior = seen.get(key)
        if prior is None:
            seen[key] = record
        elif prior["exerciseOnly"] and not exercise_only:
            seen[key] = record
        elif macron_count(record["forms"]) > macron_count(prior["forms"]):
            # Keep the better-read copy: the one that still has its macrons.
            seen[key] = record

    ordered = sorted(
        (e for e in seen.values() if not e["exerciseOnly"]),
        key=lambda e: (e["unit"], strip_marks(e["headword"]).lower()),
    )
    # Flag, do not drop.  The corpora do not attest everything Collins teaches --
    # eléison is Greek inside the Latin liturgy, avē! is an imperative, memoror is
    # a deponent the treebanks never tag -- and dropping an entry because no index
    # happens to hold it removes real vocabulary to catch one OCR artifact.  The
    # artifact is left in the list, marked, for a reviewer to strike.
    rejected = []
    for entry in ordered:
        entry["attested"] = attested(entry["headword"], lm, words_index)
        if not entry["attested"]:
            rejected.append(entry["headword"])
    names = [e for e in ordered if is_name(e)]
    teaching = [e for e in ordered if not is_name(e)]
    return teaching, names, rejected


def corpus_counts(lm: Lemmatiser) -> tuple[Counter, Counter, dict[str, Counter]]:
    """Lemma counts for the two halves of the lower volume, kept apart."""
    early: Counter = Counter()
    modern: Counter = Counter()
    unresolved: dict[str, Counter] = {"early": Counter(), "modern": Counter()}

    def absorb(text: str, bucket: Counter, miss: Counter) -> None:
        for line in text.splitlines():
            if not latin_line(line):
                continue
            for word in L.words(line):
                if not lm.is_word(word) or word.lower() in APPARATUS:
                    continue
                lemma = lm.lemma(word)
                if lemma:
                    bucket[lemma] += 1
                else:
                    miss[word] += 1

    for doc in L.church_documents():
        modern_doc = bool(MODERN_GROUPS.match(doc["group"]))
        absorb(doc["text"], modern if modern_doc else early,
               unresolved["modern"] if modern_doc else unresolved["early"])

    # Everything fetched from The Latin Library is ancient or medieval, the
    # hymns and creeds included; the modern half is the repository's own
    # sixteenth-century-and-later curial documents.
    for path in sorted(CHURCH.rglob("*.txt")):
        absorb(path.read_text(encoding="utf-8", errors="replace"),
               early, unresolved["early"])

    return early, modern, unresolved


UPOS_TO_WORDS = {
    "NOUN": "N", "PROPN": "N", "VERB": "V", "AUX": "V", "ADJ": "ADJ",
    "ADV": "ADV", "ADP": "PREP", "CCONJ": "CONJ", "SCONJ": "CONJ",
    "PRON": "PRON", "DET": "PRON", "NUM": "NUM", "INTJ": "INTERJ",
}


def choose(hits: list, lemma: str, upos: str):
    """Pick which dictionary entry a corpus lemma means.

    A folded key can land on several entries, and taking the first one in file
    order gets it wrong in two ways that both show up immediately: the Nones of
    the Roman calendar outrank the adverb non, and cum arrives as a preposition
    when the corpus tagged it a conjunction.  So the part of speech the corpus
    assigned is honoured first, and an exact spelling match after that.
    """
    if not hits:
        return None
    wanted = UPOS_TO_WORDS.get(upos, "")
    ranked = sorted(
        hits,
        key=lambda e: (
            0 if wanted and e.pos == wanted else 1,
            0 if e.lemma == lemma else 1,
            0 if e.lemma[:1].islower() else 1,
            "ABCDEFIMNX".find(e.freq or "X"),
        ),
    )
    return ranked[0]


def lesson_rows(entries: list[dict], volume: str) -> list[dict]:
    rows = []
    for index, entry in enumerate(entries):
        rows.append({
            **entry,
            "volume": volume,
            "lesson": index // WORDS_PER_LESSON + 1,
            "ordinal": index + 1,
        })
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    lm = Lemmatiser()
    words_index = W.index_by_lemma(W.load())
    teaching, collins_names, rejected = load_collins(lm, words_index)
    print(f"Collins 教學詞條 {len(teaching)}；專名另計 {len(collins_names)}"
          f"；語料與字典皆無佐證、待人工覆核 {len(rejected)}"
          f"{'：' + ', '.join(rejected[:6]) if rejected else ''}")
    if len(teaching) < VOLUME_WORDS:
        print(f"[!] 只有 {len(teaching)} 詞，不足上冊 {VOLUME_WORDS}；OCR 尚未跑完")

    upper = teaching[:VOLUME_WORDS]
    spill = teaching[VOLUME_WORDS:]
    # Fold, do not merely strip macrons.  The treebanks spell the lower
    # volume's words with classical u and i (uita, iustitia, seruus) while
    # Collins spells them uita's ecclesiastical v and j, so a macron-only
    # comparison lets fifty-eight words be taught twice under two spellings.
    taught = {L.fold(e["headword"]) for e in teaching}

    early, modern, unresolved = corpus_counts(lm)
    print(f"語料：教父／中世紀 {sum(early.values()):,} 詞；近現代 {sum(modern.values()):,} 詞")

    already: set[str] = set()

    def pick(counts: Counter, wanted: int) -> list[dict]:
        chosen: list[dict] = []
        for lemma, freq in counts.most_common():
            if wanted <= len(chosen):
                break
            key = L.fold(lemma)
            if key in already or key in taught:
                continue
            if lemma in lm.names or lm.pos.get(lemma) in {"PUNCT", "X"}:
                continue
            record = enrich(lemma, freq, lm)
            # A lesson slot must be able to print principal parts.  What fails
            # this test is not vocabulary the reader is missing: it is an
            # inflected form of something Collins already taught under another
            # citation form (se beside sui), an orthographic variant (uos,
            # littere), or a numeral the appendix carries anyway (duo, tres).
            if record["formsRoute"] == "missing":
                continue
            already.add(key)
            chosen.append(record)
        return chosen

    def enrich(lemma: str, freq: int, lm: Lemmatiser) -> dict:
        """Give a bare corpus lemma its dictionary entry.

        The treebanks that supply the lower volume print classical
        orthography -- uenerabilis, ueluti -- while the upper volume prints
        Collins's ecclesiastical v and j.  One reader cannot spell the same
        language two ways across its two volumes, so where Whitaker knows the
        word his spelling is taken as the headword, and the treebank's form is
        kept beside it as the tagged variant.
        """
        # A treebank sometimes lemmatises a sentence-initial word with its
        # capital still attached, which would put Non into the vocabulary
        # beside non.  Names are already excluded above, so anything reaching
        # here is a common word and belongs in lower case.
        lemma = lemma[:1].lower() + lemma[1:]
        hits = words_index.get(L.fold(lemma), [])
        best = choose(hits, lemma, lm.pos.get(lemma, ""))
        return {
            "headword": best.lemma if best else lemma,
            "forms": best.form if best else lemma,
            "gram": best.pos if best else lm.pos.get(lemma, ""),
            "glossEn": best.definition if best else "",
            "unit": None,
            "exerciseOnly": False,
            "under": "",
            "corpusFrequency": freq,
            "pos": lm.pos.get(lemma, ""),
            "treebankLemma": lemma,
            "formsRoute": "whitakers-words" if best else "missing",
            "age": W.AGE.get(best.age, "") if best else "",
            "area": W.AREA.get(best.area, "") if best else "",
            "ecclesiastical": bool(best and best.ecclesiastical),
        }

    # Collins's overflow heads the lower volume: it is still graded vocabulary
    # from the same textbook, and dropping it would teach a rarer synonym while
    # leaving the word itself untaught.
    half = VOLUME_WORDS // 2
    spill_head = spill[:half]
    for entry in spill_head:
        already.add(L.fold(entry["headword"]))
    first_half = spill_head + pick(early, half - len(spill_head))
    second_half = pick(modern, VOLUME_WORDS - half)
    lower = first_half + second_half

    payload = {
        "contract": {
            "volumes": 2,
            "lessonsPerVolume": LESSONS_PER_VOLUME,
            "wordsPerLesson": WORDS_PER_LESSON,
            "upperSource": "Collins, A Primer of Ecclesiastical Latin, units 1-35, textbook order",
            "lowerFirstHalf": "Collins overflow, then patristic and medieval corpus frequency",
            "lowerSecondHalf": "modern curial and liturgical corpus frequency",
            "properNames": "appendix only; never a lesson slot",
        },
        "counts": {
            "upper": len(upper),
            "lower": len(lower),
            "collinsSpillUsed": len(spill_head),
            "earlyTokens": sum(early.values()),
            "modernTokens": sum(modern.values()),
        },
        "entries": lesson_rows(upper, "上冊") + lesson_rows(lower, "下冊"),
    }
    print(f"上冊 {len(upper)}；下冊 {len(lower)}"
          f"（Collins 溢出 {len(spill_head)} + 語料 {len(lower) - len(spill_head)}）")
    missing = [e for e in lower if e.get("formsRoute") == "missing"]
    church = [e for e in lower if e.get("ecclesiastical")]
    print(f"下冊查得字典形式 {len(lower) - len(missing)}/{len(lower)}；標記教會／後古典 {len(church)}")
    print("下冊教父段前十:", ", ".join(e["headword"] for e in first_half[:10]))
    print("下冊近現代前十:", ", ".join(e["headword"] for e in second_half[:10]))
    if missing:
        print("無字典形式:", ", ".join(e["headword"] for e in missing[:12]))
    print("未解析（教父）:", ", ".join(w for w, _ in unresolved["early"].most_common(8)))
    print("未解析（近現代）:", ", ".join(w for w, _ in unresolved["modern"].most_common(8)))

    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        NAMES_OUT.write_text(json.dumps(collins_names, ensure_ascii=False, indent=1), encoding="utf-8")
        print("->", OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
