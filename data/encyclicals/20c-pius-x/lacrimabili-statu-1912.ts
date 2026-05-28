import type { PapalDocument } from '../types'

export const lacrimabiliStatu1912: PapalDocument = {
  slug: 'lacrimabili-statu-1912',
  popeSlug: 'pius-x',
  category: 'encyclical',
  titleLat: 'Lacrimabili Statu',
  titleEn: 'On the Indians of South America',
  titleZh: '《可悲狀況》通諭 — 論南美原住民境況',
  promulgationDate: '1912-06-07',
  century: 20,
  summaryZh: "碧岳十世關心南美原住民（特別是亞馬遜雨林部落）被殖民者剝削、奴役狀況的通諭。回應 1909-12 年國際間揭發祕魯亞馬遜「Putumayo 醜聞」（橡膠公司對原住民暴力剝削）。\n\n本通諭是天主教首次系統關注南美原住民人權的訓導文件，預示百年後方濟各 2020《敬愛的亞馬遜》（Querida Amazonia）勸諭的歷史源頭。",
  topics: ["南美原住民", "奴役批判", "亞馬遜", "Putumayo 醜聞"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "lacrimabili-statu-1912-chinese",
      "source": "https://www.vatican.va/content/dam/pius-x/pdf/encyclicals/documents/hf_p-x_enc_07061912_lacrimabili-statu_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "lacrimabili-statu-1912-english",
      "source": "https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_07061912_lacrimabili-statu.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "lacrimabili-statu-1912-latin",
      "source": "https://www.vatican.va/content/pius-x/la/encyclicals/documents/hf_p-x_enc_07061912_lacrimabili-statu.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "lacrimabili-statu-1912-italian",
      "source": "https://www.vatican.va/content/pius-x/it/encyclicals/documents/hf_p-x_enc_07061912_lacrimabili-statu.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_07061912_lacrimabili-statu.html',
  notes: "",
}
