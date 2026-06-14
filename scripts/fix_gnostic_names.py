"""Normalize person-name transliterations in gnostic_sections.zh to the
/translation-glossary authority (name_recommended is absolute — see
[[feedback_glossary_strict_authority]]).

The 2026-06-06 bulk translation produced inconsistent transliterations for the
same figure (e.g. Yeshua → 耶舒亞 / 耶書亞 within one gospel; Marcion → 馬吉翁
vs glossary's 馬吉安). This applies a curated, high-precision variant→authority
map via deterministic SQL replace (cheaper + safer than re-translation).

Only DISTINCTIVE variants are listed — strings that cannot collide with a
different word/person. Notable exclusions verified by hand:
  · 約書亞 (Joshua) is NOT a Yeshua/Jesus variant — never touch it.
  · 執政官 is a real Roman proconsul/consul in the Acts/dating formulas here,
    NOT the Gnostic Archon (執政者) — left alone.
  · 克勉 (Clement of Rome) ≠ 革利免 (Clement of Alexandria) — different people.

  python -X utf8 scripts/fix_gnostic_names.py --dry     # report counts
  python -X utf8 scripts/fix_gnostic_names.py --apply   # apply
"""
from __future__ import annotations
import os, sys, io, json, argparse, requests
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
load_dotenv(".env")
URL = os.environ["SUPABASE_URL"]
REF = URL.split("//")[1].split(".")[0]
TOK = os.environ["SUPABASE_ACCESS_TOKEN"]
MGMT = f"https://api.supabase.com/v1/projects/{REF}/database/query"
H = {"Authorization": f"Bearer {TOK}", "Content-Type": "application/json"}

# variant → authoritative (name_recommended). Keep each variant DISTINCTIVE.
NAME_FIXES: list[tuple[str, str]] = [
    ("耶舒亞", "耶穌"),      # Yeshua → Jesus (user: 一律照詞庫權威)
    ("耶書亞", "耶穌"),      # Yeshua → Jesus
    ("馬吉翁", "馬吉安"),    # Marcion (馬吉翁派 → 馬吉安派 too)
    ("巴西里得", "巴西理德"),  # Basilides
    ("赫拉克利翁", "赫拉克勒翁"),  # Heracleon
    ("赫拉克里翁", "赫拉克勒翁"),  # Heracleon
]


def q(sql: str):
    r = requests.post(MGMT, headers=H, json={"query": sql}, timeout=120)
    r.raise_for_status()
    return r.json()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    cols = ",\n  ".join(
        f"count(*) FILTER (WHERE text LIKE '%{v}%') AS \"{v}\"" for v, _ in NAME_FIXES)
    counts = q(f"SELECT {cols} FROM gnostic_sections WHERE version_code='zh'")[0]
    print("variant occurrences (sections):")
    for v, r in NAME_FIXES:
        print(f"   {v:8} → {r:8} : {counts[v]}")

    if not args.apply:
        print("\n(dry run — pass --apply to fix)")
        return

    nested = "text"
    for v, r in NAME_FIXES:
        nested = f"replace({nested}, '{v}', '{r}')"
    rows = q(f"""
        WITH upd AS (
          SELECT id, {nested} AS t2, text AS t1
          FROM gnostic_sections WHERE version_code='zh'
        )
        UPDATE gnostic_sections g
        SET text = upd.t2, char_count = length(upd.t2)
        FROM upd WHERE g.id = upd.id AND upd.t1 <> upd.t2
        RETURNING g.id""")
    print(f"\n✓ rows updated: {len(rows)}")


if __name__ == "__main__":
    main()
