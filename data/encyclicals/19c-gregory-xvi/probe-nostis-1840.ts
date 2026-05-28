import type { PapalDocument } from '../types'

export const probeNostis1840: PapalDocument = {
  slug: 'probe-nostis-1840',
  popeSlug: 'gregory-xvi',
  category: 'encyclical',
  titleLat: 'Probe Nostis',
  titleEn: 'On the Propogation of the Faith',
  titleZh: '《Probe Nostis》',
  promulgationDate: '1840-09-18',
  century: 19,
  summaryZh: '教宗額我略十六世於 1840-09-18 頒布的通諭（Probe Nostis, On the Propogation of the Faith）。',
  topics: [],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'probe-nostis-1840-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (papalencyclicals.net)',
      textKey: 'probe-nostis-1840-english',
      source: 'https://www.papalencyclicals.net/greg16/g16probe.htm',
    },
    {
      lang: 'lat',
      label: '拉丁原文（待補）',
      textKey: 'probe-nostis-1840-latin',
      placeholder: true,
    },
  ],
  displayMode: 'paragraph-aligned',
}
