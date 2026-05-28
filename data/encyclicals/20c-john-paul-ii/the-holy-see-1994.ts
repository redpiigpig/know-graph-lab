import type { PapalDocument } from '../types'

export const theHolySee1994: PapalDocument = {
  slug: 'the-holy-see-1994',
  popeSlug: 'john-paul-ii',
  tier: 'message',
  category: 'letter-informal',
  titleLat: 'The Holy See',
  titleEn: '',
  titleZh: '致函宗座生命科學院主席，紀念該機構創立25週年',
  promulgationDate: '1994-01-01',
  century: 20,
  summaryZh: 'hsscol P431 對位中譯。年份：1994。',
  topics: [],
  versions: [
    { lang: 'zh-Hant', label: '中文（聖神修院神哲學院 圖書館 文獻庫）', textKey: 'the-holy-see-1994-chinese', source: 'http://archive.hsscol.org.hk/Archive/database/document/P431', translator: '韓山城／思高聖經學會／光啟出版社 等編譯（依各篇）' },
    { lang: 'lat', label: '拉丁原文（待補）', textKey: 'the-holy-see-1994-latin', placeholder: true },
    { lang: 'en', label: '英文（待補）', textKey: 'the-holy-see-1994-english', placeholder: true },
  ],
  displayMode: 'simple',
  notes: 'hsscol P431 中文對位，拉/英文待 vatican.va 或其他原文源回補',
}
