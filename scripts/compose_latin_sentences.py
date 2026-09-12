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
import sys

from pathlib import Path
from typing import Any, Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_latin_lemma_corpus import (  # noqa: E402
    OUTPUT as CORPUS_FILES,
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


def part_is_taught(part: dict[str, Any], taught_lemmas: set[str], taught_keys: set[str]) -> bool:
    # The spelling variants are asked last and only when the plain comparison
    # has failed: the corpus writes ``cœnam`` for a word the textbook teaches as
    # ``cēna``, and without this the gate calls that form attested and untaught
    # at once -- a pair no sentence can satisfy.
    return (
        bool(part["lemmas"] & taught_lemmas)
        or part["key"] in taught_keys
        or bool(spelling_variants(part["key"]) & taught_keys)
    )


def verify(
    sentence: str,
    corpus: Corpus,
    tagger: Tagger,
    taught_lemmas: set[str],
    taught_keys: set[str],
) -> dict[str, Any]:
    """Gates one and two, on one sentence.  Everything reported is verbatim."""
    words = tokenise(sentence)
    readings = [word_reading(word, corpus, tagger) for word in words]
    unattested = [row["word"] for row in readings if not row["attested"]]
    untaught: list[str] = []
    for row in readings:
        if not row["attested"]:
            continue
        if not all(part_is_taught(part, taught_lemmas, taught_keys) for part in row["parts"]):
            untaught.append(row["word"])
    length_ok = MIN_WORDS <= len(words) <= MAX_WORDS
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
        "passed": not unattested and not untaught and length_ok,
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
    """Which corpus a volume's sentences are checked against.

    The upper volume prints the Vulgate and nothing else, so a form must be in
    the Vulgate.  The lower volume reads fifteen centuries of church Latin on
    top of it, and its learner has the Vulgate behind them, so both count.
    """
    return ["vulgate"] if volume == 1 else ["vulgate", "church"]


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
    appendix = appendix_keys(volume=volume)
    appendix_all: set[str] = set()
    for keys in appendix.values():
        appendix_all |= keys
    taught_keys = taught_keys | appendix_all

    print(f"第 {volume} 冊第 {lesson} 課，{len(sentences)} 句")
    print(f"語料 {'＋'.join(corpus.names)}：{len(corpus.forms)} 種字形")
    print(f"已教：{len(taught_lemmas)} 個詞位、{len(taught_keys)} 種字形"
          f"（含附錄 {len(appendix_all)}）")

    rows: list[dict[str, Any]] = []
    for index, row in enumerate(sentences, start=1):
        latin = row.get("latin", "")
        report = verify(latin, corpus, tagger, taught_lemmas, taught_keys)
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
