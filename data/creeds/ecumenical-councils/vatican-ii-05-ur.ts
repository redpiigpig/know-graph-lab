import type { Creed } from '../types'
// @ts-expect-error — Vite raw-text import
import latText from './vatican-ii/ur-latin.txt?raw'
// @ts-expect-error — Vite raw-text import
import enText from './vatican-ii/ur-english.txt?raw'

export const vaticanIIUR: Creed = {
  slug: 'vatican-ii-ur-unitatis-redintegratio',
  category: 'ecumenical-council',
  councilNo: 21,
  councilDocCode: 'UR',
  councilDocOrder: 5,
  order: 2105,
  nameZh: '大公主義法令',
  nameEn: 'Decree on Ecumenism',
  nameLat: 'Unitatis Redintegratio',
  year: 1964,
  location: '羅馬‧聖伯多祿大殿（梵二第三會期）',
  topic: '天主教投入普世合一運動的原則與方向；對東正教、東方東正教、聖公宗、新教各宗派的承認與對話框架',
  authors: [
    '教宗保祿六世（Paul VI）頒佈',
  ],
  acceptedBy: ['catholic'],
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '思高／天主教中文版（vatican.va 官方繁體 PDF）',
      text: '待補：vatican.va 中文版為 PDF 檔，需手動下載抽字後填入。\n下載：https://www.vatican.va/chinese/concilio/vat-ii_unitatis-redintegratio_zh-t.pdf',
      source: 'https://www.vatican.va/chinese/concilio/vat-ii_unitatis-redintegratio_zh-t.pdf',
      translator: '台灣地區主教團 / 香港教區禮儀委員會',
      placeholder: true,
    },
    {
      lang: 'en',
      label: 'Vatican official English translation',
      text: enText as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decree_19641121_unitatis-redintegratio_en.html',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina',
      text: latText as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decree_19641121_unitatis-redintegratio_lt.html',
    },
  ],
  summaryZh: `本文件徹底改變天主教對其他基督宗派的態度，從「分離弟兄」（fratres seiuncti）的牧靈用語、承認非天主教共同體在某種意義上的「教會性」、肯定共同祈禱與神學對話。是 1995 年若望保祿二世《Ut Unum Sint》通諭的根基。`,
  notes: `後續具體化：1965 年取消東西教會 1054 互革除（共同宣言）；1973 與科普特、1984 與敘利亞正教、1994 與亞述東方教會等系列共同基督論宣言；1999 與信義宗 JDDJ。`,
  related: ['vatican-ii-oe-orientalium-ecclesiarum', 'vatican-ii-na-nostra-aetate', 'vatican-ii-dh-dignitatis-humanae'],
}
