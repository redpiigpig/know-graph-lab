#!/usr/bin/env python3
"""A three-register lemma lexicon for fifteen centuries of church Latin.

One inventory will not do.  Building it from the Vulgate alone leaves the later
volume stranded -- Jerome barely uses scilicet, praesertim or res, so a
scholastic page comes back two-thirds unresolved.  Building it from Classical
Latin alone repeats the Greek reader's Attic mistake in Latin dress, heading
Jerome's vocabulary with Cicero's lemmas.

So three registers are read separately and merged in a fixed precedence:

    vulgate  PROIEL's Jerome sentences .................. 110k tokens
    church   Index Thomisticus (Aquinas), the Late Latin
             Charter Treebank, and Dante's Latin ......... 749k tokens
    classic  PROIEL's Caesar/Cicero/Palladius, Perseus,
             CIRCSE ...................................... 265k tokens

Where two registers tag the same form, the earlier one in that list wins, and
the form records which register named it.  That ordering is the whole point:
the reader teaches ecclesiastical Latin, so when Jerome and Cicero disagree
about what a form's dictionary entry is, Jerome decides.

Proper names are detected from each corpus's own capitalisation rather than
from a list, because a name that only the charters use will never be in a list
someone wrote for the Bible.
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
OUTPUT = CACHE / "latin-lexicon.json"

VULGATE_MARK = "Jerome's Vulgate"

REGISTERS = (
    ("vulgate", ("UD_Latin-PROIEL-master",), "vulgate-only"),
    ("church", ("UD_Latin-ITTB-master", "UD_Latin-LLCT-master", "UD_Latin-UDante-master"), "all"),
    ("classic", ("UD_Latin-PROIEL-master", "UD_Latin-Perseus-master", "UD_Latin-CIRCSE-master"), "non-vulgate"),
)


def read(dirs: tuple[str, ...], filter_mode: str):
    freq: Counter = Counter()
    exact: dict[str, Counter] = defaultdict(Counter)
    folded: dict[str, Counter] = defaultdict(Counter)
    pos: dict[str, Counter] = defaultdict(Counter)
    caps: dict[str, list[int]] = defaultdict(lambda: [0, 0])

    for name in dirs:
        for path in sorted((CACHE / name).glob("*.conllu")):
            keep = filter_mode == "all"
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.startswith("# source"):
                    is_vulgate = VULGATE_MARK in line
                    keep = is_vulgate if filter_mode == "vulgate-only" else (
                        not is_vulgate if filter_mode == "non-vulgate" else True
                    )
                    continue
                if not line or line.startswith("#") or not keep:
                    continue
                cols = line.split("\t")
                if len(cols) < 4 or "-" in cols[0]:
                    continue
                form, lemma, tag = cols[1], cols[2], cols[3]
                if tag == "PUNCT" or not lemma or lemma in {"_", ""}:
                    continue
                lemma = lemma.strip()
                freq[lemma] += 1
                exact[form][lemma] += 1
                folded[L.fold(form)][lemma] += 1
                pos[lemma][tag] += 1
                seen = caps[lemma]
                seen[0] += 1
                if form[:1].isupper():
                    seen[1] += 1

    names = {l for l, (total, upper) in caps.items() if total >= 3 and upper / total >= 0.8}
    return freq, exact, folded, pos, names


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    merged_exact: dict[str, str] = {}
    merged_folded: dict[str, str] = {}
    route: dict[str, str] = {}
    payload: dict = {"registers": {}, "license": {
        "UD_Latin-PROIEL": "CC BY-NC-SA 4.0",
        "UD_Latin-ITTB": "CC BY-NC-SA 3.0",
        "UD_Latin-LLCT": "CC BY-SA 4.0",
        "UD_Latin-UDante": "CC BY-SA 4.0",
        "UD_Latin-Perseus": "CC BY-NC-SA 2.5",
        "UD_Latin-CIRCSE": "CC BY-SA 4.0",
    }}
    all_pos: dict[str, str] = {}
    all_names: dict[str, str] = {}

    for register, dirs, mode in REGISTERS:
        freq, exact, folded, pos, names = read(dirs, mode)
        payload["registers"][register] = {
            "tokens": sum(freq.values()),
            "lemmas": len(freq),
            "frequency": dict(freq.most_common()),
        }
        for form, counts in exact.items():
            if form not in merged_exact:
                merged_exact[form] = counts.most_common(1)[0][0]
                route[form] = register
        for key, counts in folded.items():
            merged_folded.setdefault(key, counts.most_common(1)[0][0])
        for lemma, counts in pos.items():
            all_pos.setdefault(lemma, counts.most_common(1)[0][0])
        for lemma in names:
            all_names.setdefault(lemma, register)
        print(f"{register:8s} tokens {sum(freq.values()):>8,}  lemmas {len(freq):>6,}  專名 {len(names):>4}")

    payload["exactForms"] = merged_exact
    payload["foldedForms"] = merged_folded
    payload["formRegister"] = route
    payload["pos"] = all_pos
    payload["properNames"] = all_names
    print(f"merged exact {len(merged_exact):,}；folded {len(merged_folded):,}；專名 {len(all_names):,}")
    if args.write:
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        print("→", OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
