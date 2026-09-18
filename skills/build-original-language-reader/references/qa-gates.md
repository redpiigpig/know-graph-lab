# Release QA gates

Run every applicable gate against the final artifacts. A prior render or prior report is not evidence after an upstream change.

## 1. Source and data gates

- Exact source editions, variants, paths/URLs, checksums, and rights are recorded.
- Counts and stable IDs satisfy the frozen release contract.
- Vocabulary ordinals and lesson slots are continuous; textbook and extension layers are distinguishable.
- Homographs, aliases, multi-lexeme phrases, POS, lexical IDs, frequency exceptions, and proper-name types are internally consistent.
- All reviewed Traditional-Chinese glosses are nonblank, Traditional Chinese, and free of placeholders/English leakage.
- Required pointing/accents/breathings/orthography and textbook transliteration pass language-specific checks.
- Full chapters/works contain every declared segment.
- Memory units are unique, two per lesson, reviewed, and carry lexical-overlap evidence.
- Every Bible translation exactly matches the frozen version/variant through the shared crosswalk. Count both total display positions and unique source references.
- No fallback to another Bible translation is possible.

## 2. Master consistency gates

- Print and web import the same master or hashes linked to it.
- Every lesson has the required vocabulary, memory, and complete reading.
- Appendices are complete and separate from main-reading counts.
- Audio state is truthful.
- `scripts/validate_reader_release.py` exits successfully.

## 3. DOCX package gates

- Opens and renders without repair.
- Every section is exact B5 with mirrored margins.
- Page numbering, headings, TOC/index matter, RTL/LTR, table geometry, repeat headers, and row-split controls are present.
- Required fonts are explicitly assigned.
- No missing glyph/replacement character or stale-version source label appears.

## 3b. 版面硬約束（擁有者 2026-09-17）

兩條都由 `scripts/audit_reader_pages.py` 讀排好的 PDF 來驗，不是讀 builder 的常數：

- **一課最多八頁。** 數的是眉標——STYLEREF 讓一課的每一頁都印同一個課次。
  🚨 附錄那幾節的眉標沒有課次；碰到沒有課次的眉標就要停止累計，不然最後一課會
  把一百多頁附錄算進自己的厚度，一本書的最厚一課看起來像一百四十頁。
- **版心內的字一律 ≥12pt。** 量的是 span 的外框，落在頁眉／頁腳帶子裡的不算——
  不扣掉的話，每一頁的眉標與頁碼都會報成過小。
  🚨 希伯來文（複雜文種）要另外驗：它的字級寫在 `w:szCs`，`w:sz` 對它沒有作用。
  只檢查 builder 有沒有呼叫 `set_run_font` 是驗不到的，要量 PDF 裡的實際字級。

同一支還會回報「生詞表跨頁」的課數。那不是錯，是 12pt 下的物理極限（二十個詞加
課首要 187mm，長詞條折一次行那一列就高一倍），回報是為了讓下一個人知道現況、也
知道它有沒有在惡化。

## 3c. 四本各自的發行驗證器

一支一本，缺一本就等於那一本沒有人在看資料層：

| 語言 | 驗證器 |
|---|---|
| 聖經希伯來文 | `scripts/qa_hebrew_full_reader.py`（64 項，含 DOCX／PDF） |
| 通用希臘文 | `scripts/verify_greek_reader.py` |
| 教會拉丁文 | `scripts/verify_latin_reader.py` |
| 日文宗教學 | `scripts/verify_japanese_reader.py` |

希臘與日文那兩支是 2026-09-18 才補上的。在那之前那兩本只有 builder 內建的自檢，
而 **builder 只在「組不出來」的時候才出聲**：組得出來的錯——一課少一個詞、兩課共用
同一則背誦句、裁過卻沒寫範圍、某一段沒有逐詞對譯——它一句話都不會說。

寫這兩支的時候各踩了一個坑，都值得記著：

- 🚨 **欄位名要照資料實際的樣子查。** 希臘附錄的中文在 `zh` 不是 `glossZh`，照
  `glossZh` 查會把 625 筆全部報成未定。一支會亂叫的驗證器比沒有還糟。
- 🚨 **鍵要照資料實際的鍵。** 日文詞表的 `lesson` 是《大家的日本語》的課本章次，
  讀本自己的課次在 `readerLesson`；拿 `lesson` 分組，第二冊每一課都被報成
  「30 詞、127 詞」。逐詞對譯的鍵也猜不得（上冊 `scripture:<osis ref>`、下冊
  `patristic:<課次>:<段 ref>`），猜錯就是 487 段假的缺。

## 3d. 逐頁光柵檢查（`scripts/qa_reader_rendered_pages.py`）

前面幾關查的都是「文字層說了什麼」，共用一個盲點：**抽得出文字不等於印得出來**。
裁掉半個字、整頁重覆、某一頁悄悄變成空白、油墨壓到裁切線——文字層一個字都不會少。
這一支把七冊每一頁 rasterise 之後逐頁量：頁數與頁序、尺寸一致、空白頁、整頁重覆、
最外圈 0.4% 有沒有墨水。2026-09-18 首次全書跑完：2,596 頁全過。

## 3e. 逐頁版面檢查（`scripts/inspect_reader_pages.py`）

3d 問的是「這一頁印得出來嗎」，這一支問的是**「這一頁排得好不好」**——翻書的人一眼
就看出來、而前面每一道都沉默的那些：文字疊在一起、版心中間破一個大洞、一頁上只有
一兩行（孤兒頁）、一段的末行單獨落在次頁、同段兩行黏在一起。

門檻都是先量再定，常數旁邊寫著它是怎麼來的。寫這一支時誤判過三輪，都記在常數的註解裡：

- 🚨 **判疊字要比基線，不要比行框。** PyMuPDF 的 line bbox 是字型框（含升降部），而
  題號行與作答線用的是絕對行高，行框天生互相疊進去——第一版全書報出四百多處，逐頁
  看過去沒有一處是真的。
- 🚨 **基線完全相同的兩「行」是同一行。** 重音字母常被拆成獨立 span。
- 🚨 **行距過擠要同時同字級、同左緣、同字體。** 少了「同字體」，希伯來題號行（中文
  字體的「09」）與其下的原文行會被當成同一段而報成過擠。
- 封面是設計過的滿版，留白規則與尋常頁面不同，跳過。
- 🚨 **版心裡一個字都沒有的頁要單獨報一類（「只有眉標的頁」）。** 第一版把它
  `continue` 掉、寫著「空白頁由 qa_reader_rendered_pages 負責」——那一支也不會報，
  因為那一頁有文字（眉標）也有墨水（頁眉）。十一頁白紙就這樣通過了所有關卡。

2026-09-18：首跑 2,625 頁報出 32 頁孤兒頁，三類全是真的，修法見
`layout-web-audio.md`〈孤兒頁〉。修完七冊歸零。

## 4. PDF gates

- Final page count meets the expected range.
- Every MediaBox is 182 × 257 mm within tolerance.
- Required language and CJK fonts are embedded.
- Forbidden fallback fonts are absent.
- Searchable source-language and Chinese text are present.
- No clipping, footer collision, missing glyph, or stale translation/source label appears.
- No page prints in a language other than the reader's own. A gloss column that
  fell back to English renders perfectly and passes every other gate.
- `scripts/render_and_check_reader_pdfs.py` does the geometry, embedded-font,
  U+FFFD and blank-page half of this list in one command, for the readers and
  the flashcard decks alike. It gives each file its own LibreOffice
  `UserInstallation` profile — LibreOffice allows one at a time, and a second
  conversion otherwise waits or silently takes the first one's settings.
  `□ U+25A1` is a real glyph in the Hebrew reader's 「完成本課」 checklist, not a
  missing one.
- **Open the pages that carry the change you just made and read them.** The
  appendix that was still one undivided list, and the cover that was new above an
  appendix that was old, both passed every automated gate above.

## 5. Raster gates

- Render every page at one fixed resolution.
- Page numbers are continuous and dimensions uniform.
- Reject blank/near-blank accidental pages, edge intrusions, exact duplicate pages, and abnormal content density.
- Generate contact sheets for navigation only.
- Inspect every page at full resolution. Contact sheets do not replace page inspection.
- Record exact abnormal pages and re-run the entire final visual pass after correction.

## 6. Web gates

- Authentication is enforced on pages/APIs.
- `X-Robots-Tag`, `Cache-Control`, and `Vary` are correct.
- Overview, lesson, and appendix routes load the final master.
- Invalid lesson numbers return the intended error.
- Every source/translation segment renders; partial tokenization cannot hide full source text.
- Textual notes, readings, syntax notes, pronunciation profiles, and audio status are visible where required.
- Targeted tests, type checking, and production build pass. Report dependency/toolchain failures separately; never call an unrun test a pass.

## 7. Audio gates

- Every required real track exists and hashes match.
- Track pronunciation profile matches the curriculum.
- Cues are ordered, in bounds, non-overlapping, and cover the configured segments.
- Review status and recording rights are complete.
- Missing audio shows no play control.

## 8. Release manifest

- Run `scripts/hash_release_artifacts.py` on source snapshots, master, DOCX, PDF, web master, QA reports, and audio manifest.
- Store file bytes, SHA-256, and generation time.
- Confirm the QA report references the same master/DOCX/PDF hashes.
- Keep status partial until all required gates pass.

## Audits that find what the gates miss

The deterministic gates below all passed while the Latin build was pairing
Exodus 3 with John 17 and printing one hymn's Chinese beside another. Four
cheap habits found those, and none of them is a test:

- **Count the same set twice by different routes and compare.** The plan said 45
  readings needed translation; the translation queue produced 39 keys. That gap
  was eight readings sharing two source files.
- **Render a page and read it.** The empty first table row, a running header
  still naming the wrong language, an untranslated English masthead, a picture
  that contradicts its word — none of these appear in any count.
- **Probe the live endpoint.** All three reader APIs answering 401 proved the new
  data module imports and the auth guard holds. A 500 looks the same from the
  outside as a route that was never wired.
- **Diff two independent readings of one source.** Vision OCR and the PDF text
  layer disagreed on 76 words of the Mass ordinary; the disagreements are where
  the errors are, in one layer or the other.

See `silent-failures.md` for the incidents these come from.
