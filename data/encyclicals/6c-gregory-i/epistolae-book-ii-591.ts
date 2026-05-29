import type { PapalDocument } from '../types'

export const epistolaeBookIi591: PapalDocument = {
  slug: 'epistolae-book-ii-591',
  popeSlug: 'gregory-i',
  category: 'epistola',
  titleLat: 'Registrum Epistolarum, Liber II',
  titleEn: 'Register of Epistles — Book II (Year 2)',
  titleZh: '《書信錄》第二冊 — 591 年（即位第二年）',
  promulgationDate: '591-09-01',
  century: 6,
  summaryZh: `《書信錄》第二冊，591 年 9 月至 592 年 8 月。重點：與 Lombard 王 Agilulf 的初次和談、致 Velox（軍事長官）論 Naples 防禦、對 Sardinia 教區的整頓、Constantinople 牧首 John IV 的「Ecumenical Patriarch」頭銜爭論首露端倪。`,
  topics: ['書信錄', 'Lombard 和談', 'Ecumenical Patriarch 爭論'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'epistolae-book-ii-591-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (Schaff NPNF2 Vol 12)',
      textKey: 'epistolae-book-ii-591-english',
      source: 'CCEL — Schaff NPNF2 Vol 12 (Gregory the Great)',
    },
    {
      lang: 'lat',
      label: '拉丁原文（待補）',
      textKey: 'epistolae-book-ii-591-latin',
      placeholder: true,
    },
  ],
  displayMode: 'paragraph-aligned',
}
