import type { PapalDocument } from '../types'

export const sacerdotiiNostriPrimordia1959: PapalDocument = {
  slug: 'sacerdotii-nostri-primordia-1959',
  popeSlug: 'john-xxiii',
  category: 'encyclical',
  titleLat: 'Sacerdotii Nostri Primordia',
  titleEn: 'On the Hundredth Anniversary of the Death of the Curé of Ars',
  titleZh: '《我們司鐸職的初衷》通諭 — 紀念聖維雅納本堂逝世 100 週年',
  promulgationDate: '1959-08-01',
  century: 20,
  summaryZh: "若望二十三世第二道通諭，紀念聖若翰‧維雅納本堂神父（Saint Jean-Marie Vianney, 1786-1859，亞爾斯本堂）逝世 100 週年。維雅納是天主教本堂神父及聽告解司鐸的主保聖人。",
  topics: ["聖維雅納", "司鐸聖召", "牧靈職"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "sacerdotii-nostri-primordia-1959-chinese",
      "source": "https://www.vatican.va/content/dam/john-xxiii/pdf/encyclicals/documents/hf_j-xxiii_enc_19590801_sacerdotii_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "sacerdotii-nostri-primordia-1959-english",
      "source": "https://www.vatican.va/content/john-xxiii/en/encyclicals/documents/hf_j-xxiii_enc_19590801_sacerdotii.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "sacerdotii-nostri-primordia-1959-latin",
      "source": "https://www.vatican.va/content/john-xxiii/la/encyclicals/documents/hf_j-xxiii_enc_19590801_sacerdotii.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "sacerdotii-nostri-primordia-1959-italian",
      "source": "https://www.vatican.va/content/john-xxiii/it/encyclicals/documents/hf_j-xxiii_enc_19590801_sacerdotii.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/john-xxiii/en/encyclicals/documents/hf_j-xxiii_enc_19590801_sacerdotii.html',
  notes: "",
}
