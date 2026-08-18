# Greek reader — frozen release contract

Frozen 2026-08-18 for `know-graph-lab`. Verify every path live before use.

## Curriculum

| Item | Frozen value |
|---|---|
| Textbook | William D. Mounce, *Basics of Biblical Greek Grammar* (BBG), official 1,000-word list |
| Lessons | 50 |
| Vocabulary | 1,000 unique entries |
| Lessons 1–30 | BBG chapters 4–36 exactly as the textbook has them — 340 words, 2 to 26 per lesson, uneven by design (chapters 1–3, 5, 15, 26 carry no vocabulary) |
| Lessons 31–50 | Mounce frequency extension, 660 words, 33 per lesson, published order preserved |
| Assigner | `scripts/assign_greek_lessons.py --write` |
| Transliteration | Mounce standard Erasmian; Byzantine/reconstructed-Koine are separately named tracks, never merged |

Never restate this as "20 words per lesson". Lesson size comes from BBG.

## Source freeze

| Layer | Frozen source | Rights |
|---|---|---|
| New Testament Greek | SBLGNT, ed. Michael W. Holmes, via the MorphGNT analysis (`morphgnt/sblgnt`) | SBLGNT EULA, private authorized; MorphGNT annotation CC BY-SA 3.0 |
| LXX, deuterocanon, pseudepigrapha Greek | Henry Barclay Swete, *The Old Testament in Greek according to the Septuagint*, Cambridge 1909–1930, digital word database `eliranwong/LXX-Swete-1930` | Swete's text is public domain; the digital database is GPL-3.0 and is kept as a local build input, not redistributed |
| Traditional-Chinese Bible (NT + LXX-canonical) | 《和合本修訂版》（2010）, variant RCUV2（上帝版）, official HKBS payloads | private authorized, same as the Hebrew reader |
| Traditional-Chinese deuterocanon | 1933 年聖公會出版次經（信望愛站「次經閱讀」version `c1933`） | 1933 譯本已逾著作權期間；數位化循 CBOL 版權宣告作非商業使用 |
| Traditional-Chinese pseudepigrapha | self-translated, labelled `自譯` in every unit | editorial |
| Creeds and council canons | `data/creeds/**` Greek versions (Schaff/DCO), plus `creeds-greek.json` for the three texts the repository lacked | as recorded per document; the Schaff additions are public domain |
| Apostolic and Greek Fathers | public-domain Greek editions, frozen per work | per work |
| Divine Liturgy of St John Chrysostom | Greek liturgical text, ordinary-time (non-festal) Sunday order, frozen edition recorded per section | per edition |

Rahlfs–Hanhart 1935 is *not* the frozen LXX base. The accessible digital Rahlfs is CCAT-derived and requires a signed CCAT user declaration, and Rahlfs carries no Greek 1 Enoch. Swete covers LXX, all deuterocanonical books, Psalms of Solomon and the Greek 1 Enoch in one public-domain edition. Rahlfs may be cited as a collation reference only.

## 25 complete Scripture chapters

Approved split: **New Testament 13 / LXX canonical 6 / deuterocanonical 4 / pseudepigraphal 2**.

| # | Corpus | Reading | Base |
|---:|---|---|---|
| 1 | NT | 約翰一書 1 | SBLGNT |
| 2 | NT | 馬可福音 1 | SBLGNT |
| 3 | NT | 馬可福音 4 | SBLGNT |
| 4 | NT | 約翰福音 1 | SBLGNT |
| 5 | NT | 馬太福音 5 | SBLGNT |
| 6 | NT | 馬太福音 6 | SBLGNT |
| 7 | NT | 哥林多前書 13 | SBLGNT |
| 8 | NT | 使徒行傳 2 | SBLGNT |
| 9 | NT | 雅各書 1 | SBLGNT |
| 10 | NT | 腓立比書 2 | SBLGNT |
| 11 | NT | 羅馬書 8 | SBLGNT |
| 12 | NT | 希伯來書 1 | SBLGNT |
| 13 | NT | 啟示錄 21 | SBLGNT |
| 14 | LXX | 創世記 1 | Swete `Gen` |
| 15 | LXX | 創世記 22 | Swete `Gen` |
| 16 | LXX | 出埃及記 3 | Swete `Exo` |
| 17 | LXX | 詩篇 22（MT 23） | Swete `Psa` |
| 18 | LXX | 詩篇 50（MT 51） | Swete `Psa` |
| 19 | LXX | 以賽亞書 6 | Swete `Isa` |
| 20 | 次經 | 多俾亞傳 1（Sinaiticus GII） | Swete `Tbs` |
| 21 | 次經 | 友弟德傳 13 | Swete `Jdt` |
| 22 | 次經 | 智慧篇 7 | Swete `Wis` |
| 23 | 次經 | 德訓篇 24 | Swete `Sir` |
| 24 | 偽經 | 以諾一書 1（希臘文，猶大書 14–15 所引） | Swete `1En` |
| 25 | 偽經 | 所羅門詩篇 17 | Swete `Pss` |

LXX/MT numbering differences (Psalms above all) route through one shared crosswalk, exactly as the Hebrew reader does.

## 25 patristic / creed / decree readings

Declared as complete short works or explicitly labelled authorized excerpts; never mixed silently. See `greek-patristic-plan.md` for the frozen list.

## Appendix

Complete ordinary-time (non-festal Sunday) Divine Liturgy of St John Chrysostom, Greek with Traditional-Chinese parallel, kept separate from the 25 patristic readings — the structural counterpart of the Hebrew fifteen-step Haggadah.

## Stop conditions specific to this release

- The 1933 Anglican deuterocanon uses its own book names (多比傳／猶滴傳／所羅門智訓／便西拉智訓). Keep them; do not silently relabel them with the 思高 names the Catholic canon uses.
- `creeds-greek.json` marks three segments `needs_review_*`. Schaff prints variant readings and a Greek term index inside the same cells as the creed; those segments must be reviewed before they reach a reading, and never shipped as creed text unexamined.
- Greek 1 Enoch and Psalms of Solomon carry editorial brackets in Swete. Keep the bracketed source form immutable and flag any display-layer removal.
- No modern-Greek TTS may stand in for the Mounce Erasmian audio track.
