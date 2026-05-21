import type { Creed } from '../types'

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
      text: '',
      textKey: 'sc-chinese',
      source: 'https://www.vatican.va/chinese/concilio/vat-ii_sacrosanctum-concilium_zh-t.pdf',
      translator: '台灣地區主教團 / 香港教區禮儀委員會',
    },
    {
      lang: 'en',
      label: 'Vatican official English translation',
      text: '',
      textKey: 'sc-english',
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_const_19631204_sacrosanctum-concilium_en.html',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina',
      text: '',
      textKey: 'sc-latin',
      source: 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_const_19631204_sacrosanctum-concilium_lt.html',
    },
  ],
  summaryZh: `《禮儀憲章》是梵蒂岡第二屆大公會議最早通過、也是最具共識的文件，被視為現代天主教禮儀改革的奠基綱領。1963 年 12 月 4 日由教宗保祿六世於梵二第二會期落幕之日頒佈，最終以 2147 票贊成、4 票反對通過，距特倫多會議（1545-63）將彌撒禮儀凍結於拉丁文恰好四百年。

全文共 130 段，分七章 — 總則、彌撒、其他聖事與聖儀、時辰禮儀、禮儀年、聖樂、聖藝與禮儀用品 — 從理論基礎到具體規範一應俱全。它的醞釀並非偶然，而是二十世紀「禮儀運動」（Liturgical Movement）半世紀沉澱的結晶，背後可追溯至本篤會學者 Lambert Beauduin、Odo Casel、Romano Guardini、Josef A. Jungmann 等人的研究。

最關鍵的四項突破：其一，允許彌撒與聖事使用本地語言（vernacular），終結拉丁禮獨佔禮儀的四百年局面；其二，強調信徒應「主動、有意識、有效地參與」（plena, conscia atque actuosa participatio），扭轉中世紀以來神職與會眾之間的禮儀隔閡；其三，擴展讀經量，使聖經寶藏「更豐富地」展現於信眾面前（thesauros biblicos largius aperire）；其四，開啟禮儀的「本地文化適應」（accommodatio / inculturation），肯定各民族文化的禮儀表達。

直接後果是 1969 年保祿六世頒佈 Novus Ordo Missae（新禮彌撒）、1971 年新《時辰禮儀》、1972 年成人入門禮（RCIA）等一系列新禮典；對聖公會 1979 年《公禱書》（BCP）、信義會《禮儀崇拜書》（LBW）等基督宗派的禮儀復興，亦產生顯著外溢影響。`,
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
