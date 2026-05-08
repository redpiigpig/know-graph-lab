#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
standardize_pdf.py — Plan B PDF restandardize.

Re-chunks an already-parsed PDF (per-page JSONL produced by parse_worker
or standardize_pdf_lite) into chapter-level chunks driven by the PDF's
TOC bookmarks. Falls back to Plan A's per-page output (no rewrite) when:

  - PDF has no TOC, or fewer than 3 TOC entries
  - TOC is over-granular (more than ~50% of pages have a TOC entry —
    e.g. page-level TOCs that scan-houses sometimes generate)
  - The ebook has existing annotations (re-chunking would shift
    chunk_index and break references)

Per-chunk contract:

  chunk_type  = "chapter"
  chapter_path = TOC title (s2tw'd, deduped against parent path)
  page_number  = the chapter's FIRST real PDF page (sacred — citations
                 use this; never re-numbered to chunk_index+1)
  page_range   = [first_page, last_page]   ← new field

Front-matter pages BEFORE the first TOC entry are kept as a single
"前置內容" chunk so 版權頁 / 序言 still feed _extract_publisher_metadata.

Reuses everything else from standardize_pdf_lite + standardize_ebook
(s2tw, collapse_cjk_spacing, write_jsonl, push_to_r2, update_db,
publisher metadata extraction).

Usage — single book:
  python scripts/standardize_pdf.py <ebook_id>
  python scripts/standardize_pdf.py <ebook_id> --dry-run
  python scripts/standardize_pdf.py <ebook_id> --no-r2
  python scripts/standardize_pdf.py <ebook_id> --force        # ignore annotations guard

Usage — batch (auto-skips EPUBs and books without TOC):
  python scripts/standardize_pdf.py --category 哲學
  python scripts/standardize_pdf.py --all --dry-run
  python scripts/standardize_pdf.py --all
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

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Missing dependency. Run: pip install pymupdf", file=sys.stderr)
    sys.exit(1)


# ── thresholds ─────────────────────────────────────────────────
MIN_TOC_ENTRIES = 3            # below this, fall back to Plan A
MIN_PAGES_PER_ENTRY = 1.2      # below this, TOC is page-level junk (e.g. 中東史: 654 entries / 661 pages)
MAX_LEVEL = 2                  # level 0,1,2 chosen as chunk boundaries; deeper become inline headings


# ── annotations guard ───────────────────────────────────────────
def has_annotations(ebook_id: str) -> int:
    import requests
    r = requests.get(
        f"{se.URL}/rest/v1/annotations"
        f"?ebook_id=eq.{ebook_id}&select=id"
        f"&limit=1",
        headers={**se.H_GET, "Prefer": "count=exact", "Range": "0-0", "Range-Unit": "items"},
        timeout=20,
    )
    if not r.ok:
        return 0
    cr = r.headers.get("Content-Range", "0/0")
    try:
        return int(cr.split("/")[-1])
    except ValueError:
        return 0


# ── TOC processing ─────────────────────────────────────────────
def normalize_toc(toc, total_pages: int) -> list[dict] | None:
    """Return a flat list of {level, title, start_page} entries chosen as
    chunk boundaries, or None if the TOC isn't usable.

    Strategy:
      - keep entries with level <= MAX_LEVEL
      - drop empty / whitespace-only titles
      - clamp start_page into [1, total_pages]
      - if multiple entries share the same start_page, keep the topmost
        (lowest level) — others become inline headings inside that chunk
    """
    if not toc or len(toc) < MIN_TOC_ENTRIES:
        return None
    # Reject "page-level" TOCs (one bookmark per page) — they have no chapter
    # structure to extract. 中東史 has 654/661, 希伯來聖經 has 598/598.
    if total_pages > 0 and (total_pages / len(toc)) < MIN_PAGES_PER_ENTRY:
        return None

    entries = []
    for level, title, page in toc:
        title = (title or "").strip()
        if not title:
            continue
        if level > MAX_LEVEL:
            continue
        page = max(1, min(int(page or 1), total_pages))
        entries.append({"level": int(level), "title": title, "start_page": page})

    if len(entries) < MIN_TOC_ENTRIES:
        return None

    # Collapse same-start_page duplicates (keep first; merge titles? no — drop dupes)
    seen_pages = set()
    deduped = []
    for e in entries:
        if e["start_page"] in seen_pages:
            continue
        seen_pages.add(e["start_page"])
        deduped.append(e)
    if len(deduped) < MIN_TOC_ENTRIES:
        return None

    deduped.sort(key=lambda x: x["start_page"])
    return deduped


def build_chapter_path(entries: list[dict], idx: int) -> str:
    """For a given TOC entry index, walk back to find ancestor entries
    (level < current level) and join their titles with ' / '."""
    cur = entries[idx]
    parts = [cur["title"]]
    cur_level = cur["level"]
    for j in range(idx - 1, -1, -1):
        if entries[j]["level"] < cur_level:
            parts.insert(0, entries[j]["title"])
            cur_level = entries[j]["level"]
            if cur_level <= 0:
                break
    return " / ".join(parts)


# ── Standardize ────────────────────────────────────────────────
def standardize_pdf_full(book: dict, force: bool = False) -> tuple[list[dict] | None, dict | None, str | None]:
    """Returns (chapter_chunks, metadata, reason_for_fallback).

    If chapter_chunks is None, caller should leave Plan A output in place
    (`reason_for_fallback` explains why)."""
    ebook_id = book["id"]
    file_path = Path(book["file_path"])
    if not file_path.exists():
        return None, None, f"file not found: {file_path}"

    # 1. Per-page JSONL must exist (we don't re-extract — we re-chunk)
    jsonl_path = se.CHUNKS_DIR / f"{ebook_id}.jsonl"
    if not jsonl_path.exists():
        return None, None, "JSONL missing — run parse_worker / standardize_pdf_lite first"
    page_chunks = pl._read_jsonl_robust(jsonl_path)
    if not page_chunks:
        return None, None, "JSONL empty"

    # Re-run safety: if JSONL is already chapter-chunked (a prior Plan B run),
    # the page_lookup would be sparse (one entry per chapter start, not per
    # page) and re-chunking would break. Detect via page_range or chunk_type
    # and require an explicit revert via standardize_pdf_lite first.
    already_chapter = (
        any(c.get("page_range") for c in page_chunks[:5])
        or all((c.get("chunk_type") == "chapter") for c in page_chunks[:5])
    )
    if already_chapter:
        return None, None, "JSONL already chapter-chunked — run standardize_pdf_lite first to revert if you want to re-run Plan B"

    # 2. Annotations guard (re-chunking shifts chunk_index)
    if not force:
        n = has_annotations(ebook_id)
        if n > 0:
            return None, None, f"{n} annotation(s) exist — re-run with --force after migration plan"

    # 3. Read PDF TOC only (no body text re-extraction)
    try:
        doc = fitz.open(file_path)
        toc = doc.get_toc()
        total_pages = len(doc)
        doc.close()
    except Exception as e:
        return None, None, f"PDF open failed: {str(e)[:160]}"

    entries = normalize_toc(toc, total_pages)
    if not entries:
        return None, None, f"TOC unusable ({len(toc) if toc else 0} entries, {total_pages} pages)"

    # 4. Index existing per-page chunks by page_number
    page_lookup: dict[int, dict] = {}
    for c in page_chunks:
        pn = c.get("page_number")
        if pn is not None:
            page_lookup[int(pn)] = c
    if not page_lookup:
        return None, None, "JSONL has no page_number fields"
    last_page = max(page_lookup.keys())

    # 5. Build chapter chunks
    out: list[dict] = []
    first_toc_page = entries[0]["start_page"]

    # 5a. Front-matter chunk (pages 1 .. first_toc_page - 1)
    if first_toc_page > 1:
        front_pages = sorted(p for p in page_lookup.keys() if 1 <= p < first_toc_page)
        if front_pages:
            content = "\n\n".join(
                (page_lookup[p].get("content") or "").strip()
                for p in front_pages
                if (page_lookup[p].get("content") or "").strip()
            )
            content = se.to_traditional(content)
            content = pl.collapse_cjk_spacing(content)
            if content.strip():
                out.append({
                    "chunk_index": len(out),
                    "chunk_type": "chapter",
                    "page_number": front_pages[0],
                    "page_range": [front_pages[0], front_pages[-1]],
                    "chapter_path": "前置內容",
                    "format": "text",
                    "content": content,
                })

    # 5b. One chunk per TOC entry (chapter granularity)
    for idx, e in enumerate(entries):
        start_p = e["start_page"]
        end_p = (entries[idx + 1]["start_page"] - 1) if idx + 1 < len(entries) else last_page
        if end_p < start_p:
            end_p = start_p

        pages_in_range = sorted(p for p in page_lookup.keys() if start_p <= p <= end_p)
        if not pages_in_range:
            continue
        body_parts = []
        for p in pages_in_range:
            txt = (page_lookup[p].get("content") or "").strip()
            if txt:
                body_parts.append(txt)
        if not body_parts:
            # Empty chapter (image-only pages) — still emit so reader sidebar shows it
            content = ""
        else:
            content = "\n\n".join(body_parts)
            content = se.to_traditional(content)
            content = pl.collapse_cjk_spacing(content)

        chapter_path = build_chapter_path(entries, idx)
        chapter_path = se.to_traditional(chapter_path)
        chapter_path = se.normalize_chapter_title(chapter_path) or chapter_path

        out.append({
            "chunk_index": len(out),
            "chunk_type": "chapter",
            "page_number": pages_in_range[0],
            "page_range": [pages_in_range[0], pages_in_range[-1]],
            "chapter_path": chapter_path,
            "format": "text",
            "content": content,
        })

    if len(out) < MIN_TOC_ENTRIES:
        return None, None, f"only {len(out)} chunks produced after TOC processing — keeping Plan A"

    # 6. Publisher metadata extraction (now over chapter chunks; helper walks
    #    in order and first-hit wins, so the front-matter chunk dominates)
    metadata = se._extract_publisher_metadata(out)
    return out, metadata, None


# ── Persist ────────────────────────────────────────────────────
def write_jsonl(book_id: str, chunks: list[dict]) -> Path:
    se.CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    out = se.CHUNKS_DIR / f"{book_id}.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    return out


def update_db(book_id: str, chunks: list[dict], metadata: dict) -> None:
    """Same shape as standardize_pdf_lite.update_db, but:
    - chunk_count = len(chunks) (chapters, not pages)
    - total_pages stays as the highest page_number seen (real PDF page count)
    """
    import requests
    total_chars = sum(len(c.get("content") or "") for c in chunks)
    last_page = max(
        (c.get("page_range", [c.get("page_number") or 0])[-1] for c in chunks),
        default=0,
    )
    patch = {
        "chunk_count": len(chunks),
        "total_chars": total_chars,
        "total_pages": last_page or len(chunks),
        "parsed_at": datetime.utcnow().isoformat() + "Z",
    }
    if metadata.get("full_title"):
        _, sub = se._split_title_subtitle(metadata["full_title"])
        if sub:
            patch["subtitle"] = sub
    for src, dst in [
        ("original_title",        "original_title"),
        ("author_en",             "author_en"),
        ("translator",            "translator"),
        ("publisher",             "publisher"),
        ("publish_year",          "publication_year"),
        ("original_publish_year", "original_publish_year"),
        ("original_author",       "original_author"),
    ]:
        if metadata.get(src):
            patch[dst] = metadata[src]

    requests.patch(
        f"{se.URL}/rest/v1/ebooks?id=eq.{book_id}",
        headers=se.H_JSON,
        json=patch,
        timeout=30,
    )

    # Refresh ebook_chunks previews
    requests.delete(f"{se.URL}/rest/v1/ebook_chunks?ebook_id=eq.{book_id}", headers=se.H_GET, timeout=30)
    rows = [{
        "ebook_id": book_id,
        "chunk_index": c["chunk_index"],
        "chunk_type": c.get("chunk_type") or "chapter",
        "page_number": c.get("page_number"),
        "chapter_path": c.get("chapter_path"),
        # PostgreSQL JSONB rejects U+0000; scrub before insert.
        "content": (c.get("content") or "").replace("\x00", "")[:se.PREVIEW_LEN],
        "char_count": len((c.get("content") or "").replace("\x00", "")),
    } for c in chunks]
    BATCH = 50
    for i in range(0, len(rows), BATCH):
        r = requests.post(f"{se.URL}/rest/v1/ebook_chunks", headers=se.H_JSON, json=rows[i:i+BATCH], timeout=60)
        if not r.ok:
            raise RuntimeError(f"chunk preview insert failed: {r.status_code} {r.text[:200]}")


# ── Entry points ───────────────────────────────────────────────
def standardize_one(ebook_id: str, dry_run: bool = False, no_r2: bool = False, force: bool = False):
    try:
        book = se.fetch_book(ebook_id)
    except Exception as e:
        return 0, f"fetch failed: {e}"
    if book.get("file_type") != "pdf":
        return 0, f"not a PDF ({book.get('file_type')})"

    chunks, metadata, reason = standardize_pdf_full(book, force=force)
    if chunks is None:
        return 0, f"skipped: {reason}"

    if dry_run:
        chap_count = sum(1 for c in chunks if c.get("chapter_path") and c.get("chapter_path") != "前置內容")
        print(f"  would emit {len(chunks)} chapter chunks ({chap_count} from TOC + {len(chunks) - chap_count} front-matter)")
        print(f"  page_number range: {chunks[0].get('page_number')} → {chunks[-1].get('page_range', [chunks[-1].get('page_number')])[-1]}")
        if metadata:
            present = {k: v for k, v in metadata.items() if v}
            if present:
                print(f"  metadata: {json.dumps(present, ensure_ascii=False)}")
        # Sample chapter titles
        for c in chunks[:8]:
            cp = c.get("chapter_path", "?")
            pr = c.get("page_range", [c.get("page_number")])
            print(f"    p{pr[0]}-{pr[-1]}  {cp[:60]}  ({len(c.get('content') or '')} chars)")
        if len(chunks) > 8:
            print(f"    ... and {len(chunks) - 8} more")
        return len(chunks), None

    try:
        out = write_jsonl(ebook_id, chunks)
        if not no_r2:
            pl.push_to_r2(ebook_id, out)
        update_db(ebook_id, chunks, metadata or {})
    except Exception as e:
        return 0, f"persist failed: {str(e)[:200]}"
    return len(chunks), None


def cmd_batch(category=None, subcategory=None, limit=None, dry_run=False, no_r2=False, force=False):
    books = pl.fetch_pdfs_by_category(category, subcategory, limit)
    label = "ALL categories" if not category else f"Category: {category}{f' / {subcategory}' if subcategory else ''}"
    print(f"{label} — {len(books)} eligible PDFs")
    if not books:
        return
    if dry_run:
        for b in books[:20]:
            print(f"  - {b['title'][:50]:50s}  /  {(b.get('author') or '')[:20]}  ({b.get('chunk_count', '?')} chunks now)")
        if len(books) > 20:
            print(f"  ... and {len(books) - 20} more")
        return
    t0 = time.time()
    ok = skipped = failed_n = 0
    skip_reasons = {}
    for i, b in enumerate(books, 1):
        title = (b["title"] or "Untitled")[:40]
        n, err = standardize_one(b["id"], no_r2=no_r2, force=force)
        if err and err.startswith("skipped:"):
            skipped += 1
            r = err.replace("skipped: ", "")[:60]
            skip_reasons[r] = skip_reasons.get(r, 0) + 1
            print(f"  [{i:3d}/{len(books)}] · {title}: {err[:80]}", flush=True)
        elif err:
            failed_n += 1
            print(f"  [{i:3d}/{len(books)}] ⚠ {title}: {err[:80]}", flush=True)
        else:
            ok += 1
            print(f"  [{i:3d}/{len(books)}] ✓ {title}: {n} chapters", flush=True)
    print(f"\nDone in {time.time()-t0:.0f}s. OK: {ok}, Skipped: {skipped}, Failed: {failed_n}")
    if skip_reasons:
        print("Skip reason breakdown:")
        for r, n in sorted(skip_reasons.items(), key=lambda x: -x[1]):
            print(f"  {n:4d}  {r}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("ebook_id", nargs="?")
    p.add_argument("--all", action="store_true")
    p.add_argument("--category")
    p.add_argument("--subcategory")
    p.add_argument("--limit", type=int)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--no-r2", action="store_true")
    p.add_argument("--force", action="store_true", help="ignore annotations guard")
    args = p.parse_args()

    if args.ebook_id:
        n, err = standardize_one(args.ebook_id, dry_run=args.dry_run, no_r2=args.no_r2, force=args.force)
        if err:
            print(f"⚠ {err}", file=sys.stderr)
            sys.exit(1)
        print(f"✓ {n} chunks{' (dry-run)' if args.dry_run else ''}")
    elif args.all or args.category or args.subcategory:
        cmd_batch(args.category, args.subcategory, args.limit, args.dry_run, args.no_r2, args.force)
    else:
        p.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
