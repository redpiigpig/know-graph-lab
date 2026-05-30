"""Seed glossary with entries unique to NPNF1 Vol 5 (Augustine: Anti-Pelagian
Writings) and NPNF1 Vol 6 (Augustine: Sermon on the Mount + Harmony of the
Gospels + NT Sermons).

Follows the 2026-05-29 naming decisions:
  - Augustine → 奧古斯丁 / 希波的奧古斯丁 (already in DB)
  - Pelagius → 伯拉糾 (already in DB)

Idempotent: skips entries whose english name already exists.
Usage: python scripts/seed_glossary_npnf_vol16_17.py [--dry-run]
"""
from __future__ import annotations
import argparse, os
from pathlib import Path
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
URL = os.environ["SUPABASE_URL"]; KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}

V16 = "NPNF1 Vol 5"
V17 = "NPNF1 Vol 6"

# (english, original, chinese, entity_type, first_source)
ENTRIES = [
    # ── NPNF1 Vol 5 — persons (anti-Pelagian controversy) ─────────────
    ("Caelestius (disciple of Pelagius)", "Caelestius",  "凱萊斯提烏斯",   "person", V16),
    ("Julian of Eclanum",                 "Julianus",    "埃克拉努姆的尤利安","person", V16),
    # ── NPNF1 Vol 5 — works ──────────────────────────────────────────
    ("On the Merits and Forgiveness of Sins, and on the Baptism of Infants",
        "De peccatorum meritis et remissione", "論罪的功過與赦免及嬰兒的洗禮", "work", V16),
    ("On the Spirit and the Letter",      "De Spiritu et Littera", "論聖靈與字句", "work", V16),
    ("On Nature and Grace",               "De Natura et Gratia",   "論自然與恩典", "work", V16),
    ("On Man's Perfection in Righteousness", "De Perfectione Iustitiae Hominis", "論人在義中的完全", "work", V16),
    ("On the Proceedings of Pelagius",    "De Gestis Pelagii",     "論伯拉糾案的審理", "work", V16),
    ("On the Grace of Christ and on Original Sin", "De Gratia Christi et de Peccato Originali", "論基督的恩典與原罪", "work", V16),
    ("On Marriage and Concupiscence",     "De Nuptiis et Concupiscentia", "論婚姻與情慾", "work", V16),
    ("On the Soul and its Origin",        "De Anima et eius Origine", "論靈魂及其起源", "work", V16),
    ("Against Two Letters of the Pelagians", "Contra Duas Epistolas Pelagianorum", "駁伯拉糾派的兩封書信", "work", V16),
    ("On Grace and Free Will",            "De Gratia et Libero Arbitrio", "論恩典與自由意志", "work", V16),
    ("On Rebuke and Grace",               "De Correptione et Gratia", "論責備與恩典", "work", V16),
    ("On the Predestination of the Saints", "De Praedestinatione Sanctorum", "論聖徒的預定", "work", V16),
    ("On the Gift of Perseverance",       "De Dono Perseverantiae", "論堅忍的恩賜", "work", V16),
    # ── NPNF1 Vol 5 — terms ──────────────────────────────────────────
    ("Predestination",                    "praedestinatio",       "預定",       "term", V16),
    ("Final Perseverance",                "perseverantia finalis","終末堅忍",   "term", V16),
    ("Prevenient Grace",                  "gratia praeveniens",   "先在恩典",   "term", V16),
    ("Free Will",                         "liberum arbitrium",    "自由意志",   "term", V16),

    # ── NPNF1 Vol 6 — works ──────────────────────────────────────────
    ("On the Sermon on the Mount",        "De Sermone Domini in Monte", "論主的登山寶訓", "work", V17),
    ("The Harmony of the Gospels",        "De Consensu Evangelistarum", "四福音合參",     "work", V17),
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
