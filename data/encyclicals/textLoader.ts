/**
 * Lazy text loader for papal documents.
 *
 * 用 import.meta.glob 的 lazy（非 eager）模式 — 每個 .txt 只在實際呼叫時 fetch +
 * 加入 bundle，避免列表頁／SSR 階段把所有 encyclical 文本撐爆 Vite IPC buffer。
 *
 * textKey 對應規則：
 *   data/encyclicals/{NNc-pope-slug}/{textKey}.txt
 *   例：data/encyclicals/21c-francis/laudato-si-2015-latin.txt
 *       → textKey = 'laudato-si-2015-latin'
 *
 * 各世紀資料夾的 loader 個別 glob，避免 Vite 一次性 walk 整個 data/encyclicals/。
 */

import { parseDoc, type ParsedDoc } from '../creeds/paragraphParser'

const francisLoaders = import.meta.glob(
  './21c-francis/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const benedict16Loaders = import.meta.glob(
  './21c-benedict-xvi/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const johnPaul2Loaders = import.meta.glob(
  './20c-john-paul-ii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const paul6Loaders = import.meta.glob(
  './20c-paul-vi/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const john23Loaders = import.meta.glob(
  './20c-john-xxiii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const pius12Loaders = import.meta.glob(
  './20c-pius-xii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const pius11Loaders = import.meta.glob(
  './20c-pius-xi/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const benedict15Loaders = import.meta.glob(
  './20c-benedict-xv/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const pius10Loaders = import.meta.glob(
  './20c-pius-x/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const leo13Loaders = import.meta.glob(
  './19c-leo-xiii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const pius9Loaders = import.meta.glob(
  './19c-pius-ix/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

/** popeSlug → loaders；新增教宗時加一條 */
const POPE_LOADERS: Record<string, Record<string, () => Promise<string>>> = {
  'francis': francisLoaders,
  'benedict-xvi': benedict16Loaders,
  'john-paul-ii': johnPaul2Loaders,
  'paul-vi': paul6Loaders,
  'john-xxiii': john23Loaders,
  'pius-xii': pius12Loaders,
  'pius-xi': pius11Loaders,
  'benedict-xv': benedict15Loaders,
  'pius-x': pius10Loaders,
  'leo-xiii': leo13Loaders,
  'pius-ix': pius9Loaders,
}

/** popeSlug → 資料夾前綴；reverse map from POPE_LOADERS keys */
const POPE_FOLDER: Record<string, string> = {
  'francis': './21c-francis',
  'benedict-xvi': './21c-benedict-xvi',
  'john-paul-ii': './20c-john-paul-ii',
  'paul-vi': './20c-paul-vi',
  'john-xxiii': './20c-john-xxiii',
  'pius-xii': './20c-pius-xii',
  'pius-xi': './20c-pius-xi',
  'benedict-xv': './20c-benedict-xv',
  'pius-x': './20c-pius-x',
  'leo-xiii': './19c-leo-xiii',
  'pius-ix': './19c-pius-ix',
}

function resolveLoader(popeSlug: string, textKey: string): (() => Promise<string>) | undefined {
  const loaders = POPE_LOADERS[popeSlug]
  const folder = POPE_FOLDER[popeSlug]
  if (!loaders || !folder) return undefined
  return loaders[`${folder}/${textKey}.txt`]
}

const cache = new Map<string, string>()
const docCache = new Map<string, ParsedDoc>()

function cacheKey(popeSlug: string, textKey: string): string {
  return `${popeSlug}/${textKey}`
}

export async function loadPapalText(popeSlug: string, textKey: string): Promise<string> {
  const k = cacheKey(popeSlug, textKey)
  if (cache.has(k)) return cache.get(k)!
  const loader = resolveLoader(popeSlug, textKey)
  if (!loader) throw new Error(`Papal text not found: ${k}`)
  const text = await loader()
  cache.set(k, text)
  return text
}

export async function loadPapalDoc(popeSlug: string, textKey: string): Promise<ParsedDoc> {
  const k = cacheKey(popeSlug, textKey)
  if (docCache.has(k)) return docCache.get(k)!
  const text = await loadPapalText(popeSlug, textKey)
  const doc = parseDoc(text)
  docCache.set(k, doc)
  return doc
}
