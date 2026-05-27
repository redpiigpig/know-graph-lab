import type { PapalDocument } from '../types'

export const redemptorisMater1987: PapalDocument = {
  slug: 'redemptoris-mater-1987',
  popeSlug: 'john-paul-ii',
  category: 'encyclical',
  titleLat: 'Redemptoris Mater',
  titleEn: 'Mother of the Redeemer',
  titleZh: '《救主之母》通諭 — 論聖母瑪利亞',
  promulgationDate: '1987-03-25',
  century: 20,
  summaryZh: "若望保祿二世第六道通諭，論聖母瑪利亞。為紀念 1987-88 年「瑪利亞年」（Annus Marialis）而頒布。\n\n通諭以「信德旅程」（peregrinatio fidei）為核心比喻，把瑪利亞描繪為走在教會前頭的信德典範，承接梵二《教會憲章》第八章對聖母論的更新。",
  topics: ["聖母論", "瑪利亞年", "信德旅程", "教會學"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "redemptoris-mater-1987-chinese",
      "source": "https://www.vatican.va/content/dam/john-paul-ii/pdf/encyclicals/documents/hf_jp-ii_enc_25031987_redemptoris-mater_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "redemptoris-mater-1987-english",
      "source": "https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_25031987_redemptoris-mater.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "redemptoris-mater-1987-latin",
      "source": "https://www.vatican.va/content/john-paul-ii/la/encyclicals/documents/hf_jp-ii_enc_25031987_redemptoris-mater.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "redemptoris-mater-1987-italian",
      "source": "https://www.vatican.va/content/john-paul-ii/it/encyclicals/documents/hf_jp-ii_enc_25031987_redemptoris-mater.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_25031987_redemptoris-mater.html',
  notes: "簽署日 1987-03-25 為聖母領報節，與聖母題材呼應。",
}
