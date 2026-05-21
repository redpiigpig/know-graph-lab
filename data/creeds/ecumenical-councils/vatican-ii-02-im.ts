import type { Creed } from '../types'
// @ts-expect-error — Vite raw-text import
import latText from './vatican-ii/im-latin.txt?raw'
// @ts-expect-error — Vite raw-text import
import enText from './vatican-ii/im-english.txt?raw'

export const vaticanIIIM: Creed = {
  slug: 'vatican-ii-im-inter-mirifica',
  category: 'ecumenical-council',
  councilNo: 21,
  councilDocCode: 'IM',
  councilDocOrder: 2,
  order: 2102,
  nameZh: '大眾傳播工具法令',
  nameEn: 'Decree on the Media of Social Communications',
  nameLat: 'Inter Mirifica',
  year: 1963,
  location: '羅馬‧聖伯多祿大殿（梵二第二會期）',
  topic: '教會對廣播、電視、電影、報刊等大眾傳播工具的態度與牧民方針',
  authors: [
    '教宗保祿六世（Paul VI）頒佈',
  ],
  acceptedBy: ['catholic'],
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '思高／天主教中文版（vatican.va 官方繁體 PDF）',
      text: '待補：vatican.va 中文版為 PDF 檔，需手動下載抽字後填入。\n下載：https://www.vatican.va/chinese/concilio/vat-ii_inter-mirifica_zh-t.pdf',
      source: 'https://www.vatican.va/chinese/concilio/vat-ii_inter-mirifica_zh-t.pdf',
      translator: '台灣地區主教團 / 香港教區禮儀委員會',
      placeholder: true,
    },
    {
      lang: 'en',
      label: 'Vatican official English translation',
      text: enText as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decree_19631204_inter-mirifica_en.html',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina',
      text: latText as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decree_19631204_inter-mirifica_lt.html',
    },
  ],
  summaryZh: `1963 年 12 月 4 日與《禮儀憲章》同日頒佈。梵二爭議較少、票數差距較大的文件之一（1960 反 vs 164 贊成 — 反對票相對偏高），批評者認為內容偏淺、未及神學深度。但首次以教會官方文件層級肯定大眾傳播工具的價值。`,
  notes: `後續 1971 牧靈訓令《Communio et Progressio》具體展開本文件原則；1992《Aetatis Novae》再更新。`,
  related: ['vatican-ii-sc-sacrosanctum-concilium'],
}
