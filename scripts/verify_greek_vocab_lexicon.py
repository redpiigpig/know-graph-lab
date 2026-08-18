#!/usr/bin/env python3
"""Resolve the Greek vocabulary entries that no lexicon lookup had matched.

Thirty-five of the thousand entries shipped as ``source_verified_lexicon_pending``
with no Strong number and no English gloss.  None of them is a bad entry; the
first pass matched Strong's headwords by exact string, and Mounce prints:

* orthographic variants Strong's spells differently (σῴζω / σώζω, ἀποθνῄσκω,
  Καφαρναούμ, τεσσεράκοντα, Ἡρῴδης, ζῷον, κρείσσων, Δαυίδ);
* **inflected forms** taught as vocabulary in their own right (εἶπεν, ἀπεκρίθη,
  ἔφη), which are not lexicon headwords at all;
* entries whose printed form lists alternants (οὐ (οὐκ, οὐχ), ἕνεκα or ἕνεκεν).

So the resolution runs against the frozen sources rather than against a guess:
an accent- and breathing-insensitive index of Strong's headwords, and — when a
form is not a headword — the SBLGNT itself, which knows the lemma of every word
it contains.  The resolution path is recorded per entry, and anything still
unresolved is reported rather than filled in.

The printed entry, headword, lemma, lesson and Mounce transliteration are never
touched; only ``strong``, ``glossEn``, ``verification`` and the new
``lexiconResolution`` field are written.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import greek_source_texts as sources


ROOT = Path(__file__).resolve().parents[1]
VOCAB = ROOT / "data" / "originalReaders" / "vocabulary" / "greek-1000.json"
STRONGS = (
    ROOT
    / "output"
    / "source-cache"
    / "original-readers"
    / "strongs-src"
    / "strongs-master"
    / "greek"
    / "strongs-greek-dictionary.js"
)

DODSON = (
    ROOT
    / "output"
    / "source-cache"
    / "original-readers"
    / "greek-full"
    / "sources"
    / "dodson"
    / "dodson.xml"
)

STRONGS_EDITION = "Strong's Greek Dictionary (1890), Open Scriptures JSON edition, CC BY-SA"
DODSON_EDITION = "John Jeffrey Dodson, Greek Lexicon (biblicalhumanities edition, CC0)"
DODSON_URL = (
    "https://raw.githubusercontent.com/biblicalhumanities/"
    "Dodson-Greek-Lexicon/master/dodson.xml"
)


def fold(word: str) -> str:
    """Accent-, breathing- and iota-subscript-insensitive comparison key.

    Mounce, Strong and the SBLGNT disagree constantly about accents, breathings
    and whether an iota is subscript or adscript, while agreeing about the
    letters.  Folding to bare lower-case letters lets the letters decide, and
    the disagreement is reported instead of being silently normalised away.
    """
    decomposed = unicodedata.normalize("NFD", word)
    letters = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    letters = unicodedata.normalize("NFC", letters).lower()
    return letters.replace("ς", "σ")


def load_strongs() -> dict[str, list[tuple[str, dict]]]:
    text = STRONGS.read_text(encoding="utf-8")
    payload = json.loads(text[text.find("{") : text.rfind("}") + 1])
    index: dict[str, list[tuple[str, dict]]] = {}
    for number, entry in payload.items():
        lemma = (entry.get("lemma") or "").strip()
        if not lemma:
            continue
        index.setdefault(fold(lemma), []).append((number, entry))
    return index


def load_dodson() -> dict[str, list[tuple[str, dict]]]:
    """Dodson keyed by lemma, in the spelling modern editions actually use.

    Strong's 1890 headwords are often a different spelling of the same word
    (Δαβίδ for Δαυίδ, εἴδω for οἶδα, δεικνύω for δείκνυμι, Καπερναούμ for
    Καφαρναούμ), which is why matching Mounce against Strong alone leaves a
    residue.  Dodson is CC0, carries the Strong number itself, and lemmatises
    the way MorphGNT does, so it closes the gap without inventing letter rules.
    """
    index: dict[str, list[tuple[str, dict]]] = {}
    if not DODSON.exists():
        # A 1.3 MB build input, not a source of record: fetch it rather than
        # carrying it in the repository.
        DODSON.parent.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(
            DODSON_URL, headers={"User-Agent": "private-authorized-original-reader/1.0"}
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            DODSON.write_bytes(response.read())
        print(f"  已下載 Dodson 詞典 → {DODSON}")
    tree = ET.parse(DODSON)
    for entry in tree.iter():
        if not entry.tag.endswith("}entry") and entry.tag != "entry":
            continue
        name = entry.get("n") or ""
        if "|" not in name:
            continue
        lemma, _, number = name.partition("|")
        lemma, number = lemma.strip(), number.strip()
        definitions = {}
        for child in entry:
            tag = child.tag.rsplit("}", 1)[-1]
            if tag == "def":
                definitions[child.get("role") or "brief"] = re.sub(
                    r"\s+", " ", "".join(child.itertext())
                ).strip()
        if not lemma or not number.isdigit():
            continue
        payload = {
            "lemma": lemma,
            "strongs_def": definitions.get("brief", ""),
            "kjv_def": definitions.get("full", ""),
        }
        index.setdefault(fold(lemma), []).append((f"G{int(number)}", payload))
    return index


def load_sblgnt_forms() -> tuple[dict[str, Counter], dict[str, Counter]]:
    """Map folded surface forms and folded lemmas to the lemmas actually used."""
    forms: dict[str, Counter] = {}
    lemmas: dict[str, Counter] = {}
    for osis_book in sources.SBLGNT_BOOKS:
        path = sources.sblgnt_path(osis_book)
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) != 7:
                continue
            _, _, _, _, word, _, lemma = parts
            forms.setdefault(fold(word), Counter())[lemma] += 1
            lemmas.setdefault(fold(lemma), Counter())[lemma] += 1
    return forms, lemmas


def clean_gloss(entry: dict) -> str:
    gloss = (entry.get("strongs_def") or "").strip()
    if not gloss:
        gloss = (entry.get("kjv_def") or "").strip()
    return re.sub(r"\s+", " ", gloss).strip(" ;.")


ARTICLES = {"ο", "η", "το", "οι", "αι", "τα"}


def headword_candidates(entry: dict) -> list[str]:
    """Every spelling the printed entry offers, headword first.

    Only the headword and its explicit alternants count.  A Mounce noun entry is
    "λόγος, -ου, ὁ" and an indeclinable is "Δαυίδ, ὁ": everything after the first
    comma is a genitive ending or a gender article, and feeding those to the
    lookup is how an earlier pass matched Δαυίδ to the article G3588 and Μαριάμ
    to G2229 — after accents are folded away, ἡ and ἦ are the same letters.
    """
    printed = entry.get("printedEntry") or ""
    head = printed.split(",")[0].strip()
    candidates = [entry.get("headword") or "", entry.get("lemma") or "", head]
    # "οὐ (οὐκ, οὐχ)" and "ἕνεκα or ἕνεκεν" list real alternants of the headword.
    for chunk in re.split(r"[(),]|\bor\b", printed if "(" in printed or " or " in printed else head):
        chunk = chunk.strip()
        if chunk and not chunk.startswith("-") and fold(chunk) not in ARTICLES:
            candidates.append(chunk)
    seen, ordered = set(), []
    for candidate in candidates:
        if candidate and fold(candidate) not in ARTICLES and candidate not in seen:
            seen.add(candidate)
            ordered.append(candidate)
    return ordered


# Mounce, Strong and MorphGNT lemmatise the same verb under different voices and
# dialect spellings.  These are the alternations that actually separate them in
# this thousand-word list; each is reversible and letter-level, so a match found
# through one is still a match on letters, not a guess about meaning.
VARIANTS: tuple[tuple[str, str], ...] = (
    ("ομαι", "ω"),
    ("εομαι", "εω"),
    ("ω", "ομαι"),
    ("εω", "εομαι"),
    ("σσ", "ττ"),
    ("ττ", "σσ"),
)


def variant_keys(key: str) -> list[str]:
    keys = [key]
    if key.endswith("σ"):
        keys.append(key[:-1])
    else:
        keys.append(key + "σ")
    for suffix, replacement in VARIANTS:
        if key.endswith(suffix):
            keys.append(key[: -len(suffix)] + replacement)
        if suffix in key:
            keys.append(key.replace(suffix, replacement))
    seen, ordered = set(), []
    for candidate in keys:
        if candidate not in seen:
            seen.add(candidate)
            ordered.append(candidate)
    return ordered


def _strong_answer(path: str, matched: str, matches, extra: dict | None = None) -> dict:
    number, found = matches[0]
    answer = {
        "path": path,
        "matchedOn": matched,
        "strongsLemma": found.get("lemma", ""),
        "strong": number,
        "glossEn": clean_gloss(found),
        "ambiguous": len(matches) > 1,
    }
    answer.update(extra or {})
    return answer


def look_up(key: str, dodson, strongs):
    """Dodson first, then Strong; either way the caller learns which one hit."""
    matches = dodson.get(key)
    if matches:
        return matches, DODSON_EDITION
    matches = strongs.get(key)
    if matches:
        return matches, STRONGS_EDITION
    return None, ""


def resolve(entry: dict, strongs, dodson, forms, lemmas) -> dict | None:
    candidates = headword_candidates(entry)

    # 1. The printed headword, letters only.
    for candidate in candidates:
        matches, edition = look_up(fold(candidate), dodson, strongs)
        if matches:
            return _strong_answer("lexicon_headword", candidate, matches, {"edition": edition})

    # 2. The SBLGNT's lemma inventory, which uses modern lemmatisation.
    for candidate in candidates:
        counts = lemmas.get(fold(candidate))
        if not counts:
            continue
        lemma = counts.most_common(1)[0][0]
        for key in variant_keys(fold(lemma)):
            matches, edition = look_up(key, dodson, strongs)
            if matches:
                return _strong_answer(
                    "sblgnt_lemma", candidate, matches,
                    {"sblgntLemma": lemma, "edition": edition},
                )
        # A corpus lemma with no lexicon headword is still real evidence.
        return {
            "path": "sblgnt_lemma_no_lexicon",
            "matchedOn": candidate,
            "sblgntLemma": lemma,
            "strongsLemma": "",
            "strong": "",
            "glossEn": "",
            "edition": sources.SBLGNT_EDITION,
            "ambiguous": False,
        }

    # 3. An inflected form taught as vocabulary (εἶπεν, ἀπεκρίθη, ἔφη).
    for candidate in candidates:
        counts = forms.get(fold(candidate))
        if not counts:
            continue
        lemma = counts.most_common(1)[0][0]
        for key in variant_keys(fold(lemma)):
            matches, edition = look_up(key, dodson, strongs)
            if matches:
                return _strong_answer(
                    "sblgnt_form_to_lemma", candidate, matches,
                    {"sblgntLemma": lemma, "edition": edition},
                )

    # 4. Voice or dialect variants of the printed headword itself.
    for candidate in candidates:
        for key in variant_keys(fold(candidate)):
            matches, edition = look_up(key, dodson, strongs)
            if matches:
                return _strong_answer(
                    "lexicon_variant_spelling", candidate, matches, {"edition": edition}
                )
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="用凍結來源補齊未匹配的希臘文詞條")
    parser.add_argument("--write", action="store_true", help="寫回詞彙主檔")
    args = parser.parse_args()

    entries = json.loads(VOCAB.read_text(encoding="utf-8"))
    strongs = load_strongs()
    dodson = load_dodson()
    forms, lemmas = load_sblgnt_forms()
    print(
        f"Strong 詞條 {sum(len(v) for v in strongs.values())}；"
        f"Dodson 詞條 {sum(len(v) for v in dodson.values())}；SBLGNT 字形 {len(forms)}"
    )

    pending = [e for e in entries if e["verification"] != "source_and_lexicon_matched"]
    resolved = unresolved = 0
    for entry in pending:
        answer = resolve(entry, strongs, dodson, forms, lemmas)
        if not answer:
            unresolved += 1
            print(f"  ✗ #{entry['ordinal']:>4d} {entry['printedEntry']} — 三個來源都查不到，留待人工")
            continue
        resolved += 1
        if answer["strong"]:
            entry["strong"] = answer["strong"]
        if not entry.get("glossEn"):
            entry["glossEn"] = answer["glossEn"]
        # A word confirmed by the corpus but absent from both lexicons is not
        # "lexicon matched".  Μωϋσῆς / Μαριάμ / πίμπλημι / τεσσεράκοντα /
        # Καφαρναούμ are the critical text's spellings of words the 1890
        # lexicons file under their Textus Receptus forms (Μωσεύς, Μαρία,
        # πλήθω, τεσσαράκοντα, Καπερναούμ).  Forcing those together would need
        # φ↔π and α↔ε rules that are false in general, so the narrower true
        # state is recorded and the pair is left for a human to confirm.
        entry["verification"] = (
            "source_and_corpus_matched"
            if answer["path"] == "sblgnt_lemma_no_lexicon"
            else "source_and_lexicon_matched"
        )
        entry["lexiconResolution"] = {
            "path": answer["path"],
            "matchedOn": answer["matchedOn"],
            "strongsLemma": answer["strongsLemma"],
            "edition": answer.get("edition", ""),
        }
        if "sblgntLemma" in answer:
            entry["lexiconResolution"]["sblgntLemma"] = answer["sblgntLemma"]
        # The printed spelling stays authoritative; a disagreement with the
        # lexicon is recorded, never corrected.
        if fold(entry["headword"]) == fold(answer["strongsLemma"]) and \
                entry["headword"] != answer["strongsLemma"]:
            entry["lexiconResolution"]["orthographyNote"] = (
                f"課本作 {entry['headword']}，Strong 作 {answer['strongsLemma']}；"
                "以課本印刷形為準。"
            )
        note = entry["lexiconResolution"].get("orthographyNote", "")
        print(
            f"  ✓ #{entry['ordinal']:>4d} L{entry['lesson']:>2d} {entry['printedEntry']:<30s}"
            f" → {answer['strong']:<7s} {answer['path']:<22s} {note[:40]}"
        )

    print(f"  解出 {resolved}／{len(pending)}，仍待人工 {unresolved}")
    corpus_only = [e for e in entries if e["verification"] == "source_and_corpus_matched"]
    if corpus_only:
        print(f"  只有語料佐證、兩本詞典都查不到的拼法（{len(corpus_only)} 筆，待人工確認）：")
        for entry in corpus_only:
            lemma = entry.get("lexiconResolution", {}).get("sblgntLemma", "")
            print(f"      #{entry['ordinal']:>4d} L{entry['lesson']:>2d} {entry['printedEntry']}"
                  f"  SBLGNT 詞位 {lemma}")
    unverified = sum(
        1 for e in entries
        if e["verification"] not in {"source_and_lexicon_matched", "source_and_corpus_matched"}
    )
    print(f"  詞彙主檔剩餘完全未核驗 {unverified}／{len(entries)}")

    if args.write:
        VOCAB.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已寫回 {VOCAB}")
    else:
        print("（未寫檔；加 --write 才會更新主檔）")


if __name__ == "__main__":
    main()
