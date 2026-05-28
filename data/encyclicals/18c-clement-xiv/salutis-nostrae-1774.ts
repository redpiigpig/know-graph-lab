import type { PapalDocument } from '../types'

export const salutisNostrae1774: PapalDocument = {
  slug: 'salutis-nostrae-1774',
  popeSlug: 'clement-xiv',
  category: 'encyclical',
  titleLat: 'Salutis Nostrae',
  titleEn: 'Proclaiming a Universal Jubilee',
  titleZh: '《Salutis Nostrae》',
  promulgationDate: '1774-04-30',
  century: 18,
  summaryZh: '教宗克勉十四世於 1774-04-30 頒布的通諭（Salutis Nostrae, Proclaiming a Universal Jubilee）。',
  topics: [],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'salutis-nostrae-1774-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (papalencyclicals.net)',
      textKey: 'salutis-nostrae-1774-english',
      source: 'https://www.papalencyclicals.net/clem14/c14salut.htm',
    },
    {
      lang: 'lat',
      label: '拉丁原文（待補）',
      textKey: 'salutis-nostrae-1774-latin',
      placeholder: true,
    },
  ],
  displayMode: 'paragraph-aligned',
}
