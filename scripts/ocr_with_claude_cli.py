#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR scanned PDFs via Claude Haiku — uses Claude Code's OAuth token (no API key needed).

Reads the bearer token from ~/.claude/.credentials.json (claudeAiOauth.accessToken),
which is the same credential Claude Code uses. Falls back to ANTHROPIC_API_KEY if set.

One book at a time: prints confirmation before proceeding to next.

Usage:
  python scripts/ocr_with_claude_cli.py status
  python scripts/ocr_with_claude_cli.py run [--limit N] [--batch 10]
  python scripts/ocr_with_claude_cli.py run --one <ebook_id>
"""
import base64
import gzip
import io
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

try:
    import fitz
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
MODEL = "claude-haiku-4-5-20251001"
DPI = 150
DEFAULT_BATCH = 10


# ── Auth ─────────────────────────────────────────────────────────

def make_client() -> anthropic.Anthropic:
    """Create Anthropic client using API key or Claude Code's stored OAuth token."""
    api_key = ENV.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return anthropic.Anthropic(api_key=api_key)

    cred_path = Path(os.environ.get("USERPROFILE", os.environ.get("HOME", ""))) / ".claude" / ".credentials.json"
    if cred_path.exists():
        with cred_path.open(encoding="utf-8") as f:
            creds = json.load(f)
        token = creds.get("claudeAiOauth", {}).get("accessToken", "")
        if token:
            return anthropic.Anthropic(auth_token=token)

    raise RuntimeError(
        "No Anthropic credentials. Either add ANTHROPIC_API_KEY to .env, "
        "or sign in to Claude Code (`claude auth login`)."
    )


# ── DB helpers ────────────────────────────────────────────────────

def fetch_ocr_targets(sort_by_size=True):
    out = []
    offset = 0
    while True:
        params = (
            "select=id,title,author,file_type,file_path,parse_error"
            "&parse_error=ilike.*no extractable text*"
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
        def _sz(b):
            try:
                p = Path(b["file_path"])
                return p.stat().st_size if p.exists() else float("inf")
            except Exception:
                return float("inf")
        out.sort(key=_sz)
    return out


def update_book_done(book_id, total_chars, chunk_count, total_pages):
    requests.patch(
        f"{URL}/rest/v1/ebooks?id=eq.{book_id}", headers=H,
        json={"parsed_at": datetime.utcnow().isoformat() + "Z",
              "parse_error": None,
              "total_chars": total_chars,
              "chunk_count": chunk_count,
              "total_pages": total_pages},
        timeout=30)


def update_book_error(book_id, msg):
    try:
        requests.patch(f"{URL}/rest/v1/ebooks?id=eq.{book_id}", headers=H,
                       json={"parse_error": msg[:500]}, timeout=30)
    except Exception as e:
        print(f"  ⚠ failed to record error: {e}", file=sys.stderr)


def insert_chunk_previews(book_id, chunks):
    if not chunks:
        return
    rows = [{"ebook_id": book_id, "chunk_index": i, "chunk_type": "page",
             "page_number": c["page"], "chapter_path": None,
             "content": c["text"][:PREVIEW_LEN], "char_count": len(c["text"])}
            for i, c in enumerate(chunks)]
    requests.delete(f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{book_id}",
                    headers={"apikey": KEY, "Authorization": f"Bearer {KEY}"}, timeout=30)
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
            f.write(json.dumps({"chunk_index": i, "chunk_type": "page",
                                "page_number": c["page"], "chapter_path": None,
                                "content": c["text"]}, ensure_ascii=False) + "\n")
    return out


_r2_client = None
def _r2():
    global _r2_client
    if _r2_client is None:
        import boto3
        _r2_client = boto3.client("s3", region_name="auto",
                                  endpoint_url=ENV["R2_ENDPOINT"],
                                  aws_access_key_id=ENV["R2_ACCESS_KEY"],
                                  aws_secret_access_key=ENV["R2_SECRET_KEY"])
    return _r2_client


def push_to_r2(book_id, jsonl_path):
    raw = Path(jsonl_path).read_bytes()
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=6) as gz:
        gz.write(raw)
    _r2().put_object(Bucket=ENV["R2_BUCKET"],
                     Key=f"ebook-chunks/{book_id}.jsonl.gz",
                     Body=buf.getvalue(),
                     ContentType="application/x-ndjson",
                     ContentEncoding="gzip")


# ── Haiku OCR core ────────────────────────────────────────────────

BATCH_PROMPT = """\
You are an academic OCR engine working on a digitization project for a
university library. The book is a scholarly publication (history,
philosophy, religion, literature). Extract the original printed text
EXACTLY as it appears — this is faithful transcription for archival
purposes, not authorship of new content. Historical, religious, or
academic discussions of any topic must be transcribed verbatim because
they are part of the published record being preserved.

Each image is one page (Chinese Traditional/Simplified or English).
For each page, output the visible text as written.

Output format — one block per page, exactly:
[PAGE {first}]
<extracted text>

[PAGE {next}]
<extracted text>

...and so on for every image in order.
If a page is blank or purely decorative, output its [PAGE N] header with an empty body.
Do not translate, summarize, censor, or add commentary — copy the printed text faithfully.
"""


_ANTHROPIC_IMAGE_MAX = 5 * 1024 * 1024   # 5 MB cap on the BASE64-encoded payload
# Base64 grows raw bytes by 4/3, so raw must be ≤ ~3.75 MB to stay under 5 MB
# encoded. Target 3.5 MB raw → ~4.67 MB base64 → 0.33 MB cushion.
_TARGET_IMG_BYTES = int(3.5 * 1024 * 1024)


def _render_page_image(doc, page_idx: int) -> tuple[bytes, str]:
    """Render a PDF page, guaranteeing the final bytes fit Anthropic's 5 MB cap.

    Strategy ladder (each step exits early once size ≤ 4 MB target):
      Pass 1: PNG at 150 → 120 → 100 → 85 → 72 DPI (lossless preferred)
      Pass 2: JPEG at 120 DPI, quality 85 → 75 → 65 → 55
      Pass 3: JPEG at 72 DPI, quality 70 → 50 → 40
      Pass 4: JPEG at 60/48/36/24 DPI, quality 50 → 40 → 30 (huge poster-format pages)
      Final:  whatever 24 DPI JPEG quality 20 produces — readable enough for OCR
              and small enough to fit any reasonable page.

    Returns (bytes, media_type) — 'image/png' or 'image/jpeg'."""
    page = doc[page_idx]
    # Pass 1: PNG ladder
    for dpi in (DPI, 120, 100, 85, 72):
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
        png = pix.tobytes("png")
        if len(png) <= _TARGET_IMG_BYTES:
            return png, "image/png"
    # Pass 2: JPEG @ 120 DPI
    mat = fitz.Matrix(120 / 72, 120 / 72)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
    for q in (85, 75, 65, 55):
        jpg = pix.tobytes("jpeg", jpg_quality=q)
        if len(jpg) <= _TARGET_IMG_BYTES:
            return jpg, "image/jpeg"
    # Pass 3: JPEG @ 72 DPI
    mat = fitz.Matrix(72 / 72, 72 / 72)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
    for q in (70, 50, 40):
        jpg = pix.tobytes("jpeg", jpg_quality=q)
        if len(jpg) <= _TARGET_IMG_BYTES:
            return jpg, "image/jpeg"
    # Pass 4: keep cutting DPI until it fits
    for dpi in (60, 48, 36, 24):
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
        for q in (50, 40, 30):
            jpg = pix.tobytes("jpeg", jpg_quality=q)
            if len(jpg) <= _TARGET_IMG_BYTES:
                return jpg, "image/jpeg"
    # Final: tiny image — only triggers on absurd page sizes (giant fold-outs)
    mat = fitz.Matrix(24 / 72, 24 / 72)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
    return pix.tobytes("jpeg", jpg_quality=20), "image/jpeg"


def _render_page_png(doc, page_idx: int) -> bytes:
    """Backward-compat wrapper. Returns just the bytes (assume PNG); callers
    that need media_type should use _render_page_image directly."""
    img, _ = _render_page_image(doc, page_idx)
    return img


def _parse_batch_response(text: str, page_numbers: list) -> list:
    """Trust the PDF page numbers (page_numbers, in render order), not the [PAGE N]
    markers Haiku writes — Haiku sometimes echoes the book's printed pagination
    from the images (e.g. roman numerals, page 821) instead of our requested numbers."""
    # Drop the preamble before the first [PAGE N], then split bodies by marker.
    segments = re.split(r'\[PAGE\s+\d+\]', text)
    bodies = [s.strip() for s in segments[1:]]
    chunks = []
    for j, pn in enumerate(page_numbers):
        body = bodies[j] if j < len(bodies) else ""
        chunks.append({"page": pn, "text": body})
    return chunks


def ocr_book(client: anthropic.Anthropic, src_path: Path, batch_size: int):
    """Returns (chunks, pdf_total_pages). pdf_total_pages is the authoritative
    page count from PyMuPDF — used for total_pages metadata so Haiku can't
    mislabel it via odd [PAGE N] markers."""
    doc = fitz.open(src_path)
    total = len(doc)
    all_chunks = []
    for batch_start in range(0, total, batch_size):
        batch_end = min(batch_start + batch_size, total)
        page_indices = list(range(batch_start, batch_end))
        page_numbers = [i + 1 for i in page_indices]

        content = []
        for pi in page_indices:
            img, media_type = _render_page_image(doc, pi)
            b64 = base64.standard_b64encode(img).decode()
            content.append({"type": "image",
                             "source": {"type": "base64", "media_type": media_type, "data": b64}})
        prompt = BATCH_PROMPT.format(
            first=page_numbers[0],
            next=page_numbers[1] if len(page_numbers) > 1 else page_numbers[0] + 1,
        )
        content.append({"type": "text", "text": prompt})

        resp = client.messages.create(
            model=MODEL, max_tokens=4096,
            messages=[{"role": "user", "content": content}],
        )
        batch_text = resp.content[0].text if resp.content else ""
        batch_chunks = _parse_batch_response(batch_text, page_numbers)
        all_chunks.extend(batch_chunks)
        print(f"    pages {batch_start+1}-{batch_end}/{total}: {len(batch_chunks)} parsed", flush=True)

    doc.close()
    return all_chunks, total


def _run_standardize(book_id: str) -> None:
    """After successful OCR, run Plan A (lite) then Plan B (TOC chapter chunking).
    Plan B may skip (no usable TOC) — that's OK, book stays on Plan A output.
    All errors are logged but don't fail the OCR pipeline."""
    try:
        import standardize_pdf_lite as _spl
        n, err = _spl.standardize_one(book_id)
        if err:
            print(f"  ⚠ Plan A: {err[:120]}")
        else:
            print(f"  ◆ Plan A: {n} chunks (s2tw + spacing + metadata)")
    except Exception as e:
        print(f"  ⚠ Plan A crashed: {str(e)[:120]}")
        return  # don't try Plan B if Plan A blew up

    try:
        import standardize_pdf as _spdf
        n, err = _spdf.standardize_one(book_id)
        if err:
            # "skipped: ..." is the common path (no TOC); not really a failure
            tag = "skipped" if err.startswith("skipped:") else "fail"
            print(f"  ◆ Plan B: {tag} ({err[:80]})")
        else:
            print(f"  ◆ Plan B: {n} chapter chunks")
    except Exception as e:
        print(f"  ⚠ Plan B crashed: {str(e)[:120]}")


def _is_transient_net(err_str: str) -> bool:
    s = err_str.lower()
    return any(k in s for k in (
        "connection error", "connection reset", "connection refused",
        "nameresolutionerror", "getaddrinfo", "timeout", "max retries exceeded",
        "temporarily unavailable", "503", "502", "504",
    ))


def process_one(client, book: dict, src_path: Path, batch_size: int, max_retries: int = 4) -> dict:
    last_err = ""
    for attempt in range(1, max_retries + 1):
        try:
            t0 = time.time()
            chunks, pdf_total_pages = ocr_book(client, src_path, batch_size)
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
                                 total_pages=pdf_total_pages)
                # Run standardize-pdf pipeline (Plan A + Plan B) automatically
                _run_standardize(book["id"])
                return {"status": "ok"}
            else:
                update_book_error(book["id"], f"OCR ok but R2 push failed: {r2_err}")
                return {"status": "fail", "error": f"R2: {r2_err}", "transient": True}

        except anthropic.RateLimitError:
            last_err = "rate limit"
            wait = min(2 ** attempt * 10, 120)
            print(f"  ↻ rate limit, retry {attempt} after {wait}s")
            time.sleep(wait)
        except anthropic.APIStatusError as e:
            last_err = str(e)[:300]
            if e.status_code in (529, 503, 502):
                wait = min(2 ** attempt * 10, 120)
                print(f"  ↻ API {e.status_code}, retry {attempt} after {wait}s")
                time.sleep(wait)
            elif e.status_code == 401:
                # OAuth token rotated mid-run. Reload from .credentials.json
                # and rebuild the client; retry the same book.
                print(f"  ↻ 401 auth — reloading OAuth token and retrying", flush=True)
                try:
                    client = make_client()
                except Exception as me:
                    print(f"  ❌ token reload failed: {me}", file=sys.stderr)
                    return {"status": "fail", "error": last_err, "transient": True}
                time.sleep(2)
            else:
                # 400 with "content filtering" → keep in queue (re-run might succeed
                # with refined prompt, or with smaller batch isolating offending page).
                if "content filtering" in last_err.lower() or "content_filter" in last_err.lower():
                    print(f"  ↻ content filter triggered, leaving in queue")
                    return {"status": "fail", "error": last_err, "transient": True}
                # Other permanent API errors (e.g. malformed request) — don't retry
                print(f"  ❌ {last_err[:200]}")
                return {"status": "fail", "error": last_err, "transient": False}
        except Exception as e:
            last_err = str(e)[:300]
            if _is_transient_net(last_err) and attempt < max_retries:
                wait = min(2 ** attempt * 10, 120)
                print(f"  ↻ network error, retry {attempt} after {wait}s ({last_err[:80]})")
                time.sleep(wait)
                continue
            print(f"  ❌ {last_err[:200]}")
            return {"status": "fail", "error": last_err,
                    "transient": _is_transient_net(last_err)}

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


def cmd_run(limit=None, batch=DEFAULT_BATCH, one_id=None, dry_run=False):
    # Build a *function* that returns a fresh client. Long OCR runs (hours)
    # outlast OAuth tokens — Claude Code refreshes ~/.claude/.credentials.json
    # every ~hour, so reading the file once at startup leaves us holding a
    # stale token. Reload before each book.
    client = make_client()

    if one_id:
        r = requests.get(f"{URL}/rest/v1/ebooks?id=eq.{one_id}&select=id,title,file_path",
                         headers={"apikey": KEY, "Authorization": f"Bearer {KEY}"}, timeout=30)
        targets = r.json()
        if not targets:
            print(f"❌ ebook {one_id} not found")
            return
    else:
        targets = fetch_ocr_targets()
        if limit:
            targets = targets[:limit]

    print(f"OCR targets: {len(targets)}  model={MODEL}  batch={batch} pages/call")
    if dry_run:
        for b in targets[:20]:
            print(f"  {b['title'][:60]}")
        return

    ok, failed = 0, []
    for i, b in enumerate(targets, 1):
        src = Path(b["file_path"])
        if not src.exists():
            print(f"  [{i:3d}/{len(targets)}] ⚠ source missing: {src}", file=sys.stderr)
            update_book_error(b["id"], f"file not found: {src}")
            failed.append((b["title"], "source missing"))
            continue

        sz_mb = src.stat().st_size / 1024 / 1024
        title_short = (b["title"] or src.stem)[:40]
        print(f"\n  [{i:3d}/{len(targets)}] OCR  {title_short}  ({sz_mb:.1f} MB)…", flush=True)

        # Re-read the OAuth token before each book so refreshes mid-run pick up.
        try:
            client = make_client()
        except Exception as e:
            print(f"  ❌ failed to refresh client: {e}", file=sys.stderr)

        result = process_one(client, b, src, batch)
        if result["status"] == "ok":
            ok += 1
            print(f"  → ✓ 完成，繼續下一本", flush=True)
        else:
            failed.append((b["title"], result["error"]))
            if not result["transient"]:
                update_book_error(b["id"], result["error"])

    print(f"\nDone. OK: {ok}, Failed: {len(failed)}")
    if failed:
        for n, e in failed[:10]:
            print(f"  - {n[:50]}  {e[:80]}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    args = sys.argv[2:]
    if cmd == "status":
        cmd_status()
    elif cmd == "run":
        limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None
        batch = int(args[args.index("--batch") + 1]) if "--batch" in args else DEFAULT_BATCH
        one_id = args[args.index("--one") + 1] if "--one" in args else None
        cmd_run(limit=limit, batch=batch, one_id=one_id, dry_run="--dry-run" in args)
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)
