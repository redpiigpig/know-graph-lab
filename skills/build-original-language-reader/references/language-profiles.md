# Language profiles

## Biblical Hebrew

### Curriculum and lexical data

- Primary order: Pratico–Van Pelt, *Basics of Biblical Hebrew* in the user-authorized edition.
- Extend after the verified textbook rows using a frozen WLC/OSHB lemma-frequency rule.
- Keep full niqqud in every headword and running learner text. Preserve cantillation, maqaf, sof pasuq, paseq, qere, and ketiv provenance.
- Treat shureq (`וּ`) and mater lectionis correctly; a validator that only checks U+05B0–U+05BB is insufficient.
- Do not accept “at least one vowel per token” as proof of full pointing.
- Store immutable ketiv/source and pointed-qere/display layers separately.
- Use Pratico–Van Pelt textbook transliteration, including lexical exceptions. Do not substitute modern Israeli pronunciation.
- Preserve aleph (`ʾ`) and ayin (`ʿ`) according to the textbook. Qamets/qamets-hatuf and shewa require lexical/syllabic review; character-only transliteration is not automatically verified.

### Proper names

Type persons, places, peoples/nations, and divine names/titles. Mixed-sense lemmas may have multiple types. Do not classify from loose English substrings such as `man` or from “name of N Israelites” as a people group.

### Texts and appendices

- Scripture base: exact frozen WLC/OSHB edition.
- Current Traditional-Chinese parallel: 《和合本修訂版》（2010）, with variant explicit. In `know-graph-lab` the current frozen source is RCUV2（上帝版）.
- Route Psalm superscriptions, Isaiah 9, Hosea 14, and any other observed numbering difference through one tested crosswalk.
- Hebrew appendix: complete fifteen-step Haggadah. Preserve source text and mark editorial pointing.

### Typography and audio

- RTL paragraphs; mixed Chinese and transliteration remain LTR where appropriate.
- Use a Hebrew font that retains all niqqud/cantillation anchors and embeds in PDF.
- Audio profile: Biblical/Masoretic pedagogical pronunciation matching the textbook. Modern-Hebrew TTS is not an acceptable substitute.

## Biblical or Patristic Greek

### Curriculum and lexical data

- Primary source: the exact user-specified Mounce edition and verified chapter vocabulary order.
- Treat *A Graded Reader of Biblical Greek* as a reading sequence unless an authorized exact word order is verified; do not invent a vocabulary sequence from it.
- Reassign vocabulary to the frozen lesson contract. A source grouped as 20 × 50 is not automatically a 50 × 20 curriculum.
- Preserve polytonic accents, smooth/rough breathing, diaeresis, iota subscript, and final sigma. Normalize to NFC for canonical display while retaining raw source form.
- Use the Mounce textbook transliteration/pronunciation standard. Keep Erasmian, reconstructed Koine, and modern Greek as separately named profiles/tracks.
- Disambiguate accent/breathing homographs before assigning Strong numbers or glosses.

### Texts and appendices

- Freeze NT and LXX/deuterocanonical editions separately. Never imply that one version covers the other.
- Use RCUV2010 for canonical Bible parallels; freeze an authorized Traditional-Chinese source separately for deuterocanonical books.
- A Greek Fathers collection must identify author/work/section and state whether each item is complete or an authorized excerpt.

### Typography and audio

- LTR text with a fully polytonic-capable embedded font.
- Do not use modern Greek TTS as the Mounce recording track. A real track records profile, reader, rate, checksum, rights, and cues.

## Ecclesiastical Latin

### Curriculum and lexical data

- Freeze a textbook or explicitly approved frequency corpus before assigning 1,000 words. Do not convert a placeholder plan into a completed vocabulary list.
- Store dictionary principal parts and the selected inflected display form.
- Preserve source `u/v`, `i/j`, capitalization, punctuation, and ligatures. Put search normalization in a separate field.
- If macrons or stress marks are editorial, retain the unmodified source form and label the added layer.
- Default pronunciation profile is Ecclesiastical Latin when so specified. Classical reconstructed pronunciation requires a separate track and label.

### Texts and appendices

- Distinguish Clementine Vulgate, Stuttgart Vulgate, and Nova Vulgata. Freeze one exact edition per reading.
- Route Vulgate/Psalm numbering differences through a tested crosswalk to RCUV2010.
- Latin Fathers must use exact original Latin source locations; do not substitute Schaff English or an unlabelled modern translation.
- Record whether the Ordo or prayer source is historical/public-domain, modern-edition authorized, or an excerpt.

### Typography and audio

- LTR; use an embedded font with required diacritics and ligatures.
- Audio profile is explicitly Ecclesiastical or Classical. Never merge pronunciations within one unlabelled track.
