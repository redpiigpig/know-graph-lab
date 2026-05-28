import type { PapalDocument } from '../types'

export const iucundaSane1904: PapalDocument = {
  slug: 'iucunda-sane-1904',
  popeSlug: 'pius-x',
  category: 'encyclical',
  titleLat: 'Iucunda Sane',
  titleEn: 'On Pope Gregory the Great',
  titleZh: '《實在喜悅》通諭 — 紀念聖大額我略一世逝世 1300 週年',
  promulgationDate: '1904-03-12',
  century: 20,
  summaryZh: "碧岳十世紀念聖大額我略一世（Gregory the Great, 540-604）逝世 1300 週年的通諭。回顧大額我略作為教宗的牧靈榜樣——尤其其《牧靈書》（Regulae Pastoralis Liber）作為主教與司鐸培育的經典文本。",
  topics: ["大額我略", "牧靈神學", "教父傳統"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "iucunda-sane-1904-chinese",
      "source": "https://www.vatican.va/content/dam/pius-x/pdf/encyclicals/documents/hf_p-x_enc_12031904_iucunda-sane_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "iucunda-sane-1904-english",
      "source": "https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_12031904_iucunda-sane.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "iucunda-sane-1904-latin",
      "source": "https://www.vatican.va/content/pius-x/la/encyclicals/documents/hf_p-x_enc_12031904_iucunda-sane.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "iucunda-sane-1904-italian",
      "source": "https://www.vatican.va/content/pius-x/it/encyclicals/documents/hf_p-x_enc_12031904_iucunda-sane.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_12031904_iucunda-sane.html',
  notes: "聖大額我略 604-03-12 辭世，本通諭頒布日為其逝世 1300 週年紀念。",
}
