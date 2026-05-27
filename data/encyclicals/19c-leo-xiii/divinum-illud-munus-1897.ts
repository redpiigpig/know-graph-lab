import type { PapalDocument } from '../types'

export const divinumIlludMunus1897: PapalDocument = {
  slug: 'divinum-illud-munus-1897',
  popeSlug: 'leo-xiii',
  category: 'encyclical',
  titleLat: 'Divinum Illud Munus',
  titleEn: 'On the Holy Spirit',
  titleZh: '《神聖恩賜》通諭 — 論聖神',
  promulgationDate: '1897-05-09',
  century: 19,
  summaryZh: "良十三世論聖神的通諭。將傳統聖神敬禮置於現代神學脈絡，預示了若望保祿二《主及賦予生命者》（Dominum et Vivificantem, 1986）對聖神論的當代展開。",
  topics: ["聖神論", "三位一體", "祈禱"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "divinum-illud-munus-1897-chinese",
      "source": "https://www.vatican.va/content/dam/leo-xiii/pdf/encyclicals/documents/hf_l-xiii_enc_09051897_divinum-illud-munus_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "divinum-illud-munus-1897-english",
      "source": "https://www.vatican.va/content/leo-xiii/en/encyclicals/documents/hf_l-xiii_enc_09051897_divinum-illud-munus.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "divinum-illud-munus-1897-latin",
      "source": "https://www.vatican.va/content/leo-xiii/la/encyclicals/documents/hf_l-xiii_enc_09051897_divinum-illud-munus.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "divinum-illud-munus-1897-italian",
      "source": "https://www.vatican.va/content/leo-xiii/it/encyclicals/documents/hf_l-xiii_enc_09051897_divinum-illud-munus.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/leo-xiii/en/encyclicals/documents/hf_l-xiii_enc_09051897_divinum-illud-munus.html',
  notes: "",
}
