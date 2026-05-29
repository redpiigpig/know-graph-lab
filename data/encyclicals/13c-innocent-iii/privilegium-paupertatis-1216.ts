import type { PapalDocument } from '../types'

export const privilegiumPaupertatis1216: PapalDocument = {
  slug: 'privilegium-paupertatis-1216',
  popeSlug: 'innocent-iii',
  category: 'bull',
  titleLat: 'Privilegium Paupertatis',
  titleEn: 'Privilege of Poverty (Franciscan Charter)',
  titleZh: '《貧窮特許》詔書 — 方濟會聖嘉勒會「貧窮特權」',
  promulgationDate: '1216-07-15',
  century: 13,
  summaryZh: `教宗諾森三世 1216 年頒給聖嘉勒（Clare of Assisi, 1194-1253）及其修會的詔書，授予俗稱「Privilege of Poverty（貧窮特權）」——這是教廷史上極罕見的「特權」內容：不擁有財產、不接受贈與、不持有不動產的權利。傳統的修道院都被要求擁有財產（為維持生計），但 Clare 堅持要與聖方濟一樣絕對貧窮。Innocent III 在去世前 1 天親自簽署此特權。1228 Gregory IX 確認，1253 Innocent IV 最後一次確認。是中世紀「使徒貧窮」運動最高峰的官方文件。`,
  topics: ['方濟會', '聖嘉勒', '使徒貧窮', '修會特權'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'privilegium-paupertatis-1216-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文（待補）',
      textKey: 'privilegium-paupertatis-1216-english',
      placeholder: true,
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org)',
      textKey: 'privilegium-paupertatis-1216-latin',
      source: 'https://la.wikisource.org/wiki/Bulla_%C2%ABPrivilegium_Paupertatis%C2%BB_(1216)',
    },
  ],
  displayMode: 'paragraph-aligned',
}
