"""Auto-fix all T9 cross-work bleeds detected by scan_translated_book.

Strategy:
  1. Run T9 scan to find every chunk where source_text contains an h3
     heading attributing to a DIFFERENT NCX letter than the chunk's own
     title_en.
  2. For each bleed, locate the h3 position in both source_text (EN) and
     the parallel position in content (ZH). The two are paragraph-aligned
     by translate_ebook_to_zh.epub_to_chunks (each EPUB ITEM_DOCUMENT
     produces one source paragraph block + one ZH paragraph block in
     matching order).
  3. Slice the chunk at the h3 boundary — the prefix stays in the current
     chunk; the suffix (from h3 onwards) is the bled content to relocate.
  4. Determine the target chunk: the chunk whose title_en matches the
     attribute. Prepend the suffix to that chunk's content + source_text.
     If multiple candidates, pick the EARLIEST chunk_index with matching
     title_en that's AFTER the current chunk (intros go forward, not
     backward).
  5. Adjust footnotes dict / page_numbers / re-flow the heading text on
     the moved suffix.

Idempotent: re-running on a clean book is a no-op (T9 returns nothing).

Usage:
    python scripts/auto_fix_cross_bleeds.py <ebook_id> --dry-run
    python scripts/auto_fix_cross_bleeds.py <ebook_id>
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from pathlib import Path

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

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR")
                  or r"G:\我的雲端硬碟\資料\電子書\_chunks")

H3_RE = re.compile(r"^###\s+(.+?)$", re.M)
FOOTNOTE_SEP_RE = re.compile(r"^[—－\-]{15,}$", re.M)


def find_bleed_split(c: dict, ncx_index: list[dict]) -> Optional[dict]:
    """Inspect a chunk; if it contains a cross-bleed h3 in source_text,
    return {'en_split': pos, 'zh_split': pos, 'attributed_norm': str,
    'attributed_h3_en': str} describing where to cut. Returns None when
    chunk is clean.
    """
    if c.get("chunk_type") != "page":
        return None
    src = c.get("source_text") or ""
    zh = c.get("content") or ""
    title_en_norm = normalize_heading(c.get("title_en") or "")
    if not src or not zh or not title_en_norm:
        return None

    # Look up chunk's own NCX parent — same-parent intros (which
    # legitimately fold into a parent group's first letter) are NOT
    # cross-bleeds and must not trigger a split.
    chunk_parent = None
    for e in ncx_index:
        if e["en_letter_norm"] == title_en_norm:
            chunk_parent = e["parent"].upper()
            break
    if chunk_parent is None:
        b_toks_p = set(t for t in re.split(r"\W+", title_en_norm) if len(t) >= 3)
        for e in ncx_index:
            etoks = set(t for t in re.split(r"\W+", e["en_letter_norm"]) if len(t) >= 3)
            if etoks and len(b_toks_p & etoks) / max(len(b_toks_p | etoks), 1) >= 0.6:
                chunk_parent = e["parent"].upper()
                break

    # Walk EN h3 positions
    en_h3s = list(H3_RE.finditer(src))
    if not en_h3s:
        return None

    # The chunk's own h3 (matching title_en) is fine. Find the FIRST h3
    # that attributes to a DIFFERENT letter — that's the bleed boundary.
    for m in en_h3s:
        h_text = m.group(1).strip()
        attributed = attribute_heading(h_text, ncx_index)
        if not attributed:
            continue
        a = attributed["en_letter_norm"]
        b = title_en_norm
        a_toks = set(t for t in re.split(r"\W+", a) if len(t) >= 3)
        b_toks = set(t for t in re.split(r"\W+", b) if len(t) >= 3)
        overlap = len(a_toks & b_toks) / max(len(a_toks | b_toks), 1)
        same = (overlap >= 0.6) or (a in b) or (b in a)
        # Same-parent intros are not cross-bleeds
        if not same and chunk_parent and attributed.get("parent","").upper() == chunk_parent:
            same = True
        if same:
            continue
        # This is the first cross-bleed h3 → split here
        en_split = m.start()
        # Find the ZH h3 at the SAME ordinal position. Source and content
        # share paragraph-block ordering (translate_ebook_to_zh.epub_to_chunks
        # produces matched pairs); a 1:1 walk on `### ` works.
        ordinal = en_h3s.index(m)
        zh_h3s = list(H3_RE.finditer(zh))
        if ordinal >= len(zh_h3s):
            # ZH side has fewer h3 — fall back to proportional split
            zh_split = int(len(zh) * (en_split / max(len(src), 1)))
        else:
            zh_split = zh_h3s[ordinal].start()
        # The separator (em-dash run) that precedes the bleed belongs
        # with the prior chunk's footnotes; trim it off the suffix start.
        # Both ZH and EN: walk backwards from the split point past blank
        # lines + at most one separator paragraph, accept boundaries.
        return {
            "en_split": en_split,
            "zh_split": zh_split,
            "attributed_norm": a,
            "attributed_h3_en": h_text,
        }
    return None


from typing import Optional


_INTRO_NCX_RE = re.compile(r"^introductory\s+notes?\s+to\b")


def build_chunk_parent_map(chunks: list[dict],
                           ncx_index: list[dict]) -> dict[int, str]:
    """Pre-compute chunk_index → NCX parent_label by walking chunks and
    NCX entries in lockstep order. Resolves the title_en ambiguity that
    pops up when two different letters share the same English title
    (Polycarp 「Epistle to the Philippians」 vs Ignatius pseudo 「Epistle
    to the Philippians」). Each chunk gets THE parent that its position
    in the walk implies.
    """
    out: dict[int, str] = {}
    remaining = list(ncx_index)
    prev_title = None
    for c in chunks:
        if c.get("chunk_type") != "page":
            continue
        te = normalize_heading(c.get("title_en") or "")
        if not te:
            continue
        # Multi-page chunks of the SAME letter inherit prior parent
        if te == prev_title and out.get(c["chunk_index"] - 1):
            out[c["chunk_index"]] = out[c["chunk_index"] - 1]
            continue
        prev_title = te
        # Pop NCX entries until one matches te (skip intros that fold)
        while remaining:
            ncx = remaining[0]
            if _INTRO_NCX_RE.match(ncx["en_norm"]):
                remaining.pop(0)
                continue
            if ncx["en_letter_norm"] == te:
                out[c["chunk_index"]] = ncx["parent"].upper()
                remaining.pop(0)
                break
            # Token-overlap match
            te_toks = set(t for t in re.split(r"\W+", te) if len(t) >= 3)
            n_toks = set(t for t in re.split(r"\W+", ncx["en_letter_norm"]) if len(t) >= 3)
            if te_toks and n_toks and len(te_toks & n_toks) / max(len(te_toks | n_toks), 1) >= 0.6:
                out[c["chunk_index"]] = ncx["parent"].upper()
                remaining.pop(0)
                break
            # Not this one — skip and try next NCX entry
            remaining.pop(0)
    return out


def _chunk_parent(c: dict, ncx_index: list[dict],
                  parent_map: dict[int, str]) -> Optional[str]:
    return parent_map.get(c.get("chunk_index"))


def _attributed_parent(attributed_norm: str,
                       ncx_index: list[dict]) -> Optional[str]:
    """Resolve which NCX parent owns the attributed text."""
    for entry in ncx_index:
        if entry["en_letter_norm"] == attributed_norm:
            return entry["parent"].upper()
    attr_toks = set(t for t in re.split(r"\W+", attributed_norm) if len(t) >= 3)
    if not attr_toks:
        return None
    for entry in ncx_index:
        etoks = set(t for t in re.split(r"\W+", entry["en_letter_norm"]) if len(t) >= 3)
        if etoks and len(attr_toks & etoks) / max(len(attr_toks | etoks), 1) >= 0.6:
            return entry["parent"].upper()
    return None


def find_target_chunk(chunks: list[dict], current_idx: int,
                      attributed_norm: str,
                      ncx_index: list[dict],
                      parent_map: dict[int, str]) -> Optional[int]:
    """Find the chunk whose title_en best matches `attributed_norm`,
    REQUIRING the parent matches. Both forward and backward candidates
    are considered (e.g. 「Epistle of Polycarp to the Philippians」 intro
    sitting late in chunk 44 belongs back at chunk 11 — not forward)."""
    attr_parent = _attributed_parent(attributed_norm, ncx_index)
    target_toks = set(t for t in re.split(r"\W+", attributed_norm) if len(t) >= 3)
    candidates_forward: list[tuple[float, int]] = []
    candidates_backward: list[tuple[float, int]] = []
    for i, c in enumerate(chunks):
        if i == current_idx:
            continue
        if c.get("chunk_type") != "page":
            continue
        if attr_parent and parent_map.get(i) != attr_parent:
            continue
        te = normalize_heading(c.get("title_en") or "")
        if not te:
            continue
        te_toks = set(t for t in re.split(r"\W+", te) if len(t) >= 3)
        if not te_toks:
            continue
        overlap = len(target_toks & te_toks) / max(len(target_toks | te_toks), 1)
        if (overlap >= 0.6) or (te in attributed_norm) or (attributed_norm in te):
            (candidates_forward if i > current_idx else candidates_backward).append((overlap, i))
    if candidates_forward:
        candidates_forward.sort(key=lambda x: (-x[0], x[1]))
        return candidates_forward[0][1]
    if candidates_backward:
        candidates_backward.sort(key=lambda x: (-x[0], -x[1]))
        return candidates_backward[0][1]
    # Tier 2: parent fallback
    if attr_parent is None:
        return None
    for i in range(current_idx + 1, len(chunks)):
        if chunks[i].get("chunk_type") != "page":
            continue
        if parent_map.get(i) == attr_parent:
            return i
    for i in range(current_idx - 1, -1, -1):
        if chunks[i].get("chunk_type") != "page":
            continue
        if parent_map.get(i) == attr_parent:
            return i
    return None


def trim_trailing_separator(s: str) -> str:
    """Remove a trailing footnote-separator paragraph (and the blank line
    around it) — when we cut a chunk just before an h3, the preceding
    block is often a closing ——————— that「closed」the prior footnote
    section. Keep prior chunks tidy."""
    return re.sub(r"\n*[—－\-]{15,}\s*$", "", s).rstrip()


def apply_fix(c_src: dict, c_dst: dict, en_split: int, zh_split: int) -> dict:
    """Move the suffix from c_src to the front of c_dst. Returns stats."""
    en_full = c_src.get("source_text") or ""
    zh_full = c_src.get("content") or ""
    en_left = trim_trailing_separator(en_full[:en_split])
    en_right = en_full[en_split:].lstrip()
    zh_left = trim_trailing_separator(zh_full[:zh_split])
    zh_right = zh_full[zh_split:].lstrip()

    # Move footnote bodies that ONLY appear in the suffix
    src_fn = dict(c_src.get("footnotes") or {})
    dst_fn = dict(c_dst.get("footnotes") or {})
    moved_fn_keys: list[str] = []
    for k, v in list(src_fn.items()):
        nstr = str(k)
        # If the footnote body number appears in the suffix but NOT the
        # prefix, it belongs with the moved content.
        if not nstr.isdigit():
            continue
        n = int(nstr)
        # A footnote body line looks like `(N) body...` in content;
        # presence in zh_right == footnote belongs there.
        if re.search(rf"^\({n}\)\s", zh_right, re.M) and not re.search(rf"^\({n}\)\s", zh_left, re.M):
            dst_fn[k] = v
            del src_fn[k]
            moved_fn_keys.append(k)

    # Page numbers
    moved_pages = sorted({int(m.group(1))
                          for m in re.finditer(r"\{\{p:(\d+)\}\}", zh_right)})
    src_pages = sorted(set(c_src.get("page_numbers") or []) - set(moved_pages))
    dst_pages = sorted(set(c_dst.get("page_numbers") or []) | set(moved_pages))

    # Apply
    c_src["content"] = zh_left
    c_src["source_text"] = en_left
    c_src["footnotes"] = src_fn if src_fn else None
    c_src["page_numbers"] = src_pages
    if src_pages:
        c_src["page_number"] = src_pages[0]
    c_dst["content"] = zh_right + "\n\n" + (c_dst.get("content") or "").lstrip()
    c_dst["source_text"] = en_right + "\n\n" + (c_dst.get("source_text") or "").lstrip()
    c_dst["footnotes"] = dst_fn if dst_fn else None
    c_dst["page_numbers"] = dst_pages
    if dst_pages:
        c_dst["page_number"] = dst_pages[0]

    return {
        "zh_moved_chars": len(zh_right),
        "en_moved_chars": len(en_right),
        "fn_moved": moved_fn_keys,
        "pages_moved": moved_pages,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ebook_id")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--max-iterations", type=int, default=2,
                    help="Cap iterations. Default 2 — most ANF books need "
                         "1-2 passes. Multi-bleed chunks may need manual review.")
    args = ap.parse_args()

    book = fetch_book(args.ebook_id)
    if not book:
        sys.exit(f"no ebooks row for {args.ebook_id}")
    epub = find_epub(book)
    ncx_index = build_ncx_index(epub)
    print(f"Book: {book['title']}")
    print(f"NCX entries: {len(ncx_index)}")

    jsonl = CHUNKS_DIR / f"{args.ebook_id}.jsonl"
    chunks = [json.loads(l) for l in jsonl.read_text(encoding="utf-8").splitlines() if l]
    print(f"Loaded {len(chunks)} chunks")

    # Multiple bleed iterations — a chunk like c44 has 3 bleeds (one
    # h3 per next letter). After moving the FIRST bleed, the chunk
    # might still have a second bleed; we re-scan until stable.
    total_actions = 0
    iteration = 0
    while True:
        iteration += 1
        actions = []
        # Rebuild parent map each iteration — moves may shift chunk-letter
        # correspondences (rare but defensive).
        parent_map = build_chunk_parent_map(chunks, ncx_index)
        # Each chunk may be source OR destination at most once per
        # iteration. Without this, moving content into chunk M makes
        # M scannable later in the same loop with content that doesn't
        # belong to it natively — leading to ping-pong (chunk N → M then
        # immediately M → N because the moved content brought a stray h3).
        touched: set[int] = set()
        for i, c in enumerate(chunks):
            if i in touched:
                continue
            split = find_bleed_split(c, ncx_index)
            if not split:
                continue
            target_idx = find_target_chunk(chunks, i, split["attributed_norm"], ncx_index, parent_map)
            if target_idx is None:
                actions.append({"chunk": i, "action": "no_target",
                                "attributed": split["attributed_norm"]})
                continue
            stats = apply_fix(chunks[i], chunks[target_idx],
                              split["en_split"], split["zh_split"])
            actions.append({
                "chunk": i, "target": target_idx,
                "attributed": split["attributed_norm"][:40],
                **stats,
            })
            touched.add(i)
            touched.add(target_idx)
        if not actions:
            break
        print(f"\n--- iteration {iteration}: {len(actions)} actions ---")
        for a in actions:
            if a.get("action") == "no_target":
                print(f"  ⚠ chunk {a['chunk']}: bleed → '{a['attributed']}' but NO matching target chunk")
            else:
                print(f"  chunk {a['chunk']:3d} → chunk {a['target']:3d}: "
                      f"{a['zh_moved_chars']} ZH chars, "
                      f"{a['en_moved_chars']} EN chars, "
                      f"fn={len(a['fn_moved'])}, pages={a['pages_moved']} "
                      f"({a['attributed']})")
        # Bail-safety: if any iteration produced ONLY no_target actions
        # (no actual moves), break to avoid infinite loop.
        moved = [a for a in actions if a.get("action") != "no_target"]
        if not moved:
            break
        total_actions += len(moved)
        if iteration >= args.max_iterations:
            print(f"  ⚠ hit max {args.max_iterations} iterations, stopping")
            break

    print(f"\n✓ total moves: {total_actions}")

    if args.dry_run:
        print("(dry-run; not writing)")
        return

    with open(jsonl, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"✓ wrote {jsonl.name}")

    if not args.no_push:
        se.push_to_r2(args.ebook_id, jsonl)
        print("✓ pushed R2")
        # Refresh ALL previews — many chunks may have changed
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
