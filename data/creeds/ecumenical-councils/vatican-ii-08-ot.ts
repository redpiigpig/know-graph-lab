import type { Creed } from '../types'

export const vaticanIIOT: Creed = {
  slug: 'vatican-ii-ot-optatam-totius',
  category: 'ecumenical-council',
  councilNo: 21,
  councilDocCode: 'OT',
  councilDocOrder: 8,
  order: 2108,
  nameZh: '司鐸之培養法令',
  nameEn: 'Decree on the Training of Priests',
  nameLat: 'Optatam Totius',
  year: 1965,
  location: '羅馬‧聖伯多祿大殿（梵二第四會期）',
  topic: '天主教神職培育（修院）的革新方向：靈修陶成、學識陶成、牧靈陶成、人格陶成四面向整合',
  authors: [
    '教宗保祿六世（Paul VI）頒佈',
  ],
  acceptedBy: ['catholic'],
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '思高／天主教中文版（vatican.va 官方繁體 PDF 抽字）',
      text: '',
      textKey: 'ot-chinese',
      source: 'https://www.vatican.va/chinese/concilio/vat-ii_optatam-totius_zh-t.pdf',
      translator: '台灣地區主教團 / 香港教區禮儀委員會',
    },
    {
      lang: 'en',
      label: 'Vatican official English translation',
      text: '',
      textKey: 'ot-english',
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decree_19651028_optatam-totius_en.html',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina',
      text: '',
      textKey: 'ot-latin',
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decree_19651028_optatam-totius_lt.html',
    },
  ],
  summaryZh: `本文件要求神學教育以聖經為核心、深化教父研究、與時並進處理當代問題（哲學、人文社會科學的對話）。直接後果是各國神學院課綱大改、聖經學系大幅擴張。`,
  notes: `後續 1985《Ratio Fundamentalis Institutionis Sacerdotalis》與 1992 若望保祿二世《Pastores Dabo Vobis》具體化。`,
  related: ['vatican-ii-po-presbyterorum-ordinis'],
}
