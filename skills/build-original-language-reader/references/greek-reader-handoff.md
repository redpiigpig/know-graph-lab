# Greek reader — handoff, 2026-08-24

Written so another session can pick this up cold, and so the Hebrew session can
push the Greek work along with its own. Read
[`greek-reader-contract.md`](greek-reader-contract.md) first; this file records
where the work actually stands, not what it should eventually be.

## Push state — read this first

Two commits are finished and **unpushed**. List them with:

```
git log --oneline origin/master..HEAD
```

You should see these two subjects (SHAs are not quoted here — they move if a
commit is amended):

```
feat(grc-reader): 專名中文補到 84%，其餘照實留空
docs(grc-reader): 改寫凍結契約為兩冊制，並補交接文件
```

They are on `master`, tests-clean on their own, and blocked only by the pre-push
hook. An earlier Greek commit, `上冊排成五十章…`, is already on `origin` — the
parallel session carried it up with one of its own pushes.

The hook fails on three tests in `tests/original-readers.test.ts`, all of them
under **Hebrew reader curriculum** / **complete 50-lesson Hebrew private reader**:

```
× reserves 50 consecutive BBH lessons sized by the textbook's own chapters
    expected [ …(544) ] to have a length of 552 but got 544
× pins BBH homographs, aleph transliteration, POS metadata, and required names
× assembles all requested content without placeholders
    TypeError: Cannot read properties of undefined (reading 'trim')
```

Those come from the parallel Hebrew work in this same tree — `hebrew-1000.json`
is modified and `hebrew-proper-names.json` / `hebrew-appendix-seed.json` are new
and untracked. The Hebrew reader is evidently having its proper names moved to an
appendix and its lesson list backfilled, exactly as the Greek one just was, and
its tests have not caught up. **Nothing in the Greek work touches Hebrew data.**
`tests/greek-full-reader.test.ts` passes 12/12.

So: fix or update those three Hebrew assertions, then push both. Do not use
`--no-verify`, and do not revert the other session's files.

## What changed, and why

The owner replaced the curriculum on 2026-08-24. It is now **two volumes of fifty
lessons, twenty words each**, 2,000 words total — not the earlier single volume
whose lesson sizes came from BBG's chapters. Two later instructions refined it:

- *"範圍都還是通用希臘文喔，不要跑到古希臘文去了"* — the vocabulary must stay Koine.
- *"專名和前面的單字就不要重複了 / 前面單字就往前補，專名就保留在專名"* — proper names
  belong to the appendix; lesson slots backfill; no overlap.

Both are now enforced in code, and both are the kind of thing that silently breaks
again on the next rebuild, so the contract states the symptom to watch for.

## Done

| Piece | State | Built by |
|---|---|---|
| 2,000-word curriculum | ✅ NT 500 + LXX 500 + patristic 1000, disjoint | `build_greek_vocabulary_2000.py` |
| Koine lemma resolver | ✅ 761k tagged words, 15,926 Koine lemmas | `build_greek_koine_lexicon.py` |
| Morpheus form index | ✅ demoted to third resort | `build_greek_lemma_index.py` |
| 上冊 50 chapters | ✅ 1,413 verses, 26,115 words | `build_greek_scripture_plan.py` |
| 5 appendices | ✅ 625 entries | `build_greek_appendices.py` |
| Appendix names in Chinese | ✅ 341/405 (84%) | `fill_greek_appendix_names.py`, then `align_greek_names_chinese.py` |

Run them in that order. Each takes `--write`; without it they print and change
nothing. `build_greek_appendices.py` and `align_greek_names_chinese.py` need
`SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` from `.env`, and reach 信望愛 and
和合本修訂版 over the network — both cache to disk, so a second run is fast.

## Not done

Everything downstream of the redesign still describes the old fifty-lesson,
one-volume reader. Nothing below is started unless noted.

1. **下冊's readings** — 25 exist (18 patristic, 7 church documents); needs 7 more
   patristic and 18 more Greek church documents to reach 50.
2. **下冊's two sentences per lesson** — not selected. 上冊's memory verses have a
   working selector (`select_greek_memory_verses.py`); 下冊 needs the equivalent
   for prose sentences, and the owner has not been asked how they should differ.
3. **200 memory units** — the existing 100 were chosen against the old 25-chapter
   plan and the old vocabulary order. Both changed; they must be re-selected.
4. **Chinese glosses for 1,500 new words** — only Mounce's 500 have reviewed
   Traditional-Chinese. Engine policy is **Gemini → NVIDIA → Haiku**, and getting
   this wrong once already cost seventeen hours of zero progress; see the baseline.
5. **Interlinear** — the existing 50,278 glossed words cover the old chapter set.
6. **Chinese for the new chapters** — `export_reader_rcuv2010_greek.py` and
   `export_reader_fhl_deuterocanon.py` still fetch the old plan's chapters only.
7. **Two print masters** — the single 763-page B5 master is for the old design.
8. **Web reader** — `grc-lessons` pages and `greek-full-reader.ts` still assume one
   volume of fifty.
9. **Validator** — `validate_reader_release.py` still checks one volume.
10. **Mounce Erasmian audio** — still `not_recorded`; TTS substitution is forbidden.

## Traps that have already cost time

Each of these produced a *confident wrong answer*, which is worse than a failure,
so they are worth knowing before touching the code.

- **Morpheus is Attic-first.** Built on it alone, the Septuagint's top words came
  out σός, εἶπον, ὑμός, γίγνομαι, χρύσεος — Classical headwords for words Mounce
  already taught. The Koine lexicon must be consulted before it, always.
- **Accent-blind folding hides words.** `fold` maps ἕξ "six" and ἐξ "out of" to the
  same key, and εἷς to the same key as εἰς; the commoner word takes every
  occurrence and the numeral vanishes. Hence `exactForms`.
- **Folded comparison of unfolded patterns silently no-ops.** The Attic bridge
  rewrote `γιγν→γιν` against accented lemmas, where the substring "γιγν" never
  occurs. It ran for several builds doing nothing.
- **Substring matching finds names inside other words.** Aligning τυρ against verse
  text matched μαρτύρομαι and gave Tyre the Chinese 「見證」. Match at word
  boundaries.
- **Morpheus lower-cases its headwords**, so Πολύκαρπος and Εἰρηναῖος look like
  common adjectives. Only the corpus's own capitalisation identifies them.
- **Joining spellings with spaces and splitting only on punctuation** left
  `"ἄγγελος ἄγγελος ἄγγελος"` as a single dedup key, so the entire
  duplicate-detection set was empty and every Mounce word reappeared in the
  Septuagint list.
- **Swete indexes editorial markers as words.** `[1]` at Proverbs 8:21 is a
  subdivision number, not Greek. Digits-only brackets are editorial; brackets with
  Greek are restored text and stay.
- **The deuterocanon's Chinese is not uniform.** The 1933 Anglican edition has no
  Maccabees, Susanna's Greek and Chinese follow different recensions (60 vs 64
  verses), and Baruch 3 differs by one verse. Withhold and label; never align two
  texts that are not the same text.

## Owner decisions in force

- Traditional Chinese everywhere; 「‧」 as the interpunct.
- 詞庫 `name_recommended` is absolute. Never overrule it, never invent a name.
- Deuterocanonical Chinese: 香港聖公會 (信望愛 `c1933`); 思高 only as a labelled
  fallback. The 1933 book names stay (多比傳／猶滴傳／所羅門智訓／便西拉智訓).
- Textus-Receptus spelling divergences: the textbook's spelling wins.
- Pseudepigrapha are self-translated and labelled 自譯.
- The four curated appendices *may* overlap the lessons — they are a cross-index.
  Only the names are kept disjoint. The owner was told this and did not object;
  ask before changing it.
