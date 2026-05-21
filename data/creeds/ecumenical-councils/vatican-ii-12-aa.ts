import type { Creed } from '../types'
// @ts-expect-error — Vite raw-text import
import latText from './vatican-ii/aa-latin.txt?raw'
// @ts-expect-error — Vite raw-text import
import enText from './vatican-ii/aa-english.txt?raw'

export const vaticanIIAA: Creed = {
  slug: 'vatican-ii-aa-apostolicam-actuositatem',
  category: 'ecumenical-council',
  councilNo: 21,
  councilDocCode: 'AA',
  councilDocOrder: 12,
  order: 2112,
  nameZh: '教友傳教法令',
  nameEn: 'Decree on the Apostolate of the Laity',
  nameLat: 'Apostolicam Actuositatem',
  year: 1965,
  location: '羅馬‧聖伯多祿大殿（梵二第四會期）',
  topic: '平信徒在教會內外的使徒性使命：堂區、職場、家庭、社會行動、政治參與',
  authors: [
    '教宗保祿六世（Paul VI）頒佈',
  ],
  acceptedBy: ['catholic'],
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '思高／天主教中文版（vatican.va 官方繁體 PDF）',
      text: '待補：vatican.va 中文版為 PDF 檔，需手動下載抽字後填入。\n下載：https://www.vatican.va/chinese/concilio/vat-ii_apostolicam-actuositatem_zh-t.pdf',
      source: 'https://www.vatican.va/chinese/concilio/vat-ii_apostolicam-actuositatem_zh-t.pdf',
      translator: '台灣地區主教團 / 香港教區禮儀委員會',
      placeholder: true,
    },
    {
      lang: 'en',
      label: 'Vatican official English translation',
      text: enText as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decree_19651118_apostolicam-actuositatem_en.html',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina',
      text: latText as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decree_19651118_apostolicam-actuositatem_lt.html',
    },
  ],
  summaryZh: `本文件徹底改變天主教對「平信徒」的角色定位 — 不再是「神職的協助者」，而是因聖洗本身就有的「使徒性聖召」（apostolate by virtue of baptism）。後續神學發展：1988 若望保祿二世《Christifideles Laici》宗座勸諭。`,
  notes: `後續具體建制：堂區牧靈委員會、教區牧靈委員會、各國平信徒大會、Catholic Action 等運動的合法化。`,
  related: ['vatican-ii-lg-lumen-gentium'],
}
