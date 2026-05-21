import type { Creed } from '../types'
// @ts-expect-error — Vite raw-text import (provided by vite/client at runtime)
import scLatin from './vatican-ii/sc-latin.txt?raw'
// @ts-expect-error — Vite raw-text import
import scEnglish from './vatican-ii/sc-english.txt?raw'
// @ts-expect-error — Vite raw-text import
import scChinese from './vatican-ii/sc-chinese.txt?raw'

export const vaticanIISC: Creed = {
  slug: 'vatican-ii-sc-sacrosanctum-concilium',
  category: 'ecumenical-council',
  councilNo: 21,
  councilDocCode: 'SC',
  councilDocOrder: 1,
  order: 2101,
  nameZh: '禮儀憲章',
  nameEn: 'Constitution on the Sacred Liturgy',
  nameLat: 'Sacrosanctum Concilium',
  year: 1963,
  location: '羅馬‧聖伯多祿大殿（梵蒂岡第二屆大公會議第二會期）',
  topic: '禮儀改革總綱：拉丁禮可用本地語言、聖經朗讀更廣、會眾主動參與、聖事禮儀重整、聖頌禮儀架構調整 — 開啟現代天主教禮儀全面更新',
  authors: [
    '教宗保祿六世（Paul VI）頒佈',
    '禮儀委員會主席：Larraona 樞機',
    '主要起草者：Annibale Bugnini 等',
  ],
  acceptedBy: ['catholic'],
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '思高／天主教中文版（vatican.va 官方繁體 PDF 抽字）',
      text: scChinese as string,
      source: 'https://www.vatican.va/chinese/concilio/vat-ii_sacrosanctum-concilium_zh-t.pdf',
      translator: '台灣地區主教團 / 香港教區禮儀委員會',
    },
    {
      lang: 'en',
      label: 'Vatican official English translation',
      text: scEnglish as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_const_19631204_sacrosanctum-concilium_en.html',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina',
      text: scLatin as string,
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_const_19631204_sacrosanctum-concilium_lt.html',
    },
  ],
  summaryZh: `《禮儀憲章》（Sacrosanctum Concilium，簡稱 SC）於 1963 年 12 月 4 日由教宗保祿六世頒佈，是梵蒂岡第二屆大公會議通過的第一份重要文件，也是現代天主教禮儀改革的根本綱領。

本文件 130 段，分七章：① 總綱（禮儀的本質與在教會生活的地位、禮儀教育、禮儀的革新）② 至聖聖體聖事（彌撒禮儀改革）③ 其他聖事與聖儀 ④ 日課（時辰禮儀）⑤ 禮儀年 ⑥ 聖樂 ⑦ 聖藝與禮儀用品。

最關鍵的突破：① 允許在彌撒、聖事禮儀中使用「本地語言」（vernacular），結束自 Trent 以來四百年純拉丁禮的傳統 ② 強調信徒「主動、有意識、有效的參與」（plena, conscia atque actuosa participatio）③ 重整聖經朗讀，使聖經寶藏更豐富地展現給信眾 ④ 開放公教禮儀向地方文化適應（accommodatio / inculturation）。

直接後果是 Novus Ordo Missae（保祿六世新彌撒禮 1969）的誕生與本地禮儀本的編譯。對其他基督宗派的禮儀復興（聖公會 1979 BCP、信義會 LBW 等）也產生顯著外溢影響。`,
  notes: `- 表決：本文件最終以 2147 贊成 vs 4 反對通過（1963-12-04），是梵二最具共識的文件
- 歷史脈絡：1950 年代以 Jungmann、Bouyer、Bugnini 為代表的「禮儀運動」為其鋪路
- 後續實施：1969 Missale Romanum / 1971 Liturgia Horarum / 1972 RCIA / 1973 Rite of Penance 等系列新禮典
- 拉丁禮 vs 特倫多禮：本文件並未廢止拉丁特倫多禮，2007 教宗本篤十六世以《Summorum Pontificum》確認其續用權；2021 教宗方濟各《Traditionis Custodes》再度收緊
- 中文官方譯本由台灣地區主教團與香港教區禮儀委員會合譯，於 vatican.va 中文版發布`,
  related: [
    'vatican-ii-lg-lumen-gentium',
    'vatican-ii-dv-dei-verbum',
    'vatican-ii-im-inter-mirifica',
  ],
}
