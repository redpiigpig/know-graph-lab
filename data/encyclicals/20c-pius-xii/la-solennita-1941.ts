import type { PapalDocument } from '../types'

export const laSolennita1941: PapalDocument = {
  slug: 'la-solennita-1941',
  popeSlug: 'pius-xii',
  tier: 'message',
  category: 'message',
  titleLat: 'La Solennita',
  titleEn: '',
  titleZh: '五旬節',
  promulgationDate: '1941-01-01',
  century: 20,
  summaryZh: 'hsscol P099 對位中譯。年份：1941。',
  topics: [],
  versions: [
    { lang: 'zh-Hant', label: '中文（聖神修院神哲學院 圖書館 文獻庫）', textKey: 'la-solennita-1941-chinese', source: 'http://archive.hsscol.org.hk/Archive/database/document/P099', translator: '韓山城／思高聖經學會／光啟出版社 等編譯（依各篇）' },
    { lang: 'lat', label: '拉丁原文（待補）', textKey: 'la-solennita-1941-latin', placeholder: true },
    { lang: 'en', label: '英文（待補）', textKey: 'la-solennita-1941-english', placeholder: true },
  ],
  displayMode: 'simple',
  notes: 'hsscol P099 中文對位，拉/英文待 vatican.va 或其他原文源回補',
}
