import type { PapalDocument } from '../types'

export const fratelliTutti2020: PapalDocument = {
  slug: 'fratelli-tutti-2020',
  popeSlug: 'francis',
  category: 'encyclical',
  titleLat: 'Fratelli Tutti',
  titleEn: 'On Fraternity and Social Friendship',
  titleZh: '《眾位弟兄》通諭 — 論四海皆兄弟的情誼',
  promulgationDate: '2020-10-03',
  century: 21,
  summaryZh: `教宗方濟各第三道通諭，於聖方濟各瞻禮（10 月 3 日）在亞西西聖方濟之墓前簽署。全文 287 段，分八章，繼《願祢受讚頌》之後系統處理「社會友愛」議題。

通諭核心是「兄弟情誼」（fraternitas）與「社會友愛」（socialis amicitia）兩個概念，並以〈路加福音〉撒瑪黎雅好人比喻貫穿全篇。文件針對全球化過程中浮現的問題：移民、民族主義、新自由經濟、戰爭、死刑、宗教暴力等，提出對話與相遇的文化。教宗大量引用 2019 年〈阿布扎比《人類弟兄關係宣言》〉（與大伊瑪目阿薩爾的清真寺尊師 Ahmed el-Tayeb 共同簽署）作為跨宗教對話的成果。`,
  topics: ['社會友愛', '兄弟情誼', '移民', '宗教對話', '社會訓導', '撒瑪黎雅好人', '戰爭與和平', '死刑'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（天主教會臺灣地區主教團 譯）',
      textKey: 'fratelli-tutti-2020-chinese',
      source: 'https://www.vatican.va/content/dam/francesco/pdf/encyclicals/documents/papa-francesco_20201003_enciclica-fratelli-tutti_zh_tw.pdf',
      translator: '天主教會臺灣地區主教團',
    },
    {
      lang: 'en',
      label: '英文 (vatican.va)',
      textKey: 'fratelli-tutti-2020-english',
      source: 'https://www.vatican.va/content/francesco/en/encyclicals/documents/papa-francesco_20201003_enciclica-fratelli-tutti.html',
    },
    {
      lang: 'lat',
      label: '拉丁原文 (vatican.va)',
      textKey: 'fratelli-tutti-2020-latin',
      source: 'https://www.vatican.va/content/francesco/la/encyclicals/documents/papa-francesco_20201003_enciclica-fratelli-tutti.html',
    },
  ],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/francesco/en/encyclicals/documents/papa-francesco_20201003_enciclica-fratelli-tutti.html',
  related: ['laudato-si-2015', 'dilexit-nos-2024'],
  notes: `通諭題名典出聖方濟各《Admonitiones》（訓誡集）第 6 條開頭的呼喚 "Fratres omnes"（眾位弟兄）。

簽署地點選在亞西西聖方濟之墓而非梵蒂岡，是疫情高峰期間極少數教宗外出儀式，凸顯方濟各以聖方濟為精神導師、回歸貧窮與兄弟情誼之根的訊息。`,
}
