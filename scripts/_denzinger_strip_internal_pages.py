"""
Strip internal page-footer residue from Denzinger chunk content.

After consolidation the chunk content still contains OCR'd page footers
like 「- 5 -」「-6-」「(28)」「(III) 92 99」 — these are page numbers from
the original book that landed inline when pages were folded together.
They turn the reading experience into "wait, what's this number?"
every paragraph.

We pass each chunk's `content` and `source_text` through a line-level
filter that drops the standalone page-footer patterns.

Usage:
  python scripts/_denzinger_strip_internal_pages.py --dry-run
  python scripts/_denzinger_strip_internal_pages.py            # write + R2 + DB
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ocr_with_gemini import CHUNKS_DIR, URL, H, push_to_r2  # noqa: E402
import requests  # noqa: E402

BOOK_ID = "568726d3-967e-457a-ab69-7452b21d606f"
MAIN_JSONL = CHUNKS_DIR / f"{BOOK_ID}.jsonl"
PRE_STRIP_BACKUP = CHUNKS_DIR / f"{BOOK_ID}.jsonl.prestrip.bak"


# Standalone page footer patterns — strip the entire LINE if it matches.
LINE_STRIPS: list[re.Pattern] = [
    re.compile(r"^\s*-\s*\d{1,4}\s*-\s*$"),         # - 5 - , -6-
    re.compile(r"^\s*\(\s*\d{1,4}\s*\)\s*$"),       # (28)
    re.compile(r"^\s*\d{1,4}\s*$"),                 # bare 5
    re.compile(r"^\s*[一二三四五六七八九十百〇]{1,5}\s*$"),  # 「一」「廿」 (rare)
    re.compile(r"^\s*【?[註注释]\s*\d{1,4}】?\s*$"),   # 「註 5」「【註1】」 isolated
]

# Trailing-noise patterns inside an otherwise-OK line — strip just the tail.
TRAILING_STRIPS: list[re.Pattern] = [
    # 「.....NNN」or 「。。NNN」 dot leader + page number AT END OF LINE
    re.compile(r"\s*[\.…。]{3,}\s*\d{1,4}\s*$"),
    # Three or more contiguous wide-space + digit at end-of-line (TOC tail
    # left over from header chunks).
    re.compile(r"[　\s]{6,}\d{1,4}\s*$"),
]


def strip_text(text: str) -> tuple[str, int]:
    """Apply both filters; returns (cleaned, stripped_line_count)."""
    if not text:
        return text, 0
    out_lines: list[str] = []
    stripped = 0
    for ln in text.split("\n"):
        # whole-line drop
        if any(p.match(ln) for p in LINE_STRIPS):
            stripped += 1
            continue
        # trailing trim
        new_ln = ln
        for p in TRAILING_STRIPS:
            new_ln = p.sub("", new_ln)
        out_lines.append(new_ln)
    # collapse triple-or-more blank lines into a single blank
    cleaned = "\n".join(out_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned, stripped


def load_chunks() -> list[dict]:
    out: list[dict] = []
    with MAIN_JSONL.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def push_db(chunks: list[dict]) -> None:
    print("Patching DB rows…")
    import time
    t0 = time.time()
    n = 0
    for c in chunks:
        idx = c["chunk_index"]
        payload = {
            "content": c.get("content") or "",
            "source_text": c.get("source_text"),
        }
        r = requests.patch(
            f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{BOOK_ID}&chunk_index=eq.{idx}",
            headers=H,
            json=payload,
            timeout=60,
        )
        if r.status_code in (200, 204):
            n += 1
        else:
            print(f"  ⚠ row {idx} → {r.status_code}: {r.text[:120]}")
        if n and n % 100 == 0:
            print(f"  patched {n}/{len(chunks)} ({time.time()-t0:.0f}s)")
    print(f"✓ patched {n}/{len(chunks)} DB rows in {time.time()-t0:.0f}s")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-db", action="store_true")
    ap.add_argument("--no-r2", action="store_true")
    args = ap.parse_args()

    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks")

    total_zh_stripped = 0
    total_lat_stripped = 0
    for c in chunks:
        zh_new, zh_strip = strip_text(c.get("content") or "")
        lat_new, lat_strip = strip_text(c.get("source_text") or "")
        if zh_strip:
            c["content"] = zh_new
            total_zh_stripped += zh_strip
        if lat_strip:
            c["source_text"] = lat_new
            total_lat_stripped += lat_strip

    print(f"Stripped lines  : zh={total_zh_stripped}, lat={total_lat_stripped}")

    if args.dry_run:
        # Print a sample diff
        print("\n─ Sample chunk content after strip ─")
        for c in chunks[6:10]:
            print(f"\n[{c['chunk_index']:04d}] {c.get('chapter_path','')[:50]}")
            sample = (c.get("content") or "")[:600]
            print(sample)
        return 0

    if not PRE_STRIP_BACKUP.exists():
        shutil.copyfile(MAIN_JSONL, PRE_STRIP_BACKUP)
        print(f"✓ Backed up → {PRE_STRIP_BACKUP.name}")

    with MAIN_JSONL.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"✓ Wrote main JSONL ({len(chunks)} chunks)")

    if not args.no_r2:
        push_to_r2(BOOK_ID, MAIN_JSONL)
        print("✓ R2 push ok")

    if not args.no_db:
        push_db(chunks)

    return 0


if __name__ == "__main__":
    sys.exit(main())
