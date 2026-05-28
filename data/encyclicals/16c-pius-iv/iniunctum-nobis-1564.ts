import type { PapalDocument } from '../types'

export const iniunctumNobis1564: PapalDocument = {
  slug: 'iniunctum-nobis-1564',
  popeSlug: 'pius-iv',
  category: 'bull',
  titleLat: 'Iniunctum Nobis',
  titleEn: 'Tridentine Profession of Faith',
  titleZh: '《特蘭多信仰宣誓》詔書',
  promulgationDate: '1564-11-13',
  century: 16,
  summaryZh: `教宗碧岳四世於 1564 年特蘭多大公會議閉幕後頒布的「信仰宣誓」詔書（Professio Fidei Tridentina），規定主教、司鐸、神學家、修會新生等職位就任前須公開宣誓接受 Trent 教義。中世紀以降天主教神職人員「信仰宣誓」的基礎範本，DH 1862-1870 收錄。`,
  topics: ['特蘭多信經', '信仰宣誓', '反宗教改革', '神職人員'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'iniunctum-nobis-1564-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (en.wikisource.org)',
      textKey: 'iniunctum-nobis-1564-english',
      source: 'https://en.wikisource.org/wiki/Iniunctum_nobis',
    },
    {
      lang: 'lat',
      label: '拉丁原文（待補）',
      textKey: 'iniunctum-nobis-1564-latin',
      placeholder: true,
    },
  ],
  displayMode: 'paragraph-aligned',
}
