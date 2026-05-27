import type { PapalDocument } from '../types'

export const ecclesiamSuam1964: PapalDocument = {
  slug: 'ecclesiam-suam-1964',
  popeSlug: 'paul-vi',
  category: 'encyclical',
  titleLat: 'Ecclesiam Suam',
  titleEn: 'His Church',
  titleZh: '《祂的教會》通諭 — 論教會自我認識與對話',
  promulgationDate: '1964-08-06',
  century: 20,
  summaryZh: "保祿六世第一道通諭，於梵二第三會期前夕頒布，被視為梵二「對話神學」的先聲。\n\n核心命題：教會需要透過三層對話來理解自身——與天主對話（祈禱／靈修）、與基督徒對話（合一運動）、與世界對話（傳教／社會議題）。通諭首次系統使用「對話」（colloquium）作為教會神學方法論。",
  topics: ["對話神學", "教會學", "梵二", "合一運動", "對外開放"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "ecclesiam-suam-1964-chinese",
      "source": "https://www.vatican.va/content/dam/paul-vi/pdf/encyclicals/documents/hf_p-vi_enc_06081964_ecclesiam_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "ecclesiam-suam-1964-english",
      "source": "https://www.vatican.va/content/paul-vi/en/encyclicals/documents/hf_p-vi_enc_06081964_ecclesiam.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "ecclesiam-suam-1964-latin",
      "source": "https://www.vatican.va/content/paul-vi/la/encyclicals/documents/hf_p-vi_enc_06081964_ecclesiam.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "ecclesiam-suam-1964-italian",
      "source": "https://www.vatican.va/content/paul-vi/it/encyclicals/documents/hf_p-vi_enc_06081964_ecclesiam.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/paul-vi/en/encyclicals/documents/hf_p-vi_enc_06081964_ecclesiam.html',
  notes: "簽署日 1964-08-06 為主顯聖容節，象徵教會「在改變中保持本貌」。",
}
