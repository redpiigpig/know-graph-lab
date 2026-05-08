"""Backfill generic titles ('主日證道'/'主日崇拜'/'') from occasion.

For 龐 sermons whose title is one of the generic strings AND occasion is set,
copy occasion → title so the year-list and detail page show the specific
liturgical day instead of the catch-all '主日證道'.
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


def fetch_targets() -> list[dict]:
    r = requests.get(
        f"{URL}/rest/v1/pong_sermons"
        "?select=id,sermon_date,title,occasion"
        "&preacher=like.*龐*"
        "&title=in.(主日證道,主日崇拜,)"
        "&occasion=not.is.null"
        "&order=sermon_date",
        headers={"apikey": KEY, "Authorization": f"Bearer {KEY}"},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["dryrun", "apply"])
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    rows = fetch_targets()
    n = 0
    for row in rows:
        new_title = row["occasion"]
        print(f"+ {row['id']} {row['sermon_date']}  title={row['title']!r} → {new_title!r}")
        if args.mode == "apply":
            patch_sermon(row["id"], {"title": new_title})
            n += 1
    print(f"# total {len(rows)}, applied {n}")


if __name__ == "__main__":
    main()
