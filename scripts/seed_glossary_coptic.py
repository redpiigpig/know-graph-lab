"""Seed the translation glossary with the Coptic (5th-tradition) desert/native
Egyptian fathers whose names are genuinely Coptic-language (not Hellenised
Alexandrians like Cyril/Athanasius, who stay on the Greek track).

User-adjudicated 2026-06-12 (see scripture-fathers SKILL.md 譯名決策節
「科普特第五支」). Native Coptic names are rendered per the Bohairic
(living liturgical) pronunciation, rejecting Greek/Latin endings.

Goes into the `theologians` table (the patristic/theologian home — the new
per-domain glossary tables are owned by another task and untouched here).

Idempotent: skips any entry whose name_english already exists.

Usage:
    python scripts/seed_glossary_coptic.py --dry-run   # report
    python scripts/seed_glossary_coptic.py             # apply
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

FIRST_SOURCE = "科普特第五支"

# name_english, name_original (Coptic), name_latin_std, 繁中建議, 卒年, 理由/notes
ENTRIES = [
    ("Pachomius the Great", "ⲡⲁϧⲱⲙ (Pakhom)", "Pachomius", "帕宏", 348,
     "科普特原名 Pakhom（ⲡⲁϧⲱⲙ），共住隱修制創始人。按波海里腔還原，拒希臘-拉丁化「帕科繆／巴霍米烏斯」。"),
    ("Shenoute of Atripe", "ϣⲉⲛⲟⲩⲧⲉ (Shenoute)", "Sinuthius", "舍努特", 465,
     "純科普特名「神之子」，無希臘對應；白修道院院長。拒「謝努特／舍諾達」。"),
    ("Pishoi (Bishoy) the Great", "ⲡⲓϣⲱⲓ (Pishoi)", "Pisoes", "皮紹依", 417,
     "斯凱提斯沙漠教父，純科普特人名。拒希臘化「比紹伊／畢曉」。"),
    ("Paphnutius of Egypt", "ⲡⲁⲡⲛⲟⲩⲧⲉ (Papnoute)", "Paphnutius", "帕夫努特", 360,
     "科普特名「屬神的人」，拒拉丁尾「帕弗努提烏斯」。"),
    ("Onnophrius (Onuphrius) the Anchorite", "ⲁⲃⲉⲛⲛⲟⲫⲣⲓⲟⲥ (Abennofrios)", "Onuphrius", "奧諾夫里", 400,
     "名源埃及 Wennefer（歐西里斯尊號「常善者」）；沙漠隱士。"),
    ("Besa of Atripe", "ⲃⲏⲥⲁ (Besa)", "Besa", "貝薩", 474,
     "舍努特門徒兼繼任者、白修道院院長，純科普特名。"),
    ("Phib (Apa Phib)", "ⲫⲓⲃ (Phib)", "Phib", "菲布", 350,
     "帕宏同伴、塔本尼西隱修群早期長老，純科普特名。"),
]


def existing_english_names() -> set[str]:
    r = requests.get(f"{URL}/rest/v1/theologians?select=name_english",
                     headers=H_GET, timeout=30)
    r.raise_for_status()
    return {(row.get("name_english") or "").lower() for row in r.json()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    existing = existing_english_names()
    print(f"Existing theologians: {len(existing)}")

    inserts = []
    skipped = 0
    for en, original, latin, zh, died, reason in ENTRIES:
        if en.lower() in existing:
            skipped += 1
            continue
        inserts.append({
            "name_english": en,
            "name_original": original,
            "name_original_lang": "cop",
            "name_latin_std": latin,
            "nationality": "埃及",
            "century": "4-5c",
            "role": "隱修教父",
            "died_year": died,
            "name_recommended": zh,
            "recommendation_reason": reason,
            "first_source": FIRST_SOURCE,
        })

    print(f"Would insert: {len(inserts)} theologians (skipped {skipped})")
    for x in inserts:
        print(f"  + {x['name_english']:42s} -> {x['name_recommended']}")

    if args.dry_run:
        return

    if inserts:
        r = requests.post(f"{URL}/rest/v1/theologians", headers=H_JSON,
                          json=inserts, timeout=60)
        print(f"\ntheologians POST: {r.status_code}")
        if r.status_code not in (200, 201):
            print(f"  body: {r.text[:500]}", file=sys.stderr)
            sys.exit(1)
    print("done")


if __name__ == "__main__":
    main()
