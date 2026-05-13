#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
backfill_pdf_headings.py — inject markdown headings into existing Plan B PDF chunks.

Background: standardize_pdf.py v0 wrote chapter chunks with format="text" and
content that started straight from the body (no `##` heading). The reader's
loadToc() in [server/utils/ebook-chunks.ts] derives sidebar nesting from the
first `#{1,4}` heading in content; without that, every chunk collapses to
level=2 (no indentation under volumes / parent chapters).

This script walks every already-chapter-chunked PDF's JSONL, prepends a
markdown heading derived from its chapter_path (1 part → `##`, 2 → `###`,
3+ → `####`), flips format to "markdown", and overwrites JSONL + R2 + DB
previews.

CRITICAL: page_number / page_range / chunk_index are NEVER touched. Only
content (heading prepended) and format change. Annotations referencing
chunk_index stay valid.

Usage:
  python scripts/backfill_pdf_headings.py status     # how many books are eligible
  python scripts/backfill_pdf_headings.py run --dry-run --limit 3
  python scripts/backfill_pdf_headings.py run --limit 5
  python scripts/backfill_pdf_headings.py run        # full sweep
  python scripts/backfill_pdf_headings.py run --book <ebook_id>
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
import standardize_ebook as se
import standardize_pdf_lite as pl
from standardize_pdf import _prepend_heading


def fetch_candidates(only_book: str | None = None) -> list[dict]:
    """Eligible = file_type=pdf, parsed_at not null. JSONL inspection decides
    whether it's actually chapter-chunked (eligible) or still per-page."""
    import requests
    if only_book:
        r = requests.get(
            f"{se.URL}/rest/v1/ebooks?id=eq.{only_book}&select=id,title",
            headers=se.H_GET, timeout=30)
        return r.json() or []
    out = []
    offset = 0
    while True:
        r = requests.get(
            f"{se.URL}/rest/v1/ebooks"
            f"?file_type=eq.pdf&parsed_at=not.is.null"
            f"&select=id,title&order=id&limit=1000&offset={offset}",
            headers=se.H_GET, timeout=60)
        page = r.json() or []
        if not page:
            break
        out.extend(page)
        if len(page) < 1000:
            break
        offset += 1000
    return out


def is_eligible(chunks: list[dict]) -> tuple[bool, str]:
    """A book is eligible for heading backfill iff:
      - it's chapter-chunked (at least one chunk has chunk_type='chapter' or page_range)
      - at least one chunk's content does NOT already start with `#…`
      - chapter_path is populated on most chunks (so we have something to inject)
    """
    if not chunks:
        return False, "empty"
    has_chapter_marker = any(
        c.get("chunk_type") == "chapter" or c.get("page_range")
        for c in chunks
    )
    if not has_chapter_marker:
        return False, "still per-page (Plan A only)"
    needs_heading = any(
        not (c.get("content") or "").lstrip().startswith("#")
        and (c.get("chapter_path") or "").strip()
        for c in chunks
    )
    if not needs_heading:
        return False, "already has headings"
    return True, "eligible"


def backfill_one(book: dict, dry_run: bool, no_r2: bool) -> tuple[int, str | None]:
    ebook_id = book["id"]
    jsonl_path = se.CHUNKS_DIR / f"{ebook_id}.jsonl"
    if not jsonl_path.exists():
        return 0, "JSONL missing"
    try:
        chunks = pl._read_jsonl_robust(jsonl_path)
    except Exception as e:
        return 0, f"JSONL read failed: {str(e)[:120]}"
    if not chunks:
        return 0, "JSONL empty"

    ok, reason = is_eligible(chunks)
    if not ok:
        return 0, f"skipped: {reason}"

    # Transform: prepend heading + flip format
    modified = 0
    for c in chunks:
        cp = c.get("chapter_path")
        if not cp:
            # Leave format alone (might be a header/footer page with no chapter)
            if c.get("format") in (None, "text"):
                c["format"] = "markdown"
            continue
        before = c.get("content") or ""
        after = _prepend_heading(before, cp)
        if after != before:
            c["content"] = after
            modified += 1
        c["format"] = "markdown"

    if modified == 0:
        return 0, "no chunks modified (all already had headings)"

    if dry_run:
        return modified, None

    # Persist: JSONL → R2 → DB previews
    import requests
    tmp = jsonl_path.with_suffix(".jsonl.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    tmp.replace(jsonl_path)

    if not no_r2:
        try:
            pl.push_to_r2(ebook_id, jsonl_path)
        except Exception as e:
            return modified, f"R2 push failed (JSONL persisted): {str(e)[:120]}"

    # Refresh ebook_chunks previews — preview text changes (heading is now in
    # content[:200]) so the DB row must catch up.
    def _clean(v):
        return v.replace("\x00", "") if isinstance(v, str) else v
    requests.delete(f"{se.URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebook_id}",
                    headers=se.H_GET, timeout=30)
    rows = [{
        "ebook_id": ebook_id,
        "chunk_index": c.get("chunk_index", i),
        "chunk_type": c.get("chunk_type") or "chapter",
        "page_number": c.get("page_number"),
        "chapter_path": _clean(c.get("chapter_path")),
        "content": _clean(c.get("content") or "")[:se.PREVIEW_LEN],
        "char_count": len(_clean(c.get("content") or "")),
    } for i, c in enumerate(chunks)]
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
            text = r.text[:300]
            if "57014" in text or "timeout" in text.lower() or r.status_code >= 500:
                if bs > BATCH_SIZES[-1]:
                    continue
            return modified, f"DB preview insert failed: {r.status_code} {text[:120]}"
        else:
            return modified, f"DB preview insert failed at batch_size=1, row {i}"

    # Touch parsed_at so a future audit can tell when the backfill ran
    requests.patch(
        f"{se.URL}/rest/v1/ebooks?id=eq.{ebook_id}",
        headers=se.H_JSON,
        json={"parsed_at": datetime.utcnow().isoformat() + "Z"},
        timeout=30)
    return modified, None


def cmd_status():
    books = fetch_candidates()
    print(f"PDFs scanned: {len(books)}")
    elig = skip_pera = skip_done = 0
    for b in books:
        jsonl_path = se.CHUNKS_DIR / f"{b['id']}.jsonl"
        if not jsonl_path.exists():
            continue
        try:
            chunks = pl._read_jsonl_robust(jsonl_path)
        except Exception:
            continue
        ok, reason = is_eligible(chunks)
        if ok:
            elig += 1
        elif "per-page" in reason:
            skip_pera += 1
        elif "already" in reason:
            skip_done += 1
    print(f"  eligible for backfill: {elig}")
    print(f"  skipped (Plan A only): {skip_pera}")
    print(f"  skipped (already has headings): {skip_done}")


def cmd_run(only_book: str | None, limit: int | None, dry_run: bool, no_r2: bool):
    books = fetch_candidates(only_book)
    print(f"Scanning {len(books)} books...")
    if limit:
        books = books[:limit]
    t0 = time.time()
    ok = skipped = failed = 0
    for i, b in enumerate(books, 1):
        title = (b.get("title") or "")[:40]
        n, err = backfill_one(b, dry_run=dry_run, no_r2=no_r2)
        if err and err.startswith("skipped:"):
            skipped += 1
            continue
        if err:
            failed += 1
            print(f"  [{i:4d}/{len(books)}] ⚠ {title}: {err[:80]}", flush=True)
        elif n:
            ok += 1
            tag = "(dry)" if dry_run else ""
            print(f"  [{i:4d}/{len(books)}] ✓ {title}: {n} chunks {tag}", flush=True)
    print(f"\nDone in {time.time() - t0:.0f}s. OK: {ok}, Skipped: {skipped}, Failed: {failed}")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("status")
    pr = sub.add_parser("run")
    pr.add_argument("--book")
    pr.add_argument("--limit", type=int)
    pr.add_argument("--dry-run", action="store_true")
    pr.add_argument("--no-r2", action="store_true")
    args = p.parse_args()
    if args.cmd == "status":
        cmd_status()
    elif args.cmd == "run":
        cmd_run(args.book, args.limit, args.dry_run, args.no_r2)
    else:
        p.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
