/**
 * Lazy text loader for large creed/council documents.
 *
 * 用 import.meta.glob 的 lazy（非 eager）模式 — 每個 .txt 只有在實際呼叫
 * loader 時才會被 fetch + 加入 bundle，避免列表 page 或 SSR 階段 eager
 * 載入 16 份梵二 × 3 語 × 平均 50KB = ~9MB 文本撐爆 Vite IPC buffer。
 *
 * textKey 對應規則：
 *   - 梵二（vatican-ii/）：'sc-latin' / 'sc-english' / 'sc-chinese' 等 16 份 × 3 語
 *     (im / lg / oe / ur / cd / pc / ot / ge / na / dv / aa / dh / ag / po / gs)
 *   - 梵一（vatican-i/）：'df-{lang}' / 'pa-{lang}' — Dei Filius / Pastor Aeternus
 */

import { parseParagraphs, parseDoc, type Paragraph, type ParsedDoc } from './paragraphParser'

const vat2Loaders = import.meta.glob(
  './ecumenical-councils/vatican-ii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const vat1Loaders = import.meta.glob(
  './ecumenical-councils/vatican-i/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const trentLoaders = import.meta.glob(
  './ecumenical-councils/trent/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const medievalLoaders = import.meta.glob(
  './ecumenical-councils/medieval/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

/** Vatican I document code prefixes — used to route textKey to vatican-i/ folder. */
const VAT1_PREFIXES = new Set(['df', 'pa'])

function resolveLoader(textKey: string): (() => Promise<string>) | undefined {
  // Medieval councils 8-18: textKeys start with 'medieval-' (e.g. medieval-12-chinese)
  if (textKey.startsWith('medieval-')) {
    return medievalLoaders[`./ecumenical-councils/medieval/${textKey}.txt`]
  }
  // Trent: textKeys all start with 'trent-' (e.g. trent-06-chinese)
  if (textKey.startsWith('trent-')) {
    return trentLoaders[`./ecumenical-councils/trent/${textKey}.txt`]
  }
  const prefix = textKey.split('-')[0]
  if (VAT1_PREFIXES.has(prefix)) {
    return vat1Loaders[`./ecumenical-councils/vatican-i/${textKey}.txt`]
  }
  return vat2Loaders[`./ecumenical-councils/vatican-ii/${textKey}.txt`]
}

/** 已載入過的 text cache（避免重複網路 / fs 載入） */
const cache = new Map<string, string>()
const paragraphCache = new Map<string, Paragraph[]>()
const docCache = new Map<string, ParsedDoc>()

export async function loadCreedText(textKey: string): Promise<string> {
  if (cache.has(textKey)) return cache.get(textKey)!
  const loader = resolveLoader(textKey)
  if (!loader) throw new Error(`Creed text not found for key: ${textKey}`)
  const text = await loader()
  cache.set(textKey, text)
  return text
}

/**
 * Load and parse a council document into numbered paragraphs.
 * Useful for Bible-style row-by-row parallel comparison.
 */
export async function loadCreedParagraphs(textKey: string): Promise<Paragraph[]> {
  if (paragraphCache.has(textKey)) return paragraphCache.get(textKey)!
  const text = await loadCreedText(textKey)
  const paragraphs = parseParagraphs(text)
  paragraphCache.set(textKey, paragraphs)
  return paragraphs
}

/** Load and fully parse a document into structured Blocks + footnotes. */
export async function loadCreedDoc(textKey: string): Promise<ParsedDoc> {
  if (docCache.has(textKey)) return docCache.get(textKey)!
  const text = await loadCreedText(textKey)
  const doc = parseDoc(text)
  docCache.set(textKey, doc)
  return doc
}

export function availableTextKeys(): string[] {
  const keys: string[] = []
  for (const p of Object.keys(medievalLoaders)) {
    keys.push(p.replace('./ecumenical-councils/medieval/', '').replace(/\.txt$/, ''))
  }
  for (const p of Object.keys(trentLoaders)) {
    keys.push(p.replace('./ecumenical-councils/trent/', '').replace(/\.txt$/, ''))
  }
  for (const p of Object.keys(vat1Loaders)) {
    keys.push(p.replace('./ecumenical-councils/vatican-i/', '').replace(/\.txt$/, ''))
  }
  for (const p of Object.keys(vat2Loaders)) {
    keys.push(p.replace('./ecumenical-councils/vatican-ii/', '').replace(/\.txt$/, ''))
  }
  return keys
}
