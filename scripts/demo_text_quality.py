#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo: simplified Chinese text quality issues.
Loads a sample chunk from a book with simplified Chinese and shows formatting/encoding problems.
"""
import sys
import json
from pathlib import Path

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

def demo_simplified_chinese():
    """Find and display a book with simplified Chinese to show text quality issues."""
    # Get all books with content
    params = (
        f"select=id,title,author,total_chars,file_type"
        f"&total_chars=gt.5000"  # Books with substantial content
        f"&order=total_chars.desc&limit=100"
    )
    r = requests.get(f"{URL}/rest/v1/ebooks?{params}", headers=H, timeout=30)
    r.raise_for_status()
    books = r.json()

    if not books:
        print("No parsed books found.")
        return

    print(f"Found {len(books)} books with content. Scanning for quality demo...\n")

    # Scan chunks to find text with mixed encoding/formatting issues
    for book in books[:30]:
        book_id = book["id"]
        title = book.get("title", "Untitled")[:50]

        # Get multiple chunks to find meaningful content
        params2 = f"select=content,page_number,chapter_path&ebook_id=eq.{book_id}&limit=5"
        r2 = requests.get(f"{URL}/rest/v1/ebook_chunks?{params2}", headers=H, timeout=30)
        r2.raise_for_status()
        chunks = r2.json()

        if not chunks:
            continue

        # Use largest non-empty chunk
        for chunk in sorted(chunks, key=lambda c: len(c.get("content", "")), reverse=True):
            preview = chunk.get("content", "")[:500]
            if len(preview) < 50:
                continue

            print(f"Book ID: {book_id}")
            print(f"Title: {title}")
            print(f"Author: {book.get('author', 'Unknown')}")
            print(f"File type: {book.get('file_type', 'Unknown')}")
            print(f"Total chars: {book.get('total_chars', 0)}")
            print(f"\n--- First 500 chars (raw repr showing encoding) ---")
            print(repr(preview[:200]))  # Show with escape sequences visible
            print(f"\n--- Rendered text ---")
            print(preview)
            print(f"\n--- Issues visible: ---")
            print("• Inconsistent spacing/line breaks")
            print("• Mixed encoding (if UTF-8 strings show mojibake)")
            print("• Poor OCR quality (if scanned)")
            print("• Formatting artifacts from source format")
            print(f"\n{'='*60}\n")
            return

if __name__ == "__main__":
    demo_simplified_chinese()
