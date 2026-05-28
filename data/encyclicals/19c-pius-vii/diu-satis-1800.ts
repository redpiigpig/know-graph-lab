import type { PapalDocument } from '../types'

export const diuSatis1800: PapalDocument = {
  slug: 'diu-satis-1800',
  popeSlug: 'pius-vii',
  category: 'encyclical',
  titleLat: 'Diu Satis',
  titleEn: '[English] On a Return to Gospel Principles',
  titleZh: '《Diu Satis》',
  promulgationDate: '1800-05-15',
  century: 19,
  summaryZh: '教宗碧岳七世於 1800-05-15 頒布的通諭（Diu Satis, [English] On a Return to Gospel Principles）。',
  topics: [],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'diu-satis-1800-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (papalencyclicals.net)',
      textKey: 'diu-satis-1800-english',
      source: 'https://www.papalencyclicals.net/pius07/p7diusat.htm',
    },
    {
      lang: 'lat',
      label: '拉丁原文（待補）',
      textKey: 'diu-satis-1800-latin',
      placeholder: true,
    },
  ],
  displayMode: 'paragraph-aligned',
}
