"""Seed the translation glossary with curated person/place/work/sect/term
entries unique to ANF Vol 5 (Hippolytus — Refutation of All Heresies, On
Christ and Antichrist, Commentary on Daniel; Cyprian — 82 Epistles +
treatises; Caius of Rome — fragments; Novatian — On the Trinity, On
Jewish Meats; Appendix).

Pulls source-of-truth from sweep_book_quality.TERM_FIXES_ANF_VOL_5 plus a
hand-curated table of CORRECT terms with English / original-language
companions. Inserts into:
  - theologians          → entity_type='person' implicit
  - theological_terms    → with entity_type in {place,work,sect,term}

Idempotent: skips entries whose name_english/term_english already exists.

Usage:
    python scripts/seed_glossary_anf_vol5.py            # apply
    python scripts/seed_glossary_anf_vol5.py --dry-run  # report
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
    # Hippolytus & opponents (Roman schism over modalism)
    ("Pope Callistus I",                    "Callistus I",         "教宗加里斯都一世",          "person"),
    ("Pope Zephyrinus",                     "Zephyrinus",          "教宗澤斐林諾",              "person"),
    ("Pope Pontian",                        "Pontianus",           "教宗龐謙",                  "person"),
    ("Pope Urban I",                        "Urbanus I",           "教宗烏爾巴諾一世",          "person"),
    ("Noetus of Smyrna",                    "Noetus",              "諾愛圖",                    "person"),
    ("Sabellius (Modalist)",                "Sabellius",           "撒伯流",                    "person"),
    ("Theodotus of Byzantium (the Cobbler)","Theodotus",           "拜占庭的狄奧多圖",          "person"),
    ("Simon Magus",                         "Simon Magus",         "行邪術的西門",              "person"),
    ("Basilides",                           "Basilides",           "巴西里德",                  "person"),
    ("Carpocrates",                         "Carpocrates",         "卡爾波克拉特",              "person"),
    ("Cerinthus",                           "Cerinthus",           "克林妥斯",                  "person"),

    # Cyprian's correspondents, allies, opponents (Carthage + Rome)
    ("Pope Cornelius",                      "Cornelius",           "教宗高乃流",                "person"),
    ("Pope Lucius I",                       "Lucius I",            "教宗路濟",                  "person"),
    ("Pope Stephen I",                      "Stephanus I",         "教宗斯德望一世",            "person"),
    ("Pope Fabian",                         "Fabianus",            "教宗法比盎",                "person"),
    ("Pontius the Deacon (biographer)",     "Pontius Diaconus",    "執事彭修",                  "person"),
    ("Caecilius (Cyprian's mentor)",        "Caecilianus",         "凱基琉（居普良之師）",      "person"),
    ("Donatus (Cyprian correspondent)",     "Donatus",             "多納徒（居普良通信者）",    "person"),
    ("Demetrian (proconsul)",               "Demetrianus",         "德米特里安",                "person"),
    ("Fortunatus (rival bishop)",           "Fortunatus",          "福爾圖那特",                "person"),
    ("Felicissimus (Carthage schismatic)",  "Felicissimus",        "費利西西穆",                "person"),
    ("Maximus (Roman confessor)",           "Maximus",             "馬克西穆",                  "person"),
    ("Nicostratus (deacon)",                "Nicostratus",         "尼科斯特拉",                "person"),
    ("Privatus of Lambaesa",                "Privatus Lambaesitanus","蘭巴埃西斯的普里瓦圖",  "person"),
    ("Quirinus (Cyprian's son in faith)",   "Quirinus",            "奎利努",                    "person"),
    ("Pupianus (Cyprian correspondent)",    "Pupianus",            "普皮安",                    "person"),
    ("Magnus (Cyprian correspondent)",      "Magnus",              "馬格努",                    "person"),
    ("Florentius (Cyprian correspondent)",  "Florentius",          "佛羅倫修",                  "person"),
    ("Jubaianus (bishop)",                  "Iubaianus",           "尤拜安",                    "person"),
    ("Firmilian of Caesarea",               "Firmilianus",         "凱撒利亞的菲爾米連",        "person"),
    ("Mappalicus (martyr)",                 "Mappalicus",          "馬帕利庫",                  "person"),

    # Roman emperors of the persecution era
    ("Decius (emperor)",                    "Decius",              "德修",                      "person"),
    ("Trebonianus Gallus (emperor)",        "Trebonianus Gallus",  "特雷波尼安‧加盧斯",        "person"),
    ("Valerian (emperor)",                  "Valerianus",          "瓦勒良",                    "person"),
    ("Gallienus (emperor)",                 "Gallienus",           "伽利努斯",                  "person"),
    ("Aurelian (emperor)",                  "Aurelianus",          "奧勒良",                    "person"),

    # Caius / Gaius of Rome (presbyter, Hippolytus's contemporary)
    ("Caius of Rome (presbyter)",           "Gaius",               "羅馬的該猶",                "person"),

    # ── Places ─────────────────────────────────────────────────────────
    ("Carthage",                            "Carthago",            "迦太基",                    "place"),
    ("Curubis (place of Cyprian's exile)",  "Curubis",             "庫魯比斯",                  "place"),
    ("Lambaesa (Numidia)",                  "Lambaesis",           "蘭巴埃西斯",                "place"),
    ("Smyrna (Noetus)",                     "Smyrna",              "士每拿",                    "place"),
    ("Sardinia (Hippolytus exile)",         "Sardinia",            "撒丁島",                    "place"),

    # ── Sects ─────────────────────────────────────────────────────────
    ("Patripassians / Modalist Monarchians","Patripassiani / Sabelliani","聖父受苦派／撒伯流派","sect"),
    ("Adoptionists (Theodotian)",           "Theodotiani",         "嗣子論派（狄奧多圖派）",    "sect"),
    ("Novatianists / Cathari",              "Novatiani / Cathari","諾窪天派／清潔派",          "sect"),
    ("Naasenes (Ophite branch)",            "Naasseni",            "那哈申派",                  "sect"),
    ("Perates",                             "Peratae",             "佩拉特派",                  "sect"),
    ("Sethians",                            "Sethiani",            "塞特派",                    "sect"),
    ("Elcesaites",                          "Elchasaitae",         "厄爾克塞派",                "sect"),
    ("Cathari (rigorist purists)",          "Cathari",             "清潔派（嚴格派）",          "sect"),

    # ── Works ─────────────────────────────────────────────────────────
    # Hippolytus
    ("Refutation of All Heresies (Philosophumena)", "Philosophumena", "駁諸異端", "work"),
    ("Treatise on Christ and Antichrist",   "De Christo et Antichristo","論基督與敵基督",       "work"),
    ("Commentary on Daniel (Hippolytus)",   "Commentarius in Danielem","但以理書註釋",         "work"),
    ("Apostolic Tradition (attrib. Hippolytus)","Traditio Apostolica","使徒傳統",               "work"),
    ("Against Noetus",                      "Contra Noetum",       "駁諾愛圖",                  "work"),
    ("On the Universe (fragment)",          "De Universo",         "論宇宙（殘篇）",            "work"),

    # Cyprian — treatises (Epistles handled as a single corpus)
    ("On the Unity of the Church",          "De Unitate Ecclesiae","論教會的合一",              "work"),
    ("On the Lapsed",                       "De Lapsis",           "論墮落者",                  "work"),
    ("On the Lord's Prayer (Cyprian)",      "De Dominica Oratione","論主禱文",                  "work"),
    ("On Mortality",                        "De Mortalitate",      "論死亡",                    "work"),
    ("On Works and Alms",                   "De Opere et Eleemosynis","論善工與賙濟",          "work"),
    ("On the Good of Patience",             "De Bono Patientiae",  "論忍耐的好處",              "work"),
    ("On Jealousy and Envy",                "De Zelo et Livore",   "論嫉妒與妬忌",              "work"),
    ("On the Dress of Virgins",             "De Habitu Virginum",  "論貞女裝束",                "work"),
    ("Three Books of Testimonies to Quirinus","Ad Quirinum Testimonia","給奎利努的見證三卷",  "work"),
    ("To Donatus",                          "Ad Donatum",          "致多納徒書",                "work"),
    ("To Demetrian",                        "Ad Demetrianum",      "致德米特里安書",            "work"),
    ("Exhortation to Martyrdom (Cyprian)",  "Ad Fortunatum",       "致福爾圖那特勸殉道書",      "work"),
    ("The Epistles of Cyprian",             "Epistulae Cypriani",  "居普良書信集",              "work"),
    ("Life and Passion of Cyprian (Pontius)","Vita Cypriani",      "居普良傳記",                "work"),

    # Caius (Gaius) of Rome
    ("Dialogue with Proclus (Caius)",       "Dialogus cum Proclo","與普羅克路的對話",          "work"),

    # Novatian
    ("On the Trinity (Novatian)",           "De Trinitate",        "論三位一體（諾窪天）",      "work"),
    ("On Jewish Meats",                     "De Cibis Iudaicis",   "論猶太食物",                "work"),
    ("On the Shows (Novatian)",             "De Spectaculis (Novatianus)","論觀劇（諾窪天）",  "work"),
    ("On the Good of Modesty (Novatian)",   "De Bono Pudicitiae","論貞操的好處（諾窪天）",    "work"),

    # ── Terms ─────────────────────────────────────────────────────────
    # Cyprian's signature ecclesiology
    ("Cathedra Petri (Chair of Peter)",     "cathedra Petri",      "彼得的座席",                "term"),
    ("Episcopatus (episcopate)",            "episcopatus",         "主教職",                    "term"),
    ("Lapsi (the lapsed)",                  "lapsi",               "墮落者",                    "term"),
    ("Libellatici (cert-holders)",          "libellatici",         "持證背教者",                "term"),
    ("Sacrificati (those who sacrificed)",  "sacrificati",         "獻祭背教者",                "term"),
    ("Confessores (confessors)",            "confessores",         "宣信者",                    "term"),
    ("Pax Ecclesiae (peace of the Church)", "pax ecclesiae",       "教會的平安",                "term"),
    ("Communicatio (communion)",            "communicatio",        "聖事相通",                  "term"),
    ("Re-baptism (rebaptismal controversy)", "rebaptismus",        "再洗禮（重洗）",            "term"),
    ("Plebs (lay congregation)",            "plebs",               "平信徒會眾",                "term"),
    ("Schisma (schism)",                    "schisma",             "分裂",                      "term"),

    # Hippolytus / Novatian Trinitarian vocabulary
    ("Monarchia (divine monarchy)",         "monarchia",           "獨一主權",                  "term"),
    ("Economy (oikonomia)",                 "oikonomia",           "經綸",                      "term"),
    ("Prosopon (face/person)",              "prosopon",            "面位（位格）",              "term"),
    ("Probole (projection / emanation)",    "probole",             "流出（投射）",              "term"),
]

FIRST_SOURCE = "ANF Vol 5"


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
