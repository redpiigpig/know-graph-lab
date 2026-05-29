"""
Phase 5 — Entry-level consolidation.

Merges DH-level chunks into TOC-entry-level chunks so that

  - 一份完整信經 (例：DH 3-5 「埃及(Egypt)致會典章」三條版本) → 1 chunk
  - 一份完整新教信條 (例：DH 5503-5523 「奧斯堡信條」21 條) → 1 chunk
  - 一封完整書信／一道教宗詔書 → 1 chunk

The TOC entries.json from `_denzinger_parse_toc.py` defines the document
boundaries. We walk every entry and fold every main-JSONL chunk whose
`dh_number` falls in (dh_start..dh_end) into a single merged chunk.

Output is overwritten on `_chunks/{id}.jsonl`, pushed to R2, and
`ebook_chunks` is repopulated.

Usage:
  python scripts/_denzinger_consolidate_entries.py --dry-run
  python scripts/_denzinger_consolidate_entries.py            # write JSONL + R2 + DB
  python scripts/_denzinger_consolidate_entries.py --no-db    # skip DB patch
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ocr_with_gemini import (  # noqa: E402
    CHUNKS_DIR,
    URL,
    H,
    push_to_r2,
    update_book_done,
)
import requests  # noqa: E402

BOOK_ID = "568726d3-967e-457a-ab69-7452b21d606f"
MAIN_JSONL = CHUNKS_DIR / f"{BOOK_ID}.jsonl"
PRE_MERGE_BACKUP = CHUNKS_DIR / f"{BOOK_ID}.jsonl.preentrymerge.bak"
TOC_DIR = Path(__file__).parent / "_denzinger_toc"


def load_chunks(path: Path) -> list[dict]:
    out: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def load_entries() -> list[dict]:
    p = TOC_DIR / "entries.json"
    if not p.exists():
        print(f"ERROR: {p} missing — run _denzinger_parse_toc.py first.", file=sys.stderr)
        sys.exit(2)
    return json.loads(p.read_text(encoding="utf-8"))


def build_dh_to_entry(entries: list[dict]) -> dict[int, dict]:
    """{dh: entry_dict} — parent-range-wins so a 「3-5」 parent entry
    captures DH 3/4/5 even when sub-entries 「3 a)」「4 b)」「5 c)」 also
    exist in entries.json. Otherwise the sub-entries shadow the parent
    and we end up with 3 chunks (a/b/c) per document instead of 1.
    Sort by range width DESCENDING; first-write-wins picks the parent."""
    width_sorted = sorted(
        entries,
        key=lambda e: -((e.get("dh_end") or e.get("dh_start") or 0)
                        - (e.get("dh_start") or 0)),
    )
    out: dict[int, dict] = {}
    for e in width_sorted:
        s, t = e.get("dh_start"), e.get("dh_end") or e.get("dh_start")
        if s is None:
            continue
        for n in range(s, t + 1):
            out.setdefault(n, e)
    return out


def _entry_key(e: dict) -> tuple:
    return (e.get("dh_start"), e.get("dh_end"), e.get("title"))


def consolidate(chunks: list[dict], entries: list[dict]) -> list[dict]:
    """Two-pass merger.

    Pass A: bucket every entry chunk by its entries.json entry key. Stray
    DHs with no matching entry go to a `_stray` bucket and pass through
    as-is. Non-entry chunks (front matter / header / orphan commentary)
    also pass through unchanged.

    Pass B: emit chunks in PAGE ORDER. Each TOC entry's merged chunk
    inherits the entry's earliest page; non-entry chunks keep their own
    page. This prevents an out-of-place DH near the appendix from
    splitting the Augsburg merge in two.
    """
    dh_to_entry = build_dh_to_entry(entries)

    passthroughs: list[dict] = []  # non-entry chunks, render in place
    buckets: dict[tuple, dict] = {}  # entry_key → merged chunk

    for c in chunks:
        dh = c.get("dh_number")
        sec = c.get("section_type")

        if sec != "entry" or not isinstance(dh, int):
            passthroughs.append(dict(c))
            continue

        e = dh_to_entry.get(dh)
        if e is None:
            passthroughs.append(dict(c))
            continue

        key = _entry_key(e)
        if key not in buckets:
            seed = dict(c)
            seed["_entry_dh_token"] = e.get("dh_token") or str(dh)
            seed["_entry_title"] = e.get("title")
            seed["_entry_part"] = e.get("part")
            seed["_entry_volume"] = e.get("volume")
            seed["page_numbers"] = list(c.get("page_numbers") or [c.get("page_number")])
            if (e.get("dh_end") or e.get("dh_start")) != e.get("dh_start"):
                seed.pop("dh_number", None)
            buckets[key] = seed
        else:
            merged = buckets[key]

            def _append(field, glue="\n\n"):
                a = (merged.get(field) or "").strip()
                b = (c.get(field) or "").strip()
                if not b:
                    return
                merged[field] = (a + glue + b).strip() if a else b

            _append("content")
            _append("source_text")
            merged["page_numbers"].extend(
                c.get("page_numbers") or [c.get("page_number")]
            )

    # Pass B: emit by earliest page number, interleaving merged entries
    # with passthroughs. Each bucket gets sort key = min(its page_numbers);
    # passthroughs get sort key = their page_number; ties broken by the
    # original chunk_index so stable across re-runs.
    items: list[tuple[int, int, dict]] = []
    for c in passthroughs:
        pn = c.get("page_number") or (c.get("page_numbers") or [99999])[0] or 99999
        items.append((pn, c.get("chunk_index", 0), c))
    for merged in buckets.values():
        pages = [p for p in merged.get("page_numbers") or [] if isinstance(p, int)]
        pn = min(pages) if pages else 99999
        items.append((pn, -1, merged))  # entry merges before passthroughs on same page

    items.sort(key=lambda t: (t[0], t[1]))
    out = [t[2] for t in items]

    # Renumber chunk_index, dedup page_numbers, rewrite chapter_path on merged
    # chunks (label them by the TOC entry's full DH token, e.g. "DH 5503-5523
    # 奧斯堡信條"), and clean up auxiliary fields.
    for i, c in enumerate(out):
        c["chunk_index"] = i
        if c.get("_entry_title"):
            tok = c.pop("_entry_dh_token", None) or ""
            title = c.pop("_entry_title")
            c["chapter_path"] = f"DH {tok} {title}" if tok else title
            c["volume"] = c.pop("_entry_volume", None) or c.get("volume")
            c["parent_volume"] = c.pop("_entry_part", None) or c.get("parent_volume")
        c["page_numbers"] = sorted(
            {p for p in (c.get("page_numbers") or []) if isinstance(p, int)}
        )
        # Set page_number to the first page in the merged range.
        if c["page_numbers"]:
            c["page_number"] = c["page_numbers"][0]

    return out


def push_db(chunks: list[dict]) -> None:
    print(f"Deleting old rows…")
    r = requests.delete(
        f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{BOOK_ID}",
        headers={**H, "Prefer": "return=minimal"},
        timeout=120,
    )
    if r.status_code >= 300:
        print(f"⚠ delete returned {r.status_code}: {r.text[:200]}")

    print(f"Inserting {len(chunks)} entry-merged rows…")
    rows = []
    for c in chunks:
        content = c.get("content") or ""
        rows.append({
            "ebook_id": BOOK_ID,
            "chunk_index": c["chunk_index"],
            "chunk_type": c.get("chunk_type"),
            "page_number": c.get("page_number"),
            "chapter_path": c.get("chapter_path"),
            "content": content,
            "char_count": len(content) + len((c.get("source_text") or "")),
            "section_type": c.get("section_type"),
            "source_text": c.get("source_text"),
            "source_lang": c.get("source_lang"),
            "dh_number": c.get("dh_number"),
            "page_numbers": c.get("page_numbers") or [],
        })

    # Adaptive batching — Supabase free tier hits statement timeout (57014)
    # at 25-row batches when entries.json fold creates 100-200KB rows. Step
    # down on timeout.
    BATCH_SIZES = [25, 10, 5, 1]
    i = 0
    inserted = 0
    while i < len(rows):
        for bs in BATCH_SIZES:
            batch = rows[i:i + bs]
            r = requests.post(
                f"{URL}/rest/v1/ebook_chunks",
                headers={**H, "Prefer": "return=minimal"},
                json=batch,
                timeout=180,
            )
            if r.status_code in (200, 201, 204):
                i += bs
                inserted += len(batch)
                if inserted % 100 < bs:
                    print(f"  inserted {inserted}/{len(rows)}")
                break
            if r.status_code == 500 and "57014" in r.text:
                continue
            print(f"⚠ insert at {i} (bs={bs}) returned {r.status_code}: {r.text[:200]}")
            i += bs
            break
        else:
            print(f"⚠ row {i} failed even at batch size 1, skipping")
            i += 1
    print(f"✓ DB repopulated with {inserted}/{len(rows)} entry-merged rows")

    requests.patch(
        f"{URL}/rest/v1/ebooks?id=eq.{BOOK_ID}",
        headers=H,
        json={
            "chunk_count": len(rows),
            "total_chars": sum(len((c.get("content") or "")) for c in chunks),
        },
        timeout=30,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="report only")
    ap.add_argument("--no-db", action="store_true", help="skip DB patch")
    ap.add_argument("--no-r2", action="store_true", help="skip R2 push")
    args = ap.parse_args()

    chunks = load_chunks(MAIN_JSONL)
    entries = load_entries()
    print(f"Loaded {len(chunks)} chunks from main JSONL")
    print(f"Loaded {len(entries)} TOC entries")

    merged = consolidate(chunks, entries)
    print(f"\nConsolidated: {len(chunks)} → {len(merged)} chunks "
          f"({len(chunks) - len(merged)} merged away)")

    # Show a sample of merged-multi-DH chunks (where dh_token contains "-")
    multi = [c for c in merged if c.get("chapter_path", "").startswith("DH ")
             and "-" in c["chapter_path"].split(" ", 2)[1] if c.get("chapter_path", "").startswith("DH ")]
    print(f"Multi-DH merged entries: {len(multi)}")
    print(f"\n─ Sample multi-DH merges ─")
    for c in multi[:8]:
        zh_len = len((c.get("content") or ""))
        lat_len = len((c.get("source_text") or ""))
        print(f"  [{c['chunk_index']:04d}] {c['chapter_path'][:60]} | zh={zh_len:5} lat={lat_len:5} | pages={c.get('page_numbers',[])[:3]}…")

    if args.dry_run:
        print("\n[DRY RUN] no writes.")
        return 0

    # Backup current main JSONL
    if not PRE_MERGE_BACKUP.exists():
        shutil.copyfile(MAIN_JSONL, PRE_MERGE_BACKUP)
        print(f"\n✓ Backed up pre-merge main JSONL → {PRE_MERGE_BACKUP.name}")

    # Write new main JSONL
    with MAIN_JSONL.open("w", encoding="utf-8") as f:
        for c in merged:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"✓ Wrote {len(merged)} entry-merged chunks → {MAIN_JSONL.name}")

    if not args.no_r2:
        push_to_r2(BOOK_ID, MAIN_JSONL)
        print(f"✓ R2 push ok")

    if not args.no_db:
        push_db(merged)

    return 0


if __name__ == "__main__":
    sys.exit(main())
