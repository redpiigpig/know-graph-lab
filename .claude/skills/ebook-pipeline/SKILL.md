---
name: ebook-pipeline
description: Operate the Know-Graph-Lab ebook pipeline end-to-end. Use when working on parsing books from Drive into Supabase, OCR'ing scanned PDFs (daily Gemini scheduler), back-filling DB previews from local JSONL, standardizing books into reader-ready markdown, or wiring the reader to chunks. The hub for everything book-content-related.
---

> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session（"exceeds the dimension limit for many-image requests"）。使用者一說要傳截圖，立刻提醒先確認尺寸；推薦 Win+Shift+S 框選或縮到 ≤ 1920px。

# Ebook Pipeline Skill

End-to-end pipeline that takes books from a local Drive folder all the way to the reader at `/ebook/[id]`. This file is the **operational hub** — what runs, in what order, how to monitor it, and how to recover when it breaks. For the standardize step (EPUB → markdown / PDF → polished + TOC-chunked), see the [`standardize-ebook` SKILL](../standardize-ebook/SKILL.md).

## Current state (snapshot 2026-05-18)

| | 數量 |
|---|---|
| Total ebooks | **1,504** |
| Parsed (`parsed_at NOT NULL`) | **1,367** (91%) |
| **OCR queue** (`parse_error LIKE '%no extractable text%'`) | **113** |
| Permanent OCR fail (need manual) | **0** |
| Split-from-set children | 151 (150 parsed / 1 pending) |
| EPUB standardize → markdown | 505 / 505 ✅ |
| PDF Plan A (lite) | 437 / 437 ✅ |
| PDF Plan B v0 (TOC chapter chunks) | 152 / 437 ✅ |
| PDF Plan B v1 (font-driven, no-TOC subset ~285) | 📐 deferred |

---

## Pipeline scripts (all in `scripts/`)

| Script | Phase | Purpose |
|---|---|---|
| `ingest_new_books.py` | 1 — ingest (**daily**) | Watches `z-lib/`. Parses filename, classifies via Gemini (+ keyword fallback), inserts ebooks row, moves file to `G:/.../電子書/{category}/`. Auto-deletes Drive dupes. See **Workflow D** |
| `parse_worker.py` | 2 — parse | Main parser (PyMuPDF + ebooklib). `init` / `run [--limit N] [--retry-errors]` / `status` |
| `ocr_with_gemini.py` | 3 — OCR | Gemini Vision for scanned PDFs. 4 rotating keys; pushes JSONL to R2 inline; auto-Haiku-fallback on Gemini quota / >1000 pages. `--engine {gemini,haiku}`, `--book <id>` / `--exclude <id>` repeatable. Exits code 2 on daily quota |
| `run_ocr_daily.bat` | orchestrator | Windows daily runner — 5-step: ingest → parse → OCR → detect_set_volumes → split_ebook_set. Logs to `scripts/logs/ocr_YYYY-MM-DD.log` |
| `standardize_ebook.py` | 4 — standardize | EPUB → reader-ready markdown chunks. Auto-triggers 套書 split on title match |
| `standardize_pdf_lite.py` | 4 — standardize | PDF Plan A polish (s2tw + spacing collapse + publisher metadata). `page_number` preserved |
| `standardize_pdf.py` | 4 — standardize | PDF Plan B v0 TOC-driven re-chunking. Skips books with annotations / already-chunked / page-level TOC |
| `enrich_book_metadata.py` | 4b — backfill | Online lookup (Google Books → Open Library) for null publisher/year. Respects `metadata_locked` |
| `detect_set_volumes.py` | 4c — 套書 prep | Haiku detects volume boundaries in chunks → writes `volume` field or `NOT_A_SET_MARKER`. `status` / `run --book <id>` / `run --all` |
| `split_ebook_set.py` | 4d — 套書 split | Split multi-volume ebook into one row per volume. Idempotent (skip on SPLIT_MARKER / annotations). Children get `parse_error='split from set; do not re-standardize'` |
| `split_oversized_pdf_by_toc.py` | 3b — OCR rescue | Physically split a multi-volume PDF into per-volume PDFs using level-1 TOC bookmarks. For 套書 that fails BOTH Gemini (>1000 pages) AND Haiku (content-filter). Children re-enter OCR queue |
| `resplit_giant_chunks.py` | 4e — chunk refinement | Break oversized chunks (>400K chars) by internal `##`/`###` headings. Annotation guard |
| `repopulate_chunk_previews.py` | 5 — DB | Back-fill `ebook_chunks` previews from local JSONL. `run` / `retry-failed` / `status` |
| `upload_chunks_to_r2.py` | 5 — R2 | One-shot bulk uploader for JSONL not yet on R2 |

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
  cleaned_at,                    -- nullable; set by Haiku cleaner
  subtitle, original_title, author_en, translator,
  publisher, publication_year, original_publish_year, original_author,
  metadata_locked                -- blocks enrich_book_metadata writes
)

ebook_chunks (
  id uuid PK, ebook_id FK,
  chunk_index INT, chunk_type,   -- 'page' for PDF Plan A, 'chapter' for EPUB / PDF Plan B
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
  - One JSON per line: `{chunk_index, chunk_type, page_number, page_range?, chapter_path, volume?, format?, content}`
  - Auto-syncs to Google Drive cloud as backup
  - Configured via `EBOOK_CHUNKS_DIR` in `.env` (consumed by `nuxt.config.ts` → `runtimeConfig.ebookChunksDir`)
- **R2 mirror**: `r2://{R2_BUCKET}/ebook-chunks/{ebook_id}.jsonl.gz` (gzipped)
  - Read at runtime by `server/utils/ebook-chunks.ts` `loadLines()` when local file is unreachable (production, Zeabur, etc.)
- **DB previews**: `ebook_chunks.content` first 200 chars only — for fast SQL `ilike` full-text search

## Critical constraints

- **Supabase free tier 500 MB limit** — never reload full chunk text into DB. Always JSONL-on-disk + 200-char preview to DB.
- **Supabase IO budget on free tier** — bulk inserts (>1K/s) hit `57014` "canceling statement". `parse_worker.py`, `repopulate_chunk_previews.py`, `standardize_ebook.py`, `split_ebook_set.py` all use **adaptive batch sizes** (100 → 50 → 20 → 5 → 1) to ride out spikes.
- **No Supabase Storage bucket** — user explicitly forbade it. Local files only (G: drive auto-syncs to Drive).
- **Service-role key in `.env`** — never hardcode.
- **PostgREST 1000-row default cap** — server endpoints that list ebooks use `.range(0, 1999)`. Any new bulk read must do the same.

---

## Workflow A — OCR scanned PDFs

[`scripts/ocr_with_gemini.py`](../../../scripts/ocr_with_gemini.py) sends each scanned PDF to Gemini Vision via the Files API and gets back structured JSON `{pages: [{page, text}]}`. After OCR:

1. Write JSONL to local `_chunks/`
2. **Push gzipped JSONL to R2** (inline — `push_to_r2()`)
3. Insert 200-char preview rows into `ebook_chunks`
4. Mark `ebooks.parsed_at` + clear `parse_error`

**Rate limits**: Gemini 2.5 Flash free tier — 10 RPM, 250 RPD, 250K TPM. Default `--rpm 8` leaves headroom. Daily quota resets at midnight Pacific (≈ Taipei 16:00).

### Engine policy

**Default: Gemini.** 4 rotating Google API keys. 503 = transient (does NOT overwrite `parse_error`; next run retries); 429 = daily quota exhausted (script exits code 2).

**Haiku Vision: ONLY when user explicitly orders it.** Always one book at a time — bulk Haiku exhausted Max subscription with zero books completed (2026-05-07). Use:

```bash
python scripts/ocr_with_gemini.py run --engine haiku --book <id>
```

Auth via `ANTHROPIC_API_KEY` or `~/.claude/.credentials.json` OAuth token. **2-strike quota auto-pause** built in — after 2 consecutive 429/rate_limit/quota errors, loop breaks (user rule, not heuristic — see [feedback_ocr_two_strike_quota.md](../../../memory/feedback_ocr_two_strike_quota.md)).

**Automatic fallback (Gemini → Haiku) wired** for:
- Gemini hits 429 mid-run → remaining books switch to Haiku for the rest of the run
- Gemini rejects with `>1000 pages` → that single book auto-falls-back to Haiku inline (Haiku image-batch API has no 1000-page cap)
- File > 50 MB → routes to Haiku directly

### Scheduler

Bat is a **5-step runner**: `ingest_new_books → parse_worker → ocr_with_gemini → detect_set_volumes → split_ebook_set`. Steps 4a/4b are idempotent (no-op when no 套書 pending).

| Component | Path |
|---|---|
| Bat runner | [`scripts/run_ocr_daily.bat`](../../../scripts/run_ocr_daily.bat) — logs to `scripts/logs/ocr_YYYY-MM-DD.log` |
| Toast helper | [`scripts/notify.ps1`](../../../scripts/notify.ps1) — fires at start + on 429 |
| Windows Task | `KGLab-OCR-Daily` (`Register-ScheduledTask`) |
| Trigger | **Daily 16:00** Taipei time |
| Behavior | `WakeToRun` + `StartWhenAvailable` — wakes from sleep, catches up if missed |
| Cap | 12-hour `ExecutionTimeLimit` |

**Bat hardening done 2026-05-14** — `python` hardcoded to `C:\Users\user\AppData\Local\Python\bin\python.exe` (system PATH resolves to Whisper venv missing ebooklib/fitz); `wmic` swapped for `powershell Get-Date`; CRLF enforced. Each step now logs its own exit code.

```powershell
# Inspect / control
schtasks /query /tn "KGLab-OCR-Daily" /v /fo list
Start-ScheduledTask -TaskName "KGLab-OCR-Daily"   # manual fire
```

### Manual operations

```bash
python scripts/ocr_with_gemini.py status                          # how many books queued
python scripts/ocr_with_gemini.py run --limit 1                   # smoke test 1 book
python scripts/ocr_with_gemini.py run --rpm 8                     # full run
python scripts/ocr_with_gemini.py run --model gemini-2.5-flash-lite --rpm 12  # ~3x quota for faster sweep
python scripts/ocr_with_gemini.py run --engine haiku --book <id>  # one-at-a-time Haiku
```

### When OCR breaks

| `parse_error` | Meaning | Action |
|---|---|---|
| `no extractable text` | In OCR queue | next daily run picks up |
| `OCR ok but R2 push failed:` | OCR done, R2 write failed; book NOT marked parsed | next run re-tries cheaply (JSONL kept) |
| `OCR: …` | Permanent Gemini failure | investigate; possibly reset to `no extractable text` to re-try |
| `Haiku-OCR: …` | Permanent Haiku failure | investigate; often content-filter rejection |
| `file not found: …` | Drive path missing (sync disconnected / moved / renamed) | check `G:\` is mounted; restart Drive client |
| `split from set; do not re-standardize` | Volume split child, skip | leave alone |

### Multi-volume bundle rescue

When 套書 PDF fails BOTH Gemini (oversized) AND Haiku (content-filter rejects breadth-of-content), physically split into per-volume PDFs:

```bash
python scripts/split_oversized_pdf_by_toc.py <parent_ebook_id> --dry-run
python scripts/split_oversized_pdf_by_toc.py <parent_ebook_id>
```

Reads parent's level-1 TOC, writes one PDF per volume to same Drive folder named `<parent>_<volume>.pdf`, strips bundle suffixes like `（4卷本）` / `（套裝共N冊）`, inserts one new `ebooks` row per volume with `parse_error='no extractable text'`, marks parent with `SPLIT_MARKER`.

Reach for this on multi-volume bundles only. Single-volume oversized books usually go through Haiku auto-fallback fine. Requires usable level-1 TOC bookmarks (most publisher scans of multi-volume sets have them).

### Operational gotchas (not yet patched)

- **OAuth token in `~/.claude/.credentials.json` expires every few hours.** Long-running `ocr_with_gemini.py` loads token at startup and keeps it in memory — once expired, every Haiku call returns `401`. Fix: kill + restart so next instance reads refreshed file.
- **Python's DNS resolver caches failures.** After brief network blip, all subsequent socket calls inside same process return `getaddrinfo failed` even after `ping` confirms upstream. Kill + restart fixes.
- **Anthropic rolling rate limit** — after ~6-7 consecutive Haiku books, next requests return Cloudflare 502 / `Connection error` for ~30 min. Effective Haiku throughput ~6 books/hour with cooldown, ~50 books/day max — still worse than Gemini's 250/day. For bulk: Gemini. For ad-hoc tough cases: Haiku `--book <id>`.
- **Vertical-typography Chinese books** (e.g. 民族主義的不正當性, Tagore translation) — both engines struggle. Haiku scrambles column order, Gemini truncates JSON. No good fix; may need manual repair in reader.
- **Content-filter rejections** (e.g. 哥白尼革命, 規訓與懲罰, 走向馬克思主義的人道主義) — Haiku returns `Output blocked by content filtering policy`. Need different engine; currently leave queue marked permanent (run via `--engine gemini --book <id>`).

### Temp-file cleanup policy

Shipped OCR scripts do NOT leave images on disk:
- `ocr_with_gemini.py` — `tempfile.NamedTemporaryFile`, `unlink()` in `finally`. Auto-cleaned.

If `ocr_*.png` / `ocr_*.jpg` / `book_*.pdf` accumulate in `C:\tmp\`, they're leftovers from experimental scripts. Once corresponding books are OCR'd + standardized, delete:

```bash
rm /c/tmp/ocr_*.png /c/tmp/ocr_*.jpg /c/tmp/book_*.pdf 2>/dev/null
```

---

## Workflow D — Daily z-lib drop ingest

User drops freshly-acquired ebooks into [`z-lib/`](../../../z-lib/) at project root (local folder, not on Drive). Filename suffix `(z-library.sk, 1lib.sk, z-lib.sk)` from source is preserved on disk and stripped during parse. [`scripts/ingest_new_books.py`](../../../scripts/ingest_new_books.py) processes once per day as part of `run_ocr_daily.bat`. For each `.pdf` / `.epub` / `.mobi` / `.azw3`:

1. **Parse filename** → `(author, title, ext)`. Reuses `parse_drive_inventory.parse_filename()` after pre-stripping z-library suffixes.
2. **Classify** into one of 9 main categories. Two-tier:
   - **Keyword fallback first** (free): `christ|church|bonhoeffer|...|patristic|apostolic|gospel|biblical|theology` → `宗教學`; `zoroastr|avesta|islam|buddhis` → `世界宗教`.
   - **Gemini 2.5 Flash** otherwise — strict JSON. LLM mistakes like "基督教"/"神學" auto-mapped to 宗教學.
3. **Insert** `ebooks` row with `category`, `parsed_at=NULL`, `file_path` pointing to future Drive location.
4. **Move** local file → `G:/我的雲端硬碟/資料/電子書/{category}/{author}，{title}.{ext}`. G: IS the Drive sync mount, so move = upload + local-delete in one filesystem rename. No OAuth needed.

After ingest, new rows appear with `parsed_at=NULL`. Next `parse_worker.py run` (daily step 2) extracts text. If extraction fails, `ocr_with_gemini.py` picks it up in step 3.

### Manual operations

```bash
python scripts/ingest_new_books.py status              # how many waiting
python scripts/ingest_new_books.py run --dry-run       # preview classification + paths
python scripts/ingest_new_books.py run --limit 3       # smoke test
python scripts/ingest_new_books.py run                 # full sweep
```

### Failure modes

| Mode | Behavior |
|---|---|
| DB insert fails | File kept in `z-lib/`; safe to re-run |
| Move fails after DB insert | File kept, row inserted but not on Drive. Manual move or delete row. Rare |
| Gemini quota / 429 | Skip that book (file kept); others continue with keyword fallback. Tomorrow's run picks it up |
| Filename unparseable | Log `SKIP: could not parse title`; file kept. Add override to `parse_drive_inventory.TITLE_AUTHOR_OVERRIDES` |
| Target exists on Drive (dupe) | **Auto-delete `z-lib/` copy** (since 2026-05-14). Logs both sizes |

### Tuning notes

- Keyword fallback skews Christian-studies (user backlog). Extend `fallback_category()` for other dominant areas.
- Gemini shares daily quota with OCR. Order: ingest first (~1-5 calls/day) so OCR's heavy usage can't starve it. RPM gentle (`time.sleep(0.5)` between books).
- Junk files (`Z-Library-latest.exe` etc.) silently ignored — only `EBOOK_EXTS` touched.

---

## Workflow B — Standardize books → reader-ready format

See the [`standardize-ebook` SKILL](../standardize-ebook/SKILL.md) for full contract (EPUB branch + PDF Plan A + PDF Plan B v0, output format, drop/dedupe rules, idempotency, tuning per publisher).

### Quick commands

```bash
# EPUB single / batch
python scripts/standardize_ebook.py <ebook_id>
python scripts/standardize_ebook.py --category 哲學

# PDF Plan A (lite — s2tw + spacing + metadata)
python scripts/standardize_pdf_lite.py <ebook_id>
python scripts/standardize_pdf_lite.py --all

# PDF Plan B v0 (TOC-driven chapter chunks; run AFTER Plan A)
python scripts/standardize_pdf.py <ebook_id>
python scripts/standardize_pdf.py --all --dry-run            # list eligible
python scripts/standardize_pdf.py --all                      # ~6.5s/book
```

> ⚠ Re-running `standardize_ebook.py` shifts `chunk_index` if drop/dedupe rules change — avoid on books with annotations. PDF Plan A is `chunk_index`/`page_number`-stable. PDF Plan B v0 shifts `chunk_index` (re-chunks pages → chapters), but refuses without `--force` on books with annotations.

---

## Workflow C — Back-fill `ebook_chunks` previews

Needed when full-text search must cover a book whose chunks are only on disk/R2 but not in DB previews. Happens to books parsed before R2 offload, or books that hit `57014` IO timeout during first preview run.

```bash
python scripts/repopulate_chunk_previews.py status
python scripts/repopulate_chunk_previews.py run                       # initial back-fill
python scripts/repopulate_chunk_previews.py retry-failed              # adaptive batch from 100→1
python scripts/repopulate_chunk_previews.py run --book <ebook_id> --force
```

`retry-failed` is the safe re-run mode — finds books whose `ebook_chunks` count is below their expected `ebooks.chunk_count` and only retries those.

---

## Decision tree for "this book looks broken in the reader"

```
Book opens but no content?
  → Check ebook_chunks count for this book. If 0 → run repopulate_chunk_previews.py --book <id>
  → If still missing, check local JSONL exists. If not → re-parse (parse_worker.py or ocr_with_gemini.py)

Reader sidebar shows "目錄/插頁" as fake volumes?
  → standardize_ebook.py was run before volume-marker fix. Re-run for this book.

Reader shows "Digital Lab" or other publisher noise?
  → Add publisher's phrase to HARD_DROP_PATTERNS in standardize_ebook.py, re-run.

Search returns no fulltext hits but title/author work?
  → ebook_chunks doesn't have this book's previews. Run repopulate_chunk_previews.py.

A scanned PDF still shows "此頁無內容" 12+ hours after OCR scheduled?
  → Check scripts/logs/ocr_YYYY-MM-DD.log for errors. If quota hit, tomorrow's run picks up.

Many books in OCR queue showing "file not found"?
  → G: drive (Drive sync) disconnected. Get-PSDrive -PSProvider FileSystem should list G:.
  → Re-launch Google Drive client. parse_errors stay until manually reset to "no extractable text".

A new book dropped into z-lib/ never showed up in the reader?
  → Check scripts/logs/ocr_YYYY-MM-DD.log "--- ingest_new_books ---" section.
  → 'CLASSIFY FAILED' = Gemini quota; tomorrow retries.
  → 'could not parse title' = unsupported filename; rename or extend TITLE_AUTHOR_OVERRIDES.
  → 'target already exists on Drive' = duplicate book.
```

---

## Common pitfalls

- **opencc s2tw over-converts**: `历史 → 曆史` (should be 歷史), surnames like `栗 → 慄`. Post-fix table in [`scripts/parse_drive_inventory.py:TRAD_FIXES`](../../../scripts/parse_drive_inventory.py).
- **Chinese characters in shell output on Windows**: cp950 codec errors. Always use `sys.stdout.reconfigure(encoding='utf-8')` or write to UTF-8 file.
- **`server/utils/ebook-chunks.ts` LRU cache (10 min TTL)** — hot-edits to JSONL aren't visible immediately. Restart dev server after batch standardize / re-parse to clear cache.
- **Filename collisions in same folder**: when multiple files would have the same stripped title, `parse_filename()` keeps the subtitle. Already handled.
- **REST API row limit 1000**: any new bulk read must use `.range()`-based pagination.

## Files NOT to touch unless user requests

- `data/local_inventory.json` — frozen Drive scan snapshot
- `data/parse_progress.txt` — auto-managed by parse_worker
- `G:/我的雲端硬碟/資料/電子書/_chunks/*.jsonl` — source of truth for full text (R2 mirrors these; if lost, must re-parse)

## Recommended order for "I'm a new agent picking this up"

1. Run all status checks:
   ```bash
   python scripts/ingest_new_books.py status
   python scripts/repopulate_chunk_previews.py status
   python scripts/ocr_with_gemini.py status
   ```
2. If `z-lib/` has files waiting → `python scripts/ingest_new_books.py run`.
3. Read [`standardize-ebook` SKILL](../standardize-ebook/SKILL.md) before touching standardize.
4. Don't re-run `standardize_ebook.py` on books with annotations.
5. For categorized batch standardize, `--dry-run` first.
6. Watch daily scheduler at 16:00 — log in `scripts/logs/ocr_YYYY-MM-DD.log` covers ingest + parse + OCR.

## Reader-side features tied to the pipeline

### Bookshelf + reading bookmarks

Per-user reading state. Schema in [`database/bookshelf-and-bookmarks.sql`](../../../database/bookshelf-and-bookmarks.sql). RLS on; service-role endpoints filter by `user_id`.

- `user_reading_status (user_id, ebook_id, status)` — `status ∈ 'reading' | 'read'`. PK enforces one row per user-book.
- `reading_bookmarks (id, user_id, ebook_id, chunk_index, created_at)` — date-stamped 「今日讀到這裡」 markers.

Endpoints: `PUT/GET /api/ebooks/:id/reading-status`, `POST/GET /api/ebooks/:id/bookmarks`, `DELETE /api/bookmarks/:id`, `GET /api/me/bookshelf`.

Reader UX (`pages/ebook/[id].vue`):
- Toolbar status pill cycles 📚 → 📖 → ✅ → 📚
- 「📅 今日讀到這裡」 button only when status is `reading`
- TOC sidebar shows date badges next to chunks with bookmarks
- Auto-jump to latest bookmark on book open if status=`reading` AND no `?page=` in URL

### Excerpts auto-flow (`save_as_excerpt: true`)

Reader's 「+ 書摘」 button creates annotation + auto-creates `books` row (if ebook's `book_id` is null) using rich metadata from `ebooks` columns + inserts `excerpts` row with content + title + chapter + page_number + book_id + links annotation to excerpt.

Result: book appears in `/excerpts/library` with rich metadata, excerpts grouped by chapter on `/excerpts/library/[bookId]`.

### Tags

Cross-cut organization. Schema in [`database/tags.sql`](../../../database/tags.sql). `tags` + `book_tags` + `excerpt_tags`. Endpoints: `GET/POST /api/tags`, `DELETE /api/tags/:id`, `GET/PUT /api/books/:id/tags`, `GET/PUT /api/excerpts/:id/tags`. `tagId` query param on `/api/books` and `/api/ebooks`. Reusable [`components/TagPicker.vue`](../../../components/TagPicker.vue). URL-driven filter `?tag=<id>`.

### Markdown citation export

「📋 匯出 Markdown」 button on `/excerpts/library/[bookId]` toolbar. Builds self-contained markdown (bibliographic header + chapter-grouped `> blockquote` content + `——《book》, chapter, page` citation tails). Clipboard + `<book-title>.md` download. Client-side from already-loaded `book.value` + `chapterGroups`.

---

## Pending TODOs

1. **PDF Plan B v1 (font-driven)** — for the ~285 no-TOC PDFs. Design in `standardize-ebook` SKILL.
2. **37 EPUBs with single chunk >400KB and no internal headings** — `resplit_giant_chunks.py` can't help (no `##`/`###` to split on). Needs LLM page-boundary detection on raw text, or going back to raw EPUB HTML for font cues.
3. **16 套書 with `volume=None`** — Phase 2 work. Need font-size analysis (EPUB) or LLM-detect on TOC chunk content. See SKILL for approach options.
4. **Auto-trigger standardize after daily ingest** — currently standardize only runs manually. Wire into bat as step 6 (idempotent skip for already-standardized books).
5. **17 no-hit books** for `enrich_book_metadata.py` (article fragments, Chinese-Buddhist, translated Western works whose Chinese edition isn't on Google Books). Manual fill via `/excerpts/library/[bookId]` UI.

## See also

- [`standardize-ebook` SKILL](../standardize-ebook/SKILL.md) — detail-level skill for EPUB + PDF standardize
- [`EBOOK_PIPELINE.md`](../../../EBOOK_PIPELINE.md) at repo root — original design doc
- [`scripts/haiku_cleanup_guide.md`](../../../scripts/haiku_cleanup_guide.md) — Haiku text cleanup (mostly historical now)
