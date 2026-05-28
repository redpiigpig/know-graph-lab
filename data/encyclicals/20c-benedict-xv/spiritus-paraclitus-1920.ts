import type { PapalDocument } from '../types'

export const spiritusParaclitus1920: PapalDocument = {
  slug: 'spiritus-paraclitus-1920',
  popeSlug: 'benedict-xv',
  category: 'encyclical',
  titleLat: 'Spiritus Paraclitus',
  titleEn: 'On St. Jerome',
  titleZh: '《護慰之神》通諭 — 紀念聖熱羅尼莫逝世 1500 週年，論聖經',
  promulgationDate: '1920-09-15',
  century: 20,
  summaryZh: "本篤十五世紀念聖熱羅尼莫（Jerome, 347-420，Vulgate 拉丁譯本譯者、教會聖師）逝世 1500 週年的通諭。\n\n承續良十三《天主上智》（Providentissimus Deus 1893）論聖經默感的訓導路線。本通諭強調聖經整體無誤（inerrancy）的傳統立場，與當時 19 世紀末起興起的「歷史考據聖經學」對話。後於碧岳十二《奉神感發》（1943）獲得更新平衡。",
  topics: ["聖熱羅尼莫", "聖經", "默感", "Vulgate"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "spiritus-paraclitus-1920-chinese",
      "source": "https://www.vatican.va/content/dam/benedict-xv/pdf/encyclicals/documents/hf_ben-xv_enc_15091920_spiritus-paraclitus_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "spiritus-paraclitus-1920-english",
      "source": "https://www.vatican.va/content/benedict-xv/en/encyclicals/documents/hf_ben-xv_enc_15091920_spiritus-paraclitus.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "spiritus-paraclitus-1920-latin",
      "source": "https://www.vatican.va/content/benedict-xv/la/encyclicals/documents/hf_ben-xv_enc_15091920_spiritus-paraclitus.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "spiritus-paraclitus-1920-italian",
      "source": "https://www.vatican.va/content/benedict-xv/it/encyclicals/documents/hf_ben-xv_enc_15091920_spiritus-paraclitus.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/benedict-xv/en/encyclicals/documents/hf_ben-xv_enc_15091920_spiritus-paraclitus.html',
  notes: "本通諭與良十三《天主上智》（1893）、碧岳十二《奉神感發》（1943）並列為天主教「聖經學三大通諭」。",
}
