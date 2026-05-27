import type { PapalDocument } from '../types'

export const materEtMagistra1961: PapalDocument = {
  slug: 'mater-et-magistra-1961',
  popeSlug: 'john-xxiii',
  category: 'encyclical',
  titleLat: 'Mater et Magistra',
  titleEn: 'Mother and Teacher',
  titleZh: '《慈母與導師》通諭 — 論晚近社會發展',
  promulgationDate: '1961-05-15',
  century: 20,
  summaryZh: "若望二十三世第五道通諭，紀念良十三《新事》通諭頒布 70 週年。將天主教社會訓導從 19 世紀工人權利議題擴展到 20 世紀中葉的議題：農業現代化、發展中國家、社會保險、全球化等。\n\n首次提出「社會化」（socializatio）概念—社會關係日益密集、複雜的現代趨勢，並評估此趨勢對個人自由與社會團體的雙向影響。",
  topics: ["社會訓導", "社會化", "農業現代化", "發展中國家"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "mater-et-magistra-1961-chinese",
      "source": "https://www.vatican.va/content/dam/john-xxiii/pdf/encyclicals/documents/hf_j-xxiii_enc_15051961_mater_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "mater-et-magistra-1961-english",
      "source": "https://www.vatican.va/content/john-xxiii/en/encyclicals/documents/hf_j-xxiii_enc_15051961_mater.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "mater-et-magistra-1961-latin",
      "source": "https://www.vatican.va/content/john-xxiii/la/encyclicals/documents/hf_j-xxiii_enc_15051961_mater.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "mater-et-magistra-1961-italian",
      "source": "https://www.vatican.va/content/john-xxiii/it/encyclicals/documents/hf_j-xxiii_enc_15051961_mater.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/john-xxiii/en/encyclicals/documents/hf_j-xxiii_enc_15051961_mater.html',
  notes: "簽署日 1961-05-15 為《新事》通諭頒布 70 週年（1891-05-15）。",
}
