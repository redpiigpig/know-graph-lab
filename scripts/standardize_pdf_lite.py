#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
standardize_pdf_lite.py — Plan A "lite pass" PDF restandardize.

Reuses helpers from standardize_ebook.py and operates on the JSONL output
that parse_worker / ocr_with_gemini already produced. Does:

  - to_traditional() (s2tw + TRAD_FIXES) on every chunk's content
  - Strip the most common PDF noise: extra inter-character spaces, isolated
    page-number-only lines at top/bottom of page bodies (running header/
    footer)
  - Re-derive chapter_path when a clear 第N章 / Chapter N / 引言 / 序 marker
    appears at the start of a page
  - Extract publisher metadata (書名 / 譯者 / 出版社 / Copyright …) and PATCH
    onto the ebooks row (same fields as the EPUB pipeline)

Does NOT do (those need the full Plan B build with PyMuPDF):
  - chapter-level chunk splitting (we keep one-page-one-chunk)
  - cover insertion / frontmatter consolidation (would shift page_number)
  - volume hierarchy (PDFs use bookmarks; PyMuPDF needed)

CRITICAL: every chunk's `page_number` is preserved exactly. PDFs have real
publisher pagination (skipped page numbers, blanks, etc.) and citations
depend on it.

Usage — single book:
  python scripts/standardize_pdf_lite.py <ebook_id>
  python scripts/standardize_pdf_lite.py <ebook_id> --dry-run
  python scripts/standardize_pdf_lite.py <ebook_id> --no-r2

Usage — batch (auto-skips EPUBs):
  python scripts/standardize_pdf_lite.py --category 哲學
  python scripts/standardize_pdf_lite.py --all          # every parsed PDF
  python scripts/standardize_pdf_lite.py --all --limit 5 --dry-run

Idempotent: re-running overwrites local JSONL, R2 object, and ebooks
metadata fields. The ebook_chunks DB previews are also refreshed.
"""
from __future__ import annotations

import argparse
import gzip
import io
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
import standardize_ebook as se  # reuse helpers


# ── PDF-specific cleanup ────────────────────────────────────────────────

# Many parsers emit text like "路 … 文 本 、 历 史" — single CJK chars
# separated by single spaces. Collapse those without breaking real spaces
# in mixed CJK/Latin paragraphs.
def collapse_cjk_spacing(text: str) -> str:
    if not text:
        return text
    # Repeatedly squeeze "{cjk} {cjk}" → "{cjk}{cjk}" until no more matches.
    # 5 iterations is plenty for normal page widths.
    for _ in range(5):
        new = re.sub(r"([一-鿿])\s+([一-鿿])", r"\1\2", text)
        if new == text:
            break
        text = new
    return text


# Running header / footer is usually a short line at the very start or end
# containing a page number (with optional book title attached). Strip them
# only when they're highly confidently noise.
_PAGE_HEADER_RX = re.compile(r"^\s*(\d{1,4})\s+\S{0,40}$", re.MULTILINE)


def strip_page_header(text: str, expected_page: int | None) -> str:
    """If the FIRST non-empty line is just '<page-number> <title>' for the
    expected page, drop it. Conservative — only fires when the number on
    the line matches `expected_page` (so we don't accidentally strip a
    sentence that happens to start with a number)."""
    if not text or not expected_page:
        return text
    lines = text.split("\n", 2)
    if not lines:
        return text
    first = lines[0].strip()
    m = re.match(r"^(\d{1,4})\b", first)
    if m and int(m.group(1)) == expected_page and len(first) <= 40:
        return "\n".join(lines[1:]).lstrip()
    return text


# Chapter heading patterns to look for at the top of a page. Mix of CJK +
# English so the same script works on academic PDFs. We're conservative —
# only pick up clear matches at the start of the page content.
_PDF_CHAPTER_RX = re.compile(
    r"^("
    r"第[一二三四五六七八九十百千零〇\d]+(?:章|卷|編|编|册|冊|部|集|篇|節|节|回|课|課)\s*[^\n]{0,40}"
    r"|序\s*[言論章]?\s*[^\n]{0,30}"
    r"|前\s*言\s*[^\n]{0,30}"
    r"|緒\s*論\s*[^\n]{0,30}"
    r"|導\s*[言論]\s*[^\n]{0,30}"
    r"|引\s*言\s*[^\n]{0,30}"
    r"|致\s*謝\s*[^\n]{0,30}"
    r"|附\s*錄\s*[^\n]{0,30}"
    r"|目\s*錄"
    r"|版\s*權\s*頁"
    r"|Chapter\s+\d+[\s.:][^\n]{0,60}"
    r"|Introduction\b[^\n]{0,30}"
    r"|Preface\b[^\n]{0,30}"
    r"|Foreword\b[^\n]{0,30}"
    r"|Contents\b"
    r"|Acknowledg(?:e?)ments\b"
    r"|Bibliography\b"
    r"|Index\b"
    r")",
    re.IGNORECASE,
)


def derive_pdf_chapter_path(content: str) -> str | None:
    """Look at the first ~3 non-empty lines of a page; if one is a clear
    chapter heading, return it. Otherwise None (don't guess — leaving
    chapter_path null is better than mislabeling)."""
    if not content:
        return None
    seen = 0
    for raw in content.split("\n"):
        s = raw.strip()
        if not s:
            continue
        seen += 1
        m = _PDF_CHAPTER_RX.match(s)
        if m:
            return se.normalize_chapter_title(m.group(1).strip())
        if seen >= 3:
            break
    return None


# ── Standardize one PDF ────────────────────────────────────────────────

def _read_jsonl_robust(path: Path) -> list[dict]:
    """Tolerate JSONL files where a record's `content` string contains
    literal newlines that were never escaped during the original parse_worker
    write. A naive line-by-line parse trips on those records (json hits
    "Unterminated string"). We accumulate physical lines into a buffer and
    retry json.loads after each append until parsing succeeds, then start a
    fresh buffer. Records produced by a well-formed writer parse on the
    first try, so this is zero-overhead in the common case."""
    out: list[dict] = []
    buf = ""
    bad_runs = 0
    for raw in path.read_text(encoding="utf-8").split("\n"):
        if not buf and not raw.strip():
            continue
        buf = (buf + "\n" + raw) if buf else raw
        try:
            out.append(json.loads(buf))
            buf = ""
        except json.JSONDecodeError:
            # Cap runaway accumulation in case the file is truly malformed
            # (avoid swallowing the entire file into one buffer)
            bad_runs += 1
            if bad_runs > 50 and not out:
                raise
            continue
    if buf.strip():
        # Trailing fragment that never parsed — log but don't fail the book
        print(f"  ⚠ trailing fragment in {path.name} ({len(buf)} chars unparsed)", file=sys.stderr)
    return out


def standardize_pdf_chunks(book) -> tuple[list[dict], dict]:
    """Read the existing JSONL for this PDF book and return (cleaned_chunks,
    extracted_metadata). Does NOT write — caller persists."""
    src = se.CHUNKS_DIR / f"{book['id']}.jsonl"
    if not src.exists():
        raise SystemExit(f"JSONL missing on disk: {src}")

    chunks_in = _read_jsonl_robust(src)
    print(f"  read {len(chunks_in)} existing chunks from {src.name}")

    cleaned = []
    for c in chunks_in:
        page_number = c.get("page_number")  # MUST preserve as-is
        raw_content = c.get("content") or ""

        # 1. s2tw + TRAD_FIXES
        content = se.to_traditional(raw_content)
        # 2. Collapse "字 字 字" spacing artifacts
        content = collapse_cjk_spacing(content)
        # 3. Drop a running-header line if it matches the page number
        content = strip_page_header(content, page_number)
        # 4. Re-derive chapter_path only if absent
        chapter_path = c.get("chapter_path") or derive_pdf_chapter_path(content)

        cleaned.append({
            "chunk_index": len(cleaned),
            "chunk_type": c.get("chunk_type") or "page",
            "page_number": page_number,                 # ← preserved
            "chapter_path": chapter_path,
            "format": "text",
            "content": content,
        })

    # Extract publisher metadata across all chunks (early pages dominate
    # because we walk in order and first-hit wins per field).
    metadata = se._extract_publisher_metadata(cleaned)
    return cleaned, metadata


# ── Persist ─────────────────────────────────────────────────────────────

def write_jsonl(book_id: str, chunks: list[dict]) -> Path:
    se.CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    out = se.CHUNKS_DIR / f"{book_id}.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    return out


def push_to_r2(book_id: str, jsonl_path: Path) -> int:
    """Same as standardize_ebook.push_to_r2 — duplicated rather than imported
    to keep this script standalone-runnable if standardize_ebook drifts."""
    import boto3
    raw = Path(jsonl_path).read_bytes()
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=6) as gz:
        gz.write(raw)
    c = boto3.client(
        "s3", region_name="auto", endpoint_url=se.ENV["R2_ENDPOINT"],
        aws_access_key_id=se.ENV["R2_ACCESS_KEY"],
        aws_secret_access_key=se.ENV["R2_SECRET_KEY"],
    )
    c.put_object(
        Bucket=se.ENV["R2_BUCKET"],
        Key=f"ebook-chunks/{book_id}.jsonl.gz",
        Body=buf.getvalue(),
        ContentType="application/x-ndjson",
        ContentEncoding="gzip",
    )
    return len(buf.getvalue())


def update_db(book_id: str, chunks: list[dict], metadata: dict) -> None:
    import requests
    total_chars = sum(len(c.get("content") or "") for c in chunks)

    patch = {
        "chunk_count": len(chunks),
        "total_chars": total_chars,
        "parsed_at": datetime.utcnow().isoformat() + "Z",
    }
    # Same metadata mapping as standardize_ebook.update_db.
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

    # Refresh ebook_chunks previews for full-text search.
    requests.delete(f"{se.URL}/rest/v1/ebook_chunks?ebook_id=eq.{book_id}", headers=se.H_GET, timeout=30)
    # PostgreSQL JSONB rejects U+0000; scrub before insert.
    def _clean(v):
        return v.replace("\x00", "") if isinstance(v, str) else v
    rows = [{
        "ebook_id": book_id,
        "chunk_index": c["chunk_index"],
        "chunk_type": c.get("chunk_type") or "page",
        "page_number": c.get("page_number"),
        "chapter_path": _clean(c.get("chapter_path")),
        "content": _clean(c.get("content") or "")[:se.PREVIEW_LEN],
        "char_count": len(_clean(c.get("content") or "")),
    } for c in chunks]
    # Adaptive batch — on 57014 (Supabase IO timeout) shrink the batch and
    # retry instead of failing the whole book and leaving ebook_chunks empty
    # (delete already ran above). Mirrors repopulate_chunk_previews.insert_previews.
    BATCH_SIZES = [50, 20, 5, 1]
    i = 0
    while i < len(rows):
        succeeded = False
        for bs in BATCH_SIZES:
            batch = rows[i:i+bs]
            r = requests.post(f"{se.URL}/rest/v1/ebook_chunks",
                              headers=se.H_JSON, json=batch, timeout=120)
            if r.status_code in (200, 201):
                i += len(batch)
                succeeded = True
                break
            text = r.text[:300]
            if "57014" in text or "timeout" in text.lower() or r.status_code >= 500:
                if bs > BATCH_SIZES[-1]:
                    continue
            raise RuntimeError(f"chunk preview insert failed: {r.status_code} {text}")
        if not succeeded:
            raise RuntimeError(f"chunk preview insert failed at batch_size=1, row {i}")


# ── Entry points ────────────────────────────────────────────────────────

def standardize_one(ebook_id: str, dry_run: bool = False, no_r2: bool = False) -> tuple[int, str | None]:
    try:
        book = se.fetch_book(ebook_id)
    except Exception as e:
        return 0, f"fetch failed: {e}"
    if book.get("file_type") != "pdf":
        return 0, f"not a PDF ({book.get('file_type')})"
    try:
        chunks, metadata = standardize_pdf_chunks(book)
    except Exception as e:
        return 0, f"parse failed: {str(e)[:200]}"
    if not chunks:
        return 0, "no chunks produced"
    if dry_run:
        print(f"  metadata extracted: " + json.dumps({k: v for k, v in metadata.items() if v}, ensure_ascii=False))
        return len(chunks), None
    try:
        out = write_jsonl(ebook_id, chunks)
        if not no_r2:
            push_to_r2(ebook_id, out)
        update_db(ebook_id, chunks, metadata)
    except Exception as e:
        return 0, f"persist failed: {str(e)[:200]}"
    return len(chunks), None


def fetch_pdfs_by_category(category: str | None = None, subcategory: str | None = None, limit: int | None = None):
    import requests
    params = (
        "select=id,title,author,file_type,file_path,parsed_at,chunk_count,category"
        "&parsed_at=not.is.null"
        "&file_type=eq.pdf"
        "&order=category,title"
        "&limit=2000"
    )
    if category:    params += f"&category=eq.{requests.utils.quote(category)}"
    if subcategory: params += f"&subcategory=eq.{requests.utils.quote(subcategory)}"
    r = requests.get(f"{se.URL}/rest/v1/ebooks?{params}", headers=se.H_GET, timeout=30)
    r.raise_for_status()
    books = r.json()
    if limit:
        books = books[:limit]
    return books


def cmd_batch(category: str | None = None, subcategory: str | None = None,
              limit: int | None = None, dry_run: bool = False, no_r2: bool = False) -> None:
    books = fetch_pdfs_by_category(category, subcategory, limit)
    label = "ALL categories" if not category else f"Category: {category}{f' / {subcategory}' if subcategory else ''}"
    print(label)
    print(f"Eligible PDFs: {len(books)}")
    if not books:
        print("Nothing to do.")
        return
    if dry_run:
        for b in books[:20]:
            print(f"  - {b['title'][:50]:50s}  /  {(b.get('author') or '')[:20]}  ({b.get('chunk_count','?')} chunks)")
        if len(books) > 20:
            print(f"  ... and {len(books) - 20} more")
        return
    t0 = time.time()
    ok = 0
    failed = []
    for i, b in enumerate(books, 1):
        title = (b["title"] or "Untitled")[:40]
        n, err = standardize_one(b["id"], no_r2=no_r2)
        elapsed = time.time() - t0
        rate = i / elapsed if elapsed else 0
        eta = (len(books) - i) / rate if rate else 0
        if err:
            failed.append((title, err))
            print(f"  [{i:3d}/{len(books)}] ⚠ {title}: {err[:80]}", flush=True)
        else:
            ok += 1
            print(f"  [{i:3d}/{len(books)}] ✓ {title}: {n} chunks  ETA {int(eta)}s", flush=True)
    print(f"\nDone in {time.time()-t0:.0f}s. OK: {ok}, Failed: {len(failed)}")
    if failed:
        print("Failures:")
        for n, e in failed[:20]:
            print(f"  - {n}: {e[:200]}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("ebook_id", nargs="?", help="single book mode (UUID)")
    p.add_argument("--all", action="store_true", help="every parsed PDF")
    p.add_argument("--category", help="batch filter")
    p.add_argument("--subcategory", help="batch filter")
    p.add_argument("--limit", type=int, help="batch cap")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--no-r2", action="store_true")
    args = p.parse_args()

    if args.ebook_id:
        n, err = standardize_one(args.ebook_id, dry_run=args.dry_run, no_r2=args.no_r2)
        if err:
            print(f"⚠ {err}", file=sys.stderr)
            sys.exit(1)
        print(f"✓ {n} chunks{' (dry-run)' if args.dry_run else ''}")
    elif args.all or args.category or args.subcategory:
        cmd_batch(args.category, args.subcategory, args.limit, args.dry_run, args.no_r2)
    else:
        p.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
