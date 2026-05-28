import type { PapalDocument } from '../types'

export const theHolySee2008: PapalDocument = {
  slug: 'the-holy-see-2008',
  popeSlug: 'francis',
  tier: 'teaching',
  category: 'apostolic-letter',
  titleLat: 'The Holy See',
  titleEn: '',
  titleZh: '教宗方濟各宗座牧函',
  promulgationDate: '2008-01-01',
  century: 21,
  summaryZh: 'hsscol P426 對位中譯。年份：2008。',
  topics: [],
  versions: [
    { lang: 'zh-Hant', label: '中文（聖神修院神哲學院 圖書館 文獻庫）', textKey: 'the-holy-see-2008-chinese', source: 'http://archive.hsscol.org.hk/Archive/database/document/P426', translator: '韓山城／思高聖經學會／光啟出版社 等編譯（依各篇）' },
    { lang: 'lat', label: '拉丁原文（待補）', textKey: 'the-holy-see-2008-latin', placeholder: true },
    { lang: 'en', label: '英文（待補）', textKey: 'the-holy-see-2008-english', placeholder: true },
  ],
  displayMode: 'simple',
  notes: 'hsscol P426 中文對位，拉/英文待 vatican.va 或其他原文源回補',
}
