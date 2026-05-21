import type { Creed } from '../types'
// @ts-expect-error — Vite raw-text import
import latText from './vatican-ii/na-latin.txt?raw'
// @ts-expect-error — Vite raw-text import
import enText from './vatican-ii/na-english.txt?raw'
// @ts-expect-error — Vite raw-text import
import zhText from './vatican-ii/na-chinese.txt?raw'

export const vaticanIINA: Creed = {
  slug: 'vatican-ii-na-nostra-aetate',
  category: 'ecumenical-council',
  councilNo: 21,
  councilDocCode: 'NA',
  councilDocOrder: 10,
  order: 2110,
  nameZh: '教會對非基督宗教態度宣言',
  nameEn: 'Declaration on the Relation of the Church to Non-Christian Religions',
  nameLat: 'Nostra Aetate',
  year: 1965,
  location: '羅馬‧聖伯多祿大殿（梵二第四會期）',
  topic: '天主教對印度教、佛教、伊斯蘭教、猶太教的態度 — 特別著名的是第 4 段否認集體性「猶太人殺基督」指控、譴責任何形式的反猶太主義',
  authors: [
    '教宗保祿六世（Paul VI）頒佈',
  ],
  acceptedBy: ['catholic'],
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '思高／天主教中文版（vatican.va 官方繁體 PDF 抽字）',
      text: zhText as string,
      source: 'https://www.vatican.va/chinese/concilio/vat-ii_nostra-aetate_zh-t.pdf',
      translator: '台灣地區主教團 / 香港教區禮儀委員會',
    },
    {
      lang: 'en',
      label: 'Vatican official English translation',
      text: enText as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decl_19651028_nostra-aetate_en.html',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina',
      text: latText as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_decl_19651028_nostra-aetate_lt.html',
    },
  ],
  summaryZh: `本文件僅 5 段，是梵二最短文件之一，但歷史意義巨大：第 4 段徹底改變天主教與猶太教關係（後續對話常稱「梵二後猶太關係」分水嶺），第 3 段首次以官方文件層級正面承認伊斯蘭教與基督宗教共享亞伯拉罕信仰根源。亦肯定佛教、印度教的精神追求價值。`,
  notes: `1974 設立「與猶太教關係委員會」；1986 若望保祿二世訪問羅馬大會堂（首位現代教宗）；2000 千禧大赦時 mea culpa；後續宗教對話運動的根基。`,
  related: ['vatican-ii-ur-unitatis-redintegratio', 'vatican-ii-dh-dignitatis-humanae'],
}
