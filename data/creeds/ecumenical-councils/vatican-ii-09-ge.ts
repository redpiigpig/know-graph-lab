import type { Creed } from '../types'
// @ts-expect-error — Vite raw-text import
import latText from './vatican-ii/ge-latin.txt?raw'
// @ts-expect-error — Vite raw-text import
import enText from './vatican-ii/ge-english.txt?raw'

export const vaticanIIGE: Creed = {
  slug: 'vatican-ii-ge-gravissimum-educationis',
  category: 'ecumenical-council',
  councilNo: 21,
  councilDocCode: 'GE',
  councilDocOrder: 9,
  order: 2109,
  nameZh: '天主教教育宣言',
  nameEn: 'Declaration on Christian Education',
  nameLat: 'Gravissimum Educationis',
  year: 1965,
  location: '羅馬‧聖伯多祿大殿（梵二第四會期）',
  topic: '天主教學校（小中大學）的教育理念、與公立教育的關係、信仰自由與宗教教育權',
  authors: [
    '教宗保祿六世（Paul VI）頒佈',
  ],
  acceptedBy: ['catholic'],
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '思高／天主教中文版（vatican.va 官方繁體 PDF）',
      text: '待補：vatican.va 中文版為 PDF 檔，需手動下載抽字後填入。\n下載：https://www.vatican.va/chinese/concilio/vat-ii_gravissimum-educationis_zh-t.pdf',
      source: 'https://www.vatican.va/chinese/concilio/vat-ii_gravissimum-educationis_zh-t.pdf',
      translator: '台灣地區主教團 / 香港教區禮儀委員會',
      placeholder: true,
    },
    {
      lang: 'en',
      label: 'Vatican official English translation',
      text: enText as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decl_19651028_gravissimum-educationis_en.html',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina',
      text: latText as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decl_19651028_gravissimum-educationis_lt.html',
    },
  ],
  summaryZh: `本文件肯定天主教學校的權利與使命，並要求世俗政府保障父母選擇宗教教育的自由。對北美天主教學校系統、菲律賓、拉丁美洲等天主教教育網絡具直接政策意涵。`,
  notes: `宗座教育部 1977《教會學校》訓令 + 1988《天主教學校的宗教面向》具體化。`,
  related: ['vatican-ii-dh-dignitatis-humanae'],
}
