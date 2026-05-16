---
name: ebook-pipeline
description: Operate the Know-Graph-Lab ebook pipeline end-to-end. Use when working on parsing books from Drive into Supabase, OCR'ing scanned PDFs (daily Gemini scheduler), back-filling DB previews from local JSONL, standardizing EPUBs into reader-ready markdown, or wiring the reader to chunks. The hub for everything book-content-related.
---

# Ebook Pipeline Skill

End-to-end pipeline that takes books from a local Drive folder all the way to the reader at `/ebook/[id]`. This file is the **operational hub** — what runs, in what order, how to monitor it, and how to recover when it breaks. For the standardization step specifically (turning EPUBs into reader-ready markdown), see the **`standardize-ebook` skill** which is the detail-level companion.

## Current state (snapshot 2026-05-14)

| Stage | Status | Numbers |
|---|---|---|
| Drive scan + author/title parse | ✅ done | 1,309 books (initial sweep) |
| **Daily z-lib drop ingest** | ✅ wired into daily scheduler + **auto-deletes dupes** (2026-05-14) | `ingest_new_books.py` — see Workflow D |
| File rename in Drive | ✅ done | all renamed to `作者，書名.ext` |
| DB import (`ebooks` table) | ✅ rolling | grew to ~1,450 rows after 套書 split (was 1,326) |
| First-pass parse (text-extractable) | ✅ done | 921 parsed (484 EPUB + 437 text PDF) |
| mobi/azw3 → epub conversion | ✅ done | 0 remaining |
| **OCR scanned PDFs (Haiku Vision)** | 🔄 long-running OCR run started 2026-05-13 07:20 | 271-book queue; batch-level retry shipped 2026-05-13 (`89377eb`) so mid-book 502 no longer wastes batches |
| **OCR scanned PDFs (Gemini)** | 🔄 every-6h scheduled | `13 */6 * * *`; 4 rotating keys; Haiku takes over only when user orders |
| Local JSONL written | ✅ done for parsed books | `G:/我的雲端硬碟/資料/電子書/_chunks/*.jsonl` |
| R2 mirror of JSONL | ✅ done | mirrored on parse / OCR / standardize |
| `ebook_chunks` previews in DB | ✅ caught up | back-fill via `repopulate_chunk_previews.py retry-failed` |
| Frontend reads chunks | ✅ wired | `loadChunk()` from local→R2 fallback |
| Reader v2 UI (light theme + TOC + highlights + notes panel + bookshelf + tags + bookmarks) | ✅ done | with auto-save, error toasts |
| Search by title / author / fulltext | ✅ wired | `/api/ebooks/search?mode=…` |
| **EPUB standardize → markdown reader format** | ✅ done + sidebar fixes 2026-05-14 | 505/505 EPUBs format=markdown; 0 filename leaks; 0 chunks below heading-rate threshold (was 21 / 41 / 68) |
| **PDF standardize Plan A (lite)** | ✅ done | 437/437 text-extractable PDFs polished |
| **PDF standardize Plan B v0 (TOC-driven)** | ✅ done + sidebar headings ✅ (2026-05-14) | 207 Plan-B PDFs backfilled with `##` / `###` markdown headings via `backfill_pdf_headings.py` so reader sidebar renders nesting; Plan B v1 (font-driven, no-TOC subset) still deferred |
| **套書 splitting** | ✅ done 2026-05-14 | Phase 1: 19 splittable → 132 children. Phase 2: 16 unsplittable processed via `detect_set_volumes.py` (Haiku) → 14 marked NOT_A_SET (single-volume despite title) + 2 multi-volume split into 18 children. Auto-split now wired into `standardize_ebook` + daily bat. |
| **Online metadata enrichment** | ✅ done | 89% publisher / 87% publish_year coverage |
| **books / excerpts library** | ✅ done | `/excerpts/library`, tags, Markdown export, daily bookmark |

## Pipeline scripts overview (all in `scripts/`)

| Script | Phase | Purpose |
|---|---|---|
| `local_drive_pipeline.py` | 1 — ingest (initial sweep) | Scan Drive, parse `作者，書名.ext`, rename in place |
| `parse_drive_inventory.py` | 1 — ingest | Library: `parse_filename()`, `to_traditional()`, `TITLE_AUTHOR_OVERRIDES` |
| `import_local_to_supabase.py` | 1 — ingest (initial sweep) | `data/local_inventory.json` → `ebooks` rows |
| `ingest_new_books.py` | 1 — ingest (**daily**) | Watches `z-lib/` at the project root. Parses filename, classifies via Gemini (with keyword fallback), inserts ebooks row, moves file to `G:/.../電子書/{category}/`. See Workflow D |
| `parse_worker.py` | 2 — parse | **Main parser** (PyMuPDF + ebooklib). `init` / `run [--limit N] [--retry-errors]` / `status` |
| `convert_mobi_to_epub.py` | 2 — parse | Calibre wrapper for mobi/azw3 → epub. Already done; keep for new files |
| `ocr_with_gemini.py` | 3 — OCR (primary) | Gemini Vision OCR for scanned PDFs. Pushes JSONL to R2 inline. Exits with code 2 when daily quota hits (signals fallback) |
| `ocr_with_qwen.py` | 3 — OCR (fallback, **disabled**) | Local Qwen2.5-VL via Ollama. Code intact; bat trigger commented out — vision compute graph (6.7 GiB) won't fit on 4050 Mobile (6 GiB). Re-enable on better GPU. See Workflow A-2 |
| `run_ocr_daily.bat` + Task Scheduler | (orchestrator) | Windows daily runner — runs **ingest → parse → OCR (gemini only)** in sequence |
| `standardize_ebook.py` | 4 — standardize | Re-parse EPUB → markdown chunks, s2tw, drop boilerplate (see `standardize-ebook` skill) |
| `standardize_pdf_lite.py` | 4 — standardize | Plan A polish over per-page JSONL: s2tw + collapse spacing + extract publisher metadata. `page_number` preserved exactly. See `standardize-pdf` skill |
| `standardize_pdf.py` | 4 — standardize | Plan B TOC-driven re-chunking. Reads existing JSONL + PDF TOC → emits chapter-level chunks with `page_range`. Falls back to Plan A on books without usable TOC. See `standardize-pdf` skill |
| `enrich_book_metadata.py` | 4b — backfill | Online lookup (Google Books → Open Library) to fill missing `publisher` / `publish_year` on `books` rows. Idempotent; respects `metadata_locked`. `status` / `run [--limit N] [--dry-run] [--book <id>]` / `probe --book <id>` |
| `detect_set_volumes.py` | 4c — 套書 prep | Haiku-driven volume boundary detection for 套書 lacking volume metadata. Builds a TOC from chunk h2/h3 headings, asks Haiku 4.5 to identify volume boundaries, writes `volume` field into JSONL OR marks `NOT_A_SET_MARKER` if single-volume despite title. `status` / `run --book <id>` / `run --all` |
| `split_ebook_set.py` | 4d — 套書 split | Split a multi-volume ebook into one row per volume. Idempotent (skips books already marked with `SPLIT_MARKER` / `NOT_A_SET_MARKER` / annotations). `status` / `run --book <id>` / `run --all` |
| `resplit_giant_chunks.py` | 4e — chunk refinement | Break oversized chunks (>400K chars) by their internal `##` / `###` markdown headings; reduces "1-chunk-per-book" cases to reasonable per-section sizes. Annotation guard. Doesn't help chunks without internal headings (those need LLM/font-size). `status` / `run --book <id>` / `run --all` |
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

### Scheduler (set up + running)

The bat is now a **5-step runner**: `ingest_new_books → parse_worker → ocr_with_gemini → detect_set_volumes → split_ebook_set`.
Despite the historical name `KGLab-OCR-Daily`, it does more than OCR — see [`scripts/run_ocr_daily.bat`](../../../scripts/run_ocr_daily.bat). Steps 4a/4b are idempotent (no-op when no 套書 is pending).

| Component | Path |
|---|---|
| Bat runner | [`scripts/run_ocr_daily.bat`](../../../scripts/run_ocr_daily.bat) — runs ingest → parse → OCR in sequence; logs to `scripts/logs/ocr_YYYY-MM-DD.log` |
| Toast helper | [`scripts/notify.ps1`](../../../scripts/notify.ps1) — Windows toast wrapper. Bat fires it twice: at run start, and again if Gemini hits 429 (so user knows when to expect tomorrow's resumption) |
| Windows Task | `KGLab-OCR-Daily` registered via `Register-ScheduledTask` |
| Trigger | **Daily 16:00** (Taipei time). The "every 6 hours" version was reverted; current state confirmed via `Get-ScheduledTask` 2026-05-14 |
| Behavior | `WakeToRun` + `StartWhenAvailable` — wakes from sleep, catches up if missed |
| Run as | Current user, Interactive logon (no password stored; only fires while logged in) |
| Cap | 12-hour `ExecutionTimeLimit` |

### Bat hardening (2026-05-14) — post-mortem on missing 5/8-5/13 logs

**Symptom.** Between 2026-05-08 and 2026-05-13, `scripts/logs/` got zero new log files even though `Get-ScheduledTaskInfo` reported `LastRunTime = 2026-05-13 16:00:01` with `LastTaskResult = 0`. `scripts/logs/` directory mtime stayed pinned at 2026-05-07 08:05, so the bat literally never created any file during that window.

**Three independent root causes, all fixed in `run_ocr_daily.bat`:**

1. **`wmic os get localdatetime` is being deprecated and unreliable in Task Scheduler's wake-from-sleep context.** When wmic returned nothing, `TODAY` became the literal string `%DT:~0,4%-%DT:~4,2%-%DT:~6,2%`, so `LOGFILE` resolved to a path with `%` characters — every `>> "%LOGFILE%"` then failed silently while bat still finished with exit 0. **Fix:** swap in `powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd"`.
2. **`python` on the system `PATH` resolves to `_whisper_venv\Scripts\python.exe` (Apr 29-created Whisper venv) which doesn't have `ebooklib` / `fitz` / `google.genai`.** In Task Scheduler's context the same resolution happens, so each `python scripts\xxx.py` line would `ModuleNotFoundError` and exit fast — no work done, no log lines logged. **Fix:** hardcode `set PY=C:\Users\user\AppData\Local\Python\bin\python.exe` and use `"%PY%"`. Falls back to PATH `python` if that path is gone (preserving install-and-run smoke testing).
3. **The Write tool that wrote the new bat used LF-only line endings.** `cmd.exe` strictly requires CRLF for `.bat`; with LF-only it ate the first char of each line ("'M' is not recognized" for every `REM`, `etlocal` for `setlocal`, etc.). The original bat happened to have CRLF (committed via VS Code on Windows) so this was a regression introduced by the same-day fix. **Fix:** force CRLF on save. When editing the bat in the future, save with CRLF or run `(Get-Content x.bat) | Set-Content -Encoding utf8 x.bat` to renormalize.

**Added robustness** — each step now logs its own exit code:
```
step1 exit=0
step2 exit=0
step3 exit=2     # = Gemini quota hit, expected
```
A future silent failure now leaves a fingerprint instead of an empty log.

**Verification done 2026-05-14 11:38.** Drained 14-book z-lib backlog (Workflow D, 10 ingested + 4 dupes auto-deleted), then manually re-ran the fixed bat. `scripts/logs/ocr_2026-05-14.log` got written with all expected header lines and exit codes; parse + OCR continued in the background.

### OCR engine policy (2026-05-07)

**Default: Gemini** (`ocr_with_gemini.py`) — uses 4 rotating Google API keys; 503 = transient server overload (does NOT overwrite `parse_error`; next run retries); 429 = daily quota exhausted (script exits code 2).

**Claude Haiku Vision**: ONLY when user explicitly orders it. **Always one book at a time** — launching multiple parallel Haiku agents simultaneously exhausted the entire Max subscription token quota with zero books completed (2026-05-07). Two integration paths exist:

1. **Built-in `--engine haiku`** (2026-05-14, recommended). `ocr_with_gemini.py` now supports `--engine {gemini,haiku}` plus `--book <id>` / `--exclude <id>` (both repeatable). Haiku mode skips Gemini entirely and uses `process_one_haiku()` sequentially over the filtered queue. Authentication via `ANTHROPIC_API_KEY` or, if absent, the Claude Code OAuth token in `~/.claude/.credentials.json`.

2. **Manual Agent** for ad-hoc single-book OCR — `Agent(..., model="haiku", ...)`, pass PDF path via `@file` to avoid Windows shell Chinese encoding issues, wait for completion before starting next.

Quota-exhaustion fallback (Gemini → Haiku) is still wired separately — when all Gemini keys hit 429 mid-run, the script auto-switches to Haiku for the current book and all remaining books in the same run.

### OCR robustness patches (2026-05-14 → 05-16 manual run)

Long sessions of `ocr_with_gemini.py run` exposed five recurring failure modes that previously discarded books on transient issues. All shipped on master:

| Commit | Fix | Why it matters |
|---|---|---|
| `9729b0a` | `json_repair` salvage filters non-dict pages (`isinstance(p, dict)`); 0-byte file preflight before Gemini upload | A single non-dict element after Gemini truncates JSON would crash the whole book after json_repair had already recovered 100+ pages. 0-byte PDFs no longer waste a 400 round-trip. |
| `672c948` | Haiku image render → JPEG q=85 with auto-downsample loop (150 → 120 → 96 → 75 → 60 DPI) until under Anthropic's 5 MB image cap | At 150 DPI PNG a dense 17-20 MB scanned page renders to ~8 MB → permanent 400. All large books now succeed at 120 DPI JPEG. |
| `5e44dc1` | `insert_chunk_previews` uses adaptive batching (50 → 20 → 5 → 1) on 57014 / 5xx, matching parse_worker / repopulate / split_ebook_set | A single Supabase IO spike was discarding an entire 30-minute Haiku OCR run. |
| `230d8b1` | When Gemini rejects with "exceeds the supported page limit of 1000", auto-fall back inline to Haiku for that single book | Haiku image-batch API has no 1000-page cap. Books like 羅馬尼亞通史簡編 (1381 pages, recovered ✓) / 中國宗教通史 (1294 pages) no longer need manual `--book` Haiku runs. |
| `6211844` | When the oversized-PDF Haiku fallback above hits its own transient failure (connection error / 502 / 500), force `result.transient = True` | Without this, a transient Haiku blip during the oversized fallback would permanent-mark a >1000-page book even though the underlying issue is recoverable. |

**Operational gotchas surfaced this run** (not yet patched, log them when retrying these workflows):

- **OAuth token in `~/.claude/.credentials.json` expires every few hours.** A long-running `ocr_with_gemini.py` loads the token at startup and keeps using it in memory — once it expires, every Haiku call returns `Error code: 401`. The fix is kill + restart so the next instance reads the refreshed file. Auto-refresh would be a small enhancement.
- **Python's DNS resolver caches failures.** After a brief local network blip, all subsequent socket calls inside the same process keep returning `getaddrinfo failed` even after `ping` confirms upstream is reachable. Kill + restart fixes this too.
- **Anthropic rolling rate limit** — after ~6-7 consecutive Haiku books, the next requests return Cloudflare 502 / `Connection error` for ~30 minutes. The script doesn't pause; it churns through books with transient-mark failures. Tomorrow's daily run picks them up since transient = stays in queue.
- **Content-filter rejections** (e.g. 哥白尼革命, 規訓與懲罰, 走向馬克思主義的人道主義, 新版宗教史叢書 4卷本) — Haiku returns `Output blocked by content filtering policy`. These need a different OCR engine; currently they leave the queue marked permanent.

**Split-queue pattern (2026-05-14):** when specific books are known-Gemini-only (e.g. Haiku content-filter rejects 哥白尼革命 / 規訓與懲罰), run them in parallel with the rest:
```bash
# Gemini for the 2 known-Gemini-only books
python scripts/ocr_with_gemini.py run --engine gemini \
  --book acf454b2-b7e4-4dac-8110-17f311ede2ed \
  --book a54fb48e-0255-4f64-983f-dd5a89b31995

# Haiku for everything else
python scripts/ocr_with_gemini.py run --engine haiku \
  --exclude acf454b2-b7e4-4dac-8110-17f311ede2ed \
  --exclude a54fb48e-0255-4f64-983f-dd5a89b31995
```
These two share the OCR queue at the DB layer, but with `--book` / `--exclude` set to disjoint sets they never race on the same book.

**First split-queue run (2026-05-14 ~12:00).** Gemini side finished in 13 minutes (`哥白尼革命` 15 pages / 98K chars; `規訓與懲罰` 55 pages / 66K chars — both books Haiku had refused via content-filter). Haiku side started simultaneously on the remaining 284-book queue; one book at a time means total wall-clock is expected in days, not hours.

**Haiku bulk-mode lesson (2026-05-14 afternoon — DON'T do this).** Right after the split-queue launch, the Haiku side processed book 1 successfully (人的發現, 176 pages, 20 min) and then **the next 283 books all failed within ~25 minutes** — most with `Connection error` from the Anthropic SDK, the rest with PyMuPDF `Failed to open file` after Drive sync hiccuped. None of the failures were recorded in DB because Supabase REST was also unreachable in that same window (`HTTPSConnectionPool ... Max retries exceeded`). Net result: 1 success, 283 untouched-in-DB books still in the queue. The 5/7 Max-subscription-exhaustion incident repeated in a different shape — bulk Haiku just doesn't work.

**Haiku one-at-a-time pattern (the only viable Haiku usage at scale).** Per-book invocation with `--engine haiku --book <id>` succeeds reliably for a small batch:

| Book | Pages | Chars | Time | Quality |
|---|---|---|---|---|
| 人的發現 | 176 | 78K | 20 min | ✓ clean |
| 現代物理學和東方神秘主義 | 221 | 95K | 24 min | ✓ clean |
| 我們必須給歷史分期嗎？ | 151 | 78K | 17 min | ✓ clean |
| 生命言說與社群認同 | 156 | 117K | 30 min | ✓ clean |
| 民族主義的不正當性 | 147–168 | 62–75K | 14 min | ⚠ repetition + scrambled columns (vertical-typography book) |

After ~6 consecutive single-book invocations Anthropic's rolling rate limit kicks in and the next call returns `Connection error`. Cooldown ~30+ minutes. **Effective throughput ~6 books/hour with cooldown, ~50 books/day max** — still worse than Gemini's 250/day. For the foreseeable future:

- **Default for bulk OCR: Gemini** (via the daily 16:00 bat). Sustains 200-250 books/day on free tier.
- **Haiku via `--engine haiku --book <id>`**: ad-hoc for one book at a time, used when (a) a specific book is known to break Gemini (e.g. 413 / response truncation on large PDFs) or (b) user explicitly orders it.
- **Vertical-typography Chinese books** (e.g. 民族主義的不正當性, Tagore translation): both Haiku and Gemini struggle — Haiku scrambles column order, Gemini truncates JSON on output. No good fix shipped yet; books standardize-as-best-we-can and may need manual repair in the reader.

Book 5 specifically — we tried Haiku (repetition + scrambled), then Gemini (clean but only 31/187 pages because Gemini's JSON output got truncated), then Haiku again (147 pages, similar repetition). Settled on Haiku 147-page version per user's "rather have 90% coverage with quality issues than 17% clean".

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

### Temp-file cleanup policy

The shipped OCR scripts do NOT leave images on disk:

- `ocr_with_claude_cli.py` — renders each page to PNG/JPEG bytes in memory via `pix.tobytes()`, base64-encodes inline. No filesystem writes.
- `ocr_with_gemini.py` — uses `tempfile.NamedTemporaryFile` (system tmp dir, e.g. `%TEMP%`) and `unlink()` in `finally`. Auto-cleaned.

If you ever spot `ocr_*.png` / `ocr_*.jpg` / book-render PDFs accumulating in `C:\tmp\` (or any working dir), they are leftovers from experimental scripts (e.g. the 2026-05-07 parallel-Haiku-agents attempt that left ~650 PNGs / ~200 MB before being abandoned). **Once the corresponding books are OCR'd + standardized (Plan A / Plan B complete), delete them.** Cleanup command:

```bash
# Bulk delete after confirming the relevant books are parsed_at IS NOT NULL
rm /c/tmp/ocr_*.png /c/tmp/ocr_*.jpg /c/tmp/book_*.pdf 2>/dev/null
```

When writing any new OCR variant: render to memory if possible. If a temp file is unavoidable (e.g. an SDK that requires a file path), put it in `tempfile.TemporaryDirectory()` or `NamedTemporaryFile(delete=True)` so cleanup is automatic — never accumulate in a project-level `tmp/` folder.

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

## Workflow D — Daily z-lib drop ingest

The user drops freshly-acquired ebooks into [`z-lib/`](../../../z-lib/) at the project root (a local folder, not on Drive). Filename suffix `(z-library.sk, 1lib.sk, z-lib.sk)` from the source is preserved on disk and stripped during parse. [`scripts/ingest_new_books.py`](../../../scripts/ingest_new_books.py) processes that folder once per day as part of `run_ocr_daily.bat`. For each ebook file (`.pdf` / `.epub` / `.mobi` / `.azw3`):

1. **Parse filename** → `(author, title, ext)`. Reuses `parse_drive_inventory.parse_filename()` after pre-stripping z-library suffixes like `(z-library.sk, 1lib.sk, z-lib.sk)` (the parent parser only knows the older `(z-lib.org)` form, and the inner commas trip its 全形/半形 comma split).
2. **Classify** into one of the 9 main categories. Two-tier:
   - **Keyword fallback first** (free): hits `christ|church|bonhoeffer|syriac|nestorius|cyril|monophysite|chalcedon|ephrem|babai|homilies|patristic|apostolic|gospel|biblical|theology` → `宗教學`; hits `zoroastr|avesta|islam|buddhis` → `世界宗教`.
   - **Gemini 2.5 Flash** otherwise — strict JSON output, prompt explains the 9 categories. LLM mistakes like "基督教"/"神學" get auto-mapped to 宗教學.
3. **Insert** an `ebooks` row with `category` set, `parsed_at = NULL`, `file_path` pointing to the *future* Drive location (the move below puts it there).
4. **Move** local file → `G:/我的雲端硬碟/資料/電子書/{category}/{author}，{title}.{ext}`. Because G: **is** the Drive sync mount, the move IS the upload (Drive client uploads in the background) AND the local-delete in one filesystem rename. No OAuth / Drive API setup needed.

After ingest, the new rows appear in `ebooks` with `parsed_at = NULL`. The next `parse_worker.py run` (triggered by step 2 of the daily bat, or manually) extracts text where possible. If extraction fails (`parse_error LIKE '%no extractable text%'`), `ocr_with_gemini.py` picks it up in step 3.

### Manual operations

```bash
python scripts/ingest_new_books.py status              # how many ebooks waiting in z-lib/
python scripts/ingest_new_books.py run --dry-run       # preview classification + target paths
python scripts/ingest_new_books.py run --limit 3       # smoke test 3 books for real
python scripts/ingest_new_books.py run                 # full sweep
```

### Failure modes

- **DB insert fails** → file kept in `z-lib/`; safe to re-run, no orphan row.
- **Move fails after DB insert** → file kept in `z-lib/`, DB row inserted but file not on Drive. Script prints both paths so you can either move manually or delete the row. Rare on Windows (cross-drive move = copy then delete).
- **Gemini quota / 429** → that single book is skipped (file kept), other books continue with the keyword fallback. Tomorrow's run picks up the skipped book.
- **Filename can't be parsed** (no usable title) → logged "SKIP: could not parse title from filename"; file kept; add a manual override to `parse_drive_inventory.TITLE_AUTHOR_OVERRIDES` or rename the file manually.
- **Target file already exists on Drive** (duplicate book) → **auto-delete the `z-lib/` copy** (since 2026-05-14). Logs both file sizes for verification before unlinking. User explicitly asked for this so daily runs stop re-scanning the same dupes.

### Tuning notes

- The keyword fallback skews heavily toward Christian-studies content (current user backlog) — if a different research area dominates a future drop, extend `fallback_category()` in [`scripts/ingest_new_books.py`](../../../scripts/ingest_new_books.py).
- Gemini share the same daily quota with the OCR runner. Order in the bat is **ingest first** (small, ~1-5 calls/day) so OCR's heavy usage can't starve it. RPM is gentle (`time.sleep(0.5)` between books).
- Junk files in `z-lib/` (e.g., `Z-Library-latest.exe`) are silently ignored — only `EBOOK_EXTS` are touched.

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

A new book dropped into z-lib/ never showed up in the reader?
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
2. If `z-lib/` has files waiting → run `python scripts/ingest_new_books.py run` (Workflow D).
3. Read [`standardize-ebook` SKILL](../standardize-ebook/SKILL.md) before touching that pipeline.
4. Don't re-run `standardize_ebook.py` on books with annotations (`annotations` table). Currently only 文明的歷史 has any.
5. For categorized batch standardize (哲學 → others), use `--dry-run` first, then real run.
6. Watch the daily scheduler each afternoon at 16:00 — read the day's log file in `scripts/logs/`. Logs are still named `ocr_YYYY-MM-DD.log` but now also contain ingest + parse output.

## Reader-side features tied to the pipeline

### Bookshelf + reading bookmarks

Per-user reading state. Schema in
[`database/bookshelf-and-bookmarks.sql`](../../../database/bookshelf-and-bookmarks.sql).
RLS on; service-role endpoints filter by `user_id`.

- `user_reading_status (user_id, ebook_id, status, updated_at)` — `status ∈ 'reading' | 'read'`. PK enforces one row per user-book.
- `reading_bookmarks (id, user_id, ebook_id, chunk_index, created_at)` — date-stamped 「今日讀到這裡」 markers; multiple per book.

Endpoints:
- `PUT /api/ebooks/:id/reading-status` body `{status}` — null removes
- `GET /api/ebooks/:id/reading-status`
- `POST/GET /api/ebooks/:id/bookmarks`, `DELETE /api/bookmarks/:id`
- `GET /api/me/bookshelf` — merged listing for `/bookshelf` page + `/ebook` sidebar counts

Reader UX (`pages/ebook/[id].vue`):
- Toolbar status pill cycles 📚 → 📖 (reading) → ✅ (read) → 📚
- 「📅 今日讀到這裡」 button only when status is `reading`
- TOC sidebar shows date badges next to chunks with bookmarks (hover-× to delete)
- Auto-jump to latest bookmark on book open if status=`reading` AND no `?page=` in URL; skipped when status=`read`

`/ebook` sidebar has `📖 閱讀中 (n) / ✅ 已讀 (n)` entries below the categories — same URL-driven model as categories (`?shelf=reading|read`). `app/router.options.ts` adds `scrollBehavior(savedPosition)` so browser back from `/ebook/:id` → `/ebook` returns to the previous scroll.

### Excerpts auto-flow (`save_as_excerpt: true` on `POST /api/annotations`)

Reader's 「+ 書摘」 button creates an annotation **and**:
1. If the ebook's `book_id` is null → auto-creates a `books` row using ALL the rich metadata extracted by standardize (title / author / translator / publisher / publication_year / original_title / original_author / original_publish_year). Writes `book_id` back to ebooks.
2. Inserts an `excerpts` row with `content` + `title` (required, prompted via modal) + `chapter` (= `pageChapter` from reader) + `page_number` (= `第 N 段`) + the new `book_id`.
3. Links annotation to excerpt via `excerpt_id`.

Result: the book appears in `/excerpts/library` with rich metadata, excerpts grouped by chapter on `/excerpts/library/[bookId]`, and search results stay fresh because that page refetches `allBooks` on `visibilitychange`.

### Tags (`tags` + `book_tags` + `excerpt_tags`)

Cross-cut, network-style organization that complements the existing tree
categories. Schema in
[`database/tags.sql`](../../../database/tags.sql), applied via the
Management API (psycopg2 direct DB blocked by IPv6-only DNS — see the
auto-memory `reference_supabase_management_api.md`).

- `tags (id, name, color, created_at)` — global, name unique
  (case-insensitive lookup keeps the picker idempotent)
- `book_tags (book_id, tag_id)` and `excerpt_tags (excerpt_id, tag_id)`
  — junction tables, CASCADE on entity delete

Endpoints:
- `GET/POST /api/tags`, `DELETE /api/tags/:id`
- `GET/PUT /api/books/:id/tags`, `GET/PUT /api/excerpts/:id/tags`
- `tagId` query param on `/api/books` and `/api/ebooks` (resolves
  `book_tags` to a set of book_ids first, then narrows the listing query)

Reusable [`components/TagPicker.vue`](../../../components/TagPicker.vue)
shows selected tags as chips, typeahead-filters existing tags, creates
new ones on Enter (server returns the existing row when name collides).
Wired into:
- `/excerpts/library/[bookId]` book metadata block (book-level tags)
- per-excerpt card on the same page (excerpt-level tags)

URL-driven filter `?tag=<id>`:
- `/excerpts/library` shows a tag chip strip below search bar
- `/ebook` shows a 「標籤」 sidebar section below 「我的書櫃」 (only
  rendered when at least one tag exists)

### Markdown citation export

「📋 匯出 Markdown」 button on `/excerpts/library/[bookId]` toolbar.
Builds a self-contained markdown document:
- Bibliographic header (title / author / translator / publisher / year
  + Original publication line for translations)
- Chapter-grouped excerpt blocks with `> blockquote` content and
  `——《book》, chapter, page` citation tails

Copies to clipboard AND triggers a `<book-title>.md` download in one
click. No backend involved (built client-side from already-loaded
`book.value` + `chapterGroups`).

## Pending TODOs

### 2026-05-14 session log — sidebar + 套書 + dedup work

If you're a fresh agent picking this up, this is what changed in the
**2026-05-14 session** so you don't redo finished work:

| Done | Commit | What |
|---|---|---|
| ✅ | `89377eb` | OCR `process_one` retries each batch in-place — mid-book 502 no longer wastes accumulated pages |
| ✅ | `3905933` | PDF Plan B (`standardize_pdf.py`) now prepends `## chapter_title` markdown heading + `format=markdown`. `scripts/backfill_pdf_headings.py` retroactively fixed 207 Plan-B PDFs |
| ✅ | `6808f7f` | `standardize_ebook.py` — added EN `CHAPTER N` / `BOOK II` regex + content-hash disambiguator on truncate fallback. Re-standardized 41 books with filename leaks |
| ✅ | `7fc64d1` | `standardize_ebook.py` — legacy flat-TOC mode also prepends `##` so 68 EPUBs at <40% heading rate are now at 100% |
| ✅ | `609aca4` | `ingest_new_books.py` — when target on Drive already exists, **auto-delete the z-lib/ copy** + log sizes |
| ✅ | `2a883ed` + `8e8c4c1` | New `scripts/split_ebook_set.py` — split 套書 ebook into per-volume children. Heading levels flattened to `##`. 19 books split into 132 child ebooks |

**End-of-session metrics:**
- 0 EPUBs format=None (was 21)
- 0 filename leaks (was 41, 695 leak entries)
- 0 EPUBs below heading-rate threshold (was 68)
- 132 child ebooks from 套書 split (across 18 source EPUBs after 康德 dedup)
- 16 套書 still unsplittable (chunks `volume=None`) — Phase 2 work

**Remaining TODOs (priority order):**

1. ~~45 EPUBs with single chunk >400KB~~ — ⚠ partial done 2026-05-14 via `resplit_giant_chunks.py`. Internal-heading resplit took 24/61 eligible EPUBs from `61 books × 83 oversized chunks` → `44 books × 75 oversized chunks` (+547 new sub-chunks). Wins: 追逐榮耀 1→10 chunks, 牛津世界史叢書 16→140, 七大洋上的爭霸戰 47→173, 鹽野七生作品集 44→144. **37 EPUBs still resistant** — their giant chunks contain no `##`/`###` markdown headings at all, so this script's deterministic h2/h3 split has nothing to grab. Those need a different strategy (LLM page-boundary detection on the raw text, or going back to the raw EPUB HTML for font-size cues — neither shipped).
2. ~~16 套書 with `volume=None`~~ — ✅ done 2026-05-14 via `detect_set_volumes.py` (Haiku).
3. **Content-filter-rejected books** (Haiku OCR refuses) — book 4 `哥白尼革命`, book 44 `規訓與懲罰`. Future Gemini-fallback queue.
4. ~~`ingest_new_books.py` auto-split-on-ingest~~ — ✅ done 2026-05-14. `standardize_ebook.py` now auto-calls `detect_set_volumes` + `split_ebook_set` on any 套書-titled book at end of standardize. Daily bat also drains via two extra steps (4a + 4b) so any stragglers get processed.

### Online metadata enrichment — ✅ shipped 2026-05-06

`scripts/enrich_book_metadata.py` reads `books` rows where
`publisher IS NULL OR publish_year IS NULL` and tries Google Books
(primary for CJK titles) → Open Library. Each candidate must pass
title-match + author-match; subtitle-stripped variants are tried
when the precise query returns nothing. Only **null** fields get
written, and `metadata_locked = true` blocks all writes — see the
`metadata_locked` and `metadata_source` columns added in the same
session.

First-pass results on the 28-book backlog:

| Field | Filled / total `books` rows | Δ from extraction-only baseline |
|---|---|---|
| `publisher` | 109 / 123 (89%) | +8 |
| `publish_year` | 107 / 123 (87%) | +11 |
| `translator` | 58 / 123 | (untouched — 譯者 not online-enrichable) |
| `original_title` / `original_author` / `original_publish_year` | 58 / 123 | (untouched — same reason) |

Remaining 17 no-hits cluster as: article fragments (titled `〈…〉`),
Chinese-Buddhist works thinly indexed online, and translated Western
books whose Chinese edition is absent from Google Books while only
the English original is present (correctly rejected — wrong publisher
data would be worse than null). These need manual fill via the
`/excerpts/library/[bookId]` UI.

Re-run is safe:
```bash
python scripts/enrich_book_metadata.py status
python scripts/enrich_book_metadata.py run                  # only nulls + unlocked
python scripts/enrich_book_metadata.py run --book <uuid>    # single row
python scripts/enrich_book_metadata.py probe --book <uuid>  # dump raw API responses
```

Lock a manually-edited row so this script won't ever touch its
nulls again:
```sql
UPDATE books SET metadata_locked = true WHERE id = '...';
```

Optional improvement: set `GOOGLE_BOOKS_API_KEY` in `.env` for higher
quota (anonymous tier is fine for dozens of rows; useful only if
re-running over hundreds).

### 套書 splitting — ✅ Phase 1 done 2026-05-14, 16 still pending

The library originally had **35 ebook rows whose title matches a 套書 /
全集 / 套裝 pattern**. The user explicitly asked to split these into one
ebook row per volume so the reader sidebar / bookshelf treats each
volume as a standalone book.

**Phase 1 (volume-metadata-driven split) — DONE.** Ran `split_ebook_set.py
run --all` over the 19 books whose chunks already carried a `volume` field
(came from the hierarchical-TOC standardize path). Produced **132 child
ebooks** after dedup. Each child has:
- `parse_error = 'split from set; do not re-standardize'` (marker so future
  standardize re-runs don't regenerate the full bundle into one volume's slot)
- All `##` heading levels (`flatten_heading_to_h2` rewrites the first
  heading line of each chunk so the reader sidebar renders flat siblings —
  publisher's `###`/`####` 「組-內小篇」 distinction loses meaning once the
  volume stands alone)
- Inherited `author / category / subcategory / file_path` from parent

Dedup handled: 康德著作集 had 2 duplicate parents (`漢譯名著叢書` and a
bare-titled variant) — kept the 漢譯名著 children, deleted the other 10
children + the redundant source EPUB on Drive per user choice. Other
cross-set duplicate titles (理想國 from 商務印書館 vs 柏拉圖套裝, 偶像的
黃昏 from 周國平 vs 商務印書館) are **legitimate different editions**
and were not auto-deduplicated.

**Phase 2 — 16 books still pending, need volume detection.** These have
chunks with `volume=None` throughout (flat-TOC EPUB, OR PDF without volume
metadata). `split_ebook_set.py status` lists them:

- 伊斯蘭文化小叢書（11本套裝） — EPUB
- 神學大全（第1冊 / 第2冊 / 第3冊）— PDF (each `冊` is already a separate
  ebook row — they share the name pattern but DON'T need further splitting)
- 施米特文集 — EPUB
- 印順法師佛學著作全集(上)(下) — PDF
- 世界歷史文庫 希臘史 / 法國史 中 / 非洲史 — PDFs (translated 世界歷史
  文庫 series, individual volumes already, not actually 套書)
- 中東史（上、中、下 套裝共3冊） — PDF
- 二十世紀西方哲學經典（套裝共10冊） — EPUB
- 歷史理性批判文集 — EPUB
- 卡謬全集（6卷） — EPUB
- 陀思妥耶夫斯基全集 — EPUB
- 世界佛教通史（14卷） — EPUB

Approach for Phase 2 (deferred — needs implementation):
1. **Font-size analysis** for EPUB — detect `<h1>`/big-font headings inside
   the rendered HTML to find volume boundaries (analogous to PDF Plan B v1)
2. **LLM-detect** — feed the chunk-content table-of-contents page through
   Haiku/Sonnet, ask it to identify volume boundary chunk_indices
3. Then call `split_ebook_set.py` with synthesized `volume` field per chunk

**Tooling — `scripts/split_ebook_set.py` (shipped 2026-05-14, commit
`2a883ed`/`8e8c4c1`):**
- `python scripts/split_ebook_set.py status` — list current state
- `python scripts/split_ebook_set.py run --book <id> --dry-run` — preview
- `python scripts/split_ebook_set.py run --book <id>` — split one
- `python scripts/split_ebook_set.py run --all` — batch all currently
  splittable (skips books with annotations + already-split children)

**Annotation guard — re-check before re-running.** As of 2026-05-14 only
3 ebooks have annotations (文明的歷史 / A state of mixture / 道教簡史),
none of which are 套書 candidates. If new annotations appear on a 套書
parent later, the script's annotations_for() check will refuse to split
it without `--force`.

**For new 套書 ingested via z-lib drop:** the feedback memory
`feedback_set_books_split.md` says to split immediately after ingest.
Currently `ingest_new_books.py` doesn't auto-trigger split — that's a
future enhancement. For now, after a 套書 lands in `ebooks` and is
parsed + standardized, manually run `split_ebook_set.py run --book <id>`.

## See also

- [`standardize-ebook` SKILL](../standardize-ebook/SKILL.md) — detail-level skill for the markdown standardize pipeline
- [`EBOOK_PIPELINE.md`](../../../EBOOK_PIPELINE.md) at repo root — original design doc
- [`scripts/haiku_cleanup_guide.md`](../../../scripts/haiku_cleanup_guide.md) — Haiku-based text cleanup (separate from standardize; used pre-standardize, mostly historical now)
