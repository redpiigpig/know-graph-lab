import type { PapalDocument } from '../types'

export const quiPluribus1846: PapalDocument = {
  slug: 'qui-pluribus-1846',
  popeSlug: 'pius-ix',
  category: 'encyclical',
  titleLat: 'Qui Pluribus',
  titleEn: 'On Faith and Religion',
  titleZh: '《Qui Pluribus》',
  promulgationDate: '1846-11-09',
  century: 19,
  summaryZh: '教宗碧岳九世於 1846-11-09 頒布的通諭（Qui Pluribus, On Faith and Religion）。',
  topics: [],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'qui-pluribus-1846-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (papalencyclicals.net)',
      textKey: 'qui-pluribus-1846-english',
      source: 'https://www.papalencyclicals.net/pius09/p9quiplu.htm',
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org)',
      textKey: 'qui-pluribus-1846-latin',
      source: 'https://la.wikisource.org/wiki/Qui_pluribus',

    },
  ],
  displayMode: 'paragraph-aligned',
}
