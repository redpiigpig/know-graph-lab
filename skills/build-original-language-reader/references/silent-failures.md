# Failures that look like success on the page

Every bug in this list shipped a page that looked finished. None threw, none
logged, none left a blank. They were found by counting the same thing two ways
and noticing the numbers disagreed, or by rendering a page and reading it.

They came out of the Ecclesiastical Latin build (2026-08-25/26), but not one of
them is about Latin. Read this before wiring any new language, and before
believing a count you have only computed once.

## 1. A key must be an identity, not a position

**Lesson numbers move.** The reading plan sorts by difficulty, so a lesson number
is an output of that sort. The Chinese export was keyed on it; the vocabulary
changed, the sort changed, and lesson 28 stopped meaning Exodus 3. Proper-name
alignment fell from 56 matches to 1 — silently, because a name with no Chinese
looks exactly like a name whose register does not cover it.

*Key on book and chapter. Anything a builder computes is not an identifier.*

**Source paths are not unique.** Six hymns are cut out of one anthology and two
creeds out of another. The translation cache was keyed on the source file, so
eight readings collided into two keys: the hymns took turns overwriting one
another and the page printed whichever landed last, next to a different hymn.

*What distinguishes them — the section anchor — belongs in the key.*

**How both were caught:** the plan said 45 readings needed translation and the
translation queue produced 39 keys. Two counts of the same set, compared.

## 2. A file existing is not the thing existing

Twenty-seven readings had a `-chinese.txt` beside the Latin, and the build
reported twenty-seven parallel translations. Opening them: three contained the
placeholder 「⏳ 中譯待補」, fifteen were selections from the Denzinger anthology
(the Sacrosanctum Concilium file holds **one** entry out of a hundred-and-thirty-
paragraph constitution and says so in its own header), four were real
translations that number nothing, and five were real translations with section
numbers. Only those five could be set beside the Latin.

*Classify the file. Never let `path.exists()` stand for "the content is what the
name implies".*

## 3. Alignment by position, where the two sides do not correspond

Having wrongly counted twenty-seven translations, the layout paired them with
the Latin by paragraph index. Sacrosanctum Concilium has 362 Latin paragraphs
against 11 Chinese ones. Paragraph five of each is five different places in the
document, and the page looked perfectly ordinary.

*Join on something both sides carry — a verse number, a section number — or do
not join at all.*

## 4. Gates that throw away good data

**A round trip is not a script test.** The Traditional-Chinese gate called any
text simplified if OpenCC's `s2t` changed it. `s2t` rewrites 祢 to 禰 — and 祢 is
the Catholic honorific for God, in nearly every prayer the reader translates; one
reading is titled 《願祢受讚頌》. Every correct translation was being thrown away
and retried for ever. 台, 床, 群, 峰 the same.

*Allow the known variants individually, keep rejecting a line that also carries a
real simplified form, and never let a converter's opinion stand as evidence.*

**Capitalisation is not a proper-name test.** Collins capitalises `Deus`, the
nationality adjectives and the liturgical nouns. A capitalisation rule sent the
second commonest word in the Vulgate to the name appendix, where it stopped being
taught at all. Twenty-nine capitalised entries is a small enough set to
enumerate; a rule that misfires on a third of them is not worth having.

**A destroyed regex matches nothing, quietly.** Patching a file through a layer
that eats backslashes turned `\b` into a backspace character and `\d` into a
literal `d`. The year parser returned 9999 for every date and the chronological
sort came out in file order; the section matcher found no sections and paired no
Chinese. Each looked like a data problem.

*After patching a pattern, print it back and match it against a known string.*

## 5. Boundaries have to come from the work, not from a budget

**A word count is not an excerpt.** "The first nine hundred words" stops wherever
nine hundred words happen to land, mid-argument. Cut at the work's own divisions
— whole chapters, whole numbered sections, whole canons — and let the budget
decide how many fit, never how much of one.

**Divisions are not always punctuated.** The Proslogion writes `1 Excitatio
mentis ad contemplandum Deum`: number, space, capitalised title. A rule expecting
`1.` found no divisions, treated the whole work as one, and put 6,311 words into
a lesson budgeted for 1,400.

**A section number is not always tight against its point.** Dignitatis Humanae
prints `2 . Haec Vaticana Synodus declarat`.

**The edition's own furniture is inside the OCR.** Collins numbers his readings
in English — "1. The Ordinary of the Mass", "2. The Exsultet (Ambrose, d. 397)" —
and those lines went to the translator as if they were liturgical Latin. Worse,
the second title is where the first reading *ends*: the Ordo Missae was carrying
twenty-five lines of the Exsultet on its tail.

## 6. Some texts must not be machine-translated at all

Asked for 「R. Et cum spiritu tuo.」 the model returned 「執事：願天主與你們同在。
R. 及與你的聖神同在。」 — a versicle that is not in the Latin. It also rendered the
sign of the cross as 「天主，聖父、聖子、聖神的名義內」 where every Chinese-speaking
Catholic says 「因父、及子、及聖神之名」.

A liturgical formula has a received wording that the reader already knows by
heart. A self-translation of it is not a rough draft to be improved later; it is
an error the label 自譯 does not cover, and an invented response inside a Mass
text is the worst thing this series could print.

*Leave the gap, print why, and make the release gate say so on every run so
nobody fills it with a draft.* The same principle already governs the flashcard
pictures: blank beats wrong.

## 7. Report what was produced, not what was planned

The gate read the plan's classification and printed 「45 篇需自譯」 long after all
forty-five had been translated. A status line that describes intent rather than
output will be believed and will be wrong.

## The audits that actually found these

- **Count the same set twice, by different routes, and compare.** Plan versus
  queue found the key collision; classification versus file contents found the
  phantom translations.
- **Render a page and look at it.** The empty first table row, the running header
  still saying 聖經希伯來文, the END arrow on 「因此、所以」, the untranslated English
  masthead — none of these appear in any count.
- **Probe the endpoint.** 401 from all three reader APIs proved the Latin module
  imports and the auth guard holds; a 500 would have meant the opposite and no
  test covered it.
- **Diff two independent readings of the same source.** The vision OCR and the
  PDF text layer disagreed on 76 words of the Mass; the disagreements are where
  the errors are, in whichever layer.
