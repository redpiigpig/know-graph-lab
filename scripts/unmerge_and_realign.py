"""SURGICAL RECOVERY for a book whose consolidate step bled content
across letters (Vol 1 case: chunk labeled「依納爵致非拉鐵非人書 第1-10章」
actually contains Phila ch 7-11 + Smy ch 1-5).

Strategy
--------
1. Read the CURRENT consolidated JSONL (112 letter pages).
2. Split each chunk's content + source_text by `### / ####` markers into
   per-heading sub-pieces. Pair zh+en pieces by index within a chunk.
3. Walk the EPUB in document order (same skip rule as translator) to get
   the ordered list of src_file paths — this is the AUTHORITATIVE order
   per-chapter chunks SHOULD be in.
4. Positional alignment: piece[i] ↔ src_file[i].
5. Emit a fresh per-chapter JSONL (918 chunks) with each chunk tagged
   with its title_en (from heading).
6. After this, run polish + extract_epub_extras + consolidate_by_ncx
   (with the word-boundary chinese_label fix) to re-build clean letter
   pages.

Usage:
    python scripts/unmerge_and_realign.py <ebook_id>
    python scripts/unmerge_and_realign.py <ebook_id> --dry-run
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import ebooklib
from ebooklib import epub

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "scripts"))
import standardize_ebook as se

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR")
                  or r"G:\我的雲端硬碟\資料\電子書\_chunks")


def fetch_book(ebook_id: str) -> dict:
    r = requests.get(f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}&select=*",
                     headers=H_GET, timeout=30)
    r.raise_for_status()
    return r.json()[0]


def find_epub(book: dict) -> Path:
    src = Path(book["file_path"])
    if src.suffix.lower() == ".epub":
        return src
    epub_p = src.with_suffix(".epub")
    if epub_p.exists():
        return epub_p
    for f in src.parent.iterdir():
        if f.suffix.lower() == ".epub":
            return f
    sys.exit(f"no EPUB for {src}")


def walk_epub_items(epub_path: Path) -> list[tuple[str, str]]:
    """Return ordered list of (src_file, first_heading_text) for each
    ITEM_DOCUMENT that passed translate_ebook_to_zh's filters
    (non-empty markdown, len >= 30 chars)."""
    book = epub.read_epub(str(epub_path))
    out = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), "lxml")
        md_parts: list[str] = []
        first_heading = ""
        for el in soup.find_all(["h1", "h2", "h3", "h4", "p", "blockquote", "li"]):
            text = el.get_text(separator=" ", strip=True)
            if not text:
                continue
            tag = el.name
            if tag == "h1":
                md_parts.append(f"## {text}")
                if not first_heading: first_heading = text
            elif tag == "h2":
                md_parts.append(f"### {text}")
                if not first_heading: first_heading = text
            elif tag in ("h3", "h4"):
                md_parts.append(f"#### {text}")
                if not first_heading: first_heading = text
            elif tag == "blockquote":
                md_parts.append(f"> {text}")
            elif tag == "li":
                md_parts.append(f"- {text}")
            else:
                md_parts.append(text)
        content = "\n\n".join(md_parts).strip()
        if not content or len(content) < 30:
            continue
        out.append((item.get_name(), first_heading.split("\n", 1)[0].strip()))
    return out


def split_by_headings(text: str) -> list[tuple[str, str]]:
    """Split a chunk's content/source_text into (heading, body) pairs.
    Each piece starts at a `^### / ####` line. Anything before the first
    heading is appended to the heading-less prelude piece (empty heading).
    """
    if not text:
        return []
    # Find all heading boundaries
    boundaries = list(re.finditer(r"^(#{2,4})\s+(.+?)$", text, re.M))
    if not boundaries:
        return [("", text)]
    pieces: list[tuple[str, str]] = []
    # Prelude before first heading
    if boundaries[0].start() > 0:
        prelude = text[: boundaries[0].start()].strip()
        if prelude:
            pieces.append(("", prelude))
    for i, m in enumerate(boundaries):
        heading = m.group(2).strip()
        start = m.start()
        end = boundaries[i + 1].start() if i + 1 < len(boundaries) else len(text)
        body = text[start:end].strip()
        pieces.append((heading, body))
    return pieces


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ebook_id")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    ebook_id = args.ebook_id

    book = fetch_book(ebook_id)
    epub_path = find_epub(book)
    print(f"Book: {book['title']}")
    print(f"EPUB: {epub_path}")

    jsonl_path = CHUNKS_DIR / f"{ebook_id}.jsonl"
    chunks = [json.loads(l) for l in jsonl_path.read_text(encoding="utf-8").splitlines() if l]
    print(f"Current consolidated chunks: {len(chunks)}")

    # Step 1: split every chunk into per-heading sub-pieces, in chunk_index order
    zh_pieces: list[tuple[str, str]] = []  # (heading, body)
    en_pieces: list[tuple[str, str]] = []
    # Carry footnotes/page_numbers from the parent consolidated chunk; assign
    # ALL of them to the FIRST sub-piece (rough but workable — proper
    # per-chapter footnote distribution would need re-running extras)
    sub_chunk_seed: list[dict] = []  # parallel metadata for each piece
    for c in chunks:
        zh = c.get("content", "") or ""
        en = c.get("source_text", "") or ""
        zhs = split_by_headings(zh)
        ens = split_by_headings(en)
        # Pair by index; pad shorter side
        n = max(len(zhs), len(ens))
        for i in range(n):
            zh_pieces.append(zhs[i] if i < len(zhs) else ("", ""))
            en_pieces.append(ens[i] if i < len(ens) else ("", ""))
            sub_chunk_seed.append({
                "from_chunk": c["chunk_index"],
                "sub_idx": i,
            })

    print(f"Split into {len(zh_pieces)} zh pieces, {len(en_pieces)} en pieces")

    # Step 2: walk EPUB to get the ordered src_files
    src_order = walk_epub_items(epub_path)
    print(f"EPUB items (filtered, ordered): {len(src_order)}")

    # Step 3: positional alignment
    if len(zh_pieces) != len(src_order):
        print(f"⚠ Piece count {len(zh_pieces)} != EPUB items {len(src_order)} "
              f"(diff {len(zh_pieces) - len(src_order):+d})")
        print(f"  Will align by index up to min({len(zh_pieces)}, {len(src_order)})")

    new_chunks: list[dict] = []
    n_aligned = min(len(zh_pieces), len(src_order))
    for i in range(n_aligned):
        zh_h, zh_b = zh_pieces[i]
        en_h, en_b = en_pieces[i]
        src_file, epub_heading = src_order[i]
        # Prefer EPUB heading (canonical) as title_en; fall back to en piece heading
        title_en = epub_heading or en_h or f"piece-{i}"
        chapter_path = zh_h or title_en
        new_chunks.append({
            "chunk_index": i,
            "chunk_type": "chapter",
            "page_number": None,
            "chapter_path": chapter_path,
            "format": "markdown",
            "source_lang": "en",
            "title_en": title_en,
            "src_file": src_file,
            "source_text": en_b,
            "content": zh_b,
        })

    print(f"Rebuilt: {len(new_chunks)} per-chapter chunks")

    if args.dry_run:
        # Show a few samples to verify alignment
        for i in (0, 5, 50, 100, 300):
            if i < len(new_chunks):
                c = new_chunks[i]
                print(f"\n  [{i}] src_file={c['src_file']}")
                print(f"      title_en='{c['title_en']}'")
                print(f"      chapter_path='{c['chapter_path']}'")
                print(f"      content head: {c['content'][:80]}")
        return

    # Write fresh JSONL
    jsonl_path.write_text(
        "\n".join(json.dumps(c, ensure_ascii=False) for c in new_chunks) + "\n",
        encoding="utf-8"
    )
    print(f"\n✓ Wrote {jsonl_path} ({jsonl_path.stat().st_size // 1024} KB)")

    # Push R2 + update DB
    try:
        se.push_to_r2(ebook_id, jsonl_path)
        print(f"✓ R2 pushed")
    except Exception as e:
        print(f"⚠ R2 push: {e}")

    # Update DB chunk_count
    H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}
    requests.patch(f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}", headers=H_JSON,
                   json={"chunk_count": len(new_chunks),
                         "total_chars": sum(len(c["content"]) for c in new_chunks)},
                   timeout=30)
    print(f"✓ DB chunk_count updated to {len(new_chunks)}")


if __name__ == "__main__":
    main()
