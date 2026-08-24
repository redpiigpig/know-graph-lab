#!/usr/bin/env python3
"""The reader's ten appendix tables, split between its two volumes.

Fifty lessons of twenty words leave no room for the words a reader meets
constantly but never has to drill, and frequency counting handles them badly
besides: left in, Israel and Moyses take the top of any Vulgate list and push
out vocabulary; left out, someone opening Judith meets Holofernes with nothing
to go on.  So they go into appendices, arranged by kind rather than by
frequency, to be consulted rather than memorised.

Five tables face the Bible and five face the church, because this reader spans
fifteen centuries and its two halves need different reference shelves.  A reader
of the Vulgate needs the Roman measures and the biblical feasts; a reader of a
papal bull needs the Kalends, the abbreviations of the curia, and the Latin
names of modern countries.  Two of these tables have no counterpart in the
Hebrew or Greek readers at all -- how the Holy See writes today's nation-states,
and how it dates a document -- and they are the part of this reader that could
not have been carried over from either.

Chinese for the proper names is read out of the aligned translation rather than
recalled.  The Studium Biblicum edition underlines every proper name in its
verse text, so a Latin name's Chinese is whichever underlined name appears in
most of the verses that Latin name appears in, and is rare elsewhere.  That is
evidence.  Where the evidence does not reach -- a name outside the fifty printed
chapters -- the cell stays empty, and every filled cell records how it was
filled.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import latin_source_texts as L  # noqa: E402
import latin_dictionary as W  # noqa: E402
from latin_lemmatiser import Lemmatiser  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
CHURCH = CACHE / "latin-church"
SIGAO = CACHE / "sigao-zh.json"
SCRIPTURE_PLAN = CACHE / "scripture-plan.json"
OUTPUT = ROOT / "data" / "originalReaders" / "vocabulary" / "latin-appendices.json"

SENTENCE_RE = __import__('re').compile(r'[.;:?!]')

NAME_MINIMUM = 8          # below this a name is a walk-on part, not a fixture

# Titles of God rather than names of people, and the reader learns them as
# vocabulary in the first units.  They are still harvested -- they are
# capitalised throughout the Vulgate -- but the table says what they are so the
# name list does not open with five words that are not names of anybody.
DIVINE = {"dominus", "deus", "christus", "iesus", "spiritus sanctus", "altissimus",
          "emmanuel", "messias", "sabaoth", "adonai", "pater", "agnus"}
CAPITAL_RATIO = 0.8

CURATED_UPPER = {
    "numerals": {
        "title": "數字、羅馬數字與度量衡",
        "groups": {
            "基數": "unus duo tres quattuor quinque sex septem octo novem decem undecim "
                    "duodecim viginti triginta quadraginta quinquaginta sexaginta "
                    "septuaginta octoginta nonaginta centum ducenti trecenti "
                    "quadringenti quingenti mille",
            "序數": "primus secundus tertius quartus quintus sextus septimus octavus "
                    "nonus decimus undecimus duodecimus novissimus",
            "分配數與數副詞": "singuli bini terni quaterni semel bis ter quater quinquies "
                    "decies centies milies dimidium tertia pars",
            "長度與容量": "cubitus palmus digitus stadium milia passuum modius satum "
                    "batus corus hin gomor sextarius mensura",
            "錢幣與重量": "talentum mina denarius drachma stater as quadrans minutum "
                    "siclus argentum aurum libra uncia",
        },
    },
    "kinship": {
        "title": "親屬稱謂",
        "groups": {
            "直系": "pater mater filius filia parens avus avia proavus nepos neptis "
                    "primogenitus unigenitus infans puer puella",
            "旁系": "frater soror patruus amita avunculus matertera consobrinus "
                    "cognatus propinquus gemini",
            "姻親": "vir uxor maritus sponsus sponsa socer socrus gener nurus levir "
                    "vidua orphanus nuptiae",
            "家族與世系": "familia domus tribus cognatio generatio semen stirps posteritas "
                    "haeres hereditas",
        },
    },
    "calendar": {
        "title": "羅馬曆、月份與聖經節期",
        "groups": {
            "羅馬記日法": "kalendae nonae idus pridie postridie ante diem annus mensis dies "
                    "hora vigilia saeculum",
            "月份": "Ianuarius Februarius Martius Aprilis Maius Iunius Iulius Augustus "
                    "September October November December",
            "聖經節期": "pascha azyma pentecoste scenopegia expiatio neomenia sabbatum "
                    "iubilaeus encaenia",
            "時段": "mane vesper meridies nox hodie cras heri semper aeternum",
        },
    },
}

CURATED_LOWER = {
    "offices": {
        "title": "教會職分、聖統與禮儀用語",
        "groups": {
            "聖統": "papa pontifex episcopus archiepiscopus patriarcha cardinalis "
                    "presbyter sacerdos diaconus subdiaconus clericus laicus "
                    "abbas prior monachus monialis",
            "職務與機構": "curia congregatio dicasterium synodus concilium conclave "
                    "dioecesis paroecia provincia sedes cathedra vicarius legatus "
                    "nuntius protonotarius",
            "彌撒各部": "introitus kyrie gloria collecta lectio graduale alleluia "
                    "evangelium homilia credo offertorium praefatio sanctus canon "
                    "consecratio communio postcommunio benedictio",
            "聖事與禮儀": "sacramentum baptismus confirmatio eucharistia paenitentia "
                    "unctio ordo matrimonium missa liturgia officium breviarium "
                    "altare hostia calix",
        },
    },
    "liturgical_year": {
        "title": "禮儀年與時辰誦讀",
        "groups": {
            "禮儀時節": "adventus nativitas epiphania quadragesima passio resurrectio "
                    "ascensio pentecoste tempus per annum",
            "慶典等級": "sollemnitas festum memoria feria dominica vigilia octava",
            "時辰": "matutinum laudes prima tertia sexta nona vesperae completorium "
                    "horae psalterium antiphona responsorium hymnus canticum",
        },
    },
    "documents": {
        "title": "教廷文獻體裁與公文用語",
        "groups": {
            "文獻體裁": "bulla breve constitutio decretum decretalis encyclica exhortatio "
                    "epistula allocutio motu proprio rescriptum indultum privilegium",
            "公文套語": "datum actum praesentibus venerabilis dilectus salutem "
                    "apostolica benedictio perpetuam memoriam mandamus statuimus "
                    "declaramus definimus promulgamus",
            "法律用語": "canon ius lex praeceptum obligatio dispensatio censura "
                    "excommunicatio anathema irritus nullus vigor",
        },
    },
    "scholastic": {
        "title": "經院哲學與神學術語",
        "groups": {
            "存有與本質": "ens essentia existentia substantia accidens natura suppositum "
                    "quidditas subsistentia persona",
            "因果與變化": "causa effectus actus potentia forma materia finis principium "
                    "motus generatio corruptio",
            "認識": "intellectus ratio voluntas species phantasma abstractio conceptus "
                    "scientia sapientia fides",
            "神學": "gratia natura meritum praedestinatio iustificatio satisfactio "
                    "transsubstantiatio processio missio visio beatifica",
        },
    },
}


def harvest_names(units, lm, minimum: int) -> dict[str, int]:
    """Find the names in a corpus given as units of running text.

    Three things have to be right or the table fills with words that are not
    names.  Capitalisation has to be counted away from the start of a unit,
    because ``Cumque`` opens hundreds of Vulgate verses and is a conjunction.
    Counting has to be by lemma, or ``Dominus``, ``Domini``, ``Domino``,
    ``Dominum`` and ``Domine`` arrive as five separate names.  And a token that
    the treebanks already know as a common word is not promoted to a name however
    it is capitalised.
    """
    seen: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for unit in units:
        # Split into sentences first: a whole encyclical has one first word, and
        # judging capitalisation against that would let every sentence-initial
        # word through.
        for sentence in SENTENCE_RE.split(unit):
            words = L.words(sentence)
            for position, word in enumerate(words):
                lemma = lm.lemma(word)
                key = L.fold(lemma) if lemma else L.fold(word)
                seen[key][0] += 1
                if position and word[:1].isupper():
                    seen[key][1] += 1
    return {
        key: total
        for key, (total, upper) in seen.items()
        if total >= minimum and upper / total >= CAPITAL_RATIO
    }


def surface_forms(corpus_words) -> dict[str, Counter]:
    """Every capitalised spelling seen for each folded key, counted once.

    Built in a single pass on purpose.  Asking for one name's commonest spelling
    by re-scanning the corpus is fine; asking it five hundred times over three
    million words is a quarter of a billion comparisons, and it is why the first
    version of this script never finished.
    """
    forms: dict[str, Counter] = defaultdict(Counter)
    for word in corpus_words:
        if word[:1].isupper():
            forms[L.fold(word)][word] += 1
    return forms


def display_form(forms: dict[str, Counter], folded: str) -> str:
    """Print the name the way the edition prints it, not the way we folded it."""
    seen = forms.get(folded)
    return seen.most_common(1)[0][0] if seen else folded


def align_chinese(latin_names: set[str], lm) -> dict[str, dict]:
    """Read each name's Chinese out of the aligned Studium Biblicum chapters.

    The edition underlines its proper names, so each verse offers a small
    candidate set rather than a whole sentence to guess from.  A Latin name is
    matched to whichever candidate shares the most verses with it, provided that
    candidate is not simply common everywhere.
    """
    if not SIGAO.exists():
        return {}
    data = json.loads(SIGAO.read_text(encoding="utf-8"))
    latin_chapters = L.vulgate_chapters()

    by_latin: dict[str, Counter] = defaultdict(Counter)
    latin_verse_total: Counter = Counter()
    chinese_verse_total: Counter = Counter()

    # Match on book and chapter, never on lesson number.  Lesson numbers are
    # assigned by the difficulty sort, so they move whenever the vocabulary
    # changes, while the Chinese export keeps the numbers it was written with.
    # Keying on them silently pairs Exodus 3 with John 17 and the alignment
    # collapses from fifty-six names to one -- which is exactly what happened.
    for chapter in data["chapters"]:
        verses = latin_chapters[(chapter["book"], chapter["latinChapter"])]
        chinese = {v["verse"]: v for v in chapter["verses"]}
        for number, text in verses.items():
            target = chinese.get(number)
            if not target:
                continue
            words = L.words(text)
            names_here = set()
            for position, word in enumerate(words):
                if not position or not word[:1].isupper():
                    continue
                lemma = lm.lemma(word)
                key = L.fold(lemma) if lemma else L.fold(word)
                if key in latin_names:
                    names_here.add(key)
            zh_here = {n for n in target["properNames"] if n}
            for name in names_here:
                latin_verse_total[name] += 1
                for zh in zh_here:
                    by_latin[name][zh] += 1
            for zh in zh_here:
                chinese_verse_total[zh] += 1

    resolved: dict[str, dict] = {}
    for name, counts in by_latin.items():
        best, hits = counts.most_common(1)[0]
        appearances = latin_verse_total[name]
        # Two guards: the candidate must follow this name through most of its
        # verses, and it must not be a name that follows everything.
        if hits < max(2, appearances * 0.6):
            continue
        if chinese_verse_total[best] > hits * 2.5:
            continue
        resolved[name] = {
            "zh": best, "sharedVerses": hits, "latinVerses": appearances,
            "route": "sigao-underline-alignment",
        }
    return resolved


def taught_headwords() -> set[str]:
    path = ROOT / "data" / "originalReaders" / "vocabulary" / "latin-2000.json"
    if not path.exists():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    return {L.fold(entry["headword"]) for entry in data["entries"]}


def names_in_printed_chapters(latin_names: set[str], lm) -> set[str]:
    """The subset a reader of these fifty chapters will actually run into."""
    if not SCRIPTURE_PLAN.exists():
        return set()
    plan = json.loads(SCRIPTURE_PLAN.read_text(encoding="utf-8"))
    chapters = L.vulgate_chapters()
    seen: set[str] = set()
    for row in plan["chapters"]:
        for text in chapters[(row["book"], row["chapter"])].values():
            for position, word in enumerate(L.words(text)):
                if not position or not word[:1].isupper():
                    continue
                lemma = lm.lemma(word)
                key = L.fold(lemma) if lemma else L.fold(word)
                if key in latin_names:
                    seen.add(key)
    return seen


def curated_table(spec: dict, counts: Counter, words_index) -> dict:
    rows = []
    for group, words in spec["groups"].items():
        for word in words.split():
            hits = words_index.get(L.fold(word), [])
            best = hits[0] if hits else None
            rows.append({
                "group": group,
                "headword": best.lemma if best else word,
                "forms": best.form if best else word,
                "glossEn": best.definition if best else "",
                "pos": best.pos if best else "",
                "ecclesiastical": bool(best and best.ecclesiastical),
                "corpusFrequency": counts.get(L.fold(word), 0),
                "attested": counts.get(L.fold(word), 0) > 0,
                "dictionaryRoute": "whitakers-words" if best else "missing",
            })
    return {"title": spec["title"], "entries": rows}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    lm = Lemmatiser()
    words_index = W.index_by_lemma(W.load())

    vulgate_words = [w for text in L.vulgate_verses().values() for w in L.words(text)]
    church_words: list[str] = []
    for doc in L.church_documents():
        church_words.extend(L.words(doc["text"]))
    for path in sorted(CHURCH.rglob("*.txt")):
        church_words.extend(L.words(path.read_text(encoding="utf-8", errors="replace")))

    vulgate_counts = Counter(L.fold(w) for w in vulgate_words)
    church_counts = Counter(L.fold(w) for w in church_words)

    vulgate_forms = surface_forms(vulgate_words)
    church_forms = surface_forms(church_words)

    biblical_names = harvest_names(L.vulgate_verses().values(), lm, NAME_MINIMUM)
    chinese = align_chinese(set(biblical_names), lm)
    # Which names the reader actually meets is the number that matters.  A rate
    # quoted against every name in the Vulgate says the alignment failed when
    # what really happened is that five hundred of those names are in chapters
    # this reader does not print.
    in_reader = names_in_printed_chapters(set(biblical_names), lm)
    # The contract keeps names and lessons disjoint.  Deus, Christus, Israel and
    # Evangelium are capitalised throughout the Vulgate and so are harvested as
    # names, but Collins teaches them as vocabulary; a word cannot be in both.
    taught = taught_headwords()
    biblical_names = {k: v for k, v in biblical_names.items() if k not in taught}
    name_rows = []
    for folded, count in sorted(biblical_names.items(), key=lambda kv: -kv[1]):
        match = chinese.get(folded, {})
        name_rows.append({
            "headword": display_form(vulgate_forms, folded),
            "folded": folded,
            "vulgateFrequency": count,
            "type": "divine" if folded in DIVINE else "",
            "tier": "讀本所見" if folded in in_reader else "武加大其餘",
            "zh": match.get("zh", ""),
            "zhRoute": match.get("route", ""),
            "zhEvidence": (f"{match['sharedVerses']}/{match['latinVerses']} 節同現"
                           if match else ""),
        })

    # A name the Vulgate never uses but the modern curia does -- Taiuania,
    # Foederatae Civitates -- is the one register no earlier reader in this
    # series had to cover, so it gets a table of its own.
    modern_units = [doc["text"] for doc in L.church_documents()]
    modern_units += [path.read_text(encoding="utf-8", errors="replace")
                     for path in sorted(CHURCH.rglob("*.txt"))]
    modern_names = harvest_names(modern_units, lm, NAME_MINIMUM * 2)
    modern_names = {k: v for k, v in modern_names.items() if k not in taught}
    modern_rows = [
        {"headword": display_form(church_forms, folded), "folded": folded,
         "churchFrequency": count, "zh": "", "zhRoute": ""}
        for folded, count in sorted(modern_names.items(), key=lambda kv: -kv[1])
        if folded not in biblical_names
    ]

    principal_parts = [
        {"headword": e.lemma, "forms": e.form, "glossEn": e.definition,
         "conjugation": " ".join(e.codes[:2]), "kind": e.codes[2] if len(e.codes) > 2 else ""}
        for e in W.load()
        if e.pos == "V" and e.freq in {"A", "B"} and church_counts.get(L.fold(e.lemma), 0) + vulgate_counts.get(L.fold(e.lemma), 0) > 0
    ]

    payload = {
        "schemaVersion": "1.0.0",
        "generatedOn": date.today().isoformat(),
        "upper": {
            "names": {"title": "人名、地名、民族與國名（武加大）", "entries": name_rows},
            **{key: curated_table(spec, vulgate_counts, words_index)
               for key, spec in CURATED_UPPER.items()},
            "principalParts": {"title": "動詞主要部分與不規則變化",
                               "entries": sorted(principal_parts, key=lambda r: r["headword"])},
        },
        "lower": {
            **{key: curated_table(spec, church_counts, words_index)
               for key, spec in CURATED_LOWER.items()},
            "modernNames": {"title": "近現代教廷拉丁的地名、機構名與專名",
                            "entries": modern_rows[:400]},
        },
    }

    reader_rows = [r for r in name_rows if r["tier"] == "讀本所見"]
    named = sum(1 for r in reader_rows if r["zh"])
    print(f"聖經專名共 {len(name_rows)}；其中讀本五十章實際出現 {len(reader_rows)}，"
          f"已由思高逐節對位定出中文 {named}"
          f"（{named / max(len(reader_rows), 1) * 100:.0f}%）")
    print(f"其餘 {len(name_rows) - len(reader_rows)} 個只作查閱，中文從缺")
    print(f"近現代專名 {len(modern_rows)}（表列前 400）")
    for section in ("upper", "lower"):
        for key, table in payload[section].items():
            entries = table["entries"]
            attested = sum(1 for e in entries if e.get("attested", True))
            print(f"  {section:5s} {table['title']:<28s} {len(entries):>5} 條"
                  f"{'' if 'attested' not in (entries[0] if entries else {}) else f'，語料佐證 {attested}'}")
    if args.write:
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
        print("->", OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
