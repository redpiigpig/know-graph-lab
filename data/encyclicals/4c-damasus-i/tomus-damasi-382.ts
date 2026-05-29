import type { PapalDocument } from '../types'

export const tomusDamasi382: PapalDocument = {
  slug: 'tomus-damasi-382',
  popeSlug: 'damasus-i',
  category: 'epistola',
  titleLat: 'Tomus Damasi',
  titleEn: 'Tome of Damasus',
  titleZh: '《達瑪穌教義書》— 382 羅馬教會議信仰宣告與 24 條譴責',
  promulgationDate: '382-01-01',
  century: 4,
  summaryZh: `教宗達瑪穌一世 382 年羅馬地方會議後頒布的信仰宣告，凡 24 條 anathema（譴責）。針對亞略派（Arian）／半亞略派（Semi-Arian）／撒伯里安派（Sabellian）／Macedonian（譴聖神是受造的派別）／Photinian 等異端立場逐條譴責，重申尼西亞 325 與君士坦丁堡 381 信經的三一神學共識。文末附當時羅馬教廷接受的聖經正典清單（Damasine Canon）——是西方拉丁教會聖經正典史最早正式宣告之一，與後 Council of Rome (382)／Council of Hippo (393)／Carthage (397) 一脈相承。傳統認為這份文件與達瑪穌委託 Jerome 著手 Vulgate 翻譯計劃同步成立（達瑪穌也是 Jerome 的庇護人）。文獻收 Denzinger DH 152-180。`,
  topics: ['三位一體', '聖經正典', 'Damasine Canon', '反 Arianism', '反 Macedonianism', '382 羅馬會議'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'tomus-damasi-382-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文（待補）',
      textKey: 'tomus-damasi-382-english',
      placeholder: true,
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org / Tomus Damasi (= Rescriptum))',
      textKey: 'tomus-damasi-382-latin',
      source: 'https://la.wikisource.org/wiki/Rescriptum_(Damasus_I)',
    },
  ],
  displayMode: 'paragraph-aligned',
}
