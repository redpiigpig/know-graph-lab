# Greek reader — handoff, 2026-08-27

Written so another session can pick this up cold. Read
[`greek-reader-contract.md`](greek-reader-contract.md) first; this file records
where the work actually stands, not what it should eventually be.

## Where it stands

The two-volume reader is **built end to end and both volumes pass the release
validator, 22/22 and 19/19**. Print masters and PDFs are rendered and inspected.
What is left is audio, and the root cause of one appendix defect.

| Layer | State |
|---|---|
| 2,000-word curriculum | ✅ NT 500 + LXX 500 + patristic 1000, disjoint, 50 × 20 per volume |
| Traditional-Chinese glosses | ✅ 2,000/2,000, keyed by lemma |
| Transliteration | ✅ 2,000/2,000 (Mounce's own 500, rule-generated 1,500, both labelled) |
| 上冊 50 chapters | ✅ 1,413 verses, 26,115 words, Chinese complete |
| 下冊 50 readings | ✅ 2,598 segments, 67,576 words |
| 200 memory units | ✅ selected, Chinese complete, review recorded |
| Word-by-word layer | ✅ 4,216 distinct units / 4,543 ids, ~100,400 glossed words |
| 5 appendices, 625 entries | ⚠️ curated tables 220/220; names 291/405 with Chinese. All five print grouped by category (`PRINT_ORDER`), and the same grouping backs `/original-readers/grc-lessons/tables`. 114 names remain 待歸類. |
| Chrysostom liturgy | ✅ 332 steps, 下冊 only |
| Master | ✅ `greek-reader-two-volumes.json`, `content_complete_layout_pending` |
| Validator | ✅ `--volume 1` 22 PASS, `--volume 2` 19 PASS |
| Print masters | ✅ vol1 521 pp, vol2 1,184 pp; every page 182×257 mm, all fonts embedded, no replacement characters, no blank pages. Grew on 2026-08-27 when each lesson's reading moved to its own page and the appendix gained per-category sections. |
| Web reader | ✅ two volumes, lesson key `v1-12`; appendix page at `/original-readers/grc-lessons/tables`; tests pass; production build passes |
| Release hashes | ✅ `release-hashes.json`, 19 artifacts |
| Audio | ⛔ `not_recorded`; TTS substitution forbidden |
| Appendix cards | ✅ 511 cards, `output/flashcards/greek-flashcards-appendix.docx` — all five tables, sectioned by category |

## What is genuinely left

1. **Audio.** The only release gate that no amount of building can clear. The
   profile is frozen (Mounce standard Erasmian; Byzantine on its own track, never
   mixed) and the master truthfully says `not_recorded`.
2. **The 信望愛 naming route takes the wrong line.** This is the live defect.
   Reading all 340 named appendix entries turned up 49 that were not names at
   all: the Strong's dictionary's *definition* where the name should be
   (Ἄζωτος → 「非利士人的五個重」, Σήμ → 「閃的意思是」, Νηρ → 「空氣」), or a
   different entry's name (Ισμαηλ → 「以色列」, Ιθαμαρ → 「亞倫」).
   `scripts/audit_greek_appendix_names.py --write` has cleared all 49 and
   recorded what each one used to say, so the printed page now reads
   「（中文待定）」 rather than a wrong name — but the parser in
   `fill_greek_appendix_names.py` still needs fixing, and until it is, re-running
   it will put them back.
3. **Two entries are not proper names at all.** ὄζω ("to smell") and
   Ἰουδαϊσμός ("Judaism") reached the names appendix because the ≥80%-capitalised
   rule counts sentence-initial capitals. They are excluded from the lessons as
   names *and* useless in the appendix, so both are currently lost to the
   curriculum.
4. **`data/originalReaders/greek.ts` still describes the old plan.** That file is
   the three-volume planning manifest behind `/original-readers`, not the built
   reader, and it still says a thousand words in groups of fifty.
   `tests/original-readers.test.ts` asserts that shape, so it was left alone
   rather than half-changed. Deciding what the manifest is now for — a plan, or a
   summary of what was built — is the owner's call.
5. **64 appendix names have no Chinese, and that is correct.** Mostly
   deuterocanonical (Ὀλοφέρνης, Μακκαβαῖος, Ἀντίοχος); 信望愛 holds no Chinese
   Maccabees. Never invent one.

## Decisions taken this session that the owner has not confirmed

Say these out loud before treating them as settled:

- **上冊's memory verses follow the half.** Lessons 1–25 draw only from the New
  Testament, 26–50 only from the Greek Old Testament, matching each half's
  chapter. The earlier corpus-floor scheme could hand lesson three a Septuagint
  verse; this replaces it.
- **下冊's memory units are sentences, chosen by the same half rule.** Lessons
  1–25 take sentences from the patristic readings, 26–50 from the church
  documents. A sentence drawn from the lesson's own reading scores a bonus but
  is not required — 25 of the 100 came out that way.
- **The five appendix tables print in both volumes.** They index the whole work,
  and a volume read on its own still needs the numerals and kinship terms.
- **下冊's twelve canon collections come from Greek Wikisource.** The conciliar
  definitions still come from `data/creeds/**`; the canons and four hymns are
  frozen from `el.wikisource.org` with their revision ids and hashes recorded in
  `sources/church-documents/manifest.json`.
- **The Pedalion's commentary is cut out of the canons.** Several of those pages
  print Nicodemus's Ἑρμηνεία under each canon in Katharevousa. It is not the
  ancient canon and it is not Koine, so it is removed and the count of affected
  canons recorded per reading.
- **The five appendix tables print in both volumes**, and a name with no Chinese
  prints 「（中文待定）」 rather than an empty cell.

## Traps that have already cost time

Each of these produced a *confident wrong answer*, which is worse than a
failure, so they are worth knowing before touching the code.

- **A gloss cache keyed by id does not notice that the text changed.** Cutting
  the commentary out of the canons left 226 units pointing at a gloss row for the
  old, longer text, and the run reported "nothing to do" — the id was still
  there. The cache now checks that the cached tokens rebuild the current text.
- **A source's own page can carry modern Greek.** The Laodicea canons came out at
  2,702 words instead of 1,436 because the commentary was being read as canon,
  and a sentence of Katharevousa reached the memory units before anyone looked.
- **The raised dot is a semicolon, not a full stop.** Splitting sentences on
  ἄνω τελεία cut the canons into clauses.
- **Two verses are not a sample.** The name-alignment route accepted any Chinese
  run that appeared in two of two sampled verses, which is how Ἡμὰθ came to be
  named 「我們」.
- **A crosswalk that silently skips is worse than one that fails.** The RCUV
  export dropped any book missing from its own code table without a word, and
  449 verses reached the master with no Chinese; the cause surfaced seven
  chapters downstream. It now raises.
- **Septuagint Jeremiah is a different book from chapter 26 on.** LXX 38 is MT
  31. Five Septuagint chapters (25, 29, 30, 32, 51) split across two Hebrew ones
  and are refused rather than approximated; Proverbs is refused from 24:23 on
  for the same reason.
- **The Chinese Bible numbers Jonah the English way.** Septuagint Jonah 2:1 is
  和合本修訂版 1:17, and the whole chapter runs one number ahead after that.
- **A gloss layer keyed by ordinal shifts silently.** Lifting the proper names
  into the appendix renumbered the list; the layer is keyed by lemma now.
- **Surface matching cannot see inflection.** The first sentence selector matched
  printed forms against dictionary headwords and averaged one hit per sentence,
  leaving eight lessons unable to fill their slots. It resolves each form through
  the Koine lexicon first.
- **Wikisource templates are not all decoration.** The whole Akathist sits inside
  one `{{block center|<poem>…}}`; stripping templates wholesale left three header
  rows where 370 lines of hymn should have been.
- **Morpheus is Attic-first.** Built on it alone, the Septuagint's top words came
  out σός, εἶπον, ὑμός, γίγνομαι, χρύσεος — Classical headwords for words Mounce
  already taught. The Koine lexicon must be consulted before it, always.
- **Accent-blind folding hides words.** `fold` maps ἕξ "six" and ἐξ "out of" to
  the same key, and εἷς to the same key as εἰς; the commoner word takes every
  occurrence and the numeral vanishes. Hence `exactForms`.
- **Folded comparison of unfolded patterns silently no-ops.** The Attic bridge
  rewrote `γιγν→γιν` against accented lemmas, where the substring "γιγν" never
  occurs. It ran for several builds doing nothing.
- **Substring matching finds names inside other words.** Aligning τυρ against
  verse text matched μαρτύρομαι and gave Tyre the Chinese 「見證」. Match at word
  boundaries.
- **Morpheus lower-cases its headwords**, so Πολύκαρπος and Εἰρηναῖος look like
  common adjectives. Only the corpus's own capitalisation identifies them.
- **Swete indexes editorial markers as words.** `[1]` at Proverbs 8:21 is a
  subdivision number, not Greek. Digits-only brackets are editorial; brackets
  with Greek are restored text and stay.
- **The deuterocanon's Chinese is not uniform.** The 1933 Anglican edition has no
  Maccabees, Susanna's Greek and Chinese follow different recensions (60 vs 64
  verses), and Baruch 3 differs by one verse. Withhold and label; never align two
  texts that are not the same text.

## Owner decisions in force

- Traditional Chinese everywhere; 「‧」 as the interpunct.
- 詞庫 `name_recommended` is absolute. Never overrule it, never invent a name.
- Deuterocanonical Chinese: 香港聖公會 (信望愛 `c1933`); 思高 only as a labelled
  fallback. The 1933 book names stay (多比傳／猶滴傳／所羅門智訓／便西拉智訓).
- Textus-Receptus spelling divergences: the textbook's spelling wins.
- Pseudepigrapha are self-translated and labelled 自譯.
- The four curated appendices *may* overlap the lessons — they are a cross-index.
  Only the names are kept disjoint. The owner was told this and did not object;
  ask before changing it.
- The vocabulary must stay Koine. If σός, εἶπον, γίγνομαι, χρύσεος or ὑμός
  appears at the top of a frequency list, the Koine lexicon is not being
  consulted first — that is the symptom, every time.

## Run order

```
python scripts/build_greek_koine_lexicon.py --write
python scripts/build_greek_lemma_index.py --write
python scripts/build_greek_vocabulary_2000.py --write
python scripts/build_greek_vocab_glosses_2000.py
python scripts/fetch_greek_church_documents.py --write
python scripts/build_greek_scripture_plan.py --write
python scripts/build_greek_patristic_plan.py --write
python scripts/build_greek_liturgy.py --write
python scripts/select_greek_memory_verses.py --write
python scripts/select_greek_memory_sentences.py --write
python scripts/export_reader_rcuv2010_greek.py --write
python scripts/export_reader_fhl_deuterocanon.py --write
python scripts/build_greek_appendices.py --write
python scripts/fill_greek_appendix_names.py --write
python scripts/align_greek_names_chinese.py --write
python scripts/fill_greek_appendix_glosses.py --write
python scripts/audit_greek_appendix_names.py --write
python scripts/build_greek_interlinear.py --prune --workers 5
python scripts/build_greek_reader_data.py --write
python scripts/record_greek_memory_review.py --write
python scripts/build_greek_reader_data.py --write
python skills/build-original-language-reader/scripts/validate_reader_release.py \
  --master output/source-cache/original-readers/greek-full/greek-reader-two-volumes.json \
  --language grc --volume 1 --lessons 50 --vocabulary-per-lesson 20 \
  --vocabulary-total 1000 --scripture-lessons 50
python scripts/build_greek_full_reader.py
```

Then render each volume to PDF and inspect it. The managed renderer needs
`pdf2image`, which this checkout does not have; LibreOffice's console binary does
the job on its own, and PyMuPDF answers the gate questions:

```
"C:/Program Files/LibreOffice/program/soffice.com" --headless   -env:UserInstallation=file:///C:/tmp/lo_grc --convert-to pdf   --outdir output/original-readers output/original-readers/greek-original-reader-vol1.docx
```

Give each volume its own `UserInstallation` profile, or the second conversion
waits on the first. A volume takes two to six minutes.

Each takes `--write` (or `--workers`); without it they print and change nothing.
`build_greek_appendices.py` and `align_greek_names_chinese.py` need
`SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` from `.env`, and reach 信望愛 and
和合本修訂版 over the network — both cache to disk, so a second run is fast.

`scripts/render_and_check_reader_pdfs.py` now wraps both halves of that: it drives
LibreOffice with a fresh profile per file and then checks page geometry, embedded
fonts, U+FFFD and blank pages. `--only greek-original-reader-vol1` renders one.

## Volume 2 needs `--scripture-lessons 0`

The validator's default assumes the Hebrew shape, where every lesson reads a
Bible chapter. Volume two is the patristic volume and reads none, so the default
`--scripture-lessons 50` fails two checks — `reading-allocation` and
`declared-counts` — on a book that is correct. Pass `0` and it reports 19 PASS.
This is a flag, not a defect; do not "fix" the master to satisfy the default.
