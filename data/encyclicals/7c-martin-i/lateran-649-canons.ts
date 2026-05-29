import type { PapalDocument } from '../types'

export const lateran649Canons: PapalDocument = {
  slug: 'lateran-649-canons',
  popeSlug: 'martin-i',
  category: 'apostolic-const',
  titleLat: 'Acta Concilii Lateranensis (sub Martino I)',
  titleEn: 'Acts of the Lateran Council 649 — Condemnation of Monotheletism',
  titleZh: '《649 拉特朗會議憲令》★★ — 譴責 Monothelite，導致 Martin I 殉道',
  promulgationDate: '649-10-31',
  century: 7,
  summaryZh: `教宗瑪定一世 649 年 10 月召開拉特朗會議（Lateran Council of 649），由 105 位西方主教參與，正式譴責 Monothelite 異端（基督只有一個意志）與 Monoenergism（只一個能動性）。會議發布 20 條 canons，明確宣告「基督有二位格意志、二能動性」（two wills, two energies）——為 681 Constantinople III 公會議的最終信理鋪路。然而東羅馬皇帝 Constans II 因 Monothelite 是其官方立場，下令拘押 Martin I — 教宗被 Exarch of Ravenna 派人從聖殿中強行帶走、送往君士坦丁堡受審、剝奪宗座地位、流放至 Crimea，於 655 年在流放中受迫害致死。是教宗史上少數正式殉道者（最後一位殉道教宗）。本會議憲令也是 7c 西方教會教義最高峰文件之一。文獻收 DH 500-522。`,
  topics: ['Lateran 649 公會議', '反 Monothelite', '二意志論', 'Martin I 殉道', '東羅馬迫害'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'lateran-649-canons-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文（待補）',
      textKey: 'lateran-649-canons-english',
      placeholder: true,
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org / Martin I — Privilegia)',
      textKey: 'lateran-649-canons-latin',
      source: 'https://la.wikisource.org/wiki/Privilegia_(Martinus_I)',
    },
  ],
  displayMode: 'paragraph-aligned',
}
