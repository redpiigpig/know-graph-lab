#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Import data/local_inventory.json into Supabase ebooks table (clears existing first)."""
import json
import os
import sys

try:
    import requests
except ImportError:
    os.system("pip install requests -q")
    import requests


def load_env():
    env_vars = {}
    with open('.env', 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            if '=' in line:
                k, v = line.split('=', 1)
                env_vars[k.strip()] = v.strip()
    return env_vars


def main():
    env = load_env()
    url = env['SUPABASE_URL']
    key = env['SUPABASE_SERVICE_ROLE_KEY']
    headers = {
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
    }

    with open('data/local_inventory.json', 'r', encoding='utf-8') as f:
        inv = json.load(f)

    # Clear existing records
    print("Clearing existing records...", file=sys.stderr)
    r = requests.delete(f"{url}/rest/v1/ebooks?id=not.is.null", headers=headers)
    print(f"Clear: HTTP {r.status_code}", file=sys.stderr)

    # Build records — store local path in file_path
    records = []
    for r in inv:
        title = r.get('book_title') or 'Untitled'
        # Use the new (post-rename) filename's title — re-parse the new_name
        # Actually book_title was set during scan and reflects post-rename state
        records.append({
            'title': title,
            'author': r.get('author'),
            'file_type': r['extension'],
            'category': r.get('category'),
            'subcategory': r.get('subcategory'),
            'file_path': r['target_path'],  # final local path after rename
        })

    print(f"Total records to import: {len(records)}", file=sys.stderr)

    batch_size = 100
    ok = 0
    fail = 0
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        bn = i // batch_size + 1
        try:
            r = requests.post(
                f"{url}/rest/v1/ebooks",
                headers={**headers, 'Prefer': 'resolution=ignore-duplicates'},
                json=batch,
                timeout=30
            )
            if r.status_code in [200, 201]:
                ok += len(batch)
                if bn % 5 == 0 or bn == 1:
                    print(f"Batch {bn}: OK", file=sys.stderr)
            else:
                fail += len(batch)
                print(f"Batch {bn}: HTTP {r.status_code} - {r.text[:200]}", file=sys.stderr)
        except Exception as e:
            fail += len(batch)
            print(f"Batch {bn}: EXCEPTION {str(e)[:100]}", file=sys.stderr)

    print(f"\nResult: {ok} ok, {fail} failed", file=sys.stderr)

    # Verify count via Management API
    PAT = env.get('SUPABASE_ACCESS_TOKEN')
    if PAT:
        project_ref = url.split('//')[1].split('.')[0]
        r = requests.post(
            f"https://api.supabase.com/v1/projects/{project_ref}/database/query",
            headers={'Authorization': f'Bearer {PAT}', 'Content-Type': 'application/json'},
            json={'query': 'SELECT COUNT(*) as total FROM ebooks;'},
            timeout=10
        )
        if r.status_code == 201:
            print(f"DB total: {r.json()[0]['total']}", file=sys.stderr)


if __name__ == '__main__':
    main()
