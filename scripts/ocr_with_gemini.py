#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR scanned PDFs via Gemini Vision API.

Targets ebooks where parse_error LIKE '%no extractable text%' (~390 books).
For each book:
  1. Upload PDF to Gemini Files API
  2. Request structured JSON output: {pages: [{page: N, text: "..."}]}
  3. Write JSONL to local _chunks/{id}.jsonl + 200-char preview to DB
  4. Mark parsed_at, clear parse_error

Free-tier model picks (2.5 Flash, fallback 2.5 Flash-Lite):
  - gemini-2.5-flash:       10 RPM, 250 RPD, 250K TPM
  - gemini-2.5-flash-lite:  15 RPM, 1000 RPD

Idempotent: skips books with parsed_at NOT NULL. Resumable via parse_progress.

Usage:
  export GEMINI_API_KEY=...
  python scripts/ocr_with_gemini.py status
  python scripts/ocr_with_gemini.py run [--limit N] [--model gemini-2.5-flash] [--rpm 8]
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

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Missing: pip install google-genai", file=sys.stderr)
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
DEFAULT_MODEL = "gemini-2.5-pro"
DEFAULT_RPM = 4  # 2.5-pro free tier: 2 RPM; paid: 5+. 4 is conservative middle.

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
    requests.patch(
        f"{URL}/rest/v1/ebooks?id=eq.{book_id}",
        headers=H,
        json={"parse_error": msg[:500]},
        timeout=30,
    )


def insert_chunk_previews(book_id, chunks):
    """Bulk-insert preview-only rows into ebook_chunks. Same format as parse_worker."""
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
    # Insert in batches of 50
    batch = 50
    for i in range(0, len(rows), batch):
        r = requests.post(
            f"{URL}/rest/v1/ebook_chunks",
            headers=H,
            json=rows[i:i + batch],
            timeout=60,
        )
        if not r.ok:
            raise RuntimeError(f"chunk insert failed: {r.status_code} {r.text[:200]}")


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

            data = json.loads(resp.text)
            pages = data.get("pages", [])
            non_empty = [p for p in pages if (p.get("text") or "").strip()]
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


def cmd_run(limit=None, model=DEFAULT_MODEL, rpm=DEFAULT_RPM, dry_run=False):
    if not API_KEYS:
        print("❌ Missing GEMINI_API_KEY. Get one at https://aistudio.google.com/app/apikey",
              file=sys.stderr)
        print("   Then add to .env:  GEMINI_API_KEY=key1,key2,key3  (comma for rotation)",
              file=sys.stderr)
        sys.exit(1)

    targets = fetch_ocr_targets()
    print(f"OCR candidates: {len(targets)}")
    print(f"Available Gemini keys: {len(API_KEYS)} (will rotate on quota)")
    if limit:
        targets = targets[:limit]

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
    for i, b in enumerate(targets, 1):
        src = Path(b["file_path"])
        if not src.exists():
            print(f"  [{i:3d}/{len(targets)}] ⚠ source missing: {src}", file=sys.stderr)
            update_book_error(b["id"], f"file not found: {src}")
            failed.append((b["title"], "source missing"))
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
        # The book that triggered the quota is otherwise lost for this run.
        while result.get("status") != "ok" and result.get("stop"):
            if not try_next_key():
                print("⚠ All Gemini keys exhausted. Stopping. Re-run later.")
                quota_hit = True
                break
            # Reset the inter-call gap so the new key gets its first request promptly
            last_call = time.time()
            result = process_one(client, b, src, model)
        if quota_hit:
            failed.append((b["title"], "all keys quota-exhausted"))
            break

        if result["status"] == "ok":
            ok += 1
        else:
            err = result["error"]
            failed.append((b["title"], err))
            if result["transient"]:
                # Transient (non-quota) error — leave parse_error as-is so next run retries
                pass
            else:
                update_book_error(b["id"], f"OCR: {err}")

    print(f"\nDone. OK: {ok}, Failed: {len(failed)}")
    if failed:
        print("First failures:")
        for n, e in failed[:10]:
            print(f"  - {n[:50]}  {e[:100]}")
    # Exit code 2 = quota exhausted; the daily bat uses this to switch to Qwen fallback.
    if quota_hit:
        sys.exit(2)


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
        cmd_run(limit=limit, model=model, rpm=rpm, dry_run="--dry-run" in args)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
