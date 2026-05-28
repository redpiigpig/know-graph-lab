import type { PapalDocument } from '../types'

export const diuturnumIllud1881: PapalDocument = {
  slug: 'diuturnum-illud-1881',
  popeSlug: 'leo-xiii',
  category: 'encyclical',
  titleLat: 'Diuturnum Illud',
  titleEn: 'On the Origin of Civil Power',
  titleZh: '《長久以來》通諭 — 論政治權威之源',
  promulgationDate: '1881-06-29',
  century: 19,
  summaryZh: `教宗良十三世 1881 年通諭，闡明天主教政治神學的核心原則：政治權威源自上帝，但人民可以選擇授權形式（直接民主、間接代表制、君主制皆可），無須拘泥於某種特定政體。背景是 19 世紀末歐洲王權崩潰（法國第三共和、義大利統一）、社會契約論盛行。是良十三世「Christian democracy」立場奠基的一篇。`,
  topics: ['政治神學', '權威來源', '民主', '君主制'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'diuturnum-illud-1881-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (papalencyclicals.net)',
      textKey: 'diuturnum-illud-1881-english',
      source: 'https://www.papalencyclicals.net/leo13/l13diutu.htm',
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org)',
      textKey: 'diuturnum-illud-1881-latin',
      source: 'https://la.wikisource.org/wiki/Diuturnum_Illud',
    },
  ],
  displayMode: 'paragraph-aligned',
}
