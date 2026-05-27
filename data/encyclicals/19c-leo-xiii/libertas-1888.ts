import type { PapalDocument } from '../types'

export const libertas1888: PapalDocument = {
  slug: 'libertas-1888',
  popeSlug: 'leo-xiii',
  category: 'encyclical',
  titleLat: 'Libertas Praestantissimum',
  titleEn: 'On the Nature of Human Liberty',
  titleZh: '《最珍貴的自由》通諭 — 論人的自由本質',
  promulgationDate: '1888-06-20',
  century: 19,
  summaryZh: "良十三世論自由的系統性通諭。區分「正當自由」（與真理／善連繫的自由）與「世俗自由主義」的相對主義「無限自由」概念。為梵二《信仰自由宣言》（Dignitatis Humanae 1965）的天主教自由傳統奠基。",
  topics: ["自由", "自由主義批判", "良心自由", "梵二前史"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "libertas-1888-chinese",
      "source": "https://www.vatican.va/content/dam/leo-xiii/pdf/encyclicals/documents/hf_l-xiii_enc_20061888_libertas_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "libertas-1888-english",
      "source": "https://www.vatican.va/content/leo-xiii/en/encyclicals/documents/hf_l-xiii_enc_20061888_libertas.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "libertas-1888-latin",
      "source": "https://www.vatican.va/content/leo-xiii/la/encyclicals/documents/hf_l-xiii_enc_20061888_libertas.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "libertas-1888-italian",
      "source": "https://www.vatican.va/content/leo-xiii/it/encyclicals/documents/hf_l-xiii_enc_20061888_libertas.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/leo-xiii/en/encyclicals/documents/hf_l-xiii_enc_20061888_libertas.html',
  notes: "",
}
