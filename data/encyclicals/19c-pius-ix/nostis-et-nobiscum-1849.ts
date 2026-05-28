import type { PapalDocument } from '../types'

export const nostisEtNobiscum1849: PapalDocument = {
  slug: 'nostis-et-nobiscum-1849',
  popeSlug: 'pius-ix',
  category: 'encyclical',
  titleLat: 'Nostis Et Nobiscum',
  titleEn: 'On the Church in the Pontifical States',
  titleZh: '《Nostis Et Nobiscum》',
  promulgationDate: '1849-12-08',
  century: 19,
  summaryZh: '教宗碧岳九世於 1849-12-08 頒布的通諭（Nostis Et Nobiscum, On the Church in the Pontifical States）。',
  topics: [],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'nostis-et-nobiscum-1849-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (papalencyclicals.net)',
      textKey: 'nostis-et-nobiscum-1849-english',
      source: 'https://www.papalencyclicals.net/pius09/p9nostis.htm',
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org)',
      textKey: 'nostis-et-nobiscum-1849-latin',
      source: 'https://la.wikisource.org/wiki/Nostis_et_nobiscum',

    },
  ],
  displayMode: 'paragraph-aligned',
}
