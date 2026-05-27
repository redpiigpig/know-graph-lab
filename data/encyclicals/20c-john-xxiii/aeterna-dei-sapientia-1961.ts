import type { PapalDocument } from '../types'

export const aeternaDeiSapientia1961: PapalDocument = {
  slug: 'aeterna-dei-sapientia-1961',
  popeSlug: 'john-xxiii',
  category: 'encyclical',
  titleLat: 'Aeterna Dei Sapientia',
  titleEn: 'On the 1500th Anniversary of the Death of Pope Saint Leo I',
  titleZh: '《天主永恆的智慧》通諭 — 紀念聖大良一世逝世 1500 週年',
  promulgationDate: '1961-11-11',
  century: 20,
  summaryZh: "若望二十三世第六道通諭，紀念聖大良一世（Pope Saint Leo the Great, 440-461）逝世 1500 週年。聖大良是早期教宗中神學影響最大的一位，其《大良訓誡書》（Tome of Leo 449）為加采東大公會議基督論立下框架。",
  topics: ["聖大良", "教父", "基督論", "加采東會議"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "aeterna-dei-sapientia-1961-chinese",
      "source": "https://www.vatican.va/content/dam/john-xxiii/pdf/encyclicals/documents/hf_j-xxiii_enc_11111961_aeterna-dei_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "aeterna-dei-sapientia-1961-english",
      "source": "https://www.vatican.va/content/john-xxiii/en/encyclicals/documents/hf_j-xxiii_enc_11111961_aeterna-dei.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "aeterna-dei-sapientia-1961-latin",
      "source": "https://www.vatican.va/content/john-xxiii/la/encyclicals/documents/hf_j-xxiii_enc_11111961_aeterna-dei.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "aeterna-dei-sapientia-1961-italian",
      "source": "https://www.vatican.va/content/john-xxiii/it/encyclicals/documents/hf_j-xxiii_enc_11111961_aeterna-dei.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/john-xxiii/en/encyclicals/documents/hf_j-xxiii_enc_11111961_aeterna-dei.html',
  notes: "",
}
