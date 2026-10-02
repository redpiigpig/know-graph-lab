import type { ColumnStatus, NeCanon, NeDivision, NeText, NeVolume } from './types'
import { EGYPT_CANON } from './egypt'
import { SUMER_CANON } from './sumer'
import { AKKAD_CANON } from './akkad'
import { ANATOLIA_CANON } from './anatolia'
import { UGARIT_CANON } from './ugarit'
import { LEVANT_CANON } from './levant'
import { ARABIA_CANON } from './arabia'
import { HIGHLANDS_CANON } from './highlands'
import { TESTIMONIA_CANON } from './testimonia'
import { MANIFEST } from './sources'

export * from './types'

/** 八藏＋附錄。順序＝文字出現的早晚（埃及與蘇美並為最古），附錄殿後。 */
export const CANONS: NeCanon[] = [
  EGYPT_CANON,
  SUMER_CANON,
  AKKAD_CANON,
  ANATOLIA_CANON,
  UGARIT_CANON,
  LEVANT_CANON,
  ARABIA_CANON,
  HIGHLANDS_CANON,
  TESTIMONIA_CANON,
]

/** 全藏斷限。🚨 沒有單一的終點：每一藏止於它自己的文字死亡（types.ts 檔頭第二條）。 */
export const TERMINUS = {
  from: '約前 2600 年（蘇美法拉期與埃及古王國的最早宗教文本）',
  to: '各藏各自終結',
  note:
    '古代宗教沒有「改宗的那一天」，只有最後一個會寫神名的書吏死去的那一天。'
    + '所以本藏經不定一個統一的下限，而讓每一藏止於它的文字最後一次被用來寫神：'
    + '烏加里特約前 1185 年城毀、赫梯約前 1180 年哈圖沙焚棄、楔形文字約公元 75–80 年最後一塊天文泥板、'
    + '帕爾米拉 273 年陷落、菲萊島 452 年最後一則世俗體塗鴉。附錄收到哈蘭月神廟 1032 年前後被毀。',
}

export function findCanon(key: string): NeCanon | undefined {
  return CANONS.find(c => c.key === key)
}

export function findVolume(canonKey: string, volumeKey: string): NeVolume | undefined {
  return findCanon(canonKey)?.volumes.find(v => v.key === volumeKey)
}

export interface TextLocation {
  canon: NeCanon
  volume: NeVolume
  division: NeDivision
  text: NeText
}

let _index: Map<string, TextLocation> | null = null

/** slug → 位置。重複直接擲錯：靜默覆蓋會讓兩篇共用一頁而版面完全正常。 */
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
              `古近東大藏經 slug 重複：'${text.slug}' 同時出現於 `
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

export function allTexts(): TextLocation[] {
  return [...textIndex().values()]
}

export interface ColumnTally {
  total: number
  orig: Record<string, number>
  en: Record<string, number>
  zh: Record<string, number>
}

/** 實際三欄現況：取源腳本寫進 manifest 的優先，否則用書目裡的預設（「可取得」之類的估計）。 */
export function effectiveColumns(text: NeText, division: NeDivision, canon: NeCanon): ColumnStatus {
  const m = MANIFEST[text.slug]
  if (m) return { orig: m.orig, en: m.en, zh: m.zh }
  return text.columns ?? division.columns ?? canon.columns
}

export function hasText(slug: string): boolean {
  return slug in MANIFEST
}

export function tallyColumns(locs: TextLocation[] = allTexts()): ColumnTally {
  const t: ColumnTally = { total: locs.length, orig: {}, en: {}, zh: {} }
  for (const { text, division, canon } of locs) {
    const c: ColumnStatus = effectiveColumns(text, division, canon)
    t.orig[c.orig] = (t.orig[c.orig] ?? 0) + 1
    t.en[c.en] = (t.en[c.en] ?? 0) + 1
    t.zh[c.zh] = (t.zh[c.zh] ?? 0) + 1
  }
  return t
}

/** 存世狀態統計。不設 status 者算綴合本——古近東大型文學作品的常態。 */
export function tallyStatus(locs: TextLocation[] = allTexts()): Record<string, number> {
  const t: Record<string, number> = {}
  for (const { text } of locs) {
    const s = text.status ?? 'composite'
    t[s] = (t[s] ?? 0) + 1
  }
  return t
}

export function searchTexts(q: string): TextLocation[] {
  const s = q.trim().toLowerCase()
  if (!s) return []
  return allTexts().filter(({ text, volume, canon }) =>
    [text.title_zh, text.title_orig, text.siglum, text.author, text.note, text.provenance, text.bible, volume.name, canon.name]
      .some(v => v?.toLowerCase().includes(s)),
  )
}

/** 互見：seealso 的 slug 解成位置。查不到的直接略過；測試另外釘住全藏不得有懸空的 slug。 */
export function relatedOf(text: NeText): TextLocation[] {
  return (text.seealso ?? [])
    .map(s => findText(s))
    .filter((l): l is TextLocation => Boolean(l))
}
