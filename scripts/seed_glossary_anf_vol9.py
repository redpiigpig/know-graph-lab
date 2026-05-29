"""Seed the translation glossary with curated entries unique to ANF Vol 9
(Gospel of Peter, Diatessaron of Tatian, Apocalypses of Peter/Virgin/Sedrach,
Vision of Paul, Testament of Abraham, Acts of Xanthippe & Polyxena, Narrative
of Zosimus, Epistles of Clement, Apology of Aristides, Passion of the
Scillitan Martyrs, Origen — Letter to Gregory + Commentary on John +
Commentary on Matthew).

Idempotent: skips entries whose english name already exists.

Usage:
    python scripts/seed_glossary_anf_vol9.py            # apply
    python scripts/seed_glossary_anf_vol9.py --dry-run  # report
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
    # Diatessaron of Tatian (already in vol 2 as 他提安 — skip if dup)
    ("Ammonius of Alexandria",        "Ammonius",            "亞歷山卓的阿摩尼烏",      "person"),
    ("Ephraem the Syrian (Mar Ephraem)","Ephraem Syrus",     "敘利亞的厄弗冷",          "person"),
    ("Mar Aba (Catholicos of the East)","Mar Aba",           "馬·阿巴",                "person"),
    ("Theodoret of Cyrrhus",          "Theodoretus",         "居魯斯的狄奧多勒",        "person"),
    ("Rabbula of Edessa",             "Rabbula",             "厄德薩的拉布拉",          "person"),
    ("Ciasca, Augustinus (Diatessaron editor)","Ciasca",     "齊亞斯卡",                "person"),
    ("Zahn, Theodor (NT scholar)",    "Theodor Zahn",        "察恩",                    "person"),

    # Aristides (Apology)
    ("Aristides of Athens (apologist)","Aristides",          "雅典的亞里斯泰德",        "person"),
    ("Barlaam (Christian sage)",      "Barlaam",             "巴爾蘭",                  "person"),
    ("Josaphat (Indian prince in legend)","Josaphat",        "約沙法（傳奇）",          "person"),

    # Scillitan Martyrs (180 AD, Africa)
    ("Speratus (Scillitan martyr)",   "Speratus",            "斯佩拉圖斯",              "person"),
    ("Nartzalus (Scillitan martyr)",  "Nartzalus",           "納札魯",                  "person"),
    ("Cittinus (Scillitan martyr)",   "Cittinus",            "齊提努",                  "person"),
    ("Donata (Scillitan martyr)",     "Donata",              "多納妲",                  "person"),
    ("Vestia (Scillitan martyr)",     "Vestia",              "維斯提雅",                "person"),
    ("Secunda (Scillitan martyr)",    "Secunda",             "塞昆妲",                  "person"),
    ("Saturninus (proconsul of Africa)","Saturninus",        "撒圖爾尼努（非洲總督）",  "person"),

    # Testament of Abraham
    ("Michael the Archangel",         "Michael",             "天使長米迦勒",            "person"),
    ("Death personified (Mavet)",     "Mors",                "死亡（位格化）",          "person"),
    ("Sarah (Abraham's wife)",        "Sarah",               "撒拉",                    "person"),
    ("Isaac (Abraham's son)",         "Isaac",               "以撒",                    "person"),

    # Apocalypse of the Virgin / Vision of Paul
    ("Virgin Mary (Theotokos in apocalyptic literature)","Maria Theotokos",
                                                              "天主之母瑪利亞",          "person"),
    ("Tartarouchos (angel of Tartarus)","Tartarouchos",     "塔爾塔魯庫（地獄主管天使）","person"),
    ("Temeluchus (angel of punishments)","Temeluchus",       "特墨魯庫斯",              "person"),

    # Apocalypse of Sedrach
    ("Sedrach (apocalyptic seer)",    "Sedrach",             "塞德拉克",                "person"),

    # Acts of Xanthippe / Polyxena
    ("Xanthippe (sister of Polyxena)","Xanthippe",           "散提碧",                  "person"),
    ("Polyxena (Christian virgin)",   "Polyxena",            "波利克塞娜",              "person"),
    ("Rebecca (Acts of Xanthippe)",   "Rebecca",             "利百加（散提碧行傳）",    "person"),
    ("Probus (Roman governor)",       "Probus",              "普羅布",                  "person"),

    # Origen's Commentary on John — interlocutors
    ("Ambrose (Origen's patron)",     "Ambrosius",           "安波羅斯（俄利根贊助者）","person"),
    ("Heracleon (Valentinian)",       "Heracleon",           "赫拉克利安",              "person"),

    # ── Places ─────────────────────────────────────────────────────────
    ("Akhmim (Egypt — Gospel of Peter find)","Akhmim",       "阿赫米姆（埃及）",        "place"),
    ("Edessa (Diatessaron)",          "Edessa",              "厄德薩",                  "place"),
    ("Scillium (Numidia, martyrs)",   "Scillium",            "西利（努米底亞）",        "place"),

    # ── Sects ─────────────────────────────────────────────────────────
    ("Encratites (Tatian followers)", "Encratitae",          "禁慾派",                  "sect"),
    ("Marcionites (revisited)",       "Marcionitae",         "馬吉安派",                "sect"),

    # ── Works ─────────────────────────────────────────────────────────
    ("Gospel of Peter (apocryphal)",  "Evangelium Petri",    "彼得福音",                "work"),
    ("Diatessaron (Harmony of the Four Gospels)","Diatessaron","狄阿特撒龍合參福音",   "work"),
    ("Apocalypse of Peter",           "Apocalypsis Petri",   "彼得啟示錄",              "work"),
    ("Vision of Paul (Visio Pauli)",  "Visio Pauli",         "保羅異象",                "work"),
    ("Apocalypse of the Virgin",      "Apocalypsis Mariae",  "童貞女啟示錄",            "work"),
    ("Apocalypse of Sedrach",         "Apocalypsis Sedrach", "塞德拉克啟示錄",          "work"),
    ("Testament of Abraham",          "Testamentum Abrahae", "亞伯拉罕遺訓",            "work"),
    ("Acts of Xanthippe and Polyxena","Acta Xanthippae",     "散提碧與波利克塞娜行傳",  "work"),
    ("Narrative of Zosimus",          "Narratio Zosimi",     "佐西穆斯紀錄",            "work"),
    ("First Epistle of Clement to the Corinthians","I Clementis","克勉致哥林多人前書","work"),
    ("Second Epistle of Clement (homily)","II Clementis",    "克勉後書（講道）",        "work"),
    ("Apology of Aristides",          "Apologia Aristidis",  "亞里斯泰德辯護書",        "work"),
    ("Passion of the Scillitan Martyrs","Passio Scillitanorum","西利人殉道記",          "work"),
    ("Letter of Origen to Gregory Thaumaturgus","Epistula ad Gregorium",
                                                              "俄利根致格列高利書信",    "work"),
    ("Origen's Commentary on the Gospel of John","Commentarii in Iohannem",
                                                              "俄利根《約翰福音註釋》",  "work"),
    ("Origen's Commentary on the Gospel of Matthew","Commentarii in Matthaeum",
                                                              "俄利根《馬太福音註釋》",  "work"),
    ("Synoptic Harmony (Synoptikon)", "synoptikon",          "對觀合參",                "work"),

    # ── Terms ─────────────────────────────────────────────────────────
    # Apocalyptic / cosmic terms
    ("Tartarus (place of torment)",   "tartarus",            "塔爾塔魯（陰府深淵）",    "term"),
    ("Gehenna (alt. hell)",           "gehenna",             "欣嫩谷（地獄）",          "term"),
    ("Paradise (heavenly)",           "paradisus",           "樂園",                    "term"),
    ("Theotokos (God-bearer)",        "Theotokos",           "天主之母",                "term"),
    # Origen exegetical terms
    ("Logos (Origen — Word as Mediator)","logos",            "聖言（道）",              "term"),
    ("Allegoria (allegorical sense)", "allegoria",           "寓意解經",                "term"),
    ("Anagoge (mystical sense)",      "anagoge",             "靈意解經",                "term"),
    ("Spoudaios (the diligent)",      "spoudaios",           "勤勉者",                  "term"),
    ("Hupostasis (substance)",        "hypostasis",          "本體（位格）",            "term"),
    # Diatessaron-specific
    ("Harmony (of Gospels)",          "harmonia evangelica","福音合參",                "term"),
    ("Peshitta (Syriac Bible)",       "Peshitta",            "別西大譯本",              "term"),
    # Scillitan trial vocabulary
    ("Sacramentum (military oath)",   "sacramentum",         "誓約",                    "term"),
    ("Capitalis sententia (capital sentence)","capitalis sententia","死刑判決",        "term"),
    # 2 Clement
    ("Metanoia (repentance)",         "metanoia",            "悔改",                    "term"),
    ("Eulogia (blessing)",            "eulogia",             "祝福",                    "term"),
]

FIRST_SOURCE = "ANF Vol 9"


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
