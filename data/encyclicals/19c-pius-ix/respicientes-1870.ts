import type { PapalDocument } from '../types'

export const respicientes1870: PapalDocument = {
  slug: 'respicientes-1870',
  popeSlug: 'pius-ix',
  category: 'encyclical',
  titleLat: 'Respicientes',
  titleEn: 'Protesting the Taking of the Pontifical States',
  titleZh: '《Respicientes》',
  promulgationDate: '1870-11-01',
  century: 19,
  summaryZh: '教宗碧岳九世於 1870-11-01 頒布的通諭（Respicientes, Protesting the Taking of the Pontifical States）。',
  topics: [],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'respicientes-1870-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (papalencyclicals.net)',
      textKey: 'respicientes-1870-english',
      source: 'https://www.papalencyclicals.net/pius09/p9respic.htm',
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org / Pius IX — Respicientes ea)',
      textKey: 'respicientes-1870-latin',
      source: 'https://la.wikisource.org/wiki/Respicientes_ea',
    },
  ],
  displayMode: 'paragraph-aligned',
}
