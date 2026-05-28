import type { PapalDocument } from '../types'

export const humaniGenerisRedemptionem1917: PapalDocument = {
  slug: 'humani-generis-redemptionem-1917',
  popeSlug: 'benedict-xv',
  category: 'encyclical',
  titleLat: 'Humani Generis Redemptionem',
  titleEn: 'On Preaching the Word of God',
  titleZh: '《人類救贖》通諭 — 論講道',
  promulgationDate: '1917-06-15',
  century: 20,
  summaryZh: "本篤十五世論講道（praedicatio）的通諭。在一戰中期頒布，強調堂區講道作為牧靈的核心職分，警告反對華麗修辭、空洞演說、過度個人言論等不符宣講福音目的的講道方式。",
  topics: ["講道神學", "牧靈職分", "司鐸培育"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "humani-generis-redemptionem-1917-chinese",
      "source": "https://www.vatican.va/content/dam/benedict-xv/pdf/encyclicals/documents/hf_ben-xv_enc_15061917_humani-generis-redemptionem_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "humani-generis-redemptionem-1917-english",
      "source": "https://www.vatican.va/content/benedict-xv/en/encyclicals/documents/hf_ben-xv_enc_15061917_humani-generis-redemptionem.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "humani-generis-redemptionem-1917-latin",
      "source": "https://www.vatican.va/content/benedict-xv/la/encyclicals/documents/hf_ben-xv_enc_15061917_humani-generis-redemptionem.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "humani-generis-redemptionem-1917-italian",
      "source": "https://www.vatican.va/content/benedict-xv/it/encyclicals/documents/hf_ben-xv_enc_15061917_humani-generis-redemptionem.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/benedict-xv/en/encyclicals/documents/hf_ben-xv_enc_15061917_humani-generis-redemptionem.html',
  notes: "",
}
