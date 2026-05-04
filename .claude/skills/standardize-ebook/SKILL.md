---
name: standardize-ebook
description: Turn a parsed EPUB into the "reader-ready" format used by /ebook/[id] — re-parsed markdown chunks with simplified-to-traditional Chinese conversion, publisher boilerplate stripped, and (for multi-volume sets) volume hierarchy preserved. Use when wiring a new book into the reader, fixing a book whose TOC looks ugly, or batch-processing books in a category.
---

# Standardize Ebook Skill

This skill captures the pipeline that turned 文明的歷史 into the reference reading experience and generalizes it so other books can match. The full implementation is in [`scripts/standardize_ebook.py`](../../../scripts/standardize_ebook.py).

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

## Pipeline (what the script does, in order)

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

## Current state (snapshot 2026-05-04)

| Book(s) | Standardized? | Notes |
|---|---|---|
| 文明的歷史 (`181798a6-42fd-4f55-a4a8-43065dafd6f7`) | ✅ | Reference example. EPUB's K4 anchor is misplaced (mid-上冊 but tagged 下冊 start), so 發現者上冊 only has 3 chunks and 下冊 has 20. Publisher data quirk, not a script bug. |
| 哲學 category (51 EPUBs) | ⚠ done with **old volume logic** | Single-volume books had 「目錄/插頁/出版說明」 promoted to fake volumes. The fix is in main; **a re-run on the 哲學 category will clean these up** (idempotent). |
| 9 categories overall | ❌ rest not started | 哲學 done first as the demo. Other categories untouched. |

The 51 哲學 books to look at as samples (post re-run):
- 《君主論》 — single-volume; should have NO volume groups in sidebar after fix
- 《人生的智慧》 — single-volume叢書 part; same
- 《中國儒學史》 — multi-volume; should still group by 「先秦卷／漢代卷／…」 (titles contain 卷)

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
