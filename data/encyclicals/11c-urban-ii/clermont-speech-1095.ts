import type { PapalDocument } from '../types'

export const clermontSpeech1095: PapalDocument = {
  slug: 'clermont-speech-1095',
  popeSlug: 'urban-ii',
  category: 'allocution',
  titleLat: 'Sermo in Concilio Claromontano',
  titleEn: 'Speech at the Council of Clermont (Five Chronicler Versions)',
  titleZh: '《克勒蒙會議演說》★★★ — 號召第一次十字軍（5 個年代史家版本）',
  promulgationDate: '1095-11-27',
  century: 11,
  summaryZh: `教宗烏爾巴諾二世 1095 年 11 月 27 日在法國 Clermont（今 Clermont-Ferrand）會議的閉幕日演說，號召西方基督徒「武裝朝聖」（armed pilgrimage）解放耶路撒冷與東方基督徒——即第一次十字軍（1096-1099）的引信。演說現場無人完整速記，僅由 4 位年代史家分別記錄成 4 個版本（Fulcher of Chartres / Robert the Monk / Baldric of Dol / Guibert of Nogent），加上保存在書信 collection 中的第 5 版本——5 個版本在主題（耶路撒冷的悲況、要求西方教會援助、所有參戰者得大赦）大致一致，但細節差異顯示是當時史家的二手記錄。Fordham 把 5 個版本並排呈現是研究中世紀「文獻 vs 神話」的經典 case study。`,
  topics: ['第一次十字軍', 'Council of Clermont', 'Deus Vult', '中世紀教廷外交', 'armed pilgrimage 神學'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'clermont-speech-1095-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (Fordham — Internet Medieval Sourcebook)',
      textKey: 'clermont-speech-1095-english',
      source: 'https://sourcebooks.fordham.edu/source/urban2-5vers.asp',
    },
    {
      lang: 'lat',
      label: '拉丁原文（待補 — Migne PL 151）',
      textKey: 'clermont-speech-1095-latin',
      placeholder: true,
    },
  ],
  displayMode: 'paragraph-aligned',
}
