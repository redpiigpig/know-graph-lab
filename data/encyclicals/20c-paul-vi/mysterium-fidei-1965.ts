import type { PapalDocument } from '../types'

export const mysteriumFidei1965: PapalDocument = {
  slug: 'mysterium-fidei-1965',
  popeSlug: 'paul-vi',
  category: 'encyclical',
  titleLat: 'Mysterium Fidei',
  titleEn: 'The Mystery of Faith',
  titleZh: '《信德的奧蹟》通諭 — 論聖體聖事',
  promulgationDate: '1965-09-03',
  century: 20,
  summaryZh: "保祿六世第三道通諭，於梵二第四會期前夕頒布，重申天主教傳統「實體變化」（transsubstantiatio）教義。\n\n回應 1960 年代戰後神學家提出的「變意說」（transsignificatio）、「變目的說」（transfinalizatio）對特利騰大公會議聖體教義的挑戰。",
  topics: ["聖體聖事", "實體變化", "梵二", "特利騰傳統"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "mysterium-fidei-1965-chinese",
      "source": "https://www.vatican.va/content/dam/paul-vi/pdf/encyclicals/documents/hf_p-vi_enc_03091965_mysterium_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "mysterium-fidei-1965-english",
      "source": "https://www.vatican.va/content/paul-vi/en/encyclicals/documents/hf_p-vi_enc_03091965_mysterium.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "mysterium-fidei-1965-latin",
      "source": "https://www.vatican.va/content/paul-vi/la/encyclicals/documents/hf_p-vi_enc_03091965_mysterium.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "mysterium-fidei-1965-italian",
      "source": "https://www.vatican.va/content/paul-vi/it/encyclicals/documents/hf_p-vi_enc_03091965_mysterium.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/paul-vi/en/encyclicals/documents/hf_p-vi_enc_03091965_mysterium.html',
  notes: "",
}
