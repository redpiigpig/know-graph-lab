/**
 * Papal Magisterium 資料註冊器
 *
 * 新增一份教宗文件：
 *   1. 在對應世紀子資料夾建立 .ts 檔
 *      （例：21c-francis/laudato-si-2015.ts）
 *   2. 同資料夾放 {slug}-latin.txt / {slug}-english.txt / {slug}-chinese.txt
 *      檔名須對應 metadata 的 textKey
 *   3. 在本檔 import 並加進 ALL_DOCUMENTS
 *   4. 重啟 dev server 即可在 /encyclicals 看到
 */

import type { PapalDocument } from './types'

// ── 21c Francis ──────────────────────────────────────────────
import { laudatoSi2015 } from './21c-francis/laudato-si-2015'
import { fratelliTutti2020 } from './21c-francis/fratelli-tutti-2020'
import { dilexitNos2024 } from './21c-francis/dilexit-nos-2024'
import { lumenFidei2013 } from './21c-francis/lumen-fidei-2013'

export const ALL_DOCUMENTS: PapalDocument[] = [
  laudatoSi2015,
  fratelliTutti2020,
  dilexitNos2024,
  lumenFidei2013,
]

export function findDocument(slug: string): PapalDocument | undefined {
  return ALL_DOCUMENTS.find(d => d.slug === slug)
}

export function documentsByPope(popeSlug: string): PapalDocument[] {
  return ALL_DOCUMENTS
    .filter(d => d.popeSlug === popeSlug)
    .sort((a, b) => a.promulgationDate.localeCompare(b.promulgationDate))
}

/** 按世紀分組（新→舊）；每組內按文件年份新→舊排序 */
export function documentsByCentury(): { century: number; docs: PapalDocument[] }[] {
  const map = new Map<number, PapalDocument[]>()
  for (const d of ALL_DOCUMENTS) {
    if (!map.has(d.century)) map.set(d.century, [])
    map.get(d.century)!.push(d)
  }
  return [...map.entries()]
    .sort((a, b) => b[0] - a[0])
    .map(([century, docs]) => ({
      century,
      docs: docs.sort((a, b) => b.promulgationDate.localeCompare(a.promulgationDate)),
    }))
}

export function documentsInCentury(century: number): PapalDocument[] {
  return ALL_DOCUMENTS
    .filter(d => d.century === century)
    .sort((a, b) => b.promulgationDate.localeCompare(a.promulgationDate))
}

/** 單一教宗在指定世紀的文件數（用來在世紀頁顯示教宗的「本世紀著作數」chip） */
export function documentCountForPopeInCentury(popeSlug: string, century: number): number {
  return ALL_DOCUMENTS.filter(d => d.popeSlug === popeSlug && d.century === century).length
}

export * from './types'
export * from './popes-catalog'
