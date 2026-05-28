import type { PapalDocument } from '../types'

export const inPraeclaraSummorum1921: PapalDocument = {
  slug: 'in-praeclara-summorum-1921',
  popeSlug: 'benedict-xv',
  category: 'encyclical',
  titleLat: 'In Praeclara Summorum',
  titleEn: 'On Dante',
  titleZh: '《在傑出》通諭 — 紀念但丁逝世 600 週年',
  promulgationDate: '1921-04-30',
  century: 20,
  summaryZh: "本篤十五世紀念義大利詩人但丁（Dante Alighieri, 1265-1321）逝世 600 週年的通諭。本通諭是天主教史上首道、亦是少數以「俗世詩人作品」為主題的通諭。\n\n肯定《神曲》作為「天主教詩學的最高成就」，並把但丁定位為「中世紀經院神學的詩化表達」。",
  topics: ["但丁", "神曲", "天主教文學", "中世紀文化"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "in-praeclara-summorum-1921-chinese",
      "source": "https://www.vatican.va/content/dam/benedict-xv/pdf/encyclicals/documents/hf_ben-xv_enc_30041921_in-praeclara-summorum_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "in-praeclara-summorum-1921-english",
      "source": "https://www.vatican.va/content/benedict-xv/en/encyclicals/documents/hf_ben-xv_enc_30041921_in-praeclara-summorum.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "in-praeclara-summorum-1921-latin",
      "source": "https://www.vatican.va/content/benedict-xv/la/encyclicals/documents/hf_ben-xv_enc_30041921_in-praeclara-summorum.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "in-praeclara-summorum-1921-italian",
      "source": "https://www.vatican.va/content/benedict-xv/it/encyclicals/documents/hf_ben-xv_enc_30041921_in-praeclara-summorum.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/benedict-xv/en/encyclicals/documents/hf_ben-xv_enc_30041921_in-praeclara-summorum.html',
  notes: "本通諭預示了若望保祿二世對「天主教文化／藝術」的重視傳統。",
}
