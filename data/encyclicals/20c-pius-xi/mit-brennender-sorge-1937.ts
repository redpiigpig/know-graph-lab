import type { PapalDocument } from '../types'

export const mitBrennenderSorge1937: PapalDocument = {
  slug: 'mit-brennender-sorge-1937',
  popeSlug: 'pius-xi',
  category: 'encyclical',
  titleLat: 'Mit Brennender Sorge',
  titleEn: 'On the Church and the German Reich',
  titleZh: '《充滿燃燒的憂慮》通諭 — 論納粹德國對教會的迫害',
  promulgationDate: '1937-03-14',
  century: 20,
  summaryZh: "碧岳十一世明確譴責納粹政權的歷史性通諭，是其少數以德語頒布的通諭（直接面向德國信徒）。\n\n通諭譴責納粹的「種族至上」「血與土」（Blut und Boden）意識形態、毀約（1933 羅馬教廷－納粹政教條約）、迫害基督徒等行為。在德國各教堂於 1937 年聖枝主日同時宣讀，是 20 世紀天主教對極權主義最直接的譴責文件。",
  topics: ["反納粹", "反種族主義", "極權批判", "戰前訓導"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "mit-brennender-sorge-1937-chinese",
      "source": "https://www.vatican.va/content/dam/pius-xi/pdf/encyclicals/documents/hf_p-xi_enc_14031937_mit-brennender-sorge_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "mit-brennender-sorge-1937-english",
      "source": "https://www.vatican.va/content/pius-xi/en/encyclicals/documents/hf_p-xi_enc_14031937_mit-brennender-sorge.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "mit-brennender-sorge-1937-latin",
      "source": "https://www.vatican.va/content/pius-xi/la/encyclicals/documents/hf_p-xi_enc_14031937_mit-brennender-sorge.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "mit-brennender-sorge-1937-italian",
      "source": "https://www.vatican.va/content/pius-xi/it/encyclicals/documents/hf_p-xi_enc_14031937_mit-brennender-sorge.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-xi/en/encyclicals/documents/hf_p-xi_enc_14031937_mit-brennender-sorge.html',
  notes: "簽署日 1937-03-14 為四旬期第四主日。通諭手稿通過秘密管道從梵蒂岡運入德國，在各教堂的 1937-03-21（聖枝主日）同時宣讀，使蓋世太保來不及阻止。\n\n蓋世太保事後沒收所有印刷品，並逮捕涉嫌散播的神父。",
}
