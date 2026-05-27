import type { PapalDocument } from '../types'

export const christiMatri1966: PapalDocument = {
  slug: 'christi-matri-1966',
  popeSlug: 'paul-vi',
  category: 'encyclical',
  titleLat: 'Christi Matri',
  titleEn: 'To the Mother of Christ',
  titleZh: '《基督之母》通諭 — 為和平向聖母祈禱',
  promulgationDate: '1966-09-15',
  century: 20,
  summaryZh: "保祿六世第四道通諭，呼籲信徒在 10 月玫瑰經月為和平祈禱，特別針對越戰升溫。",
  topics: ["聖母敬禮", "和平祈禱", "玫瑰經", "越戰"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "christi-matri-1966-chinese",
      "source": "https://www.vatican.va/content/dam/paul-vi/pdf/encyclicals/documents/hf_p-vi_enc_15091966_christi-matri_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "christi-matri-1966-english",
      "source": "https://www.vatican.va/content/paul-vi/en/encyclicals/documents/hf_p-vi_enc_15091966_christi-matri.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "christi-matri-1966-latin",
      "source": "https://www.vatican.va/content/paul-vi/la/encyclicals/documents/hf_p-vi_enc_15091966_christi-matri.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "christi-matri-1966-italian",
      "source": "https://www.vatican.va/content/paul-vi/it/encyclicals/documents/hf_p-vi_enc_15091966_christi-matri.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/paul-vi/en/encyclicals/documents/hf_p-vi_enc_15091966_christi-matri.html',
  notes: "簽署日 1966-09-15 為痛苦聖母紀念日。",
}
