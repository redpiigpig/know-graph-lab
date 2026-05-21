import type { Creed } from '../types'
// @ts-expect-error — Vite raw-text import
import latText from './vatican-ii/dv-latin.txt?raw'
// @ts-expect-error — Vite raw-text import
import enText from './vatican-ii/dv-english.txt?raw'

export const vaticanIIDV: Creed = {
  slug: 'vatican-ii-dv-dei-verbum',
  category: 'ecumenical-council',
  councilNo: 21,
  councilDocCode: 'DV',
  councilDocOrder: 11,
  order: 2111,
  nameZh: '啟示憲章',
  nameEn: 'Dogmatic Constitution on Divine Revelation',
  nameLat: 'Dei Verbum',
  year: 1965,
  location: '羅馬‧聖伯多祿大殿（梵二第四會期）',
  topic: '啟示論：聖經與聖傳的關係、聖經默感與無謬性、聖經詮釋學原則、聖經在教會生活中的中心地位',
  authors: [
    '教宗保祿六世（Paul VI）頒佈',
  ],
  acceptedBy: ['catholic'],
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '思高／天主教中文版（vatican.va 官方繁體 PDF）',
      text: '待補：vatican.va 中文版為 PDF 檔，需手動下載抽字後填入。\n下載：https://www.vatican.va/chinese/concilio/vat-ii_dei-verbum_zh-t.pdf',
      source: 'https://www.vatican.va/chinese/concilio/vat-ii_dei-verbum_zh-t.pdf',
      translator: '台灣地區主教團 / 香港教區禮儀委員會',
      placeholder: true,
    },
    {
      lang: 'en',
      label: 'Vatican official English translation',
      text: enText as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_const_19651118_dei-verbum_en.html',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina',
      text: latText as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_const_19651118_dei-verbum_lt.html',
    },
  ],
  summaryZh: `1965 年 11 月 18 日頒佈，是梵二四大憲章之一。最關鍵突破：① 拒絕「兩源論」（聖經與聖傳為兩個獨立啟示源）改採「同一啟示之兩種傳承方式」（§9）② 肯定歷史批判方法的合法性（§12）③ 強調聖經應成為神學的「靈魂」與教會生活中心 ④ 鼓勵信徒閱讀聖經，鼓勵公版聖經多語翻譯（§22-25）。`,
  notes: `與 Trent 第四會期（1546 De canonicis Scripturis）對話：保留 Trent 對 deuterocanonical canon 的肯定，但詮釋學方法上大幅開放。也與梵一《Dei Filius》（1870）對話：保留客觀啟示概念，但加上「歷史性」維度。`,
  related: ['vatican-ii-sc-sacrosanctum-concilium', 'vatican-ii-lg-lumen-gentium'],
}
