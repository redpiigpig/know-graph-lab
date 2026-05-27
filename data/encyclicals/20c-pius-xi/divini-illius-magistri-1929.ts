import type { PapalDocument } from '../types'

export const diviniIlliusMagistri1929: PapalDocument = {
  slug: 'divini-illius-magistri-1929',
  popeSlug: 'pius-xi',
  category: 'encyclical',
  titleLat: 'Divini Illius Magistri',
  titleEn: 'On Christian Education',
  titleZh: '《那位神聖導師》通諭 — 論基督徒教育',
  promulgationDate: '1929-12-31',
  century: 20,
  summaryZh: "碧岳十一世論教育的系統性通諭。提出教育的三主體說：家庭（首要）、教會（補充）、國家（輔助），警告國家過度介入教育（針對當時義大利墨索里尼、德國威瑪共和國的世俗化教育政策）。",
  topics: ["教育神學", "家庭", "國家權力", "世俗化"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "divini-illius-magistri-1929-chinese",
      "source": "https://www.vatican.va/content/dam/pius-xi/pdf/encyclicals/documents/hf_p-xi_enc_31121929_divini-illius-magistri_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "divini-illius-magistri-1929-english",
      "source": "https://www.vatican.va/content/pius-xi/en/encyclicals/documents/hf_p-xi_enc_31121929_divini-illius-magistri.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "divini-illius-magistri-1929-latin",
      "source": "https://www.vatican.va/content/pius-xi/la/encyclicals/documents/hf_p-xi_enc_31121929_divini-illius-magistri.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "divini-illius-magistri-1929-italian",
      "source": "https://www.vatican.va/content/pius-xi/it/encyclicals/documents/hf_p-xi_enc_31121929_divini-illius-magistri.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-xi/en/encyclicals/documents/hf_p-xi_enc_31121929_divini-illius-magistri.html',
  notes: "",
}
