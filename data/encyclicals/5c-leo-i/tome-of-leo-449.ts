import type { PapalDocument } from '../types'

export const tomeOfLeo449: PapalDocument = {
  slug: 'tome-of-leo-449',
  popeSlug: 'leo-i',
  category: 'epistola',
  titleLat: 'Epistola XXVIII ad Flavianum (Tomus Leonis)',
  titleEn: 'The Tome of Leo (Letter 28 to Flavian)',
  titleZh: '《良一世大公書信》第 28 封——致 Flavianus 論基督論',
  promulgationDate: '449-06-13',
  century: 5,
  summaryZh: '良一世（「大良」）於 449-06-13 致君士坦丁堡 Flavian 宗主教的書信，駁斥君士坦丁堡修道院長 Eutyches 主張的「基督一性」（Monophysitism）異端。明確闡述：基督在一個位格內保有完整的兩個性（divine + human），各按自己本性運作而不相混淆、不相分離。此書信於 451 年 Chalcedon 大公會議上宣讀時，與會教父高呼：「伯多祿藉良說話了！」(Petrus per Leonem locutus est!) — 成為 Chalcedonian 基督論的奠基文獻，被收入 449 第二次以弗所「強盜會議」與 451 Chalcedon 會議文件，深遠影響東西方基督論。',
  topics: ['基督論', 'Chalcedon 大公會議', 'Monophysitism 駁斥', '位格與本性'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'tome-of-leo-449-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (Schaff NPNF Series 2 Vol 12)',
      textKey: 'tome-of-leo-449-english',
      source: 'https://www.ccel.org/ccel/schaff/npnf212.ii.iv.xxviii.html',
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org)',
      textKey: 'tome-of-leo-449-latin',
      source: 'https://la.wikisource.org/wiki/Tomus_ad_Flavianum',

    },
  ],
  displayMode: 'paragraph-aligned',
  notes: '拉丁原文出處：Migne PL 54.755-781 / ACO II,2,1 pp.24-33 (Schwartz, 1932)。中譯目前可參考基督教歷代名著集成第三部第二卷（湯清譯）。',
}
