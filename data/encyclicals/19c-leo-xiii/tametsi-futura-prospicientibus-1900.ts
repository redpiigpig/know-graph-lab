import type { PapalDocument } from '../types'

export const tametsiFuturaProspicientibus1900: PapalDocument = {
  slug: 'tametsi-futura-prospicientibus-1900',
  popeSlug: 'leo-xiii',
  category: 'encyclical',
  titleLat: 'Tametsi Futura Prospicientibus',
  titleEn: 'On Jesus Christ Our Redeemer',
  titleZh: '《雖然瞻望未來》通諭 — 論吾主救主基督',
  promulgationDate: '1900-11-01',
  century: 19,
  summaryZh: `教宗良十三世 1900 年通諭，世紀末總結性訓導文件。檢視 19 世紀末歐洲信仰危機、知識分子背離基督、社會崇拜物質與權力。把基督呈現為「道路、真理、生命」三位一體的核心，呼籲社會與個人回歸基督。是良十三世 25 年任期的神學遺囑，1903 他去世前最重要的牧靈訊息之一。`,
  topics: ['基督論', '救贖', '信仰危機', '世紀末'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'tametsi-futura-prospicientibus-1900-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (papalencyclicals.net)',
      textKey: 'tametsi-futura-prospicientibus-1900-english',
      source: 'https://www.papalencyclicals.net/leo13/l13tamet.htm',
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org)',
      textKey: 'tametsi-futura-prospicientibus-1900-latin',
      source: 'https://la.wikisource.org/wiki/Tametsi_Futura_Prospicientibus',
    },
  ],
  displayMode: 'paragraph-aligned',
}
