import type { PapalDocument } from '../types'

export const patrisCorde2020Alt: PapalDocument = {
  slug: 'patris-corde-2020-alt',
  popeSlug: 'francis',
  tier: 'teaching',
  category: 'apostolic-letter',
  titleLat: 'Patris Corde',
  titleEn: 'Patris Corde (apostolic letter variant)',
  titleZh: '宗座牧函 以父親的心',
  promulgationDate: '2020-01-01',
  century: 21,
  summaryZh: 'hsscol P484 對位中譯。年份：1955。',
  topics: [],
  versions: [
    { lang: 'zh-Hant', label: '中文（聖神修院神哲學院 圖書館 文獻庫）', textKey: 'patris-corde-2020-alt-chinese', source: 'http://archive.hsscol.org.hk/Archive/database/document/P484', translator: '韓山城／思高聖經學會／光啟出版社 等編譯（依各篇）' },
    { lang: 'lat', label: '拉丁原文（待補）', textKey: 'patris-corde-2020-alt-latin', placeholder: true },
    { lang: 'en', label: '英文（待補）', textKey: 'patris-corde-2020-alt-english', placeholder: true },
  ],
  displayMode: 'simple',
  notes: 'hsscol P484 中文對位，拉/英文待 vatican.va 或其他原文源回補',
}
