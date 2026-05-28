import type { PapalDocument } from '../types'

export const aeterniPatrisFilius1621: PapalDocument = {
  slug: 'aeterni-patris-filius-1621',
  popeSlug: 'gregory-xv',
  category: 'bull',
  titleLat: 'Aeterni Patris Filius',
  titleEn: 'Reform of Papal Conclave',
  titleZh: '《永生父之子》詔書 — 教宗選舉改革',
  promulgationDate: '1621-11-15',
  century: 17,
  summaryZh: `教宗額我略十五世 1621 年頒布的詔書，全面改革教宗選舉程序：規定樞機團必須以秘密投票（scrutinium）為唯一合法方式，禁止公開唱票（accessus per viva voce），並要求三分之二多數方為當選。此 procedure 沿用至今，是現代教宗選舉制度的奠基文件。`,
  topics: ['教宗選舉', '樞機團', 'Conclave 改革'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'aeterni-patris-filius-1621-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文（待補）',
      textKey: 'aeterni-patris-filius-1621-english',
      placeholder: true,
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org)',
      textKey: 'aeterni-patris-filius-1621-latin',
      source: 'https://la.wikisource.org/wiki/Aeterni_Patris_Filius',
    },
  ],
  displayMode: 'paragraph-aligned',
}
