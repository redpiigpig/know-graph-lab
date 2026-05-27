import type { PapalDocument } from '../types'

export const fulgensCorona1953: PapalDocument = {
  slug: 'fulgens-corona-1953',
  popeSlug: 'pius-xii',
  category: 'encyclical',
  titleLat: 'Fulgens Corona',
  titleEn: 'Proclaiming a Marian Year',
  titleZh: '《光輝之冠》通諭 — 宣告聖母年',
  promulgationDate: '1953-09-08',
  century: 20,
  summaryZh: "碧岳十二世宣告 1954 年為「聖母年」（Annus Marialis），紀念碧岳九世 1854 定義「無染原罪」（Ineffabilis Deus）信理 100 週年。",
  topics: ["聖母敬禮", "無染原罪", "聖母年"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "fulgens-corona-1953-chinese",
      "source": "https://www.vatican.va/content/dam/pius-xii/pdf/encyclicals/documents/hf_p-xii_enc_08091953_fulgens-corona_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "fulgens-corona-1953-english",
      "source": "https://www.vatican.va/content/pius-xii/en/encyclicals/documents/hf_p-xii_enc_08091953_fulgens-corona.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "fulgens-corona-1953-latin",
      "source": "https://www.vatican.va/content/pius-xii/la/encyclicals/documents/hf_p-xii_enc_08091953_fulgens-corona.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "fulgens-corona-1953-italian",
      "source": "https://www.vatican.va/content/pius-xii/it/encyclicals/documents/hf_p-xii_enc_08091953_fulgens-corona.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-xii/en/encyclicals/documents/hf_p-xii_enc_08091953_fulgens-corona.html',
  notes: "簽署日 1953-09-08 為聖母誕辰瞻禮。聖母年標誌碧岳十二世個人深厚的聖母敬禮，亦為其 1950 定義「聖母升天」（Munificentissimus Deus）信理之延續。",
}
