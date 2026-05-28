import type { PapalDocument } from '../types'

export const adBeatissimiApostolorum1914: PapalDocument = {
  slug: 'ad-beatissimi-apostolorum-1914',
  popeSlug: 'benedict-xv',
  category: 'encyclical',
  titleLat: 'Ad Beatissimi Apostolorum',
  titleEn: 'Appealing for Peace',
  titleZh: '《向至福宗徒》通諭 — 就任通諭，論一戰',
  promulgationDate: '1914-11-01',
  century: 20,
  summaryZh: "本篤十五世第一道通諭，於就任後兩個月、一戰爆發三個月後頒布。本通諭定下其在位 8 年（1914-22）的核心主軸——為一戰和平奔走、戰後人道救援、譴責民族主義與「種族崇拜」。\n\n核心命題：分析現代社會四大「弊病」——個人主義至上、權威崩潰、階級鬥爭、過度民族主義。本通諭預示了《和平，神聖恩賜》（Pacem Dei Munus 1920）戰後和平整體框架。",
  topics: ["就任通諭", "一戰", "和平", "民族主義批判"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "ad-beatissimi-apostolorum-1914-chinese",
      "source": "https://www.vatican.va/content/dam/benedict-xv/pdf/encyclicals/documents/hf_ben-xv_enc_01111914_ad-beatissimi-apostolorum_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "ad-beatissimi-apostolorum-1914-english",
      "source": "https://www.vatican.va/content/benedict-xv/en/encyclicals/documents/hf_ben-xv_enc_01111914_ad-beatissimi-apostolorum.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "ad-beatissimi-apostolorum-1914-latin",
      "source": "https://www.vatican.va/content/benedict-xv/la/encyclicals/documents/hf_ben-xv_enc_01111914_ad-beatissimi-apostolorum.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "ad-beatissimi-apostolorum-1914-italian",
      "source": "https://www.vatican.va/content/benedict-xv/it/encyclicals/documents/hf_ben-xv_enc_01111914_ad-beatissimi-apostolorum.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/benedict-xv/en/encyclicals/documents/hf_ben-xv_enc_01111914_ad-beatissimi-apostolorum.html',
  notes: "本篤十五世於 1914-09-03 就任（其前任碧岳十世於 1914-08-20 辭世，正值一戰爆發），本通諭 1914-11-01 簽署。",
}
