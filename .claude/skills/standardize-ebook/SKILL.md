---
name: standardize-ebook
description: Turn a parsed book (EPUB or PDF) into the "reader-ready" format used by /ebook/[id] — markdown chunks with simplified→traditional Chinese, publisher boilerplate stripped, multi-volume hierarchy, smart chapter titles. Branches by file_type — EPUB uses ebooklib + TOC anchors; PDF uses font-size heuristics. Use when wiring a new book into the reader, fixing a book whose TOC looks ugly, batch-processing a category, or extending the pipeline to support a new file type.
---

# Standardize Ebook Skill

Turn a parsed book into the reader-ready format. The pipeline **branches on file_type** because EPUB and PDF expose totally different signals — EPUB has semantic HTML + a TOC tree; PDF only has text-on-page coordinates and font sizes. Each branch produces the same output JSONL contract.

## Branch decision (read this first)

| `ebooks.file_type` | Source signals | Standardize script | Status |
|---|---|---|---|
| `epub` | `<h1-h4>`, `<b>/<em>`, `<p>`, TOC tree with anchors | [`scripts/standardize_ebook.py`](../../../scripts/standardize_ebook.py) | ✅ implemented |
| `pdf` (text-extractable) | text + font size + bbox via PyMuPDF | `scripts/standardize_pdf.py` | ⚠ **NOT YET BUILT** — design below |
| `pdf` (scanned) | image pages → Gemini Vision OCR JSON | [`scripts/ocr_with_gemini.py`](../../../scripts/ocr_with_gemini.py) emits chunks; then run the PDF pipeline on those | ✅ OCR scheduled, PDF pipeline pending |

Both branches write the **same JSONL shape** to `G:/我的雲端硬碟/資料/電子書/_chunks/{ebook_id}.jsonl` so the reader doesn't care which path produced it.

---

## Shared rules — title / boilerplate / merging (both pipelines reuse)

These rules run AFTER the file-specific extraction (HTML walk for EPUB, font heuristics for PDF) and BEFORE persistence. The PDF pipeline must reuse them — they're already implemented in `standardize_ebook.py` and should be factored into a shared module when `standardize_pdf.py` lands.

### Chapter title derivation

Pulled out of `derive_chapter_title()` and `normalize_chapter_title()` in `standardize_ebook.py`. The TOC sidebar's `chapter_path` should always end up looking like one of:

| Cosmetic rename | Triggers |
|---|---|
| `版權頁` | content starts with `圖書在版編目` / `图书在版编目`, OR title is literally `CIP數據` / `版權信息` / `版权信息` / `版權頁` / `版权页` |
| `目錄` (or `目　錄`, original spacing kept) | when chunk content's first short line is "目錄" — picked up automatically by first-line fallback |
| `後記`, `序言`, `致謝`, `導論`, `索引`, etc. | first short line as-is, no special handling needed |

Selection priority for chapter title (first match wins):

1. **Markdown heading** — `## title` / `### title` … in content (after publisher rename normalization)
2. **CIP detected anywhere in first 3 lines** → `版權頁`
3. **Earliest short non-banner line** (≤30 chars, doesn't match `叢書|丛书|名著|系列|文集|文庫|出版社`) — natural document order, so 「目錄」 beats a later「第一章」inside a TOC chunk
4. **Long chapter heading anywhere** — lines matching `^第N(章|卷|編|册|冊|部|集|篇|節|节|回|课|課)` accepted even if longer than 30 chars (君主論's chapter titles can be 30+ chars)
5. First candidate ≤60 chars as last resort
6. Filename fallback (e.g. `text/part0001.html`) — should never reach here for well-formed books

### Drop & dedupe (publisher noise)

- **Hard drop** (chunk is publisher-only ad with no value): currently
  matches 上海譯文出版社 Digital Lab pages. Pattern set is in
  `HARD_DROP_PATTERNS`. Add new publishers as they show up — keep patterns
  *narrow* to avoid eating real content.
- **Dedupe** (keep first occurrence, drop rest): for sections that publishers
  repeat per sub-volume:
  - `^版权信息` / `^版權信息`
  - `圖書在版編目` / `图书在版编目` (CIP data — multi-volume sets repeat this per volume)
- **Empty-doc handling**: if a doc has < 5 chars of plain text:
  - First cover-image-only page (`titlepage.xhtml` or filename contains `cover`) → emit a `## 封面` placeholder once
  - Later empty pages → drop silently

### Continuation merge — 後記/索引 split fix

EPUBs (and OCR'd PDFs) sometimes split one logical section across multiple
files whose TOC titles are just `一 / 二 / 三` (續篇) or `A / B / C` (索引
字母分頁). Merge those into the previous chunk:

```
Before:  [後記] + [二] + [索引] + [A] + [B] + … + [Z]   ← 27 chunks
After:   [後記] + [索引]                                 ← 2 chunks, content concatenated
```

Detection regex (in `is_continuation_title()`):
- Single Chinese numeral: `[一二三四五六七八九十百千]+`
- Single Latin letter: `[A-Za-z]`
- 1-3 digits: `\d{1,3}`
- Empty after stripping

Merge condition: same `volume` as the previous chunk (don't merge across
volume boundaries).

### Heading rewrite for cosmetic renames

When `derive_chapter_title()` applied a rename (e.g. CIP→版權頁), also
rewrite the first markdown heading line in the chunk content so the page's
own h2 matches the sidebar label. Without this the user sees `版權頁` in
the TOC but `## 圖書在版編目（CIP）數據` rendered as the page title — the
reader caught this immediately.

### Simplified → traditional + post-fix

Use `to_traditional()` (in `standardize_ebook.py`):
1. `opencc.OpenCC("s2tw").convert()` for the heavy lifting
2. Apply `TRAD_FIXES` table (24 entries — shared with `parse_drive_inventory.py`)
   to fix s2tw over-conversions: 历史→曆史 (should be 歷史), 託爾斯泰→
   should be 托爾斯泰, 慄田 should be 栗田, etc.

When you find a new mis-conversion, **add it to `parse_drive_inventory.py:TRAD_FIXES`** (single source of truth — used by both filename parsing and chunk content) and re-run the affected books.

### Volume markers

Multi-volume books are detected by their EPUB top-level TOC entries
containing one of `卷 / 冊 / 部 / 集 / 篇`. PDF pipeline can build the
equivalent from `page.get_toc()` (PDF bookmarks) when present.

If anchored TOC entries (`href="part.html#K4"`) point to anchors that don't
actually exist in the HTML (broken EPUB, like 中國儒學史), fall back to
treating the doc as a doc-level volume start.

### `ebook_chunks` DB previews

After writing JSONL + R2, refresh `ebook_chunks` rows for this book —
DELETE existing then INSERT first 200 chars of each chunk's content so
full-text search via `/api/ebooks/search?mode=fulltext` finds them.
Adaptive batch size (100 → 50 → 20 → 5 → 1) to handle Supabase IO budget
57014 timeouts on multi-volume books with 800+ chunks.

---

## Output contract — the JSONL shape consumers depend on

Each line is one chunk:

```json
{
  "chunk_index": 0,
  "chunk_type": "chapter",
  "page_number": null,
  "chapter_path": "第一卷　時　間",
  "volume": "文明的歷史：發現者（上冊）",
  "format": "markdown",
  "content": "## 第一卷　時　間\n\n時間是最偉大的改革者。\n\n**——弗朗西斯·培根：《論革新》（1625）**"
}
```

| Field | Required | Notes |
|---|---|---|
| `chunk_index` | yes | 0-based, contiguous |
| `chunk_type` | yes | `"chapter"` for EPUB; `"page"` for PDF |
| `page_number` | optional | Null for EPUB, set for PDF |
| `chapter_path` | yes | First heading text, used for sidebar TOC entry |
| `volume` | optional | Only present in multi-volume books; null = front matter or single-volume |
| `format` | yes | `"markdown"` for standardized output |
| `content` | yes | Markdown — supports `## ###  ####`, `**bold**`, `*em*`, `> blockquote` |

The reader's [`server/utils/ebook-chunks.ts`](../../../server/utils/ebook-chunks.ts) `loadToc()` reads this format and produces the sidebar; the reader page renders markdown via its own limited renderer (h1-h4 / bold / em / blockquote / paragraphs).

## EPUB pipeline (implemented)

What `standardize_ebook.py` does for EPUB input, in order:

1. **Read EPUB** with `ebooklib` — iterate spine docs in reading order.
2. **Parse top-level TOC** (`book.toc`):
   - Strip entries titled `版权信息` / `Digital Lab`
   - **Filter to volume markers only**: keep only entries whose title contains `卷 / 冊 / 部 / 集 / 篇`. Without this filter, single-volume books promote `目錄 / 插頁 / 出版說明` into fake volume groups (this was a real bug found running the 哲學 batch).
   - Remaining entries with `href` (no `#`) → mark as **volume start at this doc**
   - Entries with `href#anchor` → mark as **volume start at this anchor inside doc** (split point)
   - If fewer than 2 volume entries remain after filtering → flat (single-volume) layout
3. For each spine doc:
   - If TOC anchors point inside it, **split body** at those anchor elements into segments
   - Each segment becomes a candidate chunk
4. **HTML → markdown** ([`el_to_md`](../../../scripts/standardize_ebook.py)):
   - `<h1>` → `##`, `<h2>` → `###`, `<h3>/<h4>` → `####`
   - `<b>/<strong>` → `**…**`, `<em>/<i>` → `*…*`
   - `<p>` → paragraph, `<blockquote>` → `> …`, `<hr>` → `---`
   - Images, footnote `<sup>`, decorative `<svg>` are stripped
5. **Drop / dedupe**:
   - **Hard drop** if plain text matches `HARD_DROP_PATTERNS` (currently tuned for 上海譯文 Digital Lab)
   - **Dedupe** first-occurrence patterns (`版权信息` / `版權信息`) — keep one, drop later copies
   - **Empty docs** that are cover-image-only become a single 「封面」 placeholder chunk
6. **Convert** simplified Chinese → traditional via `opencc s2tw` (also normalizes 卷/編 names if needed).
7. **Pick `chapter_path`** from the first markdown heading; fall back to filename.
8. **Persist**:
   - Write JSONL to `G:/我的雲端硬碟/資料/電子書/_chunks/{ebook_id}.jsonl`
   - Gzip + PUT to R2 `ebook-chunks/{ebook_id}.jsonl.gz`
   - Refresh `ebook_chunks` in DB with 200-char previews (replace, don't append) so full-text search picks them up
   - Update `ebooks` row: `chunk_count`, `total_chars`, `total_pages`, `parsed_at`

## How to run

### Single book
```bash
python scripts/standardize_ebook.py <ebook_id>
python scripts/standardize_ebook.py <ebook_id> --dry-run     # preview chunks only
python scripts/standardize_ebook.py <ebook_id> --no-r2       # skip R2 push (dev)
```

### Batch by category
```bash
python scripts/standardize_ebook.py --category 哲學
python scripts/standardize_ebook.py --category 哲學 --subcategory 近代哲學
python scripts/standardize_ebook.py --category 哲學 --limit 5 --dry-run
```

Auto-skips PDFs (the script can't parse them — they need a different path, see "Limitations").

### Verify a result
```bash
python -c "
import json
from pathlib import Path
p = Path('G:/我的雲端硬碟/資料/電子書/_chunks/<ebook_id>.jsonl')
lines = p.read_text(encoding='utf-8').splitlines()
print(f'chunks: {len(lines)}')
for i in [0, 1, 2, len(lines)//2, len(lines)-1]:
    c = json.loads(lines[i])
    print(f'[{i}] vol={c.get(\"volume\")}  title={c[\"chapter_path\"][:40]}')
    print(c['content'][:200])
    print()
"
```

Or open `/ebook/<ebook_id>` in the running dev server (restart first to clear LRU cache) and check:
- TOC sidebar groups by volume if the book is multi-volume
- Headings render bold + sized (h2 centered with rule, h3 left-aligned)
- Chinese is traditional throughout
- No `Digital Lab` ad pages

---

## PDF pipeline (TO BE BUILT — design)

PDFs lack the semantic markup EPUBs give us, so we infer structure from
typography. This is **less reliable than EPUB** but tractable for well-typeset
print books. Scanned PDFs go through OCR first (which produces text without
typography signals — see "OCR fallback" below).

### Suggested script: `scripts/standardize_pdf.py`

Uses [PyMuPDF (`fitz`)](https://pymupdf.readthedocs.io/) which is already a
dependency of `parse_worker.py`.

### Pipeline order

1. **Open PDF**, iterate pages.
2. **Per-page font analysis** — for each page collect text spans with
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
   per `font_size` bucket. The most common size is the **body text size**.
4. **Classify spans by size relative to body**:
   - `≥ body_size + 6pt` and short (≤ 30 chars) → **h2** (chapter title)
   - `≥ body_size + 3pt` and short → **h3** (section title)
   - `≥ body_size + 1pt` → **h4** (subsection)
   - `flags & 16` (bold) AND short → **h3** (some publishers signal headings only by bold, not size)
   - Else → body paragraph
5. **Build markdown content** by emitting each classified span:
   - Heading spans → `## title` / `### title` / `#### title`
   - Body spans → join with newlines; merge same-paragraph spans (same y-bbox proximity, no heading between)
   - Bold/italic body → `**text**` / `*text*`
6. **Chunking strategy**:
   - **Per-chapter (preferred)**: start a new chunk at every `h2`. Keeps
     chunks meaningfully sized; matches EPUB chunk granularity.
   - **Fallback per-page**: if no headings detected anywhere (very plain PDF),
     fall back to one chunk per page (`chunk_type="page"`). Already what
     `parse_worker.py` does today, so re-running this script just upgrades
     the metadata.
7. **Reuse the EPUB pipeline's downstream pieces**:
   - `to_traditional()` for s2tw + TRAD_FIXES (already in `standardize_ebook.py`)
   - `derive_chapter_title()` for CIP→版權頁 / banner skip / long heading recognition
   - Continuation-merge for 後記/二, 索引 A-Z
   - `volume` detection — PDFs rarely have a programmatic volume marker, so
     usually flat. Could later add a TOC-bookmark reader (`page.get_toc()`)
     for paginated multi-volume sets like 《文明的歷史(全五卷)》.
   - Same `write_jsonl` / `push_to_r2` / `update_db` from `standardize_ebook.py`
     — refactor those into a shared module if the PDF script grows.

### Calibration tips when implementing

- **Body size detection is the linchpin.** Test on 5-10 books from different
  publishers first. If a book has heavy use of footnotes (small font), they
  shouldn't drown out the body. Filter by total character count per bucket,
  not just frequency.
- **Bold-only signaling is publisher-specific.** Some books (商務印書館 漢譯名著)
  put chapter titles in bold same-size as body. Only enable bold→heading
  promotion when font-size signal is weak.
- **Drop running headers/footers** — text spans appearing at the same y-bbox
  on most pages (page numbers, book title repeated). Detect by frequency.
- **Page-spanning paragraphs** — a paragraph that ends on page N and continues
  on page N+1 should NOT be split. Track "did the previous page end mid-sentence"
  using `not text.endswith(('。', '!', '?', '」', '）'))`.
- **Footnotes** — usually appear at bottom of page in smaller font. Either
  drop them or move to end of chunk as `> [註] ...`. User preference.

### Known PDFs to use as test cases

- 《尼采到底說了什麼？》by 羅伯特·所羅門 (`53625079-…`) — straightforward 哲學 PDF
- 《從封閉世界到無限宇宙》by 柯瓦雷 — typical philosophy press PDF
- 《當代數學》— may have heavy formula content; PyMuPDF text extraction will be ugly

### Current scope of哲學 PDF backlog

| Subcategory | PDF count |
|---|---|
| 哲學 (overall) | 58 PDFs (vs 51 EPUBs already standardized) |
| Across all categories | 422 text-extractable PDFs + 391 scanned-pending-OCR |

### OCR fallback for scanned PDFs

Already wired: `scripts/ocr_with_gemini.py` (run daily 16:00 by Windows Task
Scheduler) writes JSONL with `chunk_type="page"` and `format="text"`. After OCR
finishes:
- Re-running `standardize_pdf.py` on those JSONLs would mostly be a no-op
  (no font signals to work with) — it'd just apply s2tw + TRAD_FIXES + 
  `derive_chapter_title()` to upgrade them
- Each OCRed page might already include heading detection via the Gemini
  prompt — could enhance the prompt to mark heading-line vs body-line if
  needed (lower priority — current state is "readable but flat")

### When NOT to bother

- One-off book that already reads OK in the current per-page format
- PDFs with heavy formula / table layout (PyMuPDF mangles those — Gemini
  Vision is more robust but expensive)

---

## Current state (snapshot 2026-05-06)

All 481 standardized EPUBs have been re-run with the post-processing
pipeline below. The 5 books that fail consistently have invalid Windows
file paths (Errno 22) — pre-existing data issue, not a script bug.

| Category | EPUBs | Status |
|---|---|---|
| 哲學 / 宗教學 / 世界宗教 / 心理學 / 人類生物學 / 自然科學 / 文學 / 社會政治學 / 歷史學 | 481 total | ✅ all standardized; 2-3 transient persist errors per batch are auto-handled |

Reference books to spot-check (after each re-run):
- 《君主論》 — single-vol; **NO** volume groups in sidebar
- 《中國儒學史》 — 10-vol; groups by 「先秦卷／漢代卷／…」
- 《希臘羅馬神話》 (Hamilton) — fake-flat 第一部 promoted via `promote_implicit_volumes`; cover has full subtitle/原書名/作者中英
- 《A State of Mixture》 (Payne) — chapters separated correctly (no longer eaten by 「Introduction」 super-chunk); 「In honor of beloved Virgil—」 / 「Publisher.xhtml」 / title-page repeats / epigraph / series banner all consolidated into 「出版資訊」

## Post-processing pipeline (runs after the EPUB walk, before persist)

Order matters — see end of `standardize()`:

1. **`promote_implicit_volumes`** — when an EPUB TOC has an unnamed top-level group (e.g. publisher omitted 「第一部」 but properly named 「第二部」+) the chapters end up flat. Scan vol=None chunks for `第N部/卷` dividers in their `chapter_path` and synthesize the missing volume.
2. **`apply_cover_enrichment`** — replace the placeholder `## 封面 (書本封面)` chunk with structured markdown built from DB title/author + 版權頁 extraction (subtitle / original_title / author_en). Or insert one at index 0 if no cover chunk exists.
3. **`consolidate_frontmatter_into_publisher`** — when a CONTENTS-style chunk (目錄 / Contents) exists in the first ~12 entries AND no volume starts between cover and CONTENTS, fold all chunks `[1..contents-1]` into one synthesized 「出版資訊」 chunk. Substantive named entries (序 / 致謝 / 譯者序 / 推薦序 / Note on / Acknowledgments) stay separate because they appear AFTER CONTENTS.
4. **`derive_chapter_title` smart fallback** — already runs per-chunk during the main walk. Skips numeric/single-letter headings (academic EPUBs use `<h2>1</h2><h1>Real Title</h1>`); when only numeric headings exist AND a short content line follows (`<h2>01</h2><p>王權的誕生</p>`), combines into `「01 王權的誕生」`.
5. **Continuation-merge size cap** — `is_continuation_title` matches still merge tiny `「二」 / 「A」` chunks into the previous chunk, but ONLY if the chunk's plain text is ≤ 800 chars (prevents a 130KB chapter file titled just `「1」` from being eaten).

## Rich publisher metadata extraction (`_extract_publisher_metadata`)

Scans every chunk's content for 版權頁-style key-value lines and writes
the result to ebooks columns during `update_db()`:

| Field | Regex source | ebooks column |
|---|---|---|
| `full_title` (used for subtitle split) | `書名: …` / `Title: …` | `subtitle` (only the post-`：` part) |
| `original_title` | `原文書名: …` / `原書名: …` / `Original Title: …` | `original_title` |
| `author_en` | `作者: 中文（English）` parens capture | `author_en` |
| `translator` | `譯者: …` (stops at `│ | ， ; / 、`) | `translator` |
| `publisher` | `出版: …` / `出版社: …` / `Published by: …` (rejects `出版日期` / `出版年` / `出版地`) | `publisher` |
| `publish_year` | `初版: …YYYY` / `初版首刷: YYYY` / `電子書: …YYYY` | `publication_year` |
| `original_publish_year` + `original_author` | `Copyright © YYYY by AUTHOR` | both |

Field-stop char class `_FIELD_STOP = "\n│|，,；;／/（(、"` keeps regexes
from greedy-eating siblings on packed lines like
`作者：X│譯者：Y│出版者：Z│出版日期：YYYY年`.

### Auto-copy to `books` on excerpt creation

`server/api/annotations/index.post.ts` (POST handler with
`save_as_excerpt: true`) reads the rich columns from `ebooks` and copies
them into the auto-created `books` row, so books that get created by the
reader's 「+ 書摘」 button come out matching the richness of manually-
entered ones — translator / publisher / publish_year / original_title /
original_author / original_publish_year all populated when extractable.

When you tweak the extraction regexes here, **re-run `--all`** so existing
ebooks pick up the new fields, then any future excerpt save will produce
a rich `books` row.

## Idempotency

Re-running on the same book is safe — it overwrites:
- Local JSONL (write replaces)
- R2 object (PUT replaces)
- `ebook_chunks` rows (DELETE-then-INSERT)
- `ebooks` row's `chunk_count` / `total_chars` / `parsed_at`

Annotations (`annotations` table) reference `chunk_index` which generally stays stable for the same book — but if you tweak `HARD_DROP_PATTERNS` and re-run, indices shift and existing annotations may land on wrong text. Avoid re-running once users have annotations.

## Volume detection — known limits

The `looks_like_volume()` heuristic is conservative: a TOC entry must contain one of `卷 / 冊 / 部 / 集 / 篇` to be considered a volume. This works for:
- ✅ 文明的歷史：發現者（上冊） — has 「冊」
- ✅ 中國儒學史：先秦卷 — has 「卷」
- ✅ 五燈會元第N部 — has 「部」

It will **miss** books that group by other markers like:
- ❌ Series titled 「上」「中」「下」 alone (since 「上」 alone is too common in Chinese to safely match)
- ❌ Latin numerals like 「Volume I / II」 in mixed-language editions
- ❌ Publishers using 「輯」 or other terms not in the marker set

If a multi-volume book gets flattened by mistake, **add the missing marker to `VOLUME_MARKERS`** and re-run. Don't try to detect "this looks like a multi-volume set" structurally — the marker check is the only reliable signal in the EPUB TOC.

### Anchor fallback (broken EPUB anchors)

Some EPUBs put `#anchor` fragments in their TOC hrefs but the HTML body never actually emits a matching `id="..."` — `中國儒學史` does this. The script handles it:

1. After `parse_volume_toc()`, every `(file, anchor, title)` entry is validated by reading the doc's HTML and `find(attrs={"id": anchor})`.
2. If at least one anchor in a doc lands → keep the split-at-anchor behavior.
3. If **no** anchors in a doc resolve → promote the first declared title to a doc-level volume start. The volume transition still fires, just at doc beginning instead of mid-doc.

Logged as `(N anchored volume(s) had no resolvable id — promoted to doc-level starts)` per book during a batch.

## Tuning per publisher

The default boilerplate patterns target 上海譯文出版社. Adjust [`HARD_DROP_PATTERNS` and `DEDUPE_PATTERNS`](../../../scripts/standardize_ebook.py) when you find a publisher whose noise pages slip through:

```python
HARD_DROP_PATTERNS = [
    r"Digital\s*Lab是上海译文出版社",         # 上海譯文
    r"我们致力于将优质的资源送到读者手中",
    r"上海译文出版社\|Digital\s*Lab",
    # ADD HERE: e.g. r"^本书由.+出版社制作"
]
```

**Heuristic for what to add**:
- Patterns must be *narrow enough* not to match real content (a copyright page is content the user wants kept; a publisher self-promo page is not)
- Test on 1 book with `--dry-run` before running batch

## Limitations

- **PDFs not supported.** The script raises `SystemExit` for non-EPUB input. PDFs lack reliable HTML structure for headings; the OCR pipeline produces flat per-page text. A future PDF standardizer would need to LLM-detect headings — separate skill.
- **Boilerplate detection is publisher-specific.** Books from publishers not in `HARD_DROP_PATTERNS` will keep their copyright/dedication/ad pages as visible chunks. Cosmetic, not breaking.
- **TOC anchor accuracy varies.** EPUBs that link `volume2 → file#anchor` mid-document get split at the anchor. If the publisher placed the anchor at the wrong paragraph (e.g. 文明的歷史's K4 anchor is mid-上冊 but tagged as 下冊 start), the split is also wrong. Manual fix would need per-book overrides.
- **No semantic dedupe.** Two chunks with very similar but not identical 版權頁 content both get kept. The current dedupe is regex-based prefix matching only.
- **EPUB images dropped entirely.** Cover page becomes the placeholder text 「封面」. Inline figures (chart_img etc.) are stripped — content-only.

## Recovery / re-runs

If a batch run partially fails (e.g. Supabase IO budget hits 57014), the same command re-run picks up where it left off — but only because each book is overwriting independently. There's no checkpoint file. The persisted state in DB / R2 / local is your progress marker.

To find books that were standardized vs not, after a batch:
```sql
-- Approximation: standardized books have format='markdown' in their JSONL.
-- Easiest signal: their first chunk's content starts with '## '.
```
Or `ls G:/.../電子書/_chunks/*.jsonl` mtime — recent files were just standardized.

## When to NOT use this skill

- The book is a PDF (use OCR pipeline instead)
- The book has annotations from users (re-running can shift `chunk_index`, breaking saved highlights)
- The book is single-language English with a normal structure (s2tw conversion would be a no-op, but boilerplate patterns mostly target Chinese — script still works, just less cleaning)
- You want to re-parse without re-uploading to R2 (use `--no-r2`)

## Recommended order for "I'm a new agent picking this up"

1. Read this file end-to-end first.
2. Read the [`ebook-pipeline` SKILL](../ebook-pipeline/SKILL.md) for context on where this fits in the broader system.
3. Look at the **Current state** table above to see which categories are done vs not.
4. Re-run the 哲學 batch first to apply the recent volume-marker fix:
   ```bash
   python scripts/standardize_ebook.py --category 哲學
   ```
5. Pick another category and dry-run to estimate scope:
   ```bash
   python scripts/standardize_ebook.py --category <名> --dry-run
   ```
6. Look at 3-5 sample chunks before committing to a full batch — different categories have different publisher mixes.
7. After running, sample chunks visually (snippet in **How to run / Verify**). If you see boilerplate that should be dropped, extend `HARD_DROP_PATTERNS` and re-run — idempotent.
8. **Don't** re-run `standardize_ebook.py` on books whose IDs have entries in the `annotations` table (re-running can shift `chunk_index`). Check first:
   ```bash
   python -c "import requests, ... ; print(requests.get(URL+'/rest/v1/annotations?select=ebook_id', headers=H).json())"
   ```

## Related

- [`ebook-pipeline` SKILL](../ebook-pipeline/SKILL.md) — the master/orchestration skill that this slots into
- [`scripts/parse_worker.py`](../../../scripts/parse_worker.py) — the **first-pass** parser. Produces unstructured per-doc chunks. `standardize_ebook.py` is the **second pass** that converts these into reader-ready format.
- [`scripts/repopulate_chunk_previews.py`](../../../scripts/repopulate_chunk_previews.py) — back-fills `ebook_chunks` previews from local JSONL for books that were never standardized but need full-text search coverage.
- [`scripts/ocr_with_gemini.py`](../../../scripts/ocr_with_gemini.py) — for scanned PDFs. Produces JSONL of the same shape but `chunk_type="page"`.
