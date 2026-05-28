import type { PapalDocument } from '../types'

export const diviniMagistri1929: PapalDocument = {
  slug: 'divini-magistri-1929',
  popeSlug: 'pius-xi',
  tier: 'message',
  category: 'message',
  titleLat: 'Divini Magistri',
  titleEn: '',
  titleZh: '人類導師',
  promulgationDate: '1929-01-01',
  century: 20,
  summaryZh: 'hsscol P074 對位中譯。年份：1929。',
  topics: [],
  versions: [
    { lang: 'zh-Hant', label: '中文（聖神修院神哲學院 圖書館 文獻庫）', textKey: 'divini-magistri-1929-chinese', source: 'http://archive.hsscol.org.hk/Archive/database/document/P074', translator: '韓山城／思高聖經學會／光啟出版社 等編譯（依各篇）' },
    { lang: 'lat', label: '拉丁原文（待補）', textKey: 'divini-magistri-1929-latin', placeholder: true },
    { lang: 'en', label: '英文（待補）', textKey: 'divini-magistri-1929-english', placeholder: true },
  ],
  displayMode: 'simple',
  notes: 'hsscol P074 中文對位，拉/英文待 vatican.va 或其他原文源回補',
}
