import type { PapalDocument } from '../types'

export const optarem386: PapalDocument = {
  slug: 'optarem-386',
  popeSlug: 'siricius',
  category: 'epistola',
  titleLat: 'Optarem semper (Epistola II ad episcopos)',
  titleEn: 'Second Decretal — Letter to the Bishops of Italy',
  titleZh: '《我向來盼望》詔書 — 致義大利各主教（第二封 Decretal）',
  promulgationDate: '386-01-06',
  century: 4,
  summaryZh: `教宗西利修斯 386 年羅馬會議後致義大利各主教的詔書。延續首封 Decretal（385《Directa》）的紀律規範，重申神職人員守貞、信徒再洗禮處置原則、洗禮日期規定。包含教廷對 Jovinian 異端（質疑童貞優於婚姻、質疑齋戒功德）的譴責。是西方教會修道禁慾運動正面神學辯護的開始。`,
  topics: ['第二 Decretal', '反 Jovinian', '童貞 vs 婚姻', '修道禁慾'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'optarem-386-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文（待補）',
      textKey: 'optarem-386-english',
      placeholder: true,
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org / Siricius — Epistolae et decreta)',
      textKey: 'optarem-386-latin',
      source: 'https://la.wikisource.org/wiki/Epistolae_et_decreta_(Siricius)',
    },
  ],
  displayMode: 'paragraph-aligned',
}
