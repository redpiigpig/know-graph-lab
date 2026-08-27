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
| Chinese glosses | `.../gloss-zh.json` | 2,000 of 2,000 |
| 下冊 Chinese | `.../readings-zh.json` | 45 of 45 readings, 792 segments, 自譯 |
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
   All forty-five have now been translated — 792 segments — and every one is
   labelled 自譯.

   Where the five are aligned, the join is section to section: the published
   Chinese for §12 sits beside the Latin paragraph that opens §12, and the
   continuation paragraphs of that section carry none. Nostra Aetate therefore
   shows Chinese on 5 of its 104 paragraphs, which is right — it has five
   sections. The continuation paragraphs are no longer blank: they carry a
   self-translation, so the page shows the published wording where a section
   opens and 自譯 for the rest. `translate_latin_readings_zh.py` is
   resumable; re-run it until every unit reports all its segments. It runs at
   roughly two minutes a segment while the Gemini pool is rate-limited, so it is
   an overnight job, not a coffee-break one. Everything it produces is labelled
   自譯 and is **not** 《感恩祭典》.
4. **The Ordo Missae's Latin is settled**: Collins's Further Readings 1, which
   prints the post-conciliar ordinary, under the owner's verbal permission for
   this private edition.
5. **The liturgical Chinese is filled, and its fixed responses carry the
   received wording.** The owner asked on 2026-08-27 for every 〔中譯待補〕 to be
   translated; all 328 were, and the book now prints no gap. How they were
   filled is the part to check:

   - **66 lines are the received wording**, supplied from a table in
     `scripts/fill_latin_reading_gaps.py` and marked `received-wording` —
     「因父、及子、及聖神之名」, 「請舉心向上」, 「我們全心歸向上主」, the Pater
     noster, the Sanctus. A machine renders these unevenly: the same
     `Sursum corda` came back as 「舉心向上」 once and 「心向上」 the next time,
     `Habemus ad Dominum` became 「我們有向主」 which is not Chinese, and
     `Lectio sancti Evangelii secundum N.` was expanded into 「聖若望福音」,
     inventing an evangelist where the Latin prints a placeholder.
   - The rest is self-translated behind a gate that rejects invention: a
     versicle must return the same single V./R. marker, must not name a minister
     the Latin does not name, and must not become several sentences where the
     Latin is one line. The gate applies to versicles only — a rubric's whole
     job is to say who does what, and holding it to the same rule rejected every
     rubric in the Mass.

   **Outstanding:** the 66 received lines are written out here rather than
   copied from 《感恩祭典》. Check them against the book before printing.
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

## Closing the last gaps (2026-08-27)

- **Every reading and every liturgical line now carries Chinese.** 314 lines were
  filled: 68 from the received wording of the Mass, 59 rendered structurally as
  subscriptions, the rest self-translated and gated. `〔中譯待補〕` appears
  nowhere in either volume.
- **The signature list is rendered, not translated.** `subscription_zh()` in
  `fill_latin_reading_gaps.py` maps a closed table of offices — 樞機, 總主教,
  領銜主教, 宗主教, 首席總主教, 永久署理 — and keeps the personal name and the see
  in Latin. Fifty-eight of the fifty-nine match the `Ego …` shape; the odd one
  out is the secretary's countersignature.
- **A repetition gate now runs on every line, apparatus included.** One
  subscription had collapsed into six hundred characters of 聖 and passed every
  other check. It measures the repetition as a share of the line, so the fivefold
  parallelism of Deus Caritas Est still passes.
- **The glosses were in the wrong register.** Eleven headwords came back in
  Protestant Chinese — 教皇, 使徒, 上帝, 祭司, 聖靈降臨節, 道成肉身 — against the
  Studium Biblicum readings on the facing page. `CATHOLIC_TERMS` in
  `gloss_latin_vocabulary_zh.py` corrects them after the model, and the engine
  field records `catholic-usage` so the override is visible.
- **上冊 memory units are 100/100.** Four of the ten opening formulas are printed
  as one block — the Confiteor, the Our Father, the Gloria, the Creed — so each
  offered a single candidate longer than any unit may be, and those lessons came
  out empty. `split_formula()` cuts them at sentence boundaries and marks the
  pieces `reading-has-chinese`, because the published Chinese translates the
  whole block and cannot travel with a clause. Two smaller fixes went with it:
  the V./R. marker is apparatus and must not count against readability
  (「R. Amen.」 was being read as half unintelligible), and two petitions of one
  formula are allowed to resemble each other, since that repetition is the text.
- **Proper-name Chinese is 389/585**, up from 53. The route is unchanged —
  Studium Biblicum's own underlining, aligned verse by verse — and the gain came
  from fetching the 154 chapters where the unnamed names actually occur. The
  remaining 196 do not appear in any chapter the alignment can settle; a blank is
  the correct state for them.

## Layout unified and the appendix uncapped (2026-08-27, second session)

- **The two volumes now match the Hebrew reader's structure**, which is the
  house standard: banner cover, eyebrow → 課次 → Heading 1 → gold rule at each
  lesson opener, section headings at H2 (14 pt) through real Heading styles, and
  **each lesson's reading on its own page**. Sizes already came from
  `build_hebrew_full_reader`; what differed was structure. `heading()` now maps
  its size argument to a Word outline level, so the PDF gains bookmarks too.
  Volume one 332 pp, volume two 489 pp, both 182×257 mm throughout.
- **The 200-row appendix cap is gone.** It was there to hold the page count
  down, and it silently withheld 385 of the 585 upper-volume proper names — an
  appendix you cannot look a name up in is not worth the paper it saves.
- **The proper-name tables print grouped by category**, nine of them, in
  `PRINT_ORDER` from `scripts/proper_name_categories.py`.
- **281 of 585 upper-volume names are still 待歸類.** The classifier reads
  registers plus Strong's definition phrasing (see `strongs_name_kinds.py`); what
  is left is largely inflected forms the Vulgate frequency pass captured as they
  stood — `Jordanem`, `Jerosolymis`, `Levitarum`, `Pharaonem` — plus case and
  spelling duplicates (`Levites`/`Levitæ`, `iordanes`/`Jordanem`). Normalising
  that table to nominatives is the real fix and belongs to whoever owns it.
- **下冊's `modernNames` table is not a proper-name table.** All 400 rows lack
  Chinese, and the list contains abbreviations (`Psal`, `Joan`, `Virg`, `W`),
  adjectives (`Latinus`, `Graece`, `Anglorum`) and common nouns (`Cardinalis`,
  `Redemptoris`). It prints, because printing what the data says is honest, but
  it produces no flashcards and should be rebuilt at source.

### 兩件會再咬人的事

- **`build_latin_appendices.py` 會整檔重生 `latin-appendices.json`，把 `category`
  欄整批帶走。** 一個晚上發生兩次，兩次都是打開紙本才看到附錄又變成沒有分節的一長
  串——檔案還在、還能解析、585 條一條不少，只是欄位沒了，沒有任何錯誤。重生後跑
  `python scripts/classify_proper_names.py --reapply --write` 就好：它只從帳本
  `data/originalReaders/vocabulary/proper-name-categories.json` 把分類補回去，不
  連登錄、不重判。看得出來是這件事的兩個徵兆：檔案的 `generatedOn` 是今天而你自己
  那一輪是幾小時前，而且欄位是**每一列**都不見，不是難判的那幾列不見。

- **附錄那幾張表原本印的是英文。** 〈數字、羅馬數字與度量衡〉〈親屬稱謂〉〈羅馬
  曆、月份與聖經節期〉建的時候只帶了 Whitaker 的英文釋義，而印表那行寫成
  `zh or glossZh or glossEn`——沒有中文就退到英文。一本繁體中文讀本的附錄整頁
  `mother's brother`、`the day before the Kalends`。`gloss_latin_appendices_zh.py`
  補上了：先用五十課詞表已審過的中文（644 條），剩下 548 條才問模型，並沿用
  `CATHOLIC_TERMS` 修正新教用語。八張表現在都是 100%：數字 81、親屬 48、曆法 43、
  動詞主要部分 841、職分 64、禮儀年 32、文獻 41、經院 42。印表那行也改掉了，缺中文
  就印「（中文待補）」而不是退到英文——退而求其次的預設值會把資料的缺口藏起來。
