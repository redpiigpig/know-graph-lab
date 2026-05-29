import type { PapalDocument } from '../types'

export const mysteriaEvangelicaeLegis1205: PapalDocument = {
  slug: 'mysteria-evangelicae-legis-1205',
  popeSlug: 'innocent-iii',
  category: 'epistola',
  titleLat: 'Mysteria Evangelicae Legis et Sacramenti Eucharistiae',
  titleEn: 'On the Mysteries of the Gospel Law and the Sacrament of the Eucharist',
  titleZh: '《福音律的奧秘與聖體聖事》論著 ★ — 聖體變質論神學',
  promulgationDate: '1205-01-01',
  century: 13,
  summaryZh: `教宗諾森三世 1205 年寫的聖體聖事神學論著，是 1215 Lateran IV 大公會議正式定義 transubstantiation（變質說）的神學前奏。系統論述：(1) 福音律與舊約律的區別；(2) 聖體中麵餅與葡萄酒的「實質性轉變（transsubstantiatio）」教義——首次系統使用此拉丁詞彙；(3) 反對中世紀早期 Berengar of Tours 之 symbolic 觀點。本論著是中世紀盛期聖事神學的奠基性文獻。`,
  topics: ['聖體聖事', 'transubstantiation', '變質說', 'Lateran IV 前奏'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'mysteria-evangelicae-legis-1205-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文（待補）',
      textKey: 'mysteria-evangelicae-legis-1205-english',
      placeholder: true,
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org)',
      textKey: 'mysteria-evangelicae-legis-1205-latin',
      source: 'https://la.wikisource.org/wiki/Mysteria_evangelicae_legis_et_sacramenti_eucharistiae',
    },
  ],
  displayMode: 'paragraph-aligned',
}
