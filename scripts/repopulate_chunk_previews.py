#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Re-populate ebook_chunks with 200-char preview rows so /api/ebooks/search?mode=fulltext
covers every parsed book (not just the standardized + OCR'd ones).

Source of truth: local JSONL at G:/...電子書/_chunks/{ebook_id}.jsonl
                 (falls back to R2 if local missing — needs boto3 + .env)

Idempotent: skips books that already have rows in ebook_chunks (unless --force).

Usage:
  python scripts/repopulate_chunk_previews.py status
  python scripts/repopulate_chunk_previews.py run [--limit N] [--force]
  python scripts/repopulate_chunk_previews.py run --book <ebook_id>
"""
import gzip
import io
import json
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

try:
    import requests
except ImportError:
    print("Missing: pip install requests", file=sys.stderr)
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent))
from parse_worker import load_env

ENV = load_env()
URL = ENV["SUPABASE_URL"]
KEY = ENV["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_INS = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}

CHUNKS_DIR = Path(ENV.get("EBOOK_CHUNKS_DIR") or "G:/我的雲端硬碟/資料/電子書/_chunks")
PREVIEW_LEN = 200
BATCH = 100


# ── R2 lazy ────────────────────────────────────────────────────
_r2 = None
def get_r2():
    global _r2
    if _r2 is None:
        try:
            import boto3
        except ImportError:
            return None
        if not all(ENV.get(k) for k in ("R2_ENDPOINT", "R2_ACCESS_KEY", "R2_SECRET_KEY", "R2_BUCKET")):
            return None
        _r2 = boto3.client("s3", region_name="auto", endpoint_url=ENV["R2_ENDPOINT"],
                           aws_access_key_id=ENV["R2_ACCESS_KEY"],
                           aws_secret_access_key=ENV["R2_SECRET_KEY"])
    return _r2


def load_jsonl_lines(ebook_id: str):
    """Return list of parsed chunk dicts. Tries local first, then R2."""
    p = CHUNKS_DIR / f"{ebook_id}.jsonl"
    if p.exists():
        try:
            return [json.loads(ln) for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]
        except Exception as e:
            print(f"  ⚠ local read failed: {e}", file=sys.stderr)
    r2 = get_r2()
    if not r2:
        return None
    try:
        obj = r2.get_object(Bucket=ENV["R2_BUCKET"], Key=f"ebook-chunks/{ebook_id}.jsonl.gz")
        gz = obj["Body"].read()
        text = gzip.GzipFile(fileobj=io.BytesIO(gz)).read().decode("utf-8")
        return [json.loads(ln) for ln in text.splitlines() if ln.strip()]
    except Exception:
        return None


def fetch_books_with_chunks_count():
    """Returns [(ebook_id, title, chunk_count_in_db)]."""
    out = []
    offset = 0
    while True:
        params = (f"select=id,title,author,parsed_at,chunk_count"
                  f"&parsed_at=not.is.null"
                  f"&order=id&limit=1000&offset={offset}")
        r = requests.get(f"{URL}/rest/v1/ebooks?{params}", headers=H_GET, timeout=30)
        r.raise_for_status()
        page = r.json()
        if not page: break
        out.extend(page)
        if len(page) < 1000: break
        offset += 1000
    return out


def count_existing_chunks(ebook_id: str) -> int:
    """How many rows in ebook_chunks for this book."""
    r = requests.get(
        f"{URL}/rest/v1/ebook_chunks?select=id&ebook_id=eq.{ebook_id}&limit=1",
        headers={**H_GET, "Range": "0-0", "Prefer": "count=exact"},
        timeout=20,
    )
    cr = r.headers.get("Content-Range", "*/0")
    try:
        return int(cr.split("/")[-1])
    except Exception:
        return 0


def insert_previews(ebook_id: str, lines):
    """Write 200-char preview rows. Deletes existing first (idempotent re-run)."""
    requests.delete(
        f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebook_id}",
        headers=H_GET, timeout=30,
    )
    rows = []
    for c in lines:
        content = (c.get("content") or "")[:PREVIEW_LEN]
        rows.append({
            "ebook_id": ebook_id,
            "chunk_index": c.get("chunk_index"),
            "chunk_type": c.get("chunk_type") or "chapter",
            "page_number": c.get("page_number"),
            "chapter_path": c.get("chapter_path"),
            "content": content,
            "char_count": len(c.get("content") or ""),
        })
    inserted = 0
    for i in range(0, len(rows), BATCH):
        batch = rows[i:i+BATCH]
        r = requests.post(f"{URL}/rest/v1/ebook_chunks", headers=H_INS, json=batch, timeout=60)
        if r.status_code in (200, 201):
            inserted += len(batch)
        else:
            raise RuntimeError(f"insert failed: HTTP {r.status_code} {r.text[:200]}")
    return inserted


def cmd_status():
    books = fetch_books_with_chunks_count()
    print(f"Parsed ebooks: {len(books)}")
    have_local = sum(1 for b in books if (CHUNKS_DIR / f"{b['id']}.jsonl").exists())
    print(f"  with local JSONL: {have_local}")
    # Quick check of how many have rows in ebook_chunks
    needing = 0
    sample_size = min(20, len(books))
    for b in books[:sample_size]:
        if count_existing_chunks(b["id"]) == 0:
            needing += 1
    print(f"  in first {sample_size}, missing chunk rows: {needing}")


def cmd_run(limit=None, force=False, only_book=None):
    books = fetch_books_with_chunks_count()
    if only_book:
        books = [b for b in books if b["id"] == only_book]
    print(f"Books to consider: {len(books)}")

    todo = []
    skipped_no_jsonl = 0
    for b in books:
        if not force and count_existing_chunks(b["id"]) > 0:
            continue
        # Quick local existence check (cheap), R2 will be the fallback at run time
        if not (CHUNKS_DIR / f"{b['id']}.jsonl").exists():
            skipped_no_jsonl += 1
            continue
        todo.append(b)

    if limit:
        todo = todo[:limit]

    print(f"Will repopulate: {len(todo)} books  (skipped {skipped_no_jsonl} without local JSONL)")
    if not todo:
        print("Nothing to do.")
        return

    t0 = time.time()
    ok = 0
    failed = []
    for i, b in enumerate(todo, 1):
        title = (b["title"] or "Untitled")[:40]
        lines = load_jsonl_lines(b["id"])
        if not lines:
            failed.append((title, "no JSONL"))
            print(f"  [{i:4d}/{len(todo)}] ⚠ no JSONL  {title}")
            continue
        try:
            n = insert_previews(b["id"], lines)
            ok += 1
            elapsed = time.time() - t0
            rate = i / elapsed if elapsed else 0
            eta = (len(todo) - i) / rate if rate else 0
            print(f"  [{i:4d}/{len(todo)}] ✓ {n:4d} previews  {title}  ETA {int(eta)}s")
        except Exception as e:
            failed.append((title, str(e)[:120]))
            print(f"  [{i:4d}/{len(todo)}] ❌ {title}: {str(e)[:80]}", file=sys.stderr)

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.0f}s. OK: {ok}, Failed: {len(failed)}")
    if failed:
        for n, e in failed[:10]:
            print(f"  - {n}: {e}")


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    cmd = sys.argv[1]
    args = sys.argv[2:]
    if cmd == "status":
        cmd_status()
    elif cmd == "run":
        limit = None
        if "--limit" in args:
            limit = int(args[args.index("--limit") + 1])
        only_book = None
        if "--book" in args:
            only_book = args[args.index("--book") + 1]
        force = "--force" in args
        cmd_run(limit=limit, force=force, only_book=only_book)
    else:
        print(__doc__); sys.exit(1)


if __name__ == "__main__":
    main()
