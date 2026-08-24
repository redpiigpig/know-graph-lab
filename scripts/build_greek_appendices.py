#!/usr/bin/env python3
"""Build the reader's six appendices.

The fifty lessons of each volume hold exactly twenty words apiece, which leaves
no room for the words a reader meets constantly but never has to drill: the
names, the numerals, the kinship terms, the calendar, the offices of the church.
Frequency counting handles them badly too.  Left in, Ἰσραήλ and Μωϋσῆς would
take the top of the Septuagint list and push out real vocabulary; left out, a
reader opening Judith meets Ὀλοφέρνης with nothing to go on.

So they go in appendices instead, outside the lesson count, arranged by kind
rather than by frequency, to be consulted rather than memorised:

    一 人名、地名與國族     二 數字與度量衡
    三 親屬稱謂             四 曆法與節期
    五 教會職分與禮儀用語

The names are harvested: a lemma written with a capital in at least four of
every five appearances is a name, whichever corpus it is in.  The other four are
curated by category and then checked against the corpora, so each entry says how
often it actually occurs in what this reader prints, and which entries occur
nowhere - a curated list that is never checked drifts into listing words the
reader will never meet.

Chinese comes from the site's own 翻譯定名 glossary wherever the glossary knows
the Greek, because that register is authoritative here and a second rendering of
Ἀθῆναι invented locally would contradict it.  What the glossary does not cover
is left empty for the gloss pass, never guessed at.
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_greek_vocabulary_2000 as bv
import greek_source_texts as gs
from verify_greek_vocab_lexicon import fold


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "greek-full"
VOCABULARY = ROOT / "data" / "originalReaders" / "vocabulary" / "greek-2000.json"
OUTPUT = ROOT / "data" / "originalReaders" / "vocabulary" / "greek-appendices.json"

NAME_MINIMUM = 10          # below this a name is a walk-on part, not a fixture
CAPITAL_RATIO = 0.8

# Categories curated by hand, then verified against the corpora.  Grouped the way
# a reader would look them up rather than by how often they occur.
CURATED = {
    "numerals": {
        "title": "數字與度量衡",
        "groups": {
            "基數": "εἷς δύο τρεῖς τέσσαρες πέντε ἕξ ἑπτά ὀκτώ ἐννέα δέκα ἕνδεκα "
                    "δώδεκα εἴκοσι τριάκοντα τεσσαράκοντα πεντήκοντα ἑξήκοντα "
                    "ἑβδομήκοντα ὀγδοήκοντα ἐνενήκοντα ἑκατόν διακόσιοι τριακόσιοι "
                    "τετρακόσιοι πεντακόσιοι χίλιοι δισχίλιοι μύριοι",
            "序數": "πρῶτος δεύτερος τρίτος τέταρτος πέμπτος ἕκτος ἕβδομος ὄγδοος "
                    "ἔνατος δέκατος ἑνδέκατος δωδέκατος ἔσχατος",
            "倍數與分數": "ἥμισυς δίς τρίς ἑπτάκις ἑβδομηκοντάκις ἅπαξ πολλαπλασίων",
            "長度與容量": "πῆχυς σπιθαμή δάκτυλος στάδιον μίλιον κόρος βάτος "
                    "μετρητής χοῖνιξ μόδιος σάτον ξέστης γομόρ οἰφί",
            "錢幣與重量": "τάλαντον μνᾶ δηνάριον δραχμή στατήρ ἀσσάριον κοδράντης "
                    "λεπτόν σίκλος χρυσίον ἀργύριον",
        },
    },
    "kinship": {
        "title": "親屬稱謂",
        "groups": {
            "直系": "πατήρ μήτηρ υἱός θυγάτηρ τέκνον παιδίον βρέφος γονεύς πάππος "
                    "πρόγονος ἔκγονος πρωτότοκος μονογενής",
            "旁系": "ἀδελφός ἀδελφή ἀνεψιός θεῖος συγγενής δίδυμος",
            "姻親": "ἀνήρ γυνή νύμφη γαμβρός πενθερός πενθερά χήρα μνηστεύω γάμος",
            "族屬": "οἶκος πατριά φυλή γενεά σπέρμα γένος συγγένεια ὀρφανός παρθένος",
        },
    },
    "calendar": {
        "title": "曆法與節期",
        "groups": {
            "時辰與日夜": "ἡμέρα νύξ ἑσπέρα πρωΐ μεσημβρία ὥρα φυλακή ὄρθρος "
                    "σήμερον αὔριον ἐχθές",
            "週月年": "σάββατον ἑβδομάς μήν νουμηνία ἔτος ἐνιαυτός ἰωβηλαῖος "
                    "κυριακός παρασκευή",
            "以色列節期": "ἑορτή πάσχα ἄζυμος πεντηκοστή σκηνοπηγία ἐγκαίνια "
                    "νηστεία ἐξιλασμός σάλπιγξ",
            "教會節期": "ἀνάστασις γέννησις θεοφάνεια ὑπαπαντή μεταμόρφωσις "
                    "κοίμησις τεσσαρακοστή",
            "月名": "Νισάν Ἀδάρ Σιβάν Ἐλούλ Χασελεῦ Ξανθικός Δύστρος Δῖος "
                    "Ἀπελλαῖος Πάνημος",
        },
    },
    "offices": {
        "title": "教會職分與禮儀用語",
        "groups": {
            "新約職分": "ἀπόστολος προφήτης εὐαγγελιστής ποιμήν διδάσκαλος "
                    "ἐπίσκοπος πρεσβύτερος διάκονος ὑπηρέτης οἰκονόμος",
            "後期職分": "ἀρχιεπίσκοπος μητροπολίτης πατριάρχης ἡγούμενος μοναχός "
                    "ἀναγνώστης ψάλτης ὑποδιάκονος ἐξορκιστής θυρωρός "
                    "διακόνισσα κλῆρος λαϊκός",
            "按立": "χειροτονία χειροθεσία χειροτονέω καθίστημι διαδοχή τάξις",
            "聖事": "μυστήριον βάπτισμα χρῖσμα εὐχαριστία κοινωνία μετάνοια "
                    "ἐξομολόγησις εὐχέλαιον",
            "禮儀": "λειτουργία λειτουργός ἀναφορά προσκομιδή ἀνάμνησις ἐπίκλησις "
                    "ἀντίφωνον συναπτή ἐκτενής τροπάριον κοντάκιον ἀπολυτίκιον "
                    "ἀπόλυσις εὐλογία ἁγιασμός",
            "禮儀器物與呼求": "ἄρτος οἶνος ποτήριον δισκάριον θυμίαμα θυσιαστήριον "
                    "εἰκών ἀμήν ἀλληλούϊα ἐλεέω ἅγιος δόξα",
        },
    },
}


def nt_tokens():
    for book in gs.SBLGNT_BOOKS:
        path = gs.sblgnt_path(book)
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) == 7:
                yield unicodedata.normalize("NFC", parts[4])


def survey():
    """Every lemma in every corpus, with how often it is written with a capital.

    The reader's own texts are the evidence.  Each lemma also keeps the surface
    form it most often wears, because for a name the nominative is what a reader
    wants to see printed - and because a mis-analysed name is easier to catch
    there: Σηων filed under the verb σείω is obvious once the form is shown.
    """
    (koine_forms, koine_exact), koine_lemmas = bv.load_koine()
    morpheus, _ = bv.load_index()
    corpora = {
        "newTestament": nt_tokens(),
        "septuagint": bv.lxx_tokens(),
        "patristic": bv.patristic_tokens(),
    }
    counts: dict[str, Counter] = {}
    caps: Counter = Counter()
    forms: dict[str, Counter] = {}
    for name, tokens in corpora.items():
        counts[name] = Counter()
        for token in tokens:
            word = bv.clean(token)
            if not word or not bv.GREEK_RE.search(word):
                continue
            options = (koine_exact.get(word) or koine_forms.get(fold(word))
                       or morpheus.get(fold(word)))
            if not options:
                continue
            lemma = bv.to_koine(options[0], koine_lemmas)
            counts[name][lemma] += 1
            caps[lemma] += word[:1].isupper()
            forms.setdefault(lemma, Counter())[word] += 1
    return counts, caps, forms


def glossary_lookup() -> dict[str, dict]:
    """Greek headwords the site's 翻譯定名 glossary already rules on."""
    try:
        import os

        import requests
        from dotenv import load_dotenv
    except ImportError:
        print("  （缺少 requests 或 dotenv，略過詞庫對接）")
        return {}
    load_dotenv(ROOT / ".env")
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not (url and key):
        print("  （未設定 Supabase 憑證，略過詞庫對接）")
        return {}
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    tables = {
        "theologians": ("name_original", "name_recommended", "person"),
        "place_names": ("name_original", "name_recommended", "place"),
        "deities": ("name_original", "name_recommended", "deity"),
        "official_titles": ("name_original", "name_recommended", "office"),
    }
    found: dict[str, dict] = {}
    for table, (source, target, kind) in tables.items():
        response = requests.get(
            f"{url}/rest/v1/{table}",
            params={"select": f"{source},{target}", "limit": "5000"},
            headers=headers,
            timeout=60,
        )
        response.raise_for_status()
        for row in response.json():
            original = (row.get(source) or "").strip()
            recommended = (row.get(target) or "").strip()
            if original and recommended and bv.GREEK_RE.search(original):
                found.setdefault(fold(original), {
                    "zh": recommended, "kind": kind, "glossaryTable": table,
                })
    return found


def main() -> None:
    parser = argparse.ArgumentParser(description="建立讀本五個附錄")
    parser.add_argument("--write", action="store_true", help="寫出 greek-appendices.json")
    args = parser.parse_args()

    counts, caps, forms = survey()
    total: Counter = Counter()
    for corpus_counts in counts.values():
        total.update(corpus_counts)
    folded_total: dict[str, int] = {}
    for lemma, count in total.items():
        folded_total[fold(lemma)] = folded_total.get(fold(lemma), 0) + count

    glossary = glossary_lookup()
    print(f"  詞庫可對接的希臘原文 {len(glossary)} 筆")

    taught = {
        fold(entry["lemma"])
        for entry in json.loads(VOCABULARY.read_text(encoding="utf-8"))["entries"]
    }

    names = []
    for lemma, count in total.most_common():
        if count < NAME_MINIMUM or caps[lemma] < count * CAPITAL_RATIO:
            continue
        if fold(lemma) in taught:
            # Taught in a lesson, so not repeated here.  κύριος is written with a
            # capital throughout the Septuagint and looks like a name by that
            # test, but the textbook teaches it as a noun and that is where it
            # belongs.
            continue
        headword = forms[lemma].most_common(1)[0][0]
        known = glossary.get(fold(lemma)) or glossary.get(fold(headword)) or {}
        names.append({
            "headword": headword,
            "lemma": lemma,
            "frequency": count,
            "byCorpus": {k: v[lemma] for k, v in counts.items() if v[lemma]},
            "kind": known.get("kind", ""),
            "zh": known.get("zh", ""),
            "zhSource": known.get("glossaryTable", ""),
        })
    named = sum(1 for item in names if item["zh"])
    print(f"  附錄一 專名 {len(names)} 條（出現 ≥{NAME_MINIMUM} 次）；"
          f"詞庫已定名 {named}，待定名 {len(names) - named}")

    appendices = []
    for key, spec in CURATED.items():
        entries, missing = [], []
        for group, words in spec["groups"].items():
            for word in words.split():
                count = total.get(word, 0) or folded_total.get(fold(word), 0)
                known = glossary.get(fold(word)) or {}
                entries.append({
                    "lemma": word, "group": group, "frequency": count,
                    "attested": bool(count), "zh": known.get("zh", ""),
                    "zhSource": known.get("glossaryTable", ""),
                    "inLessons": fold(word) in taught,
                })
                if not count:
                    missing.append(word)
        appendices.append({"key": key, "title": spec["title"], "entries": entries})
        print(f"  {spec['title']} {len(entries)} 條；語料未見 {len(missing)} 條"
              + (f"：{'、'.join(missing)}" if missing else ""))

    payload = {
        "schemaVersion": "1.0.0",
        "note": (
            "附錄不計入每課二十詞。專名以語料大小寫判定（同一詞位八成以上首字大寫），"
            "分類與中文以站上「翻譯定名」詞庫為準；詞庫未收者留空待補，不自行擬名。"
            "策展類附錄的 frequency 為本讀本所印語料中的實際出現次數，"
            "attested 為 false 者表示語料未見，供檢討是否該列。"
        ),
        "nameThreshold": NAME_MINIMUM,
        "appendices": [
            {"key": "names", "title": "人名、地名與國族", "entries": names},
            *appendices,
        ],
    }
    if args.write:
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已寫出 {OUTPUT}")
    else:
        print("（未寫檔；加 --write 才會輸出）")


if __name__ == "__main__":
    main()
