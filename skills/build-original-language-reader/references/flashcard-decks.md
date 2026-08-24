# Printable flashcard decks

The reader's vocabulary masters also drive printed decks: Hebrew 1,000 cards,
Greek volume 1 and volume 2 at 1,000 each. They follow the household's existing
English tutoring deck (`家教單字卡.pdf`) so the same guillotine and the same
printer settings work for all of them.

## Sheet

| | |
|---|---|
| Page | A4 landscape, 297 × 210 mm |
| Grid | 4 columns × 2 rows, 8 cards a sheet |
| Card | 74.25 × 94 mm |
| Margins | 5 mm top and bottom, 0 left and right |
| Cuts | horizontal 5 / 99 / 193 mm from the top, vertical 74.25 / 148.5 / 222.75 mm from the left |
| Duplex | long-edge flip; the back sheet mirrors the column order 4-3-2-1 |

**No cutting lines are printed.** A hairline that prints a millimetre off leaves
every card with a crooked edge, so the grid is even and the cover sheet carries
the measurements instead.

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
to twenty-seven — rather than set once and allowed to overflow.

Hebrew reads its part of speech from the vocabulary master. Greek has none, so
`scripts/flashcard_pos.py` works it out from the citation form (an article makes
a noun, three terminations an adjective, a first-person form a verb) and from the
Chinese gloss where the form is silent (`（配屬格）` marks a preposition, a gloss
whose senses all end in 「的」 an adjective), with hand lists for the function
words and the irregular verbs. It settles about 64% and prints nothing for the
rest. **A blank line costs nothing; a wrong label is learned as fact.**

## Pictures

Source is OpenMoji 17.0.0 (CC BY-SA 4.0), one consistent cartoon style, cited on
each deck's cover. The 44 MB artwork is not in git;
`scripts/match_flashcard_images.py` downloads it on demand.

Matching runs strictest-first and refuses to guess:

1. **Hand-picked overrides**, named by the emoji's own name rather than a
   hexcode so a bad entry fails loudly. This is where the frequent core
   vocabulary lives, and where function words get their symbol —
   לֹא🚫, עַד🛑, אֲשֶׁר🔗, אֵין🕳️, לְמַ֫עַן🎯, ἵνα🎯, καί➕.
2. **Chinese-meaning transfer**, both ways and transitive. The three decks share
   one Traditional-Chinese gloss vocabulary, so a word whose meaning another deck
   has already pictured takes that picture: πῦρ and אֵשׁ are both 「火」 and both
   want the flame. Greek reads the Hebrew map, Hebrew reads the Greek map, and
   the Greek matcher runs a second pass over its own results so volume 2 inherits
   volume 1. Run the two matchers alternately until the counts stop moving —
   two rounds is enough.

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

Coverage as it stands: Hebrew 579/1000, Greek volume 1 627/1000, volume 2
293/1000, from 1,001 hand-picked overrides plus transfer. Volume 2 is patristic
vocabulary and mostly abstract, which is why it trails. Raising coverage further
means adding overrides, always by hand.

יְהוָה is deliberately blank. Whether the Divine Name takes a picture is the
reader's decision, not the script's.

## Commands

```
python scripts/match_flashcard_images.py --write        # Hebrew picture map
python scripts/match_greek_card_images.py --write       # Greek picture map
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
  a UI font. `pdfplumber` reports the font per character.
- The back sheet's leftmost card matches the front sheet's rightmost.
