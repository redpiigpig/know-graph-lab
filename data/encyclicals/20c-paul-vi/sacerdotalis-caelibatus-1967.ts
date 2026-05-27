import type { PapalDocument } from '../types'

export const sacerdotalisCaelibatus1967: PapalDocument = {
  slug: 'sacerdotalis-caelibatus-1967',
  popeSlug: 'paul-vi',
  category: 'encyclical',
  titleLat: 'Sacerdotalis Caelibatus',
  titleEn: 'On Priestly Celibacy',
  titleZh: '《司鐸獨身》通諭',
  promulgationDate: '1967-06-24',
  century: 20,
  summaryZh: "保祿六世第六道通諭，重申天主教拉丁禮司鐸獨身傳統。回應梵二後內部對「廢除獨身要求」的呼籲，肯定獨身為「對天國的見證」（憲憲）並提出歷史性、神學性、牧靈性論證。",
  topics: ["司鐸獨身", "聖職神學", "梵二接續"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "sacerdotalis-caelibatus-1967-chinese",
      "source": "https://www.vatican.va/content/dam/paul-vi/pdf/encyclicals/documents/hf_p-vi_enc_24061967_sacerdotalis_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "sacerdotalis-caelibatus-1967-english",
      "source": "https://www.vatican.va/content/paul-vi/en/encyclicals/documents/hf_p-vi_enc_24061967_sacerdotalis.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "sacerdotalis-caelibatus-1967-latin",
      "source": "https://www.vatican.va/content/paul-vi/la/encyclicals/documents/hf_p-vi_enc_24061967_sacerdotalis.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "sacerdotalis-caelibatus-1967-italian",
      "source": "https://www.vatican.va/content/paul-vi/it/encyclicals/documents/hf_p-vi_enc_24061967_sacerdotalis.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/paul-vi/en/encyclicals/documents/hf_p-vi_enc_24061967_sacerdotalis.html',
  notes: "",
}
