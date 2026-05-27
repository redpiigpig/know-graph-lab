import type { PapalDocument } from '../types'

export const aeterniPatris1879: PapalDocument = {
  slug: 'aeterni-patris-1879',
  popeSlug: 'leo-xiii',
  category: 'encyclical',
  titleLat: 'Aeterni Patris',
  titleEn: 'On the Restoration of Christian Philosophy',
  titleZh: '《永恆聖父》通諭 — 論基督徒哲學的重興',
  promulgationDate: '1879-08-04',
  century: 19,
  summaryZh: "良十三世第一年的標誌性通諭，宣告以聖多瑪斯‧阿奎那（Thomas Aquinas, 1225-1274）為基礎的「新多瑪斯主義」（Neo-Thomism）為天主教官方哲學體系。\n\n本通諭啟動了 19 末-20 中天主教學界的「多瑪斯復興」（Thomistic Revival），影響直達梵二（1962-65），並間接奠下若望保祿二《信仰與理性》（1998）通諭的神哲學立場。",
  topics: ["多瑪斯主義", "神哲學", "理性與信仰", "經院哲學"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "aeterni-patris-1879-chinese",
      "source": "https://www.vatican.va/content/dam/leo-xiii/pdf/encyclicals/documents/hf_l-xiii_enc_04081879_aeterni-patris_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "aeterni-patris-1879-english",
      "source": "https://www.vatican.va/content/leo-xiii/en/encyclicals/documents/hf_l-xiii_enc_04081879_aeterni-patris.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "aeterni-patris-1879-latin",
      "source": "https://www.vatican.va/content/leo-xiii/la/encyclicals/documents/hf_l-xiii_enc_04081879_aeterni-patris.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "aeterni-patris-1879-italian",
      "source": "https://www.vatican.va/content/leo-xiii/it/encyclicals/documents/hf_l-xiii_enc_04081879_aeterni-patris.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/leo-xiii/en/encyclicals/documents/hf_l-xiii_enc_04081879_aeterni-patris.html',
  notes: "良十三世於 1878-02-20 就任，本通諭 1879-08-04 簽署，1.5 年內完成首道方向性通諭。\n\n「新多瑪斯主義」的範式直至 1960 年代才隨「新神學」（Nouvelle Théologie）的興起而被部分修正，但其影響至今仍可在天主教神學體系中清楚見到。",
}
