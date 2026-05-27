import type { PapalDocument } from '../types'

export const rerumNovarum1891: PapalDocument = {
  slug: 'rerum-novarum-1891',
  popeSlug: 'leo-xiii',
  category: 'encyclical',
  titleLat: 'Rerum Novarum',
  titleEn: 'On Capital and Labor',
  titleZh: '《新事》通諭 — 論資本與勞工',
  promulgationDate: '1891-05-15',
  century: 19,
  summaryZh: "良十三世第十一年的標誌性通諭，是天主教社會訓導的開山之作。\n\n核心命題：在工業化時代，教會必須在「資本主義無限制」與「社會主義階級鬥爭」之間找出第三條道路。本通諭肯定：（一）私有財產權是自然法，（二）工人有權組工會、罷工、合理工資、休假，（三）國家有責任介入保障工人尊嚴。\n\n所有後續天主教社會通諭（《四十週年》《民族發展》《關懷社會事務》《一百週年》《在真理中實踐愛德》《眾位弟兄》）都明確自承為本通諭的延續。",
  topics: ["社會訓導", "勞工權利", "資本主義", "社會主義批判", "私有財產", "工會"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "rerum-novarum-1891-chinese",
      "source": "https://www.vatican.va/content/dam/leo-xiii/pdf/encyclicals/documents/hf_l-xiii_enc_15051891_rerum-novarum_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "rerum-novarum-1891-english",
      "source": "https://www.vatican.va/content/leo-xiii/en/encyclicals/documents/hf_l-xiii_enc_15051891_rerum-novarum.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "rerum-novarum-1891-latin",
      "source": "https://www.vatican.va/content/leo-xiii/la/encyclicals/documents/hf_l-xiii_enc_15051891_rerum-novarum.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "rerum-novarum-1891-italian",
      "source": "https://www.vatican.va/content/leo-xiii/it/encyclicals/documents/hf_l-xiii_enc_15051891_rerum-novarum.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/leo-xiii/en/encyclicals/documents/hf_l-xiii_enc_15051891_rerum-novarum.html',
  notes: "簽署日 1891-05-15 後成為天主教社會訓導的「紀念日」——碧岳十一《四十週年》（1931-05-15）、若望廿三《慈母與導師》（1961-05-15）、保祿六《八十週年》（1971-05-15）皆有意選擇 5 月 15 日頒布。\n\n本通諭是 21 世紀現存史上最具影響力的天主教訓導文件之一，被學界視為「現代社會學的天主教版本」。",
}
