import type { Creed } from '../types'
// @ts-expect-error — Vite raw-text import
import latText from './vatican-ii/gs-latin.txt?raw'
// @ts-expect-error — Vite raw-text import
import enText from './vatican-ii/gs-english.txt?raw'

export const vaticanIIGS: Creed = {
  slug: 'vatican-ii-gs-gaudium-et-spes',
  category: 'ecumenical-council',
  councilNo: 21,
  councilDocCode: 'GS',
  councilDocOrder: 16,
  order: 2116,
  nameZh: '牧靈憲章',
  nameEn: 'Pastoral Constitution on the Church in the Modern World',
  nameLat: 'Gaudium Et Spes',
  year: 1965,
  location: '羅馬‧聖伯多祿大殿（梵二第四會期）',
  topic: '教會與當代世界的關係 — 人性尊嚴、社會共善、婚姻家庭、文化、經濟、政治、和平 — 教會對 20 世紀世界處境的總體性回應',
  authors: [
    '教宗保祿六世（Paul VI）頒佈',
  ],
  acceptedBy: ['catholic'],
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '思高／天主教中文版（vatican.va 官方繁體 PDF）',
      text: '待補：vatican.va 中文版為 PDF 檔，需手動下載抽字後填入。\n下載：https://www.vatican.va/chinese/concilio/vat-ii_gaudium-et-spes_zh-t.pdf',
      source: 'https://www.vatican.va/chinese/concilio/vat-ii_gaudium-et-spes_zh-t.pdf',
      translator: '台灣地區主教團 / 香港教區禮儀委員會',
      placeholder: true,
    },
    {
      lang: 'en',
      label: 'Vatican official English translation',
      text: enText as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_const_19651207_gaudium-et-spes_en.html',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina',
      text: latText as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_const_19651207_gaudium-et-spes_lt.html',
    },
  ],
  summaryZh: `1965 年 12 月 7 日（梵二閉幕前一日）頒佈，是梵二最長文件（93 段，分兩部）。最重要特色：① 首份以「牧靈」（pastoral）為名而非「教義」（dogmatic）的大公會議文件 ② 第一部分討論教會對人的本質、社會、活動、命運的看法；第二部分具體討論婚姻家庭、文化、經濟、政治、和平五大議題 ③ 開創天主教「公共神學」與「社會教導」現代傳統。`,
  notes: `與《教會憲章》互補：LG 是「教會 ad intra」（教會內部）；GS 是「教會 ad extra」（教會面對世界）。標題開頭「Gaudium et Spes」（喜樂與希望）成為本文件代稱。`,
  related: ['vatican-ii-lg-lumen-gentium', 'vatican-ii-dh-dignitatis-humanae'],
}
