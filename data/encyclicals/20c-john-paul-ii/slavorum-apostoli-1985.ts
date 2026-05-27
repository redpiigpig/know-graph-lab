import type { PapalDocument } from '../types'

export const slavorumApostoli1985: PapalDocument = {
  slug: 'slavorum-apostoli-1985',
  popeSlug: 'john-paul-ii',
  category: 'encyclical',
  titleLat: 'Slavorum Apostoli',
  titleEn: 'The Apostles of the Slavs',
  titleZh: '《斯拉夫民族的宗徒》通諭 — 紀念聖濟利祿與聖默多狄',
  promulgationDate: '1985-06-02',
  century: 20,
  summaryZh: "若望保祿二世第四道通諭，紀念斯拉夫民族宗徒聖濟利祿（Cyril, 826-869）與聖默多狄（Methodius, 815-885）福傳殉道。\n\n通諭著重二聖將拜占庭禮儀本地化為「古教會斯拉夫語」（Old Church Slavonic）的「本地化」（inculturatio）原則，反映若望保祿二世波蘭出身的斯拉夫身份。1980 年宣告兩人為「歐洲共同主保」（与聖本篤共三人）。",
  topics: ["斯拉夫宗徒", "本地化", "東西教會", "歐洲身份"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "slavorum-apostoli-1985-chinese",
      "source": "https://www.vatican.va/content/dam/john-paul-ii/pdf/encyclicals/documents/hf_jp-ii_enc_19850602_slavorum-apostoli_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "slavorum-apostoli-1985-english",
      "source": "https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_19850602_slavorum-apostoli.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "slavorum-apostoli-1985-latin",
      "source": "https://www.vatican.va/content/john-paul-ii/la/encyclicals/documents/hf_jp-ii_enc_19850602_slavorum-apostoli.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "slavorum-apostoli-1985-italian",
      "source": "https://www.vatican.va/content/john-paul-ii/it/encyclicals/documents/hf_jp-ii_enc_19850602_slavorum-apostoli.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_19850602_slavorum-apostoli.html',
  notes: "",
}
