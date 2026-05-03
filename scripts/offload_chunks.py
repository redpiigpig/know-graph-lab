#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Offload chunk content from Supabase to local JSONL files (one per ebook).
Replaces ebook_chunks.content with a 200-char preview to keep DB under quota.

Local layout:
  G:\我的雲端硬碟\資料\電子書\_chunks\{ebook_id}.jsonl
    {"chunk_index": 0, "page_number": 1, "chapter_path": null, "content": "..."}
    {"chunk_index": 1, ...}

Usage:
  python scripts/offload_chunks.py dryrun       # show plan only
  python scripts/offload_chunks.py export       # write JSONL files (no DB change)
  python scripts/offload_chunks.py truncate     # update DB content -> 200 char preview
  python scripts/offload_chunks.py all          # export then truncate
"""
import json
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    os.system("pip install requests -q")
    import requests

CHUNKS_DIR = Path('G:/我的雲端硬碟/資料/電子書/_chunks')
PREVIEW_LEN = 200
BATCH_SIZE = 500  # chunks per fetch


def load_env():
    env = {}
    with open('.env', 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            if '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env


ENV = load_env()
URL = ENV['SUPABASE_URL']
KEY = ENV['SUPABASE_SERVICE_ROLE_KEY']
PAT = ENV['SUPABASE_ACCESS_TOKEN']
PROJECT_REF = URL.split('//')[1].split('.')[0]
H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json'}
MGMT_H = {'Authorization': f'Bearer {PAT}', 'Content-Type': 'application/json'}


def mgmt_query(sql, timeout=120):
    r = requests.post(
        f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query",
        headers=MGMT_H, json={'query': sql}, timeout=timeout
    )
    return r


def get_ebook_ids():
    """Return list of ebook ids that have at least one chunk."""
    r = mgmt_query("SELECT DISTINCT ebook_id FROM ebook_chunks ORDER BY ebook_id;")
    return [row['ebook_id'] for row in r.json()]


def get_chunks_for_ebook(ebook_id):
    """Fetch all chunks for one ebook, ordered by chunk_index."""
    r = requests.get(
        f"{URL}/rest/v1/ebook_chunks"
        f"?ebook_id=eq.{ebook_id}"
        f"&select=chunk_index,chunk_type,page_number,chapter_path,content"
        f"&order=chunk_index.asc",
        headers=H, timeout=120
    )
    if r.status_code != 200:
        raise RuntimeError(f"fetch chunks failed: HTTP {r.status_code}")
    return r.json()


def cmd_dryrun():
    ids = get_ebook_ids()
    print(f"Books with chunks: {len(ids)}", file=sys.stderr)
    print(f"Will write to: {CHUNKS_DIR}", file=sys.stderr)
    # Estimate size
    r = mgmt_query(
        "SELECT COUNT(*) as n, pg_size_pretty(SUM(LENGTH(content))::bigint) as text_size "
        "FROM ebook_chunks;"
    )
    print(f"DB stats: {r.json()}", file=sys.stderr)


def cmd_export():
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    ids = get_ebook_ids()
    print(f"Exporting {len(ids)} ebooks to {CHUNKS_DIR}", file=sys.stderr)

    written = 0
    skipped = 0
    for i, eid in enumerate(ids, 1):
        target = CHUNKS_DIR / f"{eid}.jsonl"
        if target.exists() and target.stat().st_size > 0:
            skipped += 1
            continue
        try:
            chunks = get_chunks_for_ebook(eid)
            with open(target, 'w', encoding='utf-8') as f:
                for c in chunks:
                    f.write(json.dumps(c, ensure_ascii=False) + '\n')
            written += 1
            if written % 50 == 0:
                print(f"  exported {written}/{len(ids)}", file=sys.stderr)
        except Exception as e:
            print(f"  FAIL {eid}: {e}", file=sys.stderr)

    print(f"\nWrote: {written}, Skipped (already exists): {skipped}", file=sys.stderr)


def cmd_truncate():
    """Update DB: replace content with first 200 chars."""
    print(f"Truncating DB content to first {PREVIEW_LEN} chars...", file=sys.stderr)
    sql = f"""
UPDATE ebook_chunks
SET content = LEFT(content, {PREVIEW_LEN})
WHERE LENGTH(content) > {PREVIEW_LEN};
"""
    r = mgmt_query(sql, timeout=600)
    print(f"Truncate: HTTP {r.status_code}", file=sys.stderr)
    print(f"Body: {r.text[:200]}", file=sys.stderr)

    # Vacuum to reclaim space
    print("\nVACUUM (FULL) ebook_chunks (may take a few min)...", file=sys.stderr)
    r = mgmt_query("VACUUM (FULL) ebook_chunks;", timeout=900)
    print(f"VACUUM: HTTP {r.status_code}: {r.text[:200]}", file=sys.stderr)

    # Check final size
    r = mgmt_query("SELECT pg_size_pretty(pg_database_size(current_database())) as size;")
    print(f"DB size now: {r.json()}", file=sys.stderr)


def cmd_all():
    cmd_dryrun()
    cmd_export()
    cmd_truncate()


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'dryrun'
    if cmd == 'dryrun':
        cmd_dryrun()
    elif cmd == 'export':
        cmd_export()
    elif cmd == 'truncate':
        cmd_truncate()
    elif cmd == 'all':
        cmd_all()
    else:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
