import type { PapalDocument } from '../types'

export const iamdudum1911: PapalDocument = {
  slug: 'iamdudum-1911',
  popeSlug: 'pius-x',
  category: 'encyclical',
  titleLat: 'Iamdudum',
  titleEn: 'On the Law of Separation in Portugal',
  titleZh: '《久已》通諭 — 譴責葡萄牙 1911 政教分離法',
  promulgationDate: '1911-05-24',
  century: 20,
  summaryZh: "碧岳十世譴責葡萄牙第一共和（1910-）所通過 1911 年「政教分離法」的通諭。葡萄牙於 1910-10-05 推翻君主制建立共和後，採行類似法國 1905 政教分離模式的全面世俗化政策。",
  topics: ["葡萄牙政教分離", "教會與國家", "世俗化批判"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "iamdudum-1911-chinese",
      "source": "https://www.vatican.va/content/dam/pius-x/pdf/encyclicals/documents/hf_p-x_enc_24051911_iamdudum_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "iamdudum-1911-english",
      "source": "https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_24051911_iamdudum.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "iamdudum-1911-latin",
      "source": "https://www.vatican.va/content/pius-x/la/encyclicals/documents/hf_p-x_enc_24051911_iamdudum.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "iamdudum-1911-italian",
      "source": "https://www.vatican.va/content/pius-x/it/encyclicals/documents/hf_p-x_enc_24051911_iamdudum.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_24051911_iamdudum.html',
  notes: "本通諭與《我們強烈》（1906）法國政教分離立場一脈相承。",
}
