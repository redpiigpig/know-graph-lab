import type { PapalDocument } from '../types'

export const epistolaeBookVii596: PapalDocument = {
  slug: 'epistolae-book-vii-596',
  popeSlug: 'gregory-i',
  category: 'epistola',
  titleLat: 'Registrum Epistolarum, Liber VII',
  titleEn: 'Register of Epistles — Book VII (Year 7)',
  titleZh: '《書信錄》第七冊 — 596 年',
  promulgationDate: '596-09-01',
  century: 6,
  summaryZh: `《書信錄》第七冊，596 年 9 月至 597 年 8 月。重點：致 Columbus of Numidia 論 North Africa Donatism 殘餘、Augustine of Canterbury 到達 Kent 後給 King Æthelberht 的回信、修道院制度改革、與 Lombard 持續和談。`,
  topics: ['書信錄', 'Numidia', 'Kent 皈依', 'Augustine of Canterbury'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'epistolae-book-vii-596-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (Schaff NPNF2 Vol 12)',
      textKey: 'epistolae-book-vii-596-english',
      source: 'CCEL — Schaff NPNF2 Vol 12 (Gregory the Great)',
    },
    {
      lang: 'lat',
      label: '拉丁原文（待補）',
      textKey: 'epistolae-book-vii-596-latin',
      placeholder: true,
    },
  ],
  displayMode: 'paragraph-aligned',
}
