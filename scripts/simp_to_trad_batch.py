"""Batch simplified → traditional Chinese conversion for ebook chunks.

For every ebook in the DB with chunks, sample a few chunks to decide whether
the book is written in simplified Chinese. If so, run opencc s2tw +
parse_drive_inventory.TRAD_FIXES on every chunk's `content` and rewrite the
JSONL in place (also mirrors to R2 + refreshes ebook_chunks previews).

Unlike the English → Chinese pipeline this one does NOT preserve the source —
the original simplified text is overwritten. (Drive keeps version history if
recovery is ever needed.)

Usage:
  python scripts/simp_to_trad_batch.py --scan          # report only, no writes
  python scripts/simp_to_trad_batch.py --id <ebook>    # convert one book
  python scripts/simp_to_trad_batch.py --run-all       # convert every detected simp book
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")
sys.path.insert(0, str(Path(__file__).parent))

import standardize_ebook as se  # to_traditional + push_to_r2

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=representation"}

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR")
                  or r"G:\我的雲端硬碟\資料\電子書\_chunks")

# Characters that only exist in the simplified system. Any one of these in a
# sample is enough to conclude the book is simplified.
SIMP_INDICATORS = set("历这们时国个来书学经长现产业实从问开关动头爱东车电话语门间见马体识号买卖书师纸网线红绿蓝设备质")


def is_simplified(sample: str) -> bool:
    """True iff the sample contains any simplified-only indicator char."""
    return any(ch in SIMP_INDICATORS for ch in sample)


def load_jsonl_local(ebook_id: str) -> list[dict] | None:
    p = CHUNKS_DIR / f"{ebook_id}.jsonl"
    if not p.exists():
        return None
    try:
        return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
    except Exception as e:
        print(f"  load_jsonl_local failed: {e}", file=sys.stderr)
        return None


def load_jsonl_r2(ebook_id: str) -> list[dict] | None:
    """Pull from R2 + write to local cache so subsequent --run-all can rewrite locally."""
    try:
        import boto3, gzip, io
        c = boto3.client("s3", region_name="auto",
                         endpoint_url=os.environ["R2_ENDPOINT"],
                         aws_access_key_id=os.environ["R2_ACCESS_KEY"],
                         aws_secret_access_key=os.environ["R2_SECRET_KEY"])
        obj = c.get_object(Bucket=os.environ["R2_BUCKET"], Key=f"ebook-chunks/{ebook_id}.jsonl.gz")
        raw = gzip.GzipFile(fileobj=io.BytesIO(obj["Body"].read())).read().decode("utf-8")
        chunks = [json.loads(line) for line in raw.splitlines() if line.strip()]
        # cache to local for follow-up writes
        p = CHUNKS_DIR / f"{ebook_id}.jsonl"
        p.write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in chunks) + "\n",
                     encoding="utf-8")
        return chunks
    except Exception as e:
        print(f"  load_jsonl_r2 failed: {e}", file=sys.stderr)
        return None


def fetch_ebooks() -> list[dict]:
    """All ebooks with chunks. PostgREST caps at 1000 per page, paginate."""
    rows: list[dict] = []
    offset = 0
    while True:
        r = requests.get(
            f"{URL}/rest/v1/ebooks?select=id,title,author,chunk_count&chunk_count=gt.0"
            f"&order=created_at.desc&limit=1000&offset={offset}",
            headers=H_GET, timeout=60)
        r.raise_for_status()
        page = r.json()
        rows.extend(page)
        if len(page) < 1000:
            break
        offset += 1000
    return rows


def scan_one(ebook: dict) -> dict | None:
    """Return a status dict if the book is simplified, else None."""
    ebook_id = ebook["id"]
    chunks = load_jsonl_local(ebook_id)
    if not chunks:
        chunks = load_jsonl_r2(ebook_id)
    if not chunks:
        return {"ebook_id": ebook_id, "title": ebook["title"], "status": "no-jsonl"}
    # Sample chunks[0..2] content (combined ~600 chars window)
    sample = ""
    for c in chunks[:3]:
        sample += c.get("content", "")[:300]
        if len(sample) >= 600:
            break
    if is_simplified(sample):
        # Count exactly how many indicator chars to give an idea of confidence
        hits = sum(1 for ch in sample if ch in SIMP_INDICATORS)
        return {"ebook_id": ebook_id, "title": ebook["title"],
                "chunks": len(chunks), "indicator_hits": hits, "status": "simp"}
    return None


def convert_one(ebook_id: str, title: str) -> dict:
    """Rewrite JSONL with to_traditional applied to every chunk's content."""
    chunks = load_jsonl_local(ebook_id)
    if not chunks:
        chunks = load_jsonl_r2(ebook_id)
    if not chunks:
        return {"status": "skip", "reason": "no-jsonl"}

    changed = 0
    for c in chunks:
        original = c.get("content", "")
        converted = se.to_traditional(original)
        if converted != original:
            c["content"] = converted
            changed += 1
    if changed == 0:
        return {"status": "skip", "reason": "no-change (already trad?)"}

    # Rewrite JSONL
    p = CHUNKS_DIR / f"{ebook_id}.jsonl"
    p.write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in chunks) + "\n",
                 encoding="utf-8")

    # Push R2
    r2_size = None
    try:
        r2_size = se.push_to_r2(ebook_id, str(p))
    except Exception as e:
        print(f"  ⚠ R2 push failed: {e}", file=sys.stderr)

    # Refresh ebook_chunks previews (DELETE + INSERT)
    requests.delete(f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebook_id}", headers=H_GET, timeout=30)
    rows = [{
        "ebook_id": ebook_id,
        "chunk_index": c["chunk_index"],
        "chunk_type": c.get("chunk_type", "chapter"),
        "page_number": c.get("page_number"),
        "chapter_path": c.get("chapter_path"),
        "content": c["content"][:200],
        "char_count": len(c["content"]),
    } for c in chunks]
    BATCH = 25
    for i in range(0, len(rows), BATCH):
        rr = requests.post(f"{URL}/rest/v1/ebook_chunks", headers=H_JSON, json=rows[i:i+BATCH], timeout=60)
        if not rr.ok:
            print(f"  ⚠ preview insert: {rr.status_code}: {rr.text[:200]}", file=sys.stderr)

    return {"status": "converted", "chunks_changed": changed, "total_chunks": len(chunks),
            "r2_bytes": r2_size}


def refresh_previews_only(ebook_id: str) -> dict:
    """Re-do the DELETE + INSERT previews for one ebook (no s2tw rerun).
    Uses smaller batches + retries to survive Supabase 8s statement timeout
    on large books (e.g. 535-chunk 二思集 hit the wall on the first run)."""
    chunks = load_jsonl_local(ebook_id)
    if not chunks:
        chunks = load_jsonl_r2(ebook_id)
    if not chunks:
        return {"status": "skip", "reason": "no-jsonl"}

    # DELETE with explicit longer timeout + retry; 30s should comfortably
    # cover a fresh statement_timeout even when the previews table is bloated.
    for attempt in range(3):
        try:
            r = requests.delete(f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebook_id}",
                                headers=H_GET, timeout=60)
            if r.ok or r.status_code == 404:
                break
            print(f"  DELETE attempt {attempt+1}: {r.status_code}", file=sys.stderr)
        except requests.exceptions.RequestException as e:
            print(f"  DELETE attempt {attempt+1} conn-err: {e}", file=sys.stderr)
        time.sleep(2 ** attempt)

    rows = [{
        "ebook_id": ebook_id,
        "chunk_index": c["chunk_index"],
        "chunk_type": c.get("chunk_type", "chapter"),
        "page_number": c.get("page_number"),
        "chapter_path": c.get("chapter_path"),
        "content": c["content"][:200],
        "char_count": len(c["content"]),
    } for c in chunks]
    BATCH = 10
    failures = 0
    inserted = 0
    for i in range(0, len(rows), BATCH):
        batch = rows[i:i+BATCH]
        for attempt in range(3):
            try:
                rr = requests.post(f"{URL}/rest/v1/ebook_chunks",
                                   headers=H_JSON, json=batch, timeout=60)
                if rr.ok:
                    inserted += len(batch)
                    break
                print(f"  INSERT batch {i//BATCH+1} attempt {attempt+1}: {rr.status_code}: {rr.text[:120]}",
                      file=sys.stderr)
            except requests.exceptions.RequestException as e:
                print(f"  INSERT batch {i//BATCH+1} attempt {attempt+1} conn-err: {e}", file=sys.stderr)
            time.sleep(2 ** attempt)
        else:
            failures += 1
    return {"status": "previews-refreshed", "inserted": inserted, "failed_batches": failures,
            "total_chunks": len(chunks)}


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--scan", action="store_true", help="Detect simplified books, no writes")
    g.add_argument("--id", help="Convert a single ebook_id (no detection)")
    g.add_argument("--run-all", action="store_true", help="Detect then convert all simplified books")
    g.add_argument("--previews-only", help="Refresh ebook_chunks previews for one ebook_id (no s2tw)")
    args = ap.parse_args()

    if args.previews_only:
        print(f"Refreshing previews for {args.previews_only}")
        print(f"  → {refresh_previews_only(args.previews_only)}")
        return

    if args.id:
        # Force-convert by id (skip detection)
        # Best-effort title fetch for log readability
        r = requests.get(f"{URL}/rest/v1/ebooks?id=eq.{args.id}&select=title", headers=H_GET, timeout=30)
        title = (r.json() or [{}])[0].get("title", "(unknown)")
        print(f"[1] {title}  ({args.id})")
        result = convert_one(args.id, title)
        print(f"  → {result}")
        return

    print("Fetching ebook list…", flush=True)
    ebooks = fetch_ebooks()
    print(f"Total ebooks with chunks: {len(ebooks)}", flush=True)
    print("Scanning for simplified content…", flush=True)

    simp_books: list[dict] = []
    no_jsonl = 0
    for i, b in enumerate(ebooks, start=1):
        result = scan_one(b)
        if result and result["status"] == "simp":
            simp_books.append(result)
            print(f"  [{i:4d}] SIMP  ({result['indicator_hits']} hits, {result['chunks']} chunks)  "
                  f"{b['title'][:60]}", flush=True)
        elif result and result["status"] == "no-jsonl":
            no_jsonl += 1
        if i % 50 == 0:
            print(f"  …scanned {i}/{len(ebooks)}", flush=True)

    print(f"\nScan done. Simplified: {len(simp_books)}  /  No-JSONL: {no_jsonl}  /  Trad already: {len(ebooks)-len(simp_books)-no_jsonl}",
          flush=True)

    if args.scan:
        return

    # --run-all
    print(f"\nConverting {len(simp_books)} simplified books…", flush=True)
    for i, b in enumerate(simp_books, start=1):
        print(f"\n[{i}/{len(simp_books)}] {b['title'][:70]}", flush=True)
        t0 = time.time()
        result = convert_one(b["ebook_id"], b["title"])
        elapsed = time.time() - t0
        print(f"  → {result}  ({elapsed:.1f}s)", flush=True)


if __name__ == "__main__":
    main()
