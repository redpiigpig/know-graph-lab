import type { PapalDocument } from '../types'

export const tempusDesideratum400: PapalDocument = {
  slug: 'tempus-desideratum-400',
  popeSlug: 'anastasius-i',
  category: 'epistola',
  titleLat: 'Tempus desideratum (Epistola ad Simplicianum Mediolanensem)',
  titleEn: 'Letter to Simplicianus of Milan Condemning Origen',
  titleZh: '《盼望已久之時》書信 — 致米蘭主教 Simplicianus 譴責 Origenism',
  promulgationDate: '400-01-01',
  century: 4,
  summaryZh: `教宗安納斯塔修斯一世（399-401）約 400 年致米蘭主教 Simplicianus 的書信，正式譴責 Origenism（俄利根派）的若干命題——特別是 ① 先存靈魂論（pre-existence of souls）② Apokatastasis（普世救贖、終末萬物復興）③ 過於 allegorical 的釋經傾向。教宗 Anastasius 同時譴責 Rufinus 對 Origen 著作的拉丁翻譯（Rufinus 試圖把 Origen 介紹進西方拉丁世界）。是 4c 末 5c 初 Origenist Controversy 西方教廷立場的關鍵文件。後 553 Constantinople II 公會議的第 15 條 anathema 對 Origen 的譴責即承襲此立場。文獻收 DH 211。`,
  topics: ['Origenism 譴責', 'Rufinus 翻譯爭議', 'Apokatastasis 譴責', '先存靈魂論'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'tempus-desideratum-400-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文（待補）',
      textKey: 'tempus-desideratum-400-english',
      placeholder: true,
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org / Anastasius I — Epistolae et decreta)',
      textKey: 'tempus-desideratum-400-latin',
      source: 'https://la.wikisource.org/wiki/Epistolae_et_decreta_(Anastasius_I)',
    },
  ],
  displayMode: 'paragraph-aligned',
}
