import type { Creed } from '../types'
// @ts-expect-error — Vite raw-text import
import latText from './vatican-ii/pc-latin.txt?raw'
// @ts-expect-error — Vite raw-text import
import enText from './vatican-ii/pc-english.txt?raw'

export const vaticanIIPC: Creed = {
  slug: 'vatican-ii-pc-perfectae-caritatis',
  category: 'ecumenical-council',
  councilNo: 21,
  councilDocCode: 'PC',
  councilDocOrder: 7,
  order: 2107,
  nameZh: '修會生活革新法令',
  nameEn: 'Decree on the Adaptation and Renewal of Religious Life',
  nameLat: 'Perfectae Caritatis',
  year: 1965,
  location: '羅馬‧聖伯多祿大殿（梵二第四會期）',
  topic: '天主教修會（本篤、方濟、道明、耶穌會等）的會憲、靈修、生活方式革新原則',
  authors: [
    '教宗保祿六世（Paul VI）頒佈',
  ],
  acceptedBy: ['catholic'],
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '思高／天主教中文版（vatican.va 官方繁體 PDF）',
      text: '待補：vatican.va 中文版為 PDF 檔，需手動下載抽字後填入。\n下載：https://www.vatican.va/chinese/concilio/vat-ii_perfectae-caritatis_zh-t.pdf',
      source: 'https://www.vatican.va/chinese/concilio/vat-ii_perfectae-caritatis_zh-t.pdf',
      translator: '台灣地區主教團 / 香港教區禮儀委員會',
      placeholder: true,
    },
    {
      lang: 'en',
      label: 'Vatican official English translation',
      text: enText as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decree_19651028_perfectae-caritatis_en.html',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina',
      text: latText as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decree_19651028_perfectae-caritatis_lt.html',
    },
  ],
  summaryZh: `本文件要求所有修會「回到創會神恩」（aggiornamento ad fontes）並對應現代世界更新會憲。直接後果是 1960s-70s 大批修會修訂會憲（如耶穌會 1974 GC32、本篤會 1967 修訂會規詮釋），改革派與保守派衝突激烈，許多修會聖召銳減。`,
  notes: `與《教會憲章》第六章修會章節互補。`,
  related: ['vatican-ii-lg-lumen-gentium'],
}
