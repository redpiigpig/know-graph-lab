# Data model

Keep one master JSON as the authority for print and web outputs. Source snapshots remain separate and immutable.

## Contents

- Release master
- Source record
- Vocabulary entry
- Text segment
- Interlinear layer
- Lesson
- Audio manifest
- Build provenance

## Release master

Required top-level fields:

```json
{
  "schemaVersion": "1.0.0",
  "languageCode": "hbo|grc|la",
  "privateUse": true,
  "releaseStatus": "content_complete_audio_pending",
  "printProfile": {},
  "counts": {},
  "textPolicy": {},
  "sources": {},
  "lessons": [],
  "appendices": [],
  "audio": {},
  "build": {}
}
```

## Source record

Record each rights layer separately:

```json
{
  "work": "ancient work title",
  "edition": "exact modern edition",
  "versionCode": "stable-code",
  "sourceUrl": "https://...",
  "localPath": "...",
  "sha256": "...",
  "workRights": "public-domain|authorized|unknown",
  "editionRights": "authorized",
  "transcriptionRights": "authorized",
  "translationRights": "authorized",
  "useScope": "private-authorized",
  "checkedAt": "ISO-8601"
}
```

## Vocabulary entry

Required common fields:

```json
{
  "id": "hbo-vocab-0001",
  "ordinal": 1,
  "lesson": 1,
  "lessonSlot": 1,
  "sourceOrder": 1,
  "sourceOrders": [1],
  "sourceType": "textbook_order",
  "surface": "...",
  "canonical": "...",
  "searchKey": "...",
  "lemma": "...",
  "strongs": [],
  "partOfSpeech": "...",
  "frequency": 0,
  "glossZh": "...",
  "textbookTransliteration": "...",
  "transliterationSystem": "...",
  "isProperName": false,
  "properNameTypes": [],
  "verification": "source_and_lexicon_matched"
}
```

Never use stripped spelling as a unique identifier. Store alternative spellings, homograph group, and multi-lexeme analyses explicitly.

## Text segment

```json
{
  "id": "stable-segment-id",
  "ordinal": 1,
  "ref": "Gen.1.1",
  "sourceText": "immutable source text",
  "displayText": "learner-facing text",
  "translationZh": "...",
  "sourceVersionCode": "wlc-4.20",
  "translationVersionCode": "cuv2010",
  "crosswalk": {"sourceRef": "...", "translationRef": "..."},
  "sourceSha256": "...",
  "displayPolicy": "pointed-qere",
  "notes": []
}
```

Combined translation verses may map more than one source position to one translation unit. Preserve both source positions, record the range, and do not invent a split translation.

## Interlinear layer

A reader whose only Chinese is one whole-verse translation per verse teaches nothing about which word means what. Every running-text unit therefore carries a word-by-word layer, keyed by unit id in its own master:

```json
{
  "id": "bible:Ps.136.1",
  "kind": "bible_verse|memory_verse|prayer_segment|haggadah_segment",
  "ref": "Ps.136.1",
  "text": "the exact printed string this layer was built from",
  "tokens": [{"ordinal": 1, "word": "הוֹד֣וּ", "trailing": "", "glossZh": "你們要稱謝"}],
  "senseZh": "whole-unit meaning; required wherever no published translation exists",
  "engine": "model id"
}
```

Rules:

- Tokenise the **printed** string, never a normalised one, so the gloss row always aligns with the words the learner sees. Whitespace separates tokens; a maqqef also splits while staying attached to the word it follows; sof pasuq, paseq and modern punctuation ride in `trailing` and never consume a gloss slot.
- Store one contextual gloss per token — the meaning in this sentence, with prefixes and pronominal suffixes translated into it — not a dictionary dump.
- Reject a unit whose gloss count differs from its token count, and reject glosses containing source-script or Latin text.
- Anchor glosses to the curriculum's own reviewed word list so the interlinear and the vocabulary tables never disagree.
- Consumers align by word sequence, because print may strip a leading title that the data layer still carries.
- Where the reading has a published translation (Scripture), that translation is the whole-sentence line; where it does not (prayers, articles, Haggadah), `senseZh` is required and also fills the empty `translationZh`.

## Lesson

```json
{
  "lesson": 1,
  "id": "hbo-lesson-01",
  "vocabulary": [],
  "memoryUnits": [],
  "reading": {},
  "audioTrackIds": []
}
```

## Audio manifest

Use this shape only for an existing reviewed recording:

```json
{
  "trackId": "hbo-lesson-01-reading",
  "profile": "biblical-masoretic-pedagogical-bbh2",
  "speakerRole": "reviewed-reader",
  "rate": 1.0,
  "durationMs": 0,
  "path": "private/audio/...",
  "sha256": "...",
  "rights": "private-authorized",
  "reviewStatus": "reviewed",
  "cues": [{"segmentId": "...", "startMs": 0, "endMs": 0}]
}
```

When audio is not recorded, use the release-level state below and omit track paths and cues:

```json
{
  "status": "not_recorded",
  "recordedTrackCount": 0,
  "tracks": [],
  "policy": "No play control until a reviewed track exists."
}
```

## Build provenance

Connect source snapshot hashes, master hash, DOCX hash, PDF hash, page-render hash set, web-data hash, and audio manifest hash. Regenerate the chain after any upstream change.
