/**
 * Paragraph parser for council documents (Vatican II etc.).
 *
 * Each council document is paragraph-numbered (1, 2, 3 ...). This parser splits
 * the raw text into `{ num, body }[]` so the detail page can render Bible-style
 * row-by-row parallel comparison (中 / 英 / 拉) aligned by paragraph number.
 *
 * Source format quirks (observed 2026-05-21):
 *   - Latin (vatican.va HTML): `1 . Nostra aetate...` or `1. ...`
 *   - English (vatican.va HTML): `1. In our time...`
 *   - Chinese (vatican.va PDF via pdftotext -layout): `1 在我們的時代...`
 *     - PDF retains line wrapping inside paragraphs (collapsed during parse)
 *     - Footnote refs appear as "一( ) 二( ) 三( )" (broken superscripts) — kept inline
 *     - Document preamble (title, TOC, section headings) is dropped
 */

export interface Paragraph {
  num: string
  body: string
}

/**
 * Split text into `{ num, body }` paragraphs.
 *
 * Algorithm: split on 2+ newlines, then check each block's first chars for
 * a paragraph number (1-200). Sub-blocks without numbers (subheadings,
 * spillover paragraphs) get appended to the previous numbered paragraph.
 */
export function parseParagraphs(text: string): Paragraph[] {
  if (!text || typeof text !== 'string') return []

  // Normalize Windows / Mac line endings -> LF before splitting on blank lines.
  const normalized = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n')
  const blocks = normalized.split(/\n{2,}/)
  const result: Paragraph[] = []
  let current: Paragraph | null = null
  let pendingSubhead: string | null = null

  for (const raw of blocks) {
    const block = raw.trim()
    if (!block) continue

    // Skip pure language-switcher nav line ([ AR - BE - CS ... ])
    if (/^\[\s*[A-Z]{2}(\s*-\s*[A-Z]{2})+\s*\]$/.test(block)) continue

    // Skip the standalone "<filename> - Full ... Text" markdown title (just in case)
    if (/^[A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+\s+-\s+Full/.test(block)) continue

    // Match leading paragraph number (allow trailing dot, optional spaces).
    // Examples: "1.", "1 .", "1", "12.", "130."
    const m = block.match(/^(\d{1,3})\s*\.?\s+([\s\S]*)$/)
    if (m) {
      const n = parseInt(m[1], 10)
      const bodyAfter = m[2].trim()
      if (n >= 1 && n <= 200 && bodyAfter.length >= 8) {
        // New numbered paragraph — flush previous + any pending subhead
        if (current) result.push(current)
        current = {
          num: m[1],
          body: collapseInternalWrap(bodyAfter),
        }
        pendingSubhead = null
        continue
      }
    }

    // Not a numbered start. If we have a current paragraph, append.
    if (current) {
      current.body += '\n\n' + collapseInternalWrap(block)
    } else {
      // Pre-paragraph block — may be a section heading like "緒言" / "INTRODUCTION".
      // We don't have a "current" yet, so just record it; we don't surface it.
      pendingSubhead = block
    }
  }

  if (current) result.push(current)

  // Footnote sections re-start numbering from 1 — trim everything past the first non-monotonic step.
  return trimNonMonotonic(result)
}

/**
 * vatican.va documents have two patterns that confuse a naive split:
 *
 *  (a) Section subheadings inside a chapter — `1. The Nature of the Sacred Liturgy...`
 *      These are Roman numerals (I, II, III) rendered as `1.`, `2.`, `3.` and they
 *      reset numbering each chapter. Body is short (a title sentence). We *skip* them
 *      so the main paragraph numbering continues across chapters.
 *
 *  (b) Footnote sections at the end — `1. See e.g. ...`
 *      These also restart from 1 but have long bodies. When numbering goes backward
 *      with a long body, we treat it as end-of-document and break.
 */
function trimNonMonotonic(paragraphs: Paragraph[]): Paragraph[] {
  const out: Paragraph[] = []
  let last = 0
  let consecutiveSkips = 0
  for (const p of paragraphs) {
    const n = parseInt(p.num, 10)
    if (n <= last) {
      if (p.body.length < 200) {
        // Chapter subheading (Roman numerals rendered as 1./2./3.) OR
        // a footnote block. We skip; if we see 3 in a row we conclude we hit
        // the footnote section and bail.
        consecutiveSkips++
        if (consecutiveSkips >= 3) break
        continue
      }
      // Long-body restart: footnote section with paragraph-length notes
      break
    }
    consecutiveSkips = 0
    out.push(p)
    last = n
  }
  return out
}

/**
 * Inside one paragraph, the PDF/HTML extraction may have wrapped lines.
 * Collapse single newlines into spaces while keeping double-newlines (sub-paragraph breaks).
 */
function collapseInternalWrap(s: string): string {
  return s
    .split(/\n{2,}/)
    .map(seg => seg.replace(/\n/g, ' ').replace(/\s{2,}/g, ' ').trim())
    .filter(Boolean)
    .join('\n\n')
}

/**
 * Merge parallel paragraph lists (中 / 英 / 拉) into a single row table aligned by `num`.
 *
 * Uses the union of all paragraph numbers across all langs as rows; missing langs get ''.
 * Row order: numeric paragraph number ascending.
 */
export interface ParagraphRow {
  num: string
  byLang: Record<string, string>
}

export function alignParagraphs(
  byLang: Record<string, Paragraph[]>,
): ParagraphRow[] {
  const allNums = new Set<string>()
  for (const list of Object.values(byLang)) {
    for (const p of list) allNums.add(p.num)
  }
  const sortedNums = Array.from(allNums).sort((a, b) => parseInt(a, 10) - parseInt(b, 10))

  return sortedNums.map(num => {
    const row: ParagraphRow = { num, byLang: {} }
    for (const [lang, list] of Object.entries(byLang)) {
      const p = list.find(x => x.num === num)
      row.byLang[lang] = p?.body ?? ''
    }
    return row
  })
}
