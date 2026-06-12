"""TEMP demo seed for the ACCS commentary layer — lets the /scripture reader
render the 經文上·註釋下 layout for Genesis 1 *before* the real 校園 ACCS PDF is
OCR'd.

⚠️ NOT ACCS text. Bodies below are my own one-line 繁中 summaries of well-known,
public-domain patristic positions (Basil Hexaemeron / Augustine / Ambrose, all
pre-1900 public domain), purely to exercise the UI. source_vol is marked as a
placeholder. Once ingest_accs_genesis.py runs, real ACCS rows replace these
(delete demo first: DELETE FROM accs_commentary WHERE source_vol LIKE '（公有領域示範%').

Usage: python scripts/seed_accs_genesis_demo.py   [--delete]
"""
from __future__ import annotations
import os, sys
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
for line in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip().lstrip("﻿"), v.strip().strip("'\""))
sys.path.insert(0, str(ROOT / "scripts"))
from accs_commentary import build_rows  # noqa: E402

URL = os.environ["SUPABASE_URL"]; KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
SOURCE = "（公有領域示範，待 ACCS 校園版 OCR 取代）"

ENTRIES = [
    {"ref": "1:1-2", "kind": "overview", "heading": "天地的受造",
     "body": "教父普遍視「起初」為萬有的開端，強調神由無中創造，並在「天地」二字中讀出有形與無形受造界的全體。〔示範摘要〕"},
    {"ref": "1:1-2", "kind": "comment", "father": "巴西流", "father_en": "Basil the Great",
     "work": "創世六日", "body": "「起初」不指時間的某一刻，而是受造界之始；世界既有開端，亦必有終結。〔示範摘要，非校園版原文〕"},
    {"ref": "1:1-2", "kind": "comment", "father": "奧古斯丁", "father_en": "Augustine",
     "work": "論創世記字義", "body": "未成形的「空虛混沌」並非與神並存的質料，而是受造、尚待被形塑的初始狀態。〔示範摘要〕"},
    {"ref": "1:3-5", "kind": "overview", "heading": "光的受造與晝夜之分",
     "body": "諸教父多以此光為在日月受造之前、神話語直接造成的本初之光，並引向基督為真光的預表。〔示範摘要〕"},
    {"ref": "1:3-5", "kind": "comment", "father": "安波羅修", "father_en": "Ambrose",
     "work": "創世六日", "body": "神不需器具或材料，僅以話語使光存在，顯明創造之工全憑神的命令。〔示範摘要〕"},
    {"ref": "1:3-5", "kind": "comment", "father": "金口若望", "father_en": "John Chrysostom",
     "work": "創世記講道", "body": "摩西以樸素之語向初信者述說奧祕，使凡人皆能領受造物主的智慧。〔示範摘要〕"},
]


def main():
    if "--delete" in sys.argv:
        r = requests.delete(f"{URL}/rest/v1/accs_commentary?source_vol=like.（公有領域示範*",
                            headers=H, timeout=30)
        print("deleted demo:", r.status_code); return
    rows = build_rows("gen", 1, ENTRIES, SOURCE)
    url = (f"{URL}/rest/v1/accs_commentary"
           "?on_conflict=book_code,chapter,verse_start,verse_end,entry_order")
    r = requests.post(url, headers={**H, "Prefer": "resolution=merge-duplicates,return=minimal"},
                      json=rows, timeout=60)
    print(f"upsert {r.status_code}: {len(rows)} demo rows")
    if r.status_code >= 300:
        print(r.text[:300])


if __name__ == "__main__":
    main()
