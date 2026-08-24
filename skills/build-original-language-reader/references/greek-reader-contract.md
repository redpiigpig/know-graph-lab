# Greek reader — frozen release contract

Frozen 2026-08-18 for `know-graph-lab`. Verify every path live before use.

## Curriculum

Re-frozen 2026-08-24 by the owner. The reader is **two volumes of fifty lessons,
twenty words each** — two thousand words in all. This supersedes the earlier
single-volume plan whose lesson sizes came from BBG's own chapters; that plan and
`scripts/assign_greek_lessons.py` are superseded, not merely adjusted.

| Item | Frozen value |
|---|---|
| Volumes | 2. 上冊《新約與七十士譯本》, 下冊《教父文獻與希臘教會文獻》 |
| Lessons | 50 per volume, **exactly 20 words each** |
| Vocabulary | 2,000 entries, the three lists disjoint |
| 上冊 1–25 | New Testament: 500 words from Mounce's own list in Mounce's order, plus 2 memory verses and 1 complete chapter per lesson |
| 上冊 26–50 | Greek Old Testament: 500 words by Septuagint frequency, plus 2 memory verses and 1 complete chapter per lesson |
| 下冊 1–25 | Patristic: 20 words, 2 sentences, 1 article passage per lesson |
| 下冊 26–50 | Greek church documents and liturgical texts: 20 words, 2 sentences, 1 prayer/creed/document per lesson |
| Ends with | the complete ordinary-time Chrysostom liturgy, in 下冊 only |
| No liturgy in 上冊 | owner's instruction; do not reintroduce it there |
| Builder | `scripts/build_greek_vocabulary_2000.py --write` → `data/originalReaders/vocabulary/greek-2000.json` |
| Master | `scripts/build_greek_reader_data.py --write` → `greek-reader-two-volumes.json`, schema 2.0.0, one `volumes` entry per book |
| Transliteration | Mounce's own for his 500; the same published Erasmian table applied by rule for the other 1,500, each labelled `rule_generated_from_official_table` |
| Print | one JIS B5 DOCX per volume; the five reference tables print in **both**, the liturgy in 下冊 only |

### The language is Koine, and staying there takes work

The reader teaches 通用希臘文, not Classical Greek, and the lemmatiser is where
that guarantee gets quietly broken. Morpheus covers all of Ancient Greek and is
Attic-first: asked for σου it answers with the Homeric possessive σός, and for
ἐγένετο with Attic γίγνομαι. Built on Morpheus alone, the Septuagint frequency
list came out headed by σός, εἶπον, ὑμός, γίγνομαι and χρύσεος — every one of
them a Classical headword for a word Mounce had already taught.

Three layers, in this order, never rearranged:

1. **Koine lexicon** — `scripts/build_greek_koine_lexicon.py --write` merges
   MorphGNT's 137,554 tagged New Testament words with CATSS/OSSP's 623,685 tagged
   Septuagint words into `koine-lexicon.json`. Where both tag the same form, the
   **New Testament headword wins**: the Septuagint analysis keeps older lexicon
   conventions (εἶπεν under ἔπω, σου under σοῦ, χρυσοῦν under χρύσεος) and the
   textbook uses λέγω, σύ, χρυσοῦς.
2. **Attic→Koine bridge** (`to_koine`) — γιγν→γιν, ττ→σσ, ρρ→ρσ, -εος→-οῦς, plus
   a table of suppletives and variants. Every rewrite is checked against the Koine
   inventory before it is applied, so the bridge cannot invent a word. **Compare
   on folded spellings**: written out, "γιγν" does not occur in "γίγνομαι" at all,
   and that trap has been fallen into once already.
3. **Morpheus** — consulted only for forms the two Koine corpora never attest, and
   when its Classical readings are ambiguous with no Koine candidate, the token is
   left uncounted rather than guessed. Guessing produced ὁλάω and πτελέα for what
   were really ὅλος and a proper name.

Result to beat: Septuagint 97% resolved by the Koine lexicon with **zero**
Classical headwords; patristic 88% + 6% Morpheus, 25 of 1,000 outside the tagged
Koine inventory and all of them verified as genuine later church Greek
(ἀσώματος, ἄτρεπτος, σύγγραμμα, ἀθεότης), marked `withinKoine: false`.

Accent-blind folding conflates minimal pairs whose breathing is the whole word —
ἕξ "six" with ἐξ "out of", εἷς "one" with εἰς "into" — and the commoner word takes
every occurrence, so the numeral disappears from the counts. The Koine lexicon
therefore also carries 2,511 accent-sensitive forms (`exactForms`), consulted
before the folded index.

### Proper names are not lesson words

Owner's instruction, 2026-08-24: names go in the appendix, the lesson slots are
backfilled, and the two never overlap. Mounce's first five hundred contain 28
proper names; skipping them carries the New Testament list to Mounce's 528th
entry. Verified separation: lessons ∩ appendix names = 0.

The Septuagint and patristic lists exclude names structurally — a raw Septuagint
frequency list is otherwise headed by Ἰσραήλ, Μωϋσῆς and Ἱερουσαλήμ, which crowds
out vocabulary. Names are detected from the corpora themselves: a lemma written
with a capital in ≥80% of its appearances is a name. Morpheus lower-cases its
headwords, so Πολύκαρπος and Εἰρηναῖος arrive looking like adjectives; only the
corpus's own capitalisation catches them.

## Appendices

Five, outside the twenty-per-lesson count, built by
`scripts/build_greek_appendices.py --write` →
`data/originalReaders/vocabulary/greek-appendices.json`:

| Appendix | Entries | Source |
|---|---|---|
| 人名、地名與國族 | 405 | harvested, ≥10 occurrences |
| 數字與度量衡 | 73 | curated, verified against the corpora |
| 親屬稱謂 | 37 | curated |
| 曆法與節期 | 46 | curated |
| 教會職分與禮儀用語 | 64 | curated |

The four curated appendices **do** overlap the lessons on purpose: they are a
cross-index, not a second vocabulary list. Someone looking up "the numerals" wants
εἷς there even though lesson one taught it. Only the names are kept disjoint.

Curated entries carry `attested` and the real corpus frequency, so a list that
drifts into words the reader never meets is visible.

All 220 curated entries carry Traditional Chinese, filled by
`scripts/fill_greek_appendix_glosses.py --write` in two passes and in this order:
**a word the lessons already teach keeps the lesson's own wording** (115 of them),
and only the rest go to a language model. Otherwise the same εἷς would be glossed
one way in lesson one and another way in the appendix. Every entry records
`zhSource`, so which route named it stays visible.

### Naming the appendix, in priority order

Chinese is never invented here. `scripts/fill_greek_appendix_names.py --write`
then `scripts/align_greek_names_chinese.py --write`:

1. **翻譯定名 glossary** — keyed on the Greek itself, so a hit is exact and
   authoritative (`name_recommended` outranks everything).
2. **信望愛 Chinese Strong's** (`bible.fhl.net/json/sd.php`) — covers the New
   Testament's names *including places and peoples*, which `biblical_people`
   cannot, and its part-of-speech line states person or place outright. Cached in
   `fhl-strongs-zh.json`. Strong's indexes the Textus Receptus, so its spellings
   differ (Δαβίδ, Σολομών, Μωσεύς); a one-letter unique-match bridge plus an
   explicit alias table crosses that gap.
3. **Strong's English → `biblical_people`** — dropped, never guessed, when one
   English name has several Chinese ones.
4. **Chinese-Bible verse alignment** — for the Septuagint's own names, which no
   register holds. A Greek name's verses are fetched in 和合本修訂版 and the
   character run that appears in most of them and is rare in a 9,336-verse
   background is its Chinese name. **Match the Greek stem at a word boundary**:
   plain substring matching put τυρ inside μαρτύρομαι and confidently aligned
   Tyre with 「見證」.
5. **Transliteration** — Ἰω-→Jo-, χ→h, -ίας→-iah; marked for review.

Reached 341/405. The remaining 64 are mostly deuterocanonical (Ὀλοφέρνης,
Μακκαβαῖος, Ἀντίοχος); 信望愛 holds no Chinese edition of Maccabees.

## Source freeze

| Layer | Frozen source | Rights |
|---|---|---|
| New Testament Greek | SBLGNT, ed. Michael W. Holmes, via the MorphGNT analysis (`morphgnt/sblgnt`) | SBLGNT EULA, private authorized; MorphGNT annotation CC BY-SA 3.0 |
| LXX, deuterocanon, pseudepigrapha Greek | Henry Barclay Swete, *The Old Testament in Greek according to the Septuagint*, Cambridge 1909–1930, digital word database `eliranwong/LXX-Swete-1930` | Swete's text is public domain; the digital database is GPL-3.0 and is kept as a local build input, not redistributed |
| Traditional-Chinese Bible (NT + LXX-canonical) | 《和合本修訂版》（2010）, variant RCUV2（上帝版）, official HKBS payloads | private authorized, same as the Hebrew reader |
| Traditional-Chinese deuterocanon | 1933 年聖公會出版次經（信望愛站「次經閱讀」version `c1933`） | 1933 譯本已逾著作權期間；數位化循 CBOL 版權宣告作非商業使用 |
| Traditional-Chinese pseudepigrapha | self-translated, labelled `自譯` in every unit | editorial |
| Creeds and council canons | `data/creeds/**` Greek versions (Schaff/DCO), plus `creeds-greek.json` for the three texts the repository lacked | as recorded per document; the Schaff additions are public domain |
| Canon collections and hymnody | Greek Wikisource (`el.wikisource.org`): 12 canonical collections and 4 hymns, frozen with revision id, timestamp and sha256 in `sources/church-documents/manifest.json` | the canons themselves are ancient and out of copyright; the Wikisource transcription is CC BY-SA 4.0, private authorized use with attribution |
| Apostolic and Greek Fathers | public-domain Greek editions, frozen per work | per work |
| Divine Liturgy of St John Chrysostom | Greek liturgical text, ordinary-time (non-festal) Sunday order, frozen edition recorded per section | per edition |

### One crosswalk, and it refuses rather than approximates

Every Septuagint-to-Chinese reference goes through `target_reference()` in
`scripts/export_reader_rcuv2010_greek.py`, and the master imports that same
function rather than keeping its own copy. Four books need it:

- **Psalms** — the Septuagint joins MT 9 and 10 and splits MT 116 and 147, so the
  two numberings differ by one over most of the Psalter; the superscription
  offset is read off the two verse counts rather than tabulated.
- **Jeremiah** — a different book from chapter 26 on. LXX 38 is MT 31. The five
  Septuagint chapters whose material splits across two Hebrew ones (25, 29, 30,
  32, 51) raise `LookupError` instead of being approximated.
- **Jonah** — 和合本修訂版 follows the English chapter break, so Septuagint Jonah
  2:1 is Chinese 1:17 and the rest of the chapter runs one number ahead.
- **Proverbs** — reordered from 24:23 on, so chapters past 24 are refused.

A book missing from the code table used to be skipped in silence; 449 verses
reached the master with no Chinese and the cause only surfaced seven chapters
downstream. It now raises. The memory-verse selector asks the same crosswalk
whether a chapter is pairable rather than keeping a second list.

Rahlfs–Hanhart 1935 is *not* the frozen LXX base. The accessible digital Rahlfs is CCAT-derived and requires a signed CCAT user declaration, and Rahlfs carries no Greek 1 Enoch. Swete covers LXX, all deuterocanonical books, Psalms of Solomon and the Greek 1 Enoch in one public-domain edition. Rahlfs may be cited as a collation reference only.

## 上冊：50 complete Scripture chapters

Lessons 1–25 read the New Testament, lessons 26–50 the Greek Old Testament, each
half ordered by difficulty on its own. A reader is not asked to take the
Septuagint's Hebraic syntax in lesson three just because that chapter is easy.

Approved split: **New Testament 25 / Septuagint canonical 18 / deuterocanonical 5
/ pseudepigraphal 2**. Built by `scripts/build_greek_scripture_plan.py --write`;
1,413 verses, 26,115 words.

| # | Corpus | Reading | Size | Note |
|---:|---|---|---|---|
| 1 | 新約 | 約翰一書 1 | 10 節 207 詞 |  |
| 2 | 新約 | 馬可福音 1 | 45 節 701 詞 |  |
| 3 | 新約 | 馬可福音 4 | 41 節 683 詞 |  |
| 4 | 新約 | 馬太福音 6 | 34 節 648 詞 |  |
| 5 | 新約 | 馬太福音 5 | 48 節 821 詞 |  |
| 6 | 新約 | 約翰福音 1 | 51 節 826 詞 |  |
| 7 | 新約 | 哥林多前書 13 | 13 節 197 詞 |  |
| 8 | 新約 | 路加福音 2 | 52 節 849 詞 |  |
| 9 | 新約 | 路加福音 15 | 32 節 564 詞 |  |
| 10 | 新約 | 約翰福音 15 | 27 節 500 詞 |  |
| 11 | 新約 | 腓立比書 2 | 30 節 431 詞 |  |
| 12 | 新約 | 使徒行傳 2 | 47 節 835 詞 |  |
| 13 | 新約 | 雅各書 1 | 27 節 406 詞 |  |
| 14 | 新約 | 啟示錄 21 | 27 節 603 詞 |  |
| 15 | 新約 | 羅馬書 12 | 21 節 304 詞 |  |
| 16 | 新約 | 加拉太書 5 | 26 節 313 詞 |  |
| 17 | 新約 | 彼得前書 2 | 25 節 392 詞 |  |
| 18 | 新約 | 以弗所書 2 | 22 節 362 詞 |  |
| 19 | 新約 | 路加福音 24 | 53 節 809 詞 |  |
| 20 | 新約 | 羅馬書 8 | 39 節 652 詞 |  |
| 21 | 新約 | 希伯來書 1 | 14 節 257 詞 |  |
| 22 | 新約 | 約翰福音 17 | 26 節 498 詞 |  |
| 23 | 新約 | 使徒行傳 17 | 34 節 675 詞 |  |
| 24 | 新約 | 哥林多前書 15 | 58 節 843 詞 |  |
| 25 | 新約 | 啟示錄 1 | 20 節 469 詞 |  |
| 26 | 七十士譯本（正典） | 創世記 1 LXX | 31 節 751 詞 |  |
| 27 | 七十士譯本（正典） | 創世記 22 LXX | 24 節 540 詞 |  |
| 28 | 七十士譯本（正典） | 出埃及記 3 LXX | 22 節 596 詞 |  |
| 29 | 七十士譯本（正典） | 詩篇 22 LXX（MT 23） | 6 節 104 詞 | MT 23 |
| 30 | 七十士譯本（正典） | 創世記 3 LXX | 24 節 597 詞 |  |
| 31 | 七十士譯本（正典） | 出埃及記 20 LXX | 26 節 506 詞 |  |
| 32 | 七十士譯本（正典） | 申命記 6 LXX | 25 節 538 詞 |  |
| 33 | 七十士譯本（正典） | 約拿書 2 LXX | 11 節 184 詞 |  |
| 34 | 七十士譯本（正典） | 詩篇 129 LXX（MT 130） | 8 節 84 詞 | MT 130 |
| 35 | 七十士譯本（正典） | 詩篇 50 LXX（MT 51） | 21 節 284 詞 | MT 51 |
| 36 | 七十士譯本（正典） | 以賽亞書 6 LXX | 13 節 307 詞 |  |
| 37 | 次經 | 多俾亞傳 1（西奈抄本 GII） | 22 節 729 詞 |  |
| 38 | 次經 | 友弟德傳 13 | 20 節 602 詞 |  |
| 39 | 七十士譯本（正典） | 路得記 1 LXX | 22 節 515 詞 |  |
| 40 | 七十士譯本（正典） | 詩篇 90 LXX（MT 91） | 16 節 202 詞 | MT 91 |
| 41 | 七十士譯本（正典） | 列王紀上 19 LXX（七十士作《王國記三》） | 21 節 568 詞 |  |
| 42 | 七十士譯本（正典） | 以西結書 37 LXX | 28 節 686 詞 |  |
| 43 | 次經 | 德訓篇 24 | 32 節 421 詞 |  |
| 44 | 七十士譯本（正典） | 以賽亞書 53 LXX | 12 節 286 詞 |  |
| 45 | 七十士譯本（正典） | 箴言 8 LXX | 35 節 417 詞 |  |
| 46 | 七十士譯本（正典） | 耶利米書 38 LXX（MT 31） | 40 節 864 詞 | MT 31 |
| 47 | 次經 | 瑪加伯下 7 | 42 節 876 詞 | 中文自譯 |
| 48 | 次經 | 智慧篇 7 | 30 節 437 詞 |  |
| 49 | 偽經 | 所羅門詩篇 17 | 51 節 877 詞 | 中文自譯 |
| 50 | 偽經 | 以諾一書 1（希臘文） | 9 節 299 詞 | 中文自譯 |

Swete marks the material the Septuagint adds to a verse with a bracketed digit in
the running text — Proverbs 8:21a — and his database indexes that marker as a word
of its own, so the word-count gate fails on it. **Brackets holding only digits are
editorial numbering**: excluded from the count, kept in the display layer,
recorded as `editorialVerseMarkers`. **Brackets holding Greek are restored text**
and stay, counted, as before.

2 Maccabees 7 is the one chapter whose Chinese does not come from the frozen
deuterocanonical edition: the 1933 Anglican canon does not contain Maccabees, and
信望愛 holds no Chinese Maccabees at all. It is self-translated, and says so in
`translationNote`. Susanna and Baruch were examined as replacements and rejected —
Swete prints the Old Greek Susanna (60 verses) against a Theodotion-based Chinese
(64), and Baruch 3 differs by one verse. Neither can be aligned verse by verse.
A chapter is not dropped because its source is inconvenient, and a translation
that will not arrive is not silently promised.

## 下冊：50 readings

Lessons 1–25 are patristic; lessons 26–50 are Greek church documents and
liturgical texts. Each lesson carries 20 words, 2 sentences, and one passage.
Declared as complete short works or explicitly labelled authorized excerpts;
never mixed silently.

Built by `scripts/build_greek_patristic_plan.py --write`: **50 readings, 2,598
segments, 72,585 words**, 34 complete works and 16 labelled excerpts.

| Lessons | Category | Count |
|---|---|---:|
| 1–18 | 使徒教父 | 18 |
| 19–25 | 希臘教父 | 7 |
| 26–29 | 信經與信仰定義 | 4 |
| 30–43 | 教規彙編 | 14 |
| 44–50 | 禮儀文本與頌歌 | 7 |

The canonical corpus is read in the order the canonical collections themselves
put it in: the apostolic canons, then the ecumenical councils, then the local
synods whose canons the councils ratified. Two collections are too long for one
lesson and are labelled excerpts — Trullo 1–20 of 102, Carthage 1–20 of 133.

### 下冊's two sentences per lesson

上冊's memory units are verses; 下冊's readings have no verse numbers, so its
units are **sentences**, cut from the readings on Greek sentence punctuation and
required to stand as a sentence rather than half of one. Selected by
`scripts/select_greek_memory_sentences.py --write`.

The same half rule as 上冊: lessons 1–25 take sentences from the patristic
readings, 26–50 from the church documents, so a unit never comes from a corpus
the lesson has not opened. A sentence drawn from the lesson's *own* reading
scores a bonus but is not required; 25 of the 100 came out that way.

Matching resolves each printed form through the Koine lexicon before comparing.
Comparing printed forms with dictionary headwords finds almost nothing —
ἀναμιμνήσκωμεν is not ἀναμιμνήσκω — and the first version averaged one hit per
sentence and left eight lessons unable to fill their two slots.

**The relationship between a lesson's two sentences and its reading has not been
put to the owner.** The rule above is this build's decision, recorded in
`designNote` inside `memory-sentences.json`.

The volume ends with the complete ordinary-time (non-festal Sunday) Divine
Liturgy of St John Chrysostom, Greek with Traditional-Chinese parallel, kept
separate from the 25 readings — the structural counterpart of the Hebrew
fifteen-step Haggadah. It belongs to 下冊 only; the owner removed it from 上冊.

## Stop conditions specific to this release

- The 1933 Anglican deuterocanon uses its own book names (多比傳／猶滴傳／所羅門智訓／便西拉智訓). Keep them; do not silently relabel them with the 思高 names the Catholic canon uses.
- `creeds-greek.json` marks three segments `needs_review_*`. Schaff prints variant readings and a Greek term index inside the same cells as the creed; those segments must be reviewed before they reach a reading, and never shipped as creed text unexamined.
- Greek 1 Enoch and Psalms of Solomon carry editorial brackets in Swete. Keep the bracketed source form immutable and flag any display-layer removal.
- No modern-Greek TTS may stand in for the Mounce Erasmian audio track.
- Never restate the curriculum as "lesson size comes from BBG". That was the
  earlier design and the owner replaced it on 2026-08-24 with a flat twenty words
  per lesson across two volumes. `scripts/assign_greek_lessons.py` is superseded.
- Never let a Classical headword into a vocabulary list. If σός, εἶπον, γίγνομαι,
  χρύσεος or ὑμός appears at the top of a frequency list, the Koine lexicon is not
  being consulted first — that is the symptom, every time.
- Never invent a Chinese name. Every appendix name records `zhRoute`; entries no
  register covers stay empty. 64 currently do, and that is the correct state.
- A proper name never occupies a lesson slot, and the appendix never repeats a
  lesson word. Assert `lessons ∩ appendix names == 0` after any rebuild.
