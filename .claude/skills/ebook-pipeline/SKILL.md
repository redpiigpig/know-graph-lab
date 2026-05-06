---
name: ebook-pipeline
description: Operate the Know-Graph-Lab ebook pipeline end-to-end. Use when working on parsing books from Drive into Supabase, OCR'ing scanned PDFs (daily Gemini scheduler), back-filling DB previews from local JSONL, standardizing EPUBs into reader-ready markdown, or wiring the reader to chunks. The hub for everything book-content-related.
---

# Ebook Pipeline Skill

End-to-end pipeline that takes books from a local Drive folder all the way to the reader at `/ebook/[id]`. This file is the **operational hub** — what runs, in what order, how to monitor it, and how to recover when it breaks. For the standardization step specifically (turning EPUBs into reader-ready markdown), see the **`standardize-ebook` skill** which is the detail-level companion.

## Current state (snapshot 2026-05-06)

| Stage | Status | Numbers |
|---|---|---|
| Drive scan + author/title parse | ✅ done | 1,309 books (initial sweep) |
| **Daily new-book drop ingest** | ✅ wired into daily scheduler | `ingest_new_books.py` — see Workflow D |
| File rename in Drive | ✅ done | all renamed to `作者，書名.ext` |
| DB import (`ebooks` table) | ✅ rolling | 1,326 rows (1,309 initial + 17 ingested 2026-05-06) |
| First-pass parse (text-extractable) | ✅ done | 900 parsed (478 EPUB + 422 text PDF) |
| mobi/azw3 → epub conversion | ✅ done | 0 remaining |
| **OCR scanned PDFs** | 🔄 daily-scheduled | 386 queued; auto-runs 16:00 daily |
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
| `local_drive_pipeline.py` | 1 — ingest (initial sweep) | Scan Drive, parse `作者，書名.ext`, rename in place |
| `parse_drive_inventory.py` | 1 — ingest | Library: `parse_filename()`, `to_traditional()`, `TITLE_AUTHOR_OVERRIDES` |
| `import_local_to_supabase.py` | 1 — ingest (initial sweep) | `data/local_inventory.json` → `ebooks` rows |
| `ingest_new_books.py` | 1 — ingest (**daily**) | Watches `.claude/skills/ebook-pipeline/new-book/`. Parses filename, classifies via Gemini (with keyword fallback), inserts ebooks row, moves file to `G:/.../電子書/{category}/`. See Workflow D |
| `parse_worker.py` | 2 — parse | **Main parser** (PyMuPDF + ebooklib). `init` / `run [--limit N] [--retry-errors]` / `status` |
| `convert_mobi_to_epub.py` | 2 — parse | Calibre wrapper for mobi/azw3 → epub. Already done; keep for new files |
| `ocr_with_gemini.py` | 3 — OCR (primary) | Gemini Vision OCR for scanned PDFs. Pushes JSONL to R2 inline. Exits with code 2 when daily quota hits (signals fallback) |
| `ocr_with_qwen.py` | 3 — OCR (fallback, **disabled**) | Local Qwen2.5-VL via Ollama. Code intact; bat trigger commented out — vision compute graph (6.7 GiB) won't fit on 4050 Mobile (6 GiB). Re-enable on better GPU. See Workflow A-2 |
| `run_ocr_daily.bat` + Task Scheduler | (orchestrator) | Windows daily runner — runs **ingest → parse → OCR (gemini only)** in sequence |
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

**Quota-exhaustion fallback**: when Gemini returns 429 / `RESOURCE_EXHAUSTED`, [`ocr_with_gemini.py`](../../../scripts/ocr_with_gemini.py) prints "Quota/rate-limit hit. Stopping." and exits with **code 2**. The daily bat catches that exit code and runs [`ocr_with_qwen.py`](../../../scripts/ocr_with_qwen.py) for `--limit 5` books before giving up — see Workflow A-2 below. Tomorrow's daily run starts with Gemini again on the fresh quota.

### Daily scheduler (set up + running)

The bat is now a **3-stage daily runner**: `ingest_new_books → parse_worker → ocr_with_gemini`.
Despite the historical name `KGLab-OCR-Daily`, it does more than OCR — see [`scripts/run_ocr_daily.bat`](../../../scripts/run_ocr_daily.bat).

| Component | Path |
|---|---|
| Bat runner | [`scripts/run_ocr_daily.bat`](../../../scripts/run_ocr_daily.bat) — runs ingest → parse → OCR in sequence; logs to `scripts/logs/ocr_YYYY-MM-DD.log` |
| Toast helper | [`scripts/notify.ps1`](../../../scripts/notify.ps1) — Windows toast wrapper. Bat fires it twice: at run start, and again if Gemini hits 429 (so user knows when to expect tomorrow's resumption) |
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
- `parse_error` starts with `OCR:` → permanent Gemini failure (model returned 0 usable pages, file too big, etc.). Won't auto-retry; investigate manually.
- `parse_error` starts with `Qwen-OCR:` → permanent Qwen failure (similar; Qwen returned no text, or too many per-page failures).
- Quota stop: script exits with code 2, "Quota/rate-limit hit. Stopping." → bat falls back to `ocr_with_qwen.py --limit 5` (Workflow A-2)
- `parse_error: 'file not found: ...'` → DB row references a Drive path that doesn't exist anymore (Drive sync disconnected, file moved/deleted, or rename divergence). Book is removed from OCR queue automatically; investigate by checking if `G:\` is mounted

---

## Workflow A-2 — Local Qwen2.5-VL OCR fallback (DISABLED 2026-05-06)

> Smoke-tested on RTX 4050 Mobile (6 GiB VRAM): qwen2.5vl:3b's vision compute graph alone needs **6.7 GiB** — Ollama scaled GPU layers from 20 → 0 trying to fit, then loaded the whole thing on CPU. CPU-mode rate measured ~1 token/min (3 tokens / 292 s) → ~8-15 hours per OCR page. Not viable on this hardware. The bat trigger is commented out; `ocr_with_qwen.py` and the gemini exit-code-2 plumbing stay intact for future hardware (≥ 8 GiB VRAM, or after switching to a smaller VLM like `moondream2`).

When the fallback IS enabled, [`scripts/ocr_with_qwen.py`](../../../scripts/ocr_with_qwen.py) takes over for the rest of the daily run when Gemini returns 429. Architecture:

1. PyMuPDF renders each PDF page at DPI 150 → JPEG bytes
2. POST image + Chinese-aware OCR prompt to Ollama `/api/generate` (model `qwen2.5vl:3b` by default)
3. Aggregate non-empty pages → same JSONL / R2 / DB-preview path as the Gemini script (helpers imported from `ocr_with_gemini`)

### Why limit 5 per run

Per-page Qwen latency on the dev machine (RTX 4050 Mobile, 6 GB VRAM) is ~10-30s. A 200-page book = 30-100 minutes. Setting `--limit 5` in the bat caps a daily fallback session at a few hours and keeps the laptop usable. The 391-book backlog is **not** meant to be cleared by Qwen — Gemini handles 250 books/day on the free tier when quota holds, so backlog converges in a couple of normal days. Qwen exists so progress doesn't completely stall when Gemini's down.

### Model choice

| Model | VRAM (q4) | Chinese OCR quality | Notes |
|---|---|---|---|
| `qwen2.5vl:3b` (**default**) | ~3 GB weights + ~6.7 GB compute graph | Decent — handles modern simplified/traditional well | Doesn't fit on 4050 Mobile 6 GB VRAM (compute graph alone exceeds it) |
| `qwen2.5vl:7b` | ~6 GB weights + larger graph | Notably better on dense traditional text | Even worse fit on 4050 Mobile |
| Llama 3.2 Vision | — | **Avoid** — English-heavy training, weak on 繁體 | |

Override with `--model qwen2.5vl:7b` if VRAM permits (close other GPU consumers first).

### Manual operations

```bash
# Check Ollama is up + model is pulled
ollama list | grep qwen2.5vl

# How many books would Qwen target?
python scripts/ocr_with_qwen.py status

# Run a small batch (default --limit 5)
python scripts/ocr_with_qwen.py run

# Force a specific model / DPI
python scripts/ocr_with_qwen.py run --model qwen2.5vl:7b --dpi 200 --limit 3
```

### Failure modes

- Ollama daemon not running → script exits 1 with `❌ Ollama not reachable`. Launch the Ollama desktop app or run `ollama serve`.
- Model not pulled → `ollama pull qwen2.5vl:3b`.
- Per-page errors > 25% of pages → book is marked `parse_error: 'Qwen-OCR: too many page failures'` (won't auto-retry; investigate the PDF).
- VRAM OOM mid-run → fall back to `--model qwen2.5vl:3b` or close GPU-using apps.

---

## Workflow D — Daily new-book drop ingest

The user drops freshly-acquired ebooks into [`.claude/skills/ebook-pipeline/new-book/`](./new-book/) (a local folder, not on Drive). [`scripts/ingest_new_books.py`](../../../scripts/ingest_new_books.py) processes that folder once per day as part of `run_ocr_daily.bat`. For each ebook file (`.pdf` / `.epub` / `.mobi` / `.azw3`):

1. **Parse filename** → `(author, title, ext)`. Reuses `parse_drive_inventory.parse_filename()` after pre-stripping z-library suffixes like `(z-library.sk, 1lib.sk, z-lib.sk)` (the parent parser only knows the older `(z-lib.org)` form, and the inner commas trip its 全形/半形 comma split).
2. **Classify** into one of the 9 main categories. Two-tier:
   - **Keyword fallback first** (free): hits `christ|church|bonhoeffer|syriac|nestorius|cyril|monophysite|chalcedon|ephrem|babai|homilies|patristic|apostolic|gospel|biblical|theology` → `宗教學`; hits `zoroastr|avesta|islam|buddhis` → `世界宗教`.
   - **Gemini 2.5 Flash** otherwise — strict JSON output, prompt explains the 9 categories. LLM mistakes like "基督教"/"神學" get auto-mapped to 宗教學.
3. **Insert** an `ebooks` row with `category` set, `parsed_at = NULL`, `file_path` pointing to the *future* Drive location (the move below puts it there).
4. **Move** local file → `G:/我的雲端硬碟/資料/電子書/{category}/{author}，{title}.{ext}`. Because G: **is** the Drive sync mount, the move IS the upload (Drive client uploads in the background) AND the local-delete in one filesystem rename. No OAuth / Drive API setup needed.

After ingest, the new rows appear in `ebooks` with `parsed_at = NULL`. The next `parse_worker.py run` (triggered by step 2 of the daily bat, or manually) extracts text where possible. If extraction fails (`parse_error LIKE '%no extractable text%'`), `ocr_with_gemini.py` picks it up in step 3.

### Manual operations

```bash
python scripts/ingest_new_books.py status              # how many ebooks waiting in new-book/
python scripts/ingest_new_books.py run --dry-run       # preview classification + target paths
python scripts/ingest_new_books.py run --limit 3       # smoke test 3 books for real
python scripts/ingest_new_books.py run                 # full sweep
```

### Failure modes

- **DB insert fails** → file kept in `new-book/`; safe to re-run, no orphan row.
- **Move fails after DB insert** → file kept in `new-book/`, DB row inserted but file not on Drive. Script prints both paths so you can either move manually or delete the row. Rare on Windows (cross-drive move = copy then delete).
- **Gemini quota / 429** → that single book is skipped (file kept), other books continue with the keyword fallback. Tomorrow's run picks up the skipped book.
- **Filename can't be parsed** (no usable title) → logged "SKIP: could not parse title from filename"; file kept; add a manual override to `parse_drive_inventory.TITLE_AUTHOR_OVERRIDES` or rename the file manually.
- **Target file already exists on Drive** (duplicate book) → skip, file kept in `new-book/`. Manual cleanup needed.

### Tuning notes

- The keyword fallback skews heavily toward Christian-studies content (current user backlog) — if a different research area dominates a future drop, extend `fallback_category()` in [`scripts/ingest_new_books.py`](../../../scripts/ingest_new_books.py).
- Gemini share the same daily quota with the OCR runner. Order in the bat is **ingest first** (small, ~1-5 calls/day) so OCR's heavy usage can't starve it. RPM is gentle (`time.sleep(0.5)` between books).
- Junk files in `new-book/` (e.g., `Z-Library-latest.exe`) are silently ignored — only `EBOOK_EXTS` are touched.

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
  → If quota hit and bat fell back to Qwen, look for "--- gemini quota hit, falling back to ocr_with_qwen ---" line.
  → If quota hit BUT Qwen also failed, ensure Ollama daemon is running and qwen2.5vl:3b is pulled.
  → Otherwise: just wait — tomorrow's run picks up.

Many books in OCR queue showing "file not found"?
  → Probably G: drive (Drive sync) is disconnected. Check: `Get-PSDrive -PSProvider FileSystem` should list G:.
  → Re-launch Google Drive client. The "file not found" parse_errors stay until you manually flip them back to "no extractable text" once Drive is back.

A new book dropped into new-book/ never showed up in the reader?
  → Check scripts/logs/ocr_YYYY-MM-DD.log "--- ingest_new_books ---" section.
  → 'CLASSIFY FAILED' = Gemini quota; tomorrow retries automatically.
  → 'could not parse title' = filename pattern unsupported; rename or extend TITLE_AUTHOR_OVERRIDES.
  → 'target already exists on Drive' = duplicate book, manual cleanup.
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

1. Run all three status checks to see what's queued:
   ```bash
   python scripts/ingest_new_books.py status
   python scripts/repopulate_chunk_previews.py status
   python scripts/ocr_with_gemini.py status
   ```
2. If `new-book/` has files waiting → run `python scripts/ingest_new_books.py run` (Workflow D).
3. Read [`standardize-ebook` SKILL](../standardize-ebook/SKILL.md) before touching that pipeline.
4. Don't re-run `standardize_ebook.py` on books with annotations (`annotations` table). Currently only 文明的歷史 has any.
5. For categorized batch standardize (哲學 → others), use `--dry-run` first, then real run.
6. Watch the daily scheduler each afternoon at 16:00 — read the day's log file in `scripts/logs/`. Logs are still named `ocr_YYYY-MM-DD.log` but now also contain ingest + parse output.

## See also

- [`standardize-ebook` SKILL](../standardize-ebook/SKILL.md) — detail-level skill for the markdown standardize pipeline
- [`EBOOK_PIPELINE.md`](../../../EBOOK_PIPELINE.md) at repo root — original design doc
- [`scripts/haiku_cleanup_guide.md`](../../../scripts/haiku_cleanup_guide.md) — Haiku-based text cleanup (separate from standardize; used pre-standardize, mostly historical now)
