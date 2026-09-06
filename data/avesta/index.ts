import type { ZoroCanon, ZoroDivision, ZoroPart, ZoroText, ZoroVolume, ColumnStatus } from './types'
import { AVESTAN_CANON } from './avestan'
import { PAHLAVI_CANON } from './pahlavi'
import { LATER_CANON } from './later'
import { EPIGRAPHY_CANON } from './epigraphy'

export * from './types'
export { AVESTAN_CANON } from './avestan'
export { PAHLAVI_CANON } from './pahlavi'
export { LATER_CANON } from './later'
export { EPIGRAPHY_CANON } from './epigraphy'

/** 四藏。前三藏為經典，第四藏（王室銘文）為附錄，scriptural = false。 */
export const CANONS: ZoroCanon[] = [AVESTAN_CANON, PAHLAVI_CANON, LATER_CANON, EPIGRAPHY_CANON]

/** 全藏斷限。與希臘羅馬大藏經不同，祆教沒有終點——它今天還在誦。 */
export const TERMINUS = {
  from: '約公元前 1500 年（迦薩的語言年代）',
  to: '無終點',
  note:
    '本藏經不設下限，因為祆教沒有停。伊朗亞茲德與印度孟買的火廟今天仍在誦唸耶斯那，'
    + '所用的正是本藏收錄的文本。收錄下限止於十九世紀成書者，是編纂上的權宜而非宗教史上的斷代。',
}

export function findCanon(key: string): ZoroCanon | undefined {
  return CANONS.find(c => c.key === key)
}

export function findVolume(canonKey: string, volumeKey: string): ZoroVolume | undefined {
  return findCanon(canonKey)?.volumes.find(v => v.key === volumeKey)
}

export function volumesOf(canon: ZoroCanon, part: ZoroPart): ZoroVolume[] {
  return part.volumes
    .map(k => canon.volumes.find(v => v.key === k))
    .filter((v): v is ZoroVolume => Boolean(v))
}

/** 一條篇章在全藏中的位置，供搜尋與 reader 使用 */
export interface TextLocation {
  canon: ZoroCanon
  volume: ZoroVolume
  division: ZoroDivision
  text: ZoroText
}

let _index: Map<string, TextLocation> | null = null

/** slug → 位置。slug 全藏唯一；重複會在 buildIndex 時擲錯，不容默默覆蓋。 */
export function textIndex(): Map<string, TextLocation> {
  if (_index) return _index
  const m = new Map<string, TextLocation>()
  for (const canon of CANONS) {
    for (const volume of canon.volumes) {
      for (const division of volume.divisions) {
        for (const text of division.texts) {
          const prev = m.get(text.slug)
          if (prev) {
            // 靜默覆蓋會讓兩篇共用一頁而版面完全正常——正是最難發現的一類錯。
            throw new Error(
              `祆教經典 slug 重複：'${text.slug}' 同時出現於 `
              + `${prev.canon.name}/${prev.volume.name} 與 ${canon.name}/${volume.name}`,
            )
          }
          m.set(text.slug, { canon, volume, division, text })
        }
      }
    }
  }
  _index = m
  return m
}

export function findText(slug: string): TextLocation | undefined {
  return textIndex().get(slug)
}

/** 全藏所有篇章，依藏→卷→部的順序 */
export function allTexts(): TextLocation[] {
  return [...textIndex().values()]
}

/** 三欄取源的統計。這是本藏經最誠實的一張表：哪一欄真的有東西。 */
export interface ColumnTally {
  total: number
  orig: Record<string, number>
  en: Record<string, number>
  zh: Record<string, number>
}

export function tallyColumns(locs: TextLocation[] = allTexts()): ColumnTally {
  const t: ColumnTally = { total: locs.length, orig: {}, en: {}, zh: {} }
  for (const { text, division } of locs) {
    const c: ColumnStatus = text.columns ?? division.columns ?? { orig: 'none', en: 'none', zh: 'none' }
    t.orig[c.orig] = (t.orig[c.orig] ?? 0) + 1
    t.en[c.en] = (t.en[c.en] ?? 0) + 1
    t.zh[c.zh] = (t.zh[c.zh] ?? 0) + 1
  }
  return t
}

/** 搜尋：比對中文名、原文名、英文名、編號與作者 */
export function searchTexts(q: string): TextLocation[] {
  const s = q.trim().toLowerCase()
  if (!s) return []
  return allTexts().filter(({ text, volume, canon }) =>
    [text.title_zh, text.title_orig, text.title_en, text.siglum, text.author, text.note, volume.name, canon.name]
      .some(v => v?.toLowerCase().includes(s)),
  )
}
