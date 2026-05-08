#!/usr/bin/env python3
"""
patch_sermon_metadata.py — PATCH a pong_sermons row with extra metadata.

Usage:
  python patch_sermon_metadata.py YYYY-MM-DD
"""
import os
import sys
import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
with open(ROOT / ".env", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()

sys.path.insert(0, str(Path(__file__).parent))
from sermon_2024_metadata import METADATA


def main():
    date = sys.argv[1]
    meta = METADATA.get(date)
    if not meta:
        print(f"no metadata for {date}")
        sys.exit(1)
    sermon_id = int(date.replace("-", ""))
    url = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    r = requests.patch(
        f"{url}/rest/v1/pong_sermons?id=eq.{sermon_id}",
        headers=headers,
        json=meta,
        timeout=30,
    )
    print(f"PATCH {sermon_id}: {r.status_code}")
    if r.ok:
        print(json.dumps(r.json(), ensure_ascii=False, indent=2))
    else:
        print(r.text)


if __name__ == "__main__":
    main()
