"""D1 — 1-10 章合一頁，註釋下沉到 page 末尾.

Walks JSONL chunks already grouped by `volume`. For each volume, computes
median chars per chapter chunk and decides:
  - median < THRESHOLD (default 3000) → 短書信/講道 → 10 章合 1 頁
  - median ≥ THRESHOLD              → 論述書/長章 → 維持每章一頁
Single-chunk volumes (already 1 page) and front-matter (封面/前言/書名頁/索引)
are skipped.

Consolidation:
  - Take consecutive chapter chunks within the same volume
  - Group by chapters_per_page (default 10)
  - Merge content with \\n\\n; collect all footnotes into trailing block
  - Set chunk_type='page', chapter_path='<vol> 第N-M章'
  - Preserve parent_volume, volume, source_lang on the first source chunk

Idempotent (skips chunks already chunk_type='page' with chapter_path of
the `第N-M章` form).

Usage:
    python scripts/consolidate_letters.py <EBOOK_ID> [--threshold 3000]
                                                     [--chapters-per-page 10]
                                                     [--dry-run]
    python scripts/consolidate_letters.py --all
"""
from __future__ import annotations
import argparse
import json
import os
import re
import statistics
import sys
from pathlib import Path
from collections import defaultdict
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "scripts"))
import standardize_ebook as se

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR")
                  or r"G:\我的雲端硬碟\資料\電子書\_chunks")

# Volumes that should never be consolidated (front matter / indices)
SKIP_VOLS_EXACT = {"封面", "前言", "書名頁", "序言", "索引", "目錄"}
# Volumes containing these substrings are treated as front/back matter
SKIP_VOLS_CONTAINS = ("引言", "書名頁", "封面", "前言", "目錄", "索引")

# Already done volumes (Vol 1 + future newly-translated which need full consolidate_by_ncx)
ALL_BOOKS = [
    # ("Vol 1", "c98d358d-7066-4691-a896-b7232707b0db"),  # skip: already heavily consolidated
    ("Vol 2", "4e3d16fc-ef4f-420f-a3ec-56e2e92d659f"),
    ("Vol 3", "364dac2e-410f-4906-be63-8bb86b4865ee"),
    ("Vol 4", "904661d3-16fc-4f37-bb04-f7c4aa7671e9"),
    ("Vol 5", "0e08c662-540b-4186-b250-9bca0cfe1002"),
    ("Vol 6", "dffaae40-e088-41c1-ab7f-9b96f9249661"),
    ("Vol 7", "75d8aae0-7431-4be9-baee-c57d26599653"),
    ("Vol 8", "d09946ab-154b-4a97-853f-751cbb346221"),
    ("Vol 9", "72cb2f94-da86-4e16-bbbd-4cf3391031df"),
]


def is_skip_vol(vol: str) -> bool:
    if not vol:
        return True
    if vol in SKIP_VOLS_EXACT:
        return True
    return any(s in vol for s in SKIP_VOLS_CONTAINS)


# Footnote extraction — CCEL chunks end with a `———————————` separator
# then `(N) text` lines. We extract those to merge at page end.
FN_SEPARATOR_RE = re.compile(r"\n{1,3}—{4,}\s*\n")
FN_LINE_RE = re.compile(r"^\s*\(\s*(\d+)\s*\)\s*(.+)$", re.M)


def split_body_and_footnotes(content: str) -> tuple[str, dict[int, str]]:
    """Return (body, {fn_num: text}). If no separator/footnotes, returns (content, {})."""
    parts = FN_SEPARATOR_RE.split(content, maxsplit=1)
    if len(parts) != 2:
        return content, {}
    body, tail = parts
    fns: dict[int, str] = {}
    for m in FN_LINE_RE.finditer(tail):
        try:
            n = int(m.group(1))
            fns[n] = m.group(2).strip()
        except ValueError:
            continue
    if not fns:
        return content, {}
    return body.rstrip(), fns


def merge_chunks(chunks: list[dict], vol: str, start_ch: int, end_ch: int) -> dict:
    """Merge a slice of chapter chunks into one page chunk.

    KEEPS each chapter's original CCEL-style body + `——————` separator +
    footnote block intact, simply concatenated with `\n\n` between chapters.
    The reader's `renderMarkdown` collects all footnote items across
    separators into one unified `<section class="footnotes">` at the bottom
    (see pages/ebook/[id].vue, function renderMarkdown). Don't strip — the
    reader needs the separators to detect footnote toggle.
    """
    bodies: list[str] = []
    all_fns: dict[int, str] = {}
    src_texts: list[str] = []
    page_nums: list[int] = []
    for c in chunks:
        body = (c.get("content", "") or "").strip()
        if body:
            bodies.append(body)
        # Carry forward existing footnotes dict if present (chunks set by
        # earlier consolidate_by_ncx may have a `footnotes` dict).
        for k, v in (c.get("footnotes") or {}).items():
            try:
                all_fns[int(k) if str(k).isdigit() else k] = v
            except ValueError:
                all_fns[k] = v
        if c.get("source_text"):
            src_texts.append(c["source_text"])
        for p in (c.get("page_numbers") or []):
            page_nums.append(p)
    merged_body = "\n\n".join(bodies)
    span = f"第{start_ch}章" if start_ch == end_ch else f"第{start_ch}-{end_ch}章"
    first = chunks[0]
    page = {
        "chunk_index": first["chunk_index"],  # will be re-indexed later
        "chunk_type": "page",
        "page_number": first.get("page_number"),
        "page_numbers": sorted(set(page_nums)) if page_nums else None,
        "chapter_path": f"{vol} {span}",
        "format": "markdown",
        "source_lang": first.get("source_lang") or "en",
        "title_en": first.get("title_en"),
        "volume": vol,
        "parent_volume": first.get("parent_volume"),
        "source_text": "\n\n".join(src_texts) if src_texts else None,
        "content": merged_body,
        "footnotes": all_fns if all_fns else None,
        "is_volume_header": (start_ch == 1),
    }
    return page


def process_book(label: str, ebook_id: str, threshold: int, per_page: int,
                 dry_run: bool):
    src = CHUNKS_DIR / f"{ebook_id}.jsonl"
    if not src.exists():
        print(f"  {label}: jsonl not found, skipping")
        return
    rows = [json.loads(l) for l in src.read_text(encoding="utf-8").splitlines() if l.strip()]
    print(f"\n=== {label} ({ebook_id}) — {len(rows)} chunks ===")

    # Group consecutive chapter chunks by volume — preserve original order
    # of chunks; restart group on volume change.
    new_chunks: list[dict] = []
    i = 0
    consolidated_count = 0
    pages_made = 0
    while i < len(rows):
        r = rows[i]
        vol = r.get("volume")
        ct = r.get("chunk_type")
        # Pass through if: not chapter, no vol, or vol is skip
        if ct != "chapter" or not vol or is_skip_vol(vol):
            new_chunks.append(r)
            i += 1
            continue
        # Gather consecutive chapter chunks with same volume
        j = i
        group: list[dict] = []
        while j < len(rows):
            rj = rows[j]
            if (rj.get("chunk_type") == "chapter"
                    and rj.get("volume") == vol):
                group.append(rj)
                j += 1
            else:
                break
        # Compute median chars
        chars = [len(c.get("content", "") or "") for c in group]
        med = statistics.median(chars) if chars else 0
        if med >= threshold or len(group) == 1:
            # Long-form treatise OR single chapter — keep as-is
            new_chunks.extend(group)
            i = j
            continue
        # Consolidate: pack `per_page` chunks per page
        for start in range(0, len(group), per_page):
            slice_ = group[start:start + per_page]
            page = merge_chunks(slice_, vol, start + 1, start + len(slice_))
            new_chunks.append(page)
            pages_made += 1
        consolidated_count += len(group)
        i = j

    # Re-index
    for idx, c in enumerate(new_chunks):
        c["chunk_index"] = idx

    print(f"  consolidated: {consolidated_count} chapter chunks → {pages_made} page chunks")
    print(f"  final chunk count: {len(rows)} → {len(new_chunks)}")

    if dry_run:
        print("  (dry-run)")
        return

    with open(src, "w", encoding="utf-8") as f:
        for c in new_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"  wrote {src.name} ({src.stat().st_size // 1024} KB)")

    se.push_to_r2(ebook_id, src)
    print("  pushed R2")

    # Refresh DB previews
    requests.delete(f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebook_id}",
                    headers=H_GET, timeout=60)
    insert_rows = [{
        "ebook_id": ebook_id,
        "chunk_index": c["chunk_index"],
        "chunk_type": c.get("chunk_type", "chapter"),
        "page_number": c.get("page_number"),
        "chapter_path": c.get("chapter_path"),
        "content": (c.get("content") or "")[:200],
        "char_count": len(c.get("content") or ""),
    } for c in new_chunks]
    BATCH = 25
    for i in range(0, len(insert_rows), BATCH):
        batch = insert_rows[i:i + BATCH]
        rr = requests.post(f"{URL}/rest/v1/ebook_chunks", headers=H_JSON,
                           json=batch, timeout=60)
        if rr.status_code not in (200, 201):
            print(f"    batch {i}: {rr.status_code} {rr.text[:200]}", file=sys.stderr)
    print(f"  refreshed previews ({len(insert_rows)} rows)")

    # Update ebooks row
    new_chars = sum(len(c.get("content") or "") for c in new_chunks)
    requests.patch(
        f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}",
        headers=H_JSON,
        json={"chunk_count": len(new_chunks), "total_chars": new_chars},
        timeout=30,
    )
    print(f"  ebooks row updated: chunk_count={len(new_chunks)} total_chars={new_chars}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ebook_id", nargs="?", help="single ebook id")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--threshold", type=int, default=3000,
                    help="median chars/chapter; below → consolidate")
    ap.add_argument("--chapters-per-page", type=int, default=10)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.all:
        for label, ebid in ALL_BOOKS:
            process_book(label, ebid, args.threshold,
                         args.chapters_per_page, args.dry_run)
    elif args.ebook_id:
        label = next((l for l, e in ALL_BOOKS if e == args.ebook_id), "Custom")
        process_book(label, args.ebook_id, args.threshold,
                     args.chapters_per_page, args.dry_run)
    else:
        ap.error("specify --all or an ebook_id")


if __name__ == "__main__":
    main()
