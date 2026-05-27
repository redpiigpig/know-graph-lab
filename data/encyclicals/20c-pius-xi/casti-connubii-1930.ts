import type { PapalDocument } from '../types'

export const castiConnubii1930: PapalDocument = {
  slug: 'casti-connubii-1930',
  popeSlug: 'pius-xi',
  category: 'encyclical',
  titleLat: 'Casti Connubii',
  titleEn: 'On Christian Marriage',
  titleZh: '《貞潔的婚姻》通諭 — 論基督徒婚姻',
  promulgationDate: '1930-12-31',
  century: 20,
  summaryZh: "碧岳十一世論婚姻的系統性通諭。回應 1930 年聖公會 Lambeth 會議「在某些情境下接受避孕」決議，重申天主教對人工避孕、墮胎、優生學的傳統立場。\n\n本通諭奠下保祿六《人類生命》（1968）的訓導基礎。同時也是天主教首道明確譴責「優生學運動」（Eugenics Movement）的訓導文件，預示其後納粹「種族純潔」政策。",
  topics: ["婚姻", "避孕", "墮胎", "優生學批判", "性倫理"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "casti-connubii-1930-chinese",
      "source": "https://www.vatican.va/content/dam/pius-xi/pdf/encyclicals/documents/hf_p-xi_enc_19301231_casti-connubii_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "casti-connubii-1930-english",
      "source": "https://www.vatican.va/content/pius-xi/en/encyclicals/documents/hf_p-xi_enc_19301231_casti-connubii.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "casti-connubii-1930-latin",
      "source": "https://www.vatican.va/content/pius-xi/la/encyclicals/documents/hf_p-xi_enc_19301231_casti-connubii.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "casti-connubii-1930-italian",
      "source": "https://www.vatican.va/content/pius-xi/it/encyclicals/documents/hf_p-xi_enc_19301231_casti-connubii.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-xi/en/encyclicals/documents/hf_p-xi_enc_19301231_casti-connubii.html',
  notes: "",
}
