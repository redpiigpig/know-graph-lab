import type { PapalDocument } from '../types'

export const quoPrimum1570: PapalDocument = {
  slug: 'quo-primum-1570',
  popeSlug: 'pius-v',
  category: 'bull',
  titleLat: 'Quo Primum',
  titleEn: 'Promulgating the Tridentine Liturgy',
  titleZh: '《Quo Primum》',
  promulgationDate: '1570-07-14',
  century: 16,
  summaryZh: '教宗碧岳五世於 1570-07-14 頒布的詔書（Quo Primum, Promulgating the Tridentine Liturgy）。',
  topics: [],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'quo-primum-1570-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (papalencyclicals.net)',
      textKey: 'quo-primum-1570-english',
      source: 'https://www.papalencyclicals.net/pius05/p5quopri.htm',
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org)',
      textKey: 'quo-primum-1570-latin',
      source: 'https://la.wikisource.org/wiki/Quo_Primum',

    },
  ],
  displayMode: 'simple',
}
