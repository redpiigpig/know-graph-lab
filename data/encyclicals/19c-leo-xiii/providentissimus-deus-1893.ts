import type { PapalDocument } from '../types'

export const providentissimusDeus1893: PapalDocument = {
  slug: 'providentissimus-deus-1893',
  popeSlug: 'leo-xiii',
  category: 'encyclical',
  titleLat: 'Providentissimus Deus',
  titleEn: 'On the Study of Holy Scripture',
  titleZh: '《天主上智》通諭 — 論聖經研究',
  promulgationDate: '1893-11-18',
  century: 19,
  summaryZh: "良十三世論聖經研究的通諭，是 19 世紀末天主教應對「歷史考據聖經學」（Historical-Critical Method）挑戰的首道訓導性回應。\n\n本通諭立場較保守——強調聖經默感無誤（inerrancy）的普遍性，限制現代學術方法的應用範圍。後於碧岳十二《奉神感發》（Divino Afflante Spiritu, 1943）獲得實質性的更新，為梵二《天主啟示憲章》（Dei Verbum, 1965）鋪路。",
  topics: ["聖經研究", "默感無誤", "歷史考據法", "聖經學前史"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "providentissimus-deus-1893-chinese",
      "source": "https://www.vatican.va/content/dam/leo-xiii/pdf/encyclicals/documents/hf_l-xiii_enc_18111893_providentissimus-deus_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "providentissimus-deus-1893-english",
      "source": "https://www.vatican.va/content/leo-xiii/en/encyclicals/documents/hf_l-xiii_enc_18111893_providentissimus-deus.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "providentissimus-deus-1893-latin",
      "source": "https://www.vatican.va/content/leo-xiii/la/encyclicals/documents/hf_l-xiii_enc_18111893_providentissimus-deus.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "providentissimus-deus-1893-italian",
      "source": "https://www.vatican.va/content/leo-xiii/it/encyclicals/documents/hf_l-xiii_enc_18111893_providentissimus-deus.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/leo-xiii/en/encyclicals/documents/hf_l-xiii_enc_18111893_providentissimus-deus.html',
  notes: "",
}
