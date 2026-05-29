import type { PapalDocument } from '../types'

export const epistolaAdMellitum601: PapalDocument = {
  slug: 'epistola-ad-mellitum-601',
  popeSlug: 'gregory-i',
  category: 'epistola',
  titleLat: 'Epistola ad Mellitum',
  titleEn: 'Letter to Mellitus (On Converting Pagan Temples)',
  titleZh: '《致梅利圖主教書信》— 英國異教廟改聖堂指引 ★',
  promulgationDate: '601-06-18',
  century: 7,
  summaryZh: `教宗額我略一世 601 年寫給 Mellitus 主教（後來成為 Canterbury 第三任大主教）的書信，是中世紀宣教神學的奠基文獻。針對 Augustine of Canterbury 領導的英國盎格魯薩克遜傳教工作，額我略提出突破性 inculturation 政策：「不要拆毀英國的異教廟，而是把它們聖化、改為基督教堂」（fana idolorum destrui in eadem gente minime debeant; sed ipsa, quae in eis sunt, idola destruantur）。也提到允許保留異教節日習俗、轉化為基督徒慶典（如 hanging garlands 等習俗保留為聖徒紀念）。這封信影響了之後一千年的天主教傳教實踐，從中世紀歐洲到 16-17c 利瑪竇 China mission。`,
  topics: ['傳教', 'Inculturation', '英國皈依', '異教廟改聖堂'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'epistola-ad-mellitum-601-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文（待補）',
      textKey: 'epistola-ad-mellitum-601-english',
      placeholder: true,
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org)',
      textKey: 'epistola-ad-mellitum-601-latin',
      source: 'https://la.wikisource.org/wiki/Epistola_ad_Mellitum',
    },
  ],
  displayMode: 'paragraph-aligned',
}
