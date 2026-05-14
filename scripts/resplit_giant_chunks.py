#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
resplit_giant_chunks.py — break oversized chunks (>400K chars) by their
internal markdown headings (## / ###), so the reader stops choking on
1-chunk-per-book monstrosities.

Some publisher EPUBs collapse the entire book into one HTML doc with
weak <h*> nesting that ebooklib treats as a single chapter. After
standardize_ebook produces `## chapter` + `### section` markdown,
the giant chunk's text now contains its OWN internal heading structure.
This script re-splits a chunk at those internal headings:

  Strategy (per giant chunk):
    1. Count internal `^## ` h2 headings (excluding the chunk's own leading
       heading if it's at offset 0).
       - ≥ 2 distinct h2 → split at h2 boundaries.
    2. Otherwise, count internal `^### ` h3 headings.
       - ≥ 3 distinct h3 → split at h3 boundaries.
    3. Otherwise → leave alone (no usable boundaries; needs LLM/font work).

After resplit:
  - JSONL rewritten with renumbered chunk_index (0..N-1)
  - R2 pushed
  - ebook_chunks DB previews refreshed
  - ebooks.chunk_count + total_chars updated

Annotation guard: refuses to resplit any book that has rows in `annotations`
(would shift chunk_index away from saved positions).

Usage:
  python scripts/resplit_giant_chunks.py status                  # what would be processed
  python scripts/resplit_giant_chunks.py run --book <id>         # one book
  python scripts/resplit_giant_chunks.py run --book <id> --dry-run
  python scripts/resplit_giant_chunks.py run --all               # all eligible
  python scripts/resplit_giant_chunks.py run --all --threshold 400000   # custom char threshold
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
import standardize_ebook as se
import standardize_pdf_lite as pl

import requests


GIANT_THRESHOLD = 400_000  # chars
PREVIEW_LEN = 200


def fetch_oversized_books(threshold: int = GIANT_THRESHOLD) -> list[dict]:
    """List books that have at least one chunk >= threshold."""
    # Postgres can't easily express "any chunk > N" without join; use REST.
    # Fetch oversized chunks first.
    chunks = []
    offset = 0
    while True:
        r = requests.get(
            f"{se.URL}/rest/v1/ebook_chunks?select=ebook_id,char_count"
            f"&char_count=gt.{threshold}&order=ebook_id&limit=1000&offset={offset}",
            headers=se.H_GET, timeout=60)
        page = r.json() or []
        if not page:
            break
        chunks.extend(page)
        if len(page) < 1000:
            break
        offset += 1000
    ids = sorted(set(c["ebook_id"] for c in chunks))
    if not ids:
        return []
    out = []
    for i in range(0, len(ids), 50):
        batch = ids[i:i + 50]
        in_clause = ",".join(f'"{x}"' for x in batch)
        r = requests.get(
            f"{se.URL}/rest/v1/ebooks?id=in.({in_clause})"
            "&select=id,title,author,file_type,chunk_count,total_chars,parse_error",
            headers=se.H_GET, timeout=60)
        out.extend(r.json() or [])
    return out


def load_chunks(ebook_id: str) -> list[dict] | None:
    p = se.CHUNKS_DIR / f"{ebook_id}.jsonl"
    if not p.exists():
        return None
    try:
        return pl._read_jsonl_robust(p)
    except Exception:
        return None


def annotations_for(ebook_id: str) -> int:
    r = requests.get(
        f"{se.URL}/rest/v1/annotations?ebook_id=eq.{ebook_id}&select=id&limit=1",
        headers={**se.H_GET, "Prefer": "count=exact", "Range": "0-0", "Range-Unit": "items"},
        timeout=20)
    cr = r.headers.get("Content-Range", "0/0")
    try:
        return int(cr.split("/")[-1])
    except ValueError:
        return 0


# Markdown heading regex — anchored to line start in multiline mode.
_H2_RX = re.compile(r"(?m)^##\s+(.+?)\s*$")
_H3_RX = re.compile(r"(?m)^###\s+(.+?)\s*$")


def split_at_offsets(content: str, offsets: list[int]) -> list[tuple[int, str]]:
    """Return [(start_offset, sub_content)] for each segment. Offsets must
    include 0 if you want a leading segment before the first explicit boundary.
    Returns empty list when offsets is empty."""
    if not offsets:
        return []
    boundaries = sorted(set(offsets))
    parts = []
    for i, off in enumerate(boundaries):
        end = boundaries[i + 1] if i + 1 < len(boundaries) else len(content)
        seg = content[off:end].rstrip()
        if seg.strip():
            parts.append((off, seg))
    return parts


def first_heading_text(seg: str) -> str | None:
    m = re.search(r"(?m)^#{1,4}\s+(.+?)\s*$", seg)
    return m.group(1).strip() if m else None


def resplit_chunk(chunk: dict) -> list[dict] | None:
    """If chunk can be split by internal headings, return new sub-chunks.
    Else return None (leave caller to keep the chunk as-is)."""
    content = chunk.get("content") or ""
    if len(content) < GIANT_THRESHOLD:
        return None

    # Try h2 first
    h2_offsets = [m.start() for m in _H2_RX.finditer(content)]
    # Filter to internal h2s (excluding the leading one at offset 0 if it
    # matches the chunk's chapter_path — that's the chunk's own header).
    internal_h2 = [o for o in h2_offsets if o > 0]
    distinct_h2 = len(set(h2_offsets))

    if distinct_h2 >= 2:
        # Use ALL h2 offsets including 0 (so leading h2 becomes first sub-chunk)
        offsets = h2_offsets
        boundary_level = "h2"
    else:
        h3_offsets = [m.start() for m in _H3_RX.finditer(content)]
        if len(h3_offsets) >= 3:
            # Use h3 offsets + 0 (so any text before first h3 becomes a chunk)
            offsets = [0] + h3_offsets
            boundary_level = "h3"
        else:
            return None  # not enough structure

    parts = split_at_offsets(content, offsets)
    if len(parts) < 2:
        return None

    base_chapter = chunk.get("chapter_path") or ""
    new_chunks = []
    for i, (off, seg) in enumerate(parts):
        ht = first_heading_text(seg)
        # chapter_path: prepend the parent chapter if h3-split (since h3 are
        # sub-sections OF the chunk's own chapter).
        if boundary_level == "h3" and base_chapter and ht:
            cp = f"{base_chapter} / {ht}"
        elif ht:
            cp = ht
        else:
            cp = base_chapter or None
        nc = dict(chunk)
        nc["chapter_path"] = (cp or "")[:500] or None
        nc["content"] = seg
        # chunk_index will be renumbered later
        new_chunks.append(nc)
    return new_chunks


def renumber(all_chunks: list[dict]) -> list[dict]:
    for i, c in enumerate(all_chunks):
        c["chunk_index"] = i
    return all_chunks


def push_to_r2(ebook_id: str, jsonl_path: Path) -> None:
    pl.push_to_r2(ebook_id, jsonl_path)


def write_jsonl(ebook_id: str, chunks: list[dict]) -> Path:
    p = se.CHUNKS_DIR / f"{ebook_id}.jsonl"
    with p.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    return p


def refresh_db(ebook_id: str, chunks: list[dict]) -> None:
    """Delete old chunk previews + insert new ones + update ebooks counts."""
    # Delete old previews
    requests.delete(f"{se.URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebook_id}",
                    headers=se.H_GET, timeout=30)
    # Insert new previews (preview-only — full content stays in JSONL/R2)
    rows = [{
        "ebook_id": ebook_id,
        "chunk_index": c["chunk_index"],
        "chunk_type": c.get("chunk_type") or "chapter",
        "page_number": c.get("page_number"),
        "chapter_path": (c.get("chapter_path") or "").replace("\x00", "") or None,
        "content": (c.get("content") or "").replace("\x00", "")[:PREVIEW_LEN],
        "char_count": len((c.get("content") or "").replace("\x00", "")),
    } for c in chunks]
    BATCH_SIZES = [50, 20, 5, 1]
    i = 0
    while i < len(rows):
        for bs in BATCH_SIZES:
            batch = rows[i:i + bs]
            r = requests.post(f"{se.URL}/rest/v1/ebook_chunks",
                              headers=se.H_JSON, json=batch, timeout=120)
            if r.status_code in (200, 201):
                i += len(batch)
                break
            text = r.text[:200]
            if "57014" in text or "timeout" in text.lower() or r.status_code >= 500:
                if bs > BATCH_SIZES[-1]:
                    continue
            raise RuntimeError(f"preview insert failed: {r.status_code} {text[:120]}")
        else:
            raise RuntimeError(f"preview insert failed at batch_size=1, row {i}")

    # Update ebook row counts
    total_chars = sum(len(c.get("content") or "") for c in chunks)
    requests.patch(f"{se.URL}/rest/v1/ebooks?id=eq.{ebook_id}",
                   headers=se.H_JSON,
                   json={"chunk_count": len(chunks), "total_chars": total_chars},
                   timeout=30)


def process_book(book: dict, dry_run: bool = False) -> tuple[int, str | None]:
    """Returns (chunks_added, error_or_None). chunks_added counts NEW
    sub-chunks (i.e. how much the chunk_count grew)."""
    bid = book["id"]
    title = book.get("title") or "?"
    if book.get("file_type") != "epub":
        return 0, "skipped: not EPUB (PDFs handled by standardize_pdf.py)"
    if annotations_for(bid) > 0:
        return 0, f"skipped: book has annotations"

    chunks = load_chunks(bid)
    if not chunks:
        return 0, "skipped: JSONL missing"

    original_count = len(chunks)
    new_all = []
    n_resplit = 0
    for c in chunks:
        sub = resplit_chunk(c)
        if sub is None:
            new_all.append(c)
        else:
            new_all.extend(sub)
            n_resplit += 1
    if n_resplit == 0:
        return 0, "no chunks resplittable (no usable internal headings)"

    new_all = renumber(new_all)
    added = len(new_all) - original_count

    if dry_run:
        print(f"    Would resplit {n_resplit} chunk(s): {original_count} → {len(new_all)} chunks")
        # Show new chunk sizes for spot-check
        large_after = [c for c in new_all if len(c.get("content") or "") > GIANT_THRESHOLD]
        print(f"    After resplit: {len(large_after)} chunks still > {GIANT_THRESHOLD//1000}K")
        return added, None

    p = write_jsonl(bid, new_all)
    try:
        push_to_r2(bid, p)
    except Exception as e:
        return added, f"JSONL rewritten but R2 push failed: {str(e)[:120]}"
    try:
        refresh_db(bid, new_all)
    except Exception as e:
        return added, f"R2 ok but DB refresh failed: {str(e)[:120]}"
    return added, None


def cmd_status(threshold: int):
    books = fetch_oversized_books(threshold)
    print(f"Books with at least one chunk > {threshold} chars: {len(books)}")
    skipped_annot = 0
    eligible = []
    for b in books:
        if b.get("file_type") != "epub":
            continue
        if annotations_for(b["id"]) > 0:
            skipped_annot += 1
            continue
        eligible.append(b)
    print(f"  EPUB + no annotations: {len(eligible)}")
    if skipped_annot:
        print(f"  Skipped due to annotations: {skipped_annot}")


def cmd_run(book_id: str | None, do_all: bool, dry_run: bool, threshold: int):
    if book_id:
        r = requests.get(
            f"{se.URL}/rest/v1/ebooks?id=eq.{book_id}"
            "&select=id,title,author,file_type,chunk_count,total_chars,parse_error",
            headers=se.H_GET, timeout=30).json()
        if not r:
            print(f"⚠ ebook {book_id} not found", file=sys.stderr)
            sys.exit(1)
        books = r
    elif do_all:
        books = fetch_oversized_books(threshold)
        print(f"Found {len(books)} books with chunks > {threshold}")
    else:
        print("Specify --book <id> or --all", file=sys.stderr)
        sys.exit(2)

    ok = 0
    skipped = 0
    failed = 0
    total_added = 0
    for b in books:
        print(f"\n[{b['title'][:55]}]  id={b['id']}")
        try:
            n, err = process_book(b, dry_run=dry_run)
        except Exception as e:
            print(f"  ✗ exception: {str(e)[:200]}")
            failed += 1
            continue
        if err and err.startswith("skipped"):
            print(f"  · {err}")
            skipped += 1
        elif err and "no chunks resplittable" in err:
            print(f"  · {err}")
            skipped += 1
        elif err:
            print(f"  ⚠ {err}")
            failed += 1
        else:
            print(f"  ✓ added {n} new chunk(s)")
            ok += 1
            total_added += n

    print(f"\nDone. OK: {ok}, Skipped: {skipped}, Failed: {failed}, new chunks: +{total_added}"
          f"{' (dry-run)' if dry_run else ''}")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    ps = sub.add_parser("status")
    ps.add_argument("--threshold", type=int, default=GIANT_THRESHOLD)
    pr = sub.add_parser("run")
    pr.add_argument("--book")
    pr.add_argument("--all", action="store_true")
    pr.add_argument("--dry-run", action="store_true")
    pr.add_argument("--threshold", type=int, default=GIANT_THRESHOLD)
    args = p.parse_args()
    if args.cmd == "status":
        cmd_status(args.threshold)
    elif args.cmd == "run":
        cmd_run(args.book, args.all, args.dry_run, args.threshold)
    else:
        p.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
