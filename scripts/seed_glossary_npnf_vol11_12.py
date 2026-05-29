"""Seed glossary with entries unique to NPNF1 Vol 1 (Augustine: Confessions +
Letters) and NPNF2 Vol 4 (Athanasius: Select Works and Letters).

Follows the 2026-05-29 naming decisions:
  - Augustine → 奧古斯丁 / 希波的奧古斯丁 (already in DB)
  - Athanasius → 亞他那修 (NOT 阿塔那修); Arius → 亞流

Idempotent: skips entries whose english name already exists.
Usage: python scripts/seed_glossary_npnf_vol11_12.py [--dry-run]
"""
from __future__ import annotations
import argparse, os, sys
from pathlib import Path
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
URL = os.environ["SUPABASE_URL"]; KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}

V11 = "NPNF1 Vol 1"
V12 = "NPNF2 Vol 4"

# (english, original, chinese, entity_type, first_source)
ENTRIES = [
    # ── NPNF1 Vol 1 Augustine — persons ──────────────────────────────
    ("Monica (mother of Augustine)",   "Monica",      "莫尼卡",            "person", V11),
    ("Patricius (father of Augustine)","Patricius",   "帕特里修",          "person", V11),
    ("Alypius of Thagaste",            "Alypius",      "阿呂皮烏",          "person", V11),
    ("Nebridius (friend of Augustine)","Nebridius",   "涅布里狄烏",        "person", V11),
    ("Adeodatus (son of Augustine)",   "Adeodatus",   "阿得奧達圖",        "person", V11),
    ("Romanianus (patron)",            "Romanianus",  "羅馬尼安努",        "person", V11),
    ("Ponticianus",                    "Ponticianus", "彭提齊安",          "person", V11),
    ("Faustus of Mileve (Manichaean)", "Faustus",     "米利夫的浮士德",    "person", V11),
    ("Pelagius (British monk)",        "Pelagius",    "伯拉糾",            "person", V11),
    # ── NPNF1 Vol 1 — places ─────────────────────────────────────────
    ("Hippo Regius",                   "Hippo",       "希波",              "place", V11),
    ("Thagaste (Numidia)",             "Thagaste",    "塔加斯特",          "place", V11),
    ("Madauros (Madaura)",             "Madaura",     "瑪道拉",            "place", V11),
    ("Ostia (port of Rome)",           "Ostia",       "歐斯提亞",          "place", V11),
    # ── NPNF1 Vol 1 — sects ──────────────────────────────────────────
    ("Manichaeans (Manichaeism)",      "Manichaei",   "摩尼教",            "sect", V11),
    ("Donatists",                      "Donatistae",  "多納圖派",          "sect", V11),
    ("Academics (Academic skeptics)",  "Academici",   "學園派（懷疑論）",  "sect", V11),
    # ── NPNF1 Vol 1 — works ──────────────────────────────────────────
    ("Confessions (Augustine)",        "Confessiones","懺悔錄",            "work", V11),
    ("The Retractations",              "Retractationes","修正錄",          "work", V11),
    # ── NPNF1 Vol 1 — terms ──────────────────────────────────────────
    ("Concupiscence",                  "concupiscentia","私慾偏情",        "term", V11),
    ("Original Sin",                   "peccatum originale","原罪",         "term", V11),

    # ── NPNF2 Vol 4 Athanasius — persons ─────────────────────────────
    ("Arius (Alexandrian presbyter)",  "Areios",      "亞流",              "person", V12),
    ("Antony of Egypt (the Great)",    "Antonios",    "安東尼",            "person", V12),
    ("Constantine the Great",          "Constantinus","君士坦丁",          "person", V12),
    ("Constantius II",                 "Constantius", "君士坦提烏斯",      "person", V12),
    ("Eusebius of Nicomedia",          "Eusebios",    "尼科米底亞的優西比烏","person", V12),
    ("Marcellus of Ancyra",            "Markellos",   "安該拉的馬克勒斯",  "person", V12),
    ("Alexander of Alexandria",        "Alexandros",  "亞歷山卓的亞歷山大","person", V12),
    ("Hosius of Cordova",              "Hosius",      "科爾多瓦的何西烏",  "person", V12),
    ("George of Cappadocia (Arian)",   "Georgios",    "卡帕多細亞的喬治",  "person", V12),
    ("Serapion of Thmuis",             "Serapion",    "特穆伊斯的塞拉皮昂","person", V12),
    # ── NPNF2 Vol 4 — places ─────────────────────────────────────────
    ("Nicaea (Bithynia)",              "Nicaea",      "尼西亞",            "place", V12),
    ("Ariminum (Rimini)",              "Ariminum",    "里米尼",            "place", V12),
    ("Seleucia (Isauria)",             "Seleucia",    "塞琉西亞",          "place", V12),
    # ── NPNF2 Vol 4 — sects ──────────────────────────────────────────
    ("Arians (Arianism)",              "Ariani",      "亞流派",            "sect", V12),
    ("Meletians (Egyptian schism)",    "Meletiani",   "梅勒提烏派",        "sect", V12),
    # ── NPNF2 Vol 4 — works ──────────────────────────────────────────
    ("On the Incarnation of the Word", "De Incarnatione Verbi","論道成肉身","work", V12),
    ("Against the Heathen (Contra Gentes)","Contra Gentes","駁異教徒",     "work", V12),
    ("Life of Antony (Vita Antonii)",  "Vita Antonii","安東尼傳",          "work", V12),
    ("Orations against the Arians",    "Orationes contra Arianos","駁亞流派講辭","work", V12),
    ("De Decretis (Defence of Nicene)","De Decretis", "論尼西亞信經",      "work", V12),
    ("De Synodis (On the Councils)",   "De Synodis",  "論會議",            "work", V12),
    # ── NPNF2 Vol 4 — terms ──────────────────────────────────────────
    ("Homoousios (consubstantial)",    "homoousios",  "同質（同性同體）",  "term", V12),
    ("Homoiousios (of like substance)","homoiousios", "類質（相似本體）",  "term", V12),
    ("Ecumenical Council",             "concilium oecumenicum","大公會議", "term", V12),
]


def existing() -> tuple[set[str], set[str]]:
    r1 = requests.get(f"{URL}/rest/v1/theologians?select=name_english", headers=H_GET, timeout=30)
    r2 = requests.get(f"{URL}/rest/v1/theological_terms?select=term_english", headers=H_GET, timeout=30)
    r1.raise_for_status(); r2.raise_for_status()
    return ({(x.get("name_english") or "").lower() for x in r1.json()},
            {(x.get("term_english") or "").lower() for x in r2.json()})


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    p_ex, t_ex = existing()
    print(f"Existing: {len(p_ex)} theologians, {len(t_ex)} terms")
    ip, it, skip = [], [], 0
    seen = set()
    for en, orig, zh, et, fs in ENTRIES:
        k = (et, en.lower())
        if k in seen: continue
        seen.add(k)
        if et == "person":
            if en.lower() in p_ex: skip += 1; continue
            ip.append({"name_english": en, "name_original": orig, "name_latin_std": en,
                       "name_recommended": zh, "first_source": fs})
        else:
            if en.lower() in t_ex: skip += 1; continue
            it.append({"term_english": en, "term_original": orig, "zh_recommended": zh,
                       "entity_type": et, "first_source": fs})
    print(f"Would insert: {len(ip)} theologians, {len(it)} terms; skipped {skip}")
    if args.dry_run:
        for x in ip: print(f"  person + {x['name_english']} -> {x['name_recommended']}")
        for x in it: print(f"  {x['entity_type']:6s} + {x['term_english']} -> {x['zh_recommended']}")
        return
    if ip:
        r = requests.post(f"{URL}/rest/v1/theologians", headers=H_JSON, json=ip, timeout=60)
        print(f"theologians POST: {r.status_code}", r.text[:300] if r.status_code not in (200,201) else "")
    if it:
        r = requests.post(f"{URL}/rest/v1/theological_terms", headers=H_JSON, json=it, timeout=60)
        print(f"theological_terms POST: {r.status_code}", r.text[:300] if r.status_code not in (200,201) else "")
    print("done")


if __name__ == "__main__":
    main()
