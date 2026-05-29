import type { PapalDocument } from '../types'

export const amantissimus1862: PapalDocument = {
  slug: 'amantissimus-1862',
  popeSlug: 'pius-ix',
  category: 'encyclical',
  titleLat: 'Amantissimus',
  titleEn: 'On the Care of the Churches',
  titleZh: '《Amantissimus》',
  promulgationDate: '1862-04-08',
  century: 19,
  summaryZh: '教宗碧岳九世於 1862-04-08 頒布的通諭（Amantissimus, On the Care of the Churches）。',
  topics: [],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'amantissimus-1862-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (papalencyclicals.net)',
      textKey: 'amantissimus-1862-english',
      source: 'https://www.papalencyclicals.net/pius09/p9amant2.htm',
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org / Pius IX — Amantissimus humani generis)',
      textKey: 'amantissimus-1862-latin',
      source: 'https://la.wikisource.org/wiki/Amantissimus_humani_generis',
    },
  ],
  displayMode: 'paragraph-aligned',
}
