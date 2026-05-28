import type { PapalDocument } from '../types'

export const cupimusImprimis1952: PapalDocument = {
  slug: 'cupimus-imprimis-1952',
  popeSlug: 'pius-xii',
  tier: 'teaching',
  category: 'encyclical',
  titleLat: 'Cupimus Imprimis',
  titleEn: 'Letter to Catholics in China',
  titleZh: '教宗勗勉中國苦難教胞通諭',
  promulgationDate: '1952-01-01',
  century: 20,
  summaryZh: 'hsscol P137 對位中譯。年份：1952。',
  topics: [],
  versions: [
    { lang: 'zh-Hant', label: '中文（聖神修院神哲學院 圖書館 文獻庫）', textKey: 'cupimus-imprimis-1952-chinese', source: 'http://archive.hsscol.org.hk/Archive/database/document/P137', translator: '韓山城／思高聖經學會／光啟出版社 等編譯（依各篇）' },
    { lang: 'lat', label: '拉丁原文（待補）', textKey: 'cupimus-imprimis-1952-latin', placeholder: true },
    { lang: 'en', label: '英文（待補）', textKey: 'cupimus-imprimis-1952-english', placeholder: true },
  ],
  displayMode: 'simple',
  notes: 'hsscol P137 中文對位，拉/英文待 vatican.va 或其他原文源回補',
}
