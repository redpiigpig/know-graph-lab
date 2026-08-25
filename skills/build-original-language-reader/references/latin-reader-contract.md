# Ecclesiastical Latin reader — frozen release contract

Frozen 2026-08-25 for `know-graph-lab`. Verify every path and count live before use.

## Curriculum

Two volumes of fifty lessons, twenty words each — two thousand words in all, the
same shape the Greek reader was re-frozen to on 2026-08-24.

| Item | Frozen value |
|---|---|
| Volumes | 2. 上冊《武加大譯本》, 下冊《從教父到教廷》 |
| Lessons | 50 per volume, **exactly 20 words each** |
| Vocabulary | 2,000 entries, the three sources disjoint |
| 上冊 | 1,000 words in **Collins's own order**, units 1–35, proper names lifted out and the slots backfilled |
| 上冊 readings | **10 short liturgical formulas, then 40 complete Vulgate chapters** (20 New Testament, 20 Old Testament and deuterocanon), the chapters in canonical order |
| 下冊 1–25 | Collins's overflow, then patristic and medieval corpus frequency; one patristic or medieval reading per lesson, **in chronological order** |
| 下冊 26–50 | modern curial and liturgical corpus frequency; one Trent-or-later reading per lesson, **in chronological order** |
| Ends with | the complete ordinary-time Ordo Missae, in 下冊 only, outside the fifty readings |
| Authorization | the owner attests verbal permission for this private-use edition (2026-08-25); recorded as an attestation, not a written licence |
| Builders | `scripts/build_latin_vocabulary_2000.py`, `build_latin_scripture_plan.py`, `build_latin_church_plan.py`, `build_latin_appendices.py` |

### The textbook is Collins, and its order is not a frequency ranking

`A Primer of Ecclesiastical Latin` (John F. Collins, CUA Press, 1985) is the
standard seminary text and the direct counterpart of Mounce and Pratico–Van Pelt
in the other two readers. Its publisher's own scope — "the Latin of Jerome's
Bible, of canon law, of the liturgy and papal bulls, of scholastic philosophers,
and of the Ambrosian hymns" — is exactly this reader's span.

**The order comes from the back matter, not from the thirty-five units.** The
primer's `Latin-English Vocabulary` (printed pp. 411–438) collects every unit
vocabulary into one alphabetical list and stamps each entry with the unit that
introduced it — `ambo, ambonis, m. lectern, ambo (15)`. Twenty-eight pages
therefore hold the whole curriculum, and reading them is both cheaper and less
error-prone than stitching thirty-five scattered sections back together. Entries
marked `(E20)` were glossed in an exercise only and are excluded from the
lessons.

**Never re-sort Collins into frequency order.** He introduces `missa`, `papa` and
`ecclesia` in unit 1 because those are what a church Latin reader meets first,
not because they outrank `et` and `sum`. A frequency sort buries them and
teaches a different language.

### The PDF text layer cannot supply the forms

Collins prints macrons throughout and says so in his first unit. The scanned
PDF's text layer destroys them: `ōrō, ōrāre` arrives as `ord, drare`, `amō` as
`amb`, `impōnō` as `impend`, `subeō` as `subed`, `cōnsōlō` as `cOnsolO`. The
text layer is therefore usable **only** to cross-check which entries exist and in
what order; every printed form is re-read from the page image by
`scripts/ocr_collins_vocabulary.py`.

That script sweeps all seven Gemini keys before counting a quota failure, and
falls back to Anthropic vision when every key is spoken for. On a night when the
overnight fleet holds the Gemini pool, all seven answer 429 or 503 at once and
the fallback is the only thing that finishes the run — but a two-strike rule that
aborts on the *second key* rather than the second full sweep will stop a run that
had a live lane two keys further down.

## Lemma registers, in a fixed precedence

Latin has the Greek reader's Attic trap in a different shape. An analyser trained
on Caesar and Cicero lemmatises Jerome's late spellings into Classical headwords
or fails on them; but a lexicon built from the Vulgate *alone* strands the lower
volume, because Jerome barely uses `scilicet`, `praesertim` or `res` and a
scholastic page comes back two-thirds unresolved.

So three registers are read separately and merged in this order, never
rearranged. Where two tag the same form, the earlier one wins.

| Register | Source | Tokens | Governs |
|---|---|---:|---|
| `vulgate` | UD_Latin-PROIEL, Jerome's Vulgate sentences only | 109,517 | 上冊 |
| `church` | UD_Latin-ITTB (Aquinas), UD_Latin-LLCT (charters), UD_Latin-UDante | 641,753 | 下冊 |
| `classic` | PROIEL's Caesar/Cicero/Palladius, Perseus, CIRCSE | 96,049 | last resort |

Built by `scripts/build_latin_lexicon.py --write`. Resolution measured on the
frozen corpora: **New Testament 98.7%, Old Testament 88.3%, church documents
84.9%**; the Old Testament remainder is almost entirely proper names, and the
church remainder is almost entirely citation apparatus (`Cfr`, `Matth`, `Alloc`).

`scripts/latin_lemmatiser.py` adds a bridge layer over that inventory —
enclitic stripping (`dixitque` → `dixit`), Clementine/PROIEL orthography
(`Israël`/`Israhel`, `ejus`/`eius`), and a named list of medieval spellings
(`quum`/`cum`, `michi`/`mihi`, `nichil`/`nihil`). **Every rewrite is checked
against the inventory before it is accepted**, so the bridge can only ever land
on a word actually attested; the generic rules that would generate those
spellings (`qu`→`c`, `oe`→`e`) destroy real words and are not used.

Dictionary forms for the lower volume come from Whitaker's WORDS, with the
`Support_Utils.Dictionary_Form` composer ported to
`scripts/latin_dictionary.py`. Whitaker's spelling is taken as the headword,
because the treebanks print classical `uenerabilis` and `ueluti` while the upper
volume prints Collins's `venerabilis`, and one reader cannot spell the same
language two ways across its two volumes. His `AREA` and `AGE` columns mark
ecclesiastical and post-classical vocabulary without anyone writing that list by
hand.

## Source freeze

| Layer | Frozen source | Rights |
|---|---|---|
| Vulgate Latin | Biblia Sacra Vulgata Clementina, eBible.org `latVUC` USFX transcription, sha256 `e8202b9f…f141fdc` | public domain as declared by eBible.org |
| Traditional-Chinese Bible | 思高譯本, 思高聖經學會網上版 (`sbbible.dsbiblecentre.org`) | © 思高聖經學會; private-authorized, non-redistributable |
| Patristic and medieval Latin | The Latin Library, 193 texts, 1.63M words, per-file URL and sha256 in `latin-church/manifest.json` | public-domain works in freely offered transcriptions |
| Papal and conciliar Latin | this repository's `data/encyclicals` (695 documents) and `data/creeds` (60), 1.66M words, 753 with an existing Chinese parallel | as recorded per document |
| Lemma treebanks | UD_Latin-{PROIEL, ITTB, LLCT, UDante, Perseus, CIRCSE} | CC BY-NC-SA 3.0/4.0 and CC BY-SA 4.0; local build inputs, not redistributed |
| Dictionary | Whitaker's WORDS `DICTLINE.GEN`, 39,335 entries | freely given for any use by the author |
| Ordo Missae | **not frozen.** Missale Romanum, editio typica tertia is under the Holy See's copyright | `source_pending`; no transcription may stand in for an authorized text |

The Clementine Vulgate is the frozen base. Stuttgart and the Nova Vulgata are
different editions and must never be blended into it; 信望愛 carries both
`cvul` and `nvul` and either can be cited as a collation reference only.

### Why the Chinese is not from 信望愛

信望愛 was tried first and abandoned for two reasons.

Its 思高 holding stops at the protocanonical books, so the five deuterocanonical
chapters this reader prints would have had to come from the 1933 Anglican
translation — a second edition inside one volume, under Protestant book names.

And its endpoint answers an unrecognised book with whatever it answered last,
with status `success` and no error of any kind. `engs=Gen` returns Romans 1.
`chineses=多` returns 弟鐸書 — and returns it labelled `chineses: 多`, so a guard
that checks the field it was asked about passes. **Guard on `engs`, the book code
the response carries, never on the field you supplied.**

## 上冊: ten formulas, then forty chapters

The volume opens with the ten short liturgical texts, because a lesson that has
taught twenty words cannot read a Vulgate chapter but can read *In nomine
Patris, et Filii, et Spiritus Sancti* — a sentence a reader of church Latin will
say more often than any verse in the Bible. Complete chapters begin at lesson
eleven.

The formulas run short to long -- nine words of the sign of the cross before a
hundred and seventy of the Creed -- because that gradient is about the texts
themselves.

**No Kyrie.** It is Greek, kept in Greek by the Latin rite, and the owner keeps a
separate Greek reader; a Latin volume that opens on a Greek formula teaches the
wrong book's alphabet. The preface dialogue (*Sursum corda*) takes its place: as
short, as familiar, Latin throughout.

The forty chapters were cut from fifty on a stated principle — first a second
chapter from a book already represented (Mark 4, Luke 24, Acts 17, 1 Cor 15,
Rev 21, Genesis 3, Exodus 20, Psalm 129), then the two whose Chinese cannot sit
beside the Latin verse for verse: Job 38, whose verses this edition transposes,
and Judith 13, where Jerome's recension runs to thirty-one verses against the
Greek tradition's twenty.

### Readings are not chosen to match the vocabulary

Owner's instruction, 2026-08-26: a chapter need not use the words the earlier
lessons taught — what it needs is its Chinese annotated properly. Until then both
volumes were sorted by how much of each reading the reader had already been
taught, and that sort was doing real damage: it scattered the lower volume's
fifteen centuries into a difficulty ladder that put Trent after Vatican II.

So the order is now fixed and meaningful. The upper volume's chapters run in the
Vulgate's own canonical order; the lower volume runs chronologically, from the
Apostles' Creed to *Laudato Si'*, which is the argument the volume was for.
Coverage is still measured and still printed — it tells a reader what to expect
— but it no longer decides anything.

## 上冊: the chapters themselves

Twenty-five New Testament, then twenty-five Old Testament and deuterocanonical,
each half ordered by difficulty on its own — a reader is not asked to take the
Vulgate Old Testament's Hebraic syntax in lesson three because that chapter is
short. Difficulty is computed as unknown-word rate against this reader's own
vocabulary, plus mean verse length; **proper names count as known**, since they
are looked up in the appendix and counting them as unknown makes the genealogies
look like the hardest Latin in the Bible.

1,514 verses, 24,288 words. Built by `scripts/build_latin_scripture_plan.py`,
Chinese by `scripts/export_reader_sigao.py`.

Deuterocanonical coverage: 多俾亞傳 1, 友弟德傳 13, 智慧篇 7, 德訓篇 24, 瑪加伯下 7.

### Ten chapters do not align verse for verse, and say so

| Chapter | Latin | 思高 |
|---|---:|---:|
| 宗徒大事錄 2 | 46 | 47 |
| 路加福音 24 | 51 | 53 |
| 馬爾谷福音 4 | 40 | 41 |
| 若望福音 17 | 25 | 26 |
| 出谷紀 3 | 21 | 22 |
| 達尼爾 3 | 99 | 100 |
| 友弟德傳 13 | 31 | 20 |
| 厄則克耳 37 | 27 | 28 |
| 多俾亞傳 1 | 24 | 22 |
| 箴言 8 | 35 | 36 |

Judith and Tobit differ widely because Jerome's Latin is an independent recension,
not a translation of the Greek the Chinese follows. These are recorded per
chapter in `alignmentNote`, never silently reconciled.

約伯傳 38 additionally prints its verses **out of order** — 38, 37, then 40, 39 —
because this edition transposes where its translators judged the received order
corrupt. That is a version feature, not a parse error: the gate rejects duplicate
verse numbers and records transposition.

Psalm numbers: the Vulgate follows the Greek psalter and the Studium Biblicum
follows the Hebrew, so 22↔23, 50↔51, 90↔91, 129↔130. Each pair is **verified
against the text**, not trusted — and the probe reads the whole psalm, because
this edition numbers the superscription and the Miserere does not reach 憐 until
its third verse.

## 下冊: 50 readings

Twenty-five patristic and medieval, then twenty-five from Trent onwards; ordered
by difficulty within each half.

**Every reading is a complete chapter or a complete piece.** Owner's rule,
2026-08-26. A creed, a hymn, a bull or a short council session is printed
entire. A work too long to print whole — Lumen Gentium at 21,874 words, Gaudium
et Spes at 26,709 — is cut at **its own divisions**: whole chapters, whole
numbered sections, whole canons, as many as fit the lesson, never part of one.
`scripts/build_latin_church_plan.py:complete_unit` picks the strongest marker the
work itself uses (CAPUT before roman numerals before numbered paragraphs) and
each reading records what it printed: 「第 1–4 節（完整，共 33 節）」.

This replaced a word-count rule that took the first nine hundred words of each
work. That rule stopped wherever nine hundred words happened to land, mid-
argument, and it is not what a reading is.

Seven works carry no divisions the parser can see and are longer than the whole-
work limit; they print complete paragraphs and say so — 「原文無分章標記；取前 N
個完整段落，非全文」 — rather than implying a chapter was chosen.

**27 of the 50 already have a Chinese parallel in this repository.** The
remaining 23 are the Latin Library patristic texts, which have none and must be
self-translated and labelled `自譯`. That is the largest outstanding gap in the
lower volume and it is not to be described as anything smaller.

## Memory units

Two per lesson, a hundred per volume, built by
`scripts/build_latin_memory_units.py --write`. Each unit is assigned to the
earliest lesson whose **cumulative** vocabulary can nearly read it — at most one
word in seven left to look up, because demanding total coverage against a
two-thousand-word reader in an eight-thousand-lemma Bible clears almost nothing.

Readability runs one way: a unit readable at lesson three is still readable at
lesson thirty. So each lesson draws from every pool up to its own, taking the
most demanding candidates it can now handle. Filling each lesson only from its
own pool front-loads the entire book.

下冊's running vocabulary **starts from all thousand of 上冊's words.** A reader
opening the second volume has finished the first.

Rejected outright: census and genealogy lines, anything that does not open with
a capital and close on a stop, near-duplicates of an already-chosen unit, and
anything the lemmatiser cannot read four words in five — that last one is what
keeps citation apparatus out.

## Appendices

Ten tables, outside the twenty-per-lesson count, built by
`scripts/build_latin_appendices.py --write`. Five face the Bible and five face
the church, because the two volumes need different reference shelves.

| Volume | Appendix |
|---|---|
| 上冊 | 人名、地名、民族與國名（武加大） |
| 上冊 | 數字、羅馬數字與度量衡 |
| 上冊 | 親屬稱謂 |
| 上冊 | 羅馬曆、月份與聖經節期 |
| 上冊 | 動詞主要部分與不規則變化 |
| 下冊 | 教會職分、聖統與禮儀用語 |
| 下冊 | 禮儀年與時辰誦讀 |
| 下冊 | 教廷文獻體裁與公文用語 |
| 下冊 | 經院哲學與神學術語 |
| 下冊 | 近現代教廷拉丁的地名、機構名與專名 |

The four curated tables in each volume **do** overlap the lessons on purpose:
they are a cross-index, not a second vocabulary list. Only the names are kept
disjoint from the lessons.

Two of these have no counterpart in the Hebrew or Greek readers and are this
reader's own contribution: how the Holy See writes today's nation-states and
institutions, and the Kalends/Nones/Ides dating that every papal dateline uses
(`Datum Romae, die IV Kalendas Decembris`). Latin also needs a principal-parts
table that neither of the other two languages requires, and its four-way kinship
split (`patruus`/`avunculus`/`amita`/`matertera`) maps onto Chinese 伯叔姑姨
exactly, which no European-language reader can show.

### Chinese for the names is read, not recalled

The Studium Biblicum edition underlines every proper name in its verse text, so
each verse offers a small candidate set. A Latin name's Chinese is whichever
underlined name shares the most verses with it, subject to two guards: it must
follow that name through at least 60% of its verses, and it must not be a name
that follows everything. Names outside the fifty printed chapters keep an empty
cell. Every filled cell records `zhRoute` and the verse evidence.

## Translation, layout, web and audio

**Chinese for what had none** — `scripts/translate_latin_readings_zh.py`. The
terminology is fixed in the prompt rather than left to the model, because a
general-purpose Chinese Bible vocabulary is Protestant and would print 上帝
beside a 思高 page that says 天主. Every unit is labelled 自譯（研讀用，非教會核准
禮儀譯本）: the Chinese-speaking Church has its own approved liturgical
translation of the Mass, 《感恩祭典》, and this is not it.

One paragraph per request. Told four times, in numbered form, to return four
paragraphs for four, this tier returned two; a request holding one paragraph
cannot come back misaligned.

**Print** — `scripts/build_latin_full_reader.py` writes two JIS-B5 DOCX from the
same master, reusing the Hebrew reader's geometry and type ladder so the three
readers shelve as one set. Rendered with LibreOffice: 上冊 267 pages, 下冊 577.

**Web** — `scripts/build_latin_reader_data.py` assembles one master JSON;
`data/originalReaders/latin-full-reader.ts` slices it; the API under
`server/api/original-readers/lat-lessons/` is `requireAuth` + noindex, and the
pages live at `/original-readers/lat-lessons`. The overview prints what is *not*
finished, because a page that shows only its finished parts invites a draft to
be mistaken for a release.

**Audio** — `scripts/build_latin_reader_audio.py` renders the ten formulas and
every memory unit with an Italian system voice, at the Roman pronunciation's
nearest available approximation, and stamps the manifest `draft`. **This does not
satisfy the audio gate.** A release track records reader, rate, cues, checksum
and rights, and is a human voice.

## Stop conditions specific to this release

- Never restate the upper volume's order as a frequency ranking. It is Collins's
  order, and `missa` in lesson one is the proof.
- Never take a Collins form from the PDF text layer. Every macron there is wrong.
- Never let a Classical headword head a Vulgate word. If the merge order is not
  vulgate → church → classic, that is the symptom.
- Never trust a 信望愛 response because it says `success`. Check the `engs` it
  returns against the book you asked for.
- Never describe a lower-volume reading as complete without checking its length
  against the source; and never mix a complete text and an excerpt without
  labelling both.
- The Ordo Missae's Latin is Collins's Further Readings 1, which prints the
  post-conciliar ordinary; the owner's verbal permission covers this private
  edition. Its Chinese is 自譯 and must never be presented as 《感恩祭典》.
- Never call the synthetic audio a release track, and never let a page offer a
  play control for a clip that does not exist.
- Never let the imported Hebrew layout keep its running header. Every page of
  the first Latin print run said 聖經希伯來文原文讀本.
