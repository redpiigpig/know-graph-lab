import type { PapalDocument } from '../types'

export const sapientiaeChristianae1890: PapalDocument = {
  slug: 'sapientiae-christianae-1890',
  popeSlug: 'leo-xiii',
  category: 'encyclical',
  titleLat: 'Sapientiae Christianae',
  titleEn: 'On Christians as Citizens',
  titleZh: '《基督徒的智慧》通諭 — 論基督徒作為公民',
  promulgationDate: '1890-01-10',
  century: 19,
  summaryZh: "良十三世論基督徒公民責任的通諭。在歐洲世俗化背景下，論證基督徒在公民領域的責任不僅是「服從」也是「主動建構公正社會」。",
  topics: ["公民責任", "政教關係", "教會社會立場"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "sapientiae-christianae-1890-chinese",
      "source": "https://www.vatican.va/content/dam/leo-xiii/pdf/encyclicals/documents/hf_l-xiii_enc_10011890_sapientiae-christianae_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "sapientiae-christianae-1890-english",
      "source": "https://www.vatican.va/content/leo-xiii/en/encyclicals/documents/hf_l-xiii_enc_10011890_sapientiae-christianae.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "sapientiae-christianae-1890-latin",
      "source": "https://www.vatican.va/content/leo-xiii/la/encyclicals/documents/hf_l-xiii_enc_10011890_sapientiae-christianae.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "sapientiae-christianae-1890-italian",
      "source": "https://www.vatican.va/content/leo-xiii/it/encyclicals/documents/hf_l-xiii_enc_10011890_sapientiae-christianae.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/leo-xiii/en/encyclicals/documents/hf_l-xiii_enc_10011890_sapientiae-christianae.html',
  notes: "",
}
