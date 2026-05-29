import type { PapalDocument } from '../types'

export const sermon95OnBeatitudes: PapalDocument = {
  slug: 'sermon-95-on-beatitudes',
  popeSlug: 'leo-i',
  category: 'homily',
  titleLat: 'Sermo XCV in Beatitudines (Matt. v. 1-9)',
  titleEn: 'Sermon XCV — A Homily on the Beatitudes (Matt. v. 1-9)',
  titleZh: '《真福八端講道》— 山中聖訓詮釋',
  promulgationDate: '445-02-21',
  century: 5,
  summaryZh: `教宗大良對〈瑪竇福音〉5:1-9「山中聖訓」開篇真福八端的詮釋講道。逐條展開：(1) 神貧的人有福——擁有天國；(2) 哀慟的人有福——必得安慰；(3) 溫良的人有福——必承受土地……。本講道是早期教父對真福八端最系統的釋經之一，後代天主教 ethics 經常引用。文末對 Petrine Primacy 也有附帶論述。`,
  topics: ['真福八端', '山中聖訓', '倫理神學', '瑪竇福音'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'sermon-95-on-beatitudes-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (Schaff NPNF2 Vol 12)',
      textKey: 'sermon-95-on-beatitudes-english',
      source: 'CCEL — Schaff NPNF2 Vol 12 (Leo the Great)',
    },
    {
      lang: 'lat',
      label: '拉丁原文 (Migne PL 54 — Gemini Vision OCR)',
      textKey: 'sermon-95-on-beatitudes-latin',
      source: 'https://archive.org/details/sanctileonismagn01leoi',

    },
  ],
  displayMode: 'paragraph-aligned',
}
