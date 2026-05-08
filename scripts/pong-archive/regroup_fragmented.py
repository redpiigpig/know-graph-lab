"""Dry-run / apply paragraph regrouping for fragmented 龐 sermons (avg <100)."""
from __future__ import annotations

import os
import sys
import argparse
import requests
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from standardize_sermon import (
    regroup_short_paragraphs, _avg_para_len, patch_sermon, patch_media_transcript,
)

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


def fetch_targets(min_avg: int = 100):
    return _query(
        f"""
        WITH s AS (
          SELECT id, sermon_date, content, media_id,
            length(content)::float / GREATEST(1, (length(content) - length(replace(content, E'\\n\\n', '')))/2 + 1) AS avg_para
          FROM pong_sermons
          WHERE preacher LIKE '%龐%' AND content IS NOT NULL AND length(content) > 100
        )
        SELECT id, sermon_date, content, media_id, avg_para
        FROM s WHERE avg_para < {min_avg}
        ORDER BY avg_para ASC
        """
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["dryrun", "apply"])
    ap.add_argument("--min-avg", type=int, default=100)
    ap.add_argument("--ids", help="comma-separated ids to limit scope")
    ap.add_argument("--show-sample", action="store_true",
                    help="show before/after samples for first few rows")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    rows = fetch_targets(args.min_avg)
    if args.ids:
        wanted = set(int(x) for x in args.ids.split(","))
        rows = [r for r in rows if r["id"] in wanted]

    n_changed = 0
    for i, row in enumerate(rows):
        old = row["content"]
        new = regroup_short_paragraphs(old)
        old_avg = _avg_para_len(old)
        new_avg = _avg_para_len(new)
        if new == old:
            print(f"= {row['id']} {row['sermon_date']}  avg {old_avg:.0f} (no change)")
            continue
        para_count_old = old.count("\n\n") + 1
        para_count_new = new.count("\n\n") + 1
        print(f"+ {row['id']} {row['sermon_date']}  avg {old_avg:.0f}→{new_avg:.0f}  paragraphs {para_count_old}→{para_count_new}")
        if args.show_sample and i < 3:
            print(f"   --- BEFORE first 200 ---")
            print("   " + repr(old[:200]))
            print(f"   --- AFTER first 200 ---")
            print("   " + repr(new[:200]))
        if args.mode == "apply":
            patch_sermon(row["id"], {"content": new})
            if row.get("media_id"):
                patch_media_transcript(row["media_id"], new)
            n_changed += 1

    print(f"# total {len(rows)}, {'applied' if args.mode == 'apply' else 'would apply'} {n_changed if args.mode == 'apply' else sum(1 for r in rows if regroup_short_paragraphs(r['content']) != r['content'])}")


if __name__ == "__main__":
    main()
