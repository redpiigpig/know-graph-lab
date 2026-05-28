import type { PapalDocument } from '../types'

export const vehementerNos1906: PapalDocument = {
  slug: 'vehementer-nos-1906',
  popeSlug: 'pius-x',
  category: 'encyclical',
  titleLat: 'Vehementer Nos',
  titleEn: 'On the French Law of Separation',
  titleZh: '《我們強烈》通諭 — 論法國 1905 政教分離法',
  promulgationDate: '1906-02-11',
  century: 20,
  summaryZh: "碧岳十世明確譴責法國 1905-12-09 通過的「政教分離法」（Loi de séparation des Églises et de l'État）的通諭。法國革命百年後正式廢除拿破崙與庇護七世簽訂的政教協定（Concordat 1801），單方面剝奪教會財產與法律地位。\n\n本通諭定下天主教對「世俗國家絕對主義」（laïcisme）的批判性立場——這項立場後在梵二《信仰自由宣言》（Dignitatis Humanae 1965）獲得實質性的更新。",
  topics: ["法國政教分離", "教會與國家", "laïcité 批判", "Concordat"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "vehementer-nos-1906-chinese",
      "source": "https://www.vatican.va/content/dam/pius-x/pdf/encyclicals/documents/hf_p-x_enc_11021906_vehementer-nos_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "vehementer-nos-1906-english",
      "source": "https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_11021906_vehementer-nos.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "vehementer-nos-1906-latin",
      "source": "https://www.vatican.va/content/pius-x/la/encyclicals/documents/hf_p-x_enc_11021906_vehementer-nos.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "vehementer-nos-1906-italian",
      "source": "https://www.vatican.va/content/pius-x/it/encyclicals/documents/hf_p-x_enc_11021906_vehementer-nos.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_11021906_vehementer-nos.html',
  notes: "",
}
