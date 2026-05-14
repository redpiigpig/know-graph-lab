#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
split_ebook_set.py — split a 套書 / 全集 / 套裝 ebook into one row per volume.

Reads the existing chunk JSONL of a 套書 ebook, groups chunks by their
`volume` field, and emits N new ebook rows (one per volume) with their own
JSONL / R2 / chunk_previews — then deletes the original row + its data.

A book is splittable iff its chunks already carry a populated `volume`
field (came from the hierarchical-TOC standardize path). Books whose chunks
all have `volume = None` need font/LLM detection first — those are listed
by `status` but skipped by `run`.

Per the auto-memory feedback "套書要拆成個別書" the new rows get:
  - `title` = volume name (e.g. 稻草人手記)
  - `author / category / subcategory / file_type / file_path` inherited from original
  - `parse_error = 'split from set; do not re-standardize'` — marker so future
     standardize re-runs don't regenerate the full bundle into one volume's slot
  - `parsed_at` = current UTC
  - `chunk_count`, `total_chars` computed from group

Chunks with `volume=None` between the start of the doc and the first
real volume marker (cover / 版權頁 / 目錄 / 出版資訊) are folded into the
FIRST volume. Chunks with `volume=None` BETWEEN volumes are folded into
the PREVIOUS volume (treating them as trailing matter of the prior volume).

Usage:
  python scripts/split_ebook_set.py status                          # list splittable + non-splittable
  python scripts/split_ebook_set.py run --book <id> --dry-run       # preview split plan
  python scripts/split_ebook_set.py run --book <id>                 # split one book for real
  python scripts/split_ebook_set.py run --all --dry-run             # preview all 22 splittable
  python scripts/split_ebook_set.py run --all                       # batch ALL splittable (run after spot-check)
"""
from __future__ import annotations

import argparse
import gzip
import io
import json
import re
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
import standardize_ebook as se
import standardize_pdf_lite as pl

import requests

# Title patterns that identify a 套書 / 全集 / 套裝 candidate.
SET_TITLE_RX = re.compile(
    r'套裝|套书|全集|全套|大全|文集|文庫|文库|系列'
    r'|（\d+冊）|（\d+卷）|（\d+本）|共\d+冊|共\d+卷|（共\d+）|\d+冊套|\d+卷套'
)

SPLIT_MARKER = "split from set; do not re-standardize"
# Sister marker written by detect_set_volumes.py for 套書-titled ebooks whose
# JSONL actually only contains one volume — skip them in status / run.
NOT_A_SET_MARKER = "not actually a 套書 — single volume"

_HEADING_FIRST_RX = re.compile(r"^(#{1,4})\s+(.+?)(\r?\n|$)", re.M)


def flatten_heading_to_h2(content: str) -> str:
    """After splitting a 套書 into single-volume children, the publisher's
    `###` / `####` levels that used to mean 「組-內小篇」 become noise — there's
    no parent volume anymore for them to nest under. Rewrite ONLY the first
    heading in each chunk so all sidebar entries render at level 2 (siblings).
    Subsequent in-body headings stay untouched."""
    m = _HEADING_FIRST_RX.search(content or "")
    if not m or m.group(1) == "##":
        return content
    return content[:m.start(1)] + "##" + content[m.end(1):]


def fetch_set_candidates() -> list[dict]:
    """All ebooks whose title matches the 套書 pattern AND have JSONL on disk."""
    out = []
    offset = 0
    while True:
        r = requests.get(
            f"{se.URL}/rest/v1/ebooks"
            f"?parsed_at=not.is.null&select=id,title,author,file_type,file_path,"
            f"category,subcategory,chunk_count,total_chars,parse_error"
            f"&order=id&limit=1000&offset={offset}",
            headers=se.H_GET, timeout=60)
        page = r.json() or []
        if not page:
            break
        out.extend(page)
        if len(page) < 1000:
            break
        offset += 1000
    return [b for b in out if SET_TITLE_RX.search(b.get("title") or "")]


def annotations_for(ebook_id: str) -> int:
    r = requests.get(
        f"{se.URL}/rest/v1/annotations?ebook_id=eq.{ebook_id}&select=id&limit=1",
        headers={**se.H_GET, "Prefer": "count=exact", "Range": "0-0", "Range-Unit": "items"},
        timeout=20)
    cr = r.headers.get("Content-Range", "0/0")
    try:
        return int(cr.split("/")[-1])
    except ValueError:
        return 0


def load_chunks(ebook_id: str) -> list[dict] | None:
    p = se.CHUNKS_DIR / f"{ebook_id}.jsonl"
    if not p.exists():
        return None
    try:
        return pl._read_jsonl_robust(p)
    except Exception:
        return None


def group_by_volume(chunks: list[dict]) -> list[tuple[str, list[dict]]]:
    """Group chunks into volume buckets, preserving document order.

    Volume=None chunks attach to the FOLLOWING real volume if no real volume
    has appeared yet (frontmatter), else to the PRECEDING volume (trailing).
    """
    # Find the first real volume — chunks before it are "pending frontmatter"
    first_real_idx = next(
        (i for i, c in enumerate(chunks) if c.get("volume")),
        None
    )
    if first_real_idx is None:
        return []  # nothing real to group on
    groups: list[tuple[str, list[dict]]] = []
    current_name: str | None = None
    current_bucket: list[dict] = []
    # Frontmatter (before first volume) prepended to first volume's bucket
    pending_frontmatter = chunks[:first_real_idx]
    for c in chunks[first_real_idx:]:
        v = c.get("volume")
        if v and v != current_name:
            # New volume starts — close previous bucket
            if current_name is not None:
                groups.append((current_name, current_bucket))
            current_name = v
            current_bucket = []
            if not groups and pending_frontmatter:
                # First volume — prepend the frontmatter chunks
                current_bucket.extend(pending_frontmatter)
                pending_frontmatter = []
            current_bucket.append(c)
        else:
            # Continuation of current volume OR volume=None mid-doc (trailing
            # matter of the previous volume's last chunk).
            current_bucket.append(c)
    if current_name is not None:
        groups.append((current_name, current_bucket))
    return groups


def push_r2(book_id: str, jsonl_path: Path) -> None:
    """Reuse standardize_pdf_lite.push_to_r2 logic for consistency."""
    pl.push_to_r2(book_id, jsonl_path)


def delete_r2(book_id: str) -> None:
    """Remove the original ebook's R2 object after split is verified."""
    try:
        import boto3
        c = boto3.client(
            "s3", region_name="auto", endpoint_url=se.ENV["R2_ENDPOINT"],
            aws_access_key_id=se.ENV["R2_ACCESS_KEY"],
            aws_secret_access_key=se.ENV["R2_SECRET_KEY"],
        )
        c.delete_object(
            Bucket=se.ENV["R2_BUCKET"],
            Key=f"ebook-chunks/{book_id}.jsonl.gz",
        )
    except Exception as e:
        print(f"    ⚠ R2 delete failed (non-fatal): {str(e)[:120]}", file=sys.stderr)


def insert_chunk_previews(ebook_id: str, chunks: list[dict]) -> None:
    def _clean(v):
        return v.replace("\x00", "") if isinstance(v, str) else v
    rows = [{
        "ebook_id": ebook_id,
        "chunk_index": c.get("chunk_index", i),
        "chunk_type": c.get("chunk_type") or "chapter",
        "page_number": c.get("page_number"),
        "chapter_path": _clean(c.get("chapter_path")),
        "content": _clean(c.get("content") or "")[:se.PREVIEW_LEN],
        "char_count": len(_clean(c.get("content") or "")),
    } for i, c in enumerate(chunks)]
    BATCH_SIZES = [50, 20, 5, 1]
    i = 0
    while i < len(rows):
        for bs in BATCH_SIZES:
            batch = rows[i:i + bs]
            r = requests.post(f"{se.URL}/rest/v1/ebook_chunks",
                              headers=se.H_JSON, json=batch, timeout=120)
            if r.status_code in (200, 201):
                i += len(batch)
                break
            text = r.text[:300]
            if "57014" in text or "timeout" in text.lower() or r.status_code >= 500:
                if bs > BATCH_SIZES[-1]:
                    continue
            raise RuntimeError(f"preview insert failed: {r.status_code} {text[:120]}")
        else:
            raise RuntimeError(f"preview insert failed at batch_size=1, row {i}")


def insert_new_ebook(parent: dict, volume: str, chunk_count: int, total_chars: int) -> str:
    """Create a new ebook row for one volume of a 套書. Returns new ebook_id."""
    new_id = str(uuid.uuid4())
    row = {
        "id": new_id,
        "title": volume,
        "author": parent.get("author"),
        "file_type": parent.get("file_type"),
        "file_path": parent.get("file_path"),   # same source bundle
        "category": parent.get("category"),
        "subcategory": parent.get("subcategory"),
        "chunk_count": chunk_count,
        "total_chars": total_chars,
        "parsed_at": datetime.utcnow().isoformat() + "Z",
        "parse_error": SPLIT_MARKER,
    }
    r = requests.post(f"{se.URL}/rest/v1/ebooks", headers=se.H_JSON, json=row, timeout=30)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"ebook insert failed: {r.status_code} {r.text[:200]}")
    return new_id


def delete_original(ebook_id: str) -> None:
    """Remove the original 套書 row, its chunk previews, local JSONL, R2 obj."""
    # 1. DB: ebook_chunks
    requests.delete(f"{se.URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebook_id}",
                    headers=se.H_GET, timeout=30)
    # 2. DB: ebooks row
    requests.delete(f"{se.URL}/rest/v1/ebooks?id=eq.{ebook_id}",
                    headers=se.H_GET, timeout=30)
    # 3. Local JSONL
    p = se.CHUNKS_DIR / f"{ebook_id}.jsonl"
    if p.exists():
        try:
            p.unlink()
        except Exception as e:
            print(f"    ⚠ local JSONL unlink failed: {e}", file=sys.stderr)
    # 4. R2 object
    delete_r2(ebook_id)


def split_one(book: dict, dry_run: bool = False) -> tuple[int, str | None]:
    """Returns (num_new_rows_created, error_or_None)."""
    bid = book["id"]
    title = book.get("title") or "?"

    # Annotation guard
    n_ann = annotations_for(bid)
    if n_ann > 0:
        return 0, f"skipped: {n_ann} annotation(s) on parent (would shift chunk_index)"

    # Already split? (marker present)
    if (book.get("parse_error") or "").startswith(SPLIT_MARKER):
        return 0, "skipped: parent already marked split"

    chunks = load_chunks(bid)
    if not chunks:
        return 0, "skipped: JSONL missing or unreadable"

    groups = group_by_volume(chunks)
    if len(groups) < 2:
        return 0, f"skipped: only {len(groups)} volume group(s) — needs ≥2 to split"

    # Sanity: sum should match original chunks
    total = sum(len(g[1]) for g in groups)
    if total != len(chunks):
        return 0, f"skipped: group sum {total} != original {len(chunks)} (logic bug)"

    if dry_run:
        print(f"  [dry-run] would create {len(groups)} new rows:")
        for vname, group in groups:
            chars = sum(len(c.get("content") or "") for c in group)
            print(f"    {vname[:40]:40}  {len(group):4d} chunks  {chars // 1000:5d}K chars")
        print(f"    (and DELETE parent ebook {bid})")
        return len(groups), None

    # Real run — create new rows first, only delete parent at the end
    new_ids: list[str] = []
    for vname, group in groups:
        # Renumber chunk_index 0..N-1 + flatten heading depth to ## so the
        # reader sidebar shows all entries as siblings (publisher's `###/####`
        # nesting inside the original 套書 doesn't carry meaning once the
        # volume stands alone).
        renum = []
        for new_idx, c in enumerate(group):
            nc = dict(c)
            nc["chunk_index"] = new_idx
            nc["content"] = flatten_heading_to_h2(nc.get("content") or "")
            renum.append(nc)
        total_chars = sum(len(c.get("content") or "") for c in renum)

        # 1. Create new ebook row
        try:
            new_id = insert_new_ebook(book, vname, len(renum), total_chars)
        except Exception as e:
            return len(new_ids), f"insert_new_ebook failed for '{vname}': {str(e)[:160]}"

        # 2. Write JSONL
        out_path = se.CHUNKS_DIR / f"{new_id}.jsonl"
        with out_path.open("w", encoding="utf-8") as f:
            for c in renum:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")

        # 3. Push to R2
        try:
            push_r2(new_id, out_path)
        except Exception as e:
            print(f"    ⚠ R2 push failed for '{vname}' (JSONL persisted locally): {str(e)[:120]}",
                  file=sys.stderr)
            # don't abort — leave new row alive; user can re-push later

        # 4. Insert chunk_chunks previews
        try:
            insert_chunk_previews(new_id, renum)
        except Exception as e:
            return len(new_ids) + 1, f"preview insert failed for '{vname}': {str(e)[:160]}"

        new_ids.append(new_id)
        print(f"    + {vname[:40]:40}  {len(renum):4d} chunks  {total_chars // 1000:5d}K chars  id={new_id}",
              flush=True)

    # 5. All new rows created successfully — delete original
    print(f"    - deleting parent ebook {bid} (kept new {len(new_ids)} children)", flush=True)
    delete_original(bid)
    return len(new_ids), None


def cmd_status():
    cands = fetch_set_candidates()
    splittable = []
    unsplittable = []
    already = []
    annotated = []
    for b in cands:
        pe = b.get("parse_error") or ""
        if pe.startswith(SPLIT_MARKER):
            continue  # already a split child (shouldn't usually match SET_TITLE_RX, but skip)
        if pe.startswith(NOT_A_SET_MARKER):
            continue  # detect_set_volumes already confirmed: single volume despite title
        chunks = load_chunks(b["id"])
        if not chunks:
            continue
        if annotations_for(b["id"]) > 0:
            annotated.append(b)
            continue
        n_with_vol = len(set(c.get("volume") for c in chunks if c.get("volume")))
        if n_with_vol >= 2:
            splittable.append((b, n_with_vol))
        else:
            unsplittable.append(b)
    print(f"套書 candidates: {len(cands)} matching title pattern")
    print(f"  ✓ Splittable (≥2 distinct volume markers): {len(splittable)}")
    for b, nv in sorted(splittable, key=lambda x: -x[1]):
        print(f"      {nv:3d} vols  {b['title'][:60]}  id={b['id']}")
    print(f"  ⚠ Unsplittable (no volume metadata): {len(unsplittable)}")
    for b in unsplittable:
        print(f"      {b['title'][:60]}  id={b['id']}")
    if annotated:
        print(f"  🚫 Has annotations (will not auto-split): {len(annotated)}")
        for b in annotated:
            print(f"      {b['title'][:60]}  id={b['id']}")


def cmd_run(book_id: str | None, do_all: bool, dry_run: bool):
    if book_id:
        r = requests.get(
            f"{se.URL}/rest/v1/ebooks?id=eq.{book_id}"
            "&select=id,title,author,file_type,file_path,category,subcategory,"
            "chunk_count,total_chars,parse_error",
            headers=se.H_GET, timeout=30).json()
        if not r:
            print(f"⚠ ebook {book_id} not found", file=sys.stderr)
            sys.exit(1)
        books = r
    elif do_all:
        all_cands = fetch_set_candidates()
        # Filter: must be splittable (chunks have ≥2 volume markers) and no annotations
        books = []
        for b in all_cands:
            pe = b.get("parse_error") or ""
            if pe.startswith(SPLIT_MARKER) or pe.startswith(NOT_A_SET_MARKER):
                continue
            chunks = load_chunks(b["id"])
            if not chunks:
                continue
            if annotations_for(b["id"]) > 0:
                continue
            n_with_vol = len(set(c.get("volume") for c in chunks if c.get("volume")))
            if n_with_vol >= 2:
                books.append(b)
        print(f"Found {len(books)} splittable 套書")
    else:
        print("Specify --book <id> or --all", file=sys.stderr)
        sys.exit(2)

    ok = 0; skipped = 0; failed = 0
    new_total = 0
    for b in books:
        print(f"\n[{b['title'][:55]}]  id={b['id']}")
        try:
            n, err = split_one(b, dry_run=dry_run)
        except Exception as e:
            print(f"  ❌ exception: {str(e)[:200]}")
            failed += 1
            continue
        if err and err.startswith("skipped"):
            print(f"  · {err}")
            skipped += 1
        elif err:
            print(f"  ⚠ {err}")
            failed += 1
        else:
            ok += 1
            new_total += n
    print(f"\nDone. OK: {ok}, Skipped: {skipped}, Failed: {failed}, "
          f"new rows: {new_total}{' (dry-run)' if dry_run else ''}")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("status")
    pr = sub.add_parser("run")
    pr.add_argument("--book")
    pr.add_argument("--all", action="store_true")
    pr.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    if args.cmd == "status":
        cmd_status()
    elif args.cmd == "run":
        cmd_run(args.book, args.all, args.dry_run)
    else:
        p.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
