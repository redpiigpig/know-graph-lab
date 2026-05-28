import type { PapalDocument } from '../types'

export const quodApostoliciMuneris1878: PapalDocument = {
  slug: 'quod-apostolici-muneris-1878',
  popeSlug: 'leo-xiii',
  category: 'encyclical',
  titleLat: 'Quod Apostolici Muneris',
  titleEn: 'On Socialism',
  titleZh: '《使徒職務》通諭 — 論社會主義',
  promulgationDate: '1878-12-28',
  century: 19,
  summaryZh: `教宗良十三世首道通諭，反對 19 世紀中後期歐洲新興的社會主義、共產主義、虛無主義（nihilism）。確立天主教社會教義的基本反共產主義立場——擁護財產私有、家庭結構、神授王權，譴責「妻子共有」「無家庭」等社會主義口號。是 1891 *Rerum Novarum* 的前奏：先撇清 vs. 社會主義，再積極推出第三條路。`,
  topics: ['社會主義', '共產主義', '私有財產', '家庭'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'quod-apostolici-muneris-1878-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (papalencyclicals.net)',
      textKey: 'quod-apostolici-muneris-1878-english',
      source: 'https://www.papalencyclicals.net/leo13/l13apost.htm',
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org)',
      textKey: 'quod-apostolici-muneris-1878-latin',
      source: 'https://la.wikisource.org/wiki/Quod_Apostolici_Muneris',
    },
  ],
  displayMode: 'paragraph-aligned',
}
