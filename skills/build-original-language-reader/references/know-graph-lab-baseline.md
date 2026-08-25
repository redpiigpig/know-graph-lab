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

- 50 lessons x exactly 20 words. One running order (BBH2 chapters 3-35, then the corpus-frequency extension) cut into even blocks, so a lesson spans a chapter range rather than being a chapter.
- Lesson sizing is rebuilt by `scripts/assign_hebrew_lessons.py`; rerun `scripts/build_hebrew_reader_data.py` after it.
- 546 retained BBH2 entries plus 454 frequency-extension entries. The BBH2 run is shorter than the textbook's 552 because 119 person/place/nation names were lifted into the appendix; the extension reaches correspondingly further down the corpus (to 32 occurrences). Two exact duplicate textbook rows remain traceable through `sourceOrders`.
- Proper names: 119 in the appendix table, 16 still in the lessons (11 divine names/titles, the sabbath, and אָדָם / נֶגֶב / שְׁאוֹל / יְאֹר, which carry a `keptInLessons` reason). The two halves total the same 135 verified Chinese names the QA gold list freezes, now keyed by `strong|pointed`.
- Rebuilt by `scripts/rebuild_hebrew_vocab_without_proper_names.py` (a one-shot migration; it refuses to run twice) and `scripts/build_hebrew_appendix_tables.py`.
- Four appendix reference tables, 287 rows: numerals 38, kinship 37, calendar 35, classified proper names 177 (names cross-listed under each type they carry). Web route `/original-readers/hbo-lessons/tables`.
- Traditional-Chinese glosses live in `hebrew-gloss-zh-reviewed-by-lemma.json`, keyed by `(strong, pointed)`. The old ordinal-keyed `hebrew-1000-gloss-zh-reviewed.json` is dead — it would misalign every meaning by one.
- 100 unique WLC memory verses, two per lesson, **93 of them `pending_human_review`**: the vocabulary change invalidated the hand-reviewed pairing (only 51 of the old 100 still fell in any lesson's candidate pool), so the scorer re-selected. One verse (lesson 49 slot 2) matches a single lesson word because no verse in the corpus carries two of that lesson's rare words; it is labelled, not padded.
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

Contract frozen 2026-08-18, curriculum re-frozen 2026-08-24, two-volume build
completed 2026-08-26: both volumes pass the release validator (22/22 and 19/19),
print masters are 480 and 1,138 pages of JIS B5 with every font embedded, and the
only remaining release gate is audio. See `greek-reader-contract.md` for what it
must be and `greek-reader-handoff.md` for where it actually stands. Verify live.

| Layer | Path |
|---|---|
| 2,000-word master | `data/originalReaders/vocabulary/greek-2000.json` |
| Appendices | `data/originalReaders/vocabulary/greek-appendices.json` |
| Traditional-Chinese glosses | `greek-2000-gloss-zh-by-lemma.json`, keyed by lemma |
| Koine lemma resolver | `scripts/build_greek_koine_lexicon.py` -> `koine-lexicon.json` |
| 上冊 50 chapters | `scripts/build_greek_scripture_plan.py` -> `scripture-plan.json` |
| 下冊 50 readings | `scripts/build_greek_patristic_plan.py` -> `patristic-plan.json` |
| Church-document freeze | `scripts/fetch_greek_church_documents.py` -> `sources/church-documents/manifest.json` |
| Liturgy appendix | `scripts/build_greek_liturgy.py` -> `liturgy-chrysostom.json` |
| 200 memory units | `select_greek_memory_verses.py`, `select_greek_memory_sentences.py` |
| Chinese Bible | `export_reader_rcuv2010_greek.py` -> `RCUV2010.json`; `export_reader_fhl_deuterocanon.py` -> `deuterocanon-zh.json` |
| Shared numbering crosswalk | `target_reference()` in `export_reader_rcuv2010_greek.py`; the master and the selector both import it |
| Master assembly | `scripts/build_greek_reader_data.py` -> `greek-reader-two-volumes.json` (schema 2.0.0) |
| Release validation | `validate_reader_release.py --volume 1` / `--volume 2` |
| Word-by-word layer | `scripts/build_greek_interlinear.py --workers 5` -> `interlinear.json` |
| Print masters | `scripts/build_greek_full_reader.py` -> `greek-original-reader-vol1.docx`, `-vol2.docx` |
| Web reader | `data/originalReaders/greek-full-reader.ts`, `server/api/original-readers/grc-lessons/`, `pages/original-readers/grc-lessons/`; lesson key `v1-12` |
| Tests | `tests/greek-full-reader.test.ts` |
| Names audit | `scripts/audit_greek_appendix_names.py` — clears the 49 appendix names that were dictionary definitions, not names |
| Memory review record | `scripts/record_greek_memory_review.py` — both volumes, checks the Chinese in the master |
| Release hashes | `skills/.../hash_release_artifacts.py` -> `release-hashes.json` |
| Keeper | `scripts/grc_reader_keeper.ps1`, task `KGL_Greek_Reader_Keeper` |

Source cache: `output/source-cache/original-readers/greek-full/sources/{sblgnt,swete,apostolic-fathers,first1k,church-documents,liturgy,dodson}`.

The single-volume artifacts are dead: `greek-reader-50-lessons.json`,
`greek-1000.json`, `greek-1000-gloss-zh-reviewed.json` (ordinal-keyed, would
shift every meaning by one), `assign_greek_lessons.py`, and the 763-page DOCX.
Do not use any of them as evidence.

### Engine policy for the reader's language-model layers

The gloss and interlinear jobs go through `scripts/original_reader_llm.py`, which
follows the repository's standing order: **Gemini first, then NVIDIA, then
Anthropic Haiku as a last resort.** The interlinear runs several units at once
(`--workers`); one at a time managed about two units a minute, which is eighteen
hours for a two-thousand-unit backlog, and almost all of it was network wait.

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

Still open: audio, and the root cause behind the 49 cleared appendix names — the 信望愛 parser takes the dictionary's definition line instead of the name. The memory-unit review is recorded under the owner's 2026-08-22 delegation and says so explicitly rather than claiming a human pass.

The print master reuses the Hebrew builder's typesetting helpers, which means it also inherits that volume's running header and document title; `retitle()` overrides both. Without it every page of the Greek reader says it is the Hebrew one.

Parsing traps this build hit, all fixed and worth remembering:
- First1KGreek TEI prints the critical apparatus inline as `<note type="footnote">`; `itertext()` swallows it.
- The Shepherd of Hermas numbers 5 visions + 12 mandates + 10 similitudes as 27 top-level units, not chapters.
- glt.goarch.org mixes composed and decomposed Greek, so a composed anchor silently never matches.
- glt.goarch.org's Paschal homily carries a dittography; a second witness was used instead.
- Swete indexes bare apparatus sigla as their own "words", and omits Sirach 24:18/24 entirely.
- CCEL serves decomposed Greek and sets Schaff's variant readings in the same table cell as the creed.

## Latin continuation checkpoint

The Latin manifest is still a plan/placeholder structure rather than a completed 1,000-word, 50-lesson reader. Freeze the Latin textbook/frequency source, pronunciation profile, Vulgate edition, full readings, and rights before declaring content complete.

## 希臘文讀本的語言範圍：只到通用希臘文

讀本教的是通用希臘文（Koine），不是古典希臘文。這一條會被詞位還原這一步悄悄破壞，
因為現成的希臘文形態分析器 Morpheus 涵蓋全部古希臘文，且以阿提卡方言為本位：
問它 σου 的詞位，它答荷馬的所有格形容詞 σός；問它 ἐγένετο，它答阿提卡的 γίγνομαι。
照單全收的話，詞表看起來像通用希臘文，詞頭卻是古典希臘文的。

因此詞位還原採三層，順序不可調換：

1. **通用希臘文詞典**（`scripts/build_greek_koine_lexicon.py` → `koine-lexicon.json`）。
   由兩份編者標註語料合成：MorphGNT 的新約 137,554 詞次，CATSS/OSSP 的七十士 623,685 詞次。
   同一字形兩邊都有標註時**以新約的詞頭為準**，因為七十士標註沿用較舊的辭典慣例
   （εἶπεν 歸 ἔπω、σου 歸 σοῦ、χρυσοῦν 歸 χρύσεος），而課本用的是 λέγω／σύ／χρυσοῦς。
2. **阿提卡→通用希臘文橋接**（`to_koine`）。γιγν→γιν、ττ→σσ、ρρ→ρσ、-εος→-οῦς，
   加上補充形與異體的對照表。每一條改寫都先驗證落點確實是通用希臘文語料用過的詞位，
   所以這張表造不出不存在的字。**比對一律用去重音的折疊字形**——寫成字面時
   「γιγν」根本不出現在「γίγνομαι」裡，這個坑踩過一次。
3. **Morpheus**，只查前兩層沒有的字形，且其古典分析若無通用希臘文對應、
   又有多解時**寧可不計**，不猜。（猜出來的產物是 ὁλάω 與 πτελέα，
   實際上是 ὅλος 和一個人名。）

成效：七十士 97% 由通用希臘文詞典解出、0 個古典詞位；教父 88% ＋ Morpheus 補 6%，
1000 詞中僅 24 個詞位不在新約與七十士的標註詞表內，且經查全是後期教會希臘文的專門詞
（ἀσώματος、ἄτρεπτος、σύγγραμμα、ἀθεότης 之屬），非古典詞，故保留並以 `withinKoine: false` 標明。

另兩個反覆出現的坑：Morpheus 詞頭一律小寫，坡旅甲與愛任紐因此混進普通形容詞，
改以**語料本身的大小寫**判定專名（同一詞位八成以上出現時首字大寫即為專名）；
去重時若把數種拼法用空白接成一串再只按標點切，整串會被當成一個詞，去重集合等於空的。
