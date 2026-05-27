import type { PapalDocument } from '../types'

export const humanaeVitae1968: PapalDocument = {
  slug: 'humanae-vitae-1968',
  popeSlug: 'paul-vi',
  category: 'encyclical',
  titleLat: 'Humanae Vitae',
  titleEn: 'On Human Life',
  titleZh: '《人類生命》通諭 — 論婚姻與生育之倫理',
  promulgationDate: '1968-07-25',
  century: 20,
  summaryZh: "保祿六世第七道、最後一道通諭，亦是其在位最具爭議性的訓導文件。\n\n核心命題：婚姻內的性行為「不可分割地包含結合（unitive）與生育（procreative）兩個目的」；任何意圖排除生育的人工避孕方式都違反此自然秩序。本通諭預示了若望保祿二世「身體神學」（Theology of the Body）後續發展。\n\n通諭頒布後引發西方天主教界激烈反對（含主教團集體抗議）、保祿六世本人因此再無新通諭頒布。雖被現代世俗社會視為「保守」，本通諭亦被環境主義／反消費主義者重新評價為對「身體商品化」的早期批判。",
  topics: ["人類生命", "避孕", "性倫理", "婚姻", "身體神學"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "humanae-vitae-1968-chinese",
      "source": "https://www.vatican.va/content/dam/paul-vi/pdf/encyclicals/documents/hf_p-vi_enc_25071968_humanae-vitae_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "humanae-vitae-1968-english",
      "source": "https://www.vatican.va/content/paul-vi/en/encyclicals/documents/hf_p-vi_enc_25071968_humanae-vitae.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "humanae-vitae-1968-latin",
      "source": "https://www.vatican.va/content/paul-vi/la/encyclicals/documents/hf_p-vi_enc_25071968_humanae-vitae.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "humanae-vitae-1968-italian",
      "source": "https://www.vatican.va/content/paul-vi/it/encyclicals/documents/hf_p-vi_enc_25071968_humanae-vitae.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/paul-vi/en/encyclicals/documents/hf_p-vi_enc_25071968_humanae-vitae.html',
  notes: "簽署日 1968-07-25 為聖雅各（長）瞻禮。\n\n本通諭草擬歷時數年，保祿六世在 1966 年「教宗特設委員會」多數意見（贊成允許某些避孕方式）下，仍堅持傳統訓導。此舉成為 20 世紀末天主教「訓導／權威」議題討論的關鍵案例。",
}
