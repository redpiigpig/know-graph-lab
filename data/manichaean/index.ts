import type { ManiCanon, ManiDivision, ManiPart, ManiText, ManiVolume, ColumnStatus } from './types'
import { CANON_CANON } from './canon'
import { COPTIC_CANON } from './coptic'
import { IRANIAN_CANON } from './iranian'
import { CHINESE_CANON } from './chinese'
import { TESTIMONIA_CANON } from './testimonia'

export * from './types'
export { CANON_CANON } from './canon'
export { COPTIC_CANON } from './coptic'
export { IRANIAN_CANON } from './iranian'
export { CHINESE_CANON } from './chinese'
export { TESTIMONIA_CANON } from './testimonia'

/** 五藏。前四藏為摩尼教文獻，第五藏（敵證與外部記述）為附錄，scriptural = false。 */
export const CANONS: ManiCanon[] = [
  CANON_CANON,
  COPTIC_CANON,
  IRANIAN_CANON,
  CHINESE_CANON,
  TESTIMONIA_CANON,
]

/** 全藏斷限。與祆教相反：摩尼教有明確的終點。 */
export const TERMINUS = {
  from: '約公元 240 年（摩尼開始傳教並親撰正典）',
  to: '約公元 1600 年（福建明教的最後痕跡）',
  note:
    '摩尼教與祆教不同——它**結束了**。'
    + '在西方，六世紀後的拉丁世界已無實際教團，「摩尼教徒」變成一個罵人的標籤；'
    + '在中亞，回鶻汗國覆亡後逐漸消散；'
    + '在中國，明教溶入民間法事而失去自我認同，最後的可辨痕跡在福建，約止於明代。'
    + '本藏經因此有下限。這個下限不是編纂上的權宜，而是一個宗教實際消失的時間。',
}

export function findCanon(key: string): ManiCanon | undefined {
  return CANONS.find(c => c.key === key)
}

export function findVolume(canonKey: string, volumeKey: string): ManiVolume | undefined {
  return findCanon(canonKey)?.volumes.find(v => v.key === volumeKey)
}

export function volumesOf(canon: ManiCanon, part: ManiPart): ManiVolume[] {
  return part.volumes
    .map(k => canon.volumes.find(v => v.key === k))
    .filter((v): v is ManiVolume => Boolean(v))
}

/** 一條篇章在全藏中的位置，供搜尋與 reader 使用 */
export interface TextLocation {
  canon: ManiCanon
  volume: ManiVolume
  division: ManiDivision
  text: ManiText
}

let _index: Map<string, TextLocation> | null = null

/** slug → 位置。slug 全藏唯一；重複會在建索引時擲錯，不容默默覆蓋。
 *  （靜默覆蓋會讓兩篇共用一頁而版面完全正常——最難發現的一類錯。） */
export function textIndex(): Map<string, TextLocation> {
  if (_index) return _index
  const m = new Map<string, TextLocation>()
  for (const canon of CANONS) {
    for (const volume of canon.volumes) {
      for (const division of volume.divisions) {
        for (const text of division.texts) {
          const prev = m.get(text.slug)
          if (prev) {
            throw new Error(
              `摩尼教經典 slug 重複：'${text.slug}' 同時出現於 `
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

/** 存世狀態統計。摩尼教這一藏的重點數字：有多少是「只剩書名」。 */
export function tallyStatus(locs: TextLocation[] = allTexts()): Record<string, number> {
  const t: Record<string, number> = {}
  for (const { text } of locs) {
    const s = text.status ?? 'fragment'
    t[s] = (t[s] ?? 0) + 1
  }
  return t
}

/** 搜尋：比對中文名、原文名、英文名、編號、作者與出土地 */
export function searchTexts(q: string): TextLocation[] {
  const s = q.trim().toLowerCase()
  if (!s) return []
  return allTexts().filter(({ text, volume, canon }) =>
    [text.title_zh, text.title_orig, text.title_en, text.siglum, text.author, text.note, text.provenance, volume.name, canon.name]
      .some(v => v?.toLowerCase().includes(s)),
  )
}

/** 互見：把 seealso 的 slug 解成位置。查不到的 slug 直接略過（不擲錯，
 *  因為 seealso 可以指向尚未建立的條目——那是待辦，不是錯誤）。 */
export function relatedOf(text: ManiText): TextLocation[] {
  return (text.seealso ?? [])
    .map(s => findText(s))
    .filter((l): l is TextLocation => Boolean(l))
}
