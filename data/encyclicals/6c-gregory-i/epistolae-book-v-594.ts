import type { PapalDocument } from '../types'

export const epistolaeBookV594: PapalDocument = {
  slug: 'epistolae-book-v-594',
  popeSlug: 'gregory-i',
  category: 'epistola',
  titleLat: 'Registrum Epistolarum, Liber V',
  titleEn: 'Register of Epistles — Book V (Year 5)',
  titleZh: '《書信錄》第五冊 — 594 年',
  promulgationDate: '594-09-01',
  century: 6,
  summaryZh: `《書信錄》第五冊，594 年 9 月至 595 年 8 月。重點：與 John IV of Constantinople 對「Ecumenical Patriarch」頭銜的全面論戰、教宗自稱「Servus Servorum Dei（眾僕之僕）」的標誌性表述開始大量出現、Spain 西哥德教會整合進展、嚴控修道院規律。`,
  topics: ['書信錄', 'Servus Servorum Dei', 'Ecumenical Patriarch 論戰'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'epistolae-book-v-594-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (Schaff NPNF2 Vol 12)',
      textKey: 'epistolae-book-v-594-english',
      source: 'CCEL — Schaff NPNF2 Vol 12 (Gregory the Great)',
    },
    {
      lang: 'lat',
      label: '拉丁原文（待補）',
      textKey: 'epistolae-book-v-594-latin',
      placeholder: true,
    },
  ],
  displayMode: 'paragraph-aligned',
}
