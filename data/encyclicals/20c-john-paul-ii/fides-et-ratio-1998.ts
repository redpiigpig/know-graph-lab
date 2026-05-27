import type { PapalDocument } from '../types'

export const fidesEtRatio1998: PapalDocument = {
  slug: 'fides-et-ratio-1998',
  popeSlug: 'john-paul-ii',
  category: 'encyclical',
  titleLat: 'Fides et Ratio',
  titleEn: 'Faith and Reason',
  titleZh: '《信仰與理性》通諭 — 論信仰與理性的關係',
  promulgationDate: '1998-09-14',
  century: 20,
  summaryZh: "若望保祿二世第十三道通諭，論信仰與理性的關係，作為新世紀來臨前的神學總結。\n\n通諭開篇名言：「信仰與理性是人類精神升騰至默觀真理的兩翼。」核心命題：基督信仰需要哲學，哲學需要信仰；反駁現代「理性主義／信仰主義」二極化，亦反對後現代相對主義對「真理」的取消。\n\n本文件對天主教學界產生深遠影響，被視為若望保祿二世「哲學家教宗」（前 Kraków 大學哲學教授）身份的訓導巔峰之作。",
  topics: ["神哲學", "信仰與理性", "後現代批判", "教父傳統", "多瑪斯主義"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "fides-et-ratio-1998-chinese",
      "source": "https://www.vatican.va/content/dam/john-paul-ii/pdf/encyclicals/documents/hf_jp-ii_enc_14091998_fides-et-ratio_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "fides-et-ratio-1998-english",
      "source": "https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_14091998_fides-et-ratio.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "fides-et-ratio-1998-latin",
      "source": "https://www.vatican.va/content/john-paul-ii/la/encyclicals/documents/hf_jp-ii_enc_14091998_fides-et-ratio.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "fides-et-ratio-1998-italian",
      "source": "https://www.vatican.va/content/john-paul-ii/it/encyclicals/documents/hf_jp-ii_enc_14091998_fides-et-ratio.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_14091998_fides-et-ratio.html',
  notes: "簽署日 1998-09-14 為光榮十字聖架慶日，象徵「理性面對基督苦難的奧蹟」。\n\n本通諭與其前任本篤十六世（時任 CDF 信理部長拉辛格樞機）的神學取向高度一致；拉辛格 2006 雷根斯堡演講「信仰、理性與大學」是其延伸。",
}
