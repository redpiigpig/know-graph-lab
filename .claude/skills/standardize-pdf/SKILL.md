---
name: standardize-pdf
description: Restandardize parsed PDFs into reader-ready chunks. Two flavors — Plan A (lite, implemented) reuses the EPUB pipeline's text helpers on the existing per-page JSONL; Plan B (full, design only) is a from-scratch PyMuPDF rebuild that detects chapters from font sizes and produces EPUB-grade output. Use this skill when EPUB-only standardize won't cut it for a book stuck on raw per-page text.
---

# Standardize PDF Skill

PDFs in this project go through `parse_worker` (text-extractable) or
`ocr_with_gemini` (scanned) and end up as JSONL with `chunk_type="page"`,
one chunk per PDF page. That's "readable but flat" — no chapter sidebar,
simplified Chinese, running headers in the body, no extracted publisher
metadata.

This skill upgrades them.

> **🔑 Hard rule: PDF `page_number` is sacred.** Every chunk's
> `page_number` is the real publisher pagination (often non-contiguous —
> blanks or image-only pages skip a number). Citations in 書摘 reference
> the real value. Any transform that re-numbers `page_number` is a bug.
> `chunk_index` (the position in the JSONL list) can be re-numbered freely;
> `page_number` cannot.

---

## Plan A — Lite pass (implemented)

What [`scripts/standardize_pdf_lite.py`](../../../scripts/standardize_pdf_lite.py) does, per chunk:

1. **Simplified → traditional Chinese** via `to_traditional()` (same s2tw
   + TRAD_FIXES table as the EPUB pipeline).
2. **Collapse spacing artifacts** — text extractors often emit
   `路 … 文 本 、 歷 史` with single-char gaps. `collapse_cjk_spacing()`
   squeezes adjacent CJK characters back together without touching real
   spaces in mixed CJK/Latin paragraphs.
3. **Strip page-number-only running headers** — only when the leading
   line is short and starts with a number that equals the chunk's
   `page_number`. Conservative: a header like `2  Title` on a page whose
   actual `page_number` is 7 will be left in place (Plan B handles those
   with positional detection).
4. **Re-derive `chapter_path`** — only when the page genuinely starts
   with a chapter heading (`第N章 / Chapter N / 引言 / 序 / 致謝 / 附錄
   / Bibliography / Index ...`). If unclear, leave `chapter_path` null
   (better than mislabeling).
5. **Preserve `page_number` exactly** — copy straight through.

Across the whole book it also:

- **Extract publisher metadata** with `_extract_publisher_metadata()`
  (reuse from standardize_ebook) — `書名 / 譯者 / 出版社 / 原書名 /
  Copyright © YYYY by …` — and PATCH onto the ebooks row's columns
  (`subtitle / original_title / author_en / translator / publisher /
  publication_year / original_publish_year / original_author`).

What it does NOT do (those need Plan B):

- Chapter-level chunk splitting (still one-page-one-chunk)
- Cover synthesis or frontmatter consolidation (would shift `page_number`
  semantics)
- Volume hierarchy
- Position-based running header/footer stripping
- Bold/italic/heading inference (no font signals available)

### How to run Plan A

Single book:
```bash
python scripts/standardize_pdf_lite.py <ebook_id>
python scripts/standardize_pdf_lite.py <ebook_id> --dry-run
python scripts/standardize_pdf_lite.py <ebook_id> --no-r2
```

Batch (auto-skips EPUBs):
```bash
python scripts/standardize_pdf_lite.py --category 哲學
python scripts/standardize_pdf_lite.py --category 哲學 --subcategory 近代哲學
python scripts/standardize_pdf_lite.py --all
python scripts/standardize_pdf_lite.py --all --limit 5 --dry-run
```

### Verify

```bash
python -c "
import json
from pathlib import Path
p = Path('G:/我的雲端硬碟/資料/電子書/_chunks/<ebook_id>.jsonl')
chunks = [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines()]
# page_number preservation check (compare against backup if you took one)
print('first 5 page_numbers:', [c['page_number'] for c in chunks[:5]])
print('last 3 page_numbers:', [c['page_number'] for c in chunks[-3:]])
print('chapters detected:', sum(1 for c in chunks if c.get('chapter_path')))
print()
print(chunks[0]['content'][:300])
"
```

Reader-side: open `/ebook/<ebook_id>` (restart dev server first to clear
the LRU cache) and check that:
- Text reads in traditional Chinese (no leftover 历史 / 关于 / etc.)
- Page numbers in the URL bar (`?page=N`) match the printed page number
  shown in the chunk
- Sidebar shows chapter labels for any pages that started with a chapter
  marker (will be sparse — most PDF pages are mid-chapter and stay null)

### Idempotency + safety

Re-running on the same book is safe — overwrites local JSONL, R2 object,
ebook_chunks previews, and ebooks row. **Annotations on PDFs are NOT
shifted** because `chunk_index` ordering and `page_number` are preserved
identically across runs.

---

## Plan B — Full pipeline (design, not yet built)

Plan A is a polish on the existing one-page-one-chunk output. Plan B
re-parses the PDF source with [PyMuPDF (`fitz`)](https://pymupdf.readthedocs.io/),
infers structure from typography, and emits EPUB-grade chapter-level
chunks. Target script: `scripts/standardize_pdf.py`.

### Suggested pipeline order

1. **Open PDF**, iterate pages.
2. **Per-page font analysis** — for each text span collect
   `(text, font_name, font_size, bbox, flags)`:
   ```python
   doc = fitz.open(path)
   for page in doc:
       for block in page.get_text("dict")["blocks"]:
           for line in block.get("lines", []):
               for span in line["spans"]:
                   ...  # span["text"], span["size"], span["font"], span["flags"]
   ```
3. **Build a global font histogram** — across the whole book, count chars
   per `font_size` bucket. The most common size is the body text size.
4. **Classify spans by size relative to body**:
   - `≥ body + 6pt` and short (≤30 chars) → `h2` (chapter title)
   - `≥ body + 3pt` and short → `h3` (section title)
   - `≥ body + 1pt` → `h4` (subsection)
   - `flags & 16` (bold) AND short → `h3` (some publishers signal headings only by bold, not size)
   - Else → body paragraph
5. **Build markdown content** by emitting each classified span:
   - Heading spans → `## title` / `### title` / `#### title`
   - Body spans → join with newlines; merge same-paragraph spans (same y-bbox proximity, no heading between)
   - Bold/italic body → `**text**` / `*text*`
6. **Chunking**:
   - **Per-chapter (preferred)**: start a new chunk at every `h2`. Each
     chunk records the FIRST page it covers as its `page_number` AND
     keeps a `page_range: [start, end]` so cross-page citations still
     work. Reader page-jump can index by start of range.
   - **Fallback per-page** when no headings detected: same as Plan A —
     one chunk per page, but with the cleanup pass applied.
7. **Reuse the EPUB downstream**:
   - `to_traditional()` for s2tw + TRAD_FIXES
   - `derive_chapter_title()` for cosmetic renames (CIP→版權頁)
   - `consolidate_frontmatter_into_publisher()` if a CONTENTS chunk exists
     in the early chunks AND no chapter starts in between
   - `apply_cover_enrichment()` — synthesize a cover chunk at chunk_index
     0 BUT do NOT shift downstream `page_number` (insert with
     `page_number: null` so it doesn't collide with real pagination)
   - PDF bookmarks (`page.get_toc()`) when present can drive volume
     detection for paginated multi-volume sets

### Calibration tips

- **Body size is the linchpin.** Test on 5-10 books from different
  publishers first. If a book has heavy footnotes (small font), filter
  by total char count per bucket, not just frequency.
- **Bold-only signaling is publisher-specific.** 商務印書館 漢譯名著 puts
  chapter titles in bold same-size as body. Only enable bold→heading
  promotion when font-size signal is weak.
- **Drop running headers/footers** — text spans appearing at the same
  y-bbox on most pages (page numbers, book title repeated). Detect by
  frequency across pages, not per-page.
- **Page-spanning paragraphs** — a paragraph that ends on page N and
  continues on page N+1 should NOT be split. Track "did the previous page
  end mid-sentence" using `not text.endswith(('。', '!', '?', '」', '）'))`.
- **Footnotes** — usually appear at bottom of page in smaller font.
  Either drop them or move to end of chunk as `> [註] ...`.
- **Page-number preservation under chunking**: when a chunk spans pages
  M-N, store `page_number = M` and add a new field
  `page_range: [M, N]`. Citations stay correct (point to start). The
  reader can render `第 M-N 頁` if `page_range` is present.

### Known PDFs to use as test cases

- 《尼采到底說了什麼？》by 羅伯特·所羅門 — straightforward 哲學 PDF
- 《從封閉世界到無限宇宙》by 柯瓦雷 — typical philosophy press PDF
- 《當代數學》— heavy formula content; PyMuPDF text extraction will be
  ugly; expect this to be the worst case
- 《希伯來聖經的文本歷史與思想世界》— used for Plan A smoke test;
  has running headers Plan A couldn't strip

### When NOT to do Plan B

- Book reads OK after Plan A
- PDFs with heavy formula / table layout (PyMuPDF mangles those — the
  Gemini Vision OCR pipeline is more robust but expensive)

---

## Current state (snapshot 2026-05-06, late-day)

| Pipeline | Books | Status |
|---|---|---|
| EPUB standardize | 481 / 492 | ✅ shipped, all batches re-run with rich metadata |
| PDF Plan A (lite) | 437 / 437 parsed | ✅ shipped — s2tw + spacing collapse + publisher metadata extraction; `page_number` preserved |
| PDF Plan B (full) | 0 / 437 parsed | 📐 design only — separate session work |
| PDF OCR queue | ~377 books | 🔄 daily 16:00 by `ocr_with_gemini.py` (all 4 keys share one GCP project quota; consider splitting across projects for parallel quota) |

PDF total: 834 books, 437 text-extractable + parsed (Plan A complete),
~377 still queued for OCR. After OCR lands JSONL for those, Plan A is
re-runnable across the full set in one batch.

---

## Related

- [`standardize-ebook` SKILL](../standardize-ebook/SKILL.md) — sister skill
  for EPUB; the helpers reused by Plan A all live in `standardize_ebook.py`
- [`ebook-pipeline` SKILL](../ebook-pipeline/SKILL.md) — orchestration
  hub; covers parse_worker → ocr_with_gemini → standardize fan-out
- [`scripts/parse_worker.py`](../../../scripts/parse_worker.py) —
  produces the per-page JSONL that Plan A consumes
- [`scripts/ocr_with_gemini.py`](../../../scripts/ocr_with_gemini.py) —
  same JSONL shape but for scanned PDFs; both feed Plan A
