import type { PapalDocument } from '../types'

export const adExuperium405: PapalDocument = {
  slug: 'ad-exuperium-405',
  popeSlug: 'innocent-i',
  category: 'epistola',
  titleLat: 'Consulenti tibi (Epistola ad Exsuperium Tolosanum)',
  titleEn: 'Letter to Exsuperius of Toulouse on the Canon of Scripture',
  titleZh: '《致 Toulouse 主教 Exsuperius 書信》— 405 西方教會聖經正典清單',
  promulgationDate: '405-02-20',
  century: 5,
  summaryZh: `教宗依諾增爵一世 405 年致 Toulouse 主教 Exsuperius 的書信。Exsuperius 先前請示哪些書屬於「教會接受的正典」（quae ... in canone scripturarum reciperentur）。教宗在第 7 章列出當時羅馬教廷接受的聖經正典清單——這份清單與 382 Damasine Canon / Council of Hippo 393 / Council of Carthage 397 大致一致，但比後者更具教廷正式約束力。是西方拉丁教會聖經正典 5c 早期最重要的官方文件之一。文獻收 DH 213。書信同時涵蓋紀律問題：離婚再婚的處理、神職人員守貞、Priscillianists 與 Origenists 的處置。`,
  topics: ['聖經正典', '405 教廷正典', 'Priscillianism 處置', '神職守貞延伸'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'ad-exuperium-405-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文（待補）',
      textKey: 'ad-exuperium-405-english',
      placeholder: true,
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org / Innocent I — Decreta)',
      textKey: 'ad-exuperium-405-latin',
      source: 'https://la.wikisource.org/wiki/Decreta_(Innocentius_I)',
    },
  ],
  displayMode: 'paragraph-aligned',
}
