"""
episcopal-portrait-prep-batches.py — slice remaining bishop candidates into Haiku-sized batches.

Pulls all `episcopal_succession` rows with `portrait_url IS NULL` and `name_en IS NOT NULL`,
sorted by "likely fame" (modern era first; well-documented sees first), writes batches of
N rows to c:/tmp/episcopal_batches/batch_NNN.jsonl.

Each line is `{id, name_zh, name_en, see, succession_number, start_year, end_year, notes}`
where notes is truncated to 200 chars.

Usage:
    python scripts/episcopal-portrait-prep-batches.py            # all candidates, 100/batch
    python scripts/episcopal-portrait-prep-batches.py --size 50  # 50 per batch
    python scripts/episcopal-portrait-prep-batches.py --limit 50 # cap to first 50 (POC)
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

PROJECT_REF = ENV['SUPABASE_URL'].split('//')[1].split('.')[0]
ADMIN_TOKEN = ENV['SUPABASE_ACCESS_TOKEN']

OUT_DIR = Path('c:/tmp/episcopal_batches')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--size', type=int, default=100, help='Bishops per batch')
    ap.add_argument('--limit', type=int, default=0, help='Cap total (0=all)')
    args = ap.parse_args()

    # Fame heuristic:
    #  - 'famous' sees (well-known to Wikipedia editors) ordered first
    #  - within each see, modern bishops first (year DESC, then succession DESC)
    sql = """
    SELECT id, name_zh, name_en, see, church, succession_number, start_year, end_year,
           LEFT(COALESCE(notes, ''), 200) AS notes_snippet
    FROM episcopal_succession
    WHERE portrait_url IS NULL
      AND name_en IS NOT NULL
    ORDER BY
      CASE see
        WHEN '羅馬' THEN 1
        WHEN '坎特伯里' THEN 2
        WHEN '君士坦丁堡' THEN 3
        WHEN '亞歷山卓' THEN 4
        WHEN '安提阿' THEN 5
        WHEN '耶路撒冷' THEN 6
        WHEN '埃奇米亞津' THEN 7
        WHEN '莫斯科' THEN 8
        WHEN '希波' THEN 9
        WHEN '米蘭' THEN 10
        ELSE 100
      END,
      COALESCE(start_year, -9999) DESC,
      COALESCE(succession_number, -1) DESC;
    """
    r = requests.post(
        f'https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query',
        headers={'Authorization': f'Bearer {ADMIN_TOKEN}', 'Content-Type': 'application/json'},
        json={'query': sql}, timeout=30,
    )
    if r.status_code != 201:
        raise RuntimeError(f'DB query failed: {r.status_code} {r.text[:300]}')
    rows = r.json()
    if args.limit:
        rows = rows[:args.limit]
    print(f'Total candidates: {len(rows)}')

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # wipe stale batches
    for old in OUT_DIR.glob('batch_*.jsonl'):
        old.unlink()

    n_batches = 0
    for i in range(0, len(rows), args.size):
        n_batches += 1
        batch_path = OUT_DIR / f'batch_{n_batches:03d}.jsonl'
        with batch_path.open('w', encoding='utf-8') as f:
            for row in rows[i:i + args.size]:
                f.write(json.dumps(row, ensure_ascii=False) + '\n')
    print(f'Wrote {n_batches} batches to {OUT_DIR}')

if __name__ == '__main__':
    main()
