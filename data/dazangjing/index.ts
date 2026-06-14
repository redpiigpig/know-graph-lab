import type { DazangEra } from './types'
import { ANCIENT_ERA } from './ancient'

export * from './types'

// 四個時代：古代 → 中世紀 → 近代 → 現代
// 仿佛教《大藏經》「正藏／續藏」的切割：古代為「正藏」，中世紀以降為「續藏」。
export const ERAS: DazangEra[] = [
  ANCIENT_ERA,
  {
    key: 'medieval',
    name: '中世紀基督教大藏經',
    name_en: 'Medieval Christian Canon (800–1500)',
    glyph: '中',
    subtitle: '經院哲學‧拜占庭神學‧東方教會‧修會運動',
    boundary: '800 年（查理曼加冕）至 1500 年（宗教改革前夕）。',
    enabled: false,
    collections: [],
  },
  {
    key: 'early-modern',
    name: '近代基督教大藏經',
    name_en: 'Early Modern Christian Canon (1500–1800)',
    glyph: '近',
    subtitle: '宗教改革‧反改革‧宣教擴張‧敬虔運動',
    boundary: '1500 年（宗教改革）至 1800 年。',
    enabled: false,
    collections: [],
  },
  {
    key: 'modern',
    name: '現代基督教大藏經',
    name_en: 'Modern Christian Canon (1800–)',
    glyph: '現',
    subtitle: '自由神學‧普世合一‧第三世界神學‧漢語神學',
    boundary: '1800 年至今。',
    enabled: false,
    collections: [],
  },
]

export function findEra(key: string): DazangEra | undefined {
  return ERAS.find(e => e.key === key)
}
