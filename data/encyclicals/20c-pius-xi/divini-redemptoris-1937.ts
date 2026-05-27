import type { PapalDocument } from '../types'

export const diviniRedemptoris1937: PapalDocument = {
  slug: 'divini-redemptoris-1937',
  popeSlug: 'pius-xi',
  category: 'encyclical',
  titleLat: 'Divini Redemptoris',
  titleEn: 'On Atheistic Communism',
  titleZh: '《神聖救贖者》通諭 — 論無神論共產主義',
  promulgationDate: '1937-03-19',
  century: 20,
  summaryZh: "碧岳十一世譴責共產主義的系統性通諭，在《充滿燃燒的憂慮》（譴責納粹）後 5 天頒布。在 1930 年代「兩極極權威脅」（納粹／共產）的歷史背景下，本通諭明確將共產主義列為與天主教信仰不可調和的世俗主義意識形態。",
  topics: ["反共產主義", "無神論批判", "社會訓導", "戰前訓導"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "divini-redemptoris-1937-chinese",
      "source": "https://www.vatican.va/content/dam/pius-xi/pdf/encyclicals/documents/hf_p-xi_enc_19370319_divini-redemptoris_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "divini-redemptoris-1937-english",
      "source": "https://www.vatican.va/content/pius-xi/en/encyclicals/documents/hf_p-xi_enc_19370319_divini-redemptoris.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "divini-redemptoris-1937-latin",
      "source": "https://www.vatican.va/content/pius-xi/la/encyclicals/documents/hf_p-xi_enc_19370319_divini-redemptoris.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "divini-redemptoris-1937-italian",
      "source": "https://www.vatican.va/content/pius-xi/it/encyclicals/documents/hf_p-xi_enc_19370319_divini-redemptoris.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-xi/en/encyclicals/documents/hf_p-xi_enc_19370319_divini-redemptoris.html',
  notes: "簽署日 1937-03-19 為聖若瑟瞻禮。與《充滿燃燒的憂慮》並列，構成碧岳十一世 1937 年「雙峰反極權」訓導。",
}
