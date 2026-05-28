import type { PapalDocument } from '../types'

export const eSupremi1903: PapalDocument = {
  slug: 'e-supremi-1903',
  popeSlug: 'pius-x',
  category: 'encyclical',
  titleLat: 'E Supremi',
  titleEn: 'On the Restoration of All Things in Christ',
  titleZh: '《至高使徒職位》通諭 — 論在基督內重整萬有',
  promulgationDate: '1903-10-04',
  century: 20,
  summaryZh: "碧岳十世第一道通諭，於就任後兩個月頒布。揭示其牧職主軸——「在基督內重整一切」（Instaurare omnia in Christo，弗 1:10）。\n\n面對 20 世紀初歐洲世俗化、實證主義興盛背景，本通諭定下其往後 11 年牧職的基本方向——對抗現代主義神學的「教義改造」傾向，重申聖事生活、要理教育、聖樂改革等具體牧靈措施。",
  topics: ["就任通諭", "現代主義反思", "牧靈方向", "在基督內重整"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "e-supremi-1903-chinese",
      "source": "https://www.vatican.va/content/dam/pius-x/pdf/encyclicals/documents/hf_p-x_enc_04101903_e-supremi_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "e-supremi-1903-english",
      "source": "https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_04101903_e-supremi.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "e-supremi-1903-latin",
      "source": "https://www.vatican.va/content/pius-x/la/encyclicals/documents/hf_p-x_enc_04101903_e-supremi.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "e-supremi-1903-italian",
      "source": "https://www.vatican.va/content/pius-x/it/encyclicals/documents/hf_p-x_enc_04101903_e-supremi.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_04101903_e-supremi.html',
  notes: "碧岳十世於 1903-08-04 就任，本通諭 1903-10-04 簽署，2 個月內完成首道通諭。",
}
