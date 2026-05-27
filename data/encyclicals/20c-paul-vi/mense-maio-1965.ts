import type { PapalDocument } from '../types'

export const menseMaio1965: PapalDocument = {
  slug: 'mense-maio-1965',
  popeSlug: 'paul-vi',
  category: 'encyclical',
  titleLat: 'Mense Maio',
  titleEn: 'On Prayers During May',
  titleZh: '《在五月份》通諭 — 論五月為聖母玫瑰祈禱',
  promulgationDate: '1965-04-29',
  century: 20,
  summaryZh: "保祿六世第二道通諭，呼籲信徒在五月聖母月為和平祈禱、為梵二大公會議圓滿閉幕祈禱。",
  topics: ["聖母敬禮", "玫瑰經", "和平祈禱"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "mense-maio-1965-chinese",
      "source": "https://www.vatican.va/content/dam/paul-vi/pdf/encyclicals/documents/hf_p-vi_enc_29041965_mense-maio_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "mense-maio-1965-english",
      "source": "https://www.vatican.va/content/paul-vi/en/encyclicals/documents/hf_p-vi_enc_29041965_mense-maio.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "mense-maio-1965-latin",
      "source": "https://www.vatican.va/content/paul-vi/la/encyclicals/documents/hf_p-vi_enc_29041965_mense-maio.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "mense-maio-1965-italian",
      "source": "https://www.vatican.va/content/paul-vi/it/encyclicals/documents/hf_p-vi_enc_29041965_mense-maio.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/paul-vi/en/encyclicals/documents/hf_p-vi_enc_29041965_mense-maio.html',
  notes: "",
}
