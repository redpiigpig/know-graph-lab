"""
episcopal-portrait-apply-haiku.py — apply Haiku-suggested Wikipedia portraits to DB.

Reads all `c:/tmp/episcopal_batches/batch_NNN_haiku.json` files, validates each
`portrait_url` (HEAD request to confirm image still served), and PATCHes
`episcopal_succession.portrait_url`.

Skips entries with portrait_url=null. Idempotent: re-running on the same files
just re-PATCHes the same URLs (safe; PostgREST UPDATE with same value is a no-op).

Usage:
    python scripts/episcopal-portrait-apply-haiku.py            # all batches
    python scripts/episcopal-portrait-apply-haiku.py --batch 1  # one batch
    python scripts/episcopal-portrait-apply-haiku.py --dry      # report only
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import requests

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
ENV = {}
for line in (ROOT / '.env').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.lstrip().startswith('#'):
        k, v = line.split('=', 1)
        ENV[k.strip().lstrip('﻿')] = v.strip()

SUPABASE_URL = ENV['SUPABASE_URL']
SERVICE_KEY = ENV['SUPABASE_SERVICE_ROLE_KEY']
BATCH_DIR = Path('c:/tmp/episcopal_batches')


def head_ok(url: str) -> bool:
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={'User-Agent': 'know-graph-lab/1.0'})
        return r.status_code == 200
    except Exception:
        return False


def patch(bid: str, url: str) -> bool:
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/episcopal_succession?id=eq.{bid}",
        headers={
            'apikey': SERVICE_KEY,
            'Authorization': f'Bearer {SERVICE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal',
        },
        json={'portrait_url': url},
        timeout=15,
    )
    return r.status_code in (200, 204)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--batch', type=int, default=0, help='Process only batch_NNN')
    ap.add_argument('--dry', action='store_true', help='Report only')
    ap.add_argument('--skip-head', action='store_true', help='Skip HEAD verification')
    args = ap.parse_args()

    files = sorted(BATCH_DIR.glob('batch_*_haiku.json'))
    if args.batch:
        files = [BATCH_DIR / f'batch_{args.batch:03d}_haiku.json']

    n_hits = 0
    n_dead = 0
    n_patched = 0
    n_total = 0

    for fp in files:
        if not fp.exists():
            print(f'⚠ Missing {fp.name}')
            continue
        data = json.loads(fp.read_text(encoding='utf-8'))
        for entry in data:
            n_total += 1
            url = entry.get('portrait_url')
            if not url:
                continue
            n_hits += 1
            # Head-verify (Wikipedia URLs occasionally redirect/disappear)
            if not args.skip_head and not head_ok(url):
                print(f'  ✗ DEAD {entry.get("name_en")[:30]:30} {url[-50:]}')
                n_dead += 1
                continue
            if args.dry:
                print(f'  [DRY] {entry.get("name_en")[:30]:30} → {url[-50:]}')
                n_patched += 1
                continue
            if patch(entry['id'], url):
                print(f'  ✓ {entry.get("name_en")[:30]:30} → {url[-50:]}')
                n_patched += 1
            else:
                print(f'  ⚠ PATCH failed for {entry.get("name_en")}')

    print(f'\n=== Done. processed={n_total} hits={n_hits} dead={n_dead} patched={n_patched} ===')


if __name__ == '__main__':
    main()
