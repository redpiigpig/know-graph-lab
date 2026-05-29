import type { PapalDocument } from '../types'

export const venerabilem1202: PapalDocument = {
  slug: 'venerabilem-1202',
  popeSlug: 'innocent-iii',
  category: 'bull',
  titleLat: 'Venerabilem',
  titleEn: 'On the Imperial Election (Translatio Imperii)',
  titleZh: '《尊敬的弟兄》詔書 — 教宗認可神羅皇帝選舉（translatio imperii）',
  promulgationDate: '1202-03-01',
  century: 13,
  summaryZh: `教宗諾森三世 1202 年頒布的詔書（致大公爵 Berthold of Zähringen），是中世紀「教宗 vs. 神聖羅馬帝國」關係的奠基性文件。確立四大原則：(1) 教宗有最終裁決權審查神羅皇帝選舉；(2) 一旦選舉爭議，教宗可介入；(3) 教宗有權給予或撤回對皇帝的加冕祝聖；(4) translatio imperii — 教宗將羅馬帝國權威從希臘人轉移至日耳曼人（800 年查理曼加冕、962 年奧托一世加冕的法理依據）。後納入 *Corpus Iuris Canonici* 之 *Liber Extra* (1234) 作為教會法基礎，整個 13-15 世紀帝國─教廷權力鬥爭都援引此 decretal。`,
  topics: ['教宗 vs 帝國', 'translatio imperii', '神羅皇帝選舉', '教會法'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'venerabilem-1202-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文（待補）',
      textKey: 'venerabilem-1202-english',
      placeholder: true,
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org)',
      textKey: 'venerabilem-1202-latin',
      source: 'https://la.wikisource.org/wiki/Venerabilem',
    },
  ],
  displayMode: 'paragraph-aligned',
}
