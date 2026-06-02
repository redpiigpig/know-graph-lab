# Pipeline tests — transcription & translation quality

`pytest` suite for the **pure heuristics** behind the [`ebook-pipeline`](../../.claude/skills/ebook-pipeline/SKILL.md)
and [`ebook-translate`](../../.claude/skills/ebook-translate/SKILL.md) skills.
These are the functions where the user's reported瑕疵 actually live:
**目錄 / 正文章節分類** (transcription) and **逐段對照** (translation).

The Vue/Nuxt component tests stay under `test/` (vitest); this is a separate
Python layer because the pipeline is Python.

```bash
npm run test:py          # or:
python -m pytest         # from repo root
python -m pytest scripts/tests/test_alignment.py -v
```

No network, DB, Drive, or LLM access — `conftest.py` sets dummy Supabase/R2
env vars so the modules import (they read `os.environ[...]` at module level),
and every test exercises only in-memory functions.

## What's covered

| File | Pipeline stage | Pain point |
|---|---|---|
| `test_chapter_classification.py` | standardize_ebook | 正文/章節分類: title normalize, continuation/volume/chapter/appendix detection, `derive_chapter_title`, implicit-volume promotion |
| `test_html_to_markdown.py` | standardize_ebook | 正文: HTML→markdown contract (`h1→##`, `<sup>(N)</sup>→[^N]`, svg/img stripped) |
| `test_pdf_toc.py` | standardize_pdf | 目錄: `normalize_toc` (page-level TOC rejection, level cap, NUL strip, dedupe, page clamp), `build_chapter_path` hierarchy, depth→heading |
| `test_translate_split.py` | translate_ebook_to_zh | `split_oversized` — no content loss / paragraph count preserved (alignment can't break at the split step) |
| `test_alignment.py` | scan_translated_book | **逐段對照**: `para_count` / `paragraph_drift` (the T11 metric) |
| `test_quality_sweep.py` | sweep_book_quality | T1 heading-bleed, T2 h3↔volume drift, T3 straight→CJK quotes |
| `test_simp_trad.py` | simp_to_trad_batch / parse_drive_inventory | simplified detection, TRAD_FIXES (历→**歷** not 曆), idempotency |
| `test_classification_ingest.py` | ingest_new_books | `fallback_category` keyword routing + filename fallback |
| `test_collapse_cjk_spacing.py` | standardize_pdf_lite | CJK space collapse, Latin spacing preserved |

## Open findings (tests as the optimization target)

- **`test_chapter_classification.py::...plaintext_first_line`** is an
  `xfail`: in the plain-text fallback path (degraded PDF/OCR chunk, no
  markdown heading), a long `第N章` title followed by a short body line is
  mislabeled with the body line — `derive_chapter_title` applies the
  "earliest short line wins" rule (the `目錄`-beats-`第一章` case) *before*
  the explicit-chapter-pattern rule. Normal EPUB chunks are unaffected
  (the title arrives as `## heading`). Flip to a real assertion once the
  ordering is fixed without regressing the `目錄` case.

## Extending — how these tests *optimize* quality

1. **Lock-in**: every passing test is a regression guard — changing a regex
   or threshold and re-running surfaces unintended classification shifts.
2. **Target via xfail**: encode a *desired* output for a known defect as an
   `xfail(strict=True)`; fixing the heuristic flips it green automatically.
3. **Reusable gates**: `scan_translated_book.paragraph_drift()` (the 逐段
   對照 metric) is now a module-level function — it can be called as a
   post-translation gate to flag chunks whose bilingual columns won't line
   up, not just at scan time.
