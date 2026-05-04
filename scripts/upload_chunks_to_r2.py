#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Upload local JSONL chunk files to Cloudflare R2 (gzip-compressed).

Why: production server (Zeabur) cannot read the user's local G: drive.
JSONL must be in cloud storage. R2 has free egress and 10 GB free storage,
so this is the cheapest option.

R2 layout:
  ebook-chunks/{ebook_id}.jsonl.gz   — one file per book, gzipped JSONL

Safety:
  - Pre-flight summary (file count + size, current bucket usage)
  - Skips files already uploaded (idempotent — safe to resume)
  - --limit N for testing
  - --dry-run for inspection
  - Aborts if projected total > 9 GB (free tier cushion)

Usage:
  python scripts/upload_chunks_to_r2.py status            # show local + remote sizes
  python scripts/upload_chunks_to_r2.py upload --limit 5  # test with 5 files
  python scripts/upload_chunks_to_r2.py upload            # upload all
  python scripts/upload_chunks_to_r2.py upload --force    # re-upload existing
"""
import gzip
import io
import os
import sys
import time
from pathlib import Path

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    print("Missing boto3. Run: pip install boto3", file=sys.stderr)
    sys.exit(1)

# ── stdout UTF-8 for Windows ────────────────────────────────────
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

CHUNKS_DIR = Path("G:/我的雲端硬碟/資料/電子書/_chunks")
R2_PREFIX = "ebook-chunks/"
FREE_TIER_GB = 10
SAFETY_CEILING_GB = 9  # abort if projected total > this


def load_env():
    env = {}
    with open(".env", "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


ENV = load_env()


def get_r2_client():
    return boto3.client(
        "s3",
        region_name="auto",
        endpoint_url=ENV["R2_ENDPOINT"],
        aws_access_key_id=ENV["R2_ACCESS_KEY"],
        aws_secret_access_key=ENV["R2_SECRET_KEY"],
    )


BUCKET = ENV["R2_BUCKET"]


def fmt_size(b):
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


def list_local_files():
    """Return [(path, size_bytes), ...] for all .jsonl files."""
    return sorted(
        [(p, p.stat().st_size) for p in CHUNKS_DIR.glob("*.jsonl")],
        key=lambda x: x[0].name,
    )


def list_remote_keys(client):
    """Return {key: size} for all objects under R2_PREFIX."""
    out = {}
    token = None
    while True:
        kw = {"Bucket": BUCKET, "Prefix": R2_PREFIX}
        if token:
            kw["ContinuationToken"] = token
        r = client.list_objects_v2(**kw)
        for o in r.get("Contents", []):
            out[o["Key"]] = o["Size"]
        if not r.get("IsTruncated"):
            break
        token = r.get("NextContinuationToken")
    return out


def list_bucket_total(client):
    """Return (count, bytes) for the entire bucket — for free-tier ceiling check."""
    total_n = 0
    total_b = 0
    token = None
    while True:
        kw = {"Bucket": BUCKET}
        if token:
            kw["ContinuationToken"] = token
        r = client.list_objects_v2(**kw)
        for o in r.get("Contents", []):
            total_n += 1
            total_b += o["Size"]
        if not r.get("IsTruncated"):
            break
        token = r.get("NextContinuationToken")
    return total_n, total_b


def gz_compress(data: bytes) -> bytes:
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=6) as gz:
        gz.write(data)
    return buf.getvalue()


def cmd_status():
    print(f"Chunks dir: {CHUNKS_DIR}")
    locals_ = list_local_files()
    local_total = sum(s for _, s in locals_)
    print(f"  Local: {len(locals_)} files, {fmt_size(local_total)}")
    print(f"  Estimated gzipped: {fmt_size(int(local_total * 0.25))}  (~25% of original)")

    print(f"\nR2 bucket: {BUCKET}")
    client = get_r2_client()
    bucket_n, bucket_b = list_bucket_total(client)
    print(f"  Whole bucket: {bucket_n} objects, {fmt_size(bucket_b)}  (free tier: {FREE_TIER_GB} GB)")

    remote = list_remote_keys(client)
    print(f"  ebook-chunks/: {len(remote)} objects, {fmt_size(sum(remote.values()))}")

    todo = [p for p, _ in locals_ if f"{R2_PREFIX}{p.stem}.jsonl.gz" not in remote]
    print(f"\nPending: {len(todo)} files to upload")


def cmd_upload(limit=None, dry_run=False, force=False):
    client = get_r2_client()

    print("Pre-flight checks…")
    bucket_n, bucket_b = list_bucket_total(client)
    print(f"  R2 bucket currently: {bucket_n} objects, {fmt_size(bucket_b)}")

    locals_ = list_local_files()
    local_total = sum(s for _, s in locals_)
    print(f"  Local JSONL: {len(locals_)} files, {fmt_size(local_total)}")

    remote = list_remote_keys(client) if not force else {}

    todo = []
    for p, size in locals_:
        key = f"{R2_PREFIX}{p.stem}.jsonl.gz"
        if force or key not in remote:
            todo.append((p, size, key))

    if limit:
        todo = todo[:limit]

    if not todo:
        print("Nothing to upload. ✅")
        return

    estimated_gz = int(sum(s for _, s, _ in todo) * 0.25)
    projected = bucket_b + estimated_gz
    print(
        f"\nWill upload: {len(todo)} files, raw {fmt_size(sum(s for _, s, _ in todo))} "
        f"→ ~{fmt_size(estimated_gz)} after gzip"
    )
    print(f"Projected bucket total: {fmt_size(projected)}")

    if projected > SAFETY_CEILING_GB * 1024**3:
        print(
            f"❌ ABORT: projected {fmt_size(projected)} exceeds safety ceiling {SAFETY_CEILING_GB} GB"
        )
        sys.exit(2)

    if dry_run:
        print("\n--dry-run: would upload these (showing first 20):")
        for p, size, key in todo[:20]:
            print(f"  {p.name}  ({fmt_size(size)})  → r2://{BUCKET}/{key}")
        return

    print(f"\nStarting upload (gzip level 6)…")
    t0 = time.time()
    bytes_in = 0
    bytes_out = 0
    fails = []
    for i, (p, size, key) in enumerate(todo, 1):
        try:
            raw = p.read_bytes()
            gz = gz_compress(raw)
            client.put_object(
                Bucket=BUCKET,
                Key=key,
                Body=gz,
                ContentType="application/x-ndjson",
                ContentEncoding="gzip",
            )
            bytes_in += len(raw)
            bytes_out += len(gz)
            ratio = len(gz) / len(raw) * 100 if len(raw) else 0
            elapsed = time.time() - t0
            rate = i / elapsed if elapsed > 0 else 0
            eta = (len(todo) - i) / rate if rate > 0 else 0
            print(
                f"  [{i:4d}/{len(todo)}] {p.name[:50]:50s}  "
                f"{fmt_size(size)} → {fmt_size(len(gz))} ({ratio:.0f}%)  "
                f"ETA {int(eta)}s"
            )
        except Exception as e:
            fails.append((p.name, str(e)))
            print(f"  [{i:4d}/{len(todo)}] FAILED  {p.name}: {e}", file=sys.stderr)

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s")
    print(f"  Uploaded: {len(todo) - len(fails)} files")
    print(f"  Raw → gzip: {fmt_size(bytes_in)} → {fmt_size(bytes_out)} "
          f"({bytes_out / bytes_in * 100:.1f}% if any)" if bytes_in else "")
    if fails:
        print(f"  Failed: {len(fails)}")
        for name, err in fails[:10]:
            print(f"    {name}: {err}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    args = sys.argv[2:]
    if cmd == "status":
        cmd_status()
    elif cmd == "upload":
        limit = None
        dry_run = "--dry-run" in args
        force = "--force" in args
        if "--limit" in args:
            i = args.index("--limit")
            limit = int(args[i + 1])
        cmd_upload(limit=limit, dry_run=dry_run, force=force)
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
