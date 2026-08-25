import type { Creed } from '../types'

export const westminsterShorterCatechism: Creed = {
  slug: 'westminster-shorter-catechism',
  category: 'protestant-confession',
  order: 3009,
  nameZh: '西敏小要理問答',
  nameEn: 'Westminster Shorter Catechism',
  nameLat: 'Catechismus Minor Westmonasteriensis',
  year: 1647,
  location: '英格蘭倫敦西敏寺',
  topic: '107 問答；為「初學道者」編寫，第 1 問「人的主要目的是什麼？」為英語神學史上最著名的問答',
  authors: ['西敏會議（Westminster Assembly）'],
  acceptedBy: ['reformed', 'protestant'],
  displayMode: 'simple',
  versions: [
    {
      lang: 'zh-Hant-Reformed',
      label: '呂沛淵譯本（中英對照）',
      text: '',
      textKey: 'westminster-shorter-chinese',
      source: 'TRC 藏本，107 問逐問中英並列。',
      translator: '呂沛淵',
    },
    {
      lang: 'en',
      label: 'English 1647（待補）',
      text: '',
      placeholder: true,
      source: 'The Shorter Catechism agreed upon by the Assembly of Divines, London 1647.',
    },
  ],
  summaryZh: `1647 年由西敏會議完成，與《大要理問答》同時提交英格蘭國會。兩者內容架構相同，差別在對象：大要理問答供講台講解與成人進深之用，小要理問答則為「初學道者」編寫，力求簡短可誦記。

全書 107 問，前 38 問論人當信的真道（神、預旨、創造、護理、墮落、基督、救恩之施行），後 69 問論神向人所要求的本分（十誡逐條、信心與悔改、蒙恩之道、主禱文逐句）。第 1 問「人的主要目的是什麼？答：人的主要目的是榮耀神，並以祂為樂，直到永遠。」是英語神學史上最廣為傳誦的一句。

三百餘年來為英語世界長老宗兒童與慕道者教育的標準教材，華語改革宗圈亦有多家譯本與背誦版流通。`,
  notes: `- 1647 完成並提交國會；1648 蘇格蘭教會大會採納
- 大／小要理問答架構相同，小者供初學誦記，大者供講台講解
- 站上另藏背誦版、兒童版、幼兒版與多種釋義（Thomas Vincent、James Fisher、Roderick Lawson、G. L. Williamson）
- 中譯情況：呂沛淵、趙忠輝、羅森著呂沛淵修訂本等多家`,
  related: ['westminster-confession', 'westminster-larger-catechism', 'heidelberg-catechism'],
}

export const westminsterLargerCatechism: Creed = {
  slug: 'westminster-larger-catechism',
  category: 'protestant-confession',
  order: 3010,
  nameZh: '西敏大要理問答',
  nameEn: 'Westminster Larger Catechism',
  nameLat: 'Catechismus Major Westmonasteriensis',
  year: 1647,
  location: '英格蘭倫敦西敏寺',
  topic: '196 問答；供講台講解與成人進深之用，十誡部分的解釋為全書最詳盡處',
  authors: ['西敏會議（Westminster Assembly）'],
  acceptedBy: ['reformed', 'protestant'],
  displayMode: 'simple',
  versions: [
    {
      lang: 'zh-Hant-Reformed',
      label: '呂沛淵譯本',
      text: '',
      textKey: 'westminster-larger-chinese',
      source: 'TRC 藏本，196 問全文。',
      translator: '呂沛淵',
    },
    {
      lang: 'en',
      label: 'English 1647（待補）',
      text: '',
      placeholder: true,
      source: 'The Larger Catechism agreed upon by the Assembly of Divines, London 1647.',
    },
  ],
  summaryZh: `1647 年由西敏會議完成，與《小要理問答》同時提交英格蘭國會。共 196 問，架構與小要理問答相同而篇幅遠為詳盡，設計供牧師在講台上逐問講解，以及信徒進深研讀之用。

十誡部分（問 91-152）是全書份量最重之處，逐條列出每一誡所「吩咐的本分」與「禁止的罪」，細目繁多，是清教徒倫理神學的濃縮。論教會、聖禮與主禱文的部分亦較小要理問答展開許多。

因篇幅較長，實際流通遠不如小要理問答，但研究清教徒神學與西敏神學者多以此為本。`,
  notes: `- 1647 完成並提交國會；1648 蘇格蘭教會大會採納
- 問 91-152 逐條解十誡，為全書重心，清教徒倫理神學的核心文本
- 站上另藏魏司道（Johannes G. Vos）《威斯敏斯特大要理問答註釋》片段，惟僅前 10 問，非全書
- 中譯情況：呂沛淵譯本、趙中輝譯本`,
  related: ['westminster-confession', 'westminster-shorter-catechism'],
}
