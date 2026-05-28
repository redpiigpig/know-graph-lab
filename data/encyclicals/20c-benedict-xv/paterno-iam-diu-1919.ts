import type { PapalDocument } from '../types'

export const paternoIamDiu1919: PapalDocument = {
  slug: 'paterno-iam-diu-1919',
  popeSlug: 'benedict-xv',
  category: 'encyclical',
  titleLat: 'Paterno Iam Diu',
  titleEn: 'On the Children of Central Europe',
  titleZh: '《如父般》通諭 — 論戰後中歐兒童救援',
  promulgationDate: '1919-11-24',
  century: 20,
  summaryZh: "本篤十五世為中歐戰後兒童救援呼籲的短通諭。一戰結束後中歐（特別是德國、奧地利）糧食短缺、兒童飢餓嚴重，教廷透過國際渠道籌款救援。",
  topics: ["戰後救援", "中歐兒童", "人道援助"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "paterno-iam-diu-1919-chinese",
      "source": "https://www.vatican.va/content/dam/benedict-xv/pdf/encyclicals/documents/hf_ben-xv_enc_24111919_paterno-iam-diu_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "paterno-iam-diu-1919-english",
      "source": "https://www.vatican.va/content/benedict-xv/en/encyclicals/documents/hf_ben-xv_enc_24111919_paterno-iam-diu.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "paterno-iam-diu-1919-latin",
      "source": "https://www.vatican.va/content/benedict-xv/la/encyclicals/documents/hf_ben-xv_enc_24111919_paterno-iam-diu.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "paterno-iam-diu-1919-italian",
      "source": "https://www.vatican.va/content/benedict-xv/it/encyclicals/documents/hf_ben-xv_enc_24111919_paterno-iam-diu.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/benedict-xv/en/encyclicals/documents/hf_ben-xv_enc_24111919_paterno-iam-diu.html',
  notes: "",
}
