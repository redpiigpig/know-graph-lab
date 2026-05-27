import type { PapalDocument } from '../types'

export const divinoAfflanteSpiritu1943: PapalDocument = {
  slug: 'divino-afflante-spiritu-1943',
  popeSlug: 'pius-xii',
  category: 'encyclical',
  titleLat: 'Divino Afflante Spiritu',
  titleEn: 'On Promoting Biblical Studies',
  titleZh: '《奉神感發》通諭 — 論聖經研究',
  promulgationDate: '1943-09-30',
  century: 20,
  summaryZh: "碧岳十二世第四道通諭，紀念良十三《天主上智》（Providentissimus Deus 1893）頒布 50 週年。是 20 世紀天主教聖經研究的「大憲章」。\n\n核心命題：聖經學者應採用現代「文體批判」（formgeschichtliche Methode）、「歷史考據」（critica historica）等學術方法；翻譯聖經應使用希伯來文／希臘文原文而非僅 Vulgate 拉丁譯本。本通諭解除了 1907 年現代主義危機後對天主教聖經學的諸多限制，為梵二《天主啟示憲章》（Dei Verbum 1965）鋪路。",
  topics: ["聖經研究", "歷史考據", "文體批判", "現代主義回應", "聖經翻譯"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "divino-afflante-spiritu-1943-chinese",
      "source": "https://www.vatican.va/content/dam/pius-xii/pdf/encyclicals/documents/hf_p-xii_enc_30091943_divino-afflante-spiritu_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "divino-afflante-spiritu-1943-english",
      "source": "https://www.vatican.va/content/pius-xii/en/encyclicals/documents/hf_p-xii_enc_30091943_divino-afflante-spiritu.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "divino-afflante-spiritu-1943-latin",
      "source": "https://www.vatican.va/content/pius-xii/la/encyclicals/documents/hf_p-xii_enc_30091943_divino-afflante-spiritu.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "divino-afflante-spiritu-1943-italian",
      "source": "https://www.vatican.va/content/pius-xii/it/encyclicals/documents/hf_p-xii_enc_30091943_divino-afflante-spiritu.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-xii/en/encyclicals/documents/hf_p-xii_enc_30091943_divino-afflante-spiritu.html',
  notes: "簽署日 1943-09-30 為聖熱羅尼莫紀念日（Vulgate 譯者）。本通諭是天主教聖經學現代化的轉捩點，常與《奧體》《天主上智》合稱「現代聖經學三道通諭」。",
}
