import type { PapalDocument } from '../types'

export const apostolicaeNostraeCaritatis1854: PapalDocument = {
  slug: 'apostolicae-nostrae-caritatis-1854',
  popeSlug: 'pius-ix',
  category: 'encyclical',
  titleLat: 'Apostolicae Nostrae Caritatis',
  titleEn: 'Urging Prayers of Peace',
  titleZh: '《Apostolicae Nostrae Caritatis》',
  promulgationDate: '1854-08-01',
  century: 19,
  summaryZh: '教宗碧岳九世於 1854-08-01 頒布的通諭（Apostolicae Nostrae Caritatis, Urging Prayers of Peace）。',
  topics: [],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'apostolicae-nostrae-caritatis-1854-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (papalencyclicals.net)',
      textKey: 'apostolicae-nostrae-caritatis-1854-english',
      source: 'https://www.papalencyclicals.net/pius09/p9aposto.htm',
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org / Pius IX — Apostolicae Nostrae)',
      textKey: 'apostolicae-nostrae-caritatis-1854-latin',
      source: 'https://la.wikisource.org/wiki/Apostolicae_Nostrae',
    },
  ],
  displayMode: 'paragraph-aligned',
}
