---
name: ebook-pipeline
description: Operate the Know-Graph-Lab ebook ingestion + chunking pipeline. Use when working on parsing PDF/EPUB books from Drive into Supabase, fixing books that didn't parse, wiring the frontend to chunks, adding OCR for scanned PDFs, or processing mobi/azw3 files.
---

# Ebook Pipeline Skill

This skill is the handover for the local-Drive-synced ebook system. Read [`EBOOK_PIPELINE.md`](../../../EBOOK_PIPELINE.md) at repo root for the full reference. This file is the **operational summary** — what to do, in what order, with which scripts.

## Current state (as of handover)

| Stage | Status |
|---|---|
| Drive scan + author/title parse | ✅ 1,309 books, all categorized into 9 main folders |
| File rename in Drive | ✅ all renamed to `作者，書名.ext` |
| DB import (ebooks table) | ✅ 1,309 rows |
| PDF/EPUB → chunks parsing | ⚠️ 799 succeeded, 410 failed (mostly scanned PDFs), 100 skipped (mobi/azw3) |
| Chunk storage | ✅ DB stores 200-char preview only; full text in local JSONL at `G:/我的雲端硬碟/資料/電子書/_chunks/{ebook_id}.jsonl` |
| **Frontend reads chunks** | ❌ **NOT WIRED** — `server/api/ebooks/[id].get.ts` still queries empty `book_pages` table |
| OCR for scanned PDFs | ❌ not started |
| Calibre conversion for mobi/azw3 | ❌ not started |

## First task for incoming agent: wire frontend to chunks

Edit [`server/api/ebooks/[id].get.ts`](../../../server/api/ebooks/[id].get.ts) to:
1. Query `ebook_chunks` (not `book_pages`) by `ebook_id` + `chunk_index`
2. Load full content from local JSONL `G:/我的雲端硬碟/資料/電子書/_chunks/{ebook_id}.jsonl` (line `chunk_index`)
3. Return `{ebook, chunk: {page_number, chapter_path, content}, total_chunks}`

Update [`pages/ebook/[id].vue`](../../../pages/ebook/[id].vue) to render either page-based (PDF, paginate by `page_number`) or chapter-based (EPUB, paginate by `chunk_index` with `chapter_path` as label).

## Pipeline scripts (all in `scripts/`)

| Script | Purpose |
|---|---|
| `local_drive_pipeline.py` | Walk G: drive, parse `作者，書名.ext` filenames, rename in place. Commands: `scan`, `dryrun`, `rename` |
| `parse_drive_inventory.py` | Library: `parse_filename()`, `to_traditional()`, `TITLE_AUTHOR_OVERRIDES`. Imported by other scripts. |
| `categorize_root_books.py` | Move root-level books to main category folders. Already executed; kept for reference if more roots appear. |
| `import_local_to_supabase.py` | Bulk import `data/local_inventory.json` → `ebooks` table. Clears existing first. |
| `parse_worker.py` | **Main parser.** PDF (PyMuPDF) and EPUB (ebooklib). Writes JSONL to local + 200-char preview to DB. Commands: `init`, `run [--limit N] [--retry-errors]`, `status` |
| `offload_chunks.py` | One-shot: DB chunks → local JSONL + truncate DB. Already executed; only re-run if you ever fully re-load content into DB. |

## DB schema (Supabase Postgres)

```sql
ebooks (
  id uuid PK, title, author, file_type, file_path,  -- file_path = local Drive path
  category, subcategory, total_pages, total_chars,
  parsed_at, chunk_count, parse_error  -- parse_error NOT NULL = failed; retry with --retry-errors
)

ebook_chunks (
  id uuid PK, ebook_id FK, chunk_index, chunk_type,  -- 'page' | 'chapter'
  page_number, chapter_path,
  content TEXT  -- ⚠️ first 200 chars only — full text is in local JSONL
)
```

GIN full-text index `idx_ebook_chunks_fts` on `ebook_chunks.content` (preview only — for quick filter, not full-text).

## Critical constraints

- **Supabase free tier 500 MB limit** — don't reload full chunk text into DB. Always write JSONL local + preview-only to DB. `parse_worker.py` already does this.
- **Disk IO budget on free tier** — bulk inserts can deplete it. Adaptive batching in `parse_worker.py:insert_chunks()` handles HTTP 500/57014 timeouts by halving batch size.
- **No Supabase Storage bucket** — user explicitly forbade it. Local files only (G: drive auto-syncs to Drive cloud as backup).
- **Service-role key is in `.env`** — never hardcode. Three old import scripts had hardcoded keys; cleaned in commit `7a35d07`.

## Decision tree for failures

```
ebook has parse_error?
├── 'no extractable text' → scanned PDF. Pure-Python can't OCR. Add Tesseract or Gemini Vision.
├── 'file not found' → file moved/renamed. Re-run local_drive_pipeline.py scan + import_local_to_supabase to refresh paths.
├── 'canceling statement / 57014' → Supabase IO budget. Wait for refill OR drop GIN index temporarily, then re-run with --retry-errors.
└── 'format not supported (mobi/azw3/azw)' → install Calibre, run `ebook-convert input.azw3 output.epub`, re-import.
```

## Recommended next tasks (priority order)

1. **Wire frontend to ebook_chunks** (described above) — without this, the parsed content is invisible to users.
2. **OCR scanned PDFs** (410 books). Cheapest: pytesseract + tesseract-ocr-chi-tra package locally. Better quality: Gemini Vision API free tier.
3. **mobi/azw3 conversion** (100 books). Install Calibre, batch-convert to epub, re-run `parse_worker.py run --retry-errors`.
4. **Semantic search** — generate embeddings (Gemini text-embedding-004 free tier or local model) per chunk, store in `ebook_chunks.embedding vector(768)`. Add pgvector index.

## Common pitfalls

- **opencc s2tw over-converts**: `历史 → 曆史` (should be 歷史), `栗 → 慄` (when surname). Post-fix table is in [`scripts/parse_drive_inventory.py:TRAD_FIXES`](../../../scripts/parse_drive_inventory.py). Add new entries here when found.
- **Filename collisions in same folder**: when multiple files would have the same stripped title (e.g., 西洋哲學史 series volumes), `parse_filename()` keeps the subtitle. Already handled.
- **Chinese characters in shell output on Windows**: cp950 codec errors. Always use `sys.stdout.reconfigure(encoding='utf-8')` or write to a UTF-8 file.
- **REST API row limit 1000**: When fetching `ebooks`, use offset-based pagination (already done in `parse_worker.py:fetch_all_books()` and `cmd_run()`).

## Quick commands

```bash
# Status
python scripts/parse_worker.py status

# Re-parse failed books after fix (e.g., after Calibre conversion)
python scripts/parse_worker.py run --retry-errors

# DB size check
python -c "exec(open('/tmp/usage_simple.py').read())"  # see EBOOK_PIPELINE.md for snippet

# Regen progress checklist after manual DB changes
python scripts/parse_worker.py init
```

## Files NOT to touch unless user requests

- `data/local_inventory.json` — frozen snapshot of original Drive scan. Only update via `local_drive_pipeline.py scan`.
- `data/parse_progress.txt` — auto-managed by parse_worker; don't hand-edit.
- `G:/我的雲端硬碟/資料/電子書/_chunks/*.jsonl` — source of truth for full text. If lost, must re-parse to regenerate.

## See also

- [`EBOOK_PIPELINE.md`](../../../EBOOK_PIPELINE.md) at repo root — full design doc with architecture, schema rationale, operational history.
