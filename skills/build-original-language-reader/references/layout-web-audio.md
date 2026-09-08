# Layout, web, and audio

## JIS B5 print profile

Default physical specification:

- trim: 182 × 257 mm;
- mirrored margins;
- inside 24 mm;
- outside 17 mm;
- top 18 mm;
- bottom 20 mm.

Use the frozen reader profile if the user approves a different specification.

## One shared layout across the three readers

The Hebrew builder is the standard; Greek and Latin import its size constants
and must match its *structure* too, not just its scale. Checked 2026-08-27:

- **Section headings are real headings.** `document.add_heading(..., level=2)`
  at 14 pt, never the 8.2 pt all-caps eyebrow. Greek printed 「生詞／背誦／讀文」
  through `add_label` for months — section headings smaller than the 11.5 pt
  body text. The eyebrow is for the line *above* a heading, never instead of one.
- **Heading scale**, from `build_hebrew_full_reader`: title 24, H1 17, H2 14,
  H3 12.5, body 11.5, tables 9.6, label 8.2. Nothing that acts as a heading may
  sit below the body size.
- **Cover**: dark banner table (`ACCENT_DARK`) holding a gold `ORIGINAL-LANGUAGE
  READER` eyebrow, the book name at 25 pt, and one line of the source script;
  then the volume line, a gold rule, and the `JIS B5 182 × 257 mm · 私人研讀`
  spec line. Three books side by side have to read as one series.
- **Lesson opener**: `add_label(..., page_break_before=True)` → 第 NN 課 →
  `add_heading(level=1)` → `paragraph_rule(..., color=GOLD)`.
- **Each lesson's reading starts a new page.** Vocabulary and memory units are
  preparation; the reading is the lesson itself and should begin at the top of
  a page. This is a `page_break()` inside the reading function, so no call site
  can forget it.
- **Running head and page number** (2026-09-08). 頁尾置中印頁碼，眉標印
  `書名  ·  第 NN 課`。課次不逐頁寫死，用 Word 的 `STYLEREF` 欄位指向
  `RUNNING_STYLE`（"Running Tag"）：每課開頭那行「第 NN 課」套上該樣式
  （`mark_running_tag()`），欄位就印出這一頁所屬那一課，一課跨幾十頁都對。
  非課文的部分不能沿用課次，否則附錄整區會謊稱自己是第 50 課——所以全書切成
  三節（卷首／課文／附錄），每節一個眉標，由 `start_section()` 開節。
  **分節符自己就會換頁**：接在它後面的開場不可以再帶 `page_break_before`，
  不然每一部之間多一張白紙（`add_lesson_opener`／`add_liturgy`／
  `appendix_section` 的第一個都因此要傳 `page_break_before=False`）。
- **A bound volume may not exceed 500 pages, and volumes of one language should
  be about equally thick** (2026-09-08). The lesson data is unchanged; what
  changed is how many physical books it prints as. Split only between lessons,
  never renumber a lesson (the online reader and the audio routes key on it),
  and print each half's appendix in its last part only — repeating a 125-page
  appendix in every part pushes them back over the cap. The splits live in each
  builder's `PARTS`: Greek 6 volumes of 262–301 pages, Latin 3 of 416–456,
  Hebrew 1 of 401. Greek's first two are the thin ones because its 524-page
  first half can only halve. `render_and_check_reader_pdfs.py` fails the build
  over 500.
- **Appendix tables print grouped**, in `PRINT_ORDER` from
  `scripts/proper_name_categories.py`, with the group heading at H2/H3.
- **No print caps.** Latin capped appendix groups at 200 rows to hold the page
  count down; 385 of the 585 upper-volume proper names never reached paper. An
  appendix you cannot look things up in is not worth the paper it saves.

Verify with `scripts/render_and_check_reader_pdfs.py`: it converts each DOCX
through LibreOffice (a separate `UserInstallation` profile per file — LibreOffice
allows only one at a time) and checks page geometry, embedded fonts, U+FFFD, and
blank pages. Note `□ U+25A1` is a real glyph in the Hebrew reader's 「完成本課」
checklist; do not flag it as a missing glyph.

## DOCX rules

- Generate from the authoritative master, never from UI HTML.
- Use semantic styles, real headings, page fields, and table headers.
- Set RTL at paragraph/run level for Hebrew; keep Chinese and transliteration direction correct.
- Prevent vocabulary rows from splitting across pages.
- Repeat table headers and set explicit table geometry/indent.
- Attach a page break to the actual following heading; do not create empty break paragraphs.
- Keep headings with following content and prevent orphaned “notes” headings.
- Let genuinely long running-text paragraphs split naturally; forcing a long Haggadah segment together causes clipping or overflow.
- Avoid unconditional note-line blocks that create near-empty overflow pages.
- Use Unicode fonts with the required language coverage. Never rely on Word defaults such as Calibri, Tahoma, or MS Gothic.

## Interlinear rules

- Print each word block as Hebrew above, Traditional-Chinese gloss below, then close the unit with one whole-sentence line.
- Lay word blocks right to left (`w:bidiVisual` on the row) so block order matches reading order.
- Measure each word with the real print font and pack rows to the text-block width. Absorb the leftover into one trailing filler column; never stretch the blocks to justify, or a short final row floats in the middle of the measure.
- Give the verse or segment number the first block of the first row, at the right margin.
- A source segment carrying no letters of the source script (a rule such as `-----`) prints as a rule, not as literal characters with an empty gloss.
- Web renders the same data with a wrapping RTL flex row; it must degrade to a plain source-language line for any unit not yet glossed rather than showing empty gloss slots.

## PDF rules

- Preserve exact B5 size on every page.
- Embed Hebrew/Greek/Latin and Traditional-Chinese font families.
- Keep searchable source-language and Chinese text layers.
- Reject missing glyph boxes, replacement characters, font substitution, clipping, footer collisions, duplicate pages, and accidental blank pages.
- Rasterize the final PDF only after the final DOCX build. Any content/style change invalidates the render.

## B5-height spine artwork

`scripts/build_reader_spines.py` draws one spine per **physical** volume — ten of
them as of 2026-09-08 — and is run after the print masters render, because it
measures them.

- Height is the B5 trim, 257 mm, always.
- Width comes from that volume's own page count: `頁數 ÷ 2 × 0.105 mm + 1.0 mm`
  (80 gsm woodfree plus cover board). Until 2026-09-08 the single Hebrew spine
  carried a fixed 16 mm artwork width instead; that stopped being defensible when
  the volumes ranged from 262 to 456 pages, i.e. 14.8 mm to 24.9 mm of spine. A
  printer on different stock re-runs with `--sheet`.
- A volume with no rendered master gets no spine and is reported as missing. The
  thickness is measured from the book, never guessed.
- Palette follows the cover: one colour per language (`COVER_PALETTES`), title
  set vertically in ivory, 冊次 under it in the accent, gold rule and year at the
  foot.
- Ship both the PDF (handoff) and the SVG (editable to the printer's die line).

## Never fall back to another language to fill a hole

The Latin appendix printer read `zh or glossZh or glossEn`. Three of its tables
were built carrying only Whitaker's English, so a Traditional-Chinese reader
printed whole pages of `mother's brother` and `the day before the Kalends` — and
nothing on the page said whether that was a gap or the design. Print the empty
state instead: `（中文待補）`, small and muted. A defaulting fallback hides the
very hole it is standing in.

## Authenticated web counterpart

Required surfaces:

- reader overview;
- one lesson route with vocabulary, memory units, full reading, and pronunciation state;
- each configured appendix route;
- authenticated data APIs.

Required response controls:

```text
requireAuth
X-Robots-Tag: noindex, nofollow, noarchive
Cache-Control: private, no-store
Vary: Authorization
```

Do not place private JSON or audio under `public/`. Validate invalid lesson numbers, empty source segments, and missing translations. The web reader must use the same master/crosswalk as print.

## Audio

### Track requirements

Each real track records:

- track ID and language;
- historical/textbook pronunciation profile;
- reader/speaker role;
- speed/rate;
- duration and file checksum;
- recording/source rights;
- review status;
- segment cue coverage.

Cues must be ordered, non-overlapping, within duration, and cover every declared segment according to the release contract.

### Honest missing-audio state

Use a state such as:

```json
{
  "status": "not_recorded",
  "recordedTrackCount": 0,
  "policy": "No play control until a reviewed track exists."
}
```

An external textbook link may be shown as a reference. Browser/device TTS may be a clearly labelled provisional locator but never satisfies a required historical pronunciation track.

### Where device speech is the deliverable, not a placeholder

Latin is the exception, by the owner's decision (2026-08-27): its audio lives on
the web page and there is no recorded track to wait for. That is defensible only
because Roman ecclesiastical pronunciation is Italian phonology, so an Italian
voice reading Italian-spelled Latin is *correct*, not approximate — see
`utils/ecclesiasticalLatin.ts` and the Latin contract.

Hebrew and Greek keep the old rule. Modern Israeli Hebrew merges the contrasts
BBH2 teaches and Modern Greek is not Koine; for those two, device speech stays a
labelled locator.

The shared controller is `composables/useOriginalReaderAudio.ts`:
`playDevice(language, segments)` walks a list with `currentSegmentId` for the
highlight, `speakOne(language, text)` reads one line or one word, `rate` is
shared, and `SPEECH_TEXT` holds the per-language rewrite. Warm `getVoices()` on
mount — Chrome returns an empty list on the first call, and without the warm-up
the first click reports a missing voice that is installed.
