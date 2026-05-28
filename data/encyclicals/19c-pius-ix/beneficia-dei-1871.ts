import type { PapalDocument } from '../types'

export const beneficiaDei1871: PapalDocument = {
  slug: 'beneficia-dei-1871',
  popeSlug: 'pius-ix',
  category: 'encyclical',
  titleLat: 'Beneficia Dei',
  titleEn: 'On the 25th Anniversary of His Pontificate',
  titleZh: '《Beneficia Dei》',
  promulgationDate: '1871-06-04',
  century: 19,
  summaryZh: '教宗碧岳九世於 1871-06-04 頒布的通諭（Beneficia Dei, On the 25th Anniversary of His Pontificate）。',
  topics: [],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'beneficia-dei-1871-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (papalencyclicals.net)',
      textKey: 'beneficia-dei-1871-english',
      source: 'https://www.papalencyclicals.net/pius09/p9benefi.htm',
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org)',
      textKey: 'beneficia-dei-1871-latin',
      source: 'https://la.wikisource.org/wiki/Beneficia_Dei',

    },
  ],
  displayMode: 'paragraph-aligned',
}
