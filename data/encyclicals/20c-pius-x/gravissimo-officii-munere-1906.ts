import type { PapalDocument } from '../types'

export const gravissimoOfficiiMunere1906: PapalDocument = {
  slug: 'gravissimo-officii-munere-1906',
  popeSlug: 'pius-x',
  category: 'encyclical',
  titleLat: 'Gravissimo Officii Munere',
  titleEn: 'On French Associations of Worship',
  titleZh: '《最重職責》通諭 — 進一步論法國政教分離法',
  promulgationDate: '1906-08-10',
  century: 20,
  summaryZh: "碧岳十世繼續處理法國政教分離（《我們強烈》1906-02-11）議題的通諭。明確指示法國天主教不接受 1905 政教分離法所規定的「禮拜協會」（associations cultuelles）作為教會財產管理形式——避免讓政府透過協會章程實質控制教會內部事務。",
  topics: ["法國政教分離", "禮拜協會拒絕", "教會自治"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "gravissimo-officii-munere-1906-chinese",
      "source": "https://www.vatican.va/content/dam/pius-x/pdf/encyclicals/documents/hf_p-x_enc_10081906_gravissimo-officii-munere_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "gravissimo-officii-munere-1906-english",
      "source": "https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_10081906_gravissimo-officii-munere.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "gravissimo-officii-munere-1906-latin",
      "source": "https://www.vatican.va/content/pius-x/la/encyclicals/documents/hf_p-x_enc_10081906_gravissimo-officii-munere.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "gravissimo-officii-munere-1906-italian",
      "source": "https://www.vatican.va/content/pius-x/it/encyclicals/documents/hf_p-x_enc_10081906_gravissimo-officii-munere.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_10081906_gravissimo-officii-munere.html',
  notes: "本通諭與《我們強烈》《再一次》（Une Fois Encore 1907）共同構成碧岳十世對法國政教分離爭議的三道相關通諭。",
}
