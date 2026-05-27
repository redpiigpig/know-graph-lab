import type { PapalDocument } from '../types'

export const centesimusAnnus1991: PapalDocument = {
  slug: 'centesimus-annus-1991',
  popeSlug: 'john-paul-ii',
  category: 'encyclical',
  titleLat: 'Centesimus Annus',
  titleEn: 'The Hundredth Year',
  titleZh: '《一百週年》通諭 — 紀念《新事》通諭頒布 100 週年',
  promulgationDate: '1991-05-01',
  century: 20,
  summaryZh: "若望保祿二世第九道通諭，紀念良十三《新事》通諭（Rerum Novarum 1891）頒布 100 週年。蘇東劇變（1989）後一年半頒布。\n\n通諭以蘇東共產體制崩潰為時代背景，重新評估資本主義與社會主義。提出「企業經濟」（economia di mercato/d'impresa）並「在道德／法律框架內」可獲得肯定的條件分析。第 35 段「人為中心的市場經濟」（economia di mercato a misura d'uomo）成為冷戰後天主教社會訓導的核心概念。",
  topics: ["社會訓導", "資本主義", "蘇東劇變", "人為中心經濟", "工人權利"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "centesimus-annus-1991-chinese",
      "source": "https://www.vatican.va/content/dam/john-paul-ii/pdf/encyclicals/documents/hf_jp-ii_enc_01051991_centesimus-annus_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "centesimus-annus-1991-english",
      "source": "https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_01051991_centesimus-annus.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "centesimus-annus-1991-latin",
      "source": "https://www.vatican.va/content/john-paul-ii/la/encyclicals/documents/hf_jp-ii_enc_01051991_centesimus-annus.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "centesimus-annus-1991-italian",
      "source": "https://www.vatican.va/content/john-paul-ii/it/encyclicals/documents/hf_jp-ii_enc_01051991_centesimus-annus.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_01051991_centesimus-annus.html',
  notes: "簽署日 1991-05-01 為勞工聖若瑟瞻禮，亦呼應《新事》通諭 1891-05-15 頒布日的勞動議題。",
}
