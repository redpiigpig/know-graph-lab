import type { PapalDocument } from '../types'

export const mediatorDei1947: PapalDocument = {
  slug: 'mediator-dei-1947',
  popeSlug: 'pius-xii',
  category: 'encyclical',
  titleLat: 'Mediator Dei',
  titleEn: 'On the Sacred Liturgy',
  titleZh: '《天主中保》通諭 — 論神聖禮儀',
  promulgationDate: '1947-11-20',
  century: 20,
  summaryZh: "碧岳十二世論禮儀的開創性通諭，是 20 世紀天主教「禮儀運動」（Liturgical Movement）的官方認可文件。為梵二《禮儀憲章》（Sacrosanctum Concilium 1963）鋪路。\n\n肯定信徒「主動參與」（actuosa participatio）禮儀的合法性，但同時警告反對禮儀改革過度極端的傾向。",
  topics: ["禮儀神學", "主動參與", "禮儀運動", "梵二籌備"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "mediator-dei-1947-chinese",
      "source": "https://www.vatican.va/content/dam/pius-xii/pdf/encyclicals/documents/hf_p-xii_enc_20111947_mediator-dei_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "mediator-dei-1947-english",
      "source": "https://www.vatican.va/content/pius-xii/en/encyclicals/documents/hf_p-xii_enc_20111947_mediator-dei.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "mediator-dei-1947-latin",
      "source": "https://www.vatican.va/content/pius-xii/la/encyclicals/documents/hf_p-xii_enc_20111947_mediator-dei.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "mediator-dei-1947-italian",
      "source": "https://www.vatican.va/content/pius-xii/it/encyclicals/documents/hf_p-xii_enc_20111947_mediator-dei.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-xii/en/encyclicals/documents/hf_p-xii_enc_20111947_mediator-dei.html',
  notes: "",
}
