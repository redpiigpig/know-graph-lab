---
name: build-original-language-reader
description: Produce, resume, adapt, or audit complete private-use B5 original-language readers for Biblical Hebrew, Biblical or Patristic Greek, and Ecclesiastical Latin, and the printed flashcard decks derived from their vocabulary masters. Covers a 50-lesson vocabulary curriculum, textbook-specific transliteration and pronunciation, typed biblical proper names, 100 memory units, full Scripture chapters and complete prayers or articles, language-specific appendices, authenticated noindex web readers, aligned pronunciation audio, source-rights manifests, DOCX/PDF generation, and deterministic plus full-page visual QA. Use for full production rather than samples, templates, vocabulary-only lists, or general language questions.
---

# Build complete original-language readers

Produce one authoritative data master and derive print, web, audio, and QA artifacts from it. Never treat a sample, placeholder manifest, old render, or partially populated reader as complete.

## Load the required references

Read these files for every production run:

- `references/release-contract.md`
- `references/data-model.md`
- `references/rights-and-source-freeze.md`
- `references/qa-gates.md`
- `references/exercise-sets.md` — the ten translation exercises that now stand
  where the two memory verses used to.  It carries the frozen contract (ten
  items, original into Chinese only, seven composed plus three quoted, all
  twenty lesson words present, no untaught word), the one method that was tried
  and ruled out, what the corpus gate can and cannot certify, and a status table
  saying which reader is finished.
- `references/silent-failures.md` — the bugs in this series that shipped a page
  looking finished: keys that were positions, files whose existence stood in for
  their content, alignment by index between texts that do not correspond, gates
  that threw away good data, excerpts measured in words instead of the work's own
  divisions, and the one register that must not be machine-translated at all.

Read the selected language section in `references/language-profiles.md`.

For a Latin release in `know-graph-lab`, read `references/latin-reader-contract.md`;
it carries the two-volume lesson shape, the Collins order and why it comes from
the back matter rather than the units, the three-register lemma precedence, the
Studium Biblicum Chinese and the 信望愛 endpoint that answers the wrong book
with `success`, the fifty Vulgate chapters and their ten misalignments, the fifty
church readings with their complete/excerpt split, the ten appendices, and the
release-specific stop conditions. Then read `references/latin-reader-handoff.md`
for what that release actually has, what it does not, and the traps that have
already produced silently wrong data.

For a Japanese release in `know-graph-lab`, read
`references/japanese-reader-contract.md`; it carries the two-volume shape the
owner froze on 2026-08-27 (稱第一冊／第二冊，不用上下冊), the《大家的日本語》
lesson order and the third-party page it was reconstructed from, why this reader
keeps a pitch-accent column where Greek dropped its transliteration one, the
pre-war religious-studies corpus, the 文語訳 Bible and the Buddhist formulae the
owner requires, and its own stop conditions.

For a Greek release in `know-graph-lab`, also read `references/greek-reader-contract.md`; it carries the two-volume lesson shape (50 lessons of 20 words per volume), the three-layer Koine lemma resolver, the source freeze, the 50-chapter allocation for 上冊, the 50 readings and 100 sentences of 下冊, the one numbering crosswalk that refuses rather than approximates, the appendices, and release-specific stop conditions. Then read `references/greek-reader-handoff.md` for where that release actually stands, which decisions this build took without the owner, and the traps that have already produced confident wrong answers.

Read `references/silent-failures.md` before wiring a new language, and before believing any count computed only once: every defect in it shipped a page that looked finished.

**Where the artifacts go (from 2026-08-27):** `output/` is no longer version-controlled. Finished DOCX and PDF stay in the local `output/original-readers/` working copy and are also copied to Drive `資料\知識圖工作室\語言\原文讀本\讀本\`; the print-ready masters go to `…\原文讀本\印刷母版\`. What stays in git is the curated layer only — the top-level `*.json` and `*.md` under `output/source-cache/original-readers/{hebrew,greek,latin}-full/` (scripture plans, reviewed glosses, memory selections, validation reports) plus each audio `manifest.json`. Downloaded third-party corpora under `sources/`, `morphhb-src/` and the lexicon dumps are never tracked. To track a new curated file, add one line to the `.gitignore` allowlist rather than un-ignoring a directory; the full rule is `docs/repo-hygiene.md`.

Read `references/layout-web-audio.md` before producing DOCX, PDF, online pages, or audio. Its first section is the layout the three readers share; a new reader matches it rather than inventing its own. Printed flashcard decks are their own skill, `original-reader-flashcards`; `references/flashcard-decks.md` holds their per-deck state.

Read `references/flashcard-decks.md` before building or changing a printed flashcard deck;
it also carries the sheet geometry that makes a stack cuttable and the state of the
one-picture-per-card rule. For the Hebrew proper-name appendix — its four person
categories, the three kinds of duplicate, and the two traps that make a repair land
on nothing — read `references/hebrew-appendix-names.md`.

When working in `know-graph-lab`, read `references/know-graph-lab-baseline.md`. Treat all paths and counts there as checkout-specific facts that must be verified live.

### Naming and lemmatising are register questions, not lookups

Two failures recur across languages and are worth carrying into any new reader:

- **A general-purpose analyser answers in the wrong register.** Morpheus covers all
  of Ancient Greek and is Attic-first, so a Koine reader built on it teaches
  Classical headwords under a Koine title. Prefer a lemma source tagged on the
  corpora being taught, and demote the general analyser to a last resort that is
  allowed to say nothing.
- **Chinese names come from a register, never from the model.** Route each name to
  whichever register covers it, record which route named it, and leave the cell
  empty when none does. Where no register exists, the translation itself can be
  the register: a name's Chinese can be read out of the aligned Chinese text by
  counting, which is evidence rather than recall.
- **A register can cover the neighbouring domain and still answer everything.**
  `place_names` returned clean empty results for 撒瑪黎雅, 赫貝龍 and 加里肋亞
  because it is a general historical-geography table, not a biblical one. Nothing
  errors; the misses just look like hard inputs. Print what a source actually
  contains before concluding your inputs are at fault.
- **Classifying is also a register question.** Strong's writes its definitions to
  a house style — `a place in Palestine`, `a son of Joseph`, `the name of two
  Israelites` — so reading those phrases is reading evidence, not guessing
  (`scripts/strongs_name_kinds.py`). Whatever cannot be settled stays in an
  explicit 待歸類 bucket; folding it into 其他人名 asserts a fact nobody
  established.

## Run the workflow in order

1. Inspect the workspace, dirty files, current master, previous QA reports, and running process ownership. Preserve unrelated work.
2. Freeze a release configuration: language, exact lesson/count contract, textbook vocabulary order, extension rule, source editions, Traditional-Chinese Bible edition and variant, pronunciation profile, appendices, rights status, and output paths.
3. Freeze every source separately. Record ancient work, modern edition, digital transcription, translation, recording, and font rights rather than collapsing them into one license claim.
4. Build the vocabulary master:
   - Preserve the named textbook's verified order first.
   - Do not invent a missing textbook order.
   - Extend only by a documented corpus-frequency rule after the textbook ends.
   - Lesson size is a frozen per-release decision, not a default. Either shape is legitimate: a lesson may equal one textbook chapter with that chapter's real, uneven count, or the whole running order may be cut into even blocks. Freeze which one before assigning, and make every validator, heading, checklist and test agree with it.
   - The Hebrew release is frozen at an even 50 x 20. The textbook order still governs the sequence, so a lesson spans whichever textbook chapters fall inside its block; print that span in the lesson header rather than pretending the lesson is a chapter.
   - Whenever the shape changes, re-check the artifacts that silently encode it — memory-verse selection is keyed to lesson membership and every unit must still match its own lesson's words.
   - Preserve intentional homographs as separate lexical entries.
   - Store textbook-specific transliteration, source evidence, part of speech, frequency, and typed person/place/people/divine-name metadata.
   - Review every Traditional-Chinese gloss. Reject blanks, generic categories, English leakage, and machine placeholders.
5. Build immutable source-text layers and separate learner-facing display layers. Never silently overwrite ketiv, pointing, breathings, macrons, punctuation, or source orthography.
6. Use 《和合本修訂版》（2010） for every Traditional-Chinese Bible quotation in the current project, except the Ecclesiastical Latin release, which the owner froze to 思高譯本 on 2026-08-25 because its Latin base is the Catholic canon in Greek psalm numbering. Freeze the selected variant explicitly. Do not fall back to ChiUn/CUV1919 or another version. Route all MT/LXX/Vulgate numbering differences through one shared crosswalk.
7. Build 100 memory units after vocabulary is fixed:
   - Generate a candidate pool using lesson-word overlap, cumulative coverage, grammatical completeness, and memorability.
   - Reject lists, fragments, near-duplicates, census material, and misleading verse-number joins.
   - Require exactly two unique, reviewed units per lesson.
   - Save candidate scores and the human-review decision record.
   - **They no longer print.** Since 2026-09-11 the printed lesson carries the ten
     translation exercises in that slot (`references/exercise-sets.md`); the memory
     units stay in the data master and on the web reader. All four are wired that
     way as of 2026-09-16 (Hebrew 09-12, Latin 09-14, Greek 09-15, Japanese
     09-16). Anything the book says about itself — cover subtitle, the
     how-to-use cards, the colophon, the end-of-lesson checklist — has to say
     exercises too, or the book is describing a layer it no longer contains.
   - **Then read the PDF back.** `render_and_check_reader_pdfs.py` certifies the
     paper and nothing on it; `scripts/audit_printed_exercises.py {heb|lat|grc|ja}`
     opens the rendered books and checks that each lesson prints ten items, that
     they are the ten belonging to the lesson the running head names, that no
     item line carries Chinese, and that nothing is printed twice. `ja` is a
     fourth language there; it skips the Chinese-character test, because
     Japanese is written in kanji, and relies on the exact line match instead.
   - **Then read the pages back a second way.**
     `scripts/audit_reader_pages.py` opens all fourteen books and checks what the
     render checks cannot see: lessons present and in order, ten items each, text
     inside the type area (mirrored — the bound edge swaps sides every turn),
     placeholders still unfilled, Simplified Chinese, and whether every book names
     its sections in the same words. It found, on 2026-09-16, fifty-two Chinese
     strings that had come back from a model's fallback layer in Simplified and
     been stored and printed as given — whole paragraphs of it in the Greek books.
     `scripts/fix_reader_simplified_zh.py --write` repairs that class.
     🚨 Detect Simplified **by character**, never by round-tripping OpenCC: that
     calls 祢 Simplified. And Japanese shinjitai (国・学・会・点) are not
     Simplified Chinese — counting them reports four hundred clean pages as dirty.
   - **Four books, one set of words.** The owner ruled on 2026-09-16 that every
     lesson in every reader carries a 「生詞」 heading and a 「讀本」 heading —
     not 讀文, not 完整主讀文, not an English `Reading` label and nothing else,
     which is what the four of them used to say. Same for the gloss column:
     keep a grammatical note when it names a **construction** (受詞記號,
     虛擬語氣標記, 不定詞標記, 完成式助動詞, 關係代詞, 意志·推量, 被·可能·敬),
     drop it when it names a **slot** (冠詞 and every dress of it, 主格／受格／
     賓格／與格／屬格, 單數／複數). `scripts/prune_gloss_terms.py` holds the table.
     🚨 Japanese is the exception, and the owner made it deliberately: there the
     case label *is* the whole gloss — は「（主題）」 against が「（主格）」 — so
     dropping them would blank 21,172 glosses and make the two particles
     identical in the interlinear. Japanese keeps its particle markers.
   - **Every volume needs a spine, in the course reader's format**
     (`scripts/build_reader_spines.py`, which follows `build_reader_spine.py`):
     a B5 carrier sheet, the strip drawn at its true width in the middle, 247 mm
     tall so the printer's own margin cannot clip it, characters set upright one
     per cell top to bottom (a rotated line is lying on its side, which is not
     vertical setting), half-width runs kept horizontal inside one cell, no crop
     frame, and one grey line outside it giving the page count and the computed
     width for the copy shop. Under 100 pages, no spine — it would be a few
     millimetres wide and could not be trimmed or glued.
   - **Then move the books to Drive.** `output/` is scratch, not the products'
     home. Re-render changes the page count, the page count changes the spine
     width, and a book left in `output/` is a book the owner cannot open:
     `build_reader_spines.py`, then `sync_reader_artifacts.py --write`, which
     makes the local working copy and both Drive folders match
     `output/print-masters/` and files the superseded render under
     `_superseded/`. Reader PDFs and DOCX never go to R2 — see
     `docs/repo-hygiene.md`.
8. Build full readings, not summaries disguised as readings. Preserve the approved order. The default release contract is 25 complete Scripture chapters plus 25 complete prayers or articles; appendices do not silently replace those 50 readings.
   - **Every reading is a complete chapter or a complete piece.** Where a work is too long to print entire, cut at *its own* divisions — whole chapters, numbered sections, canons — and let the budget decide how many fit, never how much of one. A word-count excerpt stops mid-argument. Record what was printed: 「第 1–4 節（完整，共 33 節）」.
   - Divisions are not always punctuated (`1 Excitatio mentis…`), section numbers are not always tight against their point (`2 . Haec…`), and the edition's own headings sit inside the OCR — including the title of the *next* reading, which is where this one ends.
   - Ordering is a frozen decision, not automatically difficulty. Once the owner says a reading need not match the vocabulary already taught, a coverage sort has nothing to recommend it: use the canon's order, or chronology, and keep coverage as a reported statistic.
9. Build the word-by-word layer over every running-text unit before layout:
   - Tokenise the printed text, gloss each token with its contextual Traditional-Chinese meaning, and give every unit without a published translation a whole-unit rendering as well.
   - Gate on gloss-count equals token-count, on blank glosses, and on source-script or Latin leaking into a gloss.
   - Cache per unit so a partial run resumes instead of restarting, and re-run rounds until nothing is missing.
   - Never ship a reading whose Chinese is only one whole-verse translation line.
   - **Do not machine-translate a text that has a received wording.** A liturgical formula the congregation knows by heart is not a rough draft to be improved: asked for `R. Et cum spiritu tuo.` a model returned a versicle that is not in the Latin. Leave the gap, print why, and make the gate repeat it every run so nobody fills it with a draft.
   - A `-chinese.txt` beside the Latin is not a parallel translation. Classify it — placeholder, anthology excerpt, unnumbered translation, numbered translation — and join only on numbers both sides carry.
10. Add each language-specific terminal section. For Hebrew, keep the complete fifteen-step Haggadah separate from the 25 prayer/article readings.
11. Build the appendices as a first-class layer, not an afterthought:
    - **Every appendix row needs Traditional Chinese of its own.** Reuse the reviewed lesson gloss wherever the word already appeared — the same word must read the same way in the lesson and in the appendix — and only then ask a model, giving it the existing English definition to render rather than a headword to recall. Latin's numerals, kinship and calendar tables shipped printing Whitaker's English because the printer read `zh or glossZh or glossEn`; **never fall back to another language**, print the empty state (`（中文待補）`) so the hole stays visible.
    - **Classify proper names into the nine categories** (`scripts/proper_name_categories.py`) and print each table sectioned, in `PRINT_ORDER`. One undivided list of four hundred names is not something anyone looks a name up in. Whatever cannot be settled stays in 待歸類.
    - **Keep a ledger of the classification** (`proper-name-categories.json`) and re-apply it with `classify_proper_names.py --reapply` whenever an upstream job regenerates the appendix file. Fields you add to a file somebody else rebuilds wholesale disappear without an error.
    - **No print caps.** Latin truncated each appendix group at 200 rows to hold the page count down and silently withheld 385 of 585 proper names.
12. Assemble one master JSON. Fail on incomplete counts, IDs, ordering, translations, diacritics, transliteration, proper names, sources, rights metadata, or placeholder text. Key every cross-file reference on an identity, never on a position a builder computed: lesson numbers move when the sort changes, and one source file can hold several readings.
13. Run `scripts/validate_reader_release.py` against the master before layout. Its defaults assume the Hebrew shape, where every lesson reads a Bible chapter; a volume that reads none needs `--scripture-lessons 0`, and two of its checks fail on a correct book without it. That is a flag, not a defect to fix in the master.
14. Generate JIS B5 DOCX and PDF from that exact master, matching the shared layout in `references/layout-web-audio.md` — banner cover, real Heading styles, no heading smaller than the body, each lesson's reading on its own page, a centred page number and a running head that names the current lesson (`STYLEREF`, one section per part). No bound volume may exceed 500 pages and the volumes of one language should be about equally thick, so a long book prints as several — the lesson ranges are frozen in each builder's `PARTS`, and `scripts/build_reader_spines.py` then draws one B5-height spine per volume from its measured page count. `scripts/render_and_check_reader_pdfs.py` drives LibreOffice (one `UserInstallation` profile per file) and then checks page geometry, embedded fonts, U+FFFD and blank pages. Invoke the Documents and PDF skills and follow their render-and-verify procedures.
15. Build the authenticated online counterpart from the same master. Keep authorized JSON and audio out of public static directories.
16. Decide where the audio lives before building it. Where the owner has said it belongs on the web — as for Ecclesiastical Latin (2026-08-27) — the deliverable is device speech in the page: per-line and per-word controls, a straight-through walk with the current line highlighted, and a spelling rewrite that makes the voice correct rather than approximate (`utils/ecclesiasticalLatin.ts`). Where a recorded track is required instead, add real recordings and segment cues only under the frozen historical/textbook profile, never expose a play control for a missing track, and never let TTS or an external link satisfy that gate.
17. Run the deterministic, package, raster, full-resolution visual, API, UI, type, build, and audio gates in `references/qa-gates.md`.
18. Run `scripts/hash_release_artifacts.py` after all artifacts pass. Store the resulting hash manifest beside the QA report.
19. Report exact paths, counts, versions, hashes, QA results, and audio status. Do not deploy, publish, or call the release complete without explicit authority and every required gate passing.

### Proper names: identity is the qualified name, never the spelling

A name register holds homonyms on purpose. Three men named Theophilus, two named
Saturninus, two named Julianus. So:

- **`name_original` is a spelling, not an identity.** Deduplicating a seed against it
  made "Theophilus of Alexandria" collide with the Caesarean's Latin spelling and be
  skipped as already present — while the appendix went on printing the Caesarean's
  Chinese for a man the corpus calls *episcopus Alexandrinus* 25 times out of 25.
  Key identity on `name_english`; that is the column carrying the qualifier.
- **The ambiguity guard compares rows, not fields.** One row offering a Catholic form
  and a recommended form that differ is still one person. Comparing field by field
  read Origen as two people and blanked him.
- **Blank beats a guess, and a cited decision beats blank.** Where the corpus really
  does show several bearers (Julianus: six; Saturninus: seven), print a
  transliteration, not a person. Where it shows one, record *which register row* in a
  referent table and let the register keep supplying the Chinese — never copy the
  Chinese into the builder, or the reader grows a second glossary nobody knows about.

### Index the display spelling under the same key as the entry

`harvest_names` keys names by **lemma**, so the table of surface spellings must be
built by lemma too. Built by raw word form instead, the lookup missed and the builder
printed the fold key itself — `iohannes`, `iordanes`, `zebedaeus`, lowercase and with
J/V flattened, where the edition prints `Joannes`, `Jordanes`, `Zebedæus`. The worst
one was `aelius`: the Latin dictionary lists the Roman gens *Aelius*, so lemmatising
`Eliam` (Elijah, 26 occurrences) produced it, and a Roman appeared in a table of
biblical names with a plausible-looking entry. **A lowercase headword in a proper-name
table is a bug, never a name** — assert on it.

### Alignment guards: three, and each catches a different lie

Matching a Latin name to its Chinese by shared verses needs all three, and the numbers
matter:

1. the candidate follows the name through most of its verses (`hits ≥ 0.6 × appearances`);
2. the candidate is not a word that follows everything (`corpus total ≤ 8 × hits`);
3. the candidate clearly beats the runner-up (`hits ≥ 1.3 × runner-up`).

Guard 2 at 2.5 killed exactly the commonest names: *Judas* followed 「猶大」 through 76
of 80 verses and was rejected because 猶大 occurs 241 times overall. The book printed a
blank for a name appearing 319 times. Guard 3 catches the opposite lie — Daniel's three
companions always appear together, so Sidrach, Misach and Abdenago had *identical*
candidate lists and all three were resolved to 沙得辣客. Two of the three were wrong on
the page and nothing showed it. **When the evidence cannot separate them, leave it
blank and say so.**

### Filling gaps by hand: label the route, never blend it

Where verse alignment cannot reach, writing the name yourself is correct — but the
route field must distinguish 「思高體例（人工補）」 from `sigao-underline-alignment`.
Blend them and nobody can ever re-verify which entries were *found* and which were
*written*. Record why each hand-filled entry is fillable (a case ending resolved, or
the verse that fixes an order, e.g. Dan 1:7 for those three companions).

And report the table that prints, not the pool it came from: this report once read
「讀本所見 108，已由思高逐節對位定出中文 108（100%）」 when 28 of them were hand-filled
and the denominator was the 585 names before the table was cut to 146. Every figure was
correct and the sentence described a different table.

### A rebuild must not be a regression

`build_latin_appendices.py` recomputes spellings and corpus attestation; the Chinese
for the numeral, kinship, calendar, principal-part and terminology tables comes from a
separate model-backed pass. Rebuilding therefore zeroed 1,192 glosses — twice — and the
book still paginated, still passed every gate, and printed 1,205 「（中文待補）」.

The builder now re-applies `appendix-gloss-zh.json` itself, so a bare rebuild is
lossless. Two things about that cache: it is keyed on the **raw headword**, not a folded
form (inventing a fold silently restored 1,062 of 1,192 and the 130 misses looked
exactly like "never glossed"), and what it cannot restore is genuinely unglossed rather
than self-inflicted. Check the count it prints, not just that it ran.

### Alignment tie-breaks must be deterministic

Candidate Chinese accumulated from a `set` of strings, so `Counter.most_common` broke
ties by `PYTHONHASHSEED`. Two builds of identical inputs disagreed on about five names
— some swapping referent, some going blank when the newly-chosen candidate failed a
frequency guard. Sort ties explicitly. **Build the same data twice and compare bytes**;
a pipeline that cannot reproduce itself cannot be audited.

## Invalidate downstream work

Any change to vocabulary, glosses, source text, translation, crosswalk, readings, appendix data, name categories, styles, fonts, or audio invalidates all downstream artifacts and their prior QA. Rebuild and re-inspect; never reuse an old PDF or page-QA result after an upstream change.

The chain is longer than it looks, and skipping a link produces a PDF that renders cleanly and is simply out of date. Appendix data feeds the master, the master feeds the DOCX, the DOCX feeds the PDF, and the same appendix data separately feeds the flashcard decks and the web tables. A patch to the print builder applied *while* a build was running produced a book whose cover was new and whose appendix was old; it looked finished and passed every gate. **Rebuild from the data layer down, in one run, and check the rendered page for the change you just made** — not for errors, for the change.

## Stop conditions

Stop the release and report the exact gap when:

- an exact source edition or authorization record is missing;
- a textbook order would need to be invented;
- a declared full reading contains placeholders or excerpts;
- a Bible translation or variant is not explicit;
- required pointing, accents, breathings, or transliteration fields are incomplete;
- real reviewed audio is required but only TTS or links exist (this does not apply where the owner has designated web device speech as the deliverable);
- a final artifact hash differs from its QA report or master;
- an appendix row would print in a language other than the reader's own.

Use precise states such as `content_complete_audio_pending`; never shorten a partial state to `complete`.
