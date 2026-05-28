import type { PapalDocument } from '../types'

export const acerboNimis1905: PapalDocument = {
  slug: 'acerbo-nimis-1905',
  popeSlug: 'pius-x',
  category: 'encyclical',
  titleLat: 'Acerbo Nimis',
  titleEn: 'On Teaching Christian Doctrine',
  titleZh: '《極為痛苦》通諭 — 論基督徒要理教育',
  promulgationDate: '1905-04-15',
  century: 20,
  summaryZh: "碧岳十世論要理教育的通諭，要求所有堂區建立「基督徒要理會」（Confraternitas Christianae Doctrinae）並對成人與兒童系統授課。\n\n本通諭為 1908 年「碧岳十世要理書」（Catechismo di Pio X）的編纂奠下基礎——成為 20 世紀初天主教世界最廣泛使用的要理範本，直至 1992《天主教教理》問世。",
  topics: ["要理教育", "堂區牧靈", "信仰培育"],
  versions:   [
    {
      "lang": "zh-Hant",
      "label": "中文（天主教會臺灣地區主教團 譯）",
      "textKey": "acerbo-nimis-1905-chinese",
      "source": "https://www.vatican.va/content/dam/pius-x/pdf/encyclicals/documents/hf_p-x_enc_15041905_acerbo-nimis_zh_tw.pdf",
      "translator": "天主教會臺灣地區主教團"
    },
    {
      "lang": "en",
      "label": "英文 (vatican.va)",
      "textKey": "acerbo-nimis-1905-english",
      "source": "https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_15041905_acerbo-nimis.html"
    },
    {
      "lang": "lat",
      "label": "拉丁原文 (vatican.va)",
      "textKey": "acerbo-nimis-1905-latin",
      "source": "https://www.vatican.va/content/pius-x/la/encyclicals/documents/hf_p-x_enc_15041905_acerbo-nimis.html"
    },
    {
      "lang": "it",
      "label": "義大利文 (vatican.va)",
      "textKey": "acerbo-nimis-1905-italian",
      "source": "https://www.vatican.va/content/pius-x/it/encyclicals/documents/hf_p-x_enc_15041905_acerbo-nimis.html"
    }
  ] as PapalDocument['versions'],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/pius-x/en/encyclicals/documents/hf_p-x_enc_15041905_acerbo-nimis.html',
  notes: "本通諭是碧岳十世「牧靈型教宗」面相最具體的展現之一，後直接推動 1908 年要理書的編纂。",
}
