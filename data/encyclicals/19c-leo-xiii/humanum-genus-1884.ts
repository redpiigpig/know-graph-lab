import type { PapalDocument } from '../types'

export const humanumGenus1884: PapalDocument = {
  slug: 'humanum-genus-1884',
  popeSlug: 'leo-xiii',
  category: 'encyclical',
  titleLat: 'Humanum Genus',
  titleEn: 'On Freemasonry',
  titleZh: '《人類》通諭 — 論共濟會',
  promulgationDate: '1884-04-20',
  century: 19,
  summaryZh: "良十三世論共濟會（Freemasonry）的通諭，將共濟會列為與天主教信仰不可調和的世俗秘密社團。本通諭延續至今的「天主教徒不可加入共濟會」立場（1983 CIC §1374）的源頭。",
  topics: ["共濟會", "秘密社團", "世俗化批判"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "humanum-genus-1884-chinese",
      "source": "https://www.vatican.va/content/dam/leo-xiii/pdf/encyclicals/documents/hf_l-xiii_enc_18840420_humanum-genus_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "humanum-genus-1884-english",
      "source": "https://www.vatican.va/content/leo-xiii/en/encyclicals/documents/hf_l-xiii_enc_18840420_humanum-genus.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "humanum-genus-1884-latin",
      "source": "https://www.vatican.va/content/leo-xiii/la/encyclicals/documents/hf_l-xiii_enc_18840420_humanum-genus.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "humanum-genus-1884-italian",
      "source": "https://www.vatican.va/content/leo-xiii/it/encyclicals/documents/hf_l-xiii_enc_18840420_humanum-genus.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/leo-xiii/en/encyclicals/documents/hf_l-xiii_enc_18840420_humanum-genus.html',
  notes: "",
}
