import type { Creed } from '../types'
// @ts-expect-error — Vite raw-text import
import latText from './vatican-ii/oe-latin.txt?raw'
// @ts-expect-error — Vite raw-text import
import enText from './vatican-ii/oe-english.txt?raw'
// @ts-expect-error — Vite raw-text import
import zhText from './vatican-ii/oe-chinese.txt?raw'

export const vaticanIIOE: Creed = {
  slug: 'vatican-ii-oe-orientalium-ecclesiarum',
  category: 'ecumenical-council',
  councilNo: 21,
  councilDocCode: 'OE',
  councilDocOrder: 4,
  order: 2104,
  nameZh: '東方公教會法令',
  nameEn: 'Decree on the Catholic Churches of the Eastern Rite',
  nameLat: 'Orientalium Ecclesiarum',
  year: 1964,
  location: '羅馬‧聖伯多祿大殿（梵二第三會期）',
  topic: '與羅馬合一的東方禮天主教會（Eastern Catholic Churches）的地位、禮儀傳統保存、與東正教關係',
  authors: [
    '教宗保祿六世（Paul VI）頒佈',
  ],
  acceptedBy: ['catholic'],
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '思高／天主教中文版（vatican.va 官方繁體 PDF 抽字）',
      text: zhText as string,
      source: 'https://www.vatican.va/chinese/concilio/vat-ii_orientalium-ecclesiarum_zh-t.pdf',
      translator: '台灣地區主教團 / 香港教區禮儀委員會',
    },
    {
      lang: 'en',
      label: 'Vatican official English translation',
      text: enText as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decree_19641121_orientalium-ecclesiarum_en.html',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina',
      text: latText as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decree_19641121_orientalium-ecclesiarum_lt.html',
    },
  ],
  summaryZh: `本文件明確肯定 23 個與羅馬合一的東方禮教會（馬龍尼、希臘公教、烏克蘭希臘公教、敘利亞公教、亞美尼亞公教、迦勒底、馬蘭卡、科普特公教、衣索匹亞公教等）的「同等尊嚴」地位，禁止強制其拉丁化，並期待其成為與東正教合一的橋樑。`,
  notes: `對應的 1990 年《東方教會法典》（CCEO）為其法律具體化。`,
  related: ['vatican-ii-ur-unitatis-redintegratio'],
}
