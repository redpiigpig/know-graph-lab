"""Seed the translation glossary with curated person/place/work/sect/term
entries unique to ANF Vol 2 (Fathers of the Second Century — Hermas,
Tatian, Athenagoras, Theophilus, Clement of Alexandria).

Pulls source-of-truth from sweep_book_quality.TERM_FIXES_ANF_VOL_2 plus a
hand-curated table of CORRECT terms with English / original-language
companions. Inserts into:
  - theologians          → entity_type='person' implicit
  - theological_terms    → with entity_type in {place,work,sect,term}

Idempotent: skips entries whose name_english/term_english already exists.

Usage:
    python scripts/seed_glossary_anf_vol2.py            # apply
    python scripts/seed_glossary_anf_vol2.py --dry-run  # report
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

# Each row: (english, original, chinese, entity_type)
# entity_type: 'person' | 'place' | 'sect' | 'work' | 'term'

ENTRIES = [
    # ── Persons ────────────────────────────────────────────────────────
    # Five featured authors of Vol 2
    ("Hermas",                              "Ἑρμᾶς",              "黑馬",                      "person"),
    ("Tatian",                              "Τατιανός",           "他提安",                    "person"),
    ("Athenagoras of Athens",               "Ἀθηναγόρας",          "雅典那哥拉",                "person"),
    ("Theophilus of Antioch",               "Θεόφιλος Ἀντιοχείας", "提阿非羅",                  "person"),
    ("Clement of Alexandria",               "Κλήμης Ἀλεξανδρεύς",  "亞歷山卓的革利免",          "person"),
    # Addressees / supporting cast
    ("Autolycus",                           "Αὐτόλυκος",           "奧托呂庫斯",                "person"),
    # Gnostic teachers Clement engages with
    ("Basilides",                           "Βασιλείδης",          "巴西理德",                  "person"),
    ("Isidorus (son of Basilides)",         "Ἰσίδωρος",            "依西多魯",                  "person"),
    ("Carpocrates",                         "Καρποκράτης",         "家波克拉特",                "person"),
    ("Heracleon (Valentinian)",             "Ἡρακλέων",            "赫拉克勒翁",                "person"),
    # Greek philosophers cited heavily in Vol 2
    ("Pythagoras",                          "Πυθαγόρας",           "畢達哥拉斯",                "person"),
    ("Plato",                               "Πλάτων",              "柏拉圖",                    "person"),
    ("Aristotle",                           "Ἀριστοτέλης",         "亞里斯多德",                "person"),
    ("Heraclitus",                          "Ἡράκλειτος",          "赫拉克利特",                "person"),
    ("Democritus",                          "Δημόκριτος",          "德謨克利特",                "person"),
    ("Empedocles",                          "Ἐμπεδοκλῆς",          "恩培多克勒",                "person"),
    ("Anaxagoras",                          "Ἀναξαγόρας",          "阿那克薩哥拉",              "person"),
    ("Thales of Miletus",                   "Θαλῆς",               "泰利斯",                    "person"),
    ("Socrates",                            "Σωκράτης",            "蘇格拉底",                  "person"),
    ("Epicurus",                            "Ἐπίκουρος",           "伊壁鳩魯",                  "person"),
    ("Protagoras",                          "Πρωταγόρας",          "普羅泰戈拉",                "person"),
    ("Critias",                             "Κριτίας",             "克里提亞",                  "person"),
    ("Diogenes of Sinope",                  "Διογένης",            "第歐根尼",                  "person"),
    ("Aristippus",                          "Ἀρίστιππος",          "亞里斯提普",                "person"),
    ("Homer",                               "Ὅμηρος",              "荷馬",                      "person"),
    ("Hesiod",                              "Ἡσίοδος",             "赫西奧德",                  "person"),
    ("Euripides",                           "Εὐριπίδης",           "歐里庇得斯",                "person"),
    ("Orpheus",                             "Ὀρφεύς",              "俄耳甫斯",                  "person"),
    # Apostolic Fathers cited but mostly Vol 1 — skip if already seeded

    # ── Places ─────────────────────────────────────────────────────────
    ("Alexandria",                          "Ἀλεξάνδρεια",         "亞歷山卓",                  "place"),
    ("Athens",                              "Ἀθῆναι",              "雅典",                      "place"),
    ("Babylon",                             "Βαβυλών",             "巴比倫",                    "place"),
    ("Phoenicia",                           "Φοινίκη",             "腓尼基",                    "place"),
    ("Persia",                              "Περσία",              "波斯",                      "place"),
    ("Egypt",                               "Αἴγυπτος",            "埃及",                      "place"),
    ("Phrygia",                             "Φρυγία",              "弗里吉亞",                  "place"),

    # ── Sects / philosophical schools ─────────────────────────────────
    ("Basilidians",                         "Βασιλειδιανοί",       "巴西理德派",                "sect"),
    ("Carpocratians",                       "Καρποκρατιανοί",      "家波克拉特派",              "sect"),
    ("Pythagoreans",                        "Πυθαγόρειοι",         "畢達哥拉斯學派",            "sect"),
    ("Platonists",                          "Πλατωνικοί",          "柏拉圖學派",                "sect"),
    ("Peripatetics",                        "Περιπατητικοί",       "逍遙學派",                  "sect"),
    ("Epicureans",                          "Ἐπικούρειοι",         "伊壁鳩魯學派",              "sect"),

    # ── Works ─────────────────────────────────────────────────────────
    ("The Shepherd of Hermas",              "Ποιμὴν τοῦ Ἑρμᾶ",     "《黑馬牧者》",              "work"),
    ("Visions (Hermas, Book 1)",            "Ὁράσεις",             "《黑馬牧者》異象篇",        "work"),
    ("Mandates (Hermas, Book 2)",           "Ἐντολαί",             "《黑馬牧者》誡命篇",        "work"),
    ("Similitudes (Hermas, Book 3)",        "Παραβολαί",           "《黑馬牧者》比喻篇",        "work"),
    ("Address to the Greeks (Tatian)",      "Λόγος πρὸς Ἕλληνας (Τατιανοῦ)", "他提安致希臘人辭",  "work"),
    ("Diatessaron",                         "Διὰ τεσσάρων",        "《四福音合參》",            "work"),
    ("To Autolycus",                        "Πρὸς Αὐτόλυκον",      "提阿非羅致奧托呂庫斯書",    "work"),
    ("A Plea for the Christians",           "Πρεσβεία περὶ Χριστιανῶν", "雅典那哥拉護基督徒辭",  "work"),
    ("On the Resurrection of the Dead",     "Περὶ ἀναστάσεως νεκρῶν", "論死者復活",            "work"),
    ("Exhortation to the Heathen (Protrepticus)", "Προτρεπτικὸς πρὸς Ἕλληνας", "革利免勸勉希臘人辭", "work"),
    ("The Instructor (Paedagogus)",         "Παιδαγωγός",          "革利免《教師》",            "work"),
    ("Stromata (Miscellanies)",             "Στρωματεῖς",          "革利免《雜文集》",          "work"),
    ("Who is the Rich Man that shall be Saved?", "Τίς ὁ σωζόμενος πλούσιος", "革利免《富者得救》", "work"),

    # ── Terms ─────────────────────────────────────────────────────────
    ("Gnosis (true knowledge in Clement)",  "γνῶσις",              "靈知",                      "term"),
    ("Apatheia (passionlessness)",          "ἀπάθεια",             "無情狀態",                  "term"),
    ("Paedagogue",                          "παιδαγωγός",          "教師",                      "term"),
    ("Stromateis (lit. patchwork carpets)", "στρωματεῖς",          "雜集",                      "term"),
    ("Anthropomorphism",                    "ἀνθρωπομορφισμός",    "擬人化",                    "term"),
    ("Recapitulation (anakephalaiosis)",    "ἀνακεφαλαίωσις",      "重述／重歸於一",            "term"),
    ("Æon (gnostic)",                       "αἰών",                "永世",                      "term"),
]

FIRST_SOURCE = "ANF Vol 2"


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
                "name_latin_std": en,
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
        for x in inserts_person[:8]:
            print(f"  person  + {x['name_english']} -> {x['name_recommended']}")
        for x in inserts_term[:8]:
            print(f"  {x['entity_type']:8s} + {x['term_english']} -> {x['zh_recommended']}")
        return

    if inserts_person:
        r = requests.post(f"{URL}/rest/v1/theologians", headers=H_JSON,
                          json=inserts_person, timeout=60)
        print(f"\ntheologians POST: {r.status_code}")
        if r.status_code not in (200, 201):
            print(f"  body: {r.text[:500]}", file=sys.stderr)
    if inserts_term:
        r = requests.post(f"{URL}/rest/v1/theological_terms", headers=H_JSON,
                          json=inserts_term, timeout=60)
        print(f"theological_terms POST: {r.status_code}")
        if r.status_code not in (200, 201):
            print(f"  body: {r.text[:500]}", file=sys.stderr)
    print("done")


if __name__ == "__main__":
    main()
