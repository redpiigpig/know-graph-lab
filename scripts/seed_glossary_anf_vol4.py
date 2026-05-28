"""Seed the translation glossary with curated person/place/work/sect/term
entries unique to ANF Vol 4 (Tertullian Part 4 — ascetic & ethical writings;
Minucius Felix — Octavius dialogue; Commodian — Instructions, Carmen
Apologeticum; Origen Parts 1-2 — De Principiis, Letters, beginning of
Contra Celsum).

Pulls source-of-truth from sweep_book_quality.TERM_FIXES_ANF_VOL_4 plus a
hand-curated table of CORRECT terms with English / original-language
companions. Inserts into:
  - theologians          → entity_type='person' implicit
  - theological_terms    → with entity_type in {place,work,sect,term}

Idempotent: skips entries whose name_english/term_english already exists.

Usage:
    python scripts/seed_glossary_anf_vol4.py            # apply
    python scripts/seed_glossary_anf_vol4.py --dry-run  # report
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
ENTRIES = [
    # ── Persons ────────────────────────────────────────────────────────
    # Minucius Felix dialogue (Octavius vs Caecilius arguing before judge M. Felix)
    ("Caecilius Natalis",                   "Caecilius Natalis",   "凱基琉‧納塔利",            "person"),
    ("Octavius Januarius",                  "Octavius Ianuarius",  "屋大維‧雅努阿留",          "person"),

    # Origen's circle & opponents
    ("Celsus (philosopher)",                "Kelsos",              "塞爾蘇斯",                  "person"),
    ("Ambrosius (Origen's patron)",         "Ambrosius",           "安博羅修斯（俄利根的庇主）","person"),
    ("Demetrius of Alexandria",             "Demetrius",           "亞歷山卓的德米特",          "person"),
    ("Heraclas of Alexandria",              "Heraclas",            "亞歷山卓的赫拉克拉",        "person"),
    ("Leonides (Origen's father)",          "Leonides",            "里奧尼德斯",                "person"),
    ("Plotinus",                            "Plotinus",            "普羅提諾",                  "person"),
    ("Numenius of Apamea",                  "Numenius",            "努門尼烏",                  "person"),
    ("Ammonius Saccas",                     "Ammonius Saccas",     "阿摩尼烏‧薩卡斯",          "person"),
    ("Porphyry of Tyre",                    "Porphyry",            "波菲利",                    "person"),
    ("Pope Gregory I (citation context)",   "Gregorius Magnus",    "大額我略",                  "person"),

    # Roman emperors in Tertullian/Origen context
    ("Septimius Severus (emperor)",         "Septimius Severus",   "塞普蒂米烏‧塞維魯",         "person"),
    ("Caracalla (emperor)",                 "Caracalla",           "卡拉卡拉",                  "person"),
    ("Marcus Aurelius (emperor-philosopher)","Marcus Aurelius",    "馬可‧奧理略",               "person"),

    # ── Places ─────────────────────────────────────────────────────────
    ("Alexandria",                          "Alexandria",          "亞歷山卓",                  "place"),
    ("Caesarea (Maritima)",                 "Caesarea Maritima",   "凱撒利亞（濱海）",          "place"),
    ("Cirta (Numidia)",                     "Cirta",               "錫爾塔",                    "place"),
    ("Ostia (port of Rome)",                "Ostia",               "奧斯提亞",                  "place"),

    # ── Sects ─────────────────────────────────────────────────────────
    ("Middle Platonists",                   "Medioplatonici",      "中期柏拉圖主義",            "sect"),
    ("Neoplatonists",                       "Neoplatonici",        "新柏拉圖主義",              "sect"),
    ("Epicureans",                          "Epicurei",            "伊壁鳩魯派",                "sect"),
    ("Stoics",                              "Stoici",              "斯多噶派",                  "sect"),

    # ── Works ─────────────────────────────────────────────────────────
    # Tertullian Part 4 (ethical / ascetic / occasional)
    ("On the Pallium (De Pallio)",          "De Pallio",           "論披袍",                    "work"),
    ("On the Apparel of Women",             "De Cultu Feminarum",  "論婦女裝飾",                "work"),
    ("On the Veiling of Virgins",           "De Virginibus Velandis","論貞女蒙頭",              "work"),
    ("To His Wife (Ad Uxorem)",             "Ad Uxorem",           "致妻書",                    "work"),
    ("On Exhortation to Chastity",          "De Exhortatione Castitatis","勸貞潔書",            "work"),
    ("On Monogamy",                         "De Monogamia",        "論獨婚",                    "work"),
    ("On Modesty (De Pudicitia)",           "De Pudicitia",        "論貞操",                    "work"),
    ("On Fasting (De Ieiunio)",             "De Ieiunio",          "論禁食",                    "work"),
    ("De Fuga in Persecutione",             "De Fuga in Persecutione","論逼迫中逃避",           "work"),

    # Minucius Felix
    ("Octavius (dialogue)",                 "Octavius",            "屋大維對話錄",              "work"),

    # Commodian
    ("Instructions (Commodian)",            "Instructiones",       "教誨集",                    "work"),
    ("Carmen Apologeticum",                 "Carmen Apologeticum","護教詩",                    "work"),

    # Origen (this volume covers De Principiis + Letters + start of Contra Celsum)
    ("De Principiis (On First Principles)", "Peri Archon",         "論原理",                    "work"),
    ("Against Celsus (Contra Celsum)",      "Contra Celsum",       "駁塞爾蘇斯",                "work"),
    ("Letter to Africanus",                 "Epistula ad Africanum","致阿弗里卡努書信",         "work"),
    ("Letter to Gregory (Thaumaturgus)",    "Epistula ad Gregorium","致格列高利書信",          "work"),
    ("Hexapla",                             "Hexapla",             "六文合參",                  "work"),
    ("Commentary on John (Origen)",         "Commentarii in Iohannem","約翰福音註解",          "work"),
    ("Commentary on Matthew (Origen)",      "Commentarii in Matthaeum","馬太福音註解",         "work"),
    ("On Prayer (Origen)",                  "Peri Euches",         "俄利根論禱告",              "work"),
    ("Exhortation to Martyrdom (Origen)",   "Exhortatio ad Martyrium","勸殉道書",              "work"),

    # ── Terms ─────────────────────────────────────────────────────────
    # Origen's signature theological vocabulary
    ("Apokatastasis (universal restoration)","apokatastasis",       "萬有復興",                  "term"),
    ("Logos (the divine Word)",             "Logos",               "道（邏各斯）",              "term"),
    ("Hypostasis (subsistence)",            "hypostasis",          "本體（位格）",              "term"),
    ("Pre-existence of souls",              "praeexistentia animarum","靈魂先存說",            "term"),
    ("Trichotomy (body-soul-spirit)",       "trichotomia",         "三元論（體‧魂‧靈）",     "term"),
    ("Allegorical exegesis",                "allegoria",           "寓意解經",                  "term"),
    ("Anagogical sense",                    "anagoge",             "靈意層次",                  "term"),
    ("Recapitulation (Origenist)",          "anakephalaiosis",     "總歸於一",                  "term"),
    ("Eternal generation of the Son",       "aeterna generatio Filii","聖子永恆受生",          "term"),

    # Tertullian's ethical vocabulary continued
    ("Continentia (continence)",            "continentia",         "節制",                      "term"),
    ("Castitas (chastity)",                 "castitas",            "貞潔",                      "term"),
    ("Pudicitia (modesty)",                 "pudicitia",           "貞操",                      "term"),
    ("Ieiunium (fasting)",                  "ieiunium",            "禁食",                      "term"),
    ("Stationes (stations)",                "stationes",           "禱告值守",                  "term"),

    # Minucius Felix apologetic vocabulary
    ("Providentia (providence)",            "providentia",         "天意",                      "term"),
    ("Demonologia (demonology)",            "daemonologia",        "鬼魔論",                    "term"),
]

FIRST_SOURCE = "ANF Vol 4"


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
