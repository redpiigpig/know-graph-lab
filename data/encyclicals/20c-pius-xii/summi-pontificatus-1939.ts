import type { PapalDocument } from '../types'

export const summiPontificatus1939: PapalDocument = {
  slug: 'summi-pontificatus-1939',
  popeSlug: 'pius-xii',
  category: 'encyclical',
  titleLat: 'Summi Pontificatus',
  titleEn: 'On the Unity of Human Society',
  titleZh: '《至高的教宗職權》通諭 — 論人類社會的合一',
  promulgationDate: '1939-10-20',
  century: 20,
  summaryZh: "碧岳十二世第一道通諭，於二次大戰爆發（1939-09-01）後一個半月頒布。明確譴責納粹主義的「種族至上」（idolatria della razza）、極權主義對個人尊嚴的壓制，並重申天主教對「人類大家庭合一」的信念。",
  topics: ["反納粹", "反種族主義", "人性尊嚴", "戰時訓導"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "summi-pontificatus-1939-chinese",
      "source": "https://www.vatican.va/content/dam/pius-xii/pdf/encyclicals/documents/hf_p-xii_enc_20101939_summi-pontificatus_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "summi-pontificatus-1939-english",
      "source": "https://www.vatican.va/content/pius-xii/en/encyclicals/documents/hf_p-xii_enc_20101939_summi-pontificatus.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "summi-pontificatus-1939-latin",
      "source": "https://www.vatican.va/content/pius-xii/la/encyclicals/documents/hf_p-xii_enc_20101939_summi-pontificatus.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "summi-pontificatus-1939-italian",
      "source": "https://www.vatican.va/content/pius-xii/it/encyclicals/documents/hf_p-xii_enc_20101939_summi-pontificatus.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-xii/en/encyclicals/documents/hf_p-xii_enc_20101939_summi-pontificatus.html',
  notes: "本通諭在 1939-10-20 頒布、二戰開戰 49 天後，是碧岳十二世對納粹政權的首次正式公開譴責。",
}
