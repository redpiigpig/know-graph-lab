import type { PapalDocument } from '../types'

export const principiApostolorumPetro1920: PapalDocument = {
  slug: 'principi-apostolorum-petro-1920',
  popeSlug: 'benedict-xv',
  category: 'encyclical',
  titleLat: 'Principi Apostolorum Petro',
  titleEn: 'On St. Ephrem the Syrian',
  titleZh: '《宗徒之首伯多祿》通諭 — 宣告聖厄弗冷為教會聖師',
  promulgationDate: '1920-10-05',
  century: 20,
  summaryZh: "本篤十五世正式宣告敘利亞教父聖厄弗冷（Ephrem the Syrian, 306-373，敘利亞神學家、聖詩作家）為「教會聖師」（Doctor Ecclesiae）的通諭。\n\n本通諭意義特殊——首位東方／敘利亞傳統教父獲此殊榮，反映本篤十五世推動天主教—東方教會合一對話的努力。",
  topics: ["聖厄弗冷", "敘利亞教父", "教會聖師", "東方教會合一"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "principi-apostolorum-petro-1920-chinese",
      "source": "https://www.vatican.va/content/dam/benedict-xv/pdf/encyclicals/documents/hf_ben-xv_enc_05101920_principi-apostolorum-petro_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "principi-apostolorum-petro-1920-english",
      "source": "https://www.vatican.va/content/benedict-xv/en/encyclicals/documents/hf_ben-xv_enc_05101920_principi-apostolorum-petro.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "principi-apostolorum-petro-1920-latin",
      "source": "https://www.vatican.va/content/benedict-xv/la/encyclicals/documents/hf_ben-xv_enc_05101920_principi-apostolorum-petro.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "principi-apostolorum-petro-1920-italian",
      "source": "https://www.vatican.va/content/benedict-xv/it/encyclicals/documents/hf_ben-xv_enc_05101920_principi-apostolorum-petro.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/benedict-xv/en/encyclicals/documents/hf_ben-xv_enc_05101920_principi-apostolorum-petro.html',
  notes: "",
}
