// 古近東大藏經 —— 正文（三欄對照）的型別與惰性載入
//
// 一篇一檔：data/near-east/sources/text/<slug>.json，檔名即書目 slug。
// manifest.json 由取源腳本寫（scripts/near_east_etcsl.py 等），記哪些 slug 有正文、各欄現況；
// 書目頁的三欄色塊以 manifest 為準，覆蓋書目裡的「可取得」預設值。
//
// 🚨 import.meta.glob 不可用 eager：希臘羅馬大藏經語料漲到數 MB 後整站變慢，才改成惰性載入。

import manifestJson from './manifest.json'
import type { ColumnStatus } from '../types'

export interface NeSegment {
  /** 原書行號範圍，照抄來源（ETCSL「11–16」），不自編 */
  ref: string
  /** 原文轉寫，行與行以換行分隔 */
  orig: string
  orig_lines?: string[]
  en: string
  zh?: string
}

export interface NeComposition {
  /** 來源編號，如 ETCSL 的 1.1.1 */
  num: string
  title_en: string
  title_zh?: string
  segments: NeSegment[]
}

export interface NeSourceDoc {
  slug: string
  source: string
  siglum: string
  source_url?: string
  license?: string
  compositions: NeComposition[]
}

export interface ManifestEntry {
  source: string
  segments: number
  orig: ColumnStatus['orig']
  en: ColumnStatus['en']
  zh: ColumnStatus['zh']
}

export const MANIFEST = manifestJson as Record<string, ManifestEntry>

export function hasText(slug: string): boolean {
  return slug in MANIFEST
}

const loaders = import.meta.glob<{ default: NeSourceDoc }>('./text/*.json')

export async function loadText(slug: string): Promise<NeSourceDoc | null> {
  const load = loaders[`./text/${slug}.json`]
  if (!load) return null
  return (await load()).default
}
