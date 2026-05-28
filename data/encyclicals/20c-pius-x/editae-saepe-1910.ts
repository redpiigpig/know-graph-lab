import type { PapalDocument } from '../types'

export const editaeSaepe1910: PapalDocument = {
  slug: 'editae-saepe-1910',
  popeSlug: 'pius-x',
  category: 'encyclical',
  titleLat: 'Editae Saepe',
  titleEn: 'On St. Charles Borromeo',
  titleZh: '《經常頒布》通諭 — 紀念聖嘉祿‧鮑榮茂 300 週年',
  promulgationDate: '1910-05-26',
  century: 20,
  summaryZh: "碧岳十世紀念聖嘉祿‧鮑榮茂（Charles Borromeo, 1538-1584，米蘭總主教、特利騰大公會議後牧靈改革代表人物）封聖 300 週年（1610 年封聖）的通諭。\n\n本通諭因部分歷史段落對 16 世紀新教改革的嚴厲措辭，引發德國新教界強烈反應，碧岳十世後續發出聲明澄清立場。",
  topics: ["聖嘉祿‧鮑榮茂", "特利騰改革", "牧靈典範"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "editae-saepe-1910-chinese",
      "source": "https://www.vatican.va/content/dam/pius-x/pdf/encyclicals/documents/hf_p-x_enc_26051910_editae-saepe_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "editae-saepe-1910-english",
      "source": "https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_26051910_editae-saepe.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "editae-saepe-1910-latin",
      "source": "https://www.vatican.va/content/pius-x/la/encyclicals/documents/hf_p-x_enc_26051910_editae-saepe.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "editae-saepe-1910-italian",
      "source": "https://www.vatican.va/content/pius-x/it/encyclicals/documents/hf_p-x_enc_26051910_editae-saepe.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_26051910_editae-saepe.html',
  notes: "本通諭因措辭引起德國新教界反彈，是 20 世紀初天主教—新教關係的微小但具歷史意義的事件。",
}
