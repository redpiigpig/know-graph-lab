# Printable flashcard decks

The reader's vocabulary masters also drive printed decks: Hebrew 1,000 cards,
Greek volume 1 and volume 2 at 1,000 each. They follow the household's existing
English tutoring deck (`家教單字卡.pdf` on the desktop) so the same guillotine
and the same printer settings work for all of them.

## State, 2026-08-25

| Deck | Cards | Pages | With picture | Part of speech blank | File |
|---|---:|---:|---:|---:|---|
| 聖經希伯來文 | 1,000 | 252 | 581 (58%) | 0 | `output/flashcards/hebrew-flashcards-1000.pdf` |
| 通用希臘文・上冊 | 1,000 | 252 | 627 (63%) | 276 | `output/flashcards/greek-flashcards-volume-1.pdf` |
| 通用希臘文・下冊 | 1,000 | 252 | 293 (29%) | 447 | `output/flashcards/greek-flashcards-volume-2.pdf` |

All three are built, rendered, verified and pushed. DOCX sits beside each PDF.

**The Greek decks are another session's work from 2026-08-25 onward.** The owner
reassigned them. Do not regenerate `greek-card-images.json`, the Greek deck files
or `match_greek_card_images.py` unless the owner says the assignment has changed.
Reading the Greek picture map is fine and expected — the Hebrew matcher does it
for meaning transfer.

### What the owner has decided

- **Every card should carry a picture.** Their reasoning: a physical deck only
  earns its keep if the picture aids memory, otherwise study online. Coverage is
  therefore a live target, not a finished number. Raising it means adding
  overrides by hand.
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
| Card | 74.25 × 94 mm |
| Margins | 5 mm top and bottom, 0 left and right |
| Cuts | horizontal 5 / 99 / 193 mm from the top, vertical 74.25 / 148.5 / 222.75 mm from the left |
| Duplex | long-edge flip; the back sheet mirrors the column order 4-3-2-1 |

**The card height is measured, not derived.** The renderer reserves more vertical
space than the declared margins account for and drops the second row onto a page
of its own long before the arithmetic says it should: a 10 mm margin fails where
5 mm holds, and 97 mm rows fail where 94 mm hold. If the page count comes out at
double what it should be, that is what happened — shrink the row, do not reason
about it. Setting `row.height` and then appending a second `w:trHeight` leaves
two competing rules in the XML and produces the same symptom.

## Card faces

Front carries the headword and the lesson. Back carries the picture (when there
is one), the Traditional-Chinese meaning, the part of speech and the lesson. The
meaning line is sized from its own length — the glosses run from two characters
to twenty-seven — rather than set once and allowed to overflow. Greek citation
forms are long (`ἄνθρωπος, -ου, ὁ`), so the headword shrinks by length too.

Hebrew reads its part of speech from the vocabulary master. Greek has none, so
`scripts/flashcard_pos.py` works it out from the citation form (an article makes
a noun, three terminations an adjective, a first-person form a verb) and from the
Chinese gloss where the form is silent (`（配屬格）` marks a preposition, a gloss
whose senses all end in 「的」 an adjective), with hand lists for the function
words and the irregular verbs. It settles about 64% and prints nothing for the
rest. **A blank line costs nothing; a wrong label is learned as fact.**

## Picture matching

Strictest-first, and it refuses to guess:

1. **Hand-picked overrides**, named by the emoji's own name rather than a
   hexcode so a bad entry fails loudly. This is where the frequent core
   vocabulary lives, and where function words get their symbol —
   לֹא🚫, עַד🛑, אֲשֶׁר🔗, אֵין🕳️, לְמַ֫עַן🎯, ἵνα🎯, καί➕. 1,003 entries so far.
2. **Chinese-meaning transfer**, both ways and transitive. The three decks share
   one Traditional-Chinese gloss vocabulary, so a word whose meaning another deck
   has already pictured takes that picture: πῦρ and אֵשׁ are both 「火」 and both
   want the flame. Greek reads the Hebrew map, Hebrew reads the Greek map, and
   the Greek matcher runs a second pass over its own results so volume 2 inherits
   volume 1. Run the matchers alternately until the counts stop moving — two
   rounds is enough.

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

## Commands

```
python scripts/match_flashcard_images.py --write        # Hebrew picture map
python scripts/match_greek_card_images.py --write       # Greek — another session owns this
python scripts/build_flashcards.py --deck hbo           # or grc1, grc2
python scripts/build_flashcards.py --deck hbo --limit 16   # proof sheet
```

Then render the DOCX to PDF with LibreOffice. Clear `PYTHONHOME`/`PYTHONPATH`
first: leaving them set makes `soffice` exit 0 having written nothing.

```
env -u PYTHONHOME -u PYTHONPATH -u PYTHONIOENCODING \
  "C:/Program Files/LibreOffice/program/soffice.com" --headless --norestore \
  -env:UserInstallation=file:///…/output/lo-profile-cards \
  --convert-to pdf --outdir …/output/flashcards …/output/flashcards/<deck>.docx
```

## Checks worth running on a new deck

- Page count is `2 + 2 × ceil(cards / 8)`. Anything larger means the row spilled.
- No font falls back: every headword glyph should report the deck's own face, not
  Tahoma or Calibri. `pdfplumber` reports the font per character.
- The back sheet's leftmost card matches the front sheet's rightmost.
- Every key in the picture map resolves against the vocabulary master.

## Next, if the owner asks for more

1. **More overrides.** The remaining blanks, by deck and by frequency, come from
   the matcher's own report — it prints the highest-frequency uncovered words on
   every run. Hebrew is the one this session owns.
2. **A paid Gemini key** would let image generation fill the rest with a style
   matched to the deck rather than to the emoji set. Check quota before promising
   anything; the free tier gave nothing.
3. **Latin.** `project_latin_original_reader` finished its data layer on
   2026-08-25, so a third language could take the same treatment. Nobody has
   asked yet.
