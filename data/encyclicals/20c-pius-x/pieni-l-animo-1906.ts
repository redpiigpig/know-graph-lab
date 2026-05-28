import type { PapalDocument } from '../types'

export const pieniLAnimo1906: PapalDocument = {
  slug: 'pieni-l-animo-1906',
  popeSlug: 'pius-x',
  category: 'encyclical',
  titleLat: "Pieni L'Animo",
  titleEn: 'On the Clergy in Italy',
  titleZh: '《心靈充滿》通諭 — 論義大利神職紀律',
  promulgationDate: '1906-07-28',
  century: 20,
  summaryZh: "碧岳十世論義大利神職紀律的義大利文通諭。針對某些義大利神父介入政治、社會運動超越教會紀律，重申司鐸職分的紀律與服從原則。",
  topics: ["神職紀律", "義大利", "司鐸服從"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "pieni-l-animo-1906-chinese",
      "source": "https://www.vatican.va/content/dam/pius-x/pdf/encyclicals/documents/hf_p-x_enc_28071906_pieni-l-animo_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "pieni-l-animo-1906-english",
      "source": "https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_28071906_pieni-l-animo.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "pieni-l-animo-1906-latin",
      "source": "https://www.vatican.va/content/pius-x/la/encyclicals/documents/hf_p-x_enc_28071906_pieni-l-animo.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "pieni-l-animo-1906-italian",
      "source": "https://www.vatican.va/content/pius-x/it/encyclicals/documents/hf_p-x_enc_28071906_pieni-l-animo.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_28071906_pieni-l-animo.html',
  notes: "以義大利文頒布，僅針對義大利教會。",
}
