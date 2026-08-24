# Ecclesiastical Latin reader — where this release actually stands

Written 2026-08-25 at the end of the first build session. Everything below was
run and its numbers read off the artifacts, not estimated. Verify live before
relying on any of it.

## What exists

| Artifact | Path | State |
|---|---|---|
| Vocabulary master | `data/originalReaders/vocabulary/latin-2000.json` | 上冊 1,000 + 下冊 1,000, all with dictionary forms |
| Proper names | `data/originalReaders/vocabulary/latin-proper-names.json` | 15, lifted out of Collins |
| Appendices | `data/originalReaders/vocabulary/latin-appendices.json` | 10 tables |
| 上冊 reading plan | `output/source-cache/original-readers/latin-full/scripture-plan.json` | 50 chapters, 1,514 verses, 24,288 words |
| 上冊 Chinese | `.../sigao-zh.json` | all 50 chapters, 思高譯本 |
| 下冊 reading plan | `.../church-plan.json` | 50 readings, 15 complete / 35 excerpt |
| Chinese glosses | `.../gloss-zh.json` | see below |
| Contract | `references/latin-reader-contract.md` | frozen |
| Gate | `scripts/verify_latin_reader.py` | hard checks pass |

Run order from a clean checkout:

```
python -X utf8 scripts/build_latin_lexicon.py --write
python -X utf8 scripts/ocr_collins_vocabulary.py --pdf <Collins.pdf>
python -X utf8 scripts/build_latin_vocabulary_2000.py --write
python -X utf8 scripts/build_latin_scripture_plan.py --write
python -X utf8 scripts/export_reader_sigao.py --write
python -X utf8 scripts/build_latin_church_plan.py --write
python -X utf8 scripts/build_latin_appendices.py --write
python -X utf8 scripts/gloss_latin_vocabulary_zh.py --write
python -X utf8 scripts/verify_latin_reader.py
```

The downloads (`latVUC`, the six UD treebanks, Whitaker's WORDS, The Latin
Library corpus, the Collins PDF) are gitignored and must be re-fetched;
`fetch_latin_church_corpus.py` is resumable and keeps a manifest with per-file
checksums.

## What does not exist yet, stated plainly

1. **The 100 memory units per volume are not built.** The release contract calls
   for two per lesson; none are selected. This is the largest missing piece of
   the curriculum proper.
2. **The word-by-word gloss layer over the readings is not built.** 24,288 words
   in 上冊 alone. Nothing has been tokenised or glossed at token level.
3. **23 of the 50 lower-volume readings have no Chinese.** They are the Latin
   Library patristic texts; the 27 that do have Chinese are the repository's own
   papal and conciliar documents. Self-translation must be labelled `自譯`.
4. **The Ordo Missae is `source_pending`.** The current Missale Romanum is under
   the Holy See's copyright and no authorized edition has been recorded. Do not
   substitute a transcription found online.
5. **Proper-name Chinese reaches 55 of the 117 names the fifty chapters actually
   print** (47%), and 0 of the 468 names elsewhere in the Vulgate. The alignment
   register only covers what is printed; extending it means printing more
   chapters, not loosening the guard.
6. **No DOCX, PDF, web reader, or audio.** Nothing has been laid out.
7. **Glosses were produced by NVIDIA llama-3.1-70b**, not reviewed by a human.
   The contract requires every Traditional-Chinese gloss to be reviewed before
   release; that review has not happened.

## Traps already fallen into, so they are not repeated

- **Lesson numbers are not stable identifiers.** They come from the difficulty
  sort and move whenever the vocabulary changes. Keying the Chinese export to
  them paired Exodus 3 with John 17 and dropped proper-name alignment from 56
  matches to 1, silently. Key on book and chapter.
- **`engs=Gen` returns Romans.** 信望愛's endpoint answers an unrecognised book
  with its previous answer, status `success`. `chineses=多` returns 弟鐸書 and
  labels it `chineses: 多`, so guarding the field you supplied does not help.
- **Capitalisation does not identify a proper name.** Collins capitalises `Deus`,
  the nationality adjectives and the liturgical nouns. A capitalisation rule sent
  the second commonest word in the Vulgate to the appendix.
- **The OCR sometimes returns a whole dictionary line as the headword**, and does
  it most often on the closed-class words: `qui, quae, quod` and `quis, quid`
  arrive whole. Unfixed, the commonest relative pronoun in Latin is absent from
  the reader and reappears as an untaught word in the second volume.
- **Fold, do not strip macrons, when comparing across the volumes.** The
  treebanks spell with classical `u`/`i` and Collins with `v`/`j`; a macron-only
  comparison let 58 words be taught twice under two spellings.
- **Some duplicates are real words.** `occīdō` "kill" and `occidō` "set",
  `praedicō` "proclaim" and `praedīcō` "foretell" are separate lexemes that only
  a macron separates. Compare whole dictionary lines: real pairs differ in their
  principal parts, a doubled OCR entry does not.
- **A two-strike quota rule must count full key sweeps, not individual keys.**
  Aborting on the second key's 429 stops a run that had a live lane two keys
  further down; on a busy night the seventh key is the one that works.
- **Do not re-scan a corpus per lookup.** Asking for one name's commonest
  spelling by scanning three million words, five hundred times, is why the first
  appendix build never finished.
