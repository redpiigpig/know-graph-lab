import type { PapalDocument } from '../types'

export const quodIamDiu1918: PapalDocument = {
  slug: 'quod-iam-diu-1918',
  popeSlug: 'benedict-xv',
  category: 'encyclical',
  titleLat: 'Quod Iam Diu',
  titleEn: 'On the Future Peace Conference',
  titleZh: '《久已》通諭 — 為戰後和平會議祈禱',
  promulgationDate: '1918-12-01',
  century: 20,
  summaryZh: "本篤十五世於一戰結束（1918-11-11 停戰）後不到三週頒布的短通諭，呼籲信徒為即將召開的巴黎和會（1919-01-18 開始）祈禱。\n\n注意：本篤十五世本人因戰時保持中立立場（與英法俄協約國對抗德奧時，教廷未明確選邊）未獲邀參加巴黎和會。",
  topics: ["戰後和平", "巴黎和會", "祈禱"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "quod-iam-diu-1918-chinese",
      "source": "https://www.vatican.va/content/dam/benedict-xv/pdf/encyclicals/documents/hf_ben-xv_enc_01121918_quod-iam-diu_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "quod-iam-diu-1918-english",
      "source": "https://www.vatican.va/content/benedict-xv/en/encyclicals/documents/hf_ben-xv_enc_01121918_quod-iam-diu.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "quod-iam-diu-1918-latin",
      "source": "https://www.vatican.va/content/benedict-xv/la/encyclicals/documents/hf_ben-xv_enc_01121918_quod-iam-diu.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "quod-iam-diu-1918-italian",
      "source": "https://www.vatican.va/content/benedict-xv/it/encyclicals/documents/hf_ben-xv_enc_01121918_quod-iam-diu.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/benedict-xv/en/encyclicals/documents/hf_ben-xv_enc_01121918_quod-iam-diu.html',
  notes: "本篤十五世於 1917-08-01 提出「七點和平方案」（Note pacem），雖獲德奧支持但被英法美拒絕。教廷未獲邀參加巴黎和會是一戰外交史的重要事件。",
}
