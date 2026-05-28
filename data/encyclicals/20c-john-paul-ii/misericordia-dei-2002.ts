import type { PapalDocument } from '../types'

export const misericordiaDei2002: PapalDocument = {
  slug: 'misericordia-dei-2002',
  popeSlug: 'john-paul-ii',
  tier: 'teaching',
  category: 'motu-proprio',
  titleLat: 'Misericordia Dei',
  titleEn: 'On Some Aspects of the Sacrament of Penance',
  titleZh: '論天主仁慈自動諭',
  promulgationDate: '2002-01-01',
  century: 21,
  summaryZh: 'hsscol P214 對位中譯。年份：1984。',
  topics: [],
  versions: [
    { lang: 'zh-Hant', label: '中文（聖神修院神哲學院 圖書館 文獻庫）', textKey: 'misericordia-dei-2002-chinese', source: 'http://archive.hsscol.org.hk/Archive/database/document/P214', translator: '韓山城／思高聖經學會／光啟出版社 等編譯（依各篇）' },
    { lang: 'lat', label: '拉丁原文（待補）', textKey: 'misericordia-dei-2002-latin', placeholder: true },
    { lang: 'en', label: '英文（待補）', textKey: 'misericordia-dei-2002-english', placeholder: true },
  ],
  displayMode: 'simple',
  notes: 'hsscol P214 中文對位，拉/英文待 vatican.va 或其他原文源回補',
}
