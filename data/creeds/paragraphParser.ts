/**
 * Structured parser for council documents (Vatican II etc.).
 *
 * Input: vatican.va HTML extracted via scripts/rebuild_vatican_ii_html.py to a
 * markdown-like .txt with these conventions:
 *
 *   ## Heading text          -> section heading
 *   N. Paragraph body...     -> numbered main paragraph
 *   [^N]: Footnote text...   -> footnote definition (after '## Footnotes' line)
 *   inline [^N] or (N)       -> footnote reference (UI renders as clickable anchor)
 *
 * For Chinese (pdftotext -layout output) the format is less reliable; we still
 * try the same patterns but degrade gracefully.
 */

export interface HeadingBlock {
  kind: 'heading'
  text: string
}

export interface ParagraphBlock {
  kind: 'paragraph'
  num: string
  body: string
}

export type Block = HeadingBlock | ParagraphBlock

export interface FootnoteDef {
  num: string
  body: string
}

export interface ParsedDoc {
  blocks: Block[]
  footnotes: FootnoteDef[]
}

export function parseDoc(text: string): ParsedDoc {
  if (!text || typeof text !== 'string') return { blocks: [], footnotes: [] }
  const normalized = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n')
  const rawBlocks = normalized.split(/\n{2,}/)

  const blocks: Block[] = []
  const footnotes: FootnoteDef[] = []

  let lastParaNum = 0
  let consecutiveSkips = 0
  let inFootnoteSection = false

  for (const raw of rawBlocks) {
    const block = raw.trim()
    if (!block) continue

    // Language switcher row from vatican.va top
    if (/^\[\s*[A-Z]{2}(\s*-\s*[A-Z]{2})+\s*\]$/.test(block)) continue
    // Top-level title line we already capture in metadata
    if (/^[A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+\s+-\s+Full/.test(block)) continue
    // Horizontal rule marker
    if (block === '---') continue

    // Heading lines (rebuild_vatican_ii_html.py adds '## ' prefix for <i><b> wraps)
    if (block.startsWith('## ')) {
      const text = block.slice(3).trim()
      if (/^Footnotes?$/i.test(text)) {
        inFootnoteSection = true
        continue
      }
      // Heading might appear inline with paragraph after (shouldn't, but guard)
      blocks.push({ kind: 'heading', text })
      consecutiveSkips = 0
      continue
    }

    // [^N]: definition (Phase B extracts footnote defs this way)
    const fnDef = block.match(/^\[\^(\d{1,4})\]:\s*([\s\S]+)$/)
    if (fnDef) {
      footnotes.push({ num: fnDef[1], body: collapseInternalWrap(fnDef[2]) })
      continue
    }

    // If we've entered the footnote section, prefer footnote-def parsing
    if (inFootnoteSection) {
      const m = block.match(/^(\d{1,4})\s*\.?\s+([\s\S]+)$/)
      if (m) {
        footnotes.push({ num: m[1], body: collapseInternalWrap(m[2]) })
      }
      continue
    }

    // Standard `N. body` numbered paragraph
    //   Cap 600 covers papal encyclicals (longest known: Evangelii Gaudium 288;
    //   Vatican II longest: GS at 93). Above 600 is almost certainly a year
    //   ("1990. Anno illo...") or some other false positive.
    const m = block.match(/^(\d{1,3})\s*\.?\s+([\s\S]*)$/)
    if (m) {
      const n = parseInt(m[1], 10)
      const bodyAfter = m[2].trim()
      if (n >= 1 && n <= 600 && bodyAfter.length >= 4) {
        if (n <= lastParaNum) {
          // Backward jump — likely a chapter sub-header rendered as "1." or a
          // footnote section that wasn't tagged.
          if (bodyAfter.length < 200) {
            consecutiveSkips++
            if (consecutiveSkips >= 3) {
              // Treat the rest as footnote definitions
              inFootnoteSection = true
              footnotes.push({ num: m[1], body: collapseInternalWrap(bodyAfter) })
            }
            continue
          }
          // Long body backward jump → start treating as footnote-def
          inFootnoteSection = true
          footnotes.push({ num: m[1], body: collapseInternalWrap(bodyAfter) })
          continue
        }
        consecutiveSkips = 0
        blocks.push({ kind: 'paragraph', num: m[1], body: collapseInternalWrap(bodyAfter) })
        lastParaNum = n
        continue
      }
    }

    // Non-numbered block: either a sub-paragraph continuation or noise.
    // Append to the most recent paragraph if any.
    const lastBlock = blocks[blocks.length - 1]
    if (lastBlock && lastBlock.kind === 'paragraph') {
      lastBlock.body += '\n\n' + collapseInternalWrap(block)
    }
  }

  return { blocks, footnotes }
}

function collapseInternalWrap(s: string): string {
  return s
    .split(/\n{2,}/)
    .map(seg => seg.replace(/\n/g, ' ').replace(/\s{2,}/g, ' ').trim())
    .filter(Boolean)
    .join('\n\n')
}

// ── Backward-compat exports for existing callers (textLoader / detail page) ──

export interface Paragraph {
  num: string
  body: string
}

/** Legacy: return paragraphs only (no headings/footnotes). */
export function parseParagraphs(text: string): Paragraph[] {
  return parseDoc(text).blocks
    .filter((b): b is ParagraphBlock => b.kind === 'paragraph')
    .map(b => ({ num: b.num, body: b.body }))
}

export interface ParagraphRow {
  num: string
  byLang: Record<string, string>
}

/** Outer-join paragraphs across languages by `num`. */
export function alignParagraphs(byLang: Record<string, Paragraph[]>): ParagraphRow[] {
  const allNums = new Set<string>()
  for (const list of Object.values(byLang)) for (const p of list) allNums.add(p.num)
  const sortedNums = Array.from(allNums).sort((a, b) => parseInt(a, 10) - parseInt(b, 10))
  return sortedNums.map(num => {
    const row: ParagraphRow = { num, byLang: {} }
    for (const [lang, list] of Object.entries(byLang)) {
      row.byLang[lang] = list.find(p => p.num === num)?.body ?? ''
    }
    return row
  })
}

// ── New: aligned doc rows (heading + paragraph) for richer UI ──

export type DocRow =
  | { kind: 'heading'; byLang: Record<string, string> }
  | { kind: 'paragraph'; num: string; byLang: Record<string, string> }

export interface AlignedDoc {
  rows: DocRow[]
  footnotesByLang: Record<string, FootnoteDef[]>
}

/**
 * Align multiple ParsedDocs into a single row stream.
 *
 * Strategy: use the first non-empty language's `blocks` as the spine (this is
 * the source-of-truth for heading positions); for paragraphs, look up the
 * matching `num` in each language; for headings, look up the same heading
 * position across languages (we use the *next* heading occurrence per lang).
 */
export function alignDocs(byLang: Record<string, ParsedDoc>): AlignedDoc {
  const langs = Object.keys(byLang)
  // Pick a spine — prefer 'orig' (latin) if available, else 'en', else first.
  const spineLang = langs.find(l => l === 'orig' && byLang[l]?.blocks.length > 0)
    ?? langs.find(l => l === 'en' && byLang[l]?.blocks.length > 0)
    ?? langs.find(l => byLang[l]?.blocks.length > 0)

  if (!spineLang) {
    return { rows: [], footnotesByLang: {} }
  }

  const spine = byLang[spineLang].blocks
  // Track heading index per lang for sequential heading lookup
  const headingIdx: Record<string, number> = {}
  for (const l of langs) headingIdx[l] = 0

  const rows: DocRow[] = []
  for (const block of spine) {
    if (block.kind === 'heading') {
      const byLangText: Record<string, string> = {}
      for (const l of langs) {
        const headings = byLang[l]?.blocks.filter((b): b is HeadingBlock => b.kind === 'heading') ?? []
        byLangText[l] = headings[headingIdx[l]]?.text ?? ''
        headingIdx[l]++
      }
      rows.push({ kind: 'heading', byLang: byLangText })
    } else {
      const byLangText: Record<string, string> = {}
      for (const l of langs) {
        const para = byLang[l]?.blocks.find(b => b.kind === 'paragraph' && b.num === block.num)
        byLangText[l] = (para && para.kind === 'paragraph') ? para.body : ''
      }
      rows.push({ kind: 'paragraph', num: block.num, byLang: byLangText })
    }
  }

  const footnotesByLang: Record<string, FootnoteDef[]> = {}
  for (const l of langs) footnotesByLang[l] = byLang[l]?.footnotes ?? []

  return { rows, footnotesByLang }
}
