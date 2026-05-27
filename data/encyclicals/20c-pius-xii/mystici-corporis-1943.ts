import type { PapalDocument } from '../types'

export const mysticiCorporis1943: PapalDocument = {
  slug: 'mystici-corporis-1943',
  popeSlug: 'pius-xii',
  category: 'encyclical',
  titleLat: 'Mystici Corporis Christi',
  titleEn: 'On the Mystical Body of Christ',
  titleZh: '《基督奧體》通諭 — 論教會作為基督奧妙身體',
  promulgationDate: '1943-06-29',
  century: 20,
  summaryZh: "碧岳十二世第三道通諭，是 20 世紀教會學的標誌性文件。系統發展「教會是基督奧妙身體」（Corpus Christi Mysticum）這一聖保祿傳統。\n\n強調聖體聖事與教會本質的內在連繫，並界定基督奧體與「羅馬天主教會」之間的關係——後成為梵二《教會憲章》「subsistit in」（教會臨在於）討論的重要前史。",
  topics: ["教會學", "基督奧體", "聖體聖事", "教會本質"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "mystici-corporis-1943-chinese",
      "source": "https://www.vatican.va/content/dam/pius-xii/pdf/encyclicals/documents/hf_p-xii_enc_29061943_mystici-corporis-christi_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "mystici-corporis-1943-english",
      "source": "https://www.vatican.va/content/pius-xii/en/encyclicals/documents/hf_p-xii_enc_29061943_mystici-corporis-christi.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "mystici-corporis-1943-latin",
      "source": "https://www.vatican.va/content/pius-xii/la/encyclicals/documents/hf_p-xii_enc_29061943_mystici-corporis-christi.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "mystici-corporis-1943-italian",
      "source": "https://www.vatican.va/content/pius-xii/it/encyclicals/documents/hf_p-xii_enc_29061943_mystici-corporis-christi.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-xii/en/encyclicals/documents/hf_p-xii_enc_29061943_mystici-corporis-christi.html',
  notes: "簽署日 1943-06-29 為聖伯多祿與聖保祿瞻禮。本通諭與《奉神感發》（Divino Afflante Spiritu，1943-09-30）共同構成碧岳十二世「教會學／聖經學」雙峰文件。",
}
