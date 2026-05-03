#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse ebooks (PDF/EPUB) into ebook_chunks table. Updates parse_progress.txt
checklist as it goes. Skips books already parsed (parsed_at IS NOT NULL).

Usage:
  python scripts/parse_worker.py init          # build checklist from DB
  python scripts/parse_worker.py run            # process all unparsed
  python scripts/parse_worker.py run --limit 5  # only 5 books (dry-run-ish)
  python scripts/parse_worker.py status         # show progress summary
"""
import json
import os
import re
import sys
import time
import traceback
from pathlib import Path
from datetime import datetime

try:
    import requests
    import fitz  # PyMuPDF
    import ebooklib
    from ebooklib import epub
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"Missing: {e}. Run: pip install requests pymupdf ebooklib beautifulsoup4", file=sys.stderr)
    sys.exit(1)

CHECKLIST = 'data/parse_progress.txt'
DRIVE_ROOT = 'G:/我的雲端硬碟/資料/電子書'

# ── env loading ────────────────────────────────────────────────
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
H = {'apikey': KEY, 'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json'}


# ── DB helpers ─────────────────────────────────────────────────
def fetch_unparsed_books(limit=None):
    """Return list of {id, title, file_type, file_path} for ebooks where parsed_at IS NULL."""
    params = 'select=id,title,file_type,file_path&parsed_at=is.null'
    if limit:
        params += f'&limit={limit}'
    r = requests.get(f"{URL}/rest/v1/ebooks?{params}", headers=H, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_all_books():
    """Return all ebooks (paginated)."""
    out = []
    offset = 0
    page_size = 1000
    while True:
        params = f'select=id,title,file_type,file_path,parsed_at,chunk_count,parse_error&order=id&limit={page_size}&offset={offset}'
        r = requests.get(f"{URL}/rest/v1/ebooks?{params}", headers=H, timeout=30)
        r.raise_for_status()
        page = r.json()
        if not page:
            break
        out.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    return out


def insert_chunks(ebook_id, chunks):
    """Bulk insert chunks. Returns number inserted."""
    rows = []
    for i, c in enumerate(chunks):
        rows.append({
            'ebook_id': ebook_id,
            'chunk_index': i,
            'chunk_type': c['type'],
            'page_number': c.get('page'),
            'chapter_path': c.get('chapter_path'),
            'content': c['content'],
            'char_count': len(c['content']),
        })
    # Insert in batches of 100
    for i in range(0, len(rows), 100):
        batch = rows[i:i+100]
        r = requests.post(f"{URL}/rest/v1/ebook_chunks", headers=H, json=batch, timeout=60)
        if r.status_code not in (200, 201):
            raise RuntimeError(f"chunk insert failed: HTTP {r.status_code} {r.text[:300]}")
    return len(rows)


def mark_parsed(ebook_id, chunk_count, total_chars):
    body = {
        'parsed_at': datetime.utcnow().isoformat() + 'Z',
        'chunk_count': chunk_count,
        'total_chars': total_chars,
        'parse_error': None,
    }
    r = requests.patch(f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}", headers=H, json=body, timeout=30)
    if r.status_code not in (200, 204):
        raise RuntimeError(f"mark_parsed failed: HTTP {r.status_code}")


def mark_error(ebook_id, error_msg):
    r = requests.patch(
        f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}",
        headers=H,
        json={'parse_error': error_msg[:1000]},
        timeout=30
    )
    return r.status_code in (200, 204)


def delete_existing_chunks(ebook_id):
    """Used when re-parsing — clear old chunks first."""
    requests.delete(f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebook_id}", headers=H, timeout=30)


# ── parsers ────────────────────────────────────────────────────
def parse_pdf(path):
    """Return list of {type:'page', page:N, content:str}."""
    chunks = []
    doc = fitz.open(path)
    try:
        for i, page in enumerate(doc):
            text = page.get_text()
            if text and text.strip():
                chunks.append({
                    'type': 'page',
                    'page': i + 1,
                    'content': text,
                })
    finally:
        doc.close()
    return chunks


def parse_epub(path):
    """Return list of {type:'chapter', chapter_path, content}."""
    book = epub.read_epub(path)

    # Build TOC map: item href -> chapter title path
    toc_map = {}
    def walk_toc(items, prefix=''):
        for item in items:
            if isinstance(item, tuple):
                section, children = item
                title = section.title if hasattr(section, 'title') else str(section)
                walk_toc(children, prefix + title + ' > ')
            else:
                title = item.title if hasattr(item, 'title') else ''
                href = item.href if hasattr(item, 'href') else ''
                if href:
                    href_clean = href.split('#')[0]
                    toc_map[href_clean] = (prefix + title).rstrip(' > ')
    try:
        walk_toc(book.toc)
    except Exception:
        pass  # TOC parsing best-effort

    chunks = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        href = item.get_name()
        soup = BeautifulSoup(item.get_content(), 'html.parser')
        text = soup.get_text(separator='\n').strip()
        if not text:
            continue
        # Collapse multiple blank lines
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

        chapter_path = toc_map.get(href) or toc_map.get(href.split('/')[-1]) or item.get_name()
        chunks.append({
            'type': 'chapter',
            'chapter_path': chapter_path[:500],  # cap length
            'content': text,
        })
    return chunks


def parse_book(path, file_type):
    """Dispatch parser by file_type. Returns chunks list or raises."""
    ft = file_type.lower()
    if ft == 'pdf':
        return parse_pdf(path)
    elif ft == 'epub':
        return parse_epub(path)
    else:
        raise NotImplementedError(f"format not supported: {ft}")


# ── checklist ──────────────────────────────────────────────────
def write_checklist(books):
    """Build initial checklist from books list."""
    os.makedirs('data', exist_ok=True)
    with open(CHECKLIST, 'w', encoding='utf-8') as f:
        f.write("# Ebook parse progress\n")
        f.write("# [ ] not started   [x] parsed   [!] error   [-] skipped (unsupported format)\n")
        f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
        for b in books:
            mark = ' '
            note = ''
            if b.get('parsed_at'):
                mark = 'x'
                note = f"  ({b.get('chunk_count', '?')} chunks)"
            elif b.get('parse_error'):
                mark = '!'
                note = f"  ERROR: {(b.get('parse_error') or '')[:80]}"
            elif b['file_type'] not in ('pdf', 'epub'):
                mark = '-'
                note = f"  (skip: {b['file_type']})"
            rel_path = (b.get('file_path') or '').replace(DRIVE_ROOT.replace('/', '\\'), '').lstrip('\\')
            f.write(f"[{mark}] {b['id'][:8]} {rel_path}{note}\n")


def update_checklist_line(ebook_id, status, note=''):
    """Replace the line for ebook_id with new status."""
    if not os.path.exists(CHECKLIST):
        return
    with open(CHECKLIST, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if f'] {ebook_id[:8]} ' in line:
            # Strip old status marker and any trailing note
            m = re.match(r'^\[.\] (\S+) (.+?)(  \(\d+ chunks\)|  ERROR:.*|  \(skip:.*\))?\s*$', line)
            if m:
                rel_path = m.group(2)
            else:
                rel_path = line.split(']', 1)[1].strip().split(' ', 1)[1] if ' ' in line.split(']', 1)[1].strip() else ''
            new_line = f"[{status}] {ebook_id[:8]} {rel_path}{note}\n"
            lines[i] = new_line
            break
    with open(CHECKLIST, 'w', encoding='utf-8') as f:
        f.writelines(lines)


# ── commands ───────────────────────────────────────────────────
def cmd_init():
    books = fetch_all_books()
    print(f"Fetched {len(books)} books from DB", file=sys.stderr)
    write_checklist(books)
    print(f"Wrote checklist: {CHECKLIST}", file=sys.stderr)
    # Stats
    parsed = sum(1 for b in books if b.get('parsed_at'))
    errored = sum(1 for b in books if b.get('parse_error'))
    skipped = sum(1 for b in books if b['file_type'] not in ('pdf', 'epub'))
    todo = len(books) - parsed - errored - skipped
    print(f"  parsed: {parsed}, error: {errored}, skip: {skipped}, todo: {todo}", file=sys.stderr)


def cmd_status():
    books = fetch_all_books()
    parsed = sum(1 for b in books if b.get('parsed_at'))
    errored = sum(1 for b in books if b.get('parse_error'))
    skipped = sum(1 for b in books if b['file_type'] not in ('pdf', 'epub'))
    todo = len(books) - parsed - errored - skipped
    total_chunks = 0
    for b in books:
        total_chunks += b.get('chunk_count') or 0
    print(f"Total books: {len(books)}")
    print(f"  parsed:  {parsed}  ({total_chunks} chunks total)")
    print(f"  error:   {errored}")
    print(f"  skip:    {skipped}  (mobi/azw3/azw — pure-Python parsing not supported)")
    print(f"  todo:    {todo}")


def cmd_run(limit=None):
    """Process all unparsed pdf/epub books."""
    # Get all unparsed PDFs and EPUBs
    params = 'select=id,title,file_type,file_path&parsed_at=is.null&parse_error=is.null&file_type=in.(pdf,epub)&order=id'
    if limit:
        params += f'&limit={limit}'
    r = requests.get(f"{URL}/rest/v1/ebooks?{params}", headers=H, timeout=30)
    r.raise_for_status()
    books = r.json()
    print(f"To process: {len(books)} books", file=sys.stderr)

    succeeded = 0
    failed = 0
    for n, b in enumerate(books, 1):
        path = b['file_path']
        ebook_id = b['id']
        title = b['title'][:60]
        ft = b['file_type']

        print(f"\n[{n}/{len(books)}] [{ft}] {title}", file=sys.stderr)

        if not path or not os.path.exists(path):
            err = f"file not found: {path}"
            print(f"  ! {err}", file=sys.stderr)
            mark_error(ebook_id, err)
            update_checklist_line(ebook_id, '!', f"  ERROR: file not found")
            failed += 1
            continue

        try:
            t0 = time.time()
            chunks = parse_book(path, ft)
            if not chunks:
                err = "no extractable text"
                print(f"  ! {err}", file=sys.stderr)
                mark_error(ebook_id, err)
                update_checklist_line(ebook_id, '!', f"  ERROR: {err}")
                failed += 1
                continue

            total_chars = sum(len(c['content']) for c in chunks)
            # Wipe any partial chunks from a previous failed attempt
            delete_existing_chunks(ebook_id)
            insert_chunks(ebook_id, chunks)
            mark_parsed(ebook_id, len(chunks), total_chars)
            update_checklist_line(ebook_id, 'x', f"  ({len(chunks)} chunks, {total_chars:,} chars)")
            elapsed = time.time() - t0
            print(f"  ✓ {len(chunks)} chunks, {total_chars:,} chars, {elapsed:.1f}s", file=sys.stderr)
            succeeded += 1
        except Exception as e:
            err_msg = f"{type(e).__name__}: {str(e)[:200]}"
            print(f"  ! {err_msg}", file=sys.stderr)
            mark_error(ebook_id, err_msg)
            update_checklist_line(ebook_id, '!', f"  ERROR: {err_msg[:80]}")
            failed += 1

    print(f"\n=== Done ===", file=sys.stderr)
    print(f"  succeeded: {succeeded}", file=sys.stderr)
    print(f"  failed:    {failed}", file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == 'init':
        cmd_init()
    elif cmd == 'status':
        cmd_status()
    elif cmd == 'run':
        limit = None
        if '--limit' in sys.argv:
            limit = int(sys.argv[sys.argv.index('--limit') + 1])
        cmd_run(limit)
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)
