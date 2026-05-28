import type { PapalDocument } from '../types'

export const uneFoisEncore1907: PapalDocument = {
  slug: 'une-fois-encore-1907',
  popeSlug: 'pius-x',
  category: 'encyclical',
  titleLat: 'Une Fois Encore',
  titleEn: 'On the Separation of Church and State',
  titleZh: '《再一次》通諭 — 再論法國政教分離',
  promulgationDate: '1907-01-06',
  century: 20,
  summaryZh: "碧岳十世第三道處理法國政教分離議題的法文通諭，是其「法國三部曲」的結尾。對法國天主教徒的牧靈呼籲——在政府敵對立場下堅持信仰、教育子女、培養聖召。",
  topics: ["法國政教分離", "教會堅守", "信徒鼓勵"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "une-fois-encore-1907-chinese",
      "source": "https://www.vatican.va/content/dam/pius-x/pdf/encyclicals/documents/hf_p-x_enc_06011907_une-fois-encore_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "une-fois-encore-1907-english",
      "source": "https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_06011907_une-fois-encore.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "une-fois-encore-1907-latin",
      "source": "https://www.vatican.va/content/pius-x/la/encyclicals/documents/hf_p-x_enc_06011907_une-fois-encore.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "une-fois-encore-1907-italian",
      "source": "https://www.vatican.va/content/pius-x/it/encyclicals/documents/hf_p-x_enc_06011907_une-fois-encore.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_06011907_une-fois-encore.html',
  notes: "以法文頒布，直接面對法國信徒。",
}
