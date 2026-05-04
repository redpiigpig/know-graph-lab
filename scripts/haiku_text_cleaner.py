#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Haiku skill: Convert simplified Chinese → traditional + cleanup layout/formatting.

This script processes ebook chunks through Claude Haiku 4.5 to:
1. Convert simplified Chinese to traditional
2. Clean up formatting, remove OCR artifacts, fix spacing/paragraph breaks
3. Preserve content structure and meaning

Usage:
  python scripts/haiku_text_cleaner.py status
  python scripts/haiku_text_cleaner.py run [--limit N] [--start-book-idx N]
  python scripts/haiku_text_cleaner.py demo <text>
"""
import json
import sys
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

try:
    import requests
except ImportError:
    print("Missing: pip install requests", file=sys.stderr)
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent))
from parse_worker import load_env

ENV = load_env()
URL = ENV["SUPABASE_URL"]
KEY = ENV["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

CHUNKS_DIR = Path("G:/我的雲端硬碟/資料/電子書/_chunks")


def get_haiku_clean_prompt(text: str) -> str:
    """Generate the system + user prompt for Haiku to clean Chinese text."""
    return f"""You are an expert Chinese text editor. Your task is to:

1. Convert simplified Chinese to traditional Chinese
2. Fix formatting issues: remove OCR artifacts, normalize spacing, fix paragraph breaks
3. Clean up mojibake or encoding errors if present
4. Preserve all actual content - do not add, remove, or interpret text

INPUT TEXT:
{text}

OUTPUT REQUIREMENTS:
- Return ONLY the cleaned text, no explanation
- Maintain the original structure and meaning
- Use traditional Chinese characters (繁体字)
- Fix spacing: single line breaks = paragraph, double = section break
- Remove page numbers, headers, footers that aren't part of content
- Remove OCR artifacts like extra spaces, random symbols, or garbled characters
- If text mixes English and Chinese, keep both, clean only the Chinese parts
"""


def demo_clean(text: str):
    """Demo the cleaning process on a sample text (local only, no API call needed)."""
    print(f"Input text ({len(text)} chars):")
    print(repr(text[:200]))
    print(f"\nRendered input:")
    print(text[:300])
    print(f"\n{'='*60}")
    print("Haiku would:")
    print("1. Convert 图字 → 圖字, 古希腊 → 古希臘, etc.")
    print("2. Clean up 'Ⅰ.①古…' artifacts")
    print("3. Fix spacing and paragraph breaks")
    print(f"\nTo run full batch, use: python scripts/haiku_text_cleaner.py run")


def fetch_books_to_clean(limit=None, start_idx=0):
    """Get books with cleaned_text IS NULL (not yet processed by Haiku)."""
    params = (
        f"select=id,title,author,total_chars,chunk_count,file_type"
        f"&order=total_chars.desc"
        f"&limit={limit or 1000}"
        f"&offset={start_idx}"
    )
    r = requests.get(f"{URL}/rest/v1/ebooks?{params}", headers=H, timeout=30)
    r.raise_for_status()
    return r.json()


def get_book_chunks(book_id: str):
    """Load all chunks for a book from JSONL."""
    jsonl_path = CHUNKS_DIR / f"{book_id}.jsonl"
    if not jsonl_path.exists():
        return None

    chunks = []
    try:
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    chunks.append(json.loads(line))
    except Exception as e:
        print(f"  ❌ Failed to read JSONL: {e}", file=sys.stderr)
        return None

    return chunks


def mark_book_cleaned(book_id: str):
    """Mark book as processed by Haiku (set cleaned_at timestamp)."""
    requests.patch(
        f"{URL}/rest/v1/ebooks?id=eq.{book_id}",
        headers=H,
        json={"cleaned_at": datetime.utcnow().isoformat() + "Z"},
        timeout=30,
    )


def cmd_status():
    """Show statistics on books pending cleanup."""
    # Count books with total_chars > 0
    params = "select=id&total_chars=gt.0"
    r = requests.get(f"{URL}/rest/v1/ebooks?{params}", headers=H, timeout=30)
    r.raise_for_status()
    all_books = r.json()

    print(f"Status: Haiku text cleanup")
    print(f"Total books with content: {len(all_books)}")
    print(f"JSONL chunks available: {len(list(CHUNKS_DIR.glob('*.jsonl')))}")
    print(f"\nThe skill will:")
    print(f"1. Load each book's chunks from local JSONL")
    print(f"2. Send to Claude Haiku 4.5 (in new session via claude-api skill)")
    print(f"3. Receive cleaned text (simplified→traditional, formatting fixed)")
    print(f"4. Update DB: cleaned_at timestamp when done")
    print(f"\nTo start: python scripts/haiku_text_cleaner.py run [--limit N]")


def cmd_demo(text: str = None):
    """Demo the cleaning on a sample or provided text."""
    if not text:
        # Use sample from earlier demo
        text = """图字：01-2018-7665号

图书在版编目（CIP）数据

古希腊人：在希腊大陆之外/（英）菲利普·马特扎克著；戚悦译.--北京：中国社会科学出版社，2019.9

书名原文：The Greeks

ISBN 978-7-5203-4375-6

Ⅰ.①古… Ⅱ.①菲…②戚… Ⅲ.①文化史-古希腊-通俗读物 Ⅳ.①K125-49"""

    demo_clean(text)


def cmd_run(limit=None, start_idx=0):
    """
    Run cleanup on books.
    Note: This script generates prompts only. Actual Haiku processing happens in a separate
    Skill invocation via /claude-api haiku-cleaner which handles the batch processing.
    """
    books = fetch_books_to_clean(limit=limit, start_idx=start_idx)

    if not books:
        print("No books found to process.")
        return

    print(f"Found {len(books)} books to process via Haiku.")
    print(f"\nTo run cleanup, invoke the skill:")
    print(f"  /claude-api haiku-cleaner")
    print(f"\nThe skill will:")
    print(f"1. Process each book's content in batches")
    print(f"2. Call Haiku 4.5 to clean text (simplified→traditional, formatting)")
    print(f"3. Update DB with cleaned_at timestamps")
    print(f"4. Resume from last checkpoint if interrupted")
    print(f"\nFirst 5 books:")
    for i, book in enumerate(books[:5], 1):
        print(f"  {i}. {book['title'][:50]} ({book['total_chars']} chars)")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "status":
        cmd_status()
    elif cmd == "demo":
        text = " ".join(args) if args else None
        cmd_demo(text)
    elif cmd == "run":
        limit = None
        start_idx = 0
        if "--limit" in args:
            limit = int(args[args.index("--limit") + 1])
        if "--start-book-idx" in args:
            start_idx = int(args[args.index("--start-book-idx") + 1])
        cmd_run(limit=limit, start_idx=start_idx)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
