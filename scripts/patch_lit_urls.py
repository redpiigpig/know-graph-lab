"""Patch fulltext_url (and optionally fulltext_status) on lit_review_entries.

Reads a JSON map {ref_key: url}  (or {ref_key: {"url":..., "status":...}}) from a
file or stdin and PATCHes each matching entry for a given project. Used by the
研究回顧 workflow to back-fill open-access links found via WebSearch + curl-verified.

  python -X utf8 scripts/patch_lit_urls.py --project bajingfa --map scripts/data/_url_patch.json

Only ref_keys that exist under the project are touched; missing keys are reported.
"""
from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.environ["SUPABASE_URL"]
SERVICE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}",
     "Content-Type": "application/json"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--map", help="JSON file {ref_key: url|{url,status}}; '-' for stdin")
    args = ap.parse_args()

    raw = sys.stdin.read() if (args.map in (None, "-")) else Path(args.map).read_text("utf-8")
    data = json.loads(raw)

    existing = {e["ref_key"]: e for e in requests.get(
        f"{SUPABASE_URL}/rest/v1/lit_review_entries"
        f"?project_slug=eq.{args.project}&select=ref_key,fulltext_url,fulltext_status",
        headers=H, timeout=60).json()}

    patched, missing = 0, []
    for ref_key, val in data.items():
        if ref_key not in existing:
            missing.append(ref_key); continue
        body = {"fulltext_url": val} if isinstance(val, str) else {
            "fulltext_url": val["url"], **({"fulltext_status": val["status"]} if val.get("status") else {})}
        r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/lit_review_entries"
            f"?project_slug=eq.{args.project}&ref_key=eq.{ref_key}",
            headers={**H, "Prefer": "return=minimal"}, data=json.dumps(body), timeout=60)
        if r.status_code in (200, 204):
            patched += 1
            print(f"  ✓ {ref_key} → {body['fulltext_url'][:70]}")
        else:
            print(f"  ✗ {ref_key}: {r.status_code} {r.text[:150]}")
    print(f"\npatched {patched}/{len(data)}; missing ref_keys: {missing or 'none'}")


if __name__ == "__main__":
    main()
