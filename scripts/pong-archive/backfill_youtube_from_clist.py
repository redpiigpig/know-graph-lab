"""Parse 城中教會講道清單/*.txt files and backfill youtube_url for 龐 sermons.

Each block is:
    # <status>           ← ⏳ 未完成 / ✅ 完成 / ⛔ 別人
    YYYY-MM-DD <label>
    <youtube url>
    <blank line>

We backfill the URL for any pong_sermons row whose sermon_date matches a block
date and whose youtube_url is currently NULL/empty. Status doesn't matter for
this purpose — even ⛔ 別人 entries have valid full-service recordings.
"""
from __future__ import annotations

import os
import re
import sys
import argparse
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from standardize_sermon import patch_sermon

URL = os.environ["SUPABASE_URL"].rstrip("/")
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
CLIST_DIR = Path("pong-archive/stores/城中教會講道清單")

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+(.*)$")
URL_RE = re.compile(r"^(https?://(?:www\.)?youtu(?:be\.com|\.be)/\S+)")


def parse_clist() -> dict[str, dict]:
    """Returns {date_iso: {url, label, status, source_file}}."""
    out = {}
    for path in sorted(CLIST_DIR.glob("城中教會講道_*.txt")):
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        i = 0
        status = None
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#"):
                status = line.lstrip("#").strip()
            elif (m := DATE_RE.match(line)):
                date_iso, label = m.group(1), m.group(2).strip()
                # next non-empty line should be URL
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                url_match = None
                if j < len(lines):
                    url_match = URL_RE.match(lines[j].strip())
                if url_match:
                    out[date_iso] = {
                        "url": url_match.group(1),
                        "label": label,
                        "status": status,
                        "source_file": path.name,
                    }
                    i = j
                status = None
            i += 1
    return out


def fetch_targets():
    r = requests.get(
        f"{URL}/rest/v1/pong_sermons"
        "?select=id,sermon_date,title,youtube_url"
        "&preacher=like.*龐*"
        "&or=(youtube_url.is.null,youtube_url.eq.)"
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

    clist = parse_clist()
    print(f"# parsed {len(clist)} entries from clist files")

    rows = fetch_targets()
    print(f"# {len(rows)} pong sermons missing youtube_url")

    n_match = n_miss = 0
    misses = []
    for row in rows:
        d = row["sermon_date"]
        entry = clist.get(d)
        if entry:
            n_match += 1
            print(f"+ {row['id']} {d}  → {entry['url']}  [{entry['status']}]")
            if args.mode == "apply":
                patch_sermon(row["id"], {"youtube_url": entry["url"]})
        else:
            n_miss += 1
            misses.append(row)

    print()
    print(f"# matched {n_match}, no clist entry {n_miss}")
    if n_miss:
        print("# rows with no clist entry:")
        for r in misses:
            print(f"  {r['id']} {r['sermon_date']}  title={r['title']!r}")


if __name__ == "__main__":
    main()
