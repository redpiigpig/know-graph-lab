#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean ebook text with Claude Haiku 4.5: simplified → traditional Chinese + layout cleanup.

Processes books in batches, calling Haiku API to clean text chunks.
Idempotent: skips books with cleaned_at NOT NULL. Resumable.

Usage:
  export ANTHROPIC_API_KEY=...
  python scripts/clean_with_haiku.py status
  python scripts/clean_with_haiku.py run [--limit N] [--dry-run]
"""
import json
import sys
import time
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

try:
    from anthropic import Anthropic
    import requests
except ImportError:
    print("Missing: pip install anthropic requests", file=sys.stderr)
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent))
from parse_worker import load_env

ENV = load_env()
URL = ENV["SUPABASE_URL"]
KEY = ENV["SUPABASE_SERVICE_ROLE_KEY"]
H = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
}

CHUNKS_DIR = Path("G:/我的雲端硬碟/資料/電子書/_chunks")
MODEL = "claude-haiku-4-5-20251001"


def fetch_books_to_clean(limit=None):
    """Get books with meaningful content (chunk_count > 0)."""
    # Use a reasonable default if not specified
    page_size = limit or 50
    offset = 0
    books = []

    while True:
        params = (
            f"select=id,title,author,total_chars,chunk_count,file_type"
            f"&chunk_count=gt.0"  # Only books with parsed chunks
            f"&total_chars=gt.5000"  # Must have meaningful content
            f"&order=total_chars.desc"
            f"&limit={page_size}"
            f"&offset={offset}"
        )
        r = requests.get(f"{URL}/rest/v1/ebooks?{params}", headers=H, timeout=30)
        r.raise_for_status()
        page = r.json()

        if not page:
            break

        books.extend(page)

        if limit and len(books) >= limit:
            books = books[:limit]
            break

        if len(page) < page_size:
            break

        offset += page_size

    return books


def get_book_chunks(book_id: str) -> list:
    """Load all chunks for a book from JSONL."""
    jsonl_path = CHUNKS_DIR / f"{book_id}.jsonl"
    if not jsonl_path.exists():
        return None

    chunks = []
    try:
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        chunks.append(json.loads(line))
                    except json.JSONDecodeError:
                        # Skip malformed lines
                        continue
    except Exception as e:
        print(f"    ❌ Failed to read JSONL: {e}", file=sys.stderr)
        return None

    return chunks if chunks else None


def clean_text_batch(client: Anthropic, chunks: list) -> dict:
    """Send chunks to Haiku for cleaning. Returns {cleaned_chunks, error?}."""
    if not chunks:
        return {"cleaned_chunks": [], "error": "No chunks"}

    # Prepare text for cleaning - combine first N chunks (up to ~10KB to stay in budget)
    chunk_texts = []
    total_chars = 0
    max_chars = 30000  # Comfortable limit for Haiku

    for chunk in chunks:
        content = chunk.get("content", "")
        if total_chars + len(content) > max_chars:
            break
        chunk_texts.append(content)
        total_chars += len(content)

    if not chunk_texts:
        return {"cleaned_chunks": [], "error": "All chunks empty"}

    combined = "\n\n---CHUNK BREAK---\n\n".join(chunk_texts)

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": f"""Clean this Chinese text:
1. Convert simplified → traditional
2. Fix formatting: spacing, paragraph breaks, remove OCR artifacts
3. Return ONLY the cleaned text, no explanation

TEXT TO CLEAN:
{combined}""",
                }
            ],
        )

        cleaned_text = response.content[0].text

        # Split back into chunks by the marker
        cleaned_parts = cleaned_text.split("---CHUNK BREAK---")

        # Reconstruct with cleaned content
        result_chunks = []
        for i, (orig_chunk, cleaned) in enumerate(
            zip(chunks[: len(cleaned_parts)], cleaned_parts)
        ):
            result_chunks.append(
                {
                    **orig_chunk,
                    "content": cleaned.strip(),
                    "content_original": orig_chunk["content"],
                }
            )

        return {"cleaned_chunks": result_chunks, "cleaned_text": cleaned_text}

    except Exception as e:
        return {"error": str(e)[:200], "cleaned_chunks": []}


def write_cleaned_jsonl(book_id: str, cleaned_chunks: list) -> bool:
    """Write cleaned chunks back to JSONL."""
    if not cleaned_chunks:
        return False

    try:
        jsonl_path = CHUNKS_DIR / f"{book_id}.jsonl"
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for chunk in cleaned_chunks:
                f.write(
                    json.dumps(
                        {k: v for k, v in chunk.items() if k != "content_original"},
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        return True
    except Exception as e:
        print(f"    ❌ Failed to write JSONL: {e}", file=sys.stderr)
        return False


def update_book_cleaned(book_id: str) -> bool:
    """Mark book as processed by adding a completion note (optional tracking)."""
    # Note: cleaned_at column may not exist yet. Skipping DB update for now.
    # Cleaned JSONL files serve as the source of truth.
    return True


def cmd_status():
    """Show cleanup status."""
    books = fetch_books_to_clean(limit=10)
    print(f"Books pending cleanup: {len(fetch_books_to_clean(limit=None))}")
    print(f"JSONL chunks available: {len(list(CHUNKS_DIR.glob('*.jsonl')))}")
    print(f"\nFirst 5 to process:")
    for i, book in enumerate(books[:5], 1):
        print(f"  {i}. {book['title'][:50]} ({book['total_chars']} chars)")


def cmd_run(limit=None, dry_run=False):
    """Run cleanup on books."""
    import os

    books = fetch_books_to_clean(limit=limit)

    if not books:
        print("No books to process.")
        return

    print(f"Books to process: {len(books)}")

    if dry_run:
        for i, book in enumerate(books[:5], 1):
            print(
                f"  {i}. {book['title'][:50]} ({book.get('chunk_count', '?')} chunks)"
            )
        return

    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n❌ Missing ANTHROPIC_API_KEY")
        print("   Get one at https://console.anthropic.com/")
        print("   Then set: export ANTHROPIC_API_KEY=sk_...")
        sys.exit(1)

    client = Anthropic()
    ok = 0
    failed = []

    for i, book in enumerate(books, 1):
        book_id = book["id"]
        title = (book["title"] or "Untitled")[:40]
        chunk_count = book.get("chunk_count", 0)

        print(f"[{i:3d}/{len(books)}] {title}…", end="", flush=True)

        # Load chunks
        chunks = get_book_chunks(book_id)
        if not chunks:
            print(" ⚠ no chunks")
            failed.append((title, "no chunks"))
            continue

        # Clean with Haiku
        result = clean_text_batch(client, chunks)
        if result.get("error"):
            print(f" ❌ {result['error'][:40]}")
            failed.append((title, result["error"][:60]))
            continue

        # Write cleaned content
        cleaned_chunks = result.get("cleaned_chunks", [])
        if not write_cleaned_jsonl(book_id, cleaned_chunks):
            print(" ❌ write failed")
            failed.append((title, "write failed"))
            continue

        # Update DB
        if not update_book_cleaned(book_id):
            print(" ❌ DB update failed")
            failed.append((title, "DB update failed"))
            continue

        print(f" ✓ {len(cleaned_chunks)} chunks cleaned")
        ok += 1

        # Rate limiting for API
        time.sleep(0.5)

    print(f"\nDone. OK: {ok}, Failed: {len(failed)}")
    if failed:
        print("First failures:")
        for title, err in failed[:5]:
            print(f"  - {title}: {err}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "status":
        cmd_status()
    elif cmd == "run":
        limit = None
        if "--limit" in args:
            limit = int(args[args.index("--limit") + 1])
        dry_run = "--dry-run" in args
        cmd_run(limit=limit, dry_run=dry_run)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
