import type { PapalDocument } from '../types'

export const letter16ToSicily447: PapalDocument = {
  slug: 'letter-16-to-sicily-447',
  popeSlug: 'leo-i',
  category: 'epistola',
  titleLat: 'Epistula XVI ad Episcopos Siciliae',
  titleEn: 'Letter XVI — To the Bishops of Sicily (on Baptismal Discipline)',
  titleZh: '《致西西里主教團》書信 — 論洗禮節期',
  promulgationDate: '447-10-21',
  century: 5,
  summaryZh: `教宗大良 447 年致西西里主教團的書信，糾正當地把洗禮時間錯置於主顯節（Epiphany 1月6日）的做法。教宗主張洗禮應集中在復活節守夜禮（Pascha）與五旬節（Pentecost），因為這兩節期才在禮儀上代表基督的死亡—復活與聖神降臨。書信並系統論述教會禮儀年三大期（受難、復活、五旬節）的神學意涵。是早期西方教會禮儀年制度的關鍵文件。`,
  topics: ['洗禮', '禮儀年', '復活節', '西西里教會'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'letter-16-to-sicily-447-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (Schaff NPNF2 Vol 12)',
      textKey: 'letter-16-to-sicily-447-english',
      source: 'CCEL — Schaff NPNF2 Vol 12 (Leo the Great)',
    },
    {
      lang: 'lat',
      label: '拉丁原文 (Migne PL 54 OCR — archive.org)',
      textKey: 'letter-16-to-sicily-447-latin',
      source: 'https://archive.org/details/sanctileonismagn01leoi',

    },
  ],
  displayMode: 'paragraph-aligned',
}
