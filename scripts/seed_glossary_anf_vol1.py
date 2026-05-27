"""Seed the translation glossary with the curated person/place/sect/work
term pairs we learned from translating ANF Vol 1.

Pulls source-of-truth from sweep_book_quality.TERM_FIXES_ANF_VOL_1 plus
a hand-curated table of the CORRECT terms with English / original-language
companions. Inserts into:
  - theologians          → entity_type='person' implicit
  - theological_terms    → with entity_type in {place,work,sect,term}

Idempotent: skips entries whose name_english already exists.

Usage:
    python scripts/seed_glossary_anf_vol1.py            # apply
    python scripts/seed_glossary_anf_vol1.py --dry-run  # report
"""
from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}

# ── Curated entries — drawn from TERM_FIXES_ANF_VOL_1 + Haiku findings ──
# Each row: (english, original, chinese, entity_type)
# entity_type: 'person' | 'place' | 'sect' | 'work' | 'term'
#
# Persons / places / sects / works / terms surfaced during ANF Vol 1
# translation; the 中文 is the standardized form the sweep enforces.

ENTRIES = [
    # Persons (theologians table)
    ("Aristion",                          "Ἀριστίων",            "亞里斯鐸",                  "person"),
    ("Cephas",                            "Κηφᾶς",               "磯法",                      "person"),
    ("Trypho",                            "Τρύφων",              "特里弗",                    "person"),
    ("Diognetus",                         "Διόγνητος",           "丟格那妥",                  "person"),
    ("Hero (deacon of Antioch)",          "Ἥρων",                "黑羅",                      "person"),
    ("Cassiodorus",                       "Cassiodorus",         "卡西奧多魯斯",              "person"),
    ("Justin Martyr",                     "Ἰουστῖνος",           "殉道者猶斯定",              "person"),
    ("Mathetes",                          "Μαθητής",             "瑪忒特",                    "person"),

    # Bible characters / 聖經人物 (also theologians table)
    ("Paul (apostle)",                    "Παῦλος",              "保羅",                      "person"),
    ("Mary (mother of Jesus)",            "Μαρία",               "馬利亞",                    "person"),
    ("Salome",                            "Σαλώμη",              "撒羅米",                    "person"),
    ("Clopas",                            "Κλωπᾶς",              "革羅帕",                    "person"),

    # Places (theological_terms with entity_type='place')
    ("Corinth",                           "Κόρινθος",            "哥林多",                    "place"),
    ("Smyrna",                            "Σμύρνα",              "士每拿",                    "place"),
    ("Antioch",                           "Ἀντιόχεια",           "安提阿",                    "place"),
    ("Philippi",                          "Φίλιπποι",            "腓立比",                    "place"),
    ("Ephesus",                           "Ἔφεσος",              "以弗所",                    "place"),
    ("Magnesia",                          "Μαγνησία",            "馬內夏",                    "place"),
    ("Tralles",                           "Τράλλεις",            "特拉勒",                    "place"),
    ("Philadelphia",                      "Φιλαδέλφεια",         "非拉鐵非",                  "place"),
    ("Tarsus",                            "Ταρσός",              "他爾索",                    "place"),
    ("Hierapolis",                        "Ἱεράπολις",           "希拉波利",                  "place"),
    ("Lyon",                              "Λούγδουνον",          "里昂",                      "place"),
    ("Rome",                              "Roma",                "羅馬",                      "place"),
    ("Samaria",                           "Σαμάρεια",            "撒瑪利亞",                  "place"),
    ("Flavia Neapolis",                   "Φλαβία Νεάπολις",     "弗拉維亞‧尼亞波利斯",       "place"),

    # Sects / 教派 (theological_terms with entity_type='sect')
    ("Ebionites",                         "Ἐβιωναῖοι",           "伊比昂派",                  "sect"),
    ("Marcionites",                       "Μαρκιωνῖται",         "馬吉安派",                  "sect"),
    ("Gnostics",                          "γνωστικοί",           "諾斯底派",                  "sect"),
    ("Valentinians",                      "Οὐαλεντινιανοί",      "瓦倫廷派",                  "sect"),
    ("Cynics",                            "Κυνικοί",             "犬儒學派",                  "sect"),
    ("Stoics",                            "Στωϊκοί",             "斯多亞學派",                "sect"),
    ("Pharisees",                         "Φαρισαῖοι",           "法利賽人",                  "sect"),
    ("Sadducees",                         "Σαδδουκαῖοι",         "撒都該人",                  "sect"),

    # Works / 作品名 (theological_terms with entity_type='work')
    ("Against Heresies",                  "Adversus Haereses",   "駁異端",                    "work"),
    ("First Apology",                     "Ἀπολογία α′",         "猶斯定第一護教辭",          "work"),
    ("Second Apology",                    "Ἀπολογία β′",         "猶斯定第二護教辭",          "work"),
    ("Dialogue with Trypho",              "Διάλογος πρὸς Τρύφωνα", "與特里弗的對話",         "work"),
    ("Exposition of the Oracles of the Lord", "Λογίων κυριακῶν ἐξήγησις", "主的神諭闡述", "work"),
    ("Martyrdom of Polycarp",             "Μαρτύριον Πολυκάρπου", "坡旅甲殉道記",             "work"),
    ("Epistle of Barnabas",               "Ἐπιστολή Βαρνάβα",    "巴拿巴書信",                "work"),
    ("Hortatory Address to the Greeks",   "Λόγος παραινετικὸς πρὸς Ἕλληνας", "勸勉希臘人辭", "work"),
    ("Discourse to the Greeks",           "Λόγος πρὸς Ἕλληνας",  "致希臘人辭",                "work"),
    ("On the Sole Government of God",     "Περὶ μοναρχίας",      "論神獨一治理",              "work"),
    ("On the Resurrection (Fragments)",   "Περὶ ἀναστάσεως",     "論復活殘篇",                "work"),

    # Theological terms (existing 159 will be deduped on name_english)
    ("Logos",                             "λόγος",               "聖言",                      "term"),
    ("Phoenix",                           "φοῖνιξ",              "鳳凰",                      "term"),
    ("Demiurge",                          "δημιουργός",          "巨匠造物者",                "term"),
    ("Æon (gnostic)",                     "αἰών",                "永世",                      "term"),
    ("Pleroma",                           "πλήρωμα",             "普累若麻",                  "term"),
    ("Ogdoad",                            "ὀγδοάς",              "八聖數",                    "term"),
    ("Decad",                             "δεκάς",               "十聖數",                    "term"),
    ("Triacontad",                        "τριακοντάς",          "三十聖數",                  "term"),
]

FIRST_SOURCE = "ANF Vol 1"


def existing_english_names() -> tuple[set[str], set[str]]:
    """Return (theologian-name-english, theological-term-english) lowercase sets."""
    r1 = requests.get(f"{URL}/rest/v1/theologians?select=name_english",
                      headers=H_GET, timeout=30)
    r2 = requests.get(f"{URL}/rest/v1/theological_terms?select=term_english",
                      headers=H_GET, timeout=30)
    r1.raise_for_status(); r2.raise_for_status()
    p_set = {(row.get("name_english") or "").lower() for row in r1.json()}
    t_set = {(row.get("term_english") or "").lower() for row in r2.json()}
    return p_set, t_set


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    p_existing, t_existing = existing_english_names()
    print(f"Existing: {len(p_existing)} theologians, {len(t_existing)} terms")

    inserts_person = []
    inserts_term = []
    skipped = 0
    for en, original, zh, etype in ENTRIES:
        key = en.lower()
        if etype == "person":
            if key in p_existing:
                skipped += 1
                continue
            inserts_person.append({
                "name_english": en,
                "name_original": original,
                "name_latin_std": en,  # required NOT NULL
                "name_recommended": zh,
                "first_source": FIRST_SOURCE,
            })
        else:
            if key in t_existing:
                skipped += 1
                continue
            inserts_term.append({
                "term_english": en,
                "term_original": original,
                "zh_recommended": zh,
                "entity_type": etype,
                "first_source": FIRST_SOURCE,
            })

    print(f"\nWould insert:")
    print(f"  theologians: {len(inserts_person)}")
    print(f"  theological_terms: {len(inserts_term)}")
    print(f"  skipped (already exist): {skipped}")

    if args.dry_run:
        for x in inserts_person[:5]:
            print(f"  person  ⊕ {x['name_english']} → {x['name_recommended']}")
        for x in inserts_term[:5]:
            print(f"  {x['entity_type']:8s} ⊕ {x['term_english']} → {x['zh_recommended']}")
        return

    if inserts_person:
        r = requests.post(f"{URL}/rest/v1/theologians", headers=H_JSON,
                          json=inserts_person, timeout=60)
        print(f"\ntheologians POST: {r.status_code}")
    if inserts_term:
        r = requests.post(f"{URL}/rest/v1/theological_terms", headers=H_JSON,
                          json=inserts_term, timeout=60)
        print(f"theological_terms POST: {r.status_code}")
    print("✓ done")


if __name__ == "__main__":
    main()
