# know-graph-lab baseline

Verify live before use. These paths describe the 2026-08 Hebrew production pipeline and are not universal defaults.

## Hebrew data pipeline

| Layer | Current path |
|---|---|
| Vocabulary extraction | `scripts/extract_original_reader_vocab_sources.py` |
| 1,000-word master | `data/originalReaders/vocabulary/hebrew-1000.json` |
| Reviewed Traditional-Chinese glosses | `output/source-cache/original-readers/hebrew-full/hebrew-1000-gloss-zh-reviewed.json` |
| WLC 25-chapter plan | `scripts/build_hebrew_scripture_plan.py` and `scripture-plan.json` |
| Memory candidate/review | `scripts/select_hebrew_memory_verses.py`, `memory-candidates.json`, `memory-selection-review.md` |
| RCUV2010 source snapshot | `scripts/export_reader_rcuv2010.mjs` and `RCUV2010.json` |
| Shared RCUV crosswalk | `scripts/rcuv2010_reader.py` |
| 25 prayers/articles | `prayers-articles.json` |
| Complete Haggadah | `haggadah-full.json` |
| Master assembly | `scripts/build_hebrew_reader_data.py` |
| Word-by-word Chinese layer | `scripts/build_hebrew_interlinear.py` and `interlinear.json` |
| B5 DOCX | `scripts/build_hebrew_full_reader.py` |
| DOCX/PDF rendering | `scripts/render_docx_with_lo_console.py` |
| Release QA | `scripts/qa_hebrew_full_reader.py` |
| Raster QA/contact sheets | `scripts/qa_hebrew_rendered_pages.py` |

## Hebrew web pipeline

- Data assembly: `data/originalReaders/hebrew-full-reader.ts`
- Interlinear rendering: `components/HebrewInterlinear.vue`
- APIs: `server/api/original-readers/hbo-lessons/`
- Pages: `pages/original-readers/hbo-lessons/`
- Shared materializer: `server/utils/original-reader-materialize.ts`
- Tests: `tests/original-readers.test.ts`

APIs must keep authentication, noindex/noarchive, private/no-store, and `Vary: Authorization`.

## Current frozen Hebrew contract

- 50 lessons × 20 words = 1,000.
- 552 retained BBH2 curriculum entries plus 448 frequency-extension entries; two exact duplicate textbook rows remain traceable through `sourceOrders`.
- 100 unique reviewed WLC memory verses, two per lesson.
- 25 approved complete WLC chapters, 614 source verse positions, 7,751 words.
- 25 complete prayers/articles, 97 segments.
- Haggadah: 15 steps, 199 segments.
- Traditional-Chinese Bible: 《和合本修訂版》（2010）, current source variant RCUV2（上帝版）, private authorized use.
- Audio remains `not_recorded` until real reviewed tracks exist.
- Every running-text unit carries a word-by-word Traditional-Chinese gloss row; prayers, articles and the Haggadah additionally carry a whole-segment Chinese rendering, because their masters shipped with `translationZh` empty.

## Stale artifacts warning

Do not use these as final evidence after the RCUV2010 change:

- `ChiUn.json` (CUV1919/older Union Version data);
- any master generated from it;
- the earlier 342-page DOCX/PDF render;
- `rendered-pages-v6` and its visual QA.

Rebuild DOCX/PDF and inspect every new page after the final RCUV2010 master.

## Greek continuation checkpoint

`data/originalReaders/vocabulary/greek-1000.json` currently represents 20 production groups of 50 words (340 Mounce BBG chapter-order entries plus 660 verified Mounce extension entries). It is not yet a 50 × 20 lesson curriculum. Reassign lessons only after freezing the Greek reader contract.

## Latin continuation checkpoint

The Latin manifest is still a plan/placeholder structure rather than a completed 1,000-word, 50-lesson reader. Freeze the Latin textbook/frequency source, pronunciation profile, Vulgate edition, full readings, and rights before declaring content complete.
