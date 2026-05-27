import type { PapalDocument } from '../types'

export const veritatisSplendor1993: PapalDocument = {
  slug: 'veritatis-splendor-1993',
  popeSlug: 'john-paul-ii',
  category: 'encyclical',
  titleLat: 'Veritatis Splendor',
  titleEn: 'The Splendor of Truth',
  titleZh: '《真理的光輝》通諭 — 論教會倫理訓導的根本問題',
  promulgationDate: '1993-08-06',
  century: 20,
  summaryZh: "若望保祿二世第十道通諭，作為《天主教教理》（1992 拉文版）的同期姊妹文件，系統處理倫理神學基礎問題。\n\n核心命題：反對 1960-80 年代「比例論」（proportionalism / consequentialism）倫理思潮。第 79-83 段確認「內在惡」（intrinsece malum）的存在：某些行為（如謀殺、墮胎、酷刑、奴隸制等）因其對象本身即與人位格尊嚴對立，無論動機或情境都不可被視為善。\n\n與後續《生命福音》（1995）構成「為生命倫理／反相對主義」雙聯通諭。",
  topics: ["倫理神學", "內在惡", "比例論批判", "良心", "天主教教理"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "veritatis-splendor-1993-chinese",
      "source": "https://www.vatican.va/content/dam/john-paul-ii/pdf/encyclicals/documents/hf_jp-ii_enc_06081993_veritatis-splendor_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "veritatis-splendor-1993-english",
      "source": "https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_06081993_veritatis-splendor.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "veritatis-splendor-1993-latin",
      "source": "https://www.vatican.va/content/john-paul-ii/la/encyclicals/documents/hf_jp-ii_enc_06081993_veritatis-splendor.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "veritatis-splendor-1993-italian",
      "source": "https://www.vatican.va/content/john-paul-ii/it/encyclicals/documents/hf_jp-ii_enc_06081993_veritatis-splendor.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_06081993_veritatis-splendor.html',
  notes: "簽署日 1993-08-06 為主顯聖容節，象徵「真理之光在基督面上顯現」。本通諭預備工作達 5 年，由 CDF 信理部長拉辛格樞機（後本篤十六世）主筆協助。",
}
