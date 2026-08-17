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

## 4. PDF gates

- Final page count meets the expected range.
- Every MediaBox is 182 × 257 mm within tolerance.
- Required language and CJK fonts are embedded.
- Forbidden fallback fonts are absent.
- Searchable source-language and Chinese text are present.
- No clipping, footer collision, missing glyph, or stale translation/source label appears.

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
