import type { PapalDocument } from '../types'

export const inHacTanta1919: PapalDocument = {
  slug: 'in-hac-tanta-1919',
  popeSlug: 'benedict-xv',
  category: 'encyclical',
  titleLat: 'In Hac Tanta',
  titleEn: 'On St. Boniface',
  titleZh: '《在如此》通諭 — 紀念聖博義 1200 週年',
  promulgationDate: '1919-05-14',
  century: 20,
  summaryZh: "本篤十五世紀念聖博義（Boniface of Mainz, 675-754，盎格魯-撒克遜出身、德意志地區福傳宗徒、被尊為「日耳曼民族的宗徒」）德意志福傳 1200 週年的通諭。\n\n戰後立刻向德國發出此通諭，反映本篤十五世調和德法戰後敵意、避免懲罰性和平條款的努力。",
  topics: ["聖博義", "德意志福傳", "戰後和解"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "in-hac-tanta-1919-chinese",
      "source": "https://www.vatican.va/content/dam/benedict-xv/pdf/encyclicals/documents/hf_ben-xv_enc_14051919_in-hac-tanta_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "in-hac-tanta-1919-english",
      "source": "https://www.vatican.va/content/benedict-xv/en/encyclicals/documents/hf_ben-xv_enc_14051919_in-hac-tanta.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "in-hac-tanta-1919-latin",
      "source": "https://www.vatican.va/content/benedict-xv/la/encyclicals/documents/hf_ben-xv_enc_14051919_in-hac-tanta.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "in-hac-tanta-1919-italian",
      "source": "https://www.vatican.va/content/benedict-xv/it/encyclicals/documents/hf_ben-xv_enc_14051919_in-hac-tanta.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/benedict-xv/en/encyclicals/documents/hf_ben-xv_enc_14051919_in-hac-tanta.html',
  notes: "",
}
