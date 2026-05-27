import type { PapalDocument } from '../types'

export const humaniGeneris1950: PapalDocument = {
  slug: 'humani-generis-1950',
  popeSlug: 'pius-xii',
  category: 'encyclical',
  titleLat: 'Humani Generis',
  titleEn: 'On False Trends in Modern Teachings',
  titleZh: '《人類》通諭 — 論當代神學若干錯誤趨勢',
  promulgationDate: '1950-08-12',
  century: 20,
  summaryZh: "碧岳十二世對 1940-50 年代「新神學」（Nouvelle Théologie，de Lubac、Daniélou、Congar、Rahner 等）的修正性訓導。對神學家若干立場提出警告——進化論的神學容許範圍、原祖父母歷史性、聖經權威範圍等。\n\n雖被視為「保守反應」，本通諭同時也設定了梵二前夕教會神學討論的邊界，並間接推動了「新神學」家轉向更謹慎的表述方式。",
  topics: ["新神學", "現代主義", "進化論", "神學界線"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "humani-generis-1950-chinese",
      "source": "https://www.vatican.va/content/dam/pius-xii/pdf/encyclicals/documents/hf_p-xii_enc_12081950_humani-generis_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "humani-generis-1950-english",
      "source": "https://www.vatican.va/content/pius-xii/en/encyclicals/documents/hf_p-xii_enc_12081950_humani-generis.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "humani-generis-1950-latin",
      "source": "https://www.vatican.va/content/pius-xii/la/encyclicals/documents/hf_p-xii_enc_12081950_humani-generis.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "humani-generis-1950-italian",
      "source": "https://www.vatican.va/content/pius-xii/it/encyclicals/documents/hf_p-xii_enc_12081950_humani-generis.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-xii/en/encyclicals/documents/hf_p-xii_enc_12081950_humani-generis.html',
  notes: "",
}
