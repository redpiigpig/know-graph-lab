import type { PapalDocument } from '../types'

export const singulariQuadam1912: PapalDocument = {
  slug: 'singulari-quadam-1912',
  popeSlug: 'pius-x',
  category: 'encyclical',
  titleLat: 'Singulari Quadam',
  titleEn: 'On Labor Organizations',
  titleZh: '《某種獨特》通諭 — 論德國勞工組織',
  promulgationDate: '1912-09-24',
  century: 20,
  summaryZh: "碧岳十世論德國勞工組織議題的通諭，處理 20 世紀初德國天主教徒是否可加入「跨宗派工會」（christliche Gewerkschaften，含基督新教徒）的爭議。准許天主教徒參與這類工會，但要求另設「天主教工人協會」（Katholische Arbeitervereine）以保障信仰實踐。",
  topics: ["勞工組織", "德國", "跨宗派合作", "社會訓導"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "singulari-quadam-1912-chinese",
      "source": "https://www.vatican.va/content/dam/pius-x/pdf/encyclicals/documents/hf_p-x_enc_24091912_singulari-quadam_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "singulari-quadam-1912-english",
      "source": "https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_24091912_singulari-quadam.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "singulari-quadam-1912-latin",
      "source": "https://www.vatican.va/content/pius-x/la/encyclicals/documents/hf_p-x_enc_24091912_singulari-quadam.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "singulari-quadam-1912-italian",
      "source": "https://www.vatican.va/content/pius-x/it/encyclicals/documents/hf_p-x_enc_24091912_singulari-quadam.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_24091912_singulari-quadam.html',
  notes: "",
}
