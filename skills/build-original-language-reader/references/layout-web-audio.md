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

- Produce one vector spine artifact at the trim height of 257 mm when the print handoff requests a spine.
- Treat its width as printer-adjustable artwork, not as a paper-thickness or page-count calculation.
- Do not invent paper stock, caliper, binding allowance, or multiple width variants unless the user explicitly asks for them.
- Keep the title, palette, and typography consistent with the reader cover.
- Supply a PDF for handoff and an editable SVG so the printer can fit the art to the final die line.

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
