import type { PapalDocument } from '../types'

export const annumSacrum1899: PapalDocument = {
  slug: 'annum-sacrum-1899',
  popeSlug: 'leo-xiii',
  category: 'encyclical',
  titleLat: 'Annum Sacrum',
  titleEn: 'On Consecration to the Sacred Heart',
  titleZh: '《聖年》通諭 — 論人類奉獻於耶穌聖心',
  promulgationDate: '1899-05-25',
  century: 19,
  summaryZh: "良十三世在 1900 年聖年前夕頒布的通諭，宣告將整個人類奉獻於耶穌聖心（Consecratio Generis Humani Sacro Cordi Iesu）。是 19-20 世紀「聖心敬禮」（Devotio ad Cor Iesu）達於高峰的訓導性文件，為碧岳十二《必汲取活水》（1956）與方濟各《祂愛了我們》（2024）兩道聖心通諭奠下基礎。",
  topics: ["耶穌聖心", "聖年", "奉獻"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "annum-sacrum-1899-chinese",
      "source": "https://www.vatican.va/content/dam/leo-xiii/pdf/encyclicals/documents/hf_l-xiii_enc_25051899_annum-sacrum_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "annum-sacrum-1899-english",
      "source": "https://www.vatican.va/content/leo-xiii/en/encyclicals/documents/hf_l-xiii_enc_25051899_annum-sacrum.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "annum-sacrum-1899-latin",
      "source": "https://www.vatican.va/content/leo-xiii/la/encyclicals/documents/hf_l-xiii_enc_25051899_annum-sacrum.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "annum-sacrum-1899-italian",
      "source": "https://www.vatican.va/content/leo-xiii/it/encyclicals/documents/hf_l-xiii_enc_25051899_annum-sacrum.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/leo-xiii/en/encyclicals/documents/hf_l-xiii_enc_25051899_annum-sacrum.html',
  notes: "1899-06-11 良十三世親自於聖伯多祿大殿正式宣讀奉獻人類於耶穌聖心。",
}
