import type { PapalDocument } from '../types'

export const pacemInTerris1963: PapalDocument = {
  slug: 'pacem-in-terris-1963',
  popeSlug: 'john-xxiii',
  category: 'encyclical',
  titleLat: 'Pacem in Terris',
  titleEn: 'Peace on Earth',
  titleZh: '《和平於世》通諭 — 論在真理、正義、愛德和自由中建立全人類和平',
  promulgationDate: '1963-04-11',
  century: 20,
  summaryZh: "若望二十三世第八道、最後一道通諭，亦是天主教史上首道明確指向「所有善心男女」（pace di tutti gli uomini di buona volontà）的通諭——突破傳統「給全體主教」的格式，首次把訓導文獻對象擴展至非天主教徒、非基督徒。\n\n本通諭於古巴飛彈危機（1962-10）半年後頒布，提出「個人與個人」「個人與國家」「國家與國家」「國家與國際社會」四層次的和平秩序。提出「人權」作為和平的基本前提，這是天主教社會訓導首次系統採用「人權」（diritti umani）作為神學語彙。",
  topics: ["和平", "人權", "國際秩序", "古巴飛彈危機", "社會訓導"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "pacem-in-terris-1963-chinese",
      "source": "https://www.vatican.va/content/dam/john-xxiii/pdf/encyclicals/documents/hf_j-xxiii_enc_11041963_pacem_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "pacem-in-terris-1963-english",
      "source": "https://www.vatican.va/content/john-xxiii/en/encyclicals/documents/hf_j-xxiii_enc_11041963_pacem.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "pacem-in-terris-1963-latin",
      "source": "https://www.vatican.va/content/john-xxiii/la/encyclicals/documents/hf_j-xxiii_enc_11041963_pacem.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "pacem-in-terris-1963-italian",
      "source": "https://www.vatican.va/content/john-xxiii/it/encyclicals/documents/hf_j-xxiii_enc_11041963_pacem.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/john-xxiii/en/encyclicals/documents/hf_j-xxiii_enc_11041963_pacem.html',
  notes: "簽署日 1963-04-11 為基督受難前的四旬期第五主日。若望二十三世於 1963-06-03 辭世。本通諭為其遺作。\n\n方濟各《眾位弟兄》通諭（2020）開篇即引用本通諭，並指其為「整個人類大家庭」對話的歷史性先例。",
}
