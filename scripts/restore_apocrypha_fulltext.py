"""
Re-import full Vision OCR text from JSONL → ebook_chunks for the 10 apocrypha books.

`vision_ocr_apocrypha.py` follows the standard ebook pattern of writing 200-char
previews to ebook_chunks (full text only lives in JSONL on Drive). For the
apocrypha reader we want full per-page text in DB so `ingest_apocrypha_zh.py`
gets the whole content, not a truncated snippet.

This script:
  1. Reads {book_id}.jsonl on Drive (full Vision text per page)
  2. Replaces ebook_chunks rows with content=full_text (not preview)

Usage:
  python -X utf8 scripts/restore_apocrypha_fulltext.py
"""
from __future__ import annotations
import os, sys, json
from pathlib import Path
import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
SUPABASE_URL = os.environ['SUPABASE_URL']
SERVICE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
CHUNKS_DIR = Path("G:/我的雲端硬碟/資料/電子書/_chunks")

BOOKS = [
    ('OT1', 'b1fbff1b-cbf1-45b6-a9cd-cf0e9f943c57'),
    ('OT2', 'd5e5df29-2428-4dca-9f79-5ca21587d073'),
    ('OT3', 'af50523d-b206-447d-8060-78d4e366ced4'),
    ('OT4', 'a96b524b-464e-419e-8d78-b302d28302d3'),
    ('OT5', '05f4b0a5-f5ba-4a33-8187-34f9c9abbff3'),
    ('OT6', '6aaa0ffe-e8ad-41d2-943e-49d7fd6125d2'),
    ('NT1', '425f2664-e967-4fc0-b053-d79bc1ac106d'),
    ('NT2', '0a1b2977-3d3c-4a47-96cd-0bee1bad17f1'),
    ('NT3', '12156219-cf9c-4610-a84c-5d5358c22817'),
    ('NT4', '677c5e16-5b19-4f9b-9499-ee44d5c3eb01'),
]


def restore_book(label: str, book_id: str):
    jsonl = CHUNKS_DIR / f"{book_id}.jsonl"
    if not jsonl.exists():
        print(f'  {label}: ⚠ no JSONL'); return

    pages = []
    with jsonl.open(encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                pages.append(json.loads(line))
            except Exception: pass

    rows = [{
        'ebook_id': book_id,
        'chunk_index': i,
        'chunk_type': 'page',
        'page_number': p.get('page_number'),
        'chapter_path': p.get('chapter_path'),
        'content': p.get('content', ''),  # FULL text (not preview)
        'char_count': len(p.get('content', '')),
    } for i, p in enumerate(pages)]

    H = {'apikey': SERVICE_KEY, 'Authorization': f'Bearer {SERVICE_KEY}',
         'Content-Type': 'application/json', 'Prefer': 'return=minimal'}

    # Delete existing chunks
    requests.delete(f"{SUPABASE_URL}/rest/v1/ebook_chunks?ebook_id=eq.{book_id}",
                    headers={'apikey': SERVICE_KEY, 'Authorization': f'Bearer {SERVICE_KEY}'},
                    timeout=120)
    # Re-insert with FULL text. Small batches → bigger rows than the 200-char
    # preview pattern, so PostgREST occasionally hits statement_timeout on
    # batch of 50. Drop to 20 with one auto-retry on 5xx.
    BATCH = 20
    for i in range(0, len(rows), BATCH):
        batch = rows[i:i + BATCH]
        for attempt in range(3):
            r = requests.post(f"{SUPABASE_URL}/rest/v1/ebook_chunks",
                              headers=H, json=batch, timeout=180)
            if r.status_code in (200, 201):
                break
            if r.status_code >= 500 and attempt < 2:
                import time
                time.sleep(2 * (attempt + 1))
                continue
            print(f'  {label} batch {i}: ERROR {r.status_code} {r.text[:200]}')
            return
    total_chars = sum(r['char_count'] for r in rows)
    print(f'  {label}: ✓ {len(rows)} chunks, {total_chars//1000}K chars')


if __name__ == '__main__':
    for label, book_id in BOOKS:
        restore_book(label, book_id)
    print('Done.')
