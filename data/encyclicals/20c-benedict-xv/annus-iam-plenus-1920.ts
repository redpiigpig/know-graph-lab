import type { PapalDocument } from '../types'

export const annusIamPlenus1920: PapalDocument = {
  slug: 'annus-iam-plenus-1920',
  popeSlug: 'benedict-xv',
  category: 'encyclical',
  titleLat: 'Annus Iam Plenus',
  titleEn: 'On the Children of Central Europe',
  titleZh: '《一年已過》通諭 — 戰後中歐兒童救援延續',
  promulgationDate: '1920-12-01',
  century: 20,
  summaryZh: "本篤十五世延續《如父般》（Paterno Iam Diu 1919）戰後兒童救援呼籲的短通諭。一戰結束一年後中歐糧食短缺仍嚴重，繼續為兒童募款。",
  topics: ["戰後救援", "中歐兒童", "人道援助續篇"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "annus-iam-plenus-1920-chinese",
      "source": "https://www.vatican.va/content/dam/benedict-xv/pdf/encyclicals/documents/hf_ben-xv_enc_01121920_annus-iam-plenus_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "annus-iam-plenus-1920-english",
      "source": "https://www.vatican.va/content/benedict-xv/en/encyclicals/documents/hf_ben-xv_enc_01121920_annus-iam-plenus.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "annus-iam-plenus-1920-latin",
      "source": "https://www.vatican.va/content/benedict-xv/la/encyclicals/documents/hf_ben-xv_enc_01121920_annus-iam-plenus.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "annus-iam-plenus-1920-italian",
      "source": "https://www.vatican.va/content/benedict-xv/it/encyclicals/documents/hf_ben-xv_enc_01121920_annus-iam-plenus.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/benedict-xv/en/encyclicals/documents/hf_ben-xv_enc_01121920_annus-iam-plenus.html',
  notes: "",
}
