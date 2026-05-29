import type { PapalDocument } from '../types'

export const epistolaeBookI590: PapalDocument = {
  slug: 'epistolae-book-i-590',
  popeSlug: 'gregory-i',
  category: 'epistola',
  titleLat: 'Registrum Epistolarum, Liber I',
  titleEn: 'Register of Epistles — Book I (Sept 590 — Year 1 of Ordination)',
  titleZh: '《書信錄》第一冊 — 590 年九月（即位首年）',
  promulgationDate: '590-09-01',
  century: 6,
  summaryZh: `教宗額我略一世《Registrum Epistolarum（書信錄）》第一冊，收錄 590 年 9 月至 591 年 8 月（即位首個 indiction 年）的全部書信。內容涵蓋對義大利各教區管理、與東方諸 Patriarch 的通訊、對 Lombard 入侵的應對、對 Sicily 莊園的管理（教廷 Patrimony Petri）、初步的傳教計劃。是 6 世紀西歐政治—宗教情勢最完整的第一手史料之一。Schaff Vol 12 編輯精選版。`,
  topics: ['書信錄', 'Registrum', '教廷管理', 'Lombard 入侵'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'epistolae-book-i-590-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (Schaff NPNF2 Vol 12)',
      textKey: 'epistolae-book-i-590-english',
      source: 'CCEL — Schaff NPNF2 Vol 12 (Gregory the Great)',
    },
    {
      lang: 'lat',
      label: '拉丁原文（待補）',
      textKey: 'epistolae-book-i-590-latin',
      placeholder: true,
    },
  ],
  displayMode: 'paragraph-aligned',
}
