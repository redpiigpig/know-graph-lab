import type { PapalDocument } from '../types'

export const redemptorHominis1979: PapalDocument = {
  slug: 'redemptor-hominis-1979',
  popeSlug: 'john-paul-ii',
  category: 'encyclical',
  titleLat: 'Redemptor Hominis',
  titleEn: 'The Redeemer of Man',
  titleZh: '《人類救主》通諭 — 論基督是人類救主',
  promulgationDate: '1979-03-04',
  century: 20,
  summaryZh: "若望保祿二世第一道通諭，於就任後 4 個月頒布，作為其整個牧職的「綱領性宣言」。\n\n核心命題：「人是教會的基本道路」（hominis via ecclesiae）。本通諭以基督論為基礎，論證唯有在基督救贖事件中，人才能真正認識自己作為「天主肖像」的尊嚴。也是 20 世紀末天主教「人類學轉向」的標誌性文件。",
  topics: ["基督論", "人類學", "救贖", "人性尊嚴", "梵二接續"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "redemptor-hominis-1979-chinese",
      "source": "https://www.vatican.va/content/dam/john-paul-ii/pdf/encyclicals/documents/hf_jp-ii_enc_04031979_redemptor-hominis_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "redemptor-hominis-1979-english",
      "source": "https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_04031979_redemptor-hominis.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "redemptor-hominis-1979-latin",
      "source": "https://www.vatican.va/content/john-paul-ii/la/encyclicals/documents/hf_jp-ii_enc_04031979_redemptor-hominis.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "redemptor-hominis-1979-italian",
      "source": "https://www.vatican.va/content/john-paul-ii/it/encyclicals/documents/hf_jp-ii_enc_04031979_redemptor-hominis.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_04031979_redemptor-hominis.html',
  notes: "若望保祿二世於 1978-10-16 就任，本通諭 1979-03-04 簽署，4 個月內完成首道通諭草擬，速度為現代教宗罕見。",
}
