import type { Creed } from '../types'

export const vaticanIICD: Creed = {
  slug: 'vatican-ii-cd-christus-dominus',
  category: 'ecumenical-council',
  councilNo: 21,
  councilDocCode: 'CD',
  councilDocOrder: 6,
  order: 2106,
  nameZh: '主教在教會內牧靈職務法令',
  nameEn: 'Decree concerning the Pastoral Office of Bishops in the Church',
  nameLat: 'Christus Dominus',
  year: 1965,
  location: '羅馬‧聖伯多祿大殿（梵二第四會期）',
  topic: '主教的牧靈職權、與教宗的關係、主教團合議性、教區結構、主教會議等具體建制',
  authors: [
    '教宗保祿六世（Paul VI）頒佈',
  ],
  acceptedBy: ['catholic'],
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '思高／天主教中文版（vatican.va 官方繁體 PDF 抽字）',
      text: '',
      textKey: 'cd-chinese',
      source: 'https://www.vatican.va/chinese/concilio/vat-ii_christus-dominus_zh-t.pdf',
      translator: '台灣地區主教團 / 香港教區禮儀委員會',
    },
    {
      lang: 'en',
      label: 'Vatican official English translation',
      text: '',
      textKey: 'cd-english',
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decree_19651028_christus-dominus_en.html',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina',
      text: '',
      textKey: 'cd-latin',
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decree_19651028_christus-dominus_lt.html',
    },
  ],
  summaryZh: `本文件把《教會憲章》第三章的「主教合議性」原則落實為具體建制：教區界線重劃、主教退休年齡 75 歲、設立主教會議（Synod of Bishops, 1965 由保祿六世先期設立）作為與教宗共同治理的常設機制。`,
  notes: `首次明確肯定主教應與本國其他主教合作（主教團 Episcopal Conference）並建議定期區域會議。`,
  related: ['vatican-ii-lg-lumen-gentium'],
}
