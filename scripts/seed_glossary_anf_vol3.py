"""Seed the translation glossary with curated person/place/work/sect/term
entries unique to ANF Vol 3 (Tertullian — Apologetic, Anti-Marcion,
Ethical writings).

Pulls source-of-truth from sweep_book_quality.TERM_FIXES_ANF_VOL_3 plus a
hand-curated table of CORRECT terms with English / original-language
companions. Inserts into:
  - theologians          → entity_type='person' implicit
  - theological_terms    → with entity_type in {place,work,sect,term}

Idempotent: skips entries whose name_english/term_english already exists.

Usage:
    python scripts/seed_glossary_anf_vol3.py            # apply
    python scripts/seed_glossary_anf_vol3.py --dry-run  # report
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
    # Tertullian himself + his opponents
    ("Tertullian",                          "Tertullianus",        "特土良",                    "person"),
    ("Marcion of Sinope",                   "Marcion",             "馬吉安",                    "person"),
    ("Hermogenes",                          "Hermogenes",          "黑摩根",                    "person"),
    ("Praxeas",                             "Praxeas",             "普拉克西亞斯",              "person"),
    ("Scapula (Proconsul of Africa)",       "Scapula",             "斯卡普拉",                  "person"),
    ("Perpetua (martyr)",                   "Vibia Perpetua",      "佩爾佩圖亞",                "person"),
    ("Felicitas (martyr)",                  "Felicitas",           "費莉西塔斯",                "person"),
    ("Pliny the Younger",                   "Plinius Caecilius",   "普利尼",                    "person"),
    ("Trajan (emperor)",                    "Traianus",            "圖拉真",                    "person"),
    # Note: Valentinus (Vol 1 glossary) + Marcion + Praxeas + Hermogenes are the
    # four primary opponents Tertullian writes against.

    # ── Places ─────────────────────────────────────────────────────────
    ("Carthage",                            "Carthago",            "迦太基",                    "place"),
    ("Sinope (Pontus)",                     "Sinope",              "錫諾普",                    "place"),
    ("Pontus",                              "Pontus",              "本都",                      "place"),
    ("Africa Proconsularis",                "Africa",              "阿非利加",                  "place"),
    ("Numidia",                             "Numidia",             "努米底亞",                  "place"),

    # ── Sects ─────────────────────────────────────────────────────────
    ("Marcionites",                         "Marcionitae",         "馬吉安派",                  "sect"),
    ("Montanists / New Prophecy",           "Montanistae",         "孟他努派",                  "sect"),
    ("Modalists / Patripassians",           "Patripassiani",       "聖父受苦派／形態論",        "sect"),

    # ── Works ─────────────────────────────────────────────────────────
    ("Apology (Tertullian)",                "Apologeticus",        "特土良護教辭",              "work"),
    ("On Idolatry",                         "De Idololatria",      "論偶像崇拜",                "work"),
    ("The Shows (De Spectaculis)",          "De Spectaculis",      "論觀劇",                    "work"),
    ("The Chaplet (De Corona)",             "De Corona",           "論花冠",                    "work"),
    ("To Scapula",                          "Ad Scapulam",         "致斯卡普拉",                "work"),
    ("Ad Nationes",                         "Ad Nationes",         "致萬民",                    "work"),
    ("An Answer to the Jews",               "Adversus Iudaeos",    "駁猶太人",                  "work"),
    ("The Soul's Testimony",                "De Testimonio Animae", "靈魂的見證",               "work"),
    ("A Treatise on the Soul",              "De Anima",            "論靈魂",                    "work"),
    ("The Prescription Against Heretics",   "De Praescriptione Haereticorum", "駁異端的時效", "work"),
    ("Against Marcion",                     "Adversus Marcionem",  "駁馬吉安",                  "work"),
    ("Against Hermogenes",                  "Adversus Hermogenem", "駁黑摩根",                  "work"),
    ("Against the Valentinians",            "Adversus Valentinianos", "駁瓦倫廷派",             "work"),
    ("On the Flesh of Christ",              "De Carne Christi",    "論基督的肉身",              "work"),
    ("On the Resurrection of the Flesh",    "De Resurrectione Carnis", "論肉身復活",            "work"),
    ("Against Praxeas",                     "Adversus Praxean",    "駁普拉克西亞斯",            "work"),
    ("Scorpiace (Antidote for Scorpion's Sting)", "Scorpiace",      "蝎傷解毒劑",                "work"),
    ("Against All Heresies (Appendix)",     "Adversus Omnes Haereses", "駁諸異端附錄",         "work"),
    ("On Repentance",                       "De Paenitentia",      "論悔改",                    "work"),
    ("On Baptism",                          "De Baptismo",         "論洗禮",                    "work"),
    ("On Prayer",                           "De Oratione",         "論禱告",                    "work"),
    ("Ad Martyras (To the Martyrs)",        "Ad Martyras",         "致殉道者",                  "work"),
    ("The Passion of Perpetua and Felicitas", "Passio Perpetuae et Felicitatis", "佩爾佩圖亞與費莉西塔斯殉道記", "work"),
    ("On Patience",                         "De Patientia",        "論忍耐",                    "work"),

    # ── Terms (Tertullian's signature Latin theological vocabulary) ──
    ("Substantia (substance)",              "substantia",          "本質",                      "term"),
    ("Persona (person)",                    "persona",             "位格",                      "term"),
    ("Trinitas (Trinity)",                  "Trinitas",            "三位一體",                  "term"),
    ("Praescriptio (legal prescription)",   "praescriptio",        "時效抗辯",                  "term"),
    ("Regula Fidei (rule of faith)",        "regula fidei",        "信仰準則",                  "term"),
    ("Sacramentum",                         "sacramentum",         "聖事／聖禮",                "term"),
    ("Caro (the flesh)",                    "caro",                "肉身",                      "term"),
    ("Anima (soul)",                        "anima",               "靈魂",                      "term"),
    ("Disciplina (church discipline)",      "disciplina",          "教會懲戒",                  "term"),
    ("Patripassianism",                     "patripassianismus",   "聖父受苦論",                "term"),
    ("Apologia (defence speech)",           "apologia",            "護教辭",                    "term"),
    ("Spectaculum (public show)",           "spectaculum",         "公共表演",                  "term"),
]

FIRST_SOURCE = "ANF Vol 3"


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
