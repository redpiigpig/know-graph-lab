"""Dry-run / apply occasion backfill for 龐 sermons missing `occasion`.

Pulls all rows where preacher contains 龐 and occasion IS NULL, runs
derive_occasion() on the content, and reports / patches.

Usage:
    python backfill_occasion.py dryrun         # report what would change
    python backfill_occasion.py apply          # actually patch DB
"""
from __future__ import annotations

import os
import sys
import argparse
import requests
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from standardize_sermon import derive_occasion, patch_sermon

URL = os.environ["SUPABASE_URL"].rstrip("/")
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
TOKEN = os.environ["SUPABASE_ACCESS_TOKEN"]
REF = URL.split("//", 1)[1].split(".", 1)[0]


def _query(sql: str):
    r = requests.post(
        f"https://api.supabase.com/v1/projects/{REF}/database/query",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        json={"query": sql},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def fetch_targets():
    return _query(
        "SELECT id, sermon_date, content, occasion AS old_occasion "
        "FROM pong_sermons "
        "WHERE preacher LIKE '%龐%' "
        "  AND (occasion IS NULL OR occasion IN ('主日證道', '主日崇拜')) "
        "  AND content IS NOT NULL AND length(content) > 100 "
        "ORDER BY sermon_date"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["dryrun", "apply"])
    ap.add_argument("--limit", type=int, default=None,
                    help="cap rows (for sampled dry-run)")
    ap.add_argument("--show-fails", action="store_true",
                    help="print rows whose content didn't match any pattern")
    args = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    rows = fetch_targets()
    if args.limit:
        rows = rows[: args.limit]

    n_match = n_skip = 0
    fails: list[dict] = []
    for row in rows:
        occ = derive_occasion(row["content"])
        if occ and occ != row.get("old_occasion"):
            n_match += 1
            old = row.get("old_occasion") or "NULL"
            print(f"+ {row['id']} {row['sermon_date']}  {old!r} → {occ!r}")
            if args.mode == "apply":
                patch_sermon(row["id"], {"occasion": occ})
        else:
            n_skip += 1
            fails.append(row)

    print()
    print(f"# total {len(rows)}  matched {n_match}  unmatched {n_skip}")
    if args.show_fails:
        print("# unmatched (first 800 chars of opening):")
        for row in fails[:30]:
            print(f"  {row['id']} {row['sermon_date']}: {row['content'][:200]!r}")


if __name__ == "__main__":
    main()
