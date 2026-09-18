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

**擁有者 2026-09-18 裁示：「生詞到第二頁沒關係。」** 所以這件事到此為止——版面
浪費該修（那是真的多印了紙），但「二十個詞一定要在同一頁」不是硬要求。
`audit_reader_pages.py` 照實回報數字，不當成錯。

2026-09-18 收工時的實測（全四本共 350 課）：

| | 生詞表跨頁 | 十題練習佔兩頁 |
|---|---:|---:|
| 收緊之前 | 87 課 | 77 課 |
| 收緊之後 | **56 課** | **52 課** |

兩個數字會一起動，因為是同一件事：生詞表多佔半頁，練習就被推下去。剩下的 56 課
幾乎都是拉丁（33 課）——它的主要部分字數中位數 22、第九十百分位 39，12pt 下沒有
辦法與繁中詞義共存於 141mm 的版心而不折行。希臘是零，它的詞條短。這是字級下限帶
來的物理極限，不是版面浪費；別再為它降字級或改表格結構。

## 孤兒頁：LibreOffice 的 keep 只認同一張表格的列與列

一頁上只有一行字、其餘全白，三道舊關卡沒有一道會出聲（尺寸對、字型對、不是空白頁、
課次頁數也沒超）。`scripts/inspect_reader_pages.py` 2026-09-18 首跑量出 32 頁，三類：
練習第 10 題單獨一頁（22 頁）、整句中譯單獨一頁（8 頁）、課末那一組單獨一頁（2 頁）。

修法之前先弄清楚一件事，不然會一直改一直沒效：

🚨 **LibreOffice 轉 PDF 時，儲存格裡的 `keepNext` 綁不住表格後面的段落。** 逐詞對譯
是一列一張表格，整句中譯原本是表格後面的段落——那一行因此可以自己跑到下一頁，而
「最後一列補 keepNext」這個看起來最自然的修法**一點作用都沒有**（`w:pPr` 裡的順序
對錯都一樣不理它）。實測腳本留在 scratchpad：兩份只差 keepNext 的 DOCX，轉出來的
PDF 完全一樣。

能用的是這兩條，都實測過：

1. **整句中譯要變成同一張表格的最後一列**（跨欄合併）。列與列之間的 keepNext
   LibreOffice 認。合併後記得把 `merge()` 串起來的空段落刪掉，否則整句下面會多印
   幾行空白。
2. **keepNext 要補在那一列每一格的每一段上**，不只補有詞的那幾格。只有部分格子帶
   keepNext 時它有時認有時不認——填充欄與課次欄補上之後才真正歸零。

另外兩類與表格無關，是段落層的 keep 漏了：

- **練習另起一頁。** 生詞表跨頁之後練習從第二頁中段才開始，十題排不完，最後一題
  被甩到第三頁。十題加說明約 205mm、版心 219mm，另起一頁一定排得下。
- **課末那一組（完成本課六條＋讀後筆記）要鎖成一塊。** 🚨 最後一條的 keepNext 只
  能在真的有讀後筆記時才加；沒有的話它會去綁下一課的標籤——那一段是另起一頁的，
  於是整組被拖到下一課的首頁。
- **標籤與標題不要各自另起一頁。** 版本記事的標籤與標題都寫了 `page_break_before`，
  印出來就是一頁只有「COLOPHON」一個詞。
- 🚨 **換頁前的空段落會印出一頁只有眉標的紙。** 表格後面那個「留點空氣」的空段落
  平常看不見，直到表格剛好排到頁腳附近：空段落自己流到下一頁，後面那一節的
  `page_break_before` 又另起一頁，中間那一頁就這樣送到印刷廠。拉丁兩冊十頁、希伯來
  一頁都是這樣來的，而**前面每一道關卡都放它過去**——那一頁不是「空白頁」（眉標是
  文字），墨水也只是頁眉。`drop_spacer_before_break()` 在存檔前掃掉；那點空氣本來就
  看不見（強制換頁前的段後距不會算），所以拿掉不改變別的。
- 🚨 **很長的整句中譯不要綁在詞列旁邊**（`LONG_SENSE_CHARS = 600`，約 18 行、100mm）。
  教父那幾篇的整句是整段翻譯，希臘下冊第 20 課那一條高 201mm。綁住的下場是：詞列被
  拖到次頁，而整句在那一頁還是擠不下、又跳一頁——那一頁上只有一個希臘詞與它的中譯。
  不綁，詞列就留在原頁排滿，整句自己佔一頁。
  🚨 **別改成「讓整句可以拆」**：試過，教父那幾篇於是每一篇都在頁首留一兩行尾巴、
  整頁其餘全白，希臘下冊一次冒出七頁。整句那一列要維持 cantSplit。

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
  builder's `PARTS`。**2026-09-18 擁有者裁示「頁數少就並冊」**：一課壓到八頁、
  讀文按版面預算節錄之後，各半都進得去一本，於是十二冊收成七冊——分冊本來就只是
  為了那條 500 頁的上限而存在的，上限不再逼人就該回到「內容的一半＝一本實體書」。

  | 書 | 冊 | 實測頁數 |
  |---|---|---:|
  | 聖經希伯來文 | 單冊 | 406 |
  | 通用希臘文 | 上冊（新約與七十士）／下冊（教父與希臘教會文獻） | 369／474 |
  | 教會拉丁文 | 上冊（武加大）／下冊（教父與教廷文獻） | 349／321 |
  | 日文宗教學 | 第一冊（現代語）／第二冊（文語） | 347／355 |

  🚨 真的需要再切的時候，切點要把**整冊的厚度**算平，不是把課文頁數算平：附錄只
  印在該半的最後一分冊（希臘下冊那份就有 150 頁）。照課文頁數對半切，2026-09-18
  那一輪切出來的是 201／277 的一薄一厚。
  🚨 冊數一改，**四個寫死的清單**都要跟著改，而漏掉任一個的症狀都不像「冊數改了」：
  `render_and_check_reader_pdfs.TARGETS`（說找不到 docx）、`audit_reader_pages.BOOKS`
  （說找不到 PDF）、`audit_printed_exercises.BOOKS`（說課次順序印錯——錯的是稽核）、
  `sync_reader_artifacts.SUPERSEDED_NAMES`（Drive 上留著一本已經不存在的冊次，而它
  自己看起來完全正常）。 `render_and_check_reader_pdfs.py` fails the build
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

## 正式課本：紙上不出現編務語言

擁有者 2026-09-18：「那是正式課本，文本中不要有註記，也不要寫說是機器做或自學用的。」

盤過一輪，四本書上原本印著約三千處不屬於課本的字，分五類：

| 類 | 例 | 處置 |
|---|---|---|
| 自學／私人身分 | 頁尾每頁「私人研讀版 · N」、`PRIVATE STUDY EDITION`、封面「JIS B5 182×257 mm · 私人研讀」 | 全部拿掉；頁尾只印頁碼 |
| 編務統計 | 「本課 20 詞全數入題」「本讀本語料中無任何字形，因而無法入題：concelebrō」「（全章 45 節、701 詞）」 | 拿掉；範圍留，詞數不留 |
| 製作過程 | 「再其次才是模型」「由 OpenCC 的 t2jp 推導」「依合約寧缺勿濫」「付印前請對照《感恩祭典》核對」 | 改寫成描述這本書的話，或移到驗證器 |
| 誰寫的 | 每一題旁的「自撰」（2,918 處） | 引用題印出處，自撰題只印題號 |
| 空缺記號 | 〔中譯待補〕〔待補〕（中文待定） | 紙上留白 |

🚨 **拿掉印刷記號，就要同時補上資料層的清點。** 空缺的可見性是這一系列的底線；
把〔待補〕從紙上拿掉而沒有別的東西數它，缺口就真的消失了。所以四本各有一支驗證器
在數：`qa_hebrew_full_reader`、`verify_greek_reader`、`verify_latin_reader`、
`verify_japanese_reader`（後兩支的希臘與日文版是 2026-09-18 才補齊的——在那之前
那兩本只有 builder 內建的自檢，而 builder 只在「組不出來」的時候才出聲）。

🚨 **狀態字串要取代，不要附加。** 來源的說明常常已經寫著「（完整，共 21 節）」，
裁過之後在後面接一句「取前 4 段」，同一行就同時宣告完整與節錄。日文與拉丁都犯過。
