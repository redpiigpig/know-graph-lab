# Release contract

## Default full-reader counts

Freeze deviations before extracting or laying out content.

| Component | Default requirement |
|---|---:|
| Lessons | 50 |
| Vocabulary | 1,000 unique curriculum entries |
| Vocabulary per lesson | frozen per release. Hebrew: exactly 20, cut from one running order (BBH2 chapters 3-35, then the frequency extension). Greek: the BBG chapter's own count while the textbook lasts, then an even split of the extension |
| Memory units | 100 unique reviewed units |
| Memory units per lesson | 2 |
| Scripture chapters read | 25（篇幅上限之內；長章按節從章首連續節錄） |
| Prayers or articles read | 25（同上，按段節錄） |
| Main reading per lesson | 1 |
| 一課的頁數 | ≤ 8（擁有者 2026-09-17 定，硬上限） |
| 可讀文字的字級 | ≥ 12pt（眉標與頁碼除外） |
| Hebrew Haggadah appendix | 15 ordered steps, separate from the 25 texts |
| Hebrew reference tables | 4 appendix tables — numerals, kinship, calendar, classified proper names |

Patristic or rabbinic collections are separately declared appendices unless the user explicitly changes the 50-lesson allocation. Record whether each item is a complete short work or an authorized excerpt; never label an excerpt as a complete work.

**讀文的長度由版面決定，不由編輯決定（2026-09-17 起）。** 擁有者定的是「一課最多
八頁」，所以「二十五章完整經文」不再是契約的一部分——長章會按節從章首連續節錄到
版面預算為止（`scripts/reader_page_budget.py`）。隨之而來的三件事，少做一件就是在
宣告一件書裡沒有的事：

1. 每一篇讀文都要帶 `completeness` 與 `extent`／`extentZh`，紙本與線上都要印出來；
2. 封面副標、凡例、目錄、任何「本書收錄……」的句子，都不能再說「完整」；
3. 自我描述的字數（如 `counts.scriptureWords`）要數**印出來的那些**，不是 plan 裡
   原本有的那些——希臘上冊照 plan 報是 26,115 詞，書上其實只有 15,902 詞。

## Vocabulary contract

1. Retain the named textbook sequence exactly for every verifiable entry.
2. Record raw source order and canonical retained order separately. Keep aliases for exact duplicate textbook rows.
3. Extend only after the textbook inventory ends. Freeze corpus, frequency unit, tie-breaks, homograph identity, exclusion rules, and proper-name policy.
4. Use lexical identity, not unpointed/normalized spelling, as the primary key.
5. Preserve homographs and textbook-separated senses. Assign separate Strong/lemma/POS evidence.
6. Store a textbook-specific transliteration/phonetic field for every entry. Mark generated values as needing review unless a rule and exception set are verified.
7. Type proper names as any applicable combination of `person`, `place`, `people_or_nation`, and `divine_name_or_title`.
8. Keep `person`, `place` and `people_or_nation` names out of the lesson word list and put them in the classified proper-name appendix instead; a name printed in both places spends a lesson slot on a word the reader can look up. Backfill the vacated slots by walking the same corpus-frequency rule further down, and never let a lifted name re-enter through the backfill.
9. Divine names and titles stay in the lessons — יְהוָה occurs 6,521 times and אֱלֹהִים 2,600 — and so does any name-flagged word that is really ordinary vocabulary (אָדָם, נֶגֶב, שְׁאוֹל, יְאֹר). Record the reason on the entry; the appendix still lists them, cross-referenced to the lesson.
10. Key the Traditional-Chinese gloss layer by `(strong, pointed)`. A layer keyed by position silently shifts all 1,000 meanings the first time the word list is re-ordered.

## Memory contract

- Fix the vocabulary lesson before scoring candidates.
- Require unique stable references and two slots per lesson.
- Save at least: matched lesson terms, match count, known coverage, score, exclusion warnings, memorability rationale, reviewer status, and final selection reason.
- Prefer a memorable, syntactically complete verse over a marginally higher lexical score.
- Allow low-overlap exceptions only when explicitly reviewed and labelled. The last lessons carry the rarest words, and for some of them no verse in the corpus contains two at once; take a single-match verse there and mark it rather than padding the lesson.
- Re-select whenever lesson membership changes, and re-stamp the review status. A verse hand-picked for the previous word list is not reviewed for the new one, and saying otherwise in the plan file is a false claim.

## Reference-table contract

Numerals, kinship terms and calendar words are not a category in a frequency-ordered curriculum: they land wherever the textbook and the corpus put them, so the learner has no page to look them up on. Give them appendix tables, and build every row from a frozen source rather than by hand.

- Take each pointed form from the corpus itself, and record how often that exact spelling occurs. Hand-typed niqqud is the single largest source of silent error here.
- Normalise to NFC before comparing. The WLC writes the shin dot before the vowel, the opposite of canonical order, so an untouched comparison never matches.
- Where a word has no absolute occurrence — חֲמוֹת, יָבָם and the other suffix-only kinship terms — quote the lexicon's citation form and label the row as such.
- Mark what is not in the text. Five of the twelve Babylonian month names appear only in post-biblical Jewish sources; they carry `attestation: post_biblical` and their own source note, and their Chinese is flagged as conventional rather than the approved Bible version's.

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
