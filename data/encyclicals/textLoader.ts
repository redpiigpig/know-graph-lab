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

const gregoryXviLoaders = import.meta.glob(
  './19c-gregory-xvi/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const piusViiiLoaders = import.meta.glob(
  './19c-pius-viii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const leoXiiLoaders = import.meta.glob(
  './19c-leo-xii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const piusViiLoaders = import.meta.glob(
  './19c-pius-vii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const piusViLoaders = import.meta.glob(
  './18c-pius-vi/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const clementXivLoaders = import.meta.glob(
  './18c-clement-xiv/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const clementXiiiLoaders = import.meta.glob(
  './18c-clement-xiii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const benedictXivLoaders = import.meta.glob(
  './18c-benedict-xiv/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const clementXiiLoaders = import.meta.glob(
  './18c-clement-xii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const clementXiLoaders = import.meta.glob(
  './18c-clement-xi/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const innocentXiLoaders = import.meta.glob(
  './17c-innocent-xi/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const innocentXiiLoaders = import.meta.glob(
  './17c-innocent-xii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const innocentXLoaders = import.meta.glob(
  './17c-innocent-x/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const gregoryXvLoaders = import.meta.glob(
  './17c-gregory-xv/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const piusIvLoaders = import.meta.glob(
  './16c-pius-iv/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const juliusIiLoaders = import.meta.glob(
  './16c-julius-ii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const paulIvLoaders = import.meta.glob(
  './16c-paul-iv/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const gregoryXiiiLoaders = import.meta.glob(
  './16c-gregory-xiii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const piusIiLoaders = import.meta.glob(
  './15c-pius-ii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const innocentViiiLoaders = import.meta.glob(
  './15c-innocent-viii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const alexanderViiLoaders = import.meta.glob(
  './17c-alexander-vii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const clementViiiLoaders = import.meta.glob(
  './16c-clement-viii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const sixtusVLoaders = import.meta.glob(
  './16c-sixtus-v/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const piusVLoaders = import.meta.glob(
  './16c-pius-v/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const paulIiiLoaders = import.meta.glob(
  './16c-paul-iii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const leoXLoaders = import.meta.glob(
  './16c-leo-x/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const alexanderViLoaders = import.meta.glob(
  './15c-alexander-vi/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const sixtusIvLoaders = import.meta.glob(
  './15c-sixtus-iv/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const nicholasVLoaders = import.meta.glob(
  './15c-nicholas-v/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const eugeneIvLoaders = import.meta.glob(
  './15c-eugene-iv/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const benedictXiiLoaders = import.meta.glob(
  './14c-benedict-xii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const johnXxiiLoaders = import.meta.glob(
  './14c-john-xxii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const clementVLoaders = import.meta.glob(
  './14c-clement-v/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const bonifaceViiiLoaders = import.meta.glob(
  './13c-boniface-viii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const nicholasIvLoaders = import.meta.glob(
  './13c-nicholas-iv/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const nicholasIiiLoaders = import.meta.glob(
  './13c-nicholas-iii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const alexanderIvLoaders = import.meta.glob(
  './13c-alexander-iv/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const innocentIvLoaders = import.meta.glob(
  './13c-innocent-iv/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const gregoryXLoaders = import.meta.glob(
  './13c-gregory-x/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const gregoryIxLoaders = import.meta.glob(
  './13c-gregory-ix/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const honoriusIiiLoaders = import.meta.glob(
  './13c-honorius-iii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const gregoryViiLoaders = import.meta.glob(
  './11c-gregory-vii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const leoILoaders = import.meta.glob(
  './5c-leo-i/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const gelasiusILoaders = import.meta.glob(
  './5c-gelasius-i/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const gregoryILoaders = import.meta.glob(
  './6c-gregory-i/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const innocentIiiLoaders = import.meta.glob(
  './13c-innocent-iii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const nicholasILoaders = import.meta.glob(
  './9c-nicholas-i/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const damasusILoaders = import.meta.glob(
  './4c-damasus-i/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const siriciusLoaders = import.meta.glob(
  './4c-siricius/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const hormisdasLoaders = import.meta.glob(
  './6c-hormisdas/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const urbanIiLoaders = import.meta.glob(
  './11c-urban-ii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const innocentILoaders = import.meta.glob(
  './5c-innocent-i/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const celestineILoaders = import.meta.glob(
  './5c-celestine-i/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const sixtusIiiLoaders = import.meta.glob(
  './5c-sixtus-iii/*.txt',
  { query: '?raw', import: 'default' },
) as Record<string, () => Promise<string>>

const vigiliusLoaders = import.meta.glob(
  './6c-vigilius/*.txt',
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
  'gregory-xvi': gregoryXviLoaders,
  'pius-viii': piusViiiLoaders,
  'leo-xii': leoXiiLoaders,
  'pius-vii': piusViiLoaders,
  'pius-vi': piusViLoaders,
  'clement-xiv': clementXivLoaders,
  'clement-xiii': clementXiiiLoaders,
  'benedict-xiv': benedictXivLoaders,
  'clement-xii': clementXiiLoaders,
  'clement-xi': clementXiLoaders,
  'innocent-xii': innocentXiiLoaders,
  'innocent-xi': innocentXiLoaders,
  'innocent-x': innocentXLoaders,
  'gregory-xv': gregoryXvLoaders,
  'alexander-vii': alexanderViiLoaders,
  'clement-viii': clementViiiLoaders,
  'sixtus-v': sixtusVLoaders,
  'gregory-xiii': gregoryXiiiLoaders,
  'pius-v': piusVLoaders,
  'pius-iv': piusIvLoaders,
  'paul-iv': paulIvLoaders,
  'paul-iii': paulIiiLoaders,
  'julius-ii': juliusIiLoaders,
  'leo-x': leoXLoaders,
  'alexander-vi': alexanderViLoaders,
  'innocent-viii': innocentViiiLoaders,
  'sixtus-iv': sixtusIvLoaders,
  'pius-ii': piusIiLoaders,
  'nicholas-v': nicholasVLoaders,
  'eugene-iv': eugeneIvLoaders,
  'benedict-xii': benedictXiiLoaders,
  'john-xxii': johnXxiiLoaders,
  'clement-v': clementVLoaders,
  'boniface-viii': bonifaceViiiLoaders,
  'nicholas-iv': nicholasIvLoaders,
  'nicholas-iii': nicholasIiiLoaders,
  'alexander-iv': alexanderIvLoaders,
  'innocent-iv': innocentIvLoaders,
  'gregory-x': gregoryXLoaders,
  'gregory-ix': gregoryIxLoaders,
  'honorius-iii': honoriusIiiLoaders,
  'innocent-iii': innocentIiiLoaders,
  'gregory-vii': gregoryViiLoaders,
  'gregory-i': gregoryILoaders,
  'gelasius-i': gelasiusILoaders,
  'leo-i': leoILoaders,
  'nicholas-i': nicholasILoaders,
  'damasus-i': damasusILoaders,
  'siricius': siriciusLoaders,
  'hormisdas': hormisdasLoaders,
  'urban-ii': urbanIiLoaders,
  'innocent-i': innocentILoaders,
  'celestine-i': celestineILoaders,
  'sixtus-iii': sixtusIiiLoaders,
  'vigilius': vigiliusLoaders,
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
  'gregory-xvi': './19c-gregory-xvi',
  'pius-viii': './19c-pius-viii',
  'leo-xii': './19c-leo-xii',
  'pius-vii': './19c-pius-vii',
  'pius-vi': './18c-pius-vi',
  'clement-xiv': './18c-clement-xiv',
  'clement-xiii': './18c-clement-xiii',
  'benedict-xiv': './18c-benedict-xiv',
  'clement-xii': './18c-clement-xii',
  'clement-xi': './18c-clement-xi',
  'innocent-xii': './17c-innocent-xii',
  'innocent-xi': './17c-innocent-xi',
  'innocent-x': './17c-innocent-x',
  'gregory-xv': './17c-gregory-xv',
  'alexander-vii': './17c-alexander-vii',
  'clement-viii': './16c-clement-viii',
  'sixtus-v': './16c-sixtus-v',
  'gregory-xiii': './16c-gregory-xiii',
  'pius-v': './16c-pius-v',
  'pius-iv': './16c-pius-iv',
  'paul-iv': './16c-paul-iv',
  'paul-iii': './16c-paul-iii',
  'julius-ii': './16c-julius-ii',
  'leo-x': './16c-leo-x',
  'alexander-vi': './15c-alexander-vi',
  'innocent-viii': './15c-innocent-viii',
  'sixtus-iv': './15c-sixtus-iv',
  'pius-ii': './15c-pius-ii',
  'nicholas-v': './15c-nicholas-v',
  'eugene-iv': './15c-eugene-iv',
  'benedict-xii': './14c-benedict-xii',
  'john-xxii': './14c-john-xxii',
  'clement-v': './14c-clement-v',
  'boniface-viii': './13c-boniface-viii',
  'nicholas-iv': './13c-nicholas-iv',
  'nicholas-iii': './13c-nicholas-iii',
  'alexander-iv': './13c-alexander-iv',
  'innocent-iv': './13c-innocent-iv',
  'gregory-x': './13c-gregory-x',
  'gregory-ix': './13c-gregory-ix',
  'honorius-iii': './13c-honorius-iii',
  'innocent-iii': './13c-innocent-iii',
  'gregory-vii': './11c-gregory-vii',
  'gregory-i': './6c-gregory-i',
  'gelasius-i': './5c-gelasius-i',
  'leo-i': './5c-leo-i',
  'nicholas-i': './9c-nicholas-i',
  'damasus-i': './4c-damasus-i',
  'siricius': './4c-siricius',
  'hormisdas': './6c-hormisdas',
  'urban-ii': './11c-urban-ii',
  'innocent-i': './5c-innocent-i',
  'celestine-i': './5c-celestine-i',
  'sixtus-iii': './5c-sixtus-iii',
  'vigilius': './6c-vigilius',
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
