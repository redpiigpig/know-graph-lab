import type { PapalDocument } from '../types'

export const ecclesiaDeEucharistia2003: PapalDocument = {
  slug: 'ecclesia-de-eucharistia-2003',
  popeSlug: 'john-paul-ii',
  category: 'encyclical',
  titleLat: 'Ecclesia de Eucharistia',
  titleEn: 'The Church from the Eucharist',
  titleZh: '《教會源於感恩聖事》通諭 — 論聖體聖事與教會的關係',
  promulgationDate: '2003-04-17',
  century: 21,
  summaryZh: "若望保祿二世第十四道、最後一道通諭，於辭世前兩年頒布。論聖體聖事（Eucharistia）與教會的內在關係。\n\n通諭重申「聖體聖事建構教會」（Ecclesia de Eucharistia vivit）的傳統教義，反駁戰後神學中對「實體變化」（transsubstantiatio）、聖體「奉獻祭」性質、僅司鐸可舉行感恩祭等核心教義的弱化。\n\n第 38-43 段對天主教—新教合一中「聖體共融」議題立場明確：與尚未恢復完全共融的教會分享聖體在教義上不可接受。",
  topics: ["聖體聖事", "教會學", "實體變化", "聖事神學", "合一運動界線"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "ecclesia-de-eucharistia-2003-chinese",
      "source": "https://www.vatican.va/content/dam/john-paul-ii/pdf/encyclicals/documents/hf_jp-ii_enc_20030417_eccl-de-euch_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "ecclesia-de-eucharistia-2003-english",
      "source": "https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_20030417_eccl-de-euch.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "ecclesia-de-eucharistia-2003-latin",
      "source": "https://www.vatican.va/content/john-paul-ii/la/encyclicals/documents/hf_jp-ii_enc_20030417_eccl-de-euch.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "ecclesia-de-eucharistia-2003-italian",
      "source": "https://www.vatican.va/content/john-paul-ii/it/encyclicals/documents/hf_jp-ii_enc_20030417_eccl-de-euch.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_20030417_eccl-de-euch.html',
  notes: "簽署日 2003-04-17 為主受難日前夕的聖週四（Holy Thursday 2003），即耶穌設立聖體聖事紀念日。\n\n若望保祿二世於 2005-04-02 辭世。本通諭頒布時其健康已嚴重惡化（帕金森氏症晚期），由樞機團代為朗讀。",
}
