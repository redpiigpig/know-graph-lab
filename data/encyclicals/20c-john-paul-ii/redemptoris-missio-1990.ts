import type { PapalDocument } from '../types'

export const redemptorisMissio1990: PapalDocument = {
  slug: 'redemptoris-missio-1990',
  popeSlug: 'john-paul-ii',
  category: 'encyclical',
  titleLat: 'Redemptoris Missio',
  titleEn: 'Mission of the Redeemer',
  titleZh: '《救主使命》通諭 — 論教會傳教使命的永久性',
  promulgationDate: '1990-12-07',
  century: 20,
  summaryZh: "若望保祿二世第八道通諭，紀念梵二《教會傳教工作》法令（Ad Gentes 1965）頒布 25 週年。\n\n通諭重申「ad gentes」（向萬民）傳教仍是教會使命的核心，反駁戰後神學中「對話取代傳教」「救恩多元主義」的傾向。第 55 段提出「對話與宣告」兩者並行不悖：傳教是「對話」、「人類進步」、「文化／宗教交談」的更廣脈絡，但宣告基督依然不可省略。",
  topics: ["傳教使命", "梵二接續", "ad gentes", "宗教對話", "救恩論"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "redemptoris-missio-1990-chinese",
      "source": "https://www.vatican.va/content/dam/john-paul-ii/pdf/encyclicals/documents/hf_jp-ii_enc_07121990_redemptoris-missio_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "redemptoris-missio-1990-english",
      "source": "https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_07121990_redemptoris-missio.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "redemptoris-missio-1990-latin",
      "source": "https://www.vatican.va/content/john-paul-ii/la/encyclicals/documents/hf_jp-ii_enc_07121990_redemptoris-missio.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "redemptoris-missio-1990-italian",
      "source": "https://www.vatican.va/content/john-paul-ii/it/encyclicals/documents/hf_jp-ii_enc_07121990_redemptoris-missio.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_07121990_redemptoris-missio.html',
  notes: "簽署日 1990-12-07 是梵二《教會傳教工作》法令頒布 25 週年（1965-12-07）。",
}
