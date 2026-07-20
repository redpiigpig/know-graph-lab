"""Extract CCEL EPUB extras (footnotes + print page numbers) and patch them
back into an already-translated ebook's JSONL.

Background
----------
`translate_ebook_to_zh.py:epub_to_chunks` builds markdown via
`soup.find_all(["h1","h2","h3","h4","p","blockquote","li"]).get_text(...)`.
That call strips three CCEL-specific markers we need for a usable reader:

  - `<a class="Note" href="#fnf_...">N</a>` — inline footnote reference
    (becomes a bare ` N ` between spaces; loses the link target).
  - `<div class="mnote">` containing `<span class="Footnote">body</span>`
    — the actual footnote text, placed at end of the chunk HTML.
  - `<span class="pb" id="..Page_N"/>` — print-edition page break marker
    (page numbers from Edinburgh / T&T Clark original).

This script re-reads the EPUB, walks each `<ITEM_DOCUMENT>` in document
order, and patches the chunk JSONL in-place:

  - Replaces bare ` NNNN ` in source_text with `[^NNNN]` markdown when N
    matches an extracted footnote number for that chunk.
  - Appends a footnote section to source_text:
      `\n\n————————————\n\n[^N]: body...`
  - Adds `page_numbers: [N, M, ...]` to each chunk (sorted, unique).
  - (Optionally) Inserts `{{p:N}}` markers in source_text at the right
    character positions so the reader can show in-line page indicators.

Idempotent: a chunk that already has `footnotes` populated is skipped.

Usage:
    python scripts/extract_epub_extras.py <ebook_id>
    python scripts/extract_epub_extras.py <ebook_id> --dry-run
    python scripts/extract_epub_extras.py <ebook_id> --inline-page-markers
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
from bs4 import BeautifulSoup, NavigableString, Tag
from dotenv import load_dotenv
import ebooklib
from ebooklib import epub

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "scripts"))
import standardize_ebook as se

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR")
                  or r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")


def fetch_book(ebook_id: str) -> dict:
    r = requests.get(f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}&select=*",
                     headers=H_GET, timeout=30)
    r.raise_for_status()
    rows = r.json()
    if not rows:
        sys.exit(f"no ebooks row for {ebook_id}")
    return rows[0]


def find_epub(book: dict) -> Path:
    src = Path(book["file_path"])
    if src.suffix.lower() == ".epub":
        return src
    epub_p = src.with_suffix(".epub")
    if epub_p.exists():
        return epub_p
    for f in src.parent.iterdir():
        if f.suffix.lower() == ".epub":
            return f
    sys.exit(f"no EPUB for {src}")


# ── EPUB walker ────────────────────────────────────────────────────────────

def extract_from_html(html_bytes: bytes, inline_page_markers: bool = False
                      ) -> tuple[str, dict[int, str], list[int]]:
    """Re-parse a single CCEL HTML file. Return:
      - markdown_with_marks: same shape as the existing translator's output,
        but with `[^N]` ref markers preserved AND optional `{{p:N}}` page
        markers inserted at the right places (only if inline_page_markers=True).
      - footnotes: {N: body_text_markdown}
      - page_numbers: sorted unique list of print pages found in this file
    """
    soup = BeautifulSoup(html_bytes, "lxml")

    # Strip footnote DIVs out of the main flow so they don't pollute body
    footnotes: dict[int, str] = {}
    for div in soup.find_all("div", class_="mnote"):
        anchor = div.find("a", class_="Note")
        sup = div.find("sup", class_="NoteRef")
        body_span = div.find("span", class_="Footnote")
        num: Optional[int] = None
        if sup and sup.get_text(strip=True).isdigit():
            num = int(sup.get_text(strip=True))
        elif anchor and anchor.get_text(strip=True).isdigit():
            num = int(anchor.get_text(strip=True))
        if num is None:
            continue
        # Pull body text; strip scripRef links into plain bible refs.
        body = body_span.get_text(separator=" ", strip=True) if body_span else ""
        body = re.sub(r"\s+", " ", body).strip()
        if body:
            footnotes[num] = body
        div.decompose()

    # Collect page breaks. CCEL self-closes them, e.g.
    #   <span class="pb" id="ii.ii.xxxvi-Page_15"/>
    page_breaks: list[int] = []
    if inline_page_markers:
        # Replace each <span class="pb"> with a text marker so it survives the
        # subsequent get_text() flow. We tag them with a stable sentinel
        # `__PB_{N}__` and post-replace to `{{p:N}}` after markdown assembly.
        for sp in soup.find_all("span", class_="pb"):
            page_id = sp.get("id", "")
            m = re.search(r"Page[_\-](\d+)", page_id)
            if m:
                n = int(m.group(1))
                page_breaks.append(n)
                # Insert a navigable string before the span gets dropped
                sp.replace_with(NavigableString(f" __PB_{n}__ "))
    else:
        for sp in soup.find_all("span", class_="pb"):
            page_id = sp.get("id", "")
            m = re.search(r"Page[_\-](\d+)", page_id)
            if m:
                page_breaks.append(int(m.group(1)))
            sp.decompose()

    # Replace inline footnote refs with `[^N]` markdown. These are
    # `<a class="Note" id="fna_..." href="#fnf_...">N</a>`
    for a in soup.find_all("a", class_="Note"):
        txt = a.get_text(strip=True)
        if txt.isdigit():
            a.replace_with(NavigableString(f"[^{txt}]"))
        else:
            a.decompose()

    # Now build markdown the same way translate_ebook_to_zh.epub_to_chunks does.
    md_parts: list[str] = []
    for el in soup.find_all(["h1", "h2", "h3", "h4", "p", "blockquote", "li"]):
        text = el.get_text(separator=" ", strip=True)
        if not text:
            continue
        tag = el.name
        if tag == "h1":
            md_parts.append(f"## {text}")
        elif tag == "h2":
            md_parts.append(f"### {text}")
        elif tag in ("h3", "h4"):
            md_parts.append(f"#### {text}")
        elif tag == "blockquote":
            md_parts.append(f"> {text}")
        elif tag == "li":
            md_parts.append(f"- {text}")
        else:
            md_parts.append(text)
    md = "\n\n".join(md_parts).strip()
    # Convert sentinels to final marker form
    md = re.sub(r"__PB_(\d+)__", r"{{p:\1}}", md)
    md = re.sub(r" +", " ", md)
    return md, footnotes, sorted(set(page_breaks))


# ── Patcher ───────────────────────────────────────────────────────────────

def patch_chunks(ebook_id: str, dry_run: bool = False,
                 inline_page_markers: bool = True) -> None:
    book = fetch_book(ebook_id)
    epub_path = find_epub(book)
    print(f"Book: {book['title']}")
    print(f"EPUB: {epub_path}")

    jsonl_path = CHUNKS_DIR / f"{ebook_id}.jsonl"
    if not jsonl_path.exists():
        sys.exit(f"JSONL not found: {jsonl_path}")
    chunks = [json.loads(l) for l in jsonl_path.read_text(encoding="utf-8").splitlines()]
    print(f"Loaded {len(chunks)} chunks")

    # Walk EPUB in document order, mapping ITEM_DOCUMENT → extracted extras.
    # The chunk JSONL stores `title_en` which == derived heading from each
    # document. To align, we extract from EVERY ITEM_DOCUMENT in order and
    # match to chunks by title_en.
    book_epub = epub.read_epub(str(epub_path))
    extras_by_title: dict[str, tuple[dict[int, str], list[int], str]] = {}
    items_processed = 0
    for item in book_epub.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        md, footnotes, page_breaks = extract_from_html(
            item.get_content(), inline_page_markers=inline_page_markers
        )
        # Derive a title key the same way translator did
        m = re.search(r"^(#{2,4})\s+(.+)", md, re.M)
        title_key = m.group(2).strip() if m else item.get_name()
        # Truncate to first line in case heading wraps
        title_key = title_key.split("\n", 1)[0].strip()
        extras_by_title[title_key] = (footnotes, page_breaks, md)
        items_processed += 1
    print(f"Walked {items_processed} EPUB documents; "
          f"{len(extras_by_title)} unique titles")

    n_patched = 0
    n_no_match = 0
    n_already = 0
    n_fn_total = 0
    n_pg_total = 0
    for c in chunks:
        if c.get("footnotes") and c.get("page_numbers") is not None:
            n_already += 1
            continue
        title_en = c.get("title_en")
        if not title_en:
            n_no_match += 1
            continue
        # Strip footnote leak that might have been merged into title
        title_en_clean = re.sub(r"\s+", " ", title_en).split("\n", 1)[0].strip()
        match = extras_by_title.get(title_en_clean)
        if not match:
            # Try a few alternate keys (heading wrapping, suffix mismatch)
            for k in extras_by_title:
                if k.startswith(title_en_clean[:30]) or title_en_clean.startswith(k[:30]):
                    match = extras_by_title[k]
                    break
        if not match:
            n_no_match += 1
            continue
        footnotes, page_breaks, fresh_md = match

        # ─ Patch source_text ─
        # 1) Inject `[^N]` ref markers: take the fresh re-extracted markdown
        #    (which has `[^N]` from our walker) and use it as canonical source.
        c["source_text"] = fresh_md
        # 2) Append footnote section
        if footnotes:
            # Use `(N) body` format because pages/ebook/[id].vue's
            # renderMarkdown footnote handler matches that shape and emits
            # the bidirectional anchor (sup ↔ paragraph link).
            lines = [""]
            lines.append("—" * 30)
            lines.append("")
            for n in sorted(footnotes.keys()):
                lines.append(f"({n}) {footnotes[n]}")
                lines.append("")
            c["source_text"] = c["source_text"].rstrip() + "\n" + "\n".join(lines)
        # Save footnote dict for reader use
        c["footnotes"] = footnotes
        c["page_numbers"] = page_breaks
        if page_breaks:
            c["page_number"] = page_breaks[0]  # primary page = first break in chunk
        n_patched += 1
        n_fn_total += len(footnotes)
        n_pg_total += len(page_breaks)

    print(f"\n  patched: {n_patched}  /  no_match: {n_no_match}  /  already: {n_already}")
    print(f"  total footnotes: {n_fn_total}")
    print(f"  total page breaks: {n_pg_total}")

    if dry_run:
        # Show one example
        for c in chunks:
            if c.get("footnotes"):
                print(f"\n  sample chunk {c['chunk_index']} ({c.get('chapter_path','')[:30]}):")
                print(f"    page_numbers={c.get('page_numbers')}")
                fn = list(c["footnotes"].items())[:2]
                for k, v in fn:
                    print(f"    [^{k}]: {v[:100]}")
                # Show source_text tail (where footnote section lives)
                src = c["source_text"]
                print(f"    source_text tail (last 400 chars):\n{src[-400:]}")
                break
        print("\n(dry-run, not writing)")
        return

    # Rewrite JSONL
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"\n  ✓ rewrote {jsonl_path.name}  ({jsonl_path.stat().st_size // 1024} KB)")

    # Push R2 + refresh previews (previews only use chinese `content`, no change there)
    try:
        se.push_to_r2(ebook_id, jsonl_path)
        print(f"  ✓ pushed R2")
    except Exception as e:
        print(f"  ⚠ R2 push: {e}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ebook_id")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-inline-page-markers", action="store_true",
                    help="Don't insert {{p:N}} markers in source_text; "
                         "still record page_numbers in chunk metadata.")
    args = ap.parse_args()
    patch_chunks(args.ebook_id, dry_run=args.dry_run,
                 inline_page_markers=not args.no_inline_page_markers)


if __name__ == "__main__":
    main()
