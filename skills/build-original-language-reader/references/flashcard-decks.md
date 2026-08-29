# Printable flashcard decks

The reader's vocabulary masters also drive printed decks: Hebrew 1,000 cards,
Greek volume 1 and volume 2 at 1,000 each, Latin volume 1 and volume 2 at 1,000
each. They follow the household's existing
English tutoring deck (`家教單字卡.pdf` on the desktop) so the same guillotine
and the same printer settings work for all of them.

## State, 2026-08-28

| Deck | Cards | Pages | With picture | Part of speech blank | File |
|---|---:|---:|---:|---:|---|
| 聖經希伯來文 | 1,000 | 252 | **1,000 (100%)** | 0 | `output/flashcards/hebrew-flashcards-1000.pdf` |
| 通用希臘文・上冊 | 1,000 | 252 | **1,000 (100%)** | **0** | `output/flashcards/greek-flashcards-volume-1.pdf` |
| 通用希臘文・下冊 | 1,000 | 252 | **1,000 (100%)** | **0** | `output/flashcards/greek-flashcards-volume-2.pdf` |
| 教會拉丁文・上冊 | 1,000 | 252 | **996 (99.6%)** | **0** | `output/flashcards/latin-flashcards-volume-1.pdf` |
| 教會拉丁文・下冊 | 1,000 | 252 | **1,000 (100%)** | **0** | `output/flashcards/latin-flashcards-volume-2.pdf` |

All five are built, rendered, verified and pushed. DOCX sits beside each PDF.

### Appendix decks, added 2026-08-27

| Deck | Cards | Pages | Dropped (no Chinese) | File |
|---|---:|---:|---:|---|
| 聖經希伯來文附錄 | 255 | 64 | 0 | `output/flashcards/hebrew-flashcards-appendix.docx` |
| 通用希臘文附錄 | 511 | 128 | 114 | `output/flashcards/greek-flashcards-appendix.docx` |
| 教會拉丁文附錄 | 745 | 188 | 191 | `output/flashcards/latin-flashcards-appendix.docx` |

The reader appendices hold the material that never enters the fifty lessons:
proper names in nine categories, numerals and measures, kinship terms, the
calendar and its feasts, church offices and liturgical vocabulary. The owner
asked for cards for all of it. These share the sheet, the card size and the
duplex rule with the five lesson decks and differ in exactly three ways: the
frame colour cycles by **section** rather than by lesson (so one section is one
colour), the footer prints the section name instead of a lesson number, and
**there are no pictures** — no emoji honestly denotes 伯特利, 猶斯定 or 第十七.

Section order is `PRINT_ORDER` from `scripts/proper_name_categories.py` for the
proper names, then each remaining table's own `group` field in first-appearance
order. The printed appendix and the web page use the same order.

A row with no Traditional-Chinese rendering is not printed and the build reports
how many it dropped. Latin's 191 are all proper names the Studium Biblicum
alignment could not settle; its numerals, kinship, calendar, offices, liturgical
year, document-genre and scholastic tables are at 100% since
`gloss_latin_appendices_zh.py` ran. Greek's 114 are the appendix names no
register covers.

**Two Latin tables are deliberately excluded.** `principalParts` (841 rows) is a
morphology reference whose headwords largely repeat the lesson verbs, and
`modernNames` (400 rows) has no Chinese at all and has swept up abbreviations and
common nouns (`Psal`, `Joan`, `Latine`, `Cardinalis`, `Redemptoris`); that table
needs rebuilding at source.

**Hebrew numerals are stored as a masculine/feminine pair**, with no single
`pointed` field. One card per form, with 「（陽性）」/「（陰性）」 on the Chinese
face — a combined card would make the reader memorise two forms at once. Check
any new language's numeral table for the same shape before assuming one row is
one card.

### What the owner has decided

- **Every card should carry a picture.** Their reasoning: a physical deck only
  earns its keep if the picture aids memory, otherwise study online. Hebrew
  reached that on 2026-08-26 (419 blanks picked by hand), and Greek on the same
  day: 925 hand picks in four passes took the two volumes from 50% to 100%, so
  the Greek `OVERRIDES` now carries 1,493 entries. Latin went 802 → 1,361 on 2026-08-27 without a single hand pick, by fixing two things in the borrowing rule rather than by picking pictures — see 「借圖只看第一個義項」 below. The remaining 639 were then hand-picked on 2026-08-28, which took all five decks to 1,996／2,000. The four left blank are 拿撒勒的、加里肋亞的、猶太的、羅馬的: 族屬形容詞, which in the other three readers live in the appendix, and appendix cards carry no picture — 沒有一個 emoji 誠實地代表得了「伯特利」.
- **Cartoon style**, one consistent look.
- **No cutting lines.** A hairline printed a millimetre off leaves every card
  with a crooked edge.
- **The Divine Name takes the God picture.** יְהוָה and יְהֹוִה use the same 🤲 as
  אֱלֹהִים / אֵל / אֲדֹנָי: one concept, one picture. Not a star of David or a
  menorah — those are symbols of later Judaism read back onto the Hebrew Bible,
  which is a different claim.

### Where the pictures come from, and what was ruled out

OpenMoji 17.0.0 (CC BY-SA 4.0), 4,565 consistent cartoon SVGs, cited on each
cover. The 44 MB artwork is not in git;
`scripts/match_flashcard_images.py` downloads it on demand.

Ruled out, so nobody spends the time again:

- **Canva** has no usable programmatic route. The Connect API is partner-gated
  and its content licence does not cover bulk export into your own teaching
  material.
- **AI image generation** was unreachable on 2026-08-25: all seven Gemini keys
  returned 429 on `gemini-2.5-flash-image` and `gemini-3.1-flash-image` (image
  generation is effectively a paid-tier feature), and NVIDIA's `ai.api.nvidia.com`
  image endpoints returned 500/404/timeout. If the owner ever supplies a paid
  Gemini key this is the route to 100% coverage with a better-matched style than
  emoji, and it is worth revisiting first.
- **Openclipart** (CC0, would have been ideal for coverage) has a dead JSON API
  — the search endpoint returns HTML. Scraping it would also mix dozens of
  artists' styles in one deck.

## Sheet

| | |
|---|---|
| Page | A4 landscape, 297 × 210 mm |
| Grid | 4 columns × 2 rows, 8 cards a sheet |
| Card | 71.25 × 98 mm |
| Margins | 6 mm left and right, 7 mm top and bottom — **symmetric on all four sides** |
| Cuts | vertical 6 / 77.25 / **148.5** / 219.75 / 291 mm from the left; horizontal 7 / **105** / 203 mm from the top |
| Duplex | long-edge flip; the back sheet mirrors the column order 4-3-2-1 |

**The two middle cuts land on the paper's own centre lines** (148.5 = half of
297, 105 = half of 210), which is what makes a guillotine stack cuttable: the
operator folds or measures to the centre once and the rest follows. The previous
sheet could not be cut evenly — 74.25 × 94 with 0 side margins and 5 mm top left
17 mm at the bottom, so the middle horizontal cut sat at 99 mm against a 105 mm
centre line, and the cards ran to the paper edge where no home printer can print.
Measured on the rendered page: now 8.9 mm top and bottom, 7.9/8.1 left and
right; before, 6.9 top against 18.8 bottom and under 2 mm at the sides.

**Declaring symmetric margins is what pushes the second row onto its own page —
not the card height.** A symmetric declaration means `top + 2×height + bottom`
equals the page exactly, and the renderer needs a little slack it never asked
for; an 86 mm card fails just as an 98 mm one does when both margins are
declared. The fix is to declare the top and left margins at their real value and
the bottom and right at **zero**: the block still ends at `margin + 2×height`,
so the leftover *is* the visual bottom margin and the page stays centred, while
the renderer keeps its slack. Setting `row.height` and then appending a second
`w:trHeight` leaves two competing rules in the XML and produces the same symptom.

`HEADWORD_MAX_MM` follows the card width rather than being written out: it was
hard-coded to 54 mm for the 74.25 mm card, and a hard-coded limit silently
overflows the moment the card changes width.

## Card faces

Front carries the headword and the lesson. Back carries the picture (when there
is one), the Traditional-Chinese meaning, the part of speech and the lesson. The
meaning line is sized from its own length — the glosses run from two characters
to twenty-seven — rather than set once and allowed to overflow.

**The Greek cards print a citation form only when it cannot be worked out.** The
reader prints the full dictionary form; the card does not need to, because for a
first- or second-declension noun the genitive follows from the ending plus the
gender — `θεός` is a masculine `-ος`, so the genitive can only be `θεοῦ`, and
printing it spends space that the headword's own size ladder would otherwise use.
What is kept is what cannot be derived: a third-declension stem
(`σῶμα, ατος, τό`), a gender that contradicts the ending (`ὁδός, οῦ, ἡ`;
`προφήτης, ου, ὁ`), or an impure alpha (`δόξα, ης, ἡ`). The decisive case is
`γένος, ους, τό` — its nominative is indistinguishable from `λόγος` and its
genitive is nothing like it.

259 of the 729 noun cards keep the form and 470 print the headword alone
(volume 1: 128/231, volume 2: 131/239). `scripts/greek_citation_form.py` decides;
the genitive and article come from the vocabulary's own `printedEntry` where
Mounce supplies one and from Dodson otherwise. The 80 nouns neither source
covers print the headword alone — **never a derived genitive**.

Latin prints the full citation form on the front — four principal parts for a
verb, nominative-genitive-gender for a noun — because that is what has to be
known, and it gets its own size ladder: the longest run past forty characters,
where the Greek ladder would shrink them to nothing. They are allowed to wrap.

Hebrew and Latin read their part of speech from the vocabulary master; Latin's
comes from the reader's own `short_pos`, which reads the gender abbreviation and
the principal parts rather than an explicit field, because Collins labels
neither. Greek has none, so
`scripts/flashcard_pos.py` works it out, strongest evidence first:

1. hand lists for the function words and the irregular verbs;
2. the citation form — an article makes a noun, three terminations an adjective,
   a first-person form a verb;
3. **the SBLGNT's own tags.** MorphGNT labels every New Testament word, so for
   anything the New Testament uses the part of speech is a recorded fact rather
   than an inference. This alone settled 603 of the 723 Greek cards that the
   first two rules left blank;
4. the Chinese gloss where the form is silent — `（配屬格）` marks a preposition,
   a gloss whose senses all end in 「的」 an adjective;
5. `EXTRA_LEXICON`, 116 Septuagint and patristic words read one at a time. Nouns
   dominate it because a bare Septuagint headword carries no article, which is
   exactly the cue rule 2 needs.

Together they settle all 2,000. **A blank line costs nothing; a wrong label is
learned as fact** — the list in rule 5 was written by reading the words, not by
guessing from endings, precisely because -ος is a noun and an adjective alike.

The adverb pattern must allow accents: `καλῶς` carries a circumflex, and a
pattern written `ως` silently never matches it.

### 借圖只看第一個義項，是 2026-08-27 才發現的漏

拉丁那副卡停在 40% 不是因為 OpenMoji 沒圖，是因為借圖只拿整串詞義、第一個
「；」段、第一個「、」段去對。拉丁詞義多半是三四個義項並列，於是
`libero`「解放、釋放」借不到已經有圖的「釋放」，`canticum`「聖歌、讚美詩」借不到
「讚美詩」。改成**逐義項依序比對**（第一義仍有優先權），一次撿回 333 張。

同時發現第二層：拉丁那本的中文用思高本，希伯來與希臘那兩本用《和合本修訂版》，
所以同一個概念兩邊寫法不同，圖借不過來——宗徒／使徒、聖神／聖靈、盟約／約。
`CATHOLIC_TO_PROTESTANT` 這張小表只放兩邊確實同指一物的對子。

代價要照規矩付：借來的圖記下 `borrowedVia`（循哪一個義項借的），非首義借來的
354 張逐張看過，錯配八張已覆蓋——「釋放」借到揮手（那是道別）、「歸還」借到站著
的人、「創建」借到錨（那是望德）、`ut` 借到 🔚（跟當初 `itaque` 一樣，目的的箭頭
不是終點，改成與希臘 ἵνα 同一個 🎯）、「洗禮」借到浴缸（同冊 `baptismus` 早就是
💧）。

## Picture matching

Strictest-first, and it refuses to guess:

1. **Hand-picked overrides**, named by the emoji's own name rather than a
   hexcode so a bad entry fails loudly. This is where the frequent core
   vocabulary lives, and where function words get their symbol —
   לֹא🚫, עַד🛑, אֲשֶׁר🔗, אֵין🕳️, לְמַ֫עַן🎯, ἵνα🎯, καί➕. 2,303 entries so far
   (Hebrew 806 by Strong number plus 4 by pointed form, Greek 1,493).
2. **Chinese-meaning transfer**, both ways and transitive. All five decks share
   one Traditional-Chinese gloss vocabulary, so a word whose meaning another deck
   has already pictured takes that picture: πῦρ and אֵשׁ are both 「火」 and both
   want the flame. Greek reads the Hebrew map, Hebrew reads the Greek map, and
   the Greek matcher runs a second pass over its own results so volume 2 inherits
   volume 1. Latin came third and reads both earlier maps, which is where 444
   of its 802 pictures came from — more than its 279 hand-picked overrides. Run
   the matchers alternately until the counts stop moving — two rounds is enough.

   A borrowed picture can still be wrong for the borrower. `itaque` 「因此、所以」
   arrived carrying 🔚 from whichever card shares that gloss; a conclusion is an
   arrow forward, not a stop. Overrides run first precisely so a deck can correct
   an inheritance without touching the deck it inherited from.

   Keep the loop variable out of the way here. Naming it `key` shadows the
   card's own `strong|pointed` and silently writes entries under their Chinese
   meaning instead, which the deck builder then cannot find. The matcher now
   asserts every key in the map resolves against the vocabulary.
3. **Exact match on the emoji's name**, never on its tag list.
4. **Nothing.** The card prints without a picture.

Rule three is not fussiness. Matching on tags scored 72% and produced בַּיִת
"house" as a potted plant, דֶּרֶךְ "way" as an exploding head and מַיִם "water" as
sweat droplets. `AMBIGUOUS_EN` additionally blocks English words whose senses
split — "watch" the verb against the wristwatch, "bear" the verb against the
animal — because Strong's glosses are English and English is full of them.

A wrong picture on a printed card teaches a sense the word does not carry, and
the learner cannot undo it. Blank beats wrong, every time.

### Filling the last 419 by hand, and what that taught

Picking a picture for every remaining word — including the abstract ones — is a
different job from matching, and it has its own failure modes:

- **Look at the artwork before trusting the name.** OpenMoji's `tap` is a finger
  tapping a screen, not a water tap; `wedding` is a church with a cross, which
  is a Christian building on a Hebrew Bible card; `assembly group` is an adult
  with a child. Render a contact sheet of every new pick (`PIL`, 110 px cells)
  and look at it before rebuilding the deck. Four wrong pictures were caught
  that way and none of them were catchable from the name.
- **Repeats are fine within a root, fatal across an opposition.** The deck has
  always let synonyms share a picture (門/出去/入口 all take the door), and a
  verb and its noun sharing one is a feature — רָעֵב and רָעָב both take 🤤,
  שָׁבָה and שְׁבִי both take the padlock. But 饑荒 must never take the same
  🍴 as 吃, and 管教 must never take the same ☝️ as 你: the card then teaches the
  opposite or an unrelated word. After each round, group the map by picture and
  read the glosses that share one.
- **Anachronism is a content error, not a style one.** Same rule as the Divine
  Name: no church for 新婦, no synagogue for 聖所 (`place of worship` 🛐 is the
  neutral one), but מְנוֹרָה does take the menorah — there it is the object
  itself, not a later symbol read back.
- **Function words take a symbol, not a scene.** 疑問助詞 ❓, כְּ ＝, לְ →,
  בְּ 🚩, מְעַט 🤏, עַד ♾️, בְּלִי 🪹.
- **Some OpenMoji names have no artwork.** `white square` (U+25A1) ships as a
  pink box with a cross through it — the set's own missing-glyph placeholder —
  and it printed on the 四方形的 card until the contact sheet caught it. Hash the
  file against that placeholder before trusting a name; `white large square` is
  the real square.
- **A picture can be wrong in the other direction.** `emergency exit door` shows
  a figure running *out*, so on 「領進」 it teaches the opposite; `ogre` is a
  Japanese oni and has no business illustrating 「蠻族人」; `passport control` is
  an officer checking papers, not a 「皈依者」; `bellhop bell` is room service,
  not 「關切」. All four were caught by looking, none by reading the name.
- **Four prefixes have no Strong number.** בְּ / כְּ / לְ / הֲ are keyed by their
  pointed form in `OVERRIDES_BY_FORM`, which the matcher consults when
  `entry["strong"]` is empty. Copy the form out of the vocabulary master rather
  than typing it: בְּ and כְּ carry a dagesh after the shva, and a hand-typed
  key silently matches nothing.

## Commands

```
python scripts/match_flashcard_images.py --write        # Hebrew picture map
python scripts/match_greek_card_images.py --write       # Greek picture map
python scripts/match_greek_card_images.py --uncovered 50  # what is still blank
python scripts/match_latin_card_images.py --write       # Latin picture map
python scripts/classify_proper_names.py --language all --write  # categories, before the appendix decks
python scripts/build_flashcards.py --deck hbo           # or grc1, grc2, lat1, lat2,
                                                       # hbo-appendix, grc-appendix, lat-appendix
python scripts/build_flashcards.py --deck hbo --limit 16   # proof sheet
```

`scripts/render_and_check_reader_pdfs.py --only <stem>` renders and checks page
geometry, embedded fonts, U+FFFD and blank pages in one step, for the decks and
the readers alike. To drive LibreOffice by hand instead, clear
`PYTHONHOME`/`PYTHONPATH` first: leaving them set makes `soffice` exit 0 having
written nothing.

```
env -u PYTHONHOME -u PYTHONPATH -u PYTHONIOENCODING \
  "C:/Program Files/LibreOffice/program/soffice.com" --headless --norestore \
  -env:UserInstallation=file:///<系統暫存>/lo-profile-cards \
  --convert-to pdf --outdir …/output/flashcards …/output/flashcards/<deck>.docx
```

## Checks worth running on a new deck

- Page count is `2 + 2 × ceil(cards / 8)`. Anything larger means the row spilled.
- No font falls back: every headword glyph should report the deck's own face, not
  Tahoma or Calibri. `pdfplumber` reports the font per character.
- The back sheet's leftmost card matches the front sheet's rightmost.
- Every key in the picture map resolves against the vocabulary master.
- Every back page carries exactly eight images once the deck is at full
  coverage: `len(page.images)` over the odd pages should be 8 for all 125 of
  them. A page with seven means one card lost its picture in the rebuild.
- Two Hebrew cards report Tahoma and that is expected, not a regression: the
  gloss lines 「弟兄；兄弟（אָח 的複數）」 and 「誡命（מִצְוָה 的不規則複數）」
  embed Hebrew inside the Chinese meaning run, which is set in the UI face.
  Headwords themselves never fall back.

## Next, if the owner asks for more

1. **Hebrew and Greek are both at 100%** and need no more overrides — the
   matchers' uncovered reports print empty. What is left in both is refinement:
   a picture that is merely adjacent to its word (肩膀 takes the prosthetic arm,
   下冊's abstract 樣式／形狀／組成 all take the puzzle piece) could be improved,
   but none of them is wrong.
2. **A paid Gemini key** would let image generation fill the rest with a style
   matched to the deck rather than to the emoji set. Check quota before promising
   anything; the free tier gave nothing.
3. **Latin coverage.** Both Latin decks are built. What they still lack is
   pictures: 46% and 35%. The uncovered head of the list is almost entirely
   abstract adverbs and particles — quasi, modo, scilicet, potius, ceterus,
   prius — which have no picture that is theirs rather than an illustration of
   some sentence they might appear in. Adding overrides for those would break
   the rule the decks are built on. The concrete nouns and verbs among the
   blanks are the ones worth a second pass.

### A gate that rejected good Chinese

The gloss checker called any text simplified if OpenCC's `s2t` changed it, and
`s2t` rewrites several characters that are already Traditional. 台 becomes 臺, so
「讀經台」 was refused eleven times running and `ambō` sat unglossed while the deck
refused to build. Worse, **祢 becomes 禰** — and 祢 is the Catholic second-person
honorific for God, which appears in nearly every prayer this project translates;
one of the readings is titled 《願祢受讚頌》. Every translation using it was being
thrown away and retried for ever.

Variants now pass individually while the line is otherwise clean, so 皇后 and
公里 are accepted and 以后我们 is still refused. 号 is deliberately not on the
list: that one really is simplified. Watch for this anywhere a
Traditional-Chinese gate is written as a round-trip comparison.
