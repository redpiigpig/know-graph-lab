#!/usr/bin/env python3
"""Form-to-lemma register for the Vulgate, built from the PROIEL treebank.

The Greek reader learned this lesson the hard way: a general-purpose analyser
answers in the wrong register, so a Koine list built on Attic-first Morpheus
came out headed by Classical headwords for words the textbook already taught.
Latin has the same trap in a different shape -- an analyser trained on Caesar
and Cicero will lemmatise the Vulgate's late spellings and Christian coinages
into Classical headwords, or fail on them outright.

So the first layer is a corpus tagged on the text being taught.  PROIEL's Latin
section contains Jerome's Vulgate lemmatised sentence by sentence, alongside
Caesar, Cicero and Palladius; only the Vulgate sentences are read here, and the
Classical authors are deliberately discarded even though they are in the same
file.  A form that Jerome uses and Cicero does not should be headed by Jerome's
lemma, and the only way to guarantee that is to never look at Cicero.

The Clementine text this reader prints spells things differently from PROIEL's
base text -- caelum against cælum, eius against ejus -- so every form is indexed
under a folded key as well as its exact spelling, and the exact spelling is
tried first.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import latin_source_texts as L  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
PROIEL = CACHE / "UD_Latin-PROIEL-master"
OUTPUT = CACHE / "vulgate-lexicon.json"

VULGATE_MARK = "Jerome's Vulgate"


def read_proiel() -> tuple[Counter, dict[str, Counter], dict[str, Counter], dict[str, Counter]]:
    """Lemma frequencies plus exact-form and folded-form indexes."""
    lemma_freq: Counter = Counter()
    exact: dict[str, Counter] = defaultdict(Counter)
    folded: dict[str, Counter] = defaultdict(Counter)
    upos: dict[str, Counter] = defaultdict(Counter)
    capitals: dict[str, list[int]] = defaultdict(lambda: [0, 0])

    for path in sorted(PROIEL.glob("*.conllu")):
        in_vulgate = False
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# source"):
                in_vulgate = VULGATE_MARK in line
                continue
            if not line or line.startswith("#") or not in_vulgate:
                continue
            cols = line.split("\t")
            if len(cols) < 4 or "-" in cols[0]:
                continue
            form, lemma, tag = cols[1], cols[2], cols[3]
            if tag == "PUNCT" or not lemma or lemma == "_":
                continue
            lemma_freq[lemma] += 1
            exact[form][lemma] += 1
            folded[L.fold(form)][lemma] += 1
            upos[lemma][tag] += 1
            seen = capitals[lemma]
            seen[0] += 1
            if form[:1].isupper():
                seen[1] += 1

    names = {
        lemma
        for lemma, (total, upper) in capitals.items()
        if total >= 3 and upper / total >= 0.8
    }
    return lemma_freq, exact, folded, upos, names


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    lemma_freq, exact, folded, upos, names = read_proiel()
    payload = {
        "source": "UD_Latin-PROIEL, Jerome's Vulgate sentences only",
        "license": "CC BY-NC-SA 3.0",
        "tokens": sum(lemma_freq.values()),
        "lemmas": len(lemma_freq),
        "lemmaFrequency": dict(lemma_freq.most_common()),
        "exactForms": {f: c.most_common(1)[0][0] for f, c in exact.items()},
        "foldedForms": {f: c.most_common(1)[0][0] for f, c in folded.items()},
        "pos": {l: c.most_common(1)[0][0] for l, c in upos.items()},
        "properNames": sorted(names),
    }
    print(f"Vulgate tokens {payload['tokens']:,}；lemmas {payload['lemmas']:,}；"
          f"exact forms {len(payload['exactForms']):,}；專名 {len(names)}")
    print("top:", ", ".join(l for l, _ in lemma_freq.most_common(15)))
    print("names:", ", ".join(sorted(names)[:12]))
    if args.write:
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        print("→", OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
