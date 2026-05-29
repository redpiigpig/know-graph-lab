import type { PapalDocument } from '../types'

export const epistolaeBookVi595: PapalDocument = {
  slug: 'epistolae-book-vi-595',
  popeSlug: 'gregory-i',
  category: 'epistola',
  titleLat: 'Registrum Epistolarum, Liber VI',
  titleEn: 'Register of Epistles — Book VI (Year 6)',
  titleZh: '《書信錄》第六冊 — 595 年',
  promulgationDate: '595-09-01',
  century: 6,
  summaryZh: `《書信錄》第六冊，595 年 9 月至 596 年 8 月。重點：派遣 Augustine of Canterbury 與 40 位修士從 Rome 出發前往英國傳教（596 年啟程 — Anglo-Saxon 皈依的開端）、致 Mauricius Augustus 論教宗與帝國關係、對 Sardinia 教區改革。`,
  topics: ['書信錄', 'Augustine of Canterbury', '英國傳教', '教廷帝國'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'epistolae-book-vi-595-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (Schaff NPNF2 Vol 12)',
      textKey: 'epistolae-book-vi-595-english',
      source: 'CCEL — Schaff NPNF2 Vol 12 (Gregory the Great)',
    },
    {
      lang: 'lat',
      label: '拉丁原文（待補）',
      textKey: 'epistolae-book-vi-595-latin',
      placeholder: true,
    },
  ],
  displayMode: 'paragraph-aligned',
}
