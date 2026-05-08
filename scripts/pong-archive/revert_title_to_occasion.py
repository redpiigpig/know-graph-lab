"""Revert the title-from-occasion backfill: title was the sermon theme, not the
liturgical day. Where I copied occasion → title in error, restore '主日崇拜'.

Detects patched rows by `title NOT IN ('主日證道','主日崇拜','') AND title = occasion`.
"""
from __future__ import annotations

import os
import sys
import argparse
import requests
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from standardize_sermon import patch_sermon

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
        "SELECT id, sermon_date, title, occasion "
        "FROM pong_sermons "
        "WHERE preacher LIKE '%龐%' "
        "  AND title NOT IN ('主日證道', '主日崇拜', '') "
        "  AND title IS NOT NULL "
        "  AND title = occasion "
        "ORDER BY sermon_date"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["dryrun", "apply"])
    ap.add_argument("--placeholder", default="主日崇拜",
                    help="value to restore (default: 主日崇拜)")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    rows = fetch_targets()
    n = 0
    for row in rows:
        print(f"- {row['id']} {row['sermon_date']}  title={row['title']!r} → {args.placeholder!r}  (occasion={row['occasion']!r} stays)")
        if args.mode == "apply":
            patch_sermon(row["id"], {"title": args.placeholder})
            n += 1
    print(f"# total {len(rows)}, {'reverted' if args.mode == 'apply' else 'would revert'} {n if args.mode == 'apply' else len(rows)}")


if __name__ == "__main__":
    main()
