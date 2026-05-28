import type { PapalDocument } from '../types'

export const christusDominus1953: PapalDocument = {
  slug: 'christus-dominus-1953',
  popeSlug: 'pius-xii',
  tier: 'teaching',
  category: 'bull',
  titleLat: 'Christus Dominus',
  titleEn: 'On Eucharistic Fast',
  titleZh: '聖體齋',
  promulgationDate: '1953-01-01',
  century: 20,
  summaryZh: 'hsscol P135 對位中譯。年份：1952。',
  topics: [],
  versions: [
    { lang: 'zh-Hant', label: '中文（聖神修院神哲學院 圖書館 文獻庫）', textKey: 'christus-dominus-1953-chinese', source: 'http://archive.hsscol.org.hk/Archive/database/document/P135', translator: '韓山城／思高聖經學會／光啟出版社 等編譯（依各篇）' },
    { lang: 'lat', label: '拉丁原文（待補）', textKey: 'christus-dominus-1953-latin', placeholder: true },
    { lang: 'en', label: '英文（待補）', textKey: 'christus-dominus-1953-english', placeholder: true },
  ],
  displayMode: 'simple',
  notes: 'hsscol P135 中文對位，拉/英文待 vatican.va 或其他原文源回補',
}
