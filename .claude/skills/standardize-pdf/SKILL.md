---
name: standardize-pdf
description: Restandardize parsed PDFs into reader-ready chunks. Two flavors shipped — Plan A (lite) reuses the EPUB text helpers on the existing per-page JSONL with `page_number` preserved; Plan B (TOC-driven) re-chunks Plan A output into chapter-level chunks using PDF bookmarks, with a `page_range` field for cross-page citations. Plan B v1 (font-size driven, for no-TOC books) is deferred design. Use when EPUB-only standardize won't cut it for a PDF book stuck on raw per-page text or needing chapter sidebar.
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

## Plan B — TOC-driven re-chunking (implemented v0)

Plan A is a polish on the existing one-page-one-chunk output. Plan B
([`scripts/standardize_pdf.py`](../../../scripts/standardize_pdf.py))
turns those flat per-page chunks into chapter-level chunks driven by
the PDF's TOC bookmarks. Same source-of-truth (existing JSONL) — no
PDF text re-extraction — so it inherits Plan A's text exactly while
re-grouping it.

> **🚧 Why TOC-driven and not font-driven?** The original v0 design
> proposed font-size analysis (h2/h3 from typographic hierarchy).
> A 30-PDF probe showed font signal is degenerate on a large fraction
> of the library — many books are image-based PDFs where PyMuPDF
> extracts <1% of body text yet PyMuPDF's TOC bookmarks survive. TOC
> is therefore both more reliable and simpler to implement. Font-driven
> chapter inference is deferred to Plan B v1 for the no-TOC subset.

### What v0 does

1. Loads the per-page JSONL produced by parse_worker / standardize_pdf_lite.
2. Reads only the PDF's TOC (`fitz.Document.get_toc()`) — no body re-extract.
3. Filters TOC entries to `level <= 2`, drops empties, dedupes
   same-start-page entries, sorts by start page.
4. For each TOC entry, concatenates the existing JSONL pages from
   `[entry.start_page, next_entry.start_page - 1]` into one chapter chunk.
5. Pages BEFORE the first TOC entry become a single `前置內容` chunk
   so 版權頁 / 序言 still feed `_extract_publisher_metadata`.
6. Applies `to_traditional()` (s2tw + TRAD_FIXES) and `collapse_cjk_spacing()`
   per chunk.
7. Builds hierarchical `chapter_path` from TOC ancestor titles
   (`祖標題 / 父標題 / 本標題`).
8. Writes JSONL → R2 mirror → DB previews + ebooks metadata PATCH
   (chunk_count / total_pages / publisher / publication_year / etc.).

### Per-chunk contract

| Field | Value |
|---|---|
| `chunk_type` | `"chapter"` |
| `chunk_index` | re-numbered from 0 |
| `page_number` | **first real PDF page in the chapter** — sacred, never re-numbered |
| `page_range` | `[first, last]` — new field |
| `chapter_path` | TOC title hierarchy, s2tw'd |
| `format` | `"text"` |
| `content` | concatenated page contents joined by `\n\n`, then s2tw + spacing-collapsed |

### Skip conditions (book stays on Plan A output, no change)

| Condition | Threshold |
|---|---|
| TOC entries < 3 | `MIN_TOC_ENTRIES` |
| Page-level TOC (≈1 entry/page) | `total_pages / len(toc) < 1.2` (`MIN_PAGES_PER_ENTRY`) — caught 中東史 (654/661) and 希伯來聖經 (598/598) |
| Existing annotations on this ebook | hard refuse without `--force` (re-chunking shifts `chunk_index` → breaks references) |
| JSONL already chapter-chunked | re-run guard (`chunk_type == 'chapter'` or `page_range` present) — must re-run `standardize_pdf_lite` first to revert |
| PDF file missing on Drive | `file not found:` error |

### How to run

Single book:
```bash
python scripts/standardize_pdf.py <ebook_id>
python scripts/standardize_pdf.py <ebook_id> --dry-run
python scripts/standardize_pdf.py <ebook_id> --no-r2
python scripts/standardize_pdf.py <ebook_id> --force        # ignore annotations guard
```

Batch:
```bash
python scripts/standardize_pdf.py --category 哲學
python scripts/standardize_pdf.py --all --dry-run            # just lists eligible PDFs
python scripts/standardize_pdf.py --all                      # ~6.5s/book → ~50min for 437
```

### Realistic hit rate (sample of 20 PDFs)

12 / 20 books got chapter-chunked. The 8 skips broke down as:
- 7 books had **0 TOC entries** (publisher exported PDF without
  bookmarks — these are candidates for Plan B v1 font analysis)
- 1 book reduced to a single TOC chunk (`only N chunks produced` guard)

### Idempotency + safety

- Re-running on a Plan-A book is safe — overwrites JSONL / R2 / DB previews.
- Re-running on a Plan-B book HARD STOPS — `JSONL already chapter-chunked`.
  Revert via `python scripts/standardize_pdf_lite.py <id>` first.
- Annotations guard fires when even one annotation row exists on
  the ebook. Currently NO PDFs in the library have annotations;
  if that ever changes, plan a chunk_index migration before
  re-chunking.
- `page_number` is preserved exactly. `chunk_index` is re-numbered.
  PDF citations in 書摘 remain correct because they reference
  `page_number`, not `chunk_index`.

---

## Plan B v1 — font-driven inference for no-TOC books (deferred)

Original Plan B design — font-size analysis to infer chapter
boundaries when the PDF has no TOC bookmarks. Worth building when
the no-TOC subset becomes the bottleneck (≈40% of 437 PDFs).

### Pipeline order

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
   - Start a new chunk at every `h2` (same per-chunk contract as v0
     above — page_number sacred, page_range new).

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

### When NOT to do v1

- Book reads OK after Plan A or Plan B v0
- PDFs with heavy formula / table layout (PyMuPDF mangles those — the
  Gemini Vision OCR pipeline is more robust but expensive)
- Image-based PDFs (run OCR first; v1's font signal will be empty)

---

## Current state (snapshot 2026-05-07)

| Pipeline | Books | Status |
|---|---|---|
| EPUB standardize | 481 / 492 | ✅ shipped, all batches re-run with rich metadata |
| PDF Plan A (lite) | 437 / 437 parsed | ✅ shipped — s2tw + spacing collapse + publisher metadata extraction; `page_number` preserved |
| PDF Plan B v0 (TOC-driven) | **152 / 437 chapter-chunked** | ✅ shipped — full `--all` batch complete (OK 152, Skipped 285, Failed 0). Skips: 0-entry TOC (no bookmarks), per-page TOC, already-chunked re-run guard. |
| PDF Plan B v1 (font-driven) | 0 / no-TOC subset (~285) | 📐 deferred design — for the ~65% with no usable PDF TOC bookmarks |
| PDF OCR queue | 322 books | 🔄 every 6h (`13 */6 * * *`) by `ocr_with_gemini.py` (Gemini default, 4 rotating keys); after OCR → Plan A → Plan B |

PDF total: 834 books, 437 text-extractable + Plan A complete, 152 chapter-chunked via Plan B,
322 still queued for OCR. After OCR lands JSONL, Plan A → Plan B re-runnable in one batch.

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
