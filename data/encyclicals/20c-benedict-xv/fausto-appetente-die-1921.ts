import type { PapalDocument } from '../types'

export const faustoAppetenteDie1921: PapalDocument = {
  slug: 'fausto-appetente-die-1921',
  popeSlug: 'benedict-xv',
  category: 'encyclical',
  titleLat: 'Fausto Appetente Die',
  titleEn: 'On St. Dominic',
  titleZh: '《吉日將臨》通諭 — 紀念聖道明逝世 700 週年',
  promulgationDate: '1921-06-29',
  century: 20,
  summaryZh: "本篤十五世紀念聖道明（Dominic Guzmán, 1170-1221，道明會創辦人）逝世 700 週年的通諭。回顧道明會在中世紀對抗 Albigensian 異端、推動神學研究（聖多瑪斯‧阿奎那為道明會士）的歷史貢獻。",
  topics: ["聖道明", "道明會", "中世紀神學", "Albigensian"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "fausto-appetente-die-1921-chinese",
      "source": "https://www.vatican.va/content/dam/benedict-xv/pdf/encyclicals/documents/hf_ben-xv_enc_29061921_fausto-appetente-die_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "fausto-appetente-die-1921-english",
      "source": "https://www.vatican.va/content/benedict-xv/en/encyclicals/documents/hf_ben-xv_enc_29061921_fausto-appetente-die.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "fausto-appetente-die-1921-latin",
      "source": "https://www.vatican.va/content/benedict-xv/la/encyclicals/documents/hf_ben-xv_enc_29061921_fausto-appetente-die.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "fausto-appetente-die-1921-italian",
      "source": "https://www.vatican.va/content/benedict-xv/it/encyclicals/documents/hf_ben-xv_enc_29061921_fausto-appetente-die.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/benedict-xv/en/encyclicals/documents/hf_ben-xv_enc_29061921_fausto-appetente-die.html',
  notes: "簽署日 1921-06-29 為聖伯多祿與聖保祿瞻禮。本通諭是本篤十五世最後一道通諭——他於 1922-01-22 辭世。",
}
