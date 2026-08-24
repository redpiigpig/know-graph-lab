#!/usr/bin/env python3
"""Build the two-volume, 2,000-word Greek curriculum.

    Volume I  — New Testament and Septuagint   : 500 + 500
    Volume II — Fathers and Greek church texts : 1,000

Fifty lessons of twenty words each, per volume.  The New Testament half is taken
from Mounce's own list, in Mounce's own order, because that is the textbook the
learner is following and its Traditional-Chinese glosses are already reviewed.
The other 1,500 words are counted from the corpora this reader actually prints,
so every word earned its place by appearing in a text the reader contains.

Counting needs lemmas, and only the New Testament source has them.  Everything
else is resolved through the Morpheus index (see build_greek_lemma_index.py),
which covers 90-94% of running words in these corpora; what it cannot resolve is
reported rather than silently dropped.

The three lists are disjoint by construction: a word taught in the New Testament
half is not taught again in the Septuagint half, and neither is repeated in the
patristic volume.  Each volume therefore teaches what is new in it.
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

import greek_source_texts as gs
import greek_patristic_sources as ps
from verify_greek_vocab_lexicon import fold


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
MOUNCE = ROOT / "data" / "originalReaders" / "vocabulary" / "greek-1000.json"
LEMMA_INDEX = CACHE / "lemma-index.json"
KOINE_LEXICON = CACHE / "koine-lexicon.json"
OUTPUT = ROOT / "data" / "originalReaders" / "vocabulary" / "greek-2000.json"

NT_TARGET = 500
LXX_TARGET = 500
PATRISTIC_TARGET = 1000
PER_LESSON = 20

GREEK_RE = re.compile(r"[Ͱ-Ͽἀ-῿]")
SIGLA = "⸀⸁⸂⸃⸄⸅⸆⸇⸈⸉⸊⸋⸌⸍[]"

# Septuagint books the reader can draw on: the whole of Swete minus the
# pseudepigrapha, which belong to neither volume's vocabulary.
LXX_BOOKS = [
    "Gen", "Exod", "Lev", "Num", "Deut", "Josh", "Judg", "Ruth", "1Sam", "2Sam",
    "1Kgs", "2Kgs", "1Chr", "2Chr", "Ezra", "Neh", "Ps", "Prov", "Eccl", "Song",
    "Job", "Isa", "Jer", "Lam", "Ezek", "Dan", "Hos", "Amos", "Mic", "Joel",
    "Obad", "Jonah", "Nah", "Hab", "Zeph", "Hag", "Zech", "Mal",
    "Wis", "Sir", "Jdt", "TobS", "1Macc", "2Macc", "Bar",
]

APOSTOLIC_FATHERS = [
    "001-i_clement", "002-ii_clement", "003-ignatius-ephesians",
    "004-ignatius-magnesians", "005-ignatius-trallians", "006-ignatius-romans",
    "007-ignatius-philadelphians", "008-ignatius-smyrnaeans",
    "009-ignatius-polycarp", "010-polycarp-philippians", "011-didache",
    "012-barnabas", "013-shepherd", "014-martyrdom", "015-diognetus",
]

FIRST1K = [
    "tlg0645.tlg001.1st1K-grc1.xml",
    "tlg2035.tlg002.1st1K-grc1.xml",
    "tlg2022.tlg007.1st1K-grc1.xml",
    "tlg2022.tlg008.1st1K-grc1.xml",
]


def load_index() -> tuple[dict[str, list[str]], dict[str, str]]:
    if not LEMMA_INDEX.exists():
        raise FileNotFoundError(
            f"缺少 {LEMMA_INDEX}；先跑 scripts/build_greek_lemma_index.py --write"
        )
    payload = json.loads(LEMMA_INDEX.read_text(encoding="utf-8"))
    return payload["forms"], payload["lemmaPos"]


def load_koine() -> tuple[dict[str, list[str]], set[str]]:
    """The Koine resolver: forms tagged by the editors of the two Koine corpora."""
    if not KOINE_LEXICON.exists():
        raise FileNotFoundError(
            f"缺少 {KOINE_LEXICON}；先跑 scripts/build_greek_koine_lexicon.py --write"
        )
    payload = json.loads(KOINE_LEXICON.read_text(encoding="utf-8"))
    # Folded spelling to the corpora's own spelling, so a lookup is accent-blind
    # but what comes back is still printable.
    inventory: dict[str, str] = {}
    for lemma, total in sorted(
        payload["lemmaTotals"].items(), key=lambda pair: -pair[1]
    ):
        inventory.setdefault(fold(lemma), lemma)
    return payload["forms"], inventory

def clean(token: str) -> str:
    return unicodedata.normalize("NFC", token.strip(SIGLA + ".,·;:!?()»«—'’")).strip()


def nt_lemma_frequency() -> Counter:
    """New Testament lemma counts, straight from MorphGNT's own analysis."""
    counts: Counter = Counter()
    for book in gs.SBLGNT_BOOKS:
        path = gs.sblgnt_path(book)
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) == 7:
                counts[unicodedata.normalize("NFC", parts[6])] += 1
    return counts


# Attic spellings and older lexicon headwords, rewritten to the Koine form the
# reader teaches.  Every rewrite is checked against the Koine lemma inventory
# before it is applied, so the mapping can only ever land on a word the New
# Testament or the Septuagint actually uses.
ATTIC_REWRITES = (
    ("γιγν", "γιν"),        # γίγνομαι, γιγνώσκω
    ("ττ", "σσ"),           # θάλαττα, πράττω
    ("ρρ", "ρσ"),           # θάρρος
    ("έος", "οῦς"),         # χρύσεος, ἀργύρεος
    ("εος", "οῦς"),
)

SUPPLETIVE = {
    "ἔπω": "λέγω", "εἶπον": "λέγω", "ἐρέω": "λέγω",
    "εἶδον": "ὁράω", "ὄψομαι": "ὁράω",
    "ἦλθον": "ἔρχομαι", "ἤνεγκα": "φέρω", "ἔφαγον": "ἐσθίω",
    "σοῦ": "σύ", "ὑμός": "ὑμεῖς", "σός": "σύ",
    "ἐθέλω": "θέλω", "ἀνθρώπειος": "ἀνθρώπινος", "ξύν": "σύν",
    "εἵνεκα": "ἕνεκα", "ἐς": "εἰς", "διατί": "διά",
}


def to_koine(lemma: str, koine_lemmas) -> str:
    """Rewrite an Attic or principal-part headword to its Koine equivalent.

    Matching happens on the folded spelling, because the rules are about letters
    and the lemmas carry accents: written out, "γιγν" does not occur in
    "γίγνομαι" at all.  ``koine_lemmas`` is therefore a folded lookup, and what
    comes back is the Koine corpora's own spelling of the word.
    """
    if "(" in lemma:
        # The Septuagint analysis writes a movable consonant in brackets -
        # οὕτω(ς), ἔξεστι(ν).  Ask the Koine corpora which spelling they print
        # as the headword and use that, rather than carrying brackets into a
        # vocabulary list.
        bare = lemma.replace("(", "").replace(")", "")
        clipped = lemma[: lemma.index("(")]
        for candidate in (bare, clipped):
            target = koine_lemmas.get(fold(candidate))
            if target:
                return target
        return bare
    if lemma in SUPPLETIVE:
        target = koine_lemmas.get(fold(SUPPLETIVE[lemma]))
        if target:
            return target
    key = fold(lemma)
    if key in koine_lemmas:
        return koine_lemmas[key]
    for attic, koine in ATTIC_REWRITES:
        if attic in key:
            target = koine_lemmas.get(key.replace(attic, koine))
            if target:
                return target
    # A deponent listed under an active voice it never has: πορεύω for πορεύομαι.
    if key.endswith("ω"):
        for suffix in ("ομαι", "ουμαι"):
            target = koine_lemmas.get(key[:-1] + suffix)
            if target:
                return target
    return lemma


def corpus_lemma_frequency(tokens, koine_forms, koine_lemmas, morpheus):
    """Count lemmas in a corpus, answering in Koine.

    The Koine lexicon is asked first, because its answers come from editors who
    tagged these very texts.  Morpheus is asked only about forms the Koine
    corpora never attest, and even then its Koine-attested analyses are taken
    ahead of its Attic and Homeric ones.  Anything that can still only be named
    with a word from outside Koine is counted separately and reported, not
    quietly folded in.
    """
    counts: Counter = Counter()
    stats = Counter()
    outside: Counter = Counter()
    capitalised: Counter = Counter()
    for token in tokens:
        word = clean(token)
        if not word or not GREEK_RE.search(word):
            continue
        key = fold(word)
        options = koine_forms.get(key)
        if options:
            lemma = to_koine(options[0], koine_lemmas)
            counts[lemma] += 1
            capitalised[lemma] += word[:1].isupper()
            stats["koine"] += 1
            continue
        options = morpheus.get(key)
        if not options:
            stats["unresolved"] += 1
            continue
        attested = [to_koine(item, koine_lemmas) for item in options]
        within = [item for item in attested if fold(item) in koine_lemmas]
        if not within and len(set(attested)) > 1:
            # No Koine reading, and Morpheus cannot decide between its Classical
            # ones.  Guessing here is what put ὁλάω and πτελέα in the list, for
            # forms that were really ὅλος and a name; leave the word uncounted
            # and say so rather than invent a headword.
            stats["ambiguousOutside"] += 1
            continue
        lemma = within[0] if within else attested[0]
        counts[lemma] += 1
        capitalised[lemma] += word[:1].isupper()
        if within:
            stats["morpheusKoine"] += 1
        else:
            stats["morpheusOutside"] += 1
            outside[lemma] += 1

    # Morpheus lower-cases its headwords, so Πολύκαρπος and Εἰρηναῖος come back
    # looking like common adjectives.  The corpus itself says otherwise: a word
    # written with a capital nearly every time it appears is a name.
    names = {
        lemma for lemma, count in counts.items()
        if capitalised[lemma] >= count * 0.8
    }
    return counts, stats, outside, names

def lxx_tokens():
    for book in LXX_BOOKS:
        try:
            verses = gs._swete_book_cached(book)
        except (KeyError, FileNotFoundError):
            continue
        for verse in verses:
            for token in verse.tokens:
                yield token.text


def patristic_tokens():
    for stem in APOSTOLIC_FATHERS:
        try:
            for segment in ps.load_apostolic_father(stem):
                yield from segment.text.split()
        except FileNotFoundError:
            continue
    for filename in FIRST1K:
        try:
            for segment in ps.load_first1k(filename):
                yield from segment.text.split()
        except (FileNotFoundError, LookupError):
            continue
    liturgy = CACHE / "liturgy-chrysostom.json"
    if liturgy.exists():
        for step in json.loads(liturgy.read_text(encoding="utf-8"))["steps"]:
            yield from step["displayText"].split()
    creeds = CACHE / "creeds-greek.json"
    if creeds.exists():
        for document in json.loads(creeds.read_text(encoding="utf-8"))["documents"]:
            for segment in document["segments"]:
                yield from segment["displayText"].split()


def is_proper_name(lemma: str, pos: dict[str, str]) -> bool:
    # Morpheus tags proper nouns, and a capitalised headword that it does not
    # tag is still almost always a name in these corpora.
    return pos.get(lemma, "") == "n" and lemma[:1].isupper() or lemma[:1].isupper()


def main() -> None:
    parser = argparse.ArgumentParser(description="建立兩冊 2000 詞課程")
    parser.add_argument("--write", action="store_true", help="寫出 greek-2000.json")
    args = parser.parse_args()

    morpheus, pos = load_index()
    koine_forms, koine_lemmas = load_koine()
    mounce = json.loads(MOUNCE.read_text(encoding="utf-8"))

    # --- Volume I, first half: Mounce's own first five hundred --------------
    nt_words = sorted(mounce, key=lambda item: item["ordinal"])[:NT_TARGET]
    taught = set()
    for item in nt_words:
        # An entry may print several spellings - "ἐκ (ἐξ)", "ἀλλά, ἀλλ'" - and a
        # word counted under any of them has been taught.
        spellings = (item["lemma"], item["headword"], item["printedEntry"])
        for piece in re.split(r"[^Ͱ-Ͽἀ-῿]+", " ".join(spellings)):
            piece = piece.strip()
            if piece and GREEK_RE.search(piece):
                taught.add(fold(piece))
                taught.add(fold(to_koine(piece, koine_lemmas)))
    print(f"  新約 {len(nt_words)} 詞：取自 Mounce 詞表前 {NT_TARGET} 筆，沿用既有繁中詞義與音譯")

    def pick(name, tokens, target, report):
        counts, stats, outside, names = corpus_lemma_frequency(
            tokens, koine_forms, koine_lemmas, morpheus
        )
        total = sum(stats.values())
        print(f"  {name}：通用希臘文詞典解出 {stats['koine'] * 100 // max(total, 1)}%，"
              f"Morpheus 補 {(stats['morpheusKoine'] + stats['morpheusOutside']) * 100 // max(total, 1)}%，"
              f"未解 {stats['unresolved'] * 100 // max(total, 1)}%")
        chosen = []
        for lemma, count in counts.most_common():
            if len(chosen) >= target:
                break
            key = fold(lemma)
            if key in taught or lemma in names or is_proper_name(lemma, pos):
                continue
            taught.add(key)
            chosen.append({
                "lemma": lemma,
                "frequency": count,
                "withinKoine": fold(lemma) in koine_lemmas,
            })
        beyond = [item["lemma"] for item in chosen if not item["withinKoine"]]
        print(f"  {name} {len(chosen)} 詞；其中 {len(beyond)} 個詞位不在新約與七十士的標註詞表內"
              f"（{report}）")
        if beyond:
            print(f"    例：{'、'.join(beyond[:8])}")
        return chosen

    # --- Volume I, second half: what the Septuagint adds --------------------
    lxx_words = pick("七十士", lxx_tokens(), LXX_TARGET, "應為七十士獨有詞，非古典希臘文")

    # --- Volume II: what the Fathers and the church texts add --------------
    pat_words = pick("教父與希臘教會文獻", patristic_tokens(), PATRISTIC_TARGET,
                     "多為教會希臘文的專門詞，如三一論與職分用語")

    entries = []
    for index, word in enumerate(nt_words):
        entries.append({
            "ordinal": index + 1, "volume": 1, "corpus": "new-testament",
            "lemma": word["lemma"], "printedEntry": word["printedEntry"],
            "headword": word["headword"],
            "textbookTransliteration": word["textbookTransliteration"],
            "glossEn": word.get("glossEn", ""), "glossZh": "",
            "strong": word.get("strong", ""),
            "isProperName": word.get("isProperName", False),
            "properNameTypes": word.get("properNameTypes", []),
            "source": "Mounce, Basics of Biblical Greek Grammar",
            "mounceOrdinal": word["ordinal"],
            "verification": word["verification"],
        })
    for index, word in enumerate(lxx_words):
        entries.append({
            "ordinal": NT_TARGET + index + 1, "volume": 1, "corpus": "septuagint",
            "lemma": word["lemma"], "printedEntry": word["lemma"],
            "headword": word["lemma"], "textbookTransliteration": "",
            "glossEn": "", "glossZh": "", "strong": "",
            "isProperName": False, "properNameTypes": [],
            "source": "Swete 七十士譯本詞頻（CATSS/OSSP 通用希臘文詞位標註）",
            "frequency": word["frequency"], "withinKoine": word["withinKoine"],
            "verification": "corpus_frequency",
        })
    for index, word in enumerate(pat_words):
        entries.append({
            "ordinal": index + 1, "volume": 2, "corpus": "patristic",
            "lemma": word["lemma"], "printedEntry": word["lemma"],
            "headword": word["lemma"], "textbookTransliteration": "",
            "glossEn": "", "glossZh": "", "strong": "",
            "isProperName": False, "properNameTypes": [],
            "source": "使徒教父＋First1KGreek＋信經＋金口若望禮儀詞頻（通用希臘文詞位標註）",
            "frequency": word["frequency"], "withinKoine": word["withinKoine"],
            "verification": "corpus_frequency",
        })

    for entry in entries:
        entry["lesson"] = (entry["ordinal"] - 1) // PER_LESSON + 1
        entry["lessonSlot"] = (entry["ordinal"] - 1) % PER_LESSON + 1

    payload = {
        "schemaVersion": "2.0.0",
        "structure": {
            "volumes": 2, "lessonsPerVolume": 50, "wordsPerLesson": PER_LESSON,
            "volume1": {"title": "新約與七十士譯本", "newTestament": NT_TARGET, "septuagint": LXX_TARGET},
            "volume2": {"title": "教父文獻與希臘教會文獻", "words": PATRISTIC_TARGET},
        },
        "lemmaResolution": {
            "newTestament": "MorphGNT 逐詞詞位，精確",
            "scope": "通用希臘文；阿提卡詞頭一律改回通用希臘文拼法，例如 γίγνομαι 作 γίνομαι",
            "septuagint": "CATSS/OSSP 標註為主，Morpheus 僅補通用希臘文語料未見之字形",
            "patristic": "同上；不在標註詞表內的詞位另以 withinKoine 標明",
        },
        "disjoint": "三份詞表互不重複；後一份只教前面沒教過的詞。",
        "counts": {
            "total": len(entries),
            "volume1": sum(1 for e in entries if e["volume"] == 1),
            "volume2": sum(1 for e in entries if e["volume"] == 2),
        },
        "entries": entries,
    }

    counts = payload["counts"]
    print(f"  合計 {counts['total']} 詞：上冊 {counts['volume1']}、下冊 {counts['volume2']}；"
          f"每冊 50 課 × {PER_LESSON} 詞")
    if counts["total"] != 2000:
        raise SystemExit(f"總詞數應為 2000，實得 {counts['total']}")

    if args.write:
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已寫出 {OUTPUT}")
    else:
        print("（未寫檔；加 --write 才會輸出）")


if __name__ == "__main__":
    main()
