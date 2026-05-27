import type { PapalDocument } from '../types'

export const evangeliiGaudium2013: PapalDocument = {
  slug: 'evangelii-gaudium-2013',
  popeSlug: 'francis',
  category: 'apostolic-exhort',
  titleLat: 'Evangelii Gaudium',
  titleEn: 'The Joy of the Gospel',
  titleZh: '《福音的喜樂》宗座勸諭',
  promulgationDate: '2013-11-24',
  century: 21,
  summaryZh: `教宗方濟各第一道宗座勸諭，也是其在位任期的「施政綱領」文件。全文 288 段，分五章，作為 2012 年「新福傳」世界主教代表會議的綜合宣告，但方濟各超出單純綜述範圍，把它寫成一份結構性改革的綱要。

本勸諭引入「走出去的教會」（Iglesia en salida）、「邊緣／邊陲」（periferias）、「不要做專制傳教士」、「現實高於理念」等方濟各特色用語，並系統批判「金錢經濟的偶像化」（idolatría del dinero）與「丟棄文化」（cultura del descarte）。第五章論「神性傳教者」、聖母瑪利亞為傳教模範。

雖然是「勸諭」而非「通諭」，因內容廣度與後續所有方濟各通諭都呼應其架構，本文件常被視為方濟各訓導的「藍圖」。`,
  topics: ['新福傳', '走出去的教會', '社會訓導', '丟棄文化', '經濟批判', '教會改革', '聖母'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（天主教會臺灣地區主教團 譯）',
      textKey: 'evangelii-gaudium-2013-chinese',
      source: 'https://www.vatican.va/content/dam/francesco/pdf/apost_exhortations/documents/papa-francesco_esortazione-ap_20131124_evangelii-gaudium_zh_tw.pdf',
      translator: '天主教會臺灣地區主教團',
    },
    {
      lang: 'en',
      label: '英文 (vatican.va)',
      textKey: 'evangelii-gaudium-2013-english',
      source: 'https://www.vatican.va/content/francesco/en/apost_exhortations/documents/papa-francesco_esortazione-ap_20131124_evangelii-gaudium.html',
    },
    {
      lang: 'it',
      label: '義大利原文 (vatican.va)',
      textKey: 'evangelii-gaudium-2013-italian',
      source: 'https://www.vatican.va/content/francesco/it/apost_exhortations/documents/papa-francesco_esortazione-ap_20131124_evangelii-gaudium.html',
    },
  ],
  displayMode: 'paragraph-aligned',
  vaticanUrl: 'https://www.vatican.va/content/francesco/en/apost_exhortations/documents/papa-francesco_esortazione-ap_20131124_evangelii-gaudium.html',
  related: ['fratelli-tutti-2020', 'laudato-si-2015'],
  notes: `頒布日 2013-11-24 為基督君王節（C 年禮儀年最後一主日），由方濟各親自接續 2012 年本篤十六世主持的「新福傳」世界主教代表會議。雖以宗座勸諭體裁頒布，篇幅與內容深度堪比通諭，學界一般視為方濟各 12 年訓導的「總論」。

第 24 段提出「教會走出去」（Iglesia en salida）的概念，後成為方濟各最常被引用的口號；第 53-58 段「金錢經濟」批判被誤譯為「反資本主義」引發英美媒體爭議，方濟各 2013-12 在 La Stampa 訪談中親自澄清。

本文件原文為西班牙文，後譯為義大利文發佈為「官方」版本；vatican.va 上的義大利版（本 skill 採用為第二欄）即為官方拉丁化體裁的官方版本（apostolic exhortation 不一定有拉丁原文）。`,
}
