import type { PapalDocument } from '../types'

export const laudatoSi2015: PapalDocument = {
  slug: 'laudato-si-2015',
  popeSlug: 'francis',
  category: 'encyclical',
  titleLat: "Laudato Si'",
  titleEn: 'On Care for Our Common Home',
  titleZh: '《願祢受讚頌》通諭 — 論愛惜我們共同的家園',
  promulgationDate: '2015-05-24',
  century: 21,
  summaryZh: `教宗方濟各第二道通諭，亦是第一道由他本人從頭撰寫的通諭（《信德之光》接續本篤十六世遺稿）。全文 246 段，分六章，以亞西西聖方濟《造物讚》「我主，願祢受讚頌」開篇，邀請整個人類大家庭共同面對「我們共同的家園」── 地球 ── 所遭遇的生態與社會雙重危機。

通諭首次系統地把「整體生態學」（Ecologia integralis）置於天主教社會訓導核心：環境問題不可從貧窮、不平等、消費主義、技術典範等社會議題切割看待。文件大量引述非天主教來源（君士坦丁堡大公宗主教巴爾多祿茂、伊斯蘭蘇菲派、阿根廷神學家），體現方濟各「對話」風格的社會訓導模式。`,
  topics: ['整體生態學', '氣候變遷', '社會訓導', '科技典範', '消費主義', '世代正義'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（天主教會臺灣地區主教團 譯）',
      textKey: 'laudato-si-2015-chinese',
      source: 'https://www.vatican.va/content/dam/francesco/pdf/encyclicals/documents/papa-francesco_20150524_enciclica-laudato-si_zh_tw.pdf',
      translator: '天主教會臺灣地區主教團',
    },
    {
      lang: 'en',
      label: '英文 (vatican.va)',
      textKey: 'laudato-si-2015-english',
      source: 'https://www.vatican.va/content/francesco/en/encyclicals/documents/papa-francesco_20150524_enciclica-laudato-si.html',
    },
    {
      lang: 'lat',
      label: '拉丁原文 (vatican.va)',
      textKey: 'laudato-si-2015-latin',
      source: 'https://www.vatican.va/content/francesco/la/encyclicals/documents/papa-francesco_20150524_enciclica-laudato-si.html',
    },
  ],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/francesco/en/encyclicals/documents/papa-francesco_20150524_enciclica-laudato-si.html',
  notes: `本通諭的命名典出亞西西聖方濟用古翁布利亞方言寫的《造物讚》（Canticle of the Creatures）首句 "Laudato si', mi' Signore"（我主，願祢受讚頌），故拉丁標題保留中世紀義大利方言原貌而非完全拉丁化。

頒布日期 2015-05-24 是聖神降臨節，刻意呼應創世記第一章「天主的神運行在水面上」的創造神學意象。`,
}
