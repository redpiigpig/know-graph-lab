---
name: ebook-pipeline
description: Operate the Know-Graph-Lab ebook pipeline end-to-end. Use when working on parsing books from Drive into Supabase, OCR'ing scanned PDFs (daily Gemini scheduler), back-filling DB previews from local JSONL, standardizing EPUBs into reader-ready markdown, or wiring the reader to chunks. The hub for everything book-content-related.
---

# Ebook Pipeline Skill

End-to-end pipeline that takes books from a local Drive folder all the way to the reader at `/ebook/[id]`. This file is the **operational hub** — what runs, in what order, how to monitor it, and how to recover when it breaks. For the standardization step specifically (turning EPUBs into reader-ready markdown), see the **`standardize-ebook` skill** which is the detail-level companion.

## Current state (snapshot 2026-05-04)

| Stage | Status | Numbers |
|---|---|---|
| Drive scan + author/title parse | ✅ done | 1,309 books |
| File rename in Drive | ✅ done | all renamed to `作者，書名.ext` |
| DB import (`ebooks` table) | ✅ done | 1,309 rows |
| First-pass parse (text-extractable) | ✅ done | 900 parsed (478 EPUB + 422 text PDF) |
| mobi/azw3 → epub conversion | ✅ done | 0 remaining |
| **OCR scanned PDFs** | 🔄 daily-scheduled | 391 queued, ~1 done; auto-runs 16:00 daily |
| Local JSONL written | ✅ done for parsed books | `G:/我的雲端硬碟/資料/電子書/_chunks/*.jsonl` |
| R2 mirror of JSONL | ✅ done | 901 files (out of 900 parsed — 1 was duplicate) |
| `ebook_chunks` previews in DB | ✅ ~88% | 115K rows; ~107 books need retry-failed |
| Frontend reads chunks | ✅ wired | `loadChunk()` from local→R2 fallback |
| Reader v2 UI (light theme + TOC + highlights + notes panel) | ✅ done | with auto-save, error toasts |
| Search by title / author / fulltext | ✅ wired | `/api/ebooks/search?mode=…` |
| **Standardize → markdown reader format** | 🔄 in progress | 文明的歷史 + 51 哲學 books done (need re-run after volume fix) |

## Pipeline scripts overview (all in `scripts/`)

| Script | Phase | Purpose |
|---|---|---|
| `local_drive_pipeline.py` | 1 — ingest | Scan Drive, parse `作者，書名.ext`, rename in place |
| `parse_drive_inventory.py` | 1 — ingest | Library: `parse_filename()`, `to_traditional()`, `TITLE_AUTHOR_OVERRIDES` |
| `import_local_to_supabase.py` | 1 — ingest | `data/local_inventory.json` → `ebooks` rows |
| `parse_worker.py` | 2 — parse | **Main parser** (PyMuPDF + ebooklib). `init` / `run [--limit N] [--retry-errors]` / `status` |
| `convert_mobi_to_epub.py` | 2 — parse | Calibre wrapper for mobi/azw3 → epub. Already done; keep for new files |
| `ocr_with_gemini.py` | 3 — OCR | Gemini Vision OCR for scanned PDFs. Pushes JSONL to R2 inline |
| `run_ocr_daily.bat` + Task Scheduler | 3 — OCR | Windows daily runner for `ocr_with_gemini.py` |
| `standardize_ebook.py` | 4 — standardize | Re-parse EPUB → markdown chunks, s2tw, drop boilerplate (see `standardize-ebook` skill) |
| `repopulate_chunk_previews.py` | 5 — DB | Back-fill `ebook_chunks` previews from local JSONL. `run` / `retry-failed` / `status` |
| `upload_chunks_to_r2.py` | 5 — R2 | One-shot bulk uploader for any books whose JSONL isn't on R2 yet |
| `offload_chunks.py` | (history) | Did the original DB-truncate after JSONL offload. Don't run again |

## DB schema

```sql
ebooks (
  id uuid PK, title, author, file_type,
  file_path,                    -- absolute path to local Drive file
  category, subcategory,         -- 9 main categories, free-form subcategory
  total_pages, total_chars,
  chunk_count,                   -- total chunks produced
  parsed_at,                     -- NULL = not yet parsed
  parse_error,                   -- NULL on success; preserved on transient fail for retry
  book_id,                       -- nullable FK to books table (for excerpt linkage)
  cleaned_at                     -- nullable; set by Haiku cleaner
)

ebook_chunks (
  id uuid PK, ebook_id FK,
  chunk_index INT, chunk_type,   -- 'page' for PDF, 'chapter' for EPUB
  page_number, chapter_path,
  content TEXT,                  -- ⚠ first 200 chars only (preview); full text in JSONL
  char_count                     -- length of full content (not preview)
)
GIN index on to_tsvector('simple', content)  -- preview-level FTS

annotations (
  id uuid PK, ebook_id FK, chunk_index,
  selected_text, context_before, context_after,
  note, color,                   -- yellow|green|blue|pink
  excerpt_id FK?,                -- if save_as_excerpt was set
  created_at
)
```

## Storage layout

- **Local JSONL** (source of truth): `G:/我的雲端硬碟/資料/電子書/_chunks/{ebook_id}.jsonl`
  - One JSON per line: `{chunk_index, chunk_type, page_number, chapter_path, volume?, format?, content}`
  - Auto-syncs to Google Drive cloud as backup
  - Configured via `EBOOK_CHUNKS_DIR` in `.env` (consumed by `nuxt.config.ts` → `runtimeConfig.ebookChunksDir`)
- **R2 mirror**: `r2://{R2_BUCKET}/ebook-chunks/{ebook_id}.jsonl.gz` (gzipped)
  - Read at runtime by `server/utils/ebook-chunks.ts` `loadLines()` when local file is unreachable (production, Zeabur, etc.)
- **DB previews**: `ebook_chunks.content` first 200 chars only — for fast SQL `ilike` full-text search

## Critical constraints

- **Supabase free tier 500 MB limit** — never reload full chunk text into DB. Always JSONL-on-disk + 200-char preview to DB.
- **Supabase IO budget on free tier** — bulk inserts (>1K/s) hit `57014` "canceling statement". Both `parse_worker.py` and `repopulate_chunk_previews.py` use **adaptive batch sizes** (100 → 50 → 20 → 5 → 1) to ride out spikes.
- **No Supabase Storage bucket** — user explicitly forbade it. Local files only (G: drive auto-syncs to Drive).
- **Service-role key in `.env`** — never hardcode. Old hardcoded keys cleaned in commit `7a35d07`; if you spot more, scrub them.
- **PostgREST 1000-row default cap** — server endpoints that list ebooks already use `.range(0, 1999)` ([server/api/ebooks/index.get.ts](../../../server/api/ebooks/index.get.ts)). Any new bulk read must do the same.

---

## Workflow A — OCR scanned PDFs (391 books)

[`scripts/ocr_with_gemini.py`](../../../scripts/ocr_with_gemini.py) sends each scanned PDF to Gemini Vision via the Files API and gets back structured JSON `{pages: [{page, text}]}`. After OCR, it:

1. Writes JSONL to local `_chunks/`
2. **Pushes gzipped JSONL to R2** (inline — see `push_to_r2()` in the script)
3. Inserts 200-char preview rows into `ebook_chunks`
4. Marks `ebooks.parsed_at` + clears `parse_error`

**Rate limits to respect**: Gemini 2.5 Flash free tier — 10 RPM, 250 RPD, 250K TPM. Default `--rpm 8` leaves headroom. Daily quota resets at midnight Pacific Time (≈ Taipei 16:00).

### Daily scheduler (set up + running)

| Component | Path |
|---|---|
| Bat runner | [`scripts/run_ocr_daily.bat`](../../../scripts/run_ocr_daily.bat) — wraps the python invocation, logs to `scripts/logs/ocr_YYYY-MM-DD.log` |
| Windows Task | `KGLab-OCR-Daily` registered via `Register-ScheduledTask` |
| Trigger | Daily at 16:00 (Taipei = 0:00 PT, when Gemini quota resets) |
| Behavior | `WakeToRun` + `StartWhenAvailable` — wakes from sleep, catches up if missed |
| Run as | Current user, Interactive logon (no password stored; only fires while logged in) |
| Cap | 12-hour `ExecutionTimeLimit` |

```powershell
# Inspect / control
schtasks /query /tn "KGLab-OCR-Daily" /v /fo list
Start-ScheduledTask -TaskName "KGLab-OCR-Daily"   # manual fire (won't help mid-day if quota exhausted)
schtasks /delete /tn "KGLab-OCR-Daily" /f          # tear it down
```

### Manual operations

```bash
python scripts/ocr_with_gemini.py status                          # how many books queued
python scripts/ocr_with_gemini.py run --limit 1                   # smoke test 1 book
python scripts/ocr_with_gemini.py run --rpm 8                     # full run, default RPM
python scripts/ocr_with_gemini.py run --model gemini-2.5-flash-lite --rpm 12  # ~3x daily quota for faster sweep
```

### When OCR breaks

- `parse_error: 'no extractable text'` → still in queue (initial failure from `parse_worker`, picked up by `ocr_with_gemini`)
- `parse_error` starts with `OCR ok but R2 push failed:` → OCR succeeded but R2 write failed; book NOT marked parsed; next OCR run re-tries (cheap — JSONL was kept locally)
- `parse_error` starts with `OCR:` → permanent OCR failure (model returned 0 usable pages, file too big, etc.). Won't auto-retry; investigate manually.
- Quota stop: script exits cleanly with "Quota/rate-limit hit. Stopping. Re-run later." — tomorrow's scheduled run picks up

---

## Workflow B — Standardize EPUB into reader-ready format

This is the **second-pass** transformation that makes a book look polished in `/ebook/[id]`: simplified→traditional Chinese, publisher boilerplate stripped, multi-volume hierarchy preserved, `<h1-h4>/<b>/<em>` mapped to markdown.

**See the [`standardize-ebook`](../standardize-ebook/SKILL.md) skill** for the full contract (output format, drop/dedupe rules, idempotency, tuning per publisher).

### Quick commands

```bash
# Single book
python scripts/standardize_ebook.py <ebook_id>
python scripts/standardize_ebook.py <ebook_id> --dry-run

# Whole category (auto-skips PDFs)
python scripts/standardize_ebook.py --category 哲學
python scripts/standardize_ebook.py --category 哲學 --subcategory 近代哲學
python scripts/standardize_ebook.py --category 哲學 --limit 5 --dry-run
```

### Current standardization state

| Book(s) | Done? | Notes |
|---|---|---|
| 文明的歷史 (id `181798a6-…`) | ✅ done | Reference example. K4 anchor in EPUB is misplaced → 發現者上冊 only has 3 chunks (publisher data quirk, not a script bug) |
| 哲學 category (51 EPUBs) | ⚠ done with old volume logic | Need re-run with new `looks_like_volume()` heuristic — single-volume books were picking up 「目錄/插頁/出版說明」 as fake volumes. Re-run is safe (idempotent) |
| Other categories | ❌ not started | 9 categories; can be batched per category |

### Recommended re-run after recent fix

```bash
# Re-apply volume marker heuristic to 51 already-standardized 哲學 books.
# (Re-running standardize is idempotent: overwrites local JSONL + R2 + DB previews.)
python scripts/standardize_ebook.py --category 哲學
```

⚠ Caveat: re-running can shift `chunk_index` if drop/dedupe rules change, which would break existing `annotations`. Only 2 annotations exist book-wide right now, both on 文明的歷史 (which won't be re-run unless fix is targeted). Safe for the 哲學 batch.

---

## Workflow C — Back-fill `ebook_chunks` previews

Needed when full-text search must cover a book whose chunks are only on disk/R2 but not in DB previews. Happens to:
- Books that were parsed before R2 offload but DB was truncated
- Books that hit `57014` IO timeout during `repopulate_chunk_previews.py`'s first run

```bash
# What's missing?
python scripts/repopulate_chunk_previews.py status

# Initial back-fill from scratch
python scripts/repopulate_chunk_previews.py run

# Re-attack books with mismatched count (preferred — adaptive batching from 100→1)
python scripts/repopulate_chunk_previews.py retry-failed

# Single book (e.g. after manually editing JSONL)
python scripts/repopulate_chunk_previews.py run --book <ebook_id> --force
```

`retry-failed` is the safe re-run mode — finds books whose `ebook_chunks` count is below their expected `ebooks.chunk_count` and only retries those, with adaptive batches that survive 57014.

---

## Decision tree for "this book looks broken in the reader"

```
Book opens but no content?
  → Check ebook_chunks count for this book. If 0 → run repopulate_chunk_previews.py --book <id>
  → If still missing, check local JSONL exists. If not → re-parse (parse_worker.py or ocr_with_gemini.py)

Reader sidebar shows "目錄/插頁" as fake volumes?
  → standardize_ebook.py was run before the volume marker fix. Re-run for this book.

Reader shows "Digital Lab" page or other publisher noise?
  → Add the publisher's specific phrase to HARD_DROP_PATTERNS in standardize_ebook.py, re-run.

Search returns no fulltext hits but title/author work?
  → ebook_chunks doesn't have this book's previews. Run repopulate_chunk_previews.py.

A scanned PDF still shows "此頁無內容" 12+ hours after OCR scheduled?
  → Check scripts/logs/ocr_YYYY-MM-DD.log for errors.
  → If quota hit, just wait — tomorrow's run picks up.
```

---

## Common pitfalls

- **opencc s2tw over-converts**: `历史 → 曆史` (should be 歷史), surnames like `栗 → 慄`. Post-fix table in [`scripts/parse_drive_inventory.py:TRAD_FIXES`](../../../scripts/parse_drive_inventory.py).
- **Chinese characters in shell output on Windows**: cp950 codec errors. Always use `sys.stdout.reconfigure(encoding='utf-8')` or write to UTF-8 file.
- **PostgREST `Range: */0` is ambiguous** — could mean 0 rows OR unknown count. Don't trust if `Prefer: count=exact` is set; use the explicit count format.
- **`server/utils/ebook-chunks.ts` LRU cache (10 min TTL)** means hot-edits to JSONL aren't visible immediately. Restart dev server after batch standardize / re-parse to clear cache.
- **Filename collisions in same folder**: when multiple files would have the same stripped title, `parse_filename()` keeps the subtitle. Already handled.
- **REST API row limit 1000**: any new bulk read must use `.range()`-based pagination. The existing index endpoint has `.range(0, 1999)` baked in.

## Files NOT to touch unless user requests

- `data/local_inventory.json` — frozen Drive scan snapshot
- `data/parse_progress.txt` — auto-managed by parse_worker
- `G:/我的雲端硬碟/資料/電子書/_chunks/*.jsonl` — source of truth for full text (R2 mirrors these; if lost, must re-parse)

## Recommended order for "I'm a new agent picking this up"

1. Run `python scripts/repopulate_chunk_previews.py status` and `python scripts/ocr_with_gemini.py status` to see what's queued.
2. Read [`standardize-ebook` SKILL](../standardize-ebook/SKILL.md) before touching that pipeline.
3. Don't re-run `standardize_ebook.py` on books with annotations (`annotations` table). Currently only 文明的歷史 has any.
4. For categorized batch standardize (哲學 → others), use `--dry-run` first, then real run.
5. Watch the OCR scheduler each afternoon at 16:00 — read the day's log file in `scripts/logs/`.

## See also

- [`standardize-ebook` SKILL](../standardize-ebook/SKILL.md) — detail-level skill for the markdown standardize pipeline
- [`EBOOK_PIPELINE.md`](../../../EBOOK_PIPELINE.md) at repo root — original design doc
- [`scripts/haiku_cleanup_guide.md`](../../../scripts/haiku_cleanup_guide.md) — Haiku-based text cleanup (separate from standardize; used pre-standardize, mostly historical now)
