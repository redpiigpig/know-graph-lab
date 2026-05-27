#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR scanned PDFs via Gemini Vision API, with automatic Haiku fallback.

Targets ebooks where parse_error LIKE '%no extractable text%'.
For each book:
  1. Upload PDF to Gemini Files API
  2. Request structured JSON output: {pages: [{page: N, text: "..."}]}
  3. Write JSONL to local _chunks/{id}.jsonl + 200-char preview to DB
  4. Mark parsed_at, clear parse_error

Fallback: when all Gemini keys hit 429 quota, the script automatically switches
to Claude Haiku (via ANTHROPIC_API_KEY). Haiku processes one book at a time,
printing "完成" confirmation before moving to the next book.

Idempotent: skips books with parsed_at NOT NULL.

Usage:
  python scripts/ocr_with_gemini.py status
  python scripts/ocr_with_gemini.py run [--limit N] [--model gemini-2.5-flash] [--rpm 4]
    [--book <ebook_id>]      # target only these books (repeatable)
    [--exclude <ebook_id>]   # skip these books (repeatable)
    [--engine gemini|haiku]  # default gemini; 'haiku' makes Haiku PRIMARY for every book in the
                             # filtered queue (Gemini is skipped entirely). Used when specific
                             # books are known-Gemini-only (e.g. Haiku content-filter rejects)
                             # so the user can split the queue: Gemini for those 2 + Haiku for rest.
"""
import gzip
import io
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path
from datetime import datetime

try:
    import json_repair as _json_repair
    _HAS_JSON_REPAIR = True
except ImportError:
    _HAS_JSON_REPAIR = False

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Missing: pip install google-genai", file=sys.stderr)
    sys.exit(1)

try:
    import anthropic as _anthropic
    _HAS_ANTHROPIC = True
except ImportError:
    _HAS_ANTHROPIC = False

try:
    import fitz as _fitz
    _HAS_FITZ = True
except ImportError:
    _HAS_FITZ = False

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
DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_RPM = 4  # under 10 RPM limit on flash, gentler on the service

def _find_gemini_keys() -> list[str]:
    """Return ALL configured Gemini keys (in priority order, dedup'd).

    Supports two formats interchangeably:
      - Comma-separated single var:  Gemini_API_Key=key1,key2,key3
      - Numbered vars:               Gemini_API_Key, GEMINI_API_KEY_2, GEMINI_API_KEY_3
    Either casing accepted. The free-tier daily quota is per-key, so
    rotating keys lets the OCR run keep going past one key's limit
    without waiting until the next-day reset."""
    raw_values: list[str] = []
    primary_names = ("GEMINI_API_KEY", "Gemini_API_Key", "gemini_api_key", "GOOGLE_API_KEY")
    # Primary slot (no number suffix)
    for name in primary_names:
        v = os.environ.get(name) or ENV.get(name)
        if v:
            raw_values.append(v); break
    # Numbered slots — _1 through _10 (some users start at _1, some skip
    # straight to _2 because the primary slot already covers "first key")
    for n in range(1, 11):
        for base in primary_names:
            v = os.environ.get(f"{base}_{n}") or ENV.get(f"{base}_{n}")
            if v:
                raw_values.append(v); break

    # Split each raw value on comma (in case the user put multiple keys
    # in one slot) and dedupe while preserving order.
    keys: list[str] = []
    seen = set()
    for raw in raw_values:
        for piece in raw.split(","):
            k = piece.strip()
            if k and k not in seen:
                seen.add(k); keys.append(k)
    return keys


API_KEYS = _find_gemini_keys()
API_KEY = API_KEYS[0] if API_KEYS else None  # kept for backward compat


def fetch_ocr_targets(sort_by_size=True):
    """Books that failed with 'no extractable text' (scanned PDFs).
    When sort_by_size=True, smallest files first (cheaper retries, faster feedback)."""
    out = []
    offset = 0
    page_size = 1000
    while True:
        params = (
            f"select=id,title,author,file_type,file_path,parse_error"
            f"&parse_error=ilike.*no extractable text*"
            f"&order=id&limit={page_size}&offset={offset}"
        )
        r = requests.get(f"{URL}/rest/v1/ebooks?{params}",
                         headers={"apikey": KEY, "Authorization": f"Bearer {KEY}"},
                         timeout=30)
        r.raise_for_status()
        page = r.json()
        if not page:
            break
        out.extend(page)
        if len(page) < page_size:
            break
        offset += page_size

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
    # Tolerant of network blips — Supabase DNS can flap mid-run and a
    # transient hiccup here shouldn't kill the entire OCR batch.
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
    """Bulk-insert preview-only rows into ebook_chunks. Adaptive batching
    (50→20→5→1) survives Supabase 57014 statement-timeout spikes — without
    it, a transient IO blip after a 30-minute Haiku OCR run discards the
    book entirely."""
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
    # Delete existing chunks for this book first (in case of retry)
    requests.delete(
        f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{book_id}",
        headers={"apikey": KEY, "Authorization": f"Bearer {KEY}"},
        timeout=30,
    )
    BATCH_SIZES = [50, 20, 5, 1]
    i = 0
    while i < len(rows):
        for bs in BATCH_SIZES:
            batch = rows[i:i + bs]
            r = requests.post(
                f"{URL}/rest/v1/ebook_chunks",
                headers=H,
                json=batch,
                timeout=120,
            )
            if r.status_code in (200, 201):
                i += len(batch)
                break
            text = r.text[:300]
            if "57014" in text or "timeout" in text.lower() or r.status_code >= 500:
                if bs > BATCH_SIZES[-1]:
                    continue
            raise RuntimeError(f"chunk insert failed: {r.status_code} {text[:200]}")
        else:
            raise RuntimeError(f"chunk insert failed at batch_size=1, row {i}")


def write_jsonl(book_id, chunks):
    """Write full text to local JSONL (same shape as parse_worker). Returns path."""
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


# ── R2 upload (lazy client) ────────────────────────────────────
_r2_client = None
def _r2():
    global _r2_client
    if _r2_client is None:
        try:
            import boto3
        except ImportError:
            print("Missing boto3. Run: pip install boto3", file=sys.stderr)
            raise
        _r2_client = boto3.client(
            "s3",
            region_name="auto",
            endpoint_url=ENV["R2_ENDPOINT"],
            aws_access_key_id=ENV["R2_ACCESS_KEY"],
            aws_secret_access_key=ENV["R2_SECRET_KEY"],
        )
    return _r2_client


def push_to_r2(book_id, jsonl_path):
    """Gzip the JSONL and upload to r2://{R2_BUCKET}/ebook-chunks/{id}.jsonl.gz.
    Idempotent: re-running overwrites. Raises on failure (caller decides)."""
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


PAGES_SCHEMA = {
    "type": "object",
    "properties": {
        "pages": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "page": {"type": "integer"},
                    "text": {"type": "string"},
                },
                "required": ["page", "text"],
            },
        },
    },
    "required": ["pages"],
}


def is_transient(err_str: str) -> bool:
    """5xx, rate limits, deadline-exceeded — leave parse_error untouched and retry later."""
    low = err_str.lower()
    return any(k in low for k in (
        "503", "502", "504", "500",
        "unavailable", "deadline_exceeded", "internal",
        "rate limit", "quota", "resource_exhausted", "429",
        "timeout", "connection", "temporarily",
    ))


def is_quota_stop(err_str: str) -> bool:
    """Daily/RPM cap reached — stop the whole run."""
    low = err_str.lower()
    return any(k in low for k in ("quota", "resource_exhausted", "429"))


def is_gemini_oversized(err_str: str) -> bool:
    """Gemini Files API rejects PDFs > 1000 pages. Haiku image-batch path
    is not subject to this cap — caller should fall back per-book."""
    low = err_str.lower()
    return ("exceeds the supported page limit" in low
            or "page limit of 1000" in low)


_HAIKU_MODEL = "claude-haiku-4-5-20251001"
_HAIKU_PAGES_PER_BATCH = 10
_HAIKU_DPI = 150
# Dense bilingual pages (Latin + Chinese, e.g. Denzinger 中譯) can have
# ~2-3K chars each. 10 pages × 2500 chars ≈ 25K chars ≈ 8K tokens output.
# Old 4096 was way too small → truncated mid-batch, 1629 pages lost on Denzinger
# until detected. Raise to 32K (Haiku 4.5 supports up to 64K). For short books
# (English-only, 1-2K chars/page), output won't approach this anyway.
_HAIKU_MAX_TOKENS = 32000
_HAIKU_BATCH_PROMPT = """\
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


def _haiku_render_page(doc, page_idx: int) -> tuple[bytes, str]:
    """Render page to bytes ≤ 5 MB (Anthropic image size limit). Tries JPEG at
    progressively lower DPI until under cap. Returns (bytes, media_type)."""
    page = doc[page_idx]
    HAIKU_IMAGE_MAX = 5_000_000  # 5 MB Anthropic cap (with margin)
    for dpi in (_HAIKU_DPI, 120, 96, 75, 60):
        mat = _fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat, colorspace=_fitz.csRGB)
        data = pix.tobytes("jpeg", jpg_quality=85)
        if len(data) <= HAIKU_IMAGE_MAX:
            return data, "image/jpeg"
    # Last resort — return whatever we got at 60 DPI even if oversized
    return data, "image/jpeg"


def _haiku_parse_response(text: str, page_numbers: list) -> list:
    """Parse Haiku's `[PAGE N]\\n<text>` blocks.

    **Important** — Haiku's `[PAGE N]` value is sometimes the book-internal
    pagination it reads from the page image (e.g. printed page 727, DH number
    3193 in margin), NOT the PDF page index we asked for. So we IGNORE the
    number in the marker and match text blocks to `page_numbers[]` by ORDER.
    The original Haiku-reported number is kept as `haiku_page_reported` for
    debugging.
    """
    import re
    parts = re.split(r'\[PAGE\s+(\d+)\]', text)
    # parts: [pre, num_1, body_1, num_2, body_2, ...]
    text_blocks: list[tuple[str, str]] = []  # (reported_num, body)
    for i in range(1, len(parts) - 1, 2):
        text_blocks.append((parts[i], parts[i + 1].strip()))

    chunks = []
    # Match by ORDER to expected page_numbers; ignore Haiku's reported number for
    # the canonical `page` field (which must be a real PDF index).
    for j, pn in enumerate(page_numbers):
        if j < len(text_blocks):
            reported, body = text_blocks[j]
            chunk = {"page": pn, "text": body}
            if reported and reported != str(pn):
                chunk["haiku_page_reported"] = reported
            chunks.append(chunk)
        else:
            # Haiku returned fewer blocks than pages — pad with empty
            chunks.append({"page": pn, "text": ""})
    return chunks


def _haiku_ocr_book(haiku_client, src_path: Path, book_id: str = None) -> list:
    """OCR a PDF book with Haiku, batch by batch.

    Checkpoint: writes each batch's chunks to `_chunks/{book_id}.batch_ckpt.jsonl`
    immediately after success, so a mid-book Cloudflare/network failure can resume
    from the last completed batch on next run instead of redoing everything.

    Per-batch retry: 5 attempts with exponential backoff (10/20/40/80/160s) on
    transient errors (Cloudflare 520, connection drops, brief 429s).
    """
    import base64
    doc = _fitz.open(src_path)
    total = len(doc)

    # ── CHECKPOINT: resume tracked by BATCH INDEX (not page numbers, which can
    # be unreliable since Haiku sometimes echoes book-internal pagination) ──
    ckpt_path = CHUNKS_DIR / f"{book_id}.batch_ckpt.jsonl" if book_id else None
    batch_idx_path = CHUNKS_DIR / f"{book_id}.batch_idx.txt" if book_id else None
    all_chunks: list = []
    done_batches: set = set()
    if ckpt_path and ckpt_path.exists():
        try:
            with ckpt_path.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        c = json.loads(line)
                        all_chunks.append(c)
                    except json.JSONDecodeError:
                        pass
        except OSError as e:
            print(f"    [haiku] checkpoint read error: {e}; starting fresh", flush=True)
    if batch_idx_path and batch_idx_path.exists():
        try:
            with batch_idx_path.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.isdigit():
                        done_batches.add(int(line))
            if done_batches:
                print(f"    [haiku] resume: {len(done_batches)} batches done "
                      f"(max batch_idx {max(done_batches)}, {len(all_chunks)} chunks)",
                      flush=True)
        except OSError as e:
            print(f"    [haiku] batch_idx read error: {e}; starting fresh", flush=True)

    ckpt_f = None
    batch_idx_f = None
    if ckpt_path:
        CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
        ckpt_f = ckpt_path.open("a", encoding="utf-8")
    if batch_idx_path:
        batch_idx_f = batch_idx_path.open("a", encoding="utf-8")

    print(f"\n    [haiku] {total} pages, batching {_HAIKU_PAGES_PER_BATCH}/call",
          flush=True)
    n_batches = (total + _HAIKU_PAGES_PER_BATCH - 1) // _HAIKU_PAGES_PER_BATCH
    t_book_start = time.time()
    try:
        for bi, batch_start in enumerate(range(0, total, _HAIKU_PAGES_PER_BATCH), 1):
            batch_end = min(batch_start + _HAIKU_PAGES_PER_BATCH, total)
            page_indices = list(range(batch_start, batch_end))
            page_numbers = [i + 1 for i in page_indices]

            # Skip whole batch if this batch_index already marked done
            if bi in done_batches:
                print(f"    [haiku] batch {bi}/{n_batches} pp{page_numbers[0]}-{page_numbers[-1]} "
                      f"SKIP (batch_idx checkpoint)", flush=True)
                continue

            t_b = time.time()
            content = []
            for pi in page_indices:
                img_bytes, media_type = _haiku_render_page(doc, pi)
                b64 = base64.standard_b64encode(img_bytes).decode()
                content.append({"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}})
            t_render = time.time() - t_b
            prompt = _HAIKU_BATCH_PROMPT.format(
                first=page_numbers[0],
                next=page_numbers[1] if len(page_numbers) > 1 else page_numbers[0] + 1,
            )
            content.append({"type": "text", "text": prompt})

            # Per-batch retry: 8 attempts with exponential backoff capped at 600s.
            # Schedule: 10/20/40/80/160/320/600/600 → ~21 min worst-case waste
            # but rides through Cloudflare hiccups that >2 min outage.
            # 401 (token expired) → call _refresh_oauth_token() + re-init client
            # immediately, don't waste exponential backoff on a doomed call.
            resp = None
            t_api = time.time()
            last_err = None
            MAX_BATCH_ATTEMPTS = 8
            for attempt in range(1, MAX_BATCH_ATTEMPTS + 1):
                try:
                    resp = haiku_client.messages.create(
                        model=_HAIKU_MODEL,
                        max_tokens=_HAIKU_MAX_TOKENS,
                        messages=[{"role": "user", "content": content}],
                    )
                    break
                except Exception as e:  # noqa: BLE001 — catch all Anthropic transient errors
                    last_err = e
                    msg = str(e)[:120]
                    is_401 = getattr(e, "status_code", None) == 401 or "401" in str(e)[:200]
                    if is_401:
                        # Token expired — refresh + rebuild client, retry immediately
                        print(f"    [haiku] batch {bi} attempt {attempt}/{MAX_BATCH_ATTEMPTS} got 401, refreshing OAuth token", flush=True)
                        _refresh_oauth_token()
                        try:
                            haiku_client = _make_anthropic_client(proactive_refresh=False)
                            print(f"    [haiku] batch {bi} client rebuilt with fresh token, retrying", flush=True)
                            continue  # retry without sleep
                        except Exception as ce:
                            print(f"    [haiku] batch {bi} client rebuild failed: {ce}", flush=True)
                    if attempt == MAX_BATCH_ATTEMPTS:
                        # exhausted retries — re-raise to outer handler
                        raise
                    # Capped exponential backoff: 10, 20, 40, 80, 160, 320, 600, 600
                    wait_s = min(10 * (2 ** (attempt - 1)), 600)
                    print(f"    [haiku] batch {bi} attempt {attempt}/{MAX_BATCH_ATTEMPTS} failed: {msg}; "
                          f"retry in {wait_s}s", flush=True)
                    time.sleep(wait_s)

            t_api_dur = time.time() - t_api
            batch_text = resp.content[0].text if resp.content else ""
            chunks = _haiku_parse_response(batch_text, page_numbers)
            all_chunks.extend(chunks)

            # Persist batch to checkpoint immediately (resume safety)
            if ckpt_f:
                for c in chunks:
                    ckpt_f.write(json.dumps(c, ensure_ascii=False) + "\n")
                ckpt_f.flush()
            # Mark batch as done by index (the source of truth for resume)
            if batch_idx_f:
                batch_idx_f.write(f"{bi}\n")
                batch_idx_f.flush()

            elapsed = time.time() - t_book_start
            eta = (elapsed / bi) * (n_batches - bi) if bi else 0
            print(f"    [haiku] batch {bi}/{n_batches} pp{page_numbers[0]}-{page_numbers[-1]} "
                  f"render={t_render:.1f}s api={t_api_dur:.1f}s pages={len(chunks)} "
                  f"elapsed={elapsed/60:.1f}m eta={eta/60:.1f}m",
                  flush=True)
    finally:
        if ckpt_f:
            ckpt_f.close()
        if batch_idx_f:
            batch_idx_f.close()
        doc.close()
    return all_chunks


# Claude Code OAuth refresh endpoint (public — same client_id as the CLI)
_CC_OAUTH_REFRESH_URL = "https://console.anthropic.com/v1/oauth/token"
_CC_OAUTH_CLIENT_ID = "9d1c250a-e61b-44d9-88ed-5944d1962f5e"


def _credentials_path() -> Path:
    return Path(os.environ.get("USERPROFILE", os.environ.get("HOME", ""))) / ".claude" / ".credentials.json"


def _refresh_oauth_token(verbose: bool = True) -> str | None:
    """Refresh Claude Code OAuth access_token via the refresh_token grant.

    Reads .credentials.json → POSTs to console.anthropic.com/v1/oauth/token →
    writes new access_token / refresh_token / expiresAt back. Returns the new
    access_token, or None on failure.
    """
    cred = _credentials_path()
    if not cred.exists():
        if verbose:
            print(f"  [oauth-refresh] no credentials file at {cred}", flush=True)
        return None
    try:
        with cred.open(encoding="utf-8") as f:
            data = json.load(f)
        oauth = data.get("claudeAiOauth", {})
        refresh_tok = oauth.get("refreshToken")
        if not refresh_tok:
            if verbose:
                print(f"  [oauth-refresh] no refreshToken in credentials", flush=True)
            return None

        resp = requests.post(
            _CC_OAUTH_REFRESH_URL,
            headers={"Content-Type": "application/json", "User-Agent": "anthropic"},
            json={
                "grant_type": "refresh_token",
                "refresh_token": refresh_tok,
                "client_id": _CC_OAUTH_CLIENT_ID,
            },
            timeout=30,
        )
        if not resp.ok:
            if verbose:
                print(f"  [oauth-refresh] HTTP {resp.status_code}: {resp.text[:200]}", flush=True)
            return None

        body = resp.json()
        new_access = body.get("access_token")
        new_refresh = body.get("refresh_token") or refresh_tok
        expires_in = body.get("expires_in")  # seconds
        if not new_access:
            if verbose:
                print(f"  [oauth-refresh] response missing access_token: {body}", flush=True)
            return None

        # Persist back to credentials.json
        oauth["accessToken"] = new_access
        oauth["refreshToken"] = new_refresh
        if expires_in:
            oauth["expiresAt"] = int(time.time() * 1000) + int(expires_in) * 1000
        data["claudeAiOauth"] = oauth
        with cred.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        if verbose:
            exp_min = (oauth["expiresAt"] - int(time.time() * 1000)) / 60000 if "expiresAt" in oauth else None
            exp_str = f", expires in {exp_min:.0f}min" if exp_min else ""
            print(f"  [oauth-refresh] ✓ token refreshed{exp_str}", flush=True)
        return new_access
    except Exception as e:
        if verbose:
            print(f"  [oauth-refresh] exception: {e}", flush=True)
        return None


def _make_anthropic_client(proactive_refresh: bool = True):
    """Create anthropic.Anthropic using API key or Claude Code's OAuth token.

    Proactive refresh: if expiresAt is within 5 minutes (or past), auto-call the
    OAuth refresh endpoint before initializing the client. This lets the OCR run
    survive past the 8-hour token lifetime without external intervention.

    10-min timeout + 2 retries — without timeout SDK hangs indefinitely on stuck socket,
    OCR run becomes zombie burning RAM (踩過坑 2026-05-19，batch 36 卡 7+ hours)."""
    common_kwargs = {"timeout": 600.0, "max_retries": 2}
    api_key = ENV.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return _anthropic.Anthropic(api_key=api_key, **common_kwargs)

    # Fall back to Claude Code's stored OAuth token
    cred_path = _credentials_path()
    if not cred_path.exists():
        raise RuntimeError("No Anthropic credentials found. Add ANTHROPIC_API_KEY to .env or sign in to Claude Code.")

    try:
        with cred_path.open(encoding="utf-8") as f:
            creds = json.load(f)
        oauth = creds.get("claudeAiOauth", {})
        token = oauth.get("accessToken", "")
        expires_at = oauth.get("expiresAt", 0)  # millis
        now_ms = int(time.time() * 1000)

        # Proactive refresh: 5-min skew + already-expired
        if proactive_refresh and (expires_at <= now_ms + 300_000):
            new_tok = _refresh_oauth_token()
            if new_tok:
                token = new_tok

        if token:
            return _anthropic.Anthropic(auth_token=token, **common_kwargs)
    except Exception as e:
        print(f"  [oauth] read credentials error: {e}", flush=True)

    raise RuntimeError("No Anthropic credentials found. Add ANTHROPIC_API_KEY to .env or sign in to Claude Code.")


def process_one_haiku(haiku_client, book: dict, src_path: Path, max_retries: int = 2) -> dict:
    """OCR one book with Haiku. Returns same {status, error?, transient?} dict as process_one.

    _haiku_ocr_book uses batch-level checkpoint (book_id keyed) so transient
    Cloudflare 520 / network failures resume from last good batch on next call.
    On successful completion, the checkpoint file is deleted.
    """
    last_err = ""
    ckpt_path = CHUNKS_DIR / f"{book['id']}.batch_ckpt.jsonl"
    batch_idx_path = CHUNKS_DIR / f"{book['id']}.batch_idx.txt"
    for attempt in range(1, max_retries + 1):
        try:
            t0 = time.time()
            chunks = _haiku_ocr_book(haiku_client, src_path, book_id=book["id"])
            non_empty = [c for c in chunks if c.get("text", "").strip()]
            if not non_empty:
                return {"status": "fail", "error": "haiku returned 0 usable pages", "transient": False}

            total_chars = sum(len(c["text"]) for c in non_empty)
            jsonl_path = write_jsonl(book["id"], non_empty)
            insert_chunk_previews(book["id"], non_empty)

            r2_ok, r2_err = True, ""
            try:
                push_to_r2(book["id"], jsonl_path)
            except Exception as e:
                r2_ok, r2_err = False, str(e)[:200]

            elapsed = time.time() - t0
            tag = "✓ Haiku" if r2_ok else "⚠ Haiku R2 fail"
            print(f"  {tag} {len(non_empty)} pages, {total_chars // 1000}K chars, {elapsed:.0f}s")

            if r2_ok:
                update_book_done(book["id"], total_chars=total_chars,
                                 chunk_count=len(non_empty),
                                 total_pages=max(c["page"] for c in non_empty))
                # Success — clean up checkpoint files
                for p in (ckpt_path, batch_idx_path):
                    try:
                        p.unlink(missing_ok=True)
                    except OSError:
                        pass
                return {"status": "ok"}
            else:
                update_book_error(book["id"], f"OCR ok but R2 push failed: {r2_err}")
                return {"status": "fail", "error": f"R2: {r2_err}", "transient": True}

        except Exception as e:
            last_err = str(e)[:300]
            is_rate = hasattr(e, "status_code") and getattr(e, "status_code", 0) in (429, 529, 503, 502)
            if is_rate and attempt < max_retries:
                wait = min(2 ** attempt * 10, 120)
                print(f"  ↻ Haiku rate limit, retry {attempt} after {wait}s")
                time.sleep(wait)
                continue
            print(f"  ❌ Haiku {last_err[:200]}")
            print(f"     (checkpoint preserved at {ckpt_path.name} for resume)")
            return {"status": "fail", "error": last_err, "transient": is_rate}
    return {"status": "fail", "error": last_err, "transient": True}


def process_one(client, book, src_path, model, max_retries=3):
    """Run OCR on one book with retries. Returns dict {status, error?, transient?, stop?}."""
    title = (book["title"] or src_path.stem)[:40]
    last_err = ""
    for attempt in range(1, max_retries + 1):
        try:
            t_start = time.time()
            # Copy to ASCII-only temp path (genai SDK puts filename in HTTP headers)
            with tempfile.NamedTemporaryFile(
                prefix=f"ebook_{book['id']}_", suffix=".pdf", delete=False
            ) as tmp:
                tmp_path = Path(tmp.name)
            shutil.copyfile(src_path, tmp_path)
            try:
                uploaded = client.files.upload(
                    file=tmp_path,
                    config=types.UploadFileConfig(
                        display_name=f"ebook_{book['id']}.pdf",
                        mime_type="application/pdf",
                    ),
                )
            finally:
                try: tmp_path.unlink()
                except Exception: pass

            resp = client.models.generate_content(
                model=model,
                contents=[uploaded, PROMPT],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=PAGES_SCHEMA,
                ),
            )

            try: client.files.delete(name=uploaded.name)
            except Exception: pass

            try:
                data = json.loads(resp.text)
            except json.JSONDecodeError as json_err:
                # Gemini truncated the JSON (hit output token limit). Try to salvage
                # whatever complete page objects were emitted before the cut-off.
                if _HAS_JSON_REPAIR:
                    try:
                        data = _json_repair.loads(resp.text)
                        if not isinstance(data, dict):
                            data = {}
                        salvaged = len(data.get("pages", []))
                        if salvaged:
                            print(f"  ⚠ truncated JSON salvaged {salvaged} pages via json_repair")
                        else:
                            raise ValueError("json_repair returned 0 pages")
                    except Exception:
                        raise json_err
                else:
                    raise
            pages = data.get("pages", [])
            non_empty = [p for p in pages if isinstance(p, dict) and (p.get("text") or "").strip()]
            if not non_empty:
                # If model returned no usable text, this is permanent (OCR genuinely failed)
                return {"status": "fail", "error": "model returned 0 usable pages", "transient": False}

            total_chars = sum(len(p["text"]) for p in non_empty)
            jsonl_path = write_jsonl(book["id"], non_empty)
            insert_chunk_previews(book["id"], non_empty)

            # Push JSONL to R2 so the production frontend can read it.
            # If R2 fails, OCR work is preserved locally + DB; book stays marked
            # "not parsed" so the next run will redo it (cheap — no API call,
            # write_jsonl is overwrite-safe).
            r2_ok = True
            r2_err = ""
            try:
                push_to_r2(book["id"], jsonl_path)
            except Exception as e:
                r2_ok = False
                r2_err = str(e)[:200]

            if r2_ok:
                update_book_done(
                    book["id"],
                    total_chars=total_chars,
                    chunk_count=len(non_empty),
                    total_pages=max(p["page"] for p in non_empty),
                )
            else:
                update_book_error(book["id"], f"OCR ok but R2 push failed: {r2_err}")

            elapsed = time.time() - t_start
            tag = "✓" if r2_ok else "⚠ R2 fail"
            print(f"  {tag} {len(non_empty)} pages, {total_chars // 1000}K chars, {elapsed:.0f}s")
            return {"status": "ok"} if r2_ok else {"status": "fail", "error": f"R2: {r2_err}", "transient": True}

        except Exception as e:
            last_err = str(e)[:300]
            transient = is_transient(last_err)
            quota = is_quota_stop(last_err)
            if quota:
                print(f"  ❌ {last_err}")
                return {"status": "fail", "error": last_err, "transient": True, "stop": True}
            if transient and attempt < max_retries:
                wait = min(2 ** attempt * 5, 60)
                print(f"  ↻ retry {attempt}/{max_retries - 1} after {wait}s ({last_err[:80]})")
                time.sleep(wait)
                continue
            print(f"  ❌ {last_err[:200]}")
            return {"status": "fail", "error": last_err, "transient": transient}

    return {"status": "fail", "error": last_err, "transient": True}


PROMPT = """\
This PDF is a scanned book that may contain Chinese (Traditional or Simplified) and/or English text.

Extract the FULL text from EVERY page of this PDF. Output ONLY a JSON object with this shape:
{
  "pages": [
    {"page": 1, "text": "..."},
    {"page": 2, "text": "..."}
  ]
}

Rules:
- "page" is the 1-based PDF page number
- "text" is the complete extracted text for that page, preserving paragraph breaks with \\n
- Skip purely decorative pages but still include them with empty "text"
- DO NOT translate, summarize, or interpret. Output the original text only
- DO NOT add commentary, markdown, or wrapper text outside the JSON
"""


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
            print(f"  {b['title'][:50]}  {sz}")


def _is_quota_err(err_str: str) -> bool:
    """Recognize per-account quota / rate-limit messages. Reused by 2-strike pause."""
    low = (err_str or "").lower()
    return any(k in low for k in (
        "429", "rate_limit", "rate limit", "exceed your account",
        "quota", "resource_exhausted",
    ))


def _run_haiku_primary(targets, dry_run=False):
    """Run Haiku-only OCR on the given queue (no Gemini at all). One book at a time,
    matching the 5/7 incident lesson (parallel Haiku exhausts Max-subscription tokens).

    Per user rule: stop after 2 consecutive 429/rate-limit failures — burning
    through the queue with fast 429 rejections wastes nothing but emits noise."""
    if not _HAS_ANTHROPIC or not _HAS_FITZ:
        missing = []
        if not _HAS_ANTHROPIC: missing.append("anthropic")
        if not _HAS_FITZ: missing.append("pymupdf")
        print(f"❌ Haiku engine requires: pip install {' '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    if dry_run:
        for b in targets[:20]:
            print(f"  {b['title'][:60]}  ({b['file_path']})")
        return

    try:
        haiku_client = _make_anthropic_client()
    except RuntimeError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)

    ok = 0
    failed = []
    consecutive_quota = 0
    for i, b in enumerate(targets, 1):
        src = Path(b["file_path"])
        if not src.exists():
            print(f"  [H {i}/{len(targets)}] ⚠ source missing: {src}", file=sys.stderr)
            update_book_error(b["id"], f"file not found: {src}")
            failed.append((b["title"], "source missing"))
            continue
        sz_mb = src.stat().st_size / 1024 / 1024
        title_short = (b["title"] or src.stem)[:40]
        print(f"  [H {i}/{len(targets)}] OCR  {title_short}  ({sz_mb:.1f} MB)…",
              end="", flush=True)
        hresult = process_one_haiku(haiku_client, b, src)
        if hresult["status"] == "ok":
            ok += 1
            consecutive_quota = 0
            print(f"  → 完成，繼續下一本", flush=True)
        else:
            failed.append((b["title"], hresult["error"]))
            if not hresult["transient"]:
                update_book_error(b["id"], hresult["error"])
            if _is_quota_err(hresult.get("error", "")):
                consecutive_quota += 1
                if consecutive_quota >= 2:
                    print(f"\n⛔ Haiku quota hit twice in a row — pausing run (per user rule).", flush=True)
                    print(f"   Retry later when quota resets.", flush=True)
                    break
            else:
                consecutive_quota = 0
    print(f"\nDone. OK: {ok}, Failed: {len(failed)}")
    if failed:
        print("First failures:")
        for n, e in failed[:10]:
            print(f"  - {n[:50]}  {e[:100]}")


def cmd_run(limit=None, model=DEFAULT_MODEL, rpm=DEFAULT_RPM, dry_run=False,
            books=None, exclude=None, engine="gemini"):
    """engine: 'gemini' (default — Haiku only as quota-fallback) | 'haiku' (use Haiku as PRIMARY for every book in the queue, skip Gemini entirely)."""
    if engine == "gemini" and not API_KEYS:
        print("❌ Missing GEMINI_API_KEY. Get one at https://aistudio.google.com/app/apikey",
              file=sys.stderr)
        print("   Then add to .env:  GEMINI_API_KEY=key1,key2,key3  (comma for rotation)",
              file=sys.stderr)
        sys.exit(1)

    targets = fetch_ocr_targets()
    if books:
        book_set = set(books)
        targets = [b for b in targets if b["id"] in book_set]
        missing = book_set - {b["id"] for b in targets}
        if missing:
            print(f"⚠ --book ids not in OCR queue (already parsed, or wrong id): {missing}", file=sys.stderr)
    if exclude:
        excl_set = set(exclude)
        targets = [b for b in targets if b["id"] not in excl_set]
    print(f"OCR candidates: {len(targets)}  (engine={engine})")
    if engine == "gemini":
        print(f"Available Gemini keys: {len(API_KEYS)} (will rotate on quota)")
    if limit:
        targets = targets[:limit]

    if engine == "haiku":
        return _run_haiku_primary(targets, dry_run=dry_run)

    if dry_run:
        for b in targets[:20]:
            print(f"  {b['title'][:60]}  ({b['file_path']})")
        return

    # Key rotation state — start with first key, advance only when quota hit.
    key_idx = 0
    client = genai.Client(api_key=API_KEYS[key_idx])
    min_gap = 60.0 / rpm  # seconds between requests
    last_call = 0.0

    def try_next_key() -> bool:
        """Advance to the next available Gemini key. Returns True if we
        switched, False if all keys are exhausted."""
        nonlocal key_idx, client
        if key_idx + 1 >= len(API_KEYS):
            return False
        key_idx += 1
        client = genai.Client(api_key=API_KEYS[key_idx])
        print(f"  ⟳ Quota hit on key #{key_idx}; switched to key #{key_idx + 1} of {len(API_KEYS)}",
              flush=True)
        return True

    ok = 0
    failed = []
    quota_hit = False
    _haiku_lazy_client = None  # lazy init for inline Haiku fallback on oversized books
    consecutive_oversized_quota = 0  # 2-strike pause for oversized-Haiku fallback path
    for i, b in enumerate(targets, 1):
        src = Path(b["file_path"])
        if not src.exists():
            print(f"  [{i:3d}/{len(targets)}] ⚠ source missing: {src}", file=sys.stderr)
            update_book_error(b["id"], f"file not found: {src}")
            failed.append((b["title"], "source missing"))
            continue

        # Pre-flight: 0-byte files just trigger 400 INVALID_ARGUMENT on Gemini.
        # Mark permanent so they leave the OCR queue without burning an API call.
        try:
            fsize = src.stat().st_size
        except Exception:
            fsize = -1
        if fsize == 0:
            print(f"  [{i:3d}/{len(targets)}] ⚠ empty file (0 bytes): {src.name}", file=sys.stderr)
            update_book_error(b["id"], "OCR: source file is empty (0 bytes)")
            failed.append((b["title"], "empty file"))
            continue

        # Pre-flight: PDFs > 50 MB always 400 INVALID_ARGUMENT from Gemini Files API.
        # Skip Gemini entirely and route to Haiku image-batch path (no file-size cap).
        GEMINI_MAX_BYTES = 50 * 1024 * 1024
        if fsize > GEMINI_MAX_BYTES and _HAS_ANTHROPIC and _HAS_FITZ:
            title_short = (b["title"] or src.stem)[:40]
            print(f"  [{i:3d}/{len(targets)}] OCR  {title_short}  ({fsize/1024/1024:.1f} MB > 50, → Haiku)…",
                  end="", flush=True)
            try:
                if _haiku_lazy_client is None:
                    _haiku_lazy_client = _make_anthropic_client()
                hresult = process_one_haiku(_haiku_lazy_client, b, src)
                if hresult["status"] == "ok":
                    ok += 1
                    consecutive_oversized_quota = 0
                else:
                    failed.append((b["title"], hresult["error"]))
                    if _is_quota_err(hresult.get("error", "")):
                        consecutive_oversized_quota += 1
                    elif not hresult.get("transient"):
                        update_book_error(b["id"], f"OCR (Haiku >50MB): {hresult['error']}")
            except Exception as e:
                print(f"  ⚠ Haiku pre-route failed: {str(e)[:120]}", file=sys.stderr)
                failed.append((b["title"], f"Haiku pre-route: {str(e)[:120]}"))
            if consecutive_oversized_quota >= 2:
                print(f"\n⛔ Oversized-Haiku quota hit twice in a row — pausing run (per user rule).",
                      flush=True)
                break
            continue

        # Rate limit
        gap = time.time() - last_call
        if gap < min_gap:
            time.sleep(min_gap - gap)
        last_call = time.time()

        title_short = (b["title"] or src.stem)[:40]
        sz_mb = src.stat().st_size / 1024 / 1024
        print(f"  [{i:3d}/{len(targets)}] OCR  {title_short}  ({sz_mb:.1f} MB)…",
              end="", flush=True)

        result = process_one(client, b, src, model)
        # If quota'd, rotate keys and retry the SAME book once per remaining key.
        while result.get("status") != "ok" and result.get("stop"):
            if not try_next_key():
                quota_hit = True
                break
            last_call = time.time()
            result = process_one(client, b, src, model)

        # Gemini Files API has a 1000-page cap — books over that limit always
        # fail with 400 INVALID_ARGUMENT. Haiku image-batch path has no such cap.
        # Auto-fall back inline so >1000 page books don't get marked permanent.
        if (result.get("status") != "ok"
                and is_gemini_oversized(result.get("error", ""))
                and _HAS_ANTHROPIC and _HAS_FITZ):
            try:
                if _haiku_lazy_client is None:
                    _haiku_lazy_client = _make_anthropic_client()
                print(f"  → Gemini page-limit hit; trying Haiku for this book")
                hresult = process_one_haiku(_haiku_lazy_client, b, src)
                if hresult["status"] == "ok":
                    result = hresult
                    consecutive_oversized_quota = 0
                else:
                    # Haiku also failed (likely connection / rate-limit cooldown).
                    # Force the book transient so it stays in queue for next run —
                    # the Gemini 1000-page failure alone is permanent, but we don't
                    # want to mark permanent until Haiku has a fair chance.
                    result["transient"] = True
                    # 2-strike: a stuck Haiku quota will fail every oversized book
                    # in a row. Track the streak so we stop after 2.
                    if _is_quota_err(hresult.get("error", "")):
                        consecutive_oversized_quota += 1
                    else:
                        consecutive_oversized_quota = 0
            except Exception as e:
                print(f"  ⚠ Haiku fallback failed: {str(e)[:120]}", file=sys.stderr)
                result["transient"] = True

        if consecutive_oversized_quota >= 2:
            print(f"\n⛔ Oversized-Haiku quota hit twice in a row — pausing run (per user rule).",
                  flush=True)
            print(f"   Retry later when Anthropic quota resets.", flush=True)
            break

        if quota_hit:
            # All Gemini keys exhausted — fall back to Haiku for this book and the rest.
            print(f"\n⚠ All Gemini keys exhausted. Switching to Haiku fallback (one book at a time).")
            if not _HAS_ANTHROPIC or not _HAS_FITZ:
                missing = []
                if not _HAS_ANTHROPIC: missing.append("anthropic")
                if not _HAS_FITZ: missing.append("pymupdf")
                print(f"  ❌ Haiku fallback requires: pip install {' '.join(missing)}", file=sys.stderr)
                failed.append((b["title"], "all keys quota-exhausted"))
                break

            try:
                haiku_client = _make_anthropic_client()
            except RuntimeError as e:
                print(f"  ❌ {e}", file=sys.stderr)
                failed.append((b["title"], "all keys quota-exhausted"))
                break

            # Process the current book (that triggered the quota) plus all remaining books.
            remaining = [b] + targets[i:]  # targets[i:] already excludes processed books
            consecutive_quota = 0
            for j, hb in enumerate(remaining, 1):
                hsrc = Path(hb["file_path"])
                if not hsrc.exists():
                    print(f"  [H {j}/{len(remaining)}] ⚠ source missing: {hsrc}", file=sys.stderr)
                    update_book_error(hb["id"], f"file not found: {hsrc}")
                    failed.append((hb["title"], "source missing"))
                    continue

                sz_mb = hsrc.stat().st_size / 1024 / 1024
                title_short = (hb["title"] or hsrc.stem)[:40]
                print(f"\n  [H {j}/{len(remaining)}] OCR  {title_short}  ({sz_mb:.1f} MB)…",
                      end="", flush=True)

                hresult = process_one_haiku(haiku_client, hb, hsrc)
                if hresult["status"] == "ok":
                    ok += 1
                    consecutive_quota = 0
                    print(f"  → 完成，繼續下一本", flush=True)
                else:
                    failed.append((hb["title"], hresult["error"]))
                    if not hresult["transient"]:
                        update_book_error(hb["id"], hresult["error"])
                    if _is_quota_err(hresult.get("error", "")):
                        consecutive_quota += 1
                        if consecutive_quota >= 2:
                            print(f"\n⛔ Haiku quota hit twice in a row — pausing run (per user rule).",
                                  flush=True)
                            print(f"   Retry later when quota resets.", flush=True)
                            break
                    else:
                        consecutive_quota = 0
            break  # Haiku loop handled all remaining; exit the Gemini loop

        if result["status"] == "ok":
            ok += 1
            # Successful book = reset the oversized streak so a future
            # oversized-Haiku-429 isn't paired with one from before this win.
            consecutive_oversized_quota = 0
        else:
            err = result["error"]
            failed.append((b["title"], err))
            if not result["transient"]:
                update_book_error(b["id"], f"OCR: {err}")

    print(f"\nDone. OK: {ok}, Failed: {len(failed)}")
    if failed:
        print("First failures:")
        for n, e in failed[:10]:
            print(f"  - {n[:50]}  {e[:100]}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    args = sys.argv[2:]
    if cmd == "status":
        cmd_status()
    elif cmd == "run":
        limit = None
        if "--limit" in args:
            limit = int(args[args.index("--limit") + 1])
        model = DEFAULT_MODEL
        if "--model" in args:
            model = args[args.index("--model") + 1]
        rpm = DEFAULT_RPM
        if "--rpm" in args:
            rpm = float(args[args.index("--rpm") + 1])
        engine = "gemini"
        if "--engine" in args:
            engine = args[args.index("--engine") + 1]
            if engine not in ("gemini", "haiku"):
                print(f"❌ --engine must be 'gemini' or 'haiku', got {engine!r}", file=sys.stderr)
                sys.exit(1)
        books = []
        # --book can repeat
        i = 0
        while i < len(args):
            if args[i] == "--book" and i + 1 < len(args):
                books.append(args[i + 1])
                i += 2
            else:
                i += 1
        exclude = []
        i = 0
        while i < len(args):
            if args[i] == "--exclude" and i + 1 < len(args):
                exclude.append(args[i + 1])
                i += 2
            else:
                i += 1
        cmd_run(limit=limit, model=model, rpm=rpm, dry_run="--dry-run" in args,
                books=books or None, exclude=exclude or None, engine=engine)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
