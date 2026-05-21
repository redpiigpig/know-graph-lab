#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""resplit_giant_chunks_v2.py
v2: same as v1 plus inline-text patterns + recursive iteration.

Patterns tried in order (first match wins) per chunk:
  1. >= 2 distinct ^## h2 (markdown)
  2. >= 3 distinct ^### h3 (markdown)
  3. >= 3 ^Book [IVXLCDM]+.   (Schaff, classics)
  4. >= 3 ^Chapter \\d+.?      (modern English books)
  5. >= 3 ^Chapter [IVXLCDM]+.? (older English books)
  6. >= 3 Chinese 第N章/卷/編/冊/部/集/篇/節
  else -> leave alone.

Recursive: after split, any sub-chunk still > threshold is re-split using
the same logic, up to MAX_ITERATIONS depth. Handles cases like 劍橋中國史
where the first pass splits by 第N卷 but each volume is still > threshold
and needs an inner 第N章 split.

Skipped on purpose:
  - bracketed footnote refs [N] (over-split indexes / glossaries)
  - bare English Roman.  e.g. LXX. He   (too much body-text noise)
  - all inline patterns require line-start so they do not match
    mid-paragraph references

Annotation guard + R2 push + DB preview refresh identical to v1.

Usage (same shape as v1):
  python scripts/resplit_giant_chunks_v2.py status
  python scripts/resplit_giant_chunks_v2.py run --book <id>
  python scripts/resplit_giant_chunks_v2.py run --all --dry-run
  python scripts/resplit_giant_chunks_v2.py run --all
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
import standardize_ebook as se
import standardize_pdf_lite as pl
import resplit_giant_chunks as v1

import requests


GIANT_THRESHOLD = v1.GIANT_THRESHOLD
PREVIEW_LEN = v1.PREVIEW_LEN


# v1 patterns (markdown headings)
_H2_RX = v1._H2_RX
_H3_RX = v1._H3_RX

# v2: inline-text section markers. All line-anchored (multiline mode).
_BOOK_ROMAN_RX = re.compile(r"(?m)^Book\s+[IVXLCDM]+\.")
_CHAPTER_ARABIC_RX = re.compile(r"(?m)^Chapter\s+\d+\.?(?=\s|$)")
_CHAPTER_ROMAN_RX = re.compile(r"(?m)^Chapter\s+[IVXLCDM]+\.?(?=\s|$)")
# Chinese: 第 + numeric chars + section type marker, followed by space/CJK
_CHINESE_SECTION_RX = re.compile(
    r"(?m)^第[一二三四五六七八九十百千零〇兩两0-9]+(?:章|卷|編|编|冊|册|部|集|篇|節|节)(?=\s|[一-鿿])"
)

# Order matters — try strongest signals first
INLINE_PATTERNS = [
    ("book_roman",     _BOOK_ROMAN_RX,     3),
    ("chapter_arabic", _CHAPTER_ARABIC_RX, 3),
    ("chapter_roman",  _CHAPTER_ROMAN_RX,  3),
    ("chinese_sec",    _CHINESE_SECTION_RX, 3),
]


def first_heading_text(seg: str) -> str | None:
    """Best chapter label from a sub-segment: markdown heading wins, else
    the first inline pattern match, else None."""
    m = re.search(r"(?m)^#{1,4}\s+(.+?)\s*$", seg)
    if m:
        return m.group(1).strip()
    # Try inline markers — capture the whole line up to ~60 chars
    for _, rx, _ in INLINE_PATTERNS:
        m = rx.search(seg)
        if m:
            # Grab the surrounding line (anchored at the match start)
            ls = seg.rfind("\n", 0, m.start()) + 1
            le = seg.find("\n", m.start())
            line = seg[ls:le if le != -1 else len(seg)].strip()
            return line[:80] if line else None
    return None


def resplit_chunk_v2(chunk: dict) -> tuple[list[dict] | None, str | None]:
    """Returns (sub_chunks, boundary_method_used).
    sub_chunks=None means not enough structure (skip)."""
    content = chunk.get("content") or ""
    if len(content) < GIANT_THRESHOLD:
        return None, None

    # 1) v1 markdown h2
    h2_offsets = [m.start() for m in _H2_RX.finditer(content)]
    if len(set(h2_offsets)) >= 2:
        offsets, level = h2_offsets, "md_h2"
    else:
        # 2) v1 markdown h3
        h3_offsets = [m.start() for m in _H3_RX.finditer(content)]
        if len(h3_offsets) >= 3:
            offsets, level = [0] + h3_offsets, "md_h3"
        else:
            offsets, level = None, None
            # 3-6) inline patterns
            for name, rx, min_hits in INLINE_PATTERNS:
                hits = [m.start() for m in rx.finditer(content)]
                if len(hits) >= min_hits:
                    # Always include 0 as a boundary so leading prose becomes
                    # its own chunk (it doesn't have a leading marker)
                    offsets = [0] + hits if 0 not in hits else hits
                    level = name
                    break
            if offsets is None:
                return None, None

    parts = v1.split_at_offsets(content, offsets)
    if len(parts) < 2:
        return None, None

    base_chapter = chunk.get("chapter_path") or ""
    new_chunks = []
    for i, (off, seg) in enumerate(parts):
        ht = first_heading_text(seg)
        if level in ("md_h3", "chinese_sec", "chapter_arabic", "chapter_roman", "book_roman") \
                and base_chapter and ht and i > 0:
            cp = f"{base_chapter} / {ht}"
        elif ht:
            cp = ht
        else:
            cp = base_chapter or None
        nc = dict(chunk)
        nc["chapter_path"] = (cp or "")[:500] or None
        nc["content"] = seg
        new_chunks.append(nc)
    return new_chunks, level


MAX_ITERATIONS = 4


def resplit_recursively(chunk: dict, method_stats: dict, depth: int = 0) -> list[dict]:
    """Apply resplit_chunk_v2 repeatedly until no sub-chunk is splittable or
    depth cap reached. Returns flat list of resulting chunks. Always returns
    at least the input chunk wrapped in a list."""
    sub, method = resplit_chunk_v2(chunk)
    if sub is None or depth >= MAX_ITERATIONS:
        return [chunk]
    method_stats[method] = method_stats.get(method, 0) + 1
    out = []
    for s in sub:
        if len(s.get("content") or "") > GIANT_THRESHOLD:
            out.extend(resplit_recursively(s, method_stats, depth + 1))
        else:
            out.append(s)
    return out


def process_book(book: dict, dry_run: bool = False) -> tuple[int, str | None, dict]:
    """Returns (chunks_added, err_or_None, method_stats).
    method_stats: {boundary_level: count_of_resplit_chunks}."""
    bid = book["id"]
    if v1.annotations_for(bid) > 0:
        return 0, "skipped: book has annotations", {}

    chunks = v1.load_chunks(bid)
    if not chunks:
        return 0, "skipped: JSONL missing", {}

    original_count = len(chunks)
    new_all = []
    method_stats: dict[str, int] = {}
    n_resplit = 0
    leftover_giants = 0
    for c in chunks:
        if len(c.get("content") or "") <= GIANT_THRESHOLD:
            new_all.append(c)
            continue
        result = resplit_recursively(c, method_stats)
        if len(result) == 1 and result[0] is c:
            # Genuinely couldn't split
            new_all.append(c)
            leftover_giants += 1
        else:
            new_all.extend(result)
            n_resplit += 1
            for s in result:
                if len(s.get("content") or "") > GIANT_THRESHOLD:
                    leftover_giants += 1
    if n_resplit == 0:
        return 0, "no chunks resplittable", {}

    new_all = v1.renumber(new_all)
    added = len(new_all) - original_count

    if dry_run:
        method_stats["_leftover_giants"] = leftover_giants
        return added, None, method_stats

    p = v1.write_jsonl(bid, new_all)
    try:
        v1.push_to_r2(bid, p)
    except Exception as e:
        return added, f"JSONL rewritten but R2 push failed: {str(e)[:120]}", method_stats
    try:
        v1.refresh_db(bid, new_all)
    except Exception as e:
        return added, f"R2 ok but DB refresh failed: {str(e)[:120]}", method_stats
    return added, None, method_stats


def cmd_status(threshold: int):
    books = v1.fetch_oversized_books(threshold)
    print(f"Books with at least one chunk > {threshold} chars: {len(books)}")
    skipped_annot = 0
    eligible = []
    for b in books:
        if v1.annotations_for(b["id"]) > 0:
            skipped_annot += 1
            continue
        eligible.append(b)
    print(f"  No annotations: {len(eligible)}  (v2 handles EPUB AND PDF)")
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
        books = v1.fetch_oversized_books(threshold)
        print(f"Found {len(books)} books with chunks > {threshold}")
    else:
        print("Specify --book <id> or --all", file=sys.stderr)
        sys.exit(2)

    ok = 0
    skipped = 0
    failed = 0
    total_added = 0
    method_totals: dict[str, int] = {}
    leftover_total = 0
    for b in books:
        title = (b.get("title") or "?")[:55]
        try:
            n, err, stats = process_book(b, dry_run=dry_run)
        except Exception as e:
            print(f"  ✗ [{title}] exception: {str(e)[:160]}")
            failed += 1
            continue
        if err and err.startswith("skipped"):
            print(f"  · [{title}] {err}")
            skipped += 1
        elif err and "no chunks resplittable" in err:
            print(f"  · [{title}] {err}  ({b['file_type']})")
            skipped += 1
        elif err:
            print(f"  ⚠ [{title}] {err}")
            failed += 1
        else:
            method_summary = ", ".join(
                f"{k}:{v}" for k, v in stats.items() if k != "_leftover_giants"
            )
            leftover = stats.get("_leftover_giants", 0)
            tail = f", leftover_giants={leftover}" if leftover else ""
            print(f"  ✓ [{title}] +{n} chunk(s)  [{method_summary}]{tail}")
            ok += 1
            total_added += n
            for k, v in stats.items():
                if k != "_leftover_giants":
                    method_totals[k] = method_totals.get(k, 0) + v
            leftover_total += stats.get("_leftover_giants", 0)

    print(f"\nDone. OK: {ok}, Skipped: {skipped}, Failed: {failed}, new chunks: +{total_added}"
          f"{' (dry-run)' if dry_run else ''}")
    if method_totals:
        print(f"  Boundary methods used: {method_totals}")
    if leftover_total:
        print(f"  Sub-chunks STILL > {threshold}: {leftover_total} (need iteration / further work)")


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
