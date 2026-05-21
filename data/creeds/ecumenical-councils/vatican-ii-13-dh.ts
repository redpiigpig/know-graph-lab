import type { Creed } from '../types'

export const vaticanIIDH: Creed = {
  slug: 'vatican-ii-dh-dignitatis-humanae',
  category: 'ecumenical-council',
  councilNo: 21,
  councilDocCode: 'DH',
  councilDocOrder: 13,
  order: 2113,
  nameZh: '信仰自由宣言',
  nameEn: 'Declaration on Religious Freedom',
  nameLat: 'Dignitatis Humanae',
  year: 1965,
  location: '羅馬‧聖伯多祿大殿（梵二第四會期）',
  topic: '宗教自由是基於人性尊嚴的基本人權；國家不得強制或禁止任何宗教信仰；與十九世紀天主教反現代主義立場的歷史轉向',
  authors: [
    '教宗保祿六世（Paul VI）頒佈',
  ],
  acceptedBy: ['catholic'],
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '思高／天主教中文版（vatican.va 官方繁體 PDF 抽字）',
      text: '',
      textKey: 'dh-chinese',
      source: 'https://www.vatican.va/chinese/concilio/vat-ii_dignitatis-humanae_zh-t.pdf',
      translator: '台灣地區主教團 / 香港教區禮儀委員會',
    },
    {
      lang: 'en',
      label: 'Vatican official English translation',
      text: '',
      textKey: 'dh-english',
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decl_19651207_dignitatis-humanae_en.html',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina',
      text: '',
      textKey: 'dh-latin',
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decl_19651207_dignitatis-humanae_lt.html',
    },
  ],
  summaryZh: `本文件是梵二爭議最大的文件之一，反對派（Lefebvre 領頭）認為與 Pius IX 1864《Syllabus Errorum》 § 15-18 譴責「宗教自由」相矛盾。最終 2308 贊成 vs 70 反對通過，但成為 SSPX 後續分裂的關鍵理由。主筆者：John Courtney Murray（耶穌會美籍神學家）。`,
  notes: `與 Pius IX 19 世紀立場的「發展連續性 vs 斷裂」之爭，至今仍是天主教傳統派與主流派的議題。1986 若望保祿二世亞西西宗教聚會將本文件原則付諸實踐。`,
  related: ['vatican-ii-na-nostra-aetate', 'vatican-ii-ge-gravissimum-educationis'],
}
