"""Plan B v1 — font-driven PDF chapter detection.

For PDFs with no usable TOC bookmarks (~285 books, the residual after
standardize_pdf.py [Plan B v0] runs). Reads font metadata via PyMuPDF
`page.get_text('dict')`, builds a body-text size baseline, then classifies
larger / bolder spans as headings to derive chapter chunks.

This is a PROTOTYPE — single-book runner with diagnostic output. The
production batch path lands once thresholds + heuristics are tuned on real
books from the no-TOC pool.

Usage:
  python scripts/standardize_pdf_v1.py <ebook_id>             # analyze + write
  python scripts/standardize_pdf_v1.py <ebook_id> --dry-run   # analysis only
  python scripts/standardize_pdf_v1.py <ebook_id> --inspect   # font histogram + sample headings
"""
import os
import sys
import json
import re
import argparse
from pathlib import Path
from collections import Counter, defaultdict
from typing import Iterable

import fitz  # PyMuPDF
import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

# Reuse Plan A helpers for s2tw + CJK-spacing cleanup so v1 output matches
# the rest of the pipeline.
sys.path.insert(0, str(Path(__file__).parent))
import standardize_pdf_lite as pl  # noqa: E402
import standardize_ebook as se  # noqa: E402

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR") or r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")

# Bold/italic flag bits in PyMuPDF span dict
FLAG_ITALIC = 1 << 1   # 2
FLAG_BOLD = 1 << 4     # 16

MAX_HEADING_LEN = 30
MIN_BODY_BUCKET_RATIO = 0.20  # body bucket must be >=20% of all chars
HEADING_SIZE_BUMP_H2 = 6.0
HEADING_SIZE_BUMP_H3 = 3.0
HEADING_SIZE_BUMP_H4 = 1.0


def fetch_book(ebook_id: str) -> dict:
    r = requests.get(f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}&select=*", headers=H_GET, timeout=30)
    r.raise_for_status()
    rows = r.json()
    if not rows:
        raise SystemExit(f"no ebooks row for {ebook_id}")
    return rows[0]


def iter_spans(doc: fitz.Document) -> Iterable[tuple[int, dict]]:
    """Yield (page_index, span_dict) for every span in the doc.
    span fields used: text, size, font, flags, bbox."""
    for page_idx in range(doc.page_count):
        page = doc[page_idx]
        d = page.get_text("dict")
        for block in d.get("blocks", []):
            if block.get("type") != 0:
                continue  # 0 == text
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    yield page_idx, span


def body_size(doc: fitz.Document) -> float:
    """Most common font size by total CHARACTERS (not span count) — body text
    dominates char volume; headings are visually loud but tiny in chars."""
    counter: Counter[float] = Counter()
    for _, span in iter_spans(doc):
        text = span.get("text", "")
        if not text.strip():
            continue
        size = round(float(span.get("size", 0)), 1)
        counter[size] += len(text)
    if not counter:
        raise ValueError("no text spans")
    total = sum(counter.values())
    top = counter.most_common(1)[0]
    if top[1] / total < MIN_BODY_BUCKET_RATIO:
        # Body bucket too small — likely image-only PDF or font-mangled
        raise ValueError(f"body bucket too small: {top[1]/total:.0%} (need ≥{MIN_BODY_BUCKET_RATIO:.0%})")
    return top[0]


def classify_span(span: dict, body: float) -> str | None:
    """Return 'h2' / 'h3' / 'h4' / None for a span. Heading rules:
    - size >= body + bumps + short text (≤MAX_HEADING_LEN)
    - bold + short text → h3"""
    text = span.get("text", "").strip()
    if not text or len(text) > MAX_HEADING_LEN:
        return None
    size = float(span.get("size", 0))
    flags = int(span.get("flags", 0))
    if size >= body + HEADING_SIZE_BUMP_H2:
        return "h2"
    if size >= body + HEADING_SIZE_BUMP_H3:
        return "h3"
    if size >= body + HEADING_SIZE_BUMP_H4:
        return "h4"
    if flags & FLAG_BOLD and len(text) <= MAX_HEADING_LEN // 2:
        return "h3"
    return None


def detect_repeated_lines(doc: fitz.Document, top_n: int = 5) -> set[str]:
    """Find text that appears at near-identical y-bbox on most pages
    (running headers/footers)."""
    line_freq: Counter[tuple[str, int]] = Counter()
    pages_with_line: defaultdict[tuple[str, int], set[int]] = defaultdict(set)
    for page_idx in range(doc.page_count):
        page = doc[page_idx]
        d = page.get_text("dict")
        for block in d.get("blocks", []):
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                text = " ".join(s.get("text", "").strip() for s in line.get("spans", [])).strip()
                if not text or len(text) > 80:
                    continue
                bbox = line.get("bbox") or [0, 0, 0, 0]
                y = int(bbox[1])  # bucket y by integer px
                key = (text, y // 10 * 10)  # 10-px bucket
                line_freq[key] += 1
                pages_with_line[key].add(page_idx)
    repeated = set()
    threshold = max(3, doc.page_count // 3)
    for key, count in line_freq.items():
        if count >= threshold:
            repeated.add(key[0])
    return repeated


def extract_chunks(doc: fitz.Document, body: float, repeated: set[str]) -> list[dict]:
    """Walk pages, collect content into chunks. New chunk at every h2."""
    chunks: list[dict] = []
    current = {
        "chunk_index": 0,
        "chunk_type": "chapter",
        "page_number": None,
        "page_range": [None, None],
        "chapter_path": "前置內容",
        "format": "text",
        "content_lines": [],
    }

    def flush():
        if not current["content_lines"]:
            return
        content = "\n".join(current["content_lines"]).strip()
        content = se.to_traditional(content)
        content = pl.collapse_cjk_spacing(content)
        current["content"] = content
        current.pop("content_lines", None)
        if current["page_range"][0] is not None:
            current["page_number"] = current["page_range"][0]
        chunks.append(dict(current))

    def new_chunk(title: str, page_idx: int):
        flush()
        tw_title = se.to_traditional(title).strip()
        current["chunk_index"] = len(chunks)
        current["chapter_path"] = tw_title
        current["page_range"] = [page_idx + 1, page_idx + 1]
        current["content_lines"] = [f"## {tw_title}"]

    for page_idx in range(doc.page_count):
        page = doc[page_idx]
        d = page.get_text("dict")
        # Track page_range
        if current["page_range"][0] is None:
            current["page_range"] = [page_idx + 1, page_idx + 1]
        else:
            current["page_range"][1] = page_idx + 1

        for block in d.get("blocks", []):
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                line_text = " ".join(s.get("text", "") for s in spans).strip()
                if not line_text or line_text in repeated:
                    continue
                # Use first span to classify
                first = spans[0]
                lvl = classify_span(first, body)
                if lvl == "h2":
                    new_chunk(line_text, page_idx)
                elif lvl == "h3":
                    current["content_lines"].append(f"\n### {line_text}\n")
                elif lvl == "h4":
                    current["content_lines"].append(f"\n#### {line_text}\n")
                else:
                    current["content_lines"].append(line_text)
    flush()
    # Re-number contiguously
    for i, c in enumerate(chunks):
        c["chunk_index"] = i
    return chunks


def inspect(book: dict) -> None:
    pdf_path = Path(book["file_path"])
    print(f"Book: {book['title']}")
    print(f"Path: {pdf_path}")
    print(f"Total pages: {book.get('total_pages')}")
    doc = fitz.open(pdf_path)
    print(f"PyMuPDF page_count: {doc.page_count}")
    print(f"TOC bookmarks: {len(doc.get_toc())}")
    print()

    # Font histogram
    counter: Counter[float] = Counter()
    for _, span in iter_spans(doc):
        text = span.get("text", "")
        if not text.strip():
            continue
        size = round(float(span.get("size", 0)), 1)
        counter[size] += len(text)
    total = sum(counter.values())
    print(f"Font size histogram (top 10 by chars):")
    for size, n in counter.most_common(10):
        pct = n / total * 100
        bar = "#" * int(pct / 2)
        print(f"  {size:>5.1f}pt  {n:>8}  {pct:>5.1f}%  {bar}")
    print()

    try:
        body = body_size(doc)
        print(f"Body size: {body}pt")
    except ValueError as e:
        print(f"Body detection failed: {e}")
        return

    # Find sample headings at each level
    samples = defaultdict(list)
    for page_idx, span in iter_spans(doc):
        lvl = classify_span(span, body)
        if lvl:
            text = span["text"].strip()
            if text and len(samples[lvl]) < 8:
                samples[lvl].append((page_idx + 1, span["size"], text[:50]))
    print(f"\nSample headings detected:")
    for lvl in ("h2", "h3", "h4"):
        print(f"  {lvl}: {len(samples[lvl])}")
        for page, size, text in samples[lvl]:
            print(f"    p{page:>3}  {size:>5.1f}pt  {text}")
    print()

    repeated = detect_repeated_lines(doc)
    print(f"Repeated header/footer lines: {len(repeated)}")
    for line in list(repeated)[:5]:
        print(f"  · {line[:60]}")


def standardize(book: dict, dry_run: bool) -> None:
    pdf_path = Path(book["file_path"])
    doc = fitz.open(pdf_path)
    if doc.get_toc():
        print("⚠ PDF has TOC bookmarks — use Plan B v0 (standardize_pdf.py) instead.")
        return
    try:
        body = body_size(doc)
    except ValueError as e:
        print(f"⚠ {e} — Plan B v1 cannot process this book")
        return
    print(f"Body size: {body}pt")
    repeated = detect_repeated_lines(doc)
    print(f"Drop {len(repeated)} repeated header/footer lines")
    chunks = extract_chunks(doc, body, repeated)
    print(f"Produced {len(chunks)} chunks")
    if dry_run:
        for i in (0, 1, len(chunks) // 2, len(chunks) - 1):
            if 0 <= i < len(chunks):
                c = chunks[i]
                print(f"\n[{i}] pp{c['page_range'][0]}-{c['page_range'][1]}  {c['chapter_path']}")
                print(c["content"][:200])
        return

    out = CHUNKS_DIR / f"{book['id']}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"✓ wrote {out}")

    try:
        se.push_to_r2(book["id"], out)
        print("  ✓ pushed R2")
    except Exception as e:
        print(f"  ⚠ R2 push failed: {e}", file=sys.stderr)

    # Update ebooks row + refresh ebook_chunks previews
    total_chars = sum(len(c.get("content") or "") for c in chunks)
    from datetime import datetime
    now = datetime.utcnow().isoformat() + "Z"
    patch = {
        "chunk_count": len(chunks),
        "total_chars": total_chars,
        "parsed_at": now,
        "standardized_at": now,
    }
    r = requests.patch(f"{URL}/rest/v1/ebooks?id=eq.{book['id']}",
                       headers={**H_GET, "Content-Type": "application/json"},
                       json=patch, timeout=30)
    if r.ok:
        print(f"  ✓ ebooks patched  chunk_count={len(chunks)}  total_chars={total_chars:,}")
    else:
        print(f"  ⚠ ebooks patch: {r.status_code}", file=sys.stderr)

    requests.delete(f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{book['id']}", headers=H_GET, timeout=30)
    rows = [{
        "ebook_id": book["id"],
        "chunk_index": c["chunk_index"],
        "chunk_type": c.get("chunk_type") or "chapter",
        "page_number": c.get("page_number"),
        "chapter_path": c.get("chapter_path"),
        "content": (c.get("content") or "")[:200],
        "char_count": len(c.get("content") or ""),
    } for c in chunks]
    BATCH = 25
    for i in range(0, len(rows), BATCH):
        rr = requests.post(f"{URL}/rest/v1/ebook_chunks",
                           headers={**H_GET, "Content-Type": "application/json"},
                           json=rows[i:i+BATCH], timeout=60)
        if not rr.ok:
            print(f"  ⚠ ebook_chunks insert {rr.status_code}: {rr.text[:200]}", file=sys.stderr)
            return
    print("  ✓ ebook_chunks previews refreshed")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("ebook_id")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--inspect", action="store_true",
                   help="show font histogram + sample headings, no chunking")
    args = p.parse_args()
    book = fetch_book(args.ebook_id)
    if args.inspect:
        inspect(book)
    else:
        standardize(book, args.dry_run)


if __name__ == "__main__":
    main()
