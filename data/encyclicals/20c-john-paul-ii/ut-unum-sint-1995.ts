import type { PapalDocument } from '../types'

export const utUnumSint1995: PapalDocument = {
  slug: 'ut-unum-sint-1995',
  popeSlug: 'john-paul-ii',
  category: 'encyclical',
  titleLat: 'Ut Unum Sint',
  titleEn: 'That They May Be One',
  titleZh: '《願他們合而為一》通諭 — 論教會合一',
  promulgationDate: '1995-05-25',
  century: 20,
  summaryZh: "若望保祿二世第十二道通諭，是首道以「合一運動」（oecumenismus）為主題的通諭。承襲梵二《大公主義法令》（Unitatis Redintegratio 1964）。\n\n通諭最具突破性的部分在第 88-96 段：若望保祿二世主動邀請其他教會領袖共同尋找「教宗職權」（munus papale）的新行使形式 — 在保持訓導職權實質的同時，探討如何讓伯多祿職權在合一中為大家所能接受。這項邀請至今仍是天主教—正教、天主教—新教合一對話的核心議題。",
  topics: ["合一運動", "教宗職權", "東正教", "新教", "Unitatis Redintegratio"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "ut-unum-sint-1995-chinese",
      "source": "https://www.vatican.va/content/dam/john-paul-ii/pdf/encyclicals/documents/hf_jp-ii_enc_25051995_ut-unum-sint_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "ut-unum-sint-1995-english",
      "source": "https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_25051995_ut-unum-sint.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "ut-unum-sint-1995-latin",
      "source": "https://www.vatican.va/content/john-paul-ii/la/encyclicals/documents/hf_jp-ii_enc_25051995_ut-unum-sint.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "ut-unum-sint-1995-italian",
      "source": "https://www.vatican.va/content/john-paul-ii/it/encyclicals/documents/hf_jp-ii_enc_25051995_ut-unum-sint.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_25051995_ut-unum-sint.html',
  notes: "簽署日 1995-05-25 為基督升天節（C 年）。題名典出〈若望福音〉17:21 耶穌大司祭祈禱「願眾人都合而為一」。",
}
