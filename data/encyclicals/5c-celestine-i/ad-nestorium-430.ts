import type { PapalDocument } from '../types'

export const adNestorium430: PapalDocument = {
  slug: 'ad-nestorium-430',
  popeSlug: 'celestine-i',
  category: 'epistola',
  titleLat: 'Aliquantis diebus (Epistola ad Nestorium)',
  titleEn: 'Letter to Nestorius Demanding Retraction',
  titleZh: '《幾天以來》書信 — 致 Nestorius 要求公開撤回',
  promulgationDate: '430-08-11',
  century: 5,
  summaryZh: `教宗策肋定一世 430 年與《Apostolici verba》同日頒布的書信，直接致 Constantinople 主教 Nestorius。給出 10 日最後通牒：必須公開撤回否認 Theotokos 的立場，否則革除。Nestorius 拒絕，導致 431 Ephesus 公會議將其革除主教職並驅逐流放。本書信展現 5c 教廷在 Christology 危機中的決斷作風。`,
  topics: ['Nestorius 最後通牒', '教廷紀律處置'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'ad-nestorium-430-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文（待補）',
      textKey: 'ad-nestorium-430-english',
      placeholder: true,
    },
    {
      lang: 'lat',
      label: '拉丁原文（待補 — Migne PL 50）',
      textKey: 'ad-nestorium-430-latin',
      placeholder: true,
    },
  ],
  displayMode: 'paragraph-aligned',
}
