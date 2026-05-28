import type { PapalDocument } from '../types'

export const sacraPropediem1921: PapalDocument = {
  slug: 'sacra-propediem-1921',
  popeSlug: 'benedict-xv',
  category: 'encyclical',
  titleLat: 'Sacra Propediem',
  titleEn: 'On the Third Order of St. Francis',
  titleZh: '《即將神聖》通諭 — 紀念方濟各第三會 700 週年',
  promulgationDate: '1921-01-06',
  century: 20,
  summaryZh: "本篤十五世紀念方濟各「第三會」（Tertius Ordo Sancti Francisci，方濟各俗世會）成立 700 週年的通諭。為 1921 年「方濟各年」（紀念聖方濟各 1226 辭世前 5 年的 1221 第三會建會）開啟。",
  topics: ["方濟各第三會", "平信徒運動", "方濟各靈修"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "sacra-propediem-1921-chinese",
      "source": "https://www.vatican.va/content/dam/benedict-xv/pdf/encyclicals/documents/hf_ben-xv_enc_06011921_sacra-propediem_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "sacra-propediem-1921-english",
      "source": "https://www.vatican.va/content/benedict-xv/en/encyclicals/documents/hf_ben-xv_enc_06011921_sacra-propediem.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "sacra-propediem-1921-latin",
      "source": "https://www.vatican.va/content/benedict-xv/la/encyclicals/documents/hf_ben-xv_enc_06011921_sacra-propediem.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "sacra-propediem-1921-italian",
      "source": "https://www.vatican.va/content/benedict-xv/it/encyclicals/documents/hf_ben-xv_enc_06011921_sacra-propediem.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/benedict-xv/en/encyclicals/documents/hf_ben-xv_enc_06011921_sacra-propediem.html',
  notes: "",
}
