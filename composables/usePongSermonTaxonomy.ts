// Shared taxonomy helpers for 龐君華 sermons (location category + type order).
// Use from any /pong-archive/sermons/* page so the two browse axes stay in
// sync with whatever the DB and the backfill script chose.

const LOCATION_RULES: { name: string; match: (loc: string) => boolean }[] = [
  // 衛理 internal — specific church names
  { name: '衛理公會城中教會',   match: l => /城中/.test(l) },
  { name: '台北衛理堂',         match: l => l === '台北衛理堂' || /台北衛理堂/.test(l) },
  { name: '衛理公會雅各堂',     match: l => /雅各堂/.test(l) },
  { name: '陽明山衛理福音園',   match: l => /福音園/.test(l) },
  { name: '衛理神學研究院',     match: l => /衛理神學/.test(l) },
  // External denominations — bucket together
  { name: '天主教堂',           match: l => /天主教/.test(l) },
  { name: '信義會教堂',         match: l => /信義會/.test(l) },
  { name: '聖公會教堂',         match: l => /聖公會/.test(l) },
  { name: '長老教會教堂',       match: l => /長老/.test(l) },
  // Misc
  { name: '線上崇拜',           match: l => /Zoom|線上|視訊/i.test(l) },
]

export function locationCategory(loc: string | null | undefined): string {
  if (!loc) return '未分類'
  for (const r of LOCATION_RULES) {
    if (r.match(loc)) return r.name
  }
  return loc
}

// Display order for sermon_type tabs/cards
export const SERMON_TYPE_ORDER = [
  '主日講道',
  '特殊節日',
  '年議會禮拜',
  '堂慶與或聯合禮拜',
  '特殊禮拜',
] as const

export type SermonType = typeof SERMON_TYPE_ORDER[number]

// Always-show location categories, in display order. The first 4 are 衛理
// internal locations the user wants surfaced even with 0 sermons (e.g. 陽明山
// 福音園 has no entries yet but will). External categories show up only when
// they have data — see `mergeLocationGroups` in by/location/index.vue.
export const CANONICAL_LOCATIONS = [
  '台北衛理堂',
  '衛理公會城中教會',
  '衛理公會雅各堂',
  '陽明山衛理福音園',
] as const
