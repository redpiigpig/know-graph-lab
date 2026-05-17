#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
split_oversized_pdf_by_toc.py — physically split a multi-volume PDF (套書 /
全集 / 多卷本) into one PDF per volume based on its TOC level-1 bookmarks.
Then insert one `ebooks` row per child so the next OCR run picks them up.

WHEN TO USE: a PDF lands in the OCR queue and reliably fails BOTH:
  - Gemini Files API (`exceeds the supported page limit of 1000` OR
    `Request contains an invalid argument` for >50 MB uploads)
  - Haiku image-batch API (`Output blocked by content filtering policy` on
    a long-running scan — the policy often triggers on the bundle's overall
    breadth of content, but smaller per-volume slices pass cleanly)

The auto-fallback paths in ocr_with_gemini.py (>1000 pages → inline Haiku;
>50 MB → pre-route to Haiku) cover most large books. This script is the
manual escape hatch for the small set that even Haiku refuses on the bundle
level. Splitting them physically lets each volume route through the normal
small-book Gemini path.

WHAT IT DOES:
  1. Reads the parent ebook row from `ebooks` table by id
  2. Opens the source PDF with PyMuPDF, extracts level-1 TOC bookmarks
  3. Writes one new PDF per volume to the same folder, named
     `<parent-title-stripped>_<volume-title>.pdf`
  4. Inserts one new `ebooks` row per volume with `parse_error =
     'no extractable text'` so the next OCR sweep picks it up
  5. Marks parent with `SPLIT_MARKER` so it leaves the OCR queue + future
     `split_ebook_set status` ignores it

REQUIRES: parent PDF has usable level-1 TOC bookmarks (most publisher
scans of multi-volume sets do). If TOC is empty, this script bails and you'll
need to split by page range manually (or extend the script).

Usage:
  python scripts/split_oversized_pdf_by_toc.py <parent_ebook_id>
  python scripts/split_oversized_pdf_by_toc.py <parent_ebook_id> --dry-run
  python scripts/split_oversized_pdf_by_toc.py <parent_ebook_id> --strip-suffix "（4卷本）"

The `--strip-suffix` arg trims a substring (e.g. "（4卷本）", "套裝", "全集")
from the parent title before composing the child filenames. Defaults to
auto-strip the common suffixes `（N卷本）` / `（共N冊）` / `（套裝共N本）`.

Idempotent: if children with the target filenames already exist on disk OR
parent already marked SPLIT_MARKER, the script aborts before doing damage.
"""
from __future__ import annotations

import argparse
import re
import sys
import uuid
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
import fitz
import requests
from parse_worker import load_env

ENV = load_env()
URL = ENV["SUPABASE_URL"]
KEY = ENV["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_WRITE = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}

SPLIT_MARKER = "split from set; do not re-standardize"

# Common volume-count suffixes to strip from parent title when naming children
DEFAULT_STRIP_PATTERNS = [
    r"（\d+卷本）",
    r"（共\d+冊）",
    r"（共\d+卷）",
    r"（套裝共\d+本）",
    r"（套裝共\d+冊）",
    r"（套裝共\d+卷）",
    r"（\d+冊套）",
    r"（\d+卷套）",
]


def strip_suffix(title: str, extra_suffix: str | None) -> str:
    """Trim multi-volume bundling suffix from the parent title."""
    out = title
    if extra_suffix:
        out = out.replace(extra_suffix, "")
    for p in DEFAULT_STRIP_PATTERNS:
        out = re.sub(p, "", out)
    return out.strip()


def fetch_parent(ebook_id: str) -> dict:
    r = requests.get(
        f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}&select=*",
        headers=H_GET, timeout=30,
    ).json()
    if not r:
        print(f"⚠ ebook id={ebook_id} not found", file=sys.stderr)
        sys.exit(1)
    return r[0]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("ebook_id")
    p.add_argument("--strip-suffix", default=None,
                   help="Extra title suffix to strip when naming children "
                        "(e.g. '（4卷本）'). Common patterns auto-stripped.")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    parent = fetch_parent(args.ebook_id)
    title = parent.get("title") or "?"
    src_path = Path(parent["file_path"])
    print(f"Parent: {title}")
    print(f"  id:   {parent['id']}")
    print(f"  file: {src_path}")

    if not src_path.exists():
        print(f"⚠ source missing: {src_path}", file=sys.stderr)
        sys.exit(1)

    pe = parent.get("parse_error") or ""
    if pe.startswith(SPLIT_MARKER):
        print(f"⚠ parent already split (SPLIT_MARKER present)")
        sys.exit(0)

    doc = fitz.open(src_path)
    total = len(doc)
    print(f"  pages: {total}")

    toc = [t for t in doc.get_toc() if t[0] == 1]
    if not toc:
        print("⚠ no level-1 TOC bookmarks — cannot split by TOC. Aborting.",
              file=sys.stderr)
        print("   For manual page-range split, edit this script.",
              file=sys.stderr)
        sys.exit(2)

    # Compute (volume_title, start_page, end_page) — 1-based inclusive
    volumes = []
    for i, (_, vt, sp) in enumerate(toc):
        ep = toc[i + 1][2] - 1 if i + 1 < len(toc) else total
        volumes.append((vt, sp, ep))

    print(f"\nVolumes detected ({len(volumes)}):")
    for vt, sp, ep in volumes:
        print(f"  {vt}: pages {sp}-{ep} ({ep - sp + 1} pp)")

    if len(volumes) < 2:
        print("⚠ only 1 volume detected — nothing to split", file=sys.stderr)
        sys.exit(2)

    base = strip_suffix(title, args.strip_suffix)
    parent_folder = src_path.parent

    # Pre-flight: check for existing output files (don't overwrite)
    target_paths = [
        parent_folder / f"{base}_{vt}.pdf" for vt, _, _ in volumes
    ]
    existing = [p for p in target_paths if p.exists()]
    if existing:
        print(f"\n⚠ target files already exist; aborting to avoid overwrite:",
              file=sys.stderr)
        for p in existing:
            print(f"   {p.name}", file=sys.stderr)
        sys.exit(3)

    if args.dry_run:
        print(f"\n[dry-run] would write {len(volumes)} files to {parent_folder}")
        for vt, sp, ep in volumes:
            print(f"   {base}_{vt}.pdf  ({ep - sp + 1} pp)")
        print(f"[dry-run] would insert {len(volumes)} child ebooks + mark parent SPLIT_MARKER")
        return

    print()
    new_ids = []
    for vt, sp, ep in volumes:
        out_path = parent_folder / f"{base}_{vt}.pdf"
        # Slice the PDF (PyMuPDF: from_page / to_page are 0-based inclusive)
        sub = fitz.open()
        sub.insert_pdf(doc, from_page=sp - 1, to_page=ep - 1)
        sub.save(str(out_path))
        sub.close()
        size_mb = out_path.stat().st_size / 1024 / 1024
        print(f"  ✓ wrote {out_path.name} ({size_mb:.1f} MB, {ep - sp + 1} pp)")

        new_id = str(uuid.uuid4())
        row = {
            "id": new_id,
            "title": f"{base}_{vt}",
            "author": parent.get("author"),
            "file_type": "pdf",
            "file_path": str(out_path),
            "category": parent.get("category"),
            "subcategory": parent.get("subcategory"),
            "parse_error": "no extractable text",
        }
        r = requests.post(f"{URL}/rest/v1/ebooks", headers=H_WRITE, json=row, timeout=30)
        if r.status_code in (200, 201):
            print(f"    + ebook row inserted: {new_id}")
            new_ids.append(new_id)
        else:
            print(f"    ⚠ insert failed: {r.status_code} {r.text[:200]}",
                  file=sys.stderr)

    doc.close()

    # Mark parent
    requests.patch(
        f"{URL}/rest/v1/ebooks?id=eq.{parent['id']}",
        headers=H_WRITE, json={"parse_error": SPLIT_MARKER}, timeout=15,
    )
    print(f"\n✓ parent marked SPLIT_MARKER; created {len(new_ids)} child ebooks")
    print(f"  Children will be picked up by the next OCR run.")


if __name__ == "__main__":
    main()
