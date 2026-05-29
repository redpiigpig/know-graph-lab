import type { PapalDocument } from '../types'

export const etsiMulta1873: PapalDocument = {
  slug: 'etsi-multa-1873',
  popeSlug: 'pius-ix',
  category: 'encyclical',
  titleLat: 'Etsi Multa',
  titleEn: 'On the Church in Italy, Germany and Switzerland',
  titleZh: '《Etsi Multa》',
  promulgationDate: '1873-11-21',
  century: 19,
  summaryZh: '教宗碧岳九世於 1873-11-21 頒布的通諭（Etsi Multa, On the Church in Italy, Germany and Switzerland）。',
  topics: [],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'etsi-multa-1873-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (papalencyclicals.net)',
      textKey: 'etsi-multa-1873-english',
      source: 'https://www.papalencyclicals.net/pius09/p9etsimu.htm',
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org / Pius IX — Etsi multa luctuosa)',
      textKey: 'etsi-multa-1873-latin',
      source: 'https://la.wikisource.org/wiki/Etsi_multa_luctuosa',
    },
  ],
  displayMode: 'paragraph-aligned',
}
