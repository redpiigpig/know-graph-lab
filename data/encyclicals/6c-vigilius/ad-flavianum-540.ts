import type { PapalDocument } from '../types'

export const adFlavianum540: PapalDocument = {
  slug: 'ad-flavianum-540',
  popeSlug: 'vigilius',
  category: 'epistola',
  titleLat: 'Dum in sanctae',
  titleEn: 'Letter on the Three Chapters Controversy',
  titleZh: '《在神聖之中》— 三章案爭議書信',
  promulgationDate: '540-06-29',
  century: 6,
  summaryZh: `教宗維吉略（Vigilius, 537-555）關於「三章案」（Three Chapters Controversy）的書信。三章案是 6c 中葉東西教會的神學爭議——Justinian I 為了與 Monophysite 東方教派和解、譴責三位已死的 5c 神學家（Theodore of Mopsuestia / Theodoret of Cyrrhus / Ibas of Edessa）。Vigilius 在這場政治壓力下立場反覆——先反對譴責、後在 Justinian 拘押下同意、再撤回、最後在 553 Constantinople II 公會議（被迫）接受。本書信為其早期立場文件之一。是研究 6c 教廷在政治與信理張力中的關鍵 case。`,
  topics: ['三章案', 'Justinian I 神學政策', 'Constantinople II 553', '教廷在帝國壓力下'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'ad-flavianum-540-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文（待補）',
      textKey: 'ad-flavianum-540-english',
      placeholder: true,
    },
    {
      lang: 'lat',
      label: '拉丁原文（待補 — Migne PL 69）',
      textKey: 'ad-flavianum-540-latin',
      placeholder: true,
    },
  ],
  displayMode: 'paragraph-aligned',
}
