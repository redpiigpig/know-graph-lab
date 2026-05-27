import type { PapalDocument } from '../types'

export const paenitentiamAgere1962: PapalDocument = {
  slug: 'paenitentiam-agere-1962',
  popeSlug: 'john-xxiii',
  category: 'encyclical',
  titleLat: 'Paenitentiam Agere',
  titleEn: 'On the Need for Penance for the Success of the Council',
  titleZh: '《行補贖》通諭 — 論為梵二大公會議的成功補贖',
  promulgationDate: '1962-07-01',
  century: 20,
  summaryZh: "若望二十三世第七道通諭，於梵二大公會議 1962-10 開幕前 3 個月頒布，呼籲信徒以祈禱、補贖、克己為梵二籌備工作的精神靈修支撐。",
  topics: ["補贖", "梵二籌備", "祈禱"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "paenitentiam-agere-1962-chinese",
      "source": "https://www.vatican.va/content/dam/john-xxiii/pdf/encyclicals/documents/hf_j-xxiii_enc_01071962_paenitentiam_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "paenitentiam-agere-1962-english",
      "source": "https://www.vatican.va/content/john-xxiii/en/encyclicals/documents/hf_j-xxiii_enc_01071962_paenitentiam.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "paenitentiam-agere-1962-latin",
      "source": "https://www.vatican.va/content/john-xxiii/la/encyclicals/documents/hf_j-xxiii_enc_01071962_paenitentiam.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "paenitentiam-agere-1962-italian",
      "source": "https://www.vatican.va/content/john-xxiii/it/encyclicals/documents/hf_j-xxiii_enc_01071962_paenitentiam.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/john-xxiii/en/encyclicals/documents/hf_j-xxiii_enc_01071962_paenitentiam.html',
  notes: "",
}
