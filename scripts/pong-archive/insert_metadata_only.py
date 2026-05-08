#!/usr/bin/env python3
"""
insert_metadata_only.py — create a pong_sermons row WITHOUT a YouTube video.

Used for entries like 2025-12-24 平安夜 where the user has servant info
but no YouTube recording. media_id will be NULL.

Usage:
  python insert_metadata_only.py YYYY-MM-DD
"""
import os
import sys
import json
from datetime import date as _date
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
    date_iso = sys.argv[1]
    meta = METADATA.get(date_iso)
    if not meta:
        print(f"no metadata for {date_iso}")
        sys.exit(1)

    sermon_id = int(date_iso.replace("-", ""))
    url = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

    # Compute church_year (Advent-start)
    d = _date.fromisoformat(date_iso)
    church_year = d.year if d.month < 12 else d.year + 1

    body = {
        "id": sermon_id,
        "sermon_date": date_iso,
        "church_year": church_year,
        "title": meta.get("occasion", "主日證道"),
        "location": "城中教會",
        "has_recording": False,
        "is_published": False,
        **meta,
    }

    # Try INSERT; if it exists, PATCH instead
    r = requests.post(
        f"{url}/rest/v1/pong_sermons",
        headers=headers,
        json=body,
        timeout=30,
    )
    if r.status_code == 409:  # conflict, row exists
        r = requests.patch(
            f"{url}/rest/v1/pong_sermons?id=eq.{sermon_id}",
            headers=headers,
            json=body,
            timeout=30,
        )

    print(f"{date_iso} → status {r.status_code}")
    if r.ok:
        rows = r.json()
        print(json.dumps(rows[0] if rows else {}, ensure_ascii=False, indent=2)[:500])
    else:
        print(r.text)


if __name__ == "__main__":
    main()
