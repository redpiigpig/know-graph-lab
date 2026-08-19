import type { HellenCanon, HellenVolume, HellenWork } from './types'
import { GREEK_CANON } from './greek'
import { ROMAN_CANON } from './roman'
import INTROS from './intros.json'

export * from './types'
export { GREEK_CANON } from './greek'
export { ROMAN_CANON } from './roman'

/** 兩藏：希臘廿四卷（正藏）、羅馬六卷（續典） */
export const CANONS: HellenCanon[] = [GREEK_CANON, ROMAN_CANON]

// 條目簡介以 intros.json 覆蓋層維護（鍵＝canon:volume:division:index），
// 由 scripts/hellenika_intro.py 逐卷補寫，載入時掛回 work 物件。
// 這樣批次策展不必改寫 greek.ts / roman.ts 的物件字面量，diff 也乾淨。
// 已直接寫在 .ts 裡的 intro 優先，不被覆蓋層蓋掉。
for (const canon of CANONS) {
  for (const volume of canon.volumes) {
    for (const division of volume.divisions) {
      division.works.forEach((work, i) => {
        if (work.intro) return
        const text = (INTROS as Record<string, string>)[`${canon.key}:${volume.key}:${division.key}:${i}`]
        if (text) work.intro = text
      })
    }
  }
}

/** 全書斷限 */
export const TERMINUS = {
  from: '約公元前 8 世紀',
  to: '公元 529 年',
  note: '東邊查士丁尼關閉雅典學園、達馬斯基烏斯等七哲東走波斯；西邊本篤在卡西諾山砸毀阿波羅像、伐倒聖林、就地建院。兩端同年合攏。',
}

export function findCanon(key: string): HellenCanon | undefined {
  return CANONS.find(c => c.key === key)
}

export function findVolume(canonKey: string, volumeKey: string): HellenVolume | undefined {
  return findCanon(canonKey)?.volumes.find(v => v.key === volumeKey)
}

/** 依卷序取前／後一卷，供卷詳頁翻頁 */
export function neighbours(canonKey: string, volumeKey: string): { prev?: HellenVolume; next?: HellenVolume } {
  const c = findCanon(canonKey)
  if (!c) return {}
  const i = c.volumes.findIndex(v => v.key === volumeKey)
  if (i < 0) return {}
  return { prev: c.volumes[i - 1], next: c.volumes[i + 1] }
}

export interface WorkHit {
  work: HellenWork
  canon: HellenCanon
  volume: HellenVolume
  divisionLabel: string
}

/** 全書書目攤平，供搜尋與統計 */
export function allWorks(): WorkHit[] {
  const out: WorkHit[] = []
  for (const canon of CANONS) {
    for (const volume of canon.volumes) {
      for (const d of volume.divisions) {
        for (const work of d.works) out.push({ work, canon, volume, divisionLabel: d.label })
      }
    }
  }
  return out
}

export function searchWorks(q: string): WorkHit[] {
  const k = q.trim().toLowerCase()
  if (!k) return []
  return allWorks().filter(({ work, volume }) =>
    [work.title_zh, work.title_orig, work.author, work.note, work.intro, work.era, work.place, work.parent, volume.name]
      .some(f => f?.toLowerCase().includes(k)),
  )
}
