#!/usr/bin/env python3
"""Build a Koine form-to-lemma lexicon from the two tagged Koine corpora.

Morpheus knows all of Ancient Greek, which is the wrong range for this reader.
Asked for the lemma of σου it offers the Homeric possessive σός; asked for
ἐγένετο it answers with the Attic γίγνομαι.  Neither is how the Greek of the
New Testament, the Septuagint or the Fathers is described, and a vocabulary
list built on them would be teaching Classical Greek under a Koine title.

Two corpora carry Koine lemmas assigned by editors rather than by an analyser:
MorphGNT tags every word of the New Testament, and the CATSS/OSSP analysis
tags every word of the Septuagint.  Together they cover roughly 750,000 running
words of exactly the register this reader teaches.  Folding them into one
form-to-lemma table gives a resolver that answers in Koine, and answers with
counts, so an ambiguous form is settled by how the tagged corpora actually read
it rather than by a guess.

Morpheus stays in the chain, but demoted: it is consulted only for forms these
two corpora never attest, and what it returns is marked as coming from outside
Koine so the caller can report it rather than absorb it silently.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import greek_source_texts as gs
from verify_greek_vocab_lexicon import fold


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
LXX_DIR = CACHE / "sources" / "lxx-lexemes"
OUTPUT = CACHE / "koine-lexicon.json"

SOURCES = {
    "newTestament": "MorphGNT / SBLGNT 逐詞詞位標註",
    "septuagint": "CATSS/OSSP 七十士逐詞詞位（eliranwong/LXX-Rahlfs-1935）",
}


def read_keyed(path: Path, column: int) -> dict[str, str]:
    """Read one column of a tab-separated file, keyed by its OSSP word number.

    The two files run to the same 623,693 word numbers but not to the same row
    counts: a handful of rows in the text file carry no form.  Joining on the
    number rather than on position keeps every word matched to its own lemma,
    and lets the incomplete rows fall out on their own.
    """
    keyed: dict[str, str] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.reader(handle, delimiter="	"):
            if len(row) > column and row[0].strip():
                value = unicodedata.normalize("NFC", row[column]).strip()
                if value:
                    keyed[row[0].strip()] = value
    return keyed

def nt_pairs():
    for book in gs.SBLGNT_BOOKS:
        path = gs.sblgnt_path(book)
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) == 7:
                yield (
                    unicodedata.normalize("NFC", parts[4]),
                    unicodedata.normalize("NFC", parts[6]),
                )


def lxx_pairs():
    forms = read_keyed(LXX_DIR / "text_accented.csv", 2)
    lemmas = read_keyed(LXX_DIR / "OSSP_lexemes.csv", 1)
    matched = forms.keys() & lemmas.keys()
    if len(matched) < len(forms) * 0.99:
        raise ValueError(
            f"七十士字形 {len(forms)} 筆只對上詞位 {len(matched)} 筆，對齊有問題"
        )
    for key in matched:
        yield forms[key], lemmas[key]

def build() -> dict:
    table: dict[str, Counter] = defaultdict(Counter)
    # Folding away accents and breathings makes ἕξ "six" indistinguishable from
    # ἐξ "out of", and εἷς "one" from εἰς "into"; the commoner word then takes
    # every occurrence and the other disappears from the counts entirely.  For
    # those pairs the breathing is the whole word, so keep an exact index too and
    # consult it before the folded one.
    exact: dict[str, Counter] = defaultdict(Counter)
    lemma_totals: Counter = Counter()
    provenance: dict[str, set] = defaultdict(set)
    tallies = {}

    for name, pairs in (("newTestament", nt_pairs()), ("septuagint", lxx_pairs())):
        count = 0
        for form, lemma in pairs:
            key = fold(form)
            if not key or not lemma:
                continue
            table[key][lemma] += 1
            exact[form][lemma] += 1
            lemma_totals[lemma] += 1
            provenance[lemma].add(name)
            count += 1
        tallies[name] = count

    # Where both corpora tag the same form, the New Testament's headword wins.
    # The Septuagint analysis keeps some older lexicon conventions - εἶπεν filed
    # under ἔπω, σου under σοῦ, χρυσοῦν under χρύσεος - and this reader teaches
    # the New Testament's, because that is what Mounce's list uses and what a
    # Koine dictionary prints today.
    nt_counts = {}
    for form, lemma in nt_pairs():
        key = fold(form)
        if key:
            nt_counts.setdefault(key, Counter())[lemma] += 1

    forms = {}
    for key, counts in table.items():
        preferred = nt_counts.get(key)
        forms[key] = sorted(
            counts,
            key=lambda lemma: (
                -(preferred.get(lemma, 0) if preferred else 0),
                -counts[lemma],
                lemma,
            ),
        )
    weights = {key: dict(counts) for key, counts in table.items()}
    exact_forms = {
        form: [lemma for lemma, _ in counts.most_common()]
        for form, counts in exact.items()
        if len(table[fold(form)]) > 1        # only where folding actually loses something
    }
    return {
        "schemaVersion": "1.0.0",
        "exactForms": exact_forms,
        "scope": "通用希臘文（Koine）：新約與七十士譯本的編者詞位標註，不含古典希臘文分析",
        "sources": SOURCES,
        "wordsTagged": tallies,
        "formCount": len(forms),
        "lemmaCount": len(lemma_totals),
        "note": (
            "鍵為去重音、去氣號、去下標 iota 的字形。一形多位時依標註語料的實際次數排序，"
            "最常見者在前。Morpheus 僅供本表查無之字形使用，且須另行標記為通用希臘文以外。"
        ),
        "forms": forms,
        "weights": weights,
        "lemmaTotals": dict(lemma_totals),
        "lemmaCorpora": {lemma: sorted(names) for lemma, names in provenance.items()},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="建立通用希臘文字形→詞位辭典")
    parser.add_argument("--write", action="store_true", help="寫出 koine-lexicon.json")
    args = parser.parse_args()

    payload = build()
    tagged = payload["wordsTagged"]
    print(f"  新約標註 {tagged['newTestament']} 詞次、七十士標註 {tagged['septuagint']} 詞次")
    print(f"  字形 {payload['formCount']}、通用希臘文詞位 {payload['lemmaCount']}")
    print(f"  另存重音敏感字形 {len(payload['exactForms'])} 筆，供 ἕξ／ἐξ 這類最小對立詞辨別")
    ambiguous = sum(1 for values in payload["forms"].values() if len(values) > 1)
    print(f"  一形多位者 {ambiguous}（{ambiguous * 100 // max(payload['formCount'], 1)}%），依標註次數排序")

    for probe in ("σου", "ἐγένετο", "χρυσοῦν", "εἶπεν"):
        options = payload["forms"].get(fold(probe), [])
        print(f"    {probe:<10s} → {'、'.join(options[:3]) or '（無）'}")

    if args.write:
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        print(f"已寫出 {OUTPUT}（{OUTPUT.stat().st_size / 1_048_576:.1f} MB）")
    else:
        print("（未寫檔；加 --write 才會輸出）")


if __name__ == "__main__":
    main()
