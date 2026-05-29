import type { PapalDocument } from '../types'

export const epistolaeBookIv593: PapalDocument = {
  slug: 'epistolae-book-iv-593',
  popeSlug: 'gregory-i',
  category: 'epistola',
  titleLat: 'Registrum Epistolarum, Liber IV',
  titleEn: 'Register of Epistles — Book IV (Year 4)',
  titleZh: '《書信錄》第四冊 — 593 年',
  promulgationDate: '593-09-01',
  century: 6,
  summaryZh: `《書信錄》第四冊，593 年 9 月至 594 年 8 月。重點：致 Constantius of Milan（Lombard 入侵下的牧靈策略）、Africa 教區 Donatist 議題、與 Constantinople 皇帝 Maurice 衝突日深、Roman patrimony 的法律處理。`,
  topics: ['書信錄', 'Lombard 牧靈', 'Donatism', '教廷與帝國'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'epistolae-book-iv-593-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (Schaff NPNF2 Vol 12)',
      textKey: 'epistolae-book-iv-593-english',
      source: 'CCEL — Schaff NPNF2 Vol 12 (Gregory the Great)',
    },
    {
      lang: 'lat',
      label: '拉丁原文（待補）',
      textKey: 'epistolae-book-iv-593-latin',
      placeholder: true,
    },
  ],
  displayMode: 'paragraph-aligned',
}
