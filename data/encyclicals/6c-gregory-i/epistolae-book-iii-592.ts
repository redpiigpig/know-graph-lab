import type { PapalDocument } from '../types'

export const epistolaeBookIii592: PapalDocument = {
  slug: 'epistolae-book-iii-592',
  popeSlug: 'gregory-i',
  category: 'epistola',
  titleLat: 'Registrum Epistolarum, Liber III',
  titleEn: 'Register of Epistles — Book III (Year 3)',
  titleZh: '《書信錄》第三冊 — 592 年',
  promulgationDate: '592-09-01',
  century: 6,
  summaryZh: `《書信錄》第三冊，592 年 9 月至 593 年 8 月。重點：對 Campania 莊園管理（致 Peter, Subdeacon）、Spain 教區與 Reccared 國王皈依（西哥德從 Arian 改正統的關鍵歷史）、對 Constantinople 牧首爭論升級、對北非 Donatist 殘餘的處理。`,
  topics: ['書信錄', '西班牙皈依', 'Donatism', '教廷莊園'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'epistolae-book-iii-592-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (Schaff NPNF2 Vol 12)',
      textKey: 'epistolae-book-iii-592-english',
      source: 'CCEL — Schaff NPNF2 Vol 12 (Gregory the Great)',
    },
    {
      lang: 'lat',
      label: '拉丁原文（待補）',
      textKey: 'epistolae-book-iii-592-latin',
      placeholder: true,
    },
  ],
  displayMode: 'paragraph-aligned',
}
