import type { PapalDocument } from '../types'

export const immortaleDei1885: PapalDocument = {
  slug: 'immortale-dei-1885',
  popeSlug: 'leo-xiii',
  category: 'encyclical',
  titleLat: 'Immortale Dei',
  titleEn: 'On the Christian Constitution of States',
  titleZh: '《不朽的天主》通諭 — 論國家的基督徒體制',
  promulgationDate: '1885-11-01',
  century: 19,
  summaryZh: "良十三世論政教關係的開創性通諭。提出「教會／國家兩權各有其領域」的「兩劍說」（duo gladii）現代版本：教會職司「天主／永恆事務」（res sacrae），國家職司「人類／時間事務」（res profanae），兩者應「友好分立」（amica separatio）。",
  topics: ["政教關係", "兩劍說", "公民社會", "宗教自由前史"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "immortale-dei-1885-chinese",
      "source": "https://www.vatican.va/content/dam/leo-xiii/pdf/encyclicals/documents/hf_l-xiii_enc_01111885_immortale-dei_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "immortale-dei-1885-english",
      "source": "https://www.vatican.va/content/leo-xiii/en/encyclicals/documents/hf_l-xiii_enc_01111885_immortale-dei.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "immortale-dei-1885-latin",
      "source": "https://www.vatican.va/content/leo-xiii/la/encyclicals/documents/hf_l-xiii_enc_01111885_immortale-dei.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "immortale-dei-1885-italian",
      "source": "https://www.vatican.va/content/leo-xiii/it/encyclicals/documents/hf_l-xiii_enc_01111885_immortale-dei.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/leo-xiii/en/encyclicals/documents/hf_l-xiii_enc_01111885_immortale-dei.html',
  notes: "",
}
