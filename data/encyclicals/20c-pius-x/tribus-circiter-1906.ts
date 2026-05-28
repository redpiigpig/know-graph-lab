import type { PapalDocument } from '../types'

export const tribusCirciter1906: PapalDocument = {
  slug: 'tribus-circiter-1906',
  popeSlug: 'pius-x',
  category: 'encyclical',
  titleLat: 'Tribus Circiter',
  titleEn: 'On the Mariavites or Mystic Priests of Poland',
  titleZh: '《大約三年》通諭 — 譴責波蘭瑪利亞神秘派',
  promulgationDate: '1906-04-05',
  century: 20,
  summaryZh: "碧岳十世譴責波蘭「瑪利亞神秘派」（Mariavites）的通諭。此派源於波蘭神秘修女 Feliksa Kozłowska 的私下啟示，宣稱聖體聖事改革神秘運動，後被定為異端並脫離天主教，建立獨立 Old Catholic 教會分支。",
  topics: ["異端", "波蘭", "私下啟示批判"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "tribus-circiter-1906-chinese",
      "source": "https://www.vatican.va/content/dam/pius-x/pdf/encyclicals/documents/hf_p-x_enc_05041906_tribus-circiter_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "tribus-circiter-1906-english",
      "source": "https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_05041906_tribus-circiter.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "tribus-circiter-1906-latin",
      "source": "https://www.vatican.va/content/pius-x/la/encyclicals/documents/hf_p-x_enc_05041906_tribus-circiter.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "tribus-circiter-1906-italian",
      "source": "https://www.vatican.va/content/pius-x/it/encyclicals/documents/hf_p-x_enc_05041906_tribus-circiter.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_05041906_tribus-circiter.html',
  notes: "",
}
