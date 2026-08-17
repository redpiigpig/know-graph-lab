---
name: build-original-language-reader
description: Produce, resume, adapt, or audit complete private-use B5 original-language readers for Biblical Hebrew, Biblical or Patristic Greek, and Ecclesiastical Latin. Covers a 50-lesson vocabulary curriculum, textbook-specific transliteration and pronunciation, typed biblical proper names, 100 memory units, full Scripture chapters and complete prayers or articles, language-specific appendices, authenticated noindex web readers, aligned pronunciation audio, source-rights manifests, DOCX/PDF generation, and deterministic plus full-page visual QA. Use for full production rather than samples, templates, vocabulary-only lists, or general language questions.
---

# Build complete original-language readers

Produce one authoritative data master and derive print, web, audio, and QA artifacts from it. Never treat a sample, placeholder manifest, old render, or partially populated reader as complete.

## Load the required references

Read these files for every production run:

- `references/release-contract.md`
- `references/data-model.md`
- `references/rights-and-source-freeze.md`
- `references/qa-gates.md`

Read the selected language section in `references/language-profiles.md`.

Read `references/layout-web-audio.md` before producing DOCX, PDF, online pages, or audio.

When working in `know-graph-lab`, read `references/know-graph-lab-baseline.md`. Treat all paths and counts there as checkout-specific facts that must be verified live.

## Run the workflow in order

1. Inspect the workspace, dirty files, current master, previous QA reports, and running process ownership. Preserve unrelated work.
2. Freeze a release configuration: language, exact lesson/count contract, textbook vocabulary order, extension rule, source editions, Traditional-Chinese Bible edition and variant, pronunciation profile, appendices, rights status, and output paths.
3. Freeze every source separately. Record ancient work, modern edition, digital transcription, translation, recording, and font rights rather than collapsing them into one license claim.
4. Build the vocabulary master:
   - Preserve the named textbook's verified order first.
   - Do not invent a missing textbook order.
   - Extend only by a documented corpus-frequency rule after the textbook ends.
   - Let the textbook set lesson size. While the named textbook lasts, one lesson is one textbook chapter with that chapter's real count — uneven by design. Do not slice its stream into equal quotas; that hides the progression the learner is following.
   - Spread only the post-textbook extension evenly over the remaining lessons, and never let a fixed words-per-lesson assumption survive in validators, headings, labels or tests.
   - Preserve intentional homographs as separate lexical entries.
   - Store textbook-specific transliteration, source evidence, part of speech, frequency, and typed person/place/people/divine-name metadata.
   - Review every Traditional-Chinese gloss. Reject blanks, generic categories, English leakage, and machine placeholders.
5. Build immutable source-text layers and separate learner-facing display layers. Never silently overwrite ketiv, pointing, breathings, macrons, punctuation, or source orthography.
6. Use 《和合本修訂版》（2010） for every Traditional-Chinese Bible quotation in the current project. Freeze the selected variant explicitly. Do not fall back to ChiUn/CUV1919 or another version. Route all MT/LXX/Vulgate numbering differences through one shared crosswalk.
7. Build 100 memory units after vocabulary is fixed:
   - Generate a candidate pool using lesson-word overlap, cumulative coverage, grammatical completeness, and memorability.
   - Reject lists, fragments, near-duplicates, census material, and misleading verse-number joins.
   - Require exactly two unique, reviewed units per lesson.
   - Save candidate scores and the human-review decision record.
8. Build full readings, not summaries disguised as readings. Preserve the approved difficulty order. The default release contract is 25 complete Scripture chapters plus 25 complete prayers or articles; appendices do not silently replace those 50 readings.
9. Build the word-by-word layer over every running-text unit before layout:
   - Tokenise the printed text, gloss each token with its contextual Traditional-Chinese meaning, and give every unit without a published translation a whole-unit rendering as well.
   - Gate on gloss-count equals token-count, on blank glosses, and on source-script or Latin leaking into a gloss.
   - Cache per unit so a partial run resumes instead of restarting, and re-run rounds until nothing is missing.
   - Never ship a reading whose Chinese is only one whole-verse translation line.
10. Add each language-specific terminal section. For Hebrew, keep the complete fifteen-step Haggadah separate from the 25 prayer/article readings.
11. Assemble one master JSON. Fail on incomplete counts, IDs, ordering, translations, diacritics, transliteration, proper names, sources, rights metadata, or placeholder text.
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
