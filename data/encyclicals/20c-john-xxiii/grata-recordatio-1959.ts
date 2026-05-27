import type { PapalDocument } from '../types'

export const grataRecordatio1959: PapalDocument = {
  slug: 'grata-recordatio-1959',
  popeSlug: 'john-xxiii',
  category: 'encyclical',
  titleLat: 'Grata Recordatio',
  titleEn: 'On the Rosary',
  titleZh: '《愉悅的紀念》通諭 — 論玫瑰經',
  promulgationDate: '1959-09-26',
  century: 20,
  summaryZh: "若望二十三世第三道通諭，呼籲在 10 月玫瑰經月以玫瑰經為梵二籌備、為和平、為亞洲非洲傳教祈禱。",
  topics: ["玫瑰經", "聖母敬禮", "梵二籌備"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "grata-recordatio-1959-chinese",
      "source": "https://www.vatican.va/content/dam/john-xxiii/pdf/encyclicals/documents/hf_j-xxiii_enc_26091959_grata-recordatio_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "grata-recordatio-1959-english",
      "source": "https://www.vatican.va/content/john-xxiii/en/encyclicals/documents/hf_j-xxiii_enc_26091959_grata-recordatio.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "grata-recordatio-1959-latin",
      "source": "https://www.vatican.va/content/john-xxiii/la/encyclicals/documents/hf_j-xxiii_enc_26091959_grata-recordatio.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "grata-recordatio-1959-italian",
      "source": "https://www.vatican.va/content/john-xxiii/it/encyclicals/documents/hf_j-xxiii_enc_26091959_grata-recordatio.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/john-xxiii/en/encyclicals/documents/hf_j-xxiii_enc_26091959_grata-recordatio.html',
  notes: "",
}
