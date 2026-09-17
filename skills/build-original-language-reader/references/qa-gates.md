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
