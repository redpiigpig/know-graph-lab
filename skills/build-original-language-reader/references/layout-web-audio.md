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

## 一課八頁、字級不小於 12pt（擁有者 2026-09-17 定）

這兩條是版面的硬約束，其他所有版面決定都排在它們後面。

- **一課最多八頁。** 一課印的就是三樣東西：二十個生詞、十題翻譯練習、一篇讀文。
  讀文的長度因此不是編輯決定的，是版面決定的——見下面的「版面預算」。
- **凡是要讀的字一律 ≥12pt。** 只有眉標與頁碼例外（版口標示，不是閱讀內容）。
  實作在 `build_hebrew_full_reader.set_run_font` 的 `MIN_READING_PT`：字級下限
  收在唯一的出口，而不是靠把一百多處常數逐一改成 12——那樣會漏掉算出來的
  （`CAPTION_PT - 0.4` 印出來是 11.6），而且攔不住下一個人新增的 9.5pt。
  眉標與頁碼走 `chrome=True` 繞過下限。
  🚨 **希伯來文要另外設 `w:szCs`。** 複雜文種（希伯來、阿拉伯…）排版讀的是
  `w:szCs` 不是 `w:sz`，而 python-docx 的 `run.font.size` 只寫後者。整本希伯來
  讀本的希伯來字因此一直印在 `szCs` 的預設值 11pt 上——詞表、逐詞對譯、練習題、
  Haggadah，五千多個字級沒有一個是 builder 要求的那個數字，而頁面看起來完全
  正常。量 PDF 才會發現（NotoSerifHebrew 只有 11.0pt 一種尺寸）。

## 版面預算：讀文能收多長是量出來的

`scripts/reader_page_budget.py` 收著一個量出來的模型：

    頁數 ≈ 固定開銷 + a × 讀文長度 + b × 單元數

四種語言各一組係數，由 `scripts/fit_reader_reading_limit.py` 從**排好的 PDF**
回歸出來（每課的眉標就是那一課的頁，數眉標就是數厚度）。裁讀文的時候不是比對
一個詞數上限，而是問「再加一個單元會不會超過預算」。

- 🚨 **單元數那一項不能省。** 逐詞對譯每個單元自成一塊，末尾那一列多半沒排滿，
  還要加一行整句中譯。同樣五百詞，分五段與分五十段厚度差很多：只用詞數回歸，
  希臘 R² 0.793、日文 0.478；補上單元數之後是 0.925 與 0.643。被這一項咬到的是
  〈聖母讚頌詞〉那種課——詞數不多、段數上百，照詞數估七頁，印出來十二頁。
- 🚨 **不要用「讀文長度 ÷ 一課總頁數」當每頁容量**：分母含生詞頁與練習頁，密度
  低估四成，上限就砍過頭。
- 🚨 **也不要用「一頁排得下幾個原文詞」回推**：段末沒排滿的那一列、整句中譯的
  行、單元之間的間距都不在那個數字裡。日文一頁排得下九十四個詞，看起來一頁可放
  兩百字元，實際只有一百。
- 🚨 **回歸線是平均，要留緩衝。** 照線設上限會有一半的課壓在線上方：第一輪就是
  這樣，四本共 31 課印成九到十頁。`SAFETY_PAGES` 就是那個緩衝，也是量出來的。
- 🚨 **版面一改，係數就作廢。** 字級、行距、cell 邊距、練習題的節奏動過之後要
  重跑 `fit_reader_reading_limit.py`，不要沿用上一輪的數字。

裁的單位一律是**文本自己的分段**（節、段、章），不是詞數切點——擁有者
2026-09-17：「要是自然段落的選集喔，不要是語意沒講完就中斷。」粗分段救不了的
時候（整篇只有一段）才退到更細的一層，退到哪一層要在 extent 裡說出來。

## 一課的三塊：生詞一頁、練習一頁、讀文自己起頁

擁有者 2026-09-17：「生詞表二十字只需要一頁啊，練習十個句子加作答空間也只需要
一頁啊。」這一段的數字都在 `build_hebrew_full_reader` 的版面節奏常數裡，四本共用。

踩過的坑，每一個都是「看起來正常、實際浪費一整頁」：

- **Word 的預設段落節奏。** 12pt 的字（字高 4.2mm）排進表格 cell 會佔掉 11.2mm，
  因為預設帶著 space_after 與 1.15 行距。`tighten_cell()` 清掉之後一列約 7mm。
- **欄寬不足會折行，折一次就多一列。** 編號欄 8mm 放不下兩位數，印出來是「1」
  換行「4」。長詞條同理——拉丁的主要部分（median 22 字母、p90 39）與繁中詞義
  （median 7 字、p90 12）在 141mm 版心裡只能取捨，兩邊都給到 p90 就爆版。
  🚨 兩個方向都要試過再定：把 forms 放寬到 56%、詞義縮到 32%，跨頁的課從 13 變
  19、整冊多六頁——詞義折行的代價一樣是多一整列，而它的分佈比 forms 集中得多。
- **練習題的三行要各自講明行距。** Normal 樣式的 1.25 是給整段中文正文的節奏，
  套在三行各自成段的題目上，十題光行距就多出兩公分。題號行與作答線給**絕對**
  行高（exact），正文那一行只能給倍數——它會折行，寫死會把第二行裁掉。
- **課首那一疊的留白。** 眉標小標、課次、課題、生詞標題各自帶著 Heading 1 給整本
  分章用的段前段後，加起來四公分；生詞表就差那幾公釐排不進一頁，於是二十個詞
  跨兩頁、十題被推到第三頁，一課憑空多兩頁。

量「生詞排不排得進一頁」有兩個想當然耳、都量錯了的判準：

1. 「練習標題的 y 要小於 27mm」——標題自己的行高與段前留白就把 y 推到 28.5mm，
   排得好好的十八課被報成壞的。
2. 「練習標題上面不能有別的東西」——生詞排得下的時候，練習標題本來就緊接在表格
   後面、跟課首同一頁。那是最緊湊的情形，不是錯。

要問的是：**詞條有沒有被擠到下一頁去**——生詞標題在前一頁，而練習標題那一頁的
上方還壓著詞條。`scripts/audit_reader_pages.py` 用的就是這一條。

## One shared layout across the three readers

The Hebrew builder is the standard; Greek and Latin import its size constants
and must match its *structure* too, not just its scale. Checked 2026-08-27:

- **Section headings are real headings.** `document.add_heading(..., level=2)`
  at 14 pt, never the 8.2 pt all-caps eyebrow. Greek printed 「生詞／背誦／讀文」
  through `add_label` for months — section headings smaller than the 11.5 pt
  body text. The eyebrow is for the line *above* a heading, never instead of one.
- **Heading scale**, from `build_hebrew_full_reader`: title 24, H1 17, H2 14,
  H3 12.5, body 12, tables 12, label 12. Nothing that acts as a heading may sit
  below the body size, and since 2026-09-17 nothing readable may sit below 12pt
  at all — the old 11.5／9.6／8.2 rungs are gone.
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
  builder's `PARTS`. 2026-09-18（12pt、一課八頁之後）實測：希臘四冊
  183／189／241／236，拉丁三冊 355／160／166，日文四冊 181／177／180／187，
  希伯來單冊 406。
  🚨 切點要把**整冊的厚度**算平，不是把課文頁數算平：附錄只印在該半的最後一分冊
  （希臘下冊那份就有 150 頁）。照課文頁數對半切，會切出 201／277 的一薄一厚。 `render_and_check_reader_pdfs.py` fails the build
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
