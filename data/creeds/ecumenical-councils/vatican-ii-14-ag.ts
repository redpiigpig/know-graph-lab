import type { Creed } from '../types'

export const vaticanIIAG: Creed = {
  slug: 'vatican-ii-ag-ad-gentes',
  category: 'ecumenical-council',
  councilNo: 21,
  councilDocCode: 'AG',
  councilDocOrder: 14,
  order: 2114,
  nameZh: '教會傳教工作法令',
  nameEn: 'Decree on the Mission Activity of the Church',
  nameLat: 'Ad Gentes',
  year: 1965,
  location: '羅馬‧聖伯多祿大殿（梵二第四會期）',
  topic: '教會的「傳教使命」（missio ad gentes）— 為什麼傳教、向誰傳教、如何傳教，特別是非基督文化地區的本土化與文化適應',
  authors: [
    '教宗保祿六世（Paul VI）頒佈',
  ],
  acceptedBy: ['catholic'],
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '思高／天主教中文版（vatican.va 官方繁體 PDF 抽字）',
      text: '',
      textKey: 'ag-chinese',
      source: 'https://www.vatican.va/chinese/concilio/vat-ii_ad-gentes_zh-t.pdf',
      translator: '台灣地區主教團 / 香港教區禮儀委員會',
    },
    {
      lang: 'en',
      label: 'Vatican official English translation',
      text: '',
      textKey: 'ag-english',
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decree_19651207_ad-gentes_en.html',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina',
      text: '',
      textKey: 'ag-latin',
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decree_19651207_ad-gentes_lt.html',
    },
  ],
  summaryZh: `本文件確立「教會本性就是傳教」（Ecclesia per se missionaria, §2）的原則；強調傳教必須「本土化」（accommodatio / inculturation），尊重當地文化、語言、思想形式；不可簡單複製西方教會模式。亞洲、非洲傳教學的根基文件。`,
  notes: `1975 保祿六世《Evangelii Nuntiandi》宗座勸諭、1990 若望保祿二世《Redemptoris Missio》通諭、2013 方濟各《Evangelii Gaudium》使徒勸諭依序具體化本文件原則。`,
  related: ['vatican-ii-na-nostra-aetate', 'vatican-ii-ur-unitatis-redintegratio'],
}
