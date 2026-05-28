import type { PapalDocument } from '../types'

export const exCordeEcclesiae1990: PapalDocument = {
  slug: 'ex-corde-ecclesiae-1990',
  popeSlug: 'john-paul-ii',
  tier: 'teaching',
  category: 'apostolic-const',
  titleLat: 'Ex Corde Ecclesiae',
  titleEn: 'On Catholic Universities',
  titleZh: '天主教大學憲章',
  promulgationDate: '1990-01-01',
  century: 20,
  summaryZh: 'hsscol P252 對位中譯。年份：1998。',
  topics: [],
  versions: [
    { lang: 'zh-Hant', label: '中文（聖神修院神哲學院 圖書館 文獻庫）', textKey: 'ex-corde-ecclesiae-1990-chinese', source: 'http://archive.hsscol.org.hk/Archive/database/document/P252', translator: '韓山城／思高聖經學會／光啟出版社 等編譯（依各篇）' },
    { lang: 'lat', label: '拉丁原文（待補）', textKey: 'ex-corde-ecclesiae-1990-latin', placeholder: true },
    { lang: 'en', label: '英文（待補）', textKey: 'ex-corde-ecclesiae-1990-english', placeholder: true },
  ],
  displayMode: 'simple',
  notes: 'hsscol P252 中文對位，拉/英文待 vatican.va 或其他原文源回補',
}
