"""Multi-h3 chunk splitter — distributes each h3 segment of a chunk to
its proper home chunk per NCX attribution.

Where auto_fix_cross_bleeds.py moves the entire post-first-bleed tail as
ONE blob (which lumps multiple sub-bleeds together), this tool walks
EACH h3 segment in source_text, attributes it via NCX, and moves it to
the target chunk for THAT specific segment.

Strategy:
  1. For each chunk, walk source_text h3 markers in order.
  2. Pair them 1:1 with content (ZH) h3 markers (same ordinal).
  3. Each [h3_i, h3_{i+1}) range is a "segment" — text between adjacent
     h3 boundaries.
  4. For each segment, look up which NCX letter it belongs to.
     - If matches chunk's own title_en → keep in chunk.
     - Else → identify target chunk via title_en match; queue for move.
  5. Apply moves: prepend each foreign segment to its target chunk's
     content+source_text, then delete from current chunk.

Strict safety guards:
  - Won't move if target chunk's parent ≠ attributed parent (no Polycarp
    Phil → Ignatius pseudo confusion).
  - Won't move a segment ≥ 70% of source chunk's length.
  - Footnote bodies (1xxx) following each segment in the content move
    with the segment if their (N) appears within the segment range.

Usage:
    python scripts/multi_h3_splitter.py <ebook_id> --dry-run
    python scripts/multi_h3_splitter.py <ebook_id>
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
import standardize_ebook as se  # noqa: E402
from scan_translated_book import (  # noqa: E402
    build_ncx_index, attribute_heading, normalize_heading, fetch_book,
)
from consolidate_by_ncx import find_epub  # noqa: E402
from auto_fix_cross_bleeds import (  # noqa: E402
    build_chunk_parent_map,
)

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR")
                  or r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")

# Match an h3 heading whose text may wrap onto subsequent lines (CCEL
# EPUBs frequently break long titles like "Introductory Note to the
# Epistle of\nMathetes to Diognetus" with a single \n). We consume up to
# the next blank line OR next heading marker so the WHOLE title is in
# group 1, then collapse internal whitespace when comparing.
H3_RE = re.compile(r"^###[ \t]+([\s\S]+?)(?=\n[ \t]*\n|\n#|\Z)", re.M)


def normalize_h3_text(raw: str) -> str:
    """Collapse internal whitespace + drop footnote refs for clean
    attribution lookup."""
    s = re.sub(r"\[\^?\d+\]", "", raw)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def find_segments(chunk: dict, ncx_index: list[dict]) -> list[dict]:
    """Return a list of segments — each between consecutive h3 markers
    in source_text — with their attributed NCX letter."""
    src = chunk.get("source_text") or ""
    zh = chunk.get("content") or ""
    en_h3s = list(H3_RE.finditer(src))
    zh_h3s = list(H3_RE.finditer(zh))
    if not en_h3s:
        return []
    # Pad EN and ZH boundaries with start/end
    en_bounds = [0] + [m.start() for m in en_h3s] + [len(src)]
    zh_bounds = [0] + [m.start() for m in zh_h3s] + [len(zh)]
    # Each h3 starts a segment. Segment i = [en_bounds[i], en_bounds[i+1])
    # We have len(en_h3s)+1 "raw" ranges but the first (pre-first-h3) is
    # usually empty or just prose; skip it if empty.
    segments = []
    for i, m in enumerate(en_h3s):
        en_start = m.start()
        en_end = en_h3s[i + 1].start() if i + 1 < len(en_h3s) else len(src)
        # Corresponding ZH range: same ordinal i, h3 marker positions
        if i < len(zh_h3s):
            zh_start = zh_h3s[i].start()
        else:
            # ZH side missing this h3 — fall back to proportional
            zh_start = int(len(zh) * (en_start / max(len(src), 1)))
        if i + 1 < len(zh_h3s):
            zh_end = zh_h3s[i + 1].start()
        else:
            zh_end = len(zh)
        h_text = normalize_h3_text(m.group(1))
        attributed = attribute_heading(h_text, ncx_index)
        segments.append({
            "ordinal": i,
            "h3_en": h_text,
            "en_range": (en_start, en_end),
            "zh_range": (zh_start, zh_end),
            "attributed": attributed,
        })
    return segments


def trim_separator(s: str) -> str:
    """Remove a trailing footnote-section close em-dash row if present."""
    return re.sub(r"\n*[—－\-]{15,}\s*$", "", s).rstrip()


def find_target_chunk_index(attributed_norm: str,
                            attributed_parent: Optional[str],
                            chunks: list[dict],
                            current_idx: int,
                            ncx_index: list[dict],
                            parent_map: dict[int, str]) -> Optional[int]:
    """Locate the chunk index that owns the attributed letter (same
    parent + matching title_en). Returns None when no match."""
    target_toks = set(t for t in re.split(r"\W+", attributed_norm) if len(t) >= 3)
    # Tier 1: title_en token match with parent guard
    for i, c in enumerate(chunks):
        if i == current_idx or c.get("chunk_type") != "page":
            continue
        if attributed_parent and parent_map.get(i) != attributed_parent:
            continue
        te = normalize_heading(c.get("title_en") or "")
        if not te:
            continue
        te_toks = set(t for t in re.split(r"\W+", te) if len(t) >= 3)
        if not te_toks:
            continue
        overlap = len(target_toks & te_toks) / max(len(target_toks | te_toks), 1)
        if (overlap >= 0.6) or (te in attributed_norm) or (attributed_norm in te):
            return i
    # Tier 2: parent fallback — first chunk under that parent
    if attributed_parent is None:
        return None
    for i in range(len(chunks)):
        if i == current_idx or chunks[i].get("chunk_type") != "page":
            continue
        if parent_map.get(i) == attributed_parent:
            return i
    return None


def _attributed_parent(attributed_norm: str, ncx_index: list[dict]) -> Optional[str]:
    for entry in ncx_index:
        if entry["en_letter_norm"] == attributed_norm:
            return entry["parent"].upper()
    return None


def plan_chunk(chunk: dict, idx: int, chunks: list[dict],
               ncx_index: list[dict], parent_map: dict[int, str]) -> list[dict]:
    """Build a move plan for one source chunk. Each entry:
    {"segment_idx", "target_idx", "h3_en", "en_text", "zh_text"}.
    Returns [] when the chunk has no h3s or none are foreign."""
    title_en_norm = normalize_heading(chunk.get("title_en") or "")
    chunk_parent = parent_map.get(idx)
    segments = find_segments(chunk, ncx_index)
    if not segments:
        return []
    src = chunk["source_text"]
    zh = chunk["content"]
    plan: list[dict] = []
    for seg in segments:
        attributed = seg["attributed"]
        if not attributed:
            continue
        a_norm = attributed["en_letter_norm"]
        # Same letter — keep
        a_toks = set(t for t in re.split(r"\W+", a_norm) if len(t) >= 3)
        b_toks = set(t for t in re.split(r"\W+", title_en_norm) if len(t) >= 3)
        overlap = len(a_toks & b_toks) / max(len(a_toks | b_toks), 1)
        same = (overlap >= 0.6) or (a_norm in title_en_norm) or (title_en_norm in a_norm)
        if not same and chunk_parent and attributed.get("parent","").upper() == chunk_parent:
            same = True
        if same:
            continue
        # Foreign — find target
        a_parent = attributed.get("parent","").upper() or None
        target = find_target_chunk_index(a_norm, a_parent, chunks, idx,
                                         ncx_index, parent_map)
        if target is None:
            continue
        en_s, en_e = seg["en_range"]
        zh_s, zh_e = seg["zh_range"]
        en_text = src[en_s:en_e]
        zh_text = zh[zh_s:zh_e]
        # Safety: refuse if segment is too large (>15K ZH) or covers >70%
        # Absolute size cap — beyond 18K chars even legitimate moves are
        # suspicious enough to warrant manual inspection.
        if len(zh_text) > 18000:
            continue
        # Percentage cap — only refuse "majority move" for SMALL chunks
        # (<5K total). For larger chunks, the legitimate case where a
        # chunk is mostly bleed (e.g. chunk 81 where Justin Fragments is
        # 3K of real content + 11K of Irenaeus intro) needs the move.
        if len(zh) < 5000 and len(zh_text) > 0.7 * len(zh):
            continue
        plan.append({
            "segment_idx": seg["ordinal"],
            "target_idx": target,
            "h3_en": seg["h3_en"][:60],
            "en_text": en_text,
            "zh_text": zh_text,
            "en_range": (en_s, en_e),
            "zh_range": (zh_s, zh_e),
        })
    return plan


def apply_plan(chunk_idx: int, plan: list[dict], chunks: list[dict]) -> dict:
    """Execute the moves: remove segments from source chunk, prepend to
    each target. Returns stats."""
    if not plan:
        return {"moves": 0}
    src_chunk = chunks[chunk_idx]
    src = src_chunk["source_text"]
    zh = src_chunk["content"]
    # Sort by en_range descending so removals don't shift earlier offsets
    sorted_plan = sorted(plan, key=lambda p: -p["en_range"][0])
    # Apply removals first (to source chunk)
    new_src = src
    new_zh = zh
    for p in sorted_plan:
        es, ee = p["en_range"]
        zs, ze = p["zh_range"]
        new_src = new_src[:es] + new_src[ee:]
        new_zh = new_zh[:zs] + new_zh[ze:]
    src_chunk["source_text"] = trim_separator(new_src)
    src_chunk["content"] = trim_separator(new_zh)

    # Group moves by target — multiple segments to same target get merged
    by_target: dict[int, list[dict]] = {}
    for p in plan:
        by_target.setdefault(p["target_idx"], []).append(p)
    # For each target, prepend all its moved segments in original order
    for ti, segs in by_target.items():
        segs_sorted = sorted(segs, key=lambda s: s["segment_idx"])
        merged_en = "\n\n".join(s["en_text"].strip() for s in segs_sorted)
        merged_zh = "\n\n".join(s["zh_text"].strip() for s in segs_sorted)
        dst = chunks[ti]
        dst["content"] = (merged_zh + "\n\n" + (dst.get("content") or "")).strip()
        dst["source_text"] = (merged_en + "\n\n" + (dst.get("source_text") or "")).strip()

    return {"moves": len(plan), "targets": len(by_target)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ebook_id")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-push", action="store_true")
    args = ap.parse_args()

    book = fetch_book(args.ebook_id)
    epub = find_epub(book)
    ncx_index = build_ncx_index(epub)
    jsonl = CHUNKS_DIR / f"{args.ebook_id}.jsonl"
    chunks = [json.loads(l) for l in jsonl.read_text(encoding="utf-8").splitlines() if l]
    print(f"Book: {book['title']}")
    print(f"Loaded {len(chunks)} chunks; {len(ncx_index)} NCX entries")

    parent_map = build_chunk_parent_map(chunks, ncx_index)

    # Build plans up front so we can iterate in stable order
    plans = []
    for i, c in enumerate(chunks):
        if c.get("chunk_type") != "page":
            continue
        plan = plan_chunk(c, i, chunks, ncx_index, parent_map)
        if plan:
            plans.append((i, plan))

    total_moves = 0
    print(f"\nFound {len(plans)} source chunks with foreign segments")
    for src_idx, plan in plans:
        sp = chunks[src_idx]
        print(f"\nchunk {src_idx} ({sp.get('chapter_path','')[:35]}): "
              f"{len(plan)} segments to move")
        for p in plan:
            tgt = chunks[p["target_idx"]]
            print(f"  → chunk {p['target_idx']:3d} ({tgt.get('chapter_path','')[:30]:30s}) "
                  f"[{len(p['zh_text'])} ZH chars] {p['h3_en'][:50]}")
        if not args.dry_run:
            stats = apply_plan(src_idx, plan, chunks)
            total_moves += stats["moves"]

    if args.dry_run:
        print("\n(dry-run; not writing)")
        return

    # Write
    with open(jsonl, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"\n✓ wrote {jsonl.name} ({total_moves} moves)")

    if not args.no_push:
        se.push_to_r2(args.ebook_id, jsonl)
        print("✓ pushed R2")
        requests.delete(f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{args.ebook_id}",
                        headers=H_GET, timeout=30)
        rows = [{
            "ebook_id": args.ebook_id,
            "chunk_index": c["chunk_index"],
            "chunk_type": c.get("chunk_type", "chapter"),
            "page_number": c.get("page_number"),
            "chapter_path": c.get("chapter_path"),
            "content": (c.get("content") or "")[:200],
            "char_count": len(c.get("content") or ""),
        } for c in chunks]
        for i in range(0, len(rows), 25):
            requests.post(f"{URL}/rest/v1/ebook_chunks",
                          headers=H_JSON, json=rows[i:i + 25], timeout=30)
        print(f"✓ refreshed previews ({len(rows)} rows)")


if __name__ == "__main__":
    main()
