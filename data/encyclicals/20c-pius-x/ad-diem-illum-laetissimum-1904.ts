import type { PapalDocument } from '../types'

export const adDiemIllumLaetissimum1904: PapalDocument = {
  slug: 'ad-diem-illum-laetissimum-1904',
  popeSlug: 'pius-x',
  category: 'encyclical',
  titleLat: 'Ad Diem Illum Laetissimum',
  titleEn: 'On the Immaculate Conception',
  titleZh: '《那最喜悅的日子》通諭 — 論無染原罪',
  promulgationDate: '1904-02-02',
  century: 20,
  summaryZh: "碧岳十世論聖母無染原罪的通諭，紀念碧岳九世《不可言喻的天主》（Ineffabilis Deus 1854）信理定義頒布 50 週年。\n\n通諭強調聖母敬禮與基督論的內在聯繫——對聖母的敬禮不是分散對基督的注意，而是把信徒引向基督的最近途徑（per Mariam ad Iesum）。",
  topics: ["聖母無染原罪", "聖母論", "基督論連繫"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "ad-diem-illum-laetissimum-1904-chinese",
      "source": "https://www.vatican.va/content/dam/pius-x/pdf/encyclicals/documents/hf_p-x_enc_02021904_ad-diem-illum-laetissimum_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "ad-diem-illum-laetissimum-1904-english",
      "source": "https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_02021904_ad-diem-illum-laetissimum.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "ad-diem-illum-laetissimum-1904-latin",
      "source": "https://www.vatican.va/content/pius-x/la/encyclicals/documents/hf_p-x_enc_02021904_ad-diem-illum-laetissimum.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "ad-diem-illum-laetissimum-1904-italian",
      "source": "https://www.vatican.va/content/pius-x/it/encyclicals/documents/hf_p-x_enc_02021904_ad-diem-illum-laetissimum.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_02021904_ad-diem-illum-laetissimum.html',
  notes: "1854 年 12 月 8 日碧岳九世定義無染原罪信理，本通諭頒布日為紀念活動展開的開始。",
}
