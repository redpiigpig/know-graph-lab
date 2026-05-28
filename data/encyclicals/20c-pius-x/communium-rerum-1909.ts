import type { PapalDocument } from '../types'

export const communiumRerum1909: PapalDocument = {
  slug: 'communium-rerum-1909',
  popeSlug: 'pius-x',
  category: 'encyclical',
  titleLat: 'Communium Rerum',
  titleEn: 'On St. Anselm of Aosta',
  titleZh: '《共同事務》通諭 — 紀念聖安瑟莫逝世 800 週年',
  promulgationDate: '1909-04-21',
  century: 20,
  summaryZh: "碧岳十世紀念聖安瑟莫（Anselm of Canterbury, 1033-1109，本篤會士、奧斯塔出身、坎特伯雷大主教、教會聖師）逝世 800 週年的通諭。回顧安瑟莫作為「經院神學之父」對「信仰尋求理解」（fides quaerens intellectum）方法的奠基貢獻。",
  topics: ["聖安瑟莫", "經院神學", "教會聖師"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "communium-rerum-1909-chinese",
      "source": "https://www.vatican.va/content/dam/pius-x/pdf/encyclicals/documents/hf_p-x_enc_21041909_communium-rerum_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "communium-rerum-1909-english",
      "source": "https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_21041909_communium-rerum.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "communium-rerum-1909-latin",
      "source": "https://www.vatican.va/content/pius-x/la/encyclicals/documents/hf_p-x_enc_21041909_communium-rerum.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "communium-rerum-1909-italian",
      "source": "https://www.vatican.va/content/pius-x/it/encyclicals/documents/hf_p-x_enc_21041909_communium-rerum.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_21041909_communium-rerum.html',
  notes: "",
}
