import type { PapalDocument } from '../types'

export const laboremExercens1981: PapalDocument = {
  slug: 'laborem-exercens-1981',
  popeSlug: 'john-paul-ii',
  category: 'encyclical',
  titleLat: 'Laborem Exercens',
  titleEn: 'On Human Work',
  titleZh: '《論人的工作》通諭',
  promulgationDate: '1981-09-14',
  century: 20,
  summaryZh: "若望保祿二世第三道通諭，紀念良十三《新事》通諭頒布 90 週年。本通諭把「人的工作」（labor）置於天主教社會訓導核心。\n\n核心命題：「工作的主體面向」（dimensio subiectiva）優先於「客體面向」（dimensio obiectiva）。即工作的價值不在於產品（資本主義邏輯）也不在於階級鬥爭（馬克思邏輯），而在於工人作為「位格」（persona）的尊嚴。",
  topics: ["社會訓導", "工作神學", "人位格", "資本主義批判", "馬克思批判"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "laborem-exercens-1981-chinese",
      "source": "https://www.vatican.va/content/dam/john-paul-ii/pdf/encyclicals/documents/hf_jp-ii_enc_14091981_laborem-exercens_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "laborem-exercens-1981-english",
      "source": "https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_14091981_laborem-exercens.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "laborem-exercens-1981-latin",
      "source": "https://www.vatican.va/content/john-paul-ii/la/encyclicals/documents/hf_jp-ii_enc_14091981_laborem-exercens.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "laborem-exercens-1981-italian",
      "source": "https://www.vatican.va/content/john-paul-ii/it/encyclicals/documents/hf_jp-ii_enc_14091981_laborem-exercens.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_14091981_laborem-exercens.html',
  notes: "簽署日 1981-09-14 為紀念《新事》通諭頒布 90 週年（1891-05-15），但因若望保祿二世 1981-05-13 槍擊案受傷需康復，原訂 5 月頒布延後至 9 月。",
}
