import type { PapalDocument } from '../types'

export const evangeliiPraecones1951: PapalDocument = {
  slug: 'evangelii-praecones-1951',
  popeSlug: 'pius-xii',
  category: 'encyclical',
  titleLat: 'Evangelii Praecones',
  titleEn: 'On Promotion of Catholic Missions',
  titleZh: '《福音傳教士》通諭 — 論促進天主教傳教事業',
  promulgationDate: '1951-06-02',
  century: 20,
  summaryZh: "碧岳十二世關於傳教的通諭，紀念本篤十五《最大的事》（Maximum Illud 1919）頒布 30 週年。重申「本地化」（inculturatio）原則：傳教不是西方文化的延伸，而是要在各地建立本地神職、本地教會。",
  topics: ["傳教神學", "本地化", "本地神職"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "evangelii-praecones-1951-chinese",
      "source": "https://www.vatican.va/content/dam/pius-xii/pdf/encyclicals/documents/hf_p-xii_enc_02061951_evangelii-praecones_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "evangelii-praecones-1951-english",
      "source": "https://www.vatican.va/content/pius-xii/en/encyclicals/documents/hf_p-xii_enc_02061951_evangelii-praecones.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "evangelii-praecones-1951-latin",
      "source": "https://www.vatican.va/content/pius-xii/la/encyclicals/documents/hf_p-xii_enc_02061951_evangelii-praecones.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "evangelii-praecones-1951-italian",
      "source": "https://www.vatican.va/content/pius-xii/it/encyclicals/documents/hf_p-xii_enc_02061951_evangelii-praecones.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-xii/en/encyclicals/documents/hf_p-xii_enc_02061951_evangelii-praecones.html',
  notes: "",
}
