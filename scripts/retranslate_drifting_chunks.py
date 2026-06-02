"""Re-translate only the bilingual chunks whose 逐段對照 alignment drifted
(content ZH paragraph count vs source_text EN paragraph count past the gate
threshold), in place, with the paragraph-preserving PROMPT_TMPL.

Why this exists: translate_ebook_to_zh.py's --resume *skips* chunks already
in the JSONL (matched by title_en), so it will never redo an already-written
but misaligned chunk. This targets exactly the drifting chunks surfaced by
`scan_translated_book.py --gate`, re-translates their source_text, and rewrites
just those chunks' `content` — keeping chunk_index / page_number / source_text
/ chapter_path / title_en untouched. Then mirrors to R2 + refreshes previews.

Usage:
  python scripts/retranslate_drifting_chunks.py <ebook_id> --dry-run
  python scripts/retranslate_drifting_chunks.py <ebook_id>
  python scripts/retranslate_drifting_chunks.py <ebook_id> --only 77,79,96
  python scripts/retranslate_drifting_chunks.py <ebook_id> --engine gemini --threshold 0.25

Engine defaults to gemini (gemini_with_haiku_fallback). Safe to run alongside
another book's translate worker — different ebook_id = no JSONL race; only
Gemini key quota is shared.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import translate_ebook_to_zh as t   # engine fns + URL/headers + split_oversized
import scan_translated_book as scan  # alignment_gate + paragraph_drift
import standardize_ebook as se       # to_traditional + push_to_r2
import standardize_pdf_lite as pl    # collapse_cjk_spacing

# Books that must not be touched (a live translate worker owns the JSONL).
ACTIVE_LOCKED = {"a7e5956e-8851-4d0f-b3d2-1f823d1bdc81"}  # vol28 in progress


def load_jsonl_defensive(ebook_id: str) -> list[dict]:
    fn = t.CHUNKS_DIR / f"{ebook_id}.jsonl"
    if not fn.exists():
        sys.exit(f"JSONL not found: {fn}")
    chunks = []
    for line in fn.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                chunks.append(json.loads(line))
            except Exception:
                pass
    return chunks


def pick_translator(engine: str):
    if engine == "sonnet":
        return t.sonnet_translate
    if engine == "haiku":
        return t.haiku_translate
    return t.gemini_with_haiku_fallback  # gemini default


def retranslate_chunk(chunk: dict, translator) -> str:
    en = chunk.get("source_text") or ""
    pieces = t.split_oversized(en)
    parts = [translator(p) for p in pieces]
    zh = "\n\n".join(parts)
    zh = se.to_traditional(zh)
    zh = pl.collapse_cjk_spacing(zh)
    return zh


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ebook_id")
    ap.add_argument("--threshold", type=float, default=scan.BILINGUAL_DRIFT_RATIO)
    ap.add_argument("--engine", default="gemini", choices=["gemini", "haiku", "sonnet"])
    ap.add_argument("--only", help="comma-separated chunk_index list to limit to")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-write", action="store_true",
                    help="re-translate + show before/after but don't write JSONL/R2/DB")
    args = ap.parse_args()

    eid = args.ebook_id
    if eid in ACTIVE_LOCKED:
        sys.exit(f"REFUSING: {eid} is owned by a live translate worker — don't touch.")

    chunks = load_jsonl_defensive(eid)
    flagged = scan.alignment_gate(chunks, args.threshold)
    if args.only:
        keep = {int(x) for x in args.only.split(",")}
        flagged = [f for f in flagged if f["chunk_index"] in keep]
    if not flagged:
        print("No drifting prose chunks — nothing to do.")
        return

    by_idx = {c.get("chunk_index"): c for c in chunks}
    print(f"{eid}: {len(flagged)} chunk(s) to re-translate (engine={args.engine}, "
          f"threshold={args.threshold})")
    for f in flagged:
        print(f"  · chunk {f['chunk_index']} [{(f['chapter_path'] or '')[:40]}]: "
              f"ZH={f['zh_paras']} EN={f['en_paras']} drift={f['drift']}")
    if args.dry_run:
        print("\n(dry-run — no translation calls)")
        return

    translator = pick_translator(args.engine)
    results = []
    for f in flagged:
        idx = f["chunk_index"]
        c = by_idx.get(idx)
        if not c or not (c.get("source_text") or "").strip():
            continue
        print(f"\n[chunk {idx}] re-translating {f['en_paras']} EN paras …", flush=True)
        try:
            new_zh = retranslate_chunk(c, translator)
        except Exception as e:
            print(f"  ⚠ failed: {e}", file=sys.stderr, flush=True)
            results.append((idx, f["drift"], None, "FAILED"))
            continue
        new_drift = scan.paragraph_drift(new_zh, c.get("source_text") or "")
        old_drift = f["drift"]
        c["content"] = new_zh
        status = "ok" if (new_drift is not None and new_drift <= args.threshold) else "STILL-DRIFTS"
        results.append((idx, old_drift, new_drift, status))
        nd = "n/a" if new_drift is None else f"{new_drift:.3f}"
        print(f"  drift {old_drift} → {nd}  [{status}]  ({len(new_zh)} zh chars)", flush=True)

    print("\n=== summary ===")
    for idx, od, nd, st in results:
        nds = "n/a" if nd is None else f"{nd:.3f}"
        print(f"  chunk {idx}: {od} → {nds}  {st}")

    if args.no_write:
        print("\n(--no-write: JSONL/R2/DB untouched)")
        return

    # Rewrite JSONL in place (chunk_index/order preserved — content swapped).
    out_path = t.CHUNKS_DIR / f"{eid}.jsonl"
    with open(out_path, "w", encoding="utf-8") as fh:
        for c in chunks:
            fh.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"\n✓ wrote {out_path} ({out_path.stat().st_size // 1024} KB)")

    try:
        se.push_to_r2(eid, out_path)
        print("✓ pushed R2")
    except Exception as e:
        print(f"⚠ R2 push failed: {e}", file=sys.stderr)

    total_chars = sum(len(c.get("content") or "") for c in chunks)
    now = datetime.utcnow().isoformat() + "Z"
    requests.patch(f"{t.URL}/rest/v1/ebooks?id=eq.{eid}", headers=t.H_JSON,
                   json={"total_chars": total_chars, "standardized_at": now},
                   timeout=30).raise_for_status()
    print("✓ ebooks row updated")

    # Refresh previews only for the chunks we changed (cheap, no full DELETE).
    changed = {idx for idx, _, _, st in results if st != "FAILED"}
    for c in chunks:
        if c.get("chunk_index") not in changed:
            continue
        ci = c["chunk_index"]
        requests.delete(
            f"{t.URL}/rest/v1/ebook_chunks?ebook_id=eq.{eid}&chunk_index=eq.{ci}",
            headers=t.H_GET, timeout=30)
        row = {
            "ebook_id": eid, "chunk_index": ci,
            "chunk_type": c.get("chunk_type"), "page_number": c.get("page_number"),
            "chapter_path": c.get("chapter_path"),
            "content": (c.get("content") or "")[:200],
            "char_count": len(c.get("content") or ""),
        }
        rr = requests.post(f"{t.URL}/rest/v1/ebook_chunks", headers=t.H_JSON,
                           json=[row], timeout=60)
        if not rr.ok:
            print(f"  ⚠ preview chunk {ci}: {rr.status_code} {rr.text[:120]}", file=sys.stderr)
    print(f"✓ refreshed {len(changed)} preview row(s)")


if __name__ == "__main__":
    main()
