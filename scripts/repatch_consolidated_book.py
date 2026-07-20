"""In-place re-patch of an already-consolidated book JSONL.

Use this AFTER consolidate_by_ncx.py has already run and you want to apply
the post-consolidation normalization rules (front-matter rename, parent_
volume backfill, Elucidation fold-back, index suffix volume clear) without
re-running the LLM translation OR re-running the NCX walk.

Rules applied (matches the normalize step in consolidate_by_ncx):
  R1  chunk 0 chapter_path  →  「封面」, volume/parent_volume = null
  R2  if chunk 1 is title-page-like AND chunk 2 is preface-like:
        merge chunk 1's content INTO chunk 2, set chapter_path = 「前言」,
        drop chunk 1 (renumber following indexes)
  R3  for every chunk with chunk_type == 'page' and a known volume:
        backfill parent_volume from VOLUME_TO_PARENT
  R4  Elucidation chunks (volume ends with 「註解」) get folded into the
        previous chunk's tail content; the Elucidation chunk is dropped.
  R5  trailing chunks with chunk_type='chapter' that follow the last
        consolidated 'page' chunk: volume/parent_volume = null
        (index suffix cleanup — indexes inherit stray volume from polish)

Usage:
    python scripts/repatch_consolidated_book.py <ebook_id>
    python scripts/repatch_consolidated_book.py <ebook_id> --dry-run
    python scripts/repatch_consolidated_book.py <ebook_id> --no-push
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "scripts"))
# Pull the canonical maps from consolidate_by_ncx so we don't duplicate.
from consolidate_by_ncx import (  # noqa: E402
    LETTER_CN_LABELS, PARENT_CN_FALLBACK,
)
import standardize_ebook as se  # noqa: E402

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR")
                  or r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")

PREFACE_LIKE = re.compile(r"序言|前言|序|Preface", re.I)
# Elucidation chunks come out of consolidate as a standalone volume whose
# Chinese name ends with 「註解」. They belong with the preceding book.
ELUCIDATION_VOLUME_RE = re.compile(r"註解$")


def derive_volume_to_parent() -> dict[str, str]:
    """Build {letter_cn: parent_cn} from the canonical maps."""
    out: dict[str, str] = {}
    for parent_key, _, letter_cn in LETTER_CN_LABELS:
        for parent_full, parent_cn in PARENT_CN_FALLBACK.items():
            if parent_key in parent_full:
                out[letter_cn] = parent_cn
                break
    # Special: 駁異端 卷 X all belong to Irenaeus.
    irenaeus_cn = PARENT_CN_FALLBACK.get("IRENÆUS") or PARENT_CN_FALLBACK["IRENAEUS"]
    out.setdefault("愛任紐《駁異端》註解", irenaeus_cn)
    return out


def fetch_book(ebook_id: str) -> dict:
    r = requests.get(f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}&select=*",
                     headers=H_GET, timeout=30)
    r.raise_for_status()
    rows = r.json()
    if not rows:
        sys.exit(f"no ebooks row for {ebook_id}")
    return rows[0]


def repatch(ebook_id: str, dry_run: bool = False, push: bool = True) -> None:
    book = fetch_book(ebook_id)
    print(f"Book: {book['title']}")

    jsonl_path = CHUNKS_DIR / f"{ebook_id}.jsonl"
    if not jsonl_path.exists():
        sys.exit(f"no JSONL: {jsonl_path}")
    chunks = [json.loads(l) for l in jsonl_path.read_text(encoding="utf-8").splitlines() if l]
    print(f"Loaded {len(chunks)} chunks")

    vol_to_parent = derive_volume_to_parent()

    # Stats / report
    actions: list[str] = []

    # ── R1: chunk 0 → 封面 ──
    if chunks:
        c0 = chunks[0]
        if c0.get("chapter_path") != "封面":
            actions.append(f"R1: chunk 0 chapter_path '{c0.get('chapter_path')}' → 封面")
            c0["chapter_path"] = "封面"
        c0["volume"] = None
        c0["parent_volume"] = None

    # ── R2: merge chunk 1 + chunk 2 into 前言 if Title-Page + Preface pair ──
    if len(chunks) >= 3:
        c1, c2 = chunks[1], chunks[2]
        l1 = c1.get("chapter_path", "") or ""
        l2 = c2.get("chapter_path", "") or ""
        if not PREFACE_LIKE.search(l1) and PREFACE_LIKE.search(l2):
            actions.append(f"R2: merge chunk 1 '{l1}' + chunk 2 '{l2}' → 前言")
            c2["content"] = (
                (c1.get("content") or "").strip() + "\n\n"
                + (c2.get("content") or "").strip()
            ).strip()
            c2["source_text"] = (
                (c1.get("source_text") or "").strip() + "\n\n"
                + (c2.get("source_text") or "").strip()
            ).strip()
            fn = dict(c1.get("footnotes") or {})
            fn.update(c2.get("footnotes") or {})
            if fn:
                c2["footnotes"] = fn
            pgs = sorted(set(
                (c1.get("page_numbers") or [])
                + (c2.get("page_numbers") or [])))
            if pgs:
                c2["page_numbers"] = pgs
                c2["page_number"] = pgs[0]
            c2["chapter_path"] = "前言"
            c2["volume"] = None
            c2["parent_volume"] = None
            # Drop chunk 1
            del chunks[1]

    # ── R4: fold Elucidation into preceding chunk ──
    # Walk backward so deletions don't shift indices we haven't visited.
    i = len(chunks) - 1
    while i > 0:
        c = chunks[i]
        vol = c.get("volume") or ""
        if ELUCIDATION_VOLUME_RE.search(vol):
            prev = chunks[i - 1]
            actions.append(
                f"R4: fold chunk '{c.get('chapter_path')}' "
                f"(vol '{vol}') into prev '{prev.get('chapter_path')}'")
            prev["content"] = (
                (prev.get("content") or "").rstrip() + "\n\n"
                + (c.get("content") or "").strip()
            ).strip()
            prev["source_text"] = (
                (prev.get("source_text") or "").rstrip() + "\n\n"
                + (c.get("source_text") or "").strip()
            ).strip()
            fn = dict(prev.get("footnotes") or {})
            fn.update(c.get("footnotes") or {})
            if fn:
                prev["footnotes"] = fn
            pgs = sorted(set(
                (prev.get("page_numbers") or [])
                + (c.get("page_numbers") or [])))
            if pgs:
                prev["page_numbers"] = pgs
                prev["page_number"] = pgs[0]
            del chunks[i]
        i -= 1

    # ── R3 + R5: backfill parent_volume; clear volume on trailing non-page chunks ──
    # Find the last 'page' chunk index — anything chunk_type='chapter' AFTER
    # that is back-matter (indexes etc.) and should not carry a volume.
    last_page_idx = -1
    for i, c in enumerate(chunks):
        if c.get("chunk_type") == "page":
            last_page_idx = i

    for i, c in enumerate(chunks):
        ct = c.get("chunk_type")
        vol = c.get("volume")
        if ct == "page":
            if vol and vol in vol_to_parent and c.get("parent_volume") != vol_to_parent[vol]:
                actions.append(f"R3: chunk {i} ({vol}) parent_volume → {vol_to_parent[vol]}")
                c["parent_volume"] = vol_to_parent[vol]
            elif vol and vol not in vol_to_parent:
                # Unknown volume — leave parent null, surface for review.
                if c.get("parent_volume") is None:
                    actions.append(f"R3: chunk {i} volume '{vol}' has no parent in map")
        else:
            # chunk_type='chapter' = front/back matter
            if i > last_page_idx and (vol or c.get("parent_volume")):
                actions.append(f"R5: chunk {i} ({c.get('chapter_path')}) "
                               f"clear stray volume '{vol}'")
                c["volume"] = None
                c["parent_volume"] = None
            elif i < last_page_idx:
                # Prefix front-matter — ensure null
                c["volume"] = None
                c["parent_volume"] = None

    # Renumber chunk_index 0..N-1 continuously
    for new_idx, c in enumerate(chunks):
        c["chunk_index"] = new_idx

    # ── Report ──
    print(f"\nApplied {len(actions)} normalization actions:")
    for a in actions[:40]:
        print(f"  · {a}")
    if len(actions) > 40:
        print(f"  · ... +{len(actions) - 40} more")

    # Sample dump
    print(f"\nFinal chunk count: {len(chunks)}")
    print("\nSample TOC (first 25 + last 10):")
    cur_p = None
    sample = list(enumerate(chunks))
    sample_idxs = list(range(min(25, len(chunks)))) + (
        list(range(max(0, len(chunks) - 10), len(chunks))) if len(chunks) > 25 else [])
    last_shown = -1
    for i in sorted(set(sample_idxs)):
        if last_shown != -1 and i > last_shown + 1:
            print("     ...")
        c = chunks[i]
        p = c.get("parent_volume") or "-"
        v = c.get("volume") or "-"
        if p != cur_p:
            cur_p = p
            print(f"  ── parent: {p} ──")
        cp = (c.get("chapter_path") or "")[:50]
        print(f"     [{c['chunk_index']:3d}] vol={v[:18]:18s} {cp}")
        last_shown = i

    if dry_run:
        print("\n(dry-run; not writing)")
        return

    # Write JSONL
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"\n✓ wrote {jsonl_path.name} ({jsonl_path.stat().st_size // 1024} KB)")

    if push:
        try:
            se.push_to_r2(ebook_id, jsonl_path)
            print("✓ pushed R2")
        except Exception as e:
            print(f"⚠ R2 push: {e}", file=sys.stderr)

        # Refresh DB previews
        try:
            r = requests.delete(f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebook_id}",
                                headers=H_GET, timeout=30)
            if r.status_code not in (200, 204):
                print(f"⚠ preview DELETE: {r.status_code}", file=sys.stderr)
            rows = [{
                "ebook_id": ebook_id,
                "chunk_index": c["chunk_index"],
                "chunk_type": c.get("chunk_type", "chapter"),
                "page_number": c.get("page_number"),
                "chapter_path": c.get("chapter_path"),
                "content": (c.get("content") or "")[:200],
                "char_count": len(c.get("content") or ""),
            } for c in chunks]
            BATCH = 25
            for i in range(0, len(rows), BATCH):
                batch = rows[i:i + BATCH]
                rr = requests.post(f"{URL}/rest/v1/ebook_chunks",
                                   headers=H_JSON, json=batch, timeout=30)
                if rr.status_code not in (200, 201):
                    for row in batch:
                        requests.post(f"{URL}/rest/v1/ebook_chunks",
                                      headers=H_JSON, json=row, timeout=30)
            print(f"✓ refreshed previews ({len(rows)} rows)")
        except Exception as e:
            print(f"⚠ preview refresh: {e}", file=sys.stderr)

        # Patch ebook row
        total_chars = sum(len(c.get("content") or "") for c in chunks)
        patch = {
            "chunk_count": len(chunks),
            "total_pages": len(chunks),
            "total_chars": total_chars,
        }
        requests.patch(f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}",
                       headers=H_JSON, json=patch, timeout=30)
        print(f"✓ ebooks row: chunk_count={len(chunks)}, total_chars={total_chars:,}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ebook_id")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-push", action="store_true",
                    help="Skip R2 push + DB refresh (local JSONL only)")
    args = ap.parse_args()
    repatch(args.ebook_id, dry_run=args.dry_run, push=not args.no_push)


if __name__ == "__main__":
    main()
