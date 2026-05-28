import type { PapalDocument } from '../types'

export const catechesiTradendae1979: PapalDocument = {
  slug: 'catechesi-tradendae-1979',
  popeSlug: 'john-paul-ii',
  tier: 'message',
  category: 'message',
  titleLat: 'Catechesi Tradendae',
  titleEn: '',
  titleZh: '論現時代的教理講授',
  promulgationDate: '1979-01-01',
  century: 20,
  summaryZh: 'hsscol P166 對位中譯。年份：1979。',
  topics: [],
  versions: [
    { lang: 'zh-Hant', label: '中文（聖神修院神哲學院 圖書館 文獻庫）', textKey: 'catechesi-tradendae-1979-chinese', source: 'http://archive.hsscol.org.hk/Archive/database/document/P166', translator: '韓山城／思高聖經學會／光啟出版社 等編譯（依各篇）' },
    { lang: 'lat', label: '拉丁原文（待補）', textKey: 'catechesi-tradendae-1979-latin', placeholder: true },
    { lang: 'en', label: '英文（待補）', textKey: 'catechesi-tradendae-1979-english', placeholder: true },
  ],
  displayMode: 'simple',
  notes: 'hsscol P166 中文對位，拉/英文待 vatican.va 或其他原文源回補',
}
