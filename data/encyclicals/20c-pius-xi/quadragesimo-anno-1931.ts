import type { PapalDocument } from '../types'

export const quadragesimoAnno1931: PapalDocument = {
  slug: 'quadragesimo-anno-1931',
  popeSlug: 'pius-xi',
  category: 'encyclical',
  titleLat: 'Quadragesimo Anno',
  titleEn: 'On the Reconstruction of the Social Order',
  titleZh: '《第四十年》通諭 — 論重建社會秩序',
  promulgationDate: '1931-05-15',
  century: 20,
  summaryZh: "碧岳十一世論社會的開創性通諭，紀念良十三《新事》通諭頒布 40 週年。對 1929 經濟大蕭條提出回應。\n\n首次系統提出「補助原則」（subsidiarité, subsidiaritas）——更高層級的社會團體不應取代更低層級可勝任的事務。這個概念後成為天主教社會訓導的核心原則之一，也成為歐盟（EU）建構的法律基礎。",
  topics: ["社會訓導", "補助原則", "經濟大蕭條", "工團主義", "資本主義批判"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "quadragesimo-anno-1931-chinese",
      "source": "https://www.vatican.va/content/dam/pius-xi/pdf/encyclicals/documents/hf_p-xi_enc_19310515_quadragesimo-anno_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "quadragesimo-anno-1931-english",
      "source": "https://www.vatican.va/content/pius-xi/en/encyclicals/documents/hf_p-xi_enc_19310515_quadragesimo-anno.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "quadragesimo-anno-1931-latin",
      "source": "https://www.vatican.va/content/pius-xi/la/encyclicals/documents/hf_p-xi_enc_19310515_quadragesimo-anno.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "quadragesimo-anno-1931-italian",
      "source": "https://www.vatican.va/content/pius-xi/it/encyclicals/documents/hf_p-xi_enc_19310515_quadragesimo-anno.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-xi/en/encyclicals/documents/hf_p-xi_enc_19310515_quadragesimo-anno.html',
  notes: "簽署日 1931-05-15 為《新事》通諭頒布 40 週年（1891-05-15）。\n\n「補助原則」（subsidiarity）是本通諭最具歷史影響力的概念，後被歐盟《馬斯垂克條約》（1992）採用為其組織原則。",
}
