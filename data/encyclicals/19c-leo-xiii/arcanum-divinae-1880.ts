import type { PapalDocument } from '../types'

export const arcanumDivinae1880: PapalDocument = {
  slug: 'arcanum-divinae-1880',
  popeSlug: 'leo-xiii',
  category: 'encyclical',
  titleLat: 'Arcanum Divinae Sapientiae',
  titleEn: 'On Christian Marriage',
  titleZh: '《神聖智慧的奧蹟》通諭 — 論基督徒婚姻',
  promulgationDate: '1880-02-10',
  century: 19,
  summaryZh: "良十三世論婚姻的通諭，回應 19 世紀末歐洲世俗化下民事婚姻取代教會婚姻的趨勢。重申婚姻是聖事、不可拆散、僅由教會管轄等傳統立場。後成為碧岳十一《貞潔的婚姻》（1930）的歷史源頭。",
  topics: ["婚姻", "聖事", "教會與國家", "世俗化批判"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "arcanum-divinae-1880-chinese",
      "source": "https://www.vatican.va/content/dam/leo-xiii/pdf/encyclicals/documents/hf_l-xiii_enc_10021880_arcanum_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "arcanum-divinae-1880-english",
      "source": "https://www.vatican.va/content/leo-xiii/en/encyclicals/documents/hf_l-xiii_enc_10021880_arcanum.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "arcanum-divinae-1880-latin",
      "source": "https://www.vatican.va/content/leo-xiii/la/encyclicals/documents/hf_l-xiii_enc_10021880_arcanum.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "arcanum-divinae-1880-italian",
      "source": "https://www.vatican.va/content/leo-xiii/it/encyclicals/documents/hf_l-xiii_enc_10021880_arcanum.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/leo-xiii/en/encyclicals/documents/hf_l-xiii_enc_10021880_arcanum.html',
  notes: "",
}
