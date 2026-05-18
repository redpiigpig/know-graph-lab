---
name: standardize-ebook
description: Standardize parsed books (EPUB + PDF) into the reader-ready format used by /ebook/[id]. EPUB → markdown chunks via TOC anchors. PDF Plan A → s2tw + collapse spacing on per-page JSONL with page_number preserved. PDF Plan B v0 → TOC-bookmark-driven chapter chunks with page_range. Use when wiring a new book into the reader, fixing a book whose TOC looks ugly, batch-processing a category, or processing freshly-OCR'd scanned PDFs.
---

> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session（"exceeds the dimension limit for many-image requests"）。使用者一說要傳截圖，立刻提醒先確認尺寸；推薦 Win+Shift+S 框選或縮到 ≤ 1920px。

# Standardize Ebook Skill

Turns a parsed book into the reader-ready format at `/ebook/[id]`. The pipeline **branches on `ebooks.file_type`** because EPUB and PDF expose totally different signals:

| `file_type` | Source | Script | Granularity |
|---|---|---|---|
| `epub` | `<h1-h4>`, `<b>/<em>`, `<p>`, TOC tree | [`scripts/standardize_ebook.py`](../../../scripts/standardize_ebook.py) | chapter chunks (`chunk_type=chapter`) |
| `pdf` (text or OCR'd) | per-page JSONL from parse_worker / ocr_with_gemini | [`scripts/standardize_pdf_lite.py`](../../../scripts/standardize_pdf_lite.py) (Plan A) → [`scripts/standardize_pdf.py`](../../../scripts/standardize_pdf.py) (Plan B) | Plan A: per-page; Plan B: chapter |

Both branches write the **same JSONL shape** to `G:/我的雲端硬碟/資料/電子書/_chunks/{ebook_id}.jsonl` so the reader stays branch-agnostic.

> **🔑 Hard rule: PDF `page_number` is sacred.** Citations in 書摘 reference the real publisher page number. Any transform that re-numbers `page_number` is a bug. `chunk_index` can be re-numbered; `page_number` cannot.

---

## 流程 — 新書 vs 舊書

### 新書（daily ingest 自動跑）

每日 16:00 `scripts/run_ocr_daily.bat` 跑完整 5-step：

```
ingest_new_books → parse_worker → ocr_with_gemini → detect_set_volumes → split_ebook_set
```

Standardize 不在 daily bat 裡 — parse / OCR 落地後 chunk_type 還是 `page` (PDF) 或 raw (EPUB)。**新書 standardize 需手動觸發**（見「舊書批次」一段的 commands）。已知 TODO：把 standardize 也鉤進 daily bat。

唯一例外是 **套書 auto-split** — `standardize_ebook.py` 在 EPUB 完成後自動呼叫 `detect_set_volumes` + `split_ebook_set`，所以 standardize-ed 套書自動拆成多個 child rows。

### 舊書（一次性 batch）

EPUB 單本：
```bash
python scripts/standardize_ebook.py <ebook_id>
python scripts/standardize_ebook.py <ebook_id> --dry-run
python scripts/standardize_ebook.py <ebook_id> --no-r2
```

EPUB 批次（自動跳過 PDF）：
```bash
python scripts/standardize_ebook.py --category 哲學
python scripts/standardize_ebook.py --category 哲學 --subcategory 近代哲學
python scripts/standardize_ebook.py --category 哲學 --limit 5 --dry-run
```

PDF Plan A（lite — s2tw + spacing collapse + publisher metadata）：
```bash
python scripts/standardize_pdf_lite.py <ebook_id>
python scripts/standardize_pdf_lite.py --category 哲學
python scripts/standardize_pdf_lite.py --all
```

PDF Plan B v0（TOC-driven chapter chunking — Plan A 跑完後才跑 B）：
```bash
python scripts/standardize_pdf.py <ebook_id>
python scripts/standardize_pdf.py --all --dry-run            # 列出 eligible PDF
python scripts/standardize_pdf.py --all                      # ~6.5s/book
python scripts/standardize_pdf.py <ebook_id> --force         # 忽略 annotations 守衛
```

---

## Current state

| Pipeline | 書數 | Status |
|---|---|---|
| EPUB standardize → format=markdown | 505 / 505 | ✅ done — 0 filename leaks / 0 chunks below heading-rate threshold |
| PDF Plan A (lite) | 437 / 437 text-extractable | ✅ done — s2tw + spacing collapse + publisher metadata |
| PDF Plan B v0 (TOC-driven) | 152 / 437 chapter-chunked | ✅ done — 285 skip 主因為 0-entry TOC（待 Plan B v1 font 救援）|
| PDF Plan B v1 (font-driven) | 0 | 📐 deferred design |
| OCR queue（轉錄主隊列） | 113 | 🔄 daily 16:00 Gemini 自動帶；新 standardize 進來才會跑 |

---

## Output contract — 共通 JSONL shape

Each line is one chunk:

```json
{
  "chunk_index": 0,
  "chunk_type": "chapter",
  "page_number": null,
  "chapter_path": "第一卷　時　間",
  "volume": "文明的歷史：發現者（上冊）",
  "format": "markdown",
  "content": "## 第一卷　時　間\n\n時間是最偉大的改革者。"
}
```

| Field | Required | EPUB | PDF Plan A | PDF Plan B v0 |
|---|---|---|---|---|
| `chunk_index` | yes | 0-based contiguous | 0-based contiguous | re-numbered from 0 |
| `chunk_type` | yes | `"chapter"` | `"page"` | `"chapter"` |
| `page_number` | optional | null | **real PDF page (sacred)** | **first real PDF page in chapter (sacred)** |
| `page_range` | new | — | — | `[first, last]` |
| `chapter_path` | yes | TOC anchor title | derived if heading detected else null | TOC ancestor hierarchy `祖 / 父 / 本` |
| `volume` | optional | multi-volume only | — | — |
| `format` | yes | `"markdown"` | `"text"` | `"text"` |
| `content` | yes | markdown (h2-h4, bold, em, blockquote) | s2tw'd + spacing-collapsed | concatenated s2tw'd pages joined by `\n\n` |

Reader's [`server/utils/ebook-chunks.ts`](../../../server/utils/ebook-chunks.ts) `loadToc()` consumes this; reader page renders markdown via its own h1-h4 / bold / em / blockquote / paragraph renderer.

---

## EPUB pipeline (`standardize_ebook.py`)

1. **Read EPUB** via `ebooklib` — iterate spine docs in reading order.
2. **Parse TOC** (`book.toc`):
   - Strip `版权信息` / `Digital Lab` entries
   - Volume filter: keep only entries with `卷 / 冊 / 部 / 集 / 篇` in title (else 「目錄/插頁/出版說明」 get promoted to fake volumes)
   - `href` (no anchor) → volume start at doc; `href#anchor` → volume start at anchor inside doc
   - <2 remaining volume entries → flat (single-volume) layout
3. **Per spine doc**: if TOC anchors point inside, split body at those anchors into segments → each becomes a candidate chunk.
4. **HTML → markdown** via `el_to_md`:
   - `<h1>` → `##`, `<h2>` → `###`, `<h3>/<h4>` → `####`
   - `<b>/<strong>` → `**…**`, `<em>/<i>` → `*…*`
   - `<p>` → para, `<blockquote>` → `> …`, `<hr>` → `---`
   - Images / `<sup>` footnote / decorative `<svg>` stripped
5. **Drop / dedupe** (see Shared rules below).
6. **s2tw + TRAD_FIXES** (see Shared rules).
7. **Pick `chapter_path`** from first markdown heading; fallback filename.
8. **Persist**: write JSONL → gzip+PUT R2 → DELETE+INSERT `ebook_chunks` previews (adaptive batch) → update ebooks row.

### Hierarchical TOC support — `parse_toc_hierarchical`

When `book.toc` exposes top-level Sections with ≥2 children each, switch from flat single-level to 2-level splitter that exposes both 章 AND 節 in the sidebar.

**Role detection.** Top-level Section title shape determines role:
- **multi_volume** — top titles are volume names (羅馬帝國衰亡史「全譯羅馬帝國衰亡史：1」). Split at child (chapter) AND grandchild (節) anchors. `volume=top_title`, `chapter_path=chap_or_section`. Heading levels: chapters `###` (sidebar pl-7), 節 `####` (pl-11).
- **single_chapter** — top titles look like printed chapters (現代世界史「第1章 歐洲的興起」 — matches `_CHAPTER_TITLE_RE`). Split at top (chapter) AND child (節) anchors. `volume=None`. Heading levels: chapters `##` (pl-3), 節 `###` (pl-7).

Decision: `_is_chapter_title()` vs `looks_like_volume()` counts. If ≥50% of tops match chapter pattern AND chapter > volume count → `single_chapter`; else `multi_volume`.

**Payload contract.** Both roles emit 3-tuple anchor payloads `(vol_or_None, chap_title, level_str)` so the standardize loop normalizes heading depth uniformly via `target_level` override.

**Survey:** 283/308 standardized EPUBs (92%) qualify for hierarchical; 25 fall back to legacy `parse_volume_toc`.

### Anchor splitting — deep walk + per-anchor dedup

`split_body_at_anchors` walks **all body descendants** in document order (publishers wrap chapter lists inside `<div>` directly under body — naïve `body.children` loop misses everything but the first anchor). Dedupes anchor matches by their `id` value (same id often emitted on both `<a>` nav target AND `<h2>` heading).

### Heading normalization (hierarchical mode only)

Reader's `loadToc` derives sidebar nesting from each chunk's first heading depth. EPUBs use whatever `<h1>/<h2>/<h3>` the publisher chose, so without this normalization some chapters render as level-2 entries and others as level-3+ children. Standardize loop forces uniform heading level per role + prepends a heading at target level if chunk has none.

### Post-processing pipeline (after EPUB walk, before persist)

Order matters — at end of `standardize()`:

1. **`promote_implicit_volumes`** — TOC has unnamed top-level group (publisher omitted 「第一部」 but named 「第二部」+). Scan vol=None chunks for `第N部/卷` dividers in `chapter_path` and synthesize missing volume.
2. **`apply_cover_enrichment`** — replace placeholder `## 封面 (書本封面)` with structured markdown from DB title/author + 版權頁 extraction (subtitle / original_title / author_en). Insert at index 0 if no cover chunk.
3. **`consolidate_frontmatter_into_publisher`** — CONTENTS-style chunk (目錄 / Contents) in first ~12 entries AND no volume between cover and CONTENTS → fold chunks `[1..contents-1]` into one synthesized 「出版資訊」. Named entries (序 / 致謝 / 譯者序 / 推薦序 / Acknowledgments) AFTER CONTENTS stay separate.
4. **`derive_chapter_title` smart fallback** — skips numeric/single-letter headings (academic EPUBs use `<h2>1</h2><h1>Real Title</h1>`); combines `「01 王權的誕生」` from `<h2>01</h2><p>王權的誕生</p>`.
5. **Continuation-merge size cap** — `is_continuation_title` merges tiny `「二」 / 「A」` into previous chunk, but only if plain text ≤ 800 chars (prevents a 130KB chapter file titled `「1」` being eaten).

### Auto-split for 套書 (since 2026-05-14)

After standardize, if title matches 套書 pattern, auto-calls `detect_set_volumes` (Haiku-driven volume boundary detection) + `split_ebook_set` (children flattened to `##`). Each child gets `parse_error = 'split from set; do not re-standardize'` marker.

---

## PDF Plan A — `standardize_pdf_lite.py`

Polish per-page JSONL from parse_worker / ocr_with_gemini. Per chunk:

1. **s2tw + TRAD_FIXES** (Shared rules).
2. **Collapse CJK spacing** — `路 … 文 本 、 歷 史` → `路文本、歷史` via `collapse_cjk_spacing()`. Squeezes adjacent CJK without touching real spaces in mixed CJK/Latin paragraphs.
3. **Strip page-number-only running header** — only when leading line is short AND starts with a number = chunk's `page_number`. Conservative: `2  Title` on a page whose actual `page_number=7` stays put (Plan B handles those positionally).
4. **Re-derive `chapter_path`** — only when page genuinely starts with chapter heading (`第N章 / Chapter N / 引言 / 序 / 致謝 / 附錄 / Bibliography / Index`). Unclear → leave null.
5. **Preserve `page_number` exactly**.

Book-level:
- **Extract publisher metadata** (Shared rules) + PATCH ebooks row.

Plan A does NOT do: chapter-level chunking, cover synthesis, frontmatter consolidation, volume hierarchy, position-based header strip, bold/italic/heading inference (no font signals in this layer).

---

## PDF Plan B v0 — `standardize_pdf.py` (TOC-driven)

Plan A polishes existing one-page-one-chunk output. Plan B re-chunks those flat pages into chapter-level chunks **driven by the PDF's TOC bookmarks**. Same source-of-truth (existing JSONL) — no PDF text re-extraction.

> **🚧 Why TOC-driven, not font-driven?** 30-PDF probe showed font signal is degenerate on a large fraction of the library — many books are image-based PDFs where PyMuPDF extracts <1% of body text yet PyMuPDF's TOC bookmarks survive. TOC is both more reliable and simpler. Font-driven inference is deferred to Plan B v1 for the no-TOC subset (~285 books).

### What v0 does

1. Load per-page JSONL (already Plan A-polished).
2. Read PDF's TOC (`fitz.Document.get_toc()`) — no body re-extract.
3. Filter TOC to `level <= 2`, drop empties, dedupe same-start-page, sort by start page.
4. For each TOC entry, concat existing JSONL pages from `[entry.start_page, next.start_page - 1]` into one chapter chunk.
5. Pages BEFORE first TOC entry → one `前置內容` chunk (so 版權頁 / 序言 still feed `_extract_publisher_metadata`).
6. Apply `to_traditional()` + `collapse_cjk_spacing()` per chunk.
7. Build hierarchical `chapter_path` from TOC ancestors (`祖 / 父 / 本`).
8. Persist JSONL → R2 → DB previews + ebooks metadata PATCH.

### Skip conditions (book stays on Plan A output)

| Condition | Threshold |
|---|---|
| TOC entries < 3 | `MIN_TOC_ENTRIES` |
| Page-level TOC (~1 entry/page) | `total_pages / len(toc) < 1.2` (`MIN_PAGES_PER_ENTRY`) — caught 中東史 (654/661), 希伯來聖經 (598/598) |
| Existing annotations on ebook | hard refuse without `--force` (re-chunking shifts `chunk_index`) |
| JSONL already chapter-chunked | re-run guard (`chunk_type == 'chapter'` or `page_range` present) — must re-run `standardize_pdf_lite` first to revert |
| PDF file missing on Drive | `file not found:` error |

### Realistic hit rate (full `--all` batch)

152 / 437 chapter-chunked. 285 skip break down:
- ~257 books had **0 TOC entries** (publisher exported PDF without bookmarks — Plan B v1 candidates)
- ~28 books reduced to single TOC chunk (`only N chunks produced` guard) or page-level TOC

---

## Plan B v1 — font-driven inference for no-TOC PDFs (deferred design)

Worth building when the no-TOC subset (~285 books) becomes the bottleneck.

1. **Open PDF**, iterate pages.
2. **Per-page font analysis** — collect spans `(text, font_name, font_size, bbox, flags)`:
   ```python
   doc = fitz.open(path)
   for page in doc:
       for block in page.get_text("dict")["blocks"]:
           for line in block.get("lines", []):
               for span in line["spans"]:
                   ...  # span["text"], span["size"], span["font"], span["flags"]
   ```
3. **Build global font histogram** — char count per `font_size` bucket. Most common size = body text size.
4. **Classify spans relative to body**:
   - `≥ body + 6pt` AND short (≤30 chars) → `h2` (chapter)
   - `≥ body + 3pt` AND short → `h3` (section)
   - `≥ body + 1pt` → `h4` (subsection)
   - `flags & 16` (bold) AND short → `h3` (publishers signaling headings only by bold)
   - Else → body para
5. **Build markdown** — heading spans → `## … / ### … / #### …`; body spans → join + merge same-paragraph spans (same y-bbox proximity, no heading between); bold/italic body → `**…**` / `*…*`.
6. **Chunking**: new chunk at every `h2`. Same per-chunk contract (`page_number` sacred, `page_range` new).

### Calibration tips
- **Body size is the linchpin.** Test on 5-10 books from different publishers first. Filter by total char count per bucket, not frequency (footnotes are small but numerous).
- **Bold-only signaling is publisher-specific.** 商務印書館 漢譯名著 puts chapter titles in bold same-size as body. Enable bold→heading promotion only when font-size signal is weak.
- **Drop running headers/footers** — text spans at the same y-bbox on most pages (page numbers, book title repeated). Detect by frequency across pages.
- **Page-spanning paragraphs** — don't split a para that ends on page N and continues on N+1. Track "did previous page end mid-sentence" via `not text.endswith(('。', '!', '?', '」', '）'))`.
- **Footnotes** — bottom of page in smaller font. Drop or move to end of chunk as `> [註] ...`.

### When NOT to do v1
- Book reads OK after Plan A or Plan B v0
- Heavy formula / table layout (PyMuPDF mangles those — Gemini Vision is more robust but expensive)
- Image-based PDFs (run OCR first; v1's font signal will be empty)

---

## Shared rules (both pipelines)

### Simplified → traditional

```python
to_traditional(text):
    1. opencc.OpenCC("s2tw").convert()
    2. Apply TRAD_FIXES table (24 entries — shared with parse_drive_inventory.py)
```

Fixes s2tw over-conversions: 历史→曆史 (should be 歷史), 託爾斯泰→托爾斯泰, 慄田→栗田, etc. When you find a new mis-conversion, **add to `parse_drive_inventory.py:TRAD_FIXES`** (single source of truth) and re-run.

### Drop & dedupe (publisher noise)

```python
HARD_DROP_PATTERNS = [
    r"Digital\s*Lab是上海译文出版社",
    r"我们致力于将优质的资源送到读者手中",
    r"上海译文出版社\|Digital\s*Lab",
]
DEDUPE_PATTERNS = [
    r"^版权信息", r"^版權信息",
    "圖書在版編目", "图书在版编目",   # CIP — multi-volume sets repeat per volume
]
```

Empty-doc: < 5 chars plain text:
- First cover-image-only page (`titlepage.xhtml` or filename `cover`) → emit `## 封面` placeholder once
- Later empty pages → drop silently

**Tuning heuristic:** patterns must be narrow enough not to match real content. Test on 1 book with `--dry-run` before batch.

### Continuation-merge

EPUBs (and OCR'd PDFs) sometimes split one logical section across multiple files whose TOC titles are just `一 / 二 / 三` (續篇) or `A / B / C` (索引字母分頁). Merge into previous chunk:

```
Before:  [後記] + [二] + [索引] + [A] + [B] + … + [Z]   ← 27 chunks
After:   [後記] + [索引]                                  ← 2 chunks, content concatenated
```

`is_continuation_title()` regex: `[一二三四五六七八九十百千]+` / single `[A-Za-z]` / 1-3 digits / empty. Merge only if **same `volume`** as previous (don't merge across volume boundaries).

### Chapter title derivation

`derive_chapter_title()` / `normalize_chapter_title()` — selection priority (first match wins):

1. **Markdown heading** — `## title` / `### title` (after rename normalization)
2. **CIP in first 3 lines** → `版權頁`
3. **Earliest short non-banner line** (≤30 chars, doesn't match `叢書|丛书|名著|系列|文集|文庫|出版社`) — document order, so 「目錄」 beats later「第一章」 inside a TOC chunk
4. **Long chapter heading anywhere** — `^第N(章|卷|編|册|冊|部|集|篇|節|节|回|课|課)` accepted even if >30 chars (君主論's chapter titles can be 30+ chars)
5. First candidate ≤60 chars as last resort
6. Filename fallback (`text/part0001.html`) — should never reach here for well-formed books

Cosmetic renames trigger **heading rewrite** in chunk content — without this, sidebar shows `版權頁` but page renders `## 圖書在版編目（CIP）數據` as title.

### Same-chapter cross-spine merge

Previous chunk has EXACT same `volume + chapter_path` as current → continuation (cross-spine-doc spillover). Strip duplicate heading and append. Without this each chapter's title-image spine doc becomes phantom standalone chunk.

### Volume detection — known limits

`looks_like_volume()` requires `卷 / 冊 / 部 / 集 / 篇` in TOC entry. Works for:
- ✅ 文明的歷史：發現者（上冊） — has 「冊」
- ✅ 中國儒學史：先秦卷 — has 「卷」
- ✅ 五燈會元第N部 — has 「部」

Misses:
- ❌ 上 / 中 / 下 alone (「上」 is too common to safely match)
- ❌ Volume I / II in mixed-lang editions
- ❌ 輯 or other markers not in set

If a multi-volume book gets flattened, **add the marker to `VOLUME_MARKERS`** and re-run. Don't try structural detection — the marker check is the only reliable EPUB TOC signal.

### Broken anchor fallback (EPUB)

Some EPUBs (e.g. 中國儒學史) put `#anchor` fragments in TOC but body never emits matching `id="..."`. Handler:

1. After `parse_volume_toc()`, validate each `(file, anchor, title)` against the doc's HTML.
2. ≥1 anchor lands → keep split-at-anchor behavior.
3. **No** anchors resolve → promote first declared title to doc-level volume start. Transition still fires at doc beginning.

Logged as `(N anchored volume(s) had no resolvable id — promoted to doc-level starts)`.

### Rich publisher metadata extraction (`_extract_publisher_metadata`)

Scans every chunk for 版權頁-style key-value lines, writes to ebooks columns during `update_db()`:

| Field | Regex source | ebooks column |
|---|---|---|
| `full_title` (subtitle split) | `書名: …` / `Title: …` | `subtitle` (post-`：` part) |
| `original_title` | `原文書名: …` / `原書名: …` / `Original Title: …` | `original_title` |
| `author_en` | `作者: 中文（English）` parens capture | `author_en` |
| `translator` | `譯者: …` (stops at `│ \| ， ; / 、`) | `translator` |
| `publisher` | `出版: …` / `出版社: …` / `Published by: …` (rejects `出版日期/年/地`) | `publisher` |
| `publish_year` | `初版: …YYYY` / `初版首刷: YYYY` / `電子書: …YYYY` | `publication_year` |
| `original_publish_year` + `original_author` | `Copyright © YYYY by AUTHOR` | both |

Field-stop char class `_FIELD_STOP = "\n│|，,；;／/（(、"` keeps regexes from greedy-eating siblings on packed lines like `作者：X│譯者：Y│出版者：Z│出版日期：YYYY年`.

**Auto-copy to `books` on excerpt creation** — `server/api/annotations/index.post.ts` POST handler with `save_as_excerpt: true` reads rich columns from `ebooks` and copies them into auto-created `books` row, so 「+ 書摘」-created books match the richness of manually-entered ones. When you tweak extraction regexes here, re-run `--all` so existing ebooks pick up new fields.

### DB previews (`ebook_chunks`)

After writing JSONL + R2, refresh `ebook_chunks`:
- DELETE existing rows for this ebook
- INSERT 200-char preview of each chunk
- Adaptive batch (100 → 50 → 20 → 5 → 1) to ride out Supabase IO budget 57014 timeouts on 800+ chunk multi-volume books

---

## Idempotency + annotation safety

| Branch | Re-run safe? | Annotation safety |
|---|---|---|
| EPUB | ✅ overwrites JSONL / R2 / DB / ebooks columns | ⚠ `chunk_index` can shift if HARD_DROP_PATTERNS / dedupe rules change — avoid re-running on books with annotations |
| PDF Plan A | ✅ overwrites | ✅ `chunk_index` + `page_number` preserved exactly |
| PDF Plan B v0 on Plan-A book | ✅ overwrites | ⚠ re-chunks → `chunk_index` shifts; refuses without `--force` if annotations exist |
| PDF Plan B v0 on Plan-B book | ⛔ HARD STOP `JSONL already chapter-chunked` — revert via `standardize_pdf_lite` first | — |

Currently 3 ebooks have annotations: 文明的歷史 / A state of mixture / 道教簡史 (none are 套書, none are PDFs). Check first if you batch-run.

---

## Verify a result

```bash
python -c "
import json
from pathlib import Path
p = Path('G:/我的雲端硬碟/資料/電子書/_chunks/<ebook_id>.jsonl')
chunks = [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines()]
print(f'chunks: {len(chunks)}')
print(f'first 5 page_numbers: {[c.get(\"page_number\") for c in chunks[:5]]}')
print(f'last 3 page_numbers: {[c.get(\"page_number\") for c in chunks[-3:]]}')
print(f'chapters detected: {sum(1 for c in chunks if c.get(\"chapter_path\"))}')
print(f'volumes: {set(c.get(\"volume\") for c in chunks if c.get(\"volume\"))}')
print()
for i in [0, 1, len(chunks)//2, len(chunks)-1]:
    c = chunks[i]
    print(f'[{i}] vol={c.get(\"volume\")} title={c[\"chapter_path\"]}')
    print(c['content'][:200])
    print()
"
```

Reader-side: open `/ebook/<id>` (restart dev server first to clear LRU cache):
- TOC sidebar groups by volume if multi-volume
- Headings render bold + sized (h2 centered with rule, h3 left-aligned)
- Chinese is traditional throughout
- No `Digital Lab` ad pages
- PDF: `?page=N` URL matches printed page in the chunk content
- Chapter labels for pages that started with chapter marker

---

## 故障排除

**Reader sidebar shows 「目錄/插頁」 as fake volumes**
→ `standardize_ebook.py` was run before volume-marker filter. Re-run.

**Reader shows publisher ad page (e.g. Digital Lab)**
→ Add the phrase to `HARD_DROP_PATTERNS` in `standardize_ebook.py`, re-run.

**EPUB chapter titles show as filename (e.g. `text/part0001.html`)**
→ Heading detection failed. Check if h1-h4 exists in source HTML; if not, add to `CHAPTER_TITLE_RE` or extend `derive_chapter_title()`.

**PDF chapter_path mostly null after Plan A**
→ Normal — most PDF pages are mid-chapter. Run Plan B to get chapter chunks.

**PDF Plan B skipped a book with 「only N chunks produced」**
→ TOC had ≤3 usable entries OR was page-level. Book stays on Plan A (acceptable).

**「JSONL already chapter-chunked」 when re-running Plan B**
→ Run `standardize_pdf_lite.py <id>` first to revert to per-page, then Plan B again.

**Search returns no fulltext hits**
→ `ebook_chunks` table doesn't have previews for this book. Run `repopulate_chunk_previews.py --book <id>`.

**`Errno 22` invalid Windows path during batch**
→ Pre-existing data issue, not a script bug. 5 books in the library have this; skip them.

---

## Files NOT to touch

- `data/local_inventory.json` — frozen Drive scan snapshot
- `G:/我的雲端硬碟/資料/電子書/_chunks/*.jsonl` — source of truth for full text (R2 mirrors these; if lost, must re-parse)

## Related

- [`ebook-pipeline` SKILL](../ebook-pipeline/SKILL.md) — orchestration hub (parse_worker → ocr_with_gemini → standardize fan-out)
- [`scripts/parse_worker.py`](../../../scripts/parse_worker.py) — first-pass parser; produces unstructured per-doc / per-page chunks that this skill polishes
- [`scripts/ocr_with_gemini.py`](../../../scripts/ocr_with_gemini.py) — for scanned PDFs; emits same per-page JSONL as parse_worker
- [`scripts/repopulate_chunk_previews.py`](../../../scripts/repopulate_chunk_previews.py) — back-fill DB previews from local JSONL
