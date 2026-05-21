import type { Creed } from '../types'
// @ts-expect-error — Vite raw-text import
import latText from './vatican-ii/lg-latin.txt?raw'
// @ts-expect-error — Vite raw-text import
import enText from './vatican-ii/lg-english.txt?raw'

export const vaticanIILG: Creed = {
  slug: 'vatican-ii-lg-lumen-gentium',
  category: 'ecumenical-council',
  councilNo: 21,
  councilDocCode: 'LG',
  councilDocOrder: 3,
  order: 2103,
  nameZh: '教會憲章',
  nameEn: 'Dogmatic Constitution on the Church',
  nameLat: 'Lumen Gentium',
  year: 1964,
  location: '羅馬‧聖伯多祿大殿（梵二第三會期）',
  topic: '教會本質、結構、職能 — 8 章涵蓋天主子民、主教團、平信徒、修會、教會的末世性、聖母瑪利亞',
  authors: [
    '教宗保祿六世（Paul VI）頒佈',
  ],
  acceptedBy: ['catholic'],
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '思高／天主教中文版（vatican.va 官方繁體 PDF）',
      text: '待補：vatican.va 中文版為 PDF 檔，需手動下載抽字後填入。\n下載：https://www.vatican.va/chinese/concilio/vat-ii_lumen-gentium_zh-t.pdf',
      source: 'https://www.vatican.va/chinese/concilio/vat-ii_lumen-gentium_zh-t.pdf',
      translator: '台灣地區主教團 / 香港教區禮儀委員會',
      placeholder: true,
    },
    {
      lang: 'en',
      label: 'Vatican official English translation',
      text: enText as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_const_19641121_lumen-gentium_en.html',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina',
      text: latText as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_const_19641121_lumen-gentium_lt.html',
    },
  ],
  summaryZh: `1964 年 11 月 21 日頒佈，是梵二最具神學份量的文件，與《啟示憲章》《禮儀憲章》《牧靈憲章》並列四大憲章。最重要的突破：① 教會自我定義從「完美社會」轉向「天主子民」（Chapter 2）② 確立主教團與教宗共同治理教會的「合議性」（collegiality, Chapter 3, §22）③ 平信徒在教會內的「使徒性」地位（Chapter 4）④ 普世聖召（universal call to holiness, Chapter 5）⑤ 第八章專論聖母瑪利亞，不另立獨立文件。`,
  notes: `Nota explicativa praevia（前置說明）— 為平衡主教合議性與教宗首席地位，保祿六世下令加入此「前置註解」附於文件之後，是當時神學辯論的關鍵折衷產物。`,
  related: ['vatican-ii-sc-sacrosanctum-concilium', 'vatican-ii-dv-dei-verbum', 'vatican-ii-gs-gaudium-et-spes'],
}
