import type { PapalDocument } from '../types'

export const ubiPrimum1849: PapalDocument = {
  slug: 'ubi-primum-1849',
  popeSlug: 'pius-ix',
  category: 'encyclical',
  titleLat: 'Ubi Primum',
  titleEn: 'On the Immaculate Conception',
  titleZh: '《Ubi Primum》',
  promulgationDate: '1849-02-02',
  century: 19,
  summaryZh: '教宗碧岳九世於 1849-02-02 頒布的通諭（Ubi Primum, On the Immaculate Conception）。',
  topics: [],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'ubi-primum-1849-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (papalencyclicals.net)',
      textKey: 'ubi-primum-1849-english',
      source: 'https://www.papalencyclicals.net/pius09/p9ubipr2.htm',
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org / Pius IX — Ubi primum 1849)',
      textKey: 'ubi-primum-1849-latin',
      source: 'https://la.wikisource.org/wiki/Ubi_primum_(Pius_IX_1849)',
    },
  ],
  displayMode: 'paragraph-aligned',
}
