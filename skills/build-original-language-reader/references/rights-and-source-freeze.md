# Rights and source freeze

## Separate the rights layers

For every text or recording, record these independently:

1. Ancient work or public-domain composition.
2. Modern critical or liturgical edition.
3. Digital transcription or database.
4. Modern translation.
5. Pronunciation recording.
6. Font/software license.

An ancient work being public domain does not make a modern edition, transcription, translation, or recording freely redistributable.

## Private authorized use

When the user states that authorization has been obtained:

- Record `useScope: private-authorized` and the exact edition/variant.
- Do not ask the user to republish proof or place it in a public repository.
- Keep authorized full text and audio behind authenticated routes and outside public static folders.
- Use `Cache-Control: private, no-store`, `Vary: Authorization`, and noindex/noarchive headers.
- Do not deploy, share, export, or publish without a separate explicit request.

## Freeze manifest

Before transformation, create a source manifest with:

- stable source ID;
- work/author/title/section;
- language and text tradition;
- edition/version code and publication year;
- exact local path or URL;
- source and content SHA-256;
- retrieval/check date;
- immutable source-text policy;
- rights for each layer;
- selected Bible translation and named variant;
- known versification/orthography differences.

## RCUV2010 rules

- Do not equate `ChiUn`, CUV1919, and RCUV2010.
- Freeze `RCUV1（神版）` or `RCUV2（上帝版）` explicitly. They are not interchangeable labels.
- Record `© 香港聖經公會` and the user's private authorization scope.
- Keep the official/supplied source snapshot private.
- Preserve official combined verse ranges. Map multiple source positions to the combined unit instead of inventing separate translated clauses.
- A translation or source update invalidates master, DOCX, PDF, web data, and all prior QA.

## Source conflict policy

When sources disagree:

1. Do not silently choose the most frequent or highest-ranked candidate.
2. Preserve both raw observations.
3. Resolve by edition, vocalization/accent, gloss, POS, morphology, and explicit human override.
4. Store the decision and evidence.
5. Leave unresolved metadata blank or `needs_review`; never mark rule-generated output as verified without review.

## Forbidden skill assets

Do not bundle textbook vocabulary tables, RCUV2010 text, modern critical editions, complete licensed prayers, recordings, or non-redistributable fonts inside this skill. Bundle workflow, schemas, validation code, and empty examples only.
