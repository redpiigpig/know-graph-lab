import type { PapalDocument } from '../types'

export const princepsPastorum1959: PapalDocument = {
  slug: 'princeps-pastorum-1959',
  popeSlug: 'john-xxiii',
  category: 'encyclical',
  titleLat: 'Princeps Pastorum',
  titleEn: 'On the Missions, Native Clergy, and Lay Participation',
  titleZh: '《牧者之首》通諭 — 論傳教、本地神職與平信徒參與',
  promulgationDate: '1959-11-28',
  century: 20,
  summaryZh: "若望二十三世第四道通諭，紀念本篤十五《最大的事》通諭（Maximum Illud 1919，傳教本地化先聲）頒布 40 週年。強調傳教不是西方文化的延伸，而需要本地神職與平信徒的全面參與。",
  topics: ["傳教神學", "本地化", "本地神職", "平信徒參與"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "princeps-pastorum-1959-chinese",
      "source": "https://www.vatican.va/content/dam/john-xxiii/pdf/encyclicals/documents/hf_j-xxiii_enc_28111959_princeps_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "princeps-pastorum-1959-english",
      "source": "https://www.vatican.va/content/john-xxiii/en/encyclicals/documents/hf_j-xxiii_enc_28111959_princeps.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "princeps-pastorum-1959-latin",
      "source": "https://www.vatican.va/content/john-xxiii/la/encyclicals/documents/hf_j-xxiii_enc_28111959_princeps.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "princeps-pastorum-1959-italian",
      "source": "https://www.vatican.va/content/john-xxiii/it/encyclicals/documents/hf_j-xxiii_enc_28111959_princeps.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/john-xxiii/en/encyclicals/documents/hf_j-xxiii_enc_28111959_princeps.html',
  notes: "",
}
