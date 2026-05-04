#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert mobi/azw/azw3 ebooks to epub via Calibre's ebook-convert.

After conversion:
  - new .epub file lives next to the original
  - DB row updated: file_path → .epub path, file_type → 'epub'
  - parse_worker will pick it up on the next `run` (parsed_at still NULL)

Idempotent: skips books already converted (file_type already 'epub' OR
target .epub file exists with non-zero size).

Usage:
  python scripts/convert_mobi_to_epub.py status
  python scripts/convert_mobi_to_epub.py run [--limit N] [--keep-original] [--dry-run]
"""
import os
import sys
import subprocess
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

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

EBOOK_CONVERT = r"C:\Program Files\Calibre2\ebook-convert.exe"
TARGETS = ("mobi", "azw3", "azw")


def fetch_to_convert():
    """All books with file_type in TARGETS that aren't done yet."""
    out = []
    for ft in TARGETS:
        r = requests.get(
            f"{URL}/rest/v1/ebooks?select=id,title,author,file_type,file_path,parsed_at"
            f"&file_type=eq.{ft}&limit=2000",
            headers={"apikey": KEY, "Authorization": f"Bearer {KEY}"},
            timeout=30,
        )
        r.raise_for_status()
        out.extend(r.json())
    return out


def update_book(book_id, new_path, new_type):
    """Set file_path + file_type, clear parse_error so it'll be picked up."""
    r = requests.patch(
        f"{URL}/rest/v1/ebooks?id=eq.{book_id}",
        headers=H,
        json={"file_path": new_path, "file_type": new_type, "parse_error": None},
        timeout=30,
    )
    r.raise_for_status()


def cmd_status():
    books = fetch_to_convert()
    from collections import Counter
    c = Counter((b["file_type"], "ok" if b.get("parsed_at") else "todo") for b in books)
    print("Books in target formats:")
    for (ft, st), n in sorted(c.items()):
        print(f"  {ft:5s} {st:6s} {n}")
    print(f"\nTotal needing conversion: {sum(1 for b in books if not b.get('parsed_at'))}")


def cmd_run(limit=None, keep_original=False, dry_run=False):
    if not Path(EBOOK_CONVERT).exists():
        print(f"❌ ebook-convert not found at {EBOOK_CONVERT}", file=sys.stderr)
        print("Install Calibre: winget install Calibre.Calibre", file=sys.stderr)
        sys.exit(1)

    books = [b for b in fetch_to_convert() if not b.get("parsed_at")]
    print(f"Books to convert: {len(books)}")
    if limit:
        books = books[:limit]
        print(f"  (limited to {limit})")

    if dry_run:
        for b in books[:20]:
            print(f"  {b['file_type']:5s}  {b['file_path']}")
        if len(books) > 20:
            print(f"  … and {len(books) - 20} more")
        return

    t0 = time.time()
    ok = 0
    failed = []
    for i, b in enumerate(books, 1):
        src = Path(b["file_path"])
        if not src.exists():
            print(f"  [{i:3d}/{len(books)}] ⚠ source missing: {src}", file=sys.stderr)
            failed.append((b["title"], "source missing"))
            continue

        dst = src.with_suffix(".epub")
        if dst.exists() and dst.stat().st_size > 0:
            print(f"  [{i:3d}/{len(books)}] skip (already converted): {dst.name}")
            update_book(b["id"], str(dst), "epub")
            ok += 1
            continue

        title_short = (b["title"] or src.stem)[:40]
        print(f"  [{i:3d}/{len(books)}] {b['file_type']:5s} → epub  {title_short}…", end="", flush=True)

        try:
            res = subprocess.run(
                [EBOOK_CONVERT, str(src), str(dst)],
                capture_output=True,
                timeout=300,
            )
            if res.returncode != 0 or not dst.exists() or dst.stat().st_size == 0:
                err = (res.stderr.decode("utf-8", errors="replace")[:200]
                       or res.stdout.decode("utf-8", errors="replace")[-200:])
                print(f"  ❌ {err.strip()}")
                failed.append((b["title"], err.strip()[:120]))
                continue

            update_book(b["id"], str(dst), "epub")
            if not keep_original:
                try:
                    src.unlink()
                except Exception as e:
                    print(f"  (couldn't delete original: {e})", end="")
            elapsed = time.time() - t0
            rate = i / elapsed if elapsed > 0 else 0
            eta = (len(books) - i) / rate if rate > 0 else 0
            print(f"  ✓ ({dst.stat().st_size // 1024} KB)  ETA {int(eta)}s")
            ok += 1
        except subprocess.TimeoutExpired:
            print(f"  ❌ timeout (>5min)")
            failed.append((b["title"], "timeout"))
        except Exception as e:
            print(f"  ❌ {e}")
            failed.append((b["title"], str(e)[:120]))

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.0f}s. Converted: {ok}, Failed: {len(failed)}")
    if failed:
        print("Failures:")
        for name, err in failed[:20]:
            print(f"  - {name[:50]}  ({err})")
    print(f"\nNext: python scripts/parse_worker.py run")


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
        cmd_run(limit=limit, keep_original="--keep-original" in args, dry_run="--dry-run" in args)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
