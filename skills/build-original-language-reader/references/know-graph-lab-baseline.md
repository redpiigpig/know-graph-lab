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

- 50 lessons, 1,000 words, uneven by design: lessons 1–33 are BBH2 chapters 3–35 exactly as the textbook has them (4 to 39 words each, 552 total); lessons 34–50 split the 448-word frequency extension (26–27 each).
- Lesson sizing is rebuilt by `scripts/assign_hebrew_lessons.py`; rerun `scripts/build_hebrew_reader_data.py` after it.
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

Contract frozen 2026-08-18 — see `greek-reader-contract.md`. Verify live.

| Layer | Current path | State |
|---|---|---|
| 50-lesson assignment | `scripts/assign_greek_lessons.py` | done — lessons 1-30 are BBG ch. 4-36 (340 words, 2-26 each), lessons 31-50 split the 660-word Mounce extension (33 each) |
| 1,000-word master | `data/originalReaders/vocabulary/greek-1000.json` | lesson/lessonSlot/lessonSource/lessonLabel written; `glossZh` stays empty by design |
| Traditional-Chinese gloss layer | `scripts/build_greek_vocab_glosses.py` -> `greek-1000-gloss-zh-reviewed.json` | running, resumable, cache-backed |
| Frozen text loaders | `scripts/greek_source_texts.py` | SBLGNT (MorphGNT) + Swete 1930 word database |
| 25-chapter plan | `scripts/build_greek_scripture_plan.py` -> `scripture-plan.json` | done — 709 verses, 13,214 Greek words, NT 13 / LXX 6 / deuterocanon 4 / pseudepigrapha 2 |
| Patristic loaders | `scripts/greek_patristic_sources.py` | Open Apostolic Fathers, First1KGreek TEI, repository creed files, glt.goarch.org |
| Shared LLM client | `scripts/original_reader_llm.py` | extracted from the Hebrew interlinear so both jobs share one 429 gate |

Source cache: `output/source-cache/original-readers/greek-full/sources/{sblgnt,swete,apostolic-fathers,first1k,liturgy}`.

Still open: the 25 patristic/creed/decree master, the Chrysostom liturgy appendix, the 100 memory verses, the RCUV2010 export for New Testament and LXX-canonical chapters, the deuterocanonical Chinese text, the interlinear layer, the master assembly, the web reader and the print build.

Known source gaps to resolve rather than paper over:
- `data/creeds/ecumenical-councils/02-constantinople-381.ts` carries no Greek version at all.
- `early-06-greek.txt` (Constantinople III, 681) was never scraped.
- `early-04-greek.txt` holds the Chalcedonian *canons*, not the Definition of Faith.

## Latin continuation checkpoint

The Latin manifest is still a plan/placeholder structure rather than a completed 1,000-word, 50-lesson reader. Freeze the Latin textbook/frequency source, pronunciation profile, Vulgate edition, full readings, and rights before declaring content complete.
