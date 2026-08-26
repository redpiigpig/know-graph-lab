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

For a Greek release in `know-graph-lab`, also read `references/greek-reader-contract.md`; it carries the two-volume lesson shape (50 lessons of 20 words per volume), the three-layer Koine lemma resolver, the source freeze, the 50-chapter allocation for 上冊, the 50 readings and 100 sentences of 下冊, the one numbering crosswalk that refuses rather than approximates, the appendices, and release-specific stop conditions. Then read `references/greek-reader-handoff.md` for where that release actually stands, which decisions this build took without the owner, and the traps that have already produced confident wrong answers.

Read `references/silent-failures.md` before wiring a new language, and before believing any count computed only once: every defect in it shipped a page that looked finished.

Read `references/layout-web-audio.md` before producing DOCX, PDF, online pages, or audio. Printed flashcard decks are their own skill, `original-reader-flashcards`; `references/flashcard-decks.md` holds their per-deck state.

Read `references/flashcard-decks.md` before building or changing a printed flashcard deck.

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
11. Assemble one master JSON. Fail on incomplete counts, IDs, ordering, translations, diacritics, transliteration, proper names, sources, rights metadata, or placeholder text. Key every cross-file reference on an identity, never on a position a builder computed: lesson numbers move when the sort changes, and one source file can hold several readings.
12. Run `scripts/validate_reader_release.py` against the master before layout.
13. Generate JIS B5 DOCX and PDF from that exact master. Invoke the Documents and PDF skills and follow their render-and-verify procedures.
14. Build the authenticated online counterpart from the same master. Keep authorized JSON and audio out of public static directories.
15. Add real pronunciation recordings and segment cues only under the frozen historical/textbook profile. Do not expose a play control for a missing track. TTS or an external reference does not satisfy the audio release gate.
16. Run the deterministic, package, raster, full-resolution visual, API, UI, type, build, and audio gates in `references/qa-gates.md`.
17. Run `scripts/hash_release_artifacts.py` after all artifacts pass. Store the resulting hash manifest beside the QA report.
18. Report exact paths, counts, versions, hashes, QA results, and audio status. Do not deploy, publish, or call the release complete without explicit authority and every required gate passing.

## Invalidate downstream work

Any change to vocabulary, glosses, source text, translation, crosswalk, readings, styles, fonts, or audio invalidates all downstream artifacts and their prior QA. Rebuild and re-inspect; never reuse an old PDF or page-QA result after an upstream change.

## Stop conditions

Stop the release and report the exact gap when:

- an exact source edition or authorization record is missing;
- a textbook order would need to be invented;
- a declared full reading contains placeholders or excerpts;
- a Bible translation or variant is not explicit;
- required pointing, accents, breathings, or transliteration fields are incomplete;
- real reviewed audio is required but only TTS or links exist;
- a final artifact hash differs from its QA report or master.

Use precise states such as `content_complete_audio_pending`; never shorten a partial state to `complete`.
