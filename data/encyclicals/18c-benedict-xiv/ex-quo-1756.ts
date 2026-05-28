import type { PapalDocument } from '../types'

export const exQuo1756: PapalDocument = {
  slug: 'ex-quo-1756',
  popeSlug: 'benedict-xiv',
  category: 'encyclical',
  titleLat: 'Ex Quo',
  titleEn: 'On the Euchologion',
  titleZh: '《Ex Quo》',
  promulgationDate: '1756-03-01',
  century: 18,
  summaryZh: '教宗本篤十四世於 1756-03-01 頒布的通諭（Ex Quo, On the Euchologion）。',
  topics: [],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'ex-quo-1756-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (papalencyclicals.net)',
      textKey: 'ex-quo-1756-english',
      source: 'https://www.papalencyclicals.net/ben14/b14exquo.htm',
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org)',
      textKey: 'ex-quo-1756-latin',
      source: 'https://la.wikisource.org/wiki/Ex_quo',

    },
  ],
  displayMode: 'paragraph-aligned',
}
