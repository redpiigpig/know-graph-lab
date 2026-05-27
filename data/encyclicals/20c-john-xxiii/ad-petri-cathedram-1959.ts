import type { PapalDocument } from '../types'

export const adPetriCathedram1959: PapalDocument = {
  slug: 'ad-petri-cathedram-1959',
  popeSlug: 'john-xxiii',
  category: 'encyclical',
  titleLat: 'Ad Petri Cathedram',
  titleEn: 'To the Chair of Peter',
  titleZh: '《向伯多祿寶座》通諭 — 論真理、合一與和平',
  promulgationDate: '1959-06-29',
  century: 20,
  summaryZh: "若望二十三世第一道通諭，宣告其牧職以「真理、合一與和平」三主題為核心。本通諭首次公開提及「召開大公會議」的計畫，預告了梵二（1962-65）的籌備。",
  topics: ["合一運動", "和平", "梵二籌備"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "ad-petri-cathedram-1959-chinese",
      "source": "https://www.vatican.va/content/dam/john-xxiii/pdf/encyclicals/documents/hf_j-xxiii_enc_29061959_ad-petri_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "ad-petri-cathedram-1959-english",
      "source": "https://www.vatican.va/content/john-xxiii/en/encyclicals/documents/hf_j-xxiii_enc_29061959_ad-petri.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "ad-petri-cathedram-1959-latin",
      "source": "https://www.vatican.va/content/john-xxiii/la/encyclicals/documents/hf_j-xxiii_enc_29061959_ad-petri.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "ad-petri-cathedram-1959-italian",
      "source": "https://www.vatican.va/content/john-xxiii/it/encyclicals/documents/hf_j-xxiii_enc_29061959_ad-petri.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/john-xxiii/en/encyclicals/documents/hf_j-xxiii_enc_29061959_ad-petri.html',
  notes: "簽署日 1959-06-29 為聖伯多祿與聖保祿瞻禮，是 1959-01-25 若望二十三宣告召開梵二後的首道通諭。",
}
