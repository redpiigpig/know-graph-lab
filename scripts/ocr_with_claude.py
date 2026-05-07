#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR scanned PDFs via Claude Vision (Anthropic API).

Targets ebooks where parse_error LIKE '%no extractable text%'.
For each book:
  1. Render PDF pages as PNG via PyMuPDF (150 DPI, in-memory)
  2. Send batches of PAGES_PER_BATCH page images to Claude Haiku
  3. Parse [PAGE N] marker response into per-page chunks
  4. Write JSONL to local _chunks/{id}.jsonl + 200-char preview to DB
  5. Mark parsed_at, clear parse_error

Advantages over ocr_with_gemini.py:
  - No Gemini quota (uses Anthropic API credits instead)
  - No JSON truncation: plain-text [PAGE N] format, no token-limit cutoff
  - Full coverage: all pages processed regardless of PDF size

Usage:
  python scripts/ocr_with_claude.py status
  python scripts/ocr_with_claude.py run [--limit N] [--rpm 20]
  python scripts/ocr_with_claude.py run --dry-run
"""

import base64
import gzip
import io
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Missing: pip install pymupdf", file=sys.stderr)
    sys.exit(1)

try:
    import anthropic
except ImportError:
    print("Missing: pip install anthropic", file=sys.stderr)
    sys.exit(1)

import requests

sys.path.insert(0, str(Path(__file__).parent))
from parse_worker import load_env

ENV = load_env()
URL = ENV["SUPABASE_URL"]
KEY = ENV["SUPABASE_SERVICE_ROLE_KEY"]
H = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}

CHUNKS_DIR = Path("G:/我的雲端硬碟/資料/電子書/_chunks")
PREVIEW_LEN = 200
DEFAULT_MODEL = "claude-haiku-4-5-20251001"
PAGES_PER_BATCH = 10
DPI = 150
DEFAULT_RPM = 20


# ── DB helpers (same contract as ocr_with_gemini.py) ─────────────

def fetch_ocr_targets(sort_by_size=True):
    out = []
    offset = 0
    while True:
        params = (
            f"select=id,title,author,file_type,file_path,parse_error"
            f"&parse_error=ilike.*no extractable text*"
            f"&order=id&limit=1000&offset={offset}"
        )
        r = requests.get(f"{URL}/rest/v1/ebooks?{params}",
                         headers={"apikey": KEY, "Authorization": f"Bearer {KEY}"},
                         timeout=30)
        r.raise_for_status()
        page = r.json()
        if not page:
            break
        out.extend(page)
        if len(page) < 1000:
            break
        offset += 1000
    if sort_by_size:
        def size_of(b):
            try:
                p = Path(b["file_path"])
                return p.stat().st_size if p.exists() else float("inf")
            except Exception:
                return float("inf")
        out.sort(key=size_of)
    return out


def update_book_done(book_id, total_chars, chunk_count, total_pages):
    requests.patch(
        f"{URL}/rest/v1/ebooks?id=eq.{book_id}",
        headers=H,
        json={
            "parsed_at": datetime.utcnow().isoformat() + "Z",
            "parse_error": None,
            "total_chars": total_chars,
            "chunk_count": chunk_count,
            "total_pages": total_pages,
        },
        timeout=30,
    )


def update_book_error(book_id, msg):
    try:
        requests.patch(
            f"{URL}/rest/v1/ebooks?id=eq.{book_id}",
            headers=H,
            json={"parse_error": msg[:500]},
            timeout=30,
        )
    except Exception as e:
        print(f"  ⚠ failed to record parse_error for {book_id}: {str(e)[:80]}",
              file=sys.stderr)


def insert_chunk_previews(book_id, chunks):
    if not chunks:
        return
    rows = [
        {
            "ebook_id": book_id,
            "chunk_index": i,
            "chunk_type": "page",
            "page_number": c["page"],
            "chapter_path": None,
            "content": c["text"][:PREVIEW_LEN],
            "char_count": len(c["text"]),
        }
        for i, c in enumerate(chunks)
    ]
    requests.delete(
        f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{book_id}",
        headers={"apikey": KEY, "Authorization": f"Bearer {KEY}"},
        timeout=30,
    )
    for i in range(0, len(rows), 50):
        r = requests.post(f"{URL}/rest/v1/ebook_chunks", headers=H,
                          json=rows[i:i + 50], timeout=60)
        if not r.ok:
            raise RuntimeError(f"chunk insert failed: {r.status_code} {r.text[:200]}")


def write_jsonl(book_id, chunks):
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    out = CHUNKS_DIR / f"{book_id}.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for i, c in enumerate(chunks):
            f.write(json.dumps({
                "chunk_index": i,
                "chunk_type": "page",
                "page_number": c["page"],
                "chapter_path": None,
                "content": c["text"],
            }, ensure_ascii=False) + "\n")
    return out


_r2_client = None
def _r2():
    global _r2_client
    if _r2_client is None:
        import boto3
        _r2_client = boto3.client(
            "s3", region_name="auto",
            endpoint_url=ENV["R2_ENDPOINT"],
            aws_access_key_id=ENV["R2_ACCESS_KEY"],
            aws_secret_access_key=ENV["R2_SECRET_KEY"],
        )
    return _r2_client


def push_to_r2(book_id, jsonl_path):
    raw = Path(jsonl_path).read_bytes()
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=6) as gz:
        gz.write(raw)
    _r2().put_object(
        Bucket=ENV["R2_BUCKET"],
        Key=f"ebook-chunks/{book_id}.jsonl.gz",
        Body=buf.getvalue(),
        ContentType="application/x-ndjson",
        ContentEncoding="gzip",
    )


# ── Claude OCR core ───────────────────────────────────────────────

BATCH_PROMPT = """\
Each image is one page from a scanned book (Chinese Traditional/Simplified or English).
For each page, extract ALL visible text exactly as written — do NOT translate, summarize, or add commentary.

Output format — one block per page, exactly:
[PAGE {first}]
<extracted text>

[PAGE {next}]
<extracted text>

...and so on for every image in order.
If a page is blank or purely decorative, output its [PAGE N] header with an empty body.
"""


def _render_page_png(doc, page_idx: int) -> bytes:
    """Render a single PDF page to PNG bytes at DPI resolution."""
    page = doc[page_idx]
    mat = fitz.Matrix(DPI / 72, DPI / 72)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
    return pix.tobytes("png")


def _parse_batch_response(text: str, page_numbers: list[int]) -> list[dict]:
    """Parse [PAGE N] delimited response into list of {page, text} dicts."""
    chunks = []
    # Split on [PAGE N] markers
    import re
    parts = re.split(r'\[PAGE\s+(\d+)\]', text)
    # parts = ['preamble', 'N', 'body', 'M', 'body', ...]
    for i in range(1, len(parts) - 1, 2):
        try:
            page_num = int(parts[i])
            body = parts[i + 1].strip()
            chunks.append({"page": page_num, "text": body})
        except (ValueError, IndexError):
            continue
    # Fall back: if parsing produced nothing, assign by position
    if not chunks and page_numbers:
        lines = text.strip().split("\n")
        for j, pn in enumerate(page_numbers):
            chunks.append({"page": pn, "text": lines[j] if j < len(lines) else ""})
    return chunks


def ocr_book(client, src_path: Path, model: str) -> list[dict]:
    """OCR all pages of a PDF. Returns list of {page, text} dicts."""
    doc = fitz.open(src_path)
    total = len(doc)
    all_chunks: list[dict] = []

    for batch_start in range(0, total, PAGES_PER_BATCH):
        batch_end = min(batch_start + PAGES_PER_BATCH, total)
        page_indices = list(range(batch_start, batch_end))
        page_numbers = [i + 1 for i in page_indices]  # 1-based

        # Build message content: one image per page
        content: list = []
        for pi in page_indices:
            png_bytes = _render_page_png(doc, pi)
            b64 = base64.standard_b64encode(png_bytes).decode()
            content.append({
                "type": "image",
                "source": {"type": "base64", "media_type": "image/png", "data": b64},
            })
        prompt = BATCH_PROMPT.format(first=page_numbers[0], next=page_numbers[1] if len(page_numbers) > 1 else page_numbers[0] + 1)
        content.append({"type": "text", "text": prompt})

        resp = client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": content}],
        )
        batch_text = resp.content[0].text if resp.content else ""
        batch_chunks = _parse_batch_response(batch_text, page_numbers)
        all_chunks.extend(batch_chunks)

    doc.close()
    return all_chunks


def process_one(client, book: dict, src_path: Path, model: str, max_retries: int = 2) -> dict:
    title = (book["title"] or src_path.stem)[:40]
    last_err = ""
    for attempt in range(1, max_retries + 1):
        try:
            t0 = time.time()
            chunks = ocr_book(client, src_path, model)
            non_empty = [c for c in chunks if c.get("text", "").strip()]
            if not non_empty:
                return {"status": "fail", "error": "model returned 0 usable pages", "transient": False}

            total_chars = sum(len(c["text"]) for c in non_empty)
            jsonl_path = write_jsonl(book["id"], non_empty)
            insert_chunk_previews(book["id"], non_empty)

            r2_ok, r2_err = True, ""
            try:
                push_to_r2(book["id"], jsonl_path)
            except Exception as e:
                r2_ok, r2_err = False, str(e)[:200]

            elapsed = time.time() - t0
            tag = "✓" if r2_ok else "⚠ R2 fail"
            print(f"  {tag} {len(non_empty)} pages, {total_chars // 1000}K chars, {elapsed:.0f}s")

            if r2_ok:
                update_book_done(book["id"], total_chars=total_chars,
                                 chunk_count=len(non_empty),
                                 total_pages=max(c["page"] for c in non_empty))
                return {"status": "ok"}
            else:
                update_book_error(book["id"], f"OCR ok but R2 push failed: {r2_err}")
                return {"status": "fail", "error": f"R2: {r2_err}", "transient": True}

        except anthropic.RateLimitError as e:
            last_err = str(e)[:300]
            wait = min(2 ** attempt * 10, 120)
            print(f"  ↻ rate limit, retry {attempt} after {wait}s")
            time.sleep(wait)
        except anthropic.APIStatusError as e:
            last_err = str(e)[:300]
            if e.status_code in (529, 503, 502):  # overloaded / unavailable
                wait = min(2 ** attempt * 10, 120)
                print(f"  ↻ API {e.status_code}, retry {attempt} after {wait}s")
                time.sleep(wait)
            else:
                print(f"  ❌ {last_err[:200]}")
                return {"status": "fail", "error": last_err, "transient": False}
        except Exception as e:
            last_err = str(e)[:300]
            print(f"  ❌ {last_err[:200]}")
            return {"status": "fail", "error": last_err, "transient": False}

    return {"status": "fail", "error": last_err, "transient": True}


# ── commands ──────────────────────────────────────────────────────

def cmd_status():
    targets = fetch_ocr_targets()
    print(f"OCR candidates (parse_error contains 'no extractable text'): {len(targets)}")
    if targets[:3]:
        print("\nFirst 3:")
        for b in targets[:3]:
            sz = ""
            try:
                p = Path(b["file_path"])
                if p.exists():
                    sz = f"  ({p.stat().st_size // 1024} KB)"
            except Exception:
                pass
            print(f"  {b['title'][:50]}{sz}")


def cmd_run(limit=None, model=DEFAULT_MODEL, rpm=DEFAULT_RPM, dry_run=False):
    api_key = ENV.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Missing ANTHROPIC_API_KEY in .env", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    targets = fetch_ocr_targets()
    if limit:
        targets = targets[:limit]
    print(f"OCR candidates: {len(targets)}  model={model}  rpm={rpm}")

    if dry_run:
        for b in targets[:20]:
            print(f"  {b['title'][:60]}")
        return

    min_gap = 60.0 / rpm
    last_call = 0.0
    ok, failed = 0, []

    for i, b in enumerate(targets, 1):
        src = Path(b["file_path"])
        if not src.exists():
            print(f"  [{i:3d}/{len(targets)}] ⚠ source missing: {src}", file=sys.stderr)
            update_book_error(b["id"], f"file not found: {src}")
            failed.append((b["title"], "source missing"))
            continue

        gap = time.time() - last_call
        if gap < min_gap:
            time.sleep(min_gap - gap)
        last_call = time.time()

        sz_mb = src.stat().st_size / 1024 / 1024
        title_short = (b["title"] or src.stem)[:40]
        print(f"  [{i:3d}/{len(targets)}] OCR  {title_short}  ({sz_mb:.1f} MB)…",
              end="", flush=True)

        result = process_one(client, b, src, model)
        if result["status"] == "ok":
            ok += 1
        else:
            failed.append((b["title"], result["error"]))
            if not result["transient"]:
                update_book_error(b["id"], result["error"])

    print(f"\nDone. OK: {ok}, Failed: {len(failed)}")
    if failed:
        print("First failures:")
        for title, err in failed[:5]:
            print(f"  - {title[:50]}  {err[:80]}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "status":
        cmd_status()
    elif cmd == "run":
        limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None
        model = args[args.index("--model") + 1] if "--model" in args else DEFAULT_MODEL
        rpm = int(args[args.index("--rpm") + 1]) if "--rpm" in args else DEFAULT_RPM
        cmd_run(limit=limit, model=model, rpm=rpm, dry_run="--dry-run" in args)
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)
