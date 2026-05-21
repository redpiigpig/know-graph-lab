import type { Creed } from '../types'
// @ts-expect-error — Vite raw-text import
import latText from './vatican-ii/po-latin.txt?raw'
// @ts-expect-error — Vite raw-text import
import enText from './vatican-ii/po-english.txt?raw'

export const vaticanIIPO: Creed = {
  slug: 'vatican-ii-po-presbyterorum-ordinis',
  category: 'ecumenical-council',
  councilNo: 21,
  councilDocCode: 'PO',
  councilDocOrder: 15,
  order: 2115,
  nameZh: '司鐸職務與生活法令',
  nameEn: 'Decree on the Ministry and Life of Priests',
  nameLat: 'Presbyterorum Ordinis',
  year: 1965,
  location: '羅馬‧聖伯多祿大殿（梵二第四會期）',
  topic: '天主教司鐸（priests / presbyters）的職務、靈修生活、獨身、終身陶成、與主教及修生關係',
  authors: [
    '教宗保祿六世（Paul VI）頒佈',
  ],
  acceptedBy: ['catholic'],
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '思高／天主教中文版（vatican.va 官方繁體 PDF）',
      text: '待補：vatican.va 中文版為 PDF 檔，需手動下載抽字後填入。\n下載：https://www.vatican.va/chinese/concilio/vat-ii_presbyterorum-ordinis_zh-t.pdf',
      source: 'https://www.vatican.va/chinese/concilio/vat-ii_presbyterorum-ordinis_zh-t.pdf',
      translator: '台灣地區主教團 / 香港教區禮儀委員會',
      placeholder: true,
    },
    {
      lang: 'en',
      label: 'Vatican official English translation',
      text: enText as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decree_19651207_presbyterorum-ordinis_en.html',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina',
      text: latText as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decree_19651207_presbyterorum-ordinis_lt.html',
    },
  ],
  summaryZh: `本文件補充《教會憲章》的主教神學，集中討論「次於主教的司鐸職」。確認司鐸獨身為「至寶」但區別於聖事性必要（拉丁禮紀律）；強調司鐸的「兄弟團」（presbyterium）作為教會性建制；要求終身陶成。`,
  notes: `後續具體化：1992 若望保祿二世《Pastores Dabo Vobis》宗座勸諭、各地司鐸進修課程。`,
  related: ['vatican-ii-ot-optatam-totius', 'vatican-ii-lg-lumen-gentium'],
}
