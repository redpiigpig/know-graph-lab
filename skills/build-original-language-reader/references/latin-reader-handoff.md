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
| Chinese glosses | `.../gloss-zh.json` | 1,999 of 2,000 |
| Memory units | `.../memory-units.json`, `memory-selection-review.md` | 上冊 79/100, 下冊 100/100, unreviewed |
| Contract | `references/latin-reader-contract.md` | frozen |
| Gate | `scripts/verify_latin_reader.py` | hard checks pass |
| Liturgy | `.../liturgy.json` | 10 formulas + the whole Ordo Missae, 1,722 words |
| Readings' Chinese | `.../readings-zh.json` | in progress; see below |
| Print | `output/original-readers/latin-original-reader-vol{1,2}.{docx,pdf}` | 上冊 267 頁, 下冊 577 頁 |
| Web | `/original-readers/lat-lessons`, API under `server/api/original-readers/lat-lessons/` | requireAuth + noindex |
| Audio | `output/original-readers/audio/latin/manifest.json` | 189 draft clips, gitignored |

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
python -X utf8 scripts/build_latin_memory_units.py --write
python -X utf8 scripts/verify_latin_reader.py
```

The downloads (`latVUC`, the six UD treebanks, Whitaker's WORDS, The Latin
Library corpus, the Collins PDF) are gitignored and must be re-fetched;
`fetch_latin_church_corpus.py` is resumable and keeps a manifest with per-file
checksums.

## What does not exist yet, stated plainly

1. **Memory units: 下冊 is complete at 100/100, 上冊 stands at 79/100.**
   Built by `scripts/build_latin_memory_units.py`, reviewable in
   `memory-selection-review.md`; none of them has been read by a human yet.
   The upper volume's gap is concentrated in lessons 1–12, and it is a real
   constraint rather than a bug: a lesson that has taught twenty words cannot
   read a complete Vulgate verse. The obvious filler is the short liturgical
   formulas — Kyrie, Amen, Deo gratias, the petitions of the Pater noster — but
   the Greek release's owner explicitly barred liturgy from 上冊, so whether
   that bar applies here is the owner's call and was left alone.
2. **The word-by-word gloss layer over the readings is not built.** 24,288 words
   in 上冊 alone. Nothing has been tokenised or glossed at token level.
3. **Forty-five of the fifty lower-volume readings need a Chinese translation,
   not twenty-three.** The earlier count trusted that a `-chinese.txt` file
   beside the Latin meant a parallel translation existed. It does not. Of the
   twenty-seven files that exist: three are the placeholder 「⏳ 中譯待補」,
   fifteen are selections from the Denzinger anthology (the Sacrosanctum
   Concilium file holds *one* entry out of a hundred-and-thirty-paragraph
   constitution and says so in its own header), four are real translations that
   number nothing, and five are real translations that number their sections.
   Only those five can be set beside the Latin, matched on the section number.
   The Chinese for the rest is being produced and is not finished.

   Where the five are aligned, the join is section to section: the published
   Chinese for §12 sits beside the Latin paragraph that opens §12, and the
   continuation paragraphs of that section carry none. Nostra Aetate therefore
   shows Chinese on 5 of its 104 paragraphs, which is right — it has five
   sections — but it reads unevenly, and a future pass could set the Chinese
   against the whole section rather than its first paragraph. `translate_latin_readings_zh.py` is
   resumable; re-run it until every unit reports all its segments. It runs at
   roughly two minutes a segment while the Gemini pool is rate-limited, so it is
   an overnight job, not a coffee-break one. Everything it produces is labelled
   自譯 and is **not** 《感恩祭典》.
4. **The Ordo Missae's Latin is settled**: Collins's Further Readings 1, which
   prints the post-conciliar ordinary, under the owner's verbal permission for
   this private edition. Its Chinese is part of item 3.
6. **Proper-name Chinese reaches about half the names the printed chapters
   contain**, and none of the rest of the Vulgate's. The alignment
   register only covers what is printed; extending it means printing more
   chapters, not loosening the guard.
6. **Print, web and audio exist as first cuts and none has been proofread.**
   The DOCX/PDF render and the pages load, but nobody has read a page of either.
   The audio is an Italian system voice and the manifest says `draft`: a release
   track is a human voice with reader, rate, cues, checksum and rights recorded.
8. **Glosses were produced by NVIDIA llama-3.1-70b**, not reviewed by a human.
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
- **The second volume starts from the first volume's thousand words**, not from
  zero. Accumulating only 下冊's own vocabulary counted `et`, `sum` and `qui` as
  unknown in patristic prose and cut its memory units from a hundred to two.
- **The repository's curial documents keep their footnote citations inline.**
  Split into sentences, they yield "Dei genetricis, Hom." and "Quam Apostoli
  sententiam S." — references that parse as sentences. Memory-unit selection
  draws only from the Latin Library texts until that apparatus is stripped.
- **"Excerpt" without edges is not a decision.** Marking a reading `excerpt`
  and saying no more let the translator render sixteen thousand words of Vincent
  of Lérins into a book that had budgeted nine hundred.
- **Two readings must not point at the same anthology file.** Six hymns and two
  creeds each pointed at the whole collection, so six readings printed the same
  sixteen hundred words. Cut by anchors, and pick the longest span the anchors
  yield — these files repeat every title in a contents list at the top.
- **The imported layout brings the imported running header.** Every page of the
  first Latin print run said 聖經希伯來文原文讀本.
- **Collins does not label his nouns and verbs.** The gender abbreviation and the
  four principal parts *are* the labels; reading only an explicit field left the
  part-of-speech column empty for most of the book.
- **A `-chinese.txt` file existing does not mean a translation exists.** Three
  different things were sitting under that name, and pairing any of them to the
  Latin by paragraph index printed unrelated text side by side — Sacrosanctum
  Concilium has 362 Latin paragraphs against 11 Chinese ones. Classify the file;
  join on section numbers where both sides carry them; self-translate otherwise.
- **Collins's own English headings sit inside the OCR of his readings.**
  "Further Readings" and "1. The Ordinary of the Mass" were translated as if
  they were liturgical Latin, and the numbered title of the *next* reading is
  where the current one ends: the Ordo Missae was carrying twenty-five lines of
  the Exsultet on its tail before anyone noticed.
- **Eight readings share two source files.** Six hymns are cut out of one
  anthology and two creeds out of another, so a translation cache keyed on the
  source path alone collides eight ways: the six hymns take turns overwriting
  one another and the page prints whichever landed last. What makes them
  different readings is the section anchor, so the anchor belongs in the key.
- **A section number is not always tight against its point.** Dignitatis
  Humanae prints 「2 . Haec Vaticana Synodus declarat」, and a pattern demanding
  the digit and the period be adjacent matched nothing and paired no Chinese at
  all — silently, because a reading with no Chinese looks the same as one whose
  translation has not arrived.
- **OpenCC `s2t` is not a test for simplified Chinese.** It rewrites 祢 to 禰,
  and 祢 is the Catholic honorific this reader's translations are full of; it
  also rewrites 台, 床, 群, 峰. A gate that treats "the converter changed
  something" as proof of simplified text rejects the project's own vocabulary.
- **Do not re-scan a corpus per lookup.** Asking for one name's commonest
  spelling by scanning three million words, five hundred times, is why the first
  appendix build never finished.
