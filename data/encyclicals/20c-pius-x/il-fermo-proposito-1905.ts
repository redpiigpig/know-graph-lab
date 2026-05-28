import type { PapalDocument } from '../types'

export const ilFermoProposito1905: PapalDocument = {
  slug: 'il-fermo-proposito-1905',
  popeSlug: 'pius-x',
  category: 'encyclical',
  titleLat: 'Il Fermo Proposito',
  titleEn: 'On Catholic Action in Italy',
  titleZh: '《堅定的決意》通諭 — 論意大利天主教 Action',
  promulgationDate: '1905-06-11',
  century: 20,
  summaryZh: "碧岳十世論「天主教 Action」（Azione Cattolica）的義大利文通諭。在 1870 年義大利統一、教廷國終結的「羅馬議題」（Questione Romana）下，碧岳十世調整碧岳九世時代對天主教徒參與義大利政治生活的全面禁令，准許「天主教 Action」這類社會運動組織。",
  topics: ["天主教 Action", "義大利", "教會與國家", "平信徒運動"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "il-fermo-proposito-1905-chinese",
      "source": "https://www.vatican.va/content/dam/pius-x/pdf/encyclicals/documents/hf_p-x_enc_11061905_il-fermo-proposito_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "il-fermo-proposito-1905-english",
      "source": "https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_11061905_il-fermo-proposito.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "il-fermo-proposito-1905-latin",
      "source": "https://www.vatican.va/content/pius-x/la/encyclicals/documents/hf_p-x_enc_11061905_il-fermo-proposito.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "il-fermo-proposito-1905-italian",
      "source": "https://www.vatican.va/content/pius-x/it/encyclicals/documents/hf_p-x_enc_11061905_il-fermo-proposito.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_11061905_il-fermo-proposito.html',
  notes: "本通諭以義大利文（而非拉丁文）原文頒布，反映其僅針對義大利教會的特殊背景。",
}
