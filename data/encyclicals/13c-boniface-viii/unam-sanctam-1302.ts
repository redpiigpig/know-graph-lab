import type { PapalDocument } from '../types'

export const unamSanctam1302: PapalDocument = {
  slug: 'unam-sanctam-1302',
  popeSlug: 'boniface-viii',
  category: 'bull',
  titleLat: 'Unam Sanctam',
  titleEn: 'One God, One Faith, One Spiritual Authority',
  titleZh: '《Unam Sanctam》',
  promulgationDate: '1302-11-18',
  century: 13,
  summaryZh: '教宗鮑尼法八世於 1302-11-18 頒布的詔書（Unam Sanctam, One God, One Faith, One Spiritual Authority）。',
  topics: [],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'unam-sanctam-1302-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (papalencyclicals.net)',
      textKey: 'unam-sanctam-1302-english',
      source: 'https://www.papalencyclicals.net/bon08/b8unam.htm',
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org / Boniface VIII — Unam sanctam)',
      textKey: 'unam-sanctam-1302-latin',
      source: 'https://la.wikisource.org/wiki/Unam_sanctam',
    },
  ],
  displayMode: 'simple',
}
