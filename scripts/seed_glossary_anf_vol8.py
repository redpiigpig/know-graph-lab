"""Seed the translation glossary with curated entries unique to ANF Vol 8
(Twelve Patriarchs + Theodotus + Two Virginity Epistles + Pseudo-Clementine
Recognitions/Homilies + NT Apocrypha + Decretals + Edessa Memoirs +
Remains of 2nd-3rd century).

Idempotent: skips entries whose english name already exists.

Usage:
    python scripts/seed_glossary_anf_vol8.py            # apply
    python scripts/seed_glossary_anf_vol8.py --dry-run  # report
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

# (english, original, chinese, entity_type)
ENTRIES = [
    # ── Persons ────────────────────────────────────────────────────────
    # Twelve Patriarchs (already biblical — likely deduped by glossary)
    ("Theodotus the Valentinian (gnostic)",   "Theodotus",          "瓦倫廷派的狄奧多托",       "person"),
    # Pseudo-Clementine cast
    ("Simon Magus (Clementine Homilies foe)", "Simon Magus",        "行邪術的西門",             "person"),
    ("Clement of Rome (Pseudo-Clementine narrator)","Clemens Romanus","羅馬的克勉",            "person"),
    ("Faustinianus (Clement's father)",       "Faustinianus",       "福斯提尼安（革利免之父）", "person"),
    ("Faustus (Clement's brother)",           "Faustus",            "福斯圖",                   "person"),
    ("Faustinus (Clement's brother)",         "Faustinus",          "福斯提奴",                 "person"),
    ("Mattidia (Clement's mother)",           "Mattidia",           "瑪提狄雅",                 "person"),
    ("Apion the Grammarian",                  "Apion",              "文法學家阿庇翁",           "person"),
    ("Aquila (Clementine companion)",         "Aquila",             "亞居拉",                   "person"),
    ("Niceta (Clementine companion)",         "Niceta",             "尼克塔",                   "person"),

    # NT Apocrypha
    ("Joseph of Arimathea (apocryphal)",      "Iosephus ab Arimathea","亞利馬太的約瑟",         "person"),
    ("Nicodemus",                             "Nicodemus",          "尼哥底母",                 "person"),
    ("Thecla (martyr / companion of Paul)",   "Thecla",             "黛克拉",                   "person"),
    ("Pontius Pilate (apocryphal acts)",      "Pontius Pilatus",    "彼拉多",                   "person"),
    ("Veronica (Cura Sanitatis Tiberii)",     "Veronica",           "維羅尼加",                 "person"),

    # Edessa / Syriac Documents
    ("Abgar V of Edessa (Black King)",        "Abgar V Ukkama",     "厄德薩的阿布加爾五世",     "person"),
    ("Addai (Thaddeus of Edessa)",            "Addai / Addaeus",    "阿岱（厄德薩使徒）",       "person"),
    ("Bardesanes (Bar Daisan of Edessa)",     "Bardesanes",         "巴德撒尼斯",               "person"),
    ("Hystaspes (Persian sage)",              "Hystaspes",          "希斯塔斯佩斯",             "person"),

    # Remains of 2nd-3rd century
    ("Melito of Sardis",                      "Melito",             "撒狄的美利托",             "person"),
    ("Hegesippus (church historian)",         "Hegesippus",         "黑格希普",                 "person"),
    ("Quadratus of Athens (apologist)",       "Quadratus",          "雅典的庫德拉圖",           "person"),
    ("Pinytus of Knossos",                    "Pinytus",            "克諾索斯的皮尼圖斯",       "person"),
    ("Dionysius of Corinth",                  "Dionysius Corinthius","哥林多的狄奧尼修",        "person"),
    ("Serapion of Antioch",                   "Serapion",           "安提阿的塞拉皮昂",         "person"),
    ("Apollonius (anti-Montanist)",           "Apollonius",         "阿波羅尼烏斯",             "person"),
    ("Maximus of Jerusalem",                  "Maximus",            "耶路撒冷的馬克西穆",       "person"),
    ("Polycrates of Ephesus",                 "Polycrates",         "以弗所的波利克拉特",       "person"),
    ("Theophilus of Caesarea",                "Theophilus",         "凱撒利亞的提阿非羅",       "person"),

    # Twelve Patriarchs unique names (Hebrew Bible names — mostly already in
    # glossary, but listed for completeness)
    ("Reuben (firstborn of Jacob)",           "Reuben",             "流便",                     "person"),
    ("Simeon (second son of Jacob)",          "Simeon",             "西緬",                     "person"),
    ("Levi (third son of Jacob)",             "Levi",               "利未",                     "person"),
    ("Judah (fourth son of Jacob)",           "Judah",              "猶大",                     "person"),
    ("Issachar (fifth son of Jacob)",         "Issachar",           "以薩迦",                   "person"),
    ("Zebulun (sixth son of Jacob)",          "Zebulun",            "西布倫",                   "person"),
    ("Dan (seventh son of Jacob)",            "Dan",                "但",                       "person"),
    ("Naphtali (eighth son of Jacob)",        "Naphtali",           "拿弗他利",                 "person"),
    ("Gad (ninth son of Jacob)",              "Gad",                "迦得",                     "person"),
    ("Asher (tenth son of Jacob)",            "Asher",              "亞設",                     "person"),
    ("Joseph (Jacob's son, Egypt vizier)",    "Joseph",             "約瑟",                     "person"),
    ("Benjamin (twelfth son of Jacob)",       "Benjamin",           "便雅憫",                   "person"),

    # ── Places ─────────────────────────────────────────────────────────
    ("Edessa (city of Abgar)",                "Edessa",             "厄德薩",                   "place"),
    ("Sardis (Lydia)",                        "Sardis",             "撒狄（呂底亞）",           "place"),

    # ── Sects ─────────────────────────────────────────────────────────
    ("Ebionites (Pseudo-Clementine background)","Ebionitae",        "厄比恩派",                 "sect"),
    ("Elcesaites (Pseudo-Clementine)",        "Elchasaitae",        "厄爾克塞派",               "sect"),
    ("Montanists (Apollonius's target)",      "Montanistae",        "孟他奴派",                 "sect"),

    # ── Works ─────────────────────────────────────────────────────────
    ("Testaments of the Twelve Patriarchs",   "Testamenta XII Patriarcharum","十二族長遺訓",   "work"),
    ("Excerpts of Theodotus",                 "Excerpta ex Theodoto","狄奧多托殘篇",           "work"),
    ("Two Epistles Concerning Virginity",     "De Virginitate Epistulae","論貞潔書信二篇",    "work"),
    ("Pseudo-Clementine Recognitions",        "Recognitiones",      "偽克勉《再認集》",         "work"),
    ("Pseudo-Clementine Homilies",            "Homiliae Clementinae","偽克勉《講道集》",       "work"),
    ("Protevangelium of James",               "Protevangelium Iacobi","雅各原福音",            "work"),
    ("Gospel of Nicodemus (Acts of Pilate)",  "Evangelium Nicodemi","尼哥底母福音（彼拉多行傳）","work"),
    ("Acts of Paul and Thecla",               "Acta Pauli et Theclae","保羅與黛克拉行傳",      "work"),
    ("Acts of Andrew",                        "Acta Andreae",       "安得烈行傳",               "work"),
    ("Acts of Thomas",                        "Acta Thomae",        "多馬行傳",                 "work"),
    ("Acts of John",                          "Acta Iohannis",      "約翰行傳",                 "work"),
    ("Doctrine of Addai",                     "Doctrina Addai",     "阿岱訓誨",                 "work"),
    ("Letter of Abgar to Jesus",              "Epistula Abgari",    "阿布加爾致耶穌書",         "work"),
    ("Book of the Laws of Countries (Bardesanes)","Liber Legum Regionum","諸國律法書",       "work"),
    ("Oracles of Hystaspes",                  "Oracula Hystaspis",  "希斯塔斯佩斯神諭",         "work"),
    ("Decretals (false)",                     "Decretales Pseudo-Isidorianae","偽伊西多祿教令集","work"),

    # ── Terms ─────────────────────────────────────────────────────────
    # Pseudo-Clementine / Gnostic terms
    ("Recognitions (Anagnoreseis)",           "anagnoreseis",       "重認",                     "term"),
    ("Syzygies (Clementine pairs doctrine)",  "syzygiai",           "對偶論",                   "term"),
    ("True Prophet (Clementine title)",       "verus propheta",     "真先知",                   "term"),
    # Twelve Patriarchs themes
    ("Beliar (= Belial)",                     "Belial / Beliar",    "彼列",                     "term"),
    # NT Apocrypha trial vocabulary
    ("Anastasis (resurrection)",              "anastasis",          "復活",                     "term"),
    ("Praetorium (Pilate's headquarters)",    "praetorium",         "公廨",                     "term"),
    # Syriac
    ("Mar (Syriac honorific)",                "Mar / Mor",          "瑪／聖",                   "term"),
]

FIRST_SOURCE = "ANF Vol 8"


def existing_english_names() -> tuple[set[str], set[str]]:
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
    seen_keys: set[str] = set()
    for en, original, zh, etype in ENTRIES:
        key = (etype, en.lower())
        if key in seen_keys:
            continue
        seen_keys.add(key)
        if etype == "person":
            if en.lower() in p_existing:
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
            if en.lower() in t_existing:
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
    print(f"  skipped: {skipped}")

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
