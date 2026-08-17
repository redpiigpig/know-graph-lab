# Release contract

## Default full-reader counts

Freeze deviations before extracting or laying out content.

| Component | Default requirement |
|---|---:|
| Lessons | 50 |
| Vocabulary | 1,000 unique curriculum entries |
| Vocabulary per lesson | 20 |
| Memory units | 100 unique reviewed units |
| Memory units per lesson | 2 |
| Complete Scripture chapters | 25 |
| Complete prayers or articles | 25 |
| Main reading per lesson | 1 |
| Hebrew Haggadah appendix | 15 ordered steps, separate from the 25 texts |

Patristic or rabbinic collections are separately declared appendices unless the user explicitly changes the 50-lesson allocation. Record whether each item is a complete short work or an authorized excerpt; never label an excerpt as a complete work.

## Vocabulary contract

1. Retain the named textbook sequence exactly for every verifiable entry.
2. Record raw source order and canonical retained order separately. Keep aliases for exact duplicate textbook rows.
3. Extend only after the textbook inventory ends. Freeze corpus, frequency unit, tie-breaks, homograph identity, exclusion rules, and proper-name policy.
4. Use lexical identity, not unpointed/normalized spelling, as the primary key.
5. Preserve homographs and textbook-separated senses. Assign separate Strong/lemma/POS evidence.
6. Store a textbook-specific transliteration/phonetic field for every entry. Mark generated values as needing review unless a rule and exception set are verified.
7. Type proper names as any applicable combination of `person`, `place`, `people_or_nation`, and `divine_name_or_title`.

## Memory contract

- Fix the vocabulary lesson before scoring candidates.
- Require unique stable references and two slots per lesson.
- Save at least: matched lesson terms, match count, known coverage, score, exclusion warnings, memorability rationale, reviewer status, and final selection reason.
- Prefer a memorable, syntactically complete verse over a marginally higher lexical score.
- Allow low-overlap exceptions only when explicitly reviewed and labelled.

## Reading contract

- Scripture chapters contain every source verse position, including explicitly handled title or combined-verse crosswalks.
- Prayers/articles contain complete declared textual units with stable segments and sources.
- The immutable source text remains available beside any editorial display text.
- Every Bible translation is versioned and mapped from the source tradition's numbering.

## Completion states

Use the narrowest true state:

- `planned`
- `source_frozen`
- `vocabulary_complete`
- `content_complete_layout_pending`
- `content_complete_audio_pending`
- `print_qa_passed_audio_pending`
- `release_candidate`
- `complete_private_release`

`complete_private_release` requires every configured print, web, audio, rights, and QA gate. A missing required audio track, stale render, incomplete full build, or placeholder prevents completion.
