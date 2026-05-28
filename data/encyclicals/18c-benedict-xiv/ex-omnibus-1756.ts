import type { PapalDocument } from '../types'

export const exOmnibus1756: PapalDocument = {
  slug: 'ex-omnibus-1756',
  popeSlug: 'benedict-xiv',
  category: 'apostolic-const',
  titleLat: 'Ex Omnibus',
  titleEn: 'On the Apostolic Constitution Unigenitus',
  titleZh: '《Ex Omnibus》',
  promulgationDate: '1756-10-16',
  century: 18,
  summaryZh: '教宗本篤十四世於 1756-10-16 頒布的使徒憲令（Ex Omnibus, On the Apostolic Constitution Unigenitus）。',
  topics: [],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'ex-omnibus-1756-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (papalencyclicals.net)',
      textKey: 'ex-omnibus-1756-english',
      source: 'https://www.papalencyclicals.net/ben14/b14exomn.htm',
    },
    {
      lang: 'lat',
      label: '拉丁原文（待補）',
      textKey: 'ex-omnibus-1756-latin',
      placeholder: true,
    },
  ],
  displayMode: 'paragraph-aligned',
}
