import type { PapalDocument } from '../types'

export const gravibusEcclesiae1874: PapalDocument = {
  slug: 'gravibus-ecclesiae-1874',
  popeSlug: 'pius-ix',
  category: 'encyclical',
  titleLat: 'Gravibus Ecclesiae',
  titleEn: 'Proclaiming A Jubilee',
  titleZh: '《Gravibus Ecclesiae》',
  promulgationDate: '1874-12-24',
  century: 19,
  summaryZh: '教宗碧岳九世於 1874-12-24 頒布的通諭（Gravibus Ecclesiae, Proclaiming A Jubilee）。',
  topics: [],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'gravibus-ecclesiae-1874-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (papalencyclicals.net)',
      textKey: 'gravibus-ecclesiae-1874-english',
      source: 'https://www.papalencyclicals.net/pius09/p9gravib.htm',
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org)',
      textKey: 'gravibus-ecclesiae-1874-latin',
      source: 'https://la.wikisource.org/wiki/Gravibus_Ecclesiae',

    },
  ],
  displayMode: 'paragraph-aligned',
}
