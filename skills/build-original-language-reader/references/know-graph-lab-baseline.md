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

Contract frozen 2026-08-18; assembled 2026-08-19. See `greek-reader-contract.md`. Verify live.

| Layer | Path | State |
|---|---|---|
| 50-lesson assignment | `scripts/assign_greek_lessons.py` | done — lessons 1-30 are BBG ch. 4-36 (340 words, 2-26 each), lessons 31-50 split the 660-word Mounce extension (33 each) |
| 1,000-word master | `data/originalReaders/vocabulary/greek-1000.json` | done — 995 lexicon-matched, 5 corpus-matched, 0 unverified |
| Lexicon resolution | `scripts/verify_greek_vocab_lexicon.py`, `scripts/fill_greek_vocab_glosses_en.py` | done — Strong + Dodson + SBLGNT ladder, resolution path recorded per entry |
| Traditional-Chinese gloss layer | `scripts/build_greek_vocab_glosses.py` -> `greek-1000-gloss-zh-reviewed.json` | **blocked on quota, 0/1000**; resumable, re-queues failed batches |
| Frozen text loaders | `scripts/greek_source_texts.py`, `scripts/greek_patristic_sources.py` | done |
| 25 chapters | `scripts/build_greek_scripture_plan.py` -> `scripture-plan.json` | done — 707 verses, 13,214 words, NT 13 / LXX 6 / deutero 4 / pseudep 2 |
| 25 patristic readings | `scripts/build_greek_patristic_plan.py` -> `patristic-plan.json` | done — 913 segments, 30,060 words, 16 complete / 9 excerpts |
| Liturgy appendix | `scripts/build_greek_liturgy.py` -> `liturgy-chrysostom.json` | done — 332 steps, 26 sections, 6,772 words |
| 100 memory verses | `scripts/select_greek_memory_verses.py` -> `memory-verses.json` | done — 2 per lesson, NT 70 / LXX 15 / deutero 10 / pseudep 5, all `pending_human_review` |
| Deuterocanon Chinese | `scripts/export_reader_fhl_deuterocanon.py` -> `deuterocanon-zh.json` | done — 1933 Anglican, 4 chapters / 106 verses, verse counts match Swete |
| Missing conciliar Greek | `scripts/export_reader_creed_greek.py` -> `creeds-greek.json` | done — 381 / Chalcedon / Constantinople III, from Schaff vol. II |
| RCUV2010 Chinese | `scripts/export_reader_rcuv2010_greek.py` -> `RCUV2010.json` | done — 22 books, 90 chapters, 3,256 verses; psalm crosswalk incl. superscription offset |
| Master assembly | `scripts/build_greek_reader_data.py` -> `greek-reader-50-lessons.json` | done — 50,046 running words; fails rather than emitting a partial master |
| Release validation | `skills/.../validate_reader_release.py --language grc` | 20 PASS / 2 FAIL, both truthful (glosses pending, memory review pending) |
| Web reader | `data/originalReaders/greek-full-reader.ts`, `server/api/original-readers/grc-lessons/`, `pages/original-readers/grc-lessons/` | done — overview / lesson / liturgy, authenticated + noindex |
| Tests | `tests/greek-full-reader.test.ts` | 12 tests |
| Interlinear | `scripts/build_greek_interlinear.py` | written, not started — 2,021 units, 50,278 glossable words, 1,281 needing a whole-segment rendering |

Source cache: `output/source-cache/original-readers/greek-full/sources/{sblgnt,swete,apostolic-fathers,first1k,liturgy,dodson}`.

### Engine policy for the reader's language-model layers

The gloss and interlinear jobs go through `scripts/original_reader_llm.py`, which
follows the repository's standing order: **Gemini first, then NVIDIA, then
Anthropic Haiku as a last resort.**

The first version was Anthropic-only, inherited from the Hebrew interlinear, and
that cost seventeen hours of zero progress: the Claude Max account is shared with
the overnight fleet — around two dozen jobs at once — so every batch sat at 429
while seven Gemini keys and seven NVIDIA keys went untouched. A reader build has
no business queueing behind the fleet for a tier it does not need.

When a layer stops advancing, probe the tiers before touching the code:

- Anthropic 429 alone means the fleet is busy; the keeper will catch up.
- All seven Gemini keys returning 429 means the fleet is on Gemini too.
- NVIDIA needs two checks, because its failures look alike. A bad-key POST that
  returns 401 in a fraction of a second and a `/v1/models` listing that returns
  200 prove the endpoint is healthy; if a real completion then hangs until the
  read timeout, the *model* is saturated, not the account. `deepseek-v4-flash-0731`
  behaved exactly this way on 2026-08-21 — still listed, still authorised, and
  never answering.

Still open: the Chinese gloss layer and the interlinear layer (both quota-bound), human review of the 100 memory verses, DOCX/PDF, and audio.

Parsing traps this build hit, all fixed and worth remembering:
- First1KGreek TEI prints the critical apparatus inline as `<note type="footnote">`; `itertext()` swallows it.
- The Shepherd of Hermas numbers 5 visions + 12 mandates + 10 similitudes as 27 top-level units, not chapters.
- glt.goarch.org mixes composed and decomposed Greek, so a composed anchor silently never matches.
- glt.goarch.org's Paschal homily carries a dittography; a second witness was used instead.
- Swete indexes bare apparatus sigla as their own "words", and omits Sirach 24:18/24 entirely.
- CCEL serves decomposed Greek and sets Schaff's variant readings in the same table cell as the creed.

## Latin continuation checkpoint

The Latin manifest is still a plan/placeholder structure rather than a completed 1,000-word, 50-lesson reader. Freeze the Latin textbook/frequency source, pronunciation profile, Vulgate edition, full readings, and rights before declaring content complete.
