import type { PapalDocument } from '../types'

export const populorumProgressio1967: PapalDocument = {
  slug: 'populorum-progressio-1967',
  popeSlug: 'paul-vi',
  category: 'encyclical',
  titleLat: 'Populorum Progressio',
  titleEn: 'On the Development of Peoples',
  titleZh: '《民族發展》通諭',
  promulgationDate: '1967-03-26',
  century: 20,
  summaryZh: "保祿六世第五道通諭，亦是其最重要的社會通諭。提出「發展是和平的新名字」（development is the new name for peace），為冷戰末期天主教社會訓導奠下整體發展框架。\n\n核心命題：發展不可化約為經濟增長，而是「整體性的人類發展」（sviluppo integrale）—包括物質、文化、精神各層面。對國際組織、富國對窮國的責任、自由貿易的倫理限度等議題提出全面分析。",
  topics: ["社會訓導", "整體發展", "南北經濟差距", "國際正義"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "populorum-progressio-1967-chinese",
      "source": "https://www.vatican.va/content/dam/paul-vi/pdf/encyclicals/documents/hf_p-vi_enc_26031967_populorum_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "populorum-progressio-1967-english",
      "source": "https://www.vatican.va/content/paul-vi/en/encyclicals/documents/hf_p-vi_enc_26031967_populorum.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "populorum-progressio-1967-latin",
      "source": "https://www.vatican.va/content/paul-vi/la/encyclicals/documents/hf_p-vi_enc_26031967_populorum.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "populorum-progressio-1967-italian",
      "source": "https://www.vatican.va/content/paul-vi/it/encyclicals/documents/hf_p-vi_enc_26031967_populorum.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/paul-vi/en/encyclicals/documents/hf_p-vi_enc_26031967_populorum.html',
  notes: "簽署日 1967-03-26 為復活節。本通諭標誌保祿六世社會思想的高峰，是若望保祿二《關懷社會事務》、本篤十六《在真理中實踐愛德》、方濟各《眾位弟兄》三道社會通諭的共同源頭。",
}
