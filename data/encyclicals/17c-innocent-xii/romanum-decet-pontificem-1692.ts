import type { PapalDocument } from '../types'

export const romanumDecetPontificem1692: PapalDocument = {
  slug: 'romanum-decet-pontificem-1692',
  popeSlug: 'innocent-xii',
  category: 'bull',
  titleLat: 'Romanum Decet Pontificem',
  titleEn: 'On the Limitation of Papal Nepotism',
  titleZh: '《教宗合宜》詔書 — 限制教宗 nepotism',
  promulgationDate: '1692-06-22',
  century: 17,
  summaryZh: `教宗諾森十二世 1692 年頒布的反 nepotism 詔書，禁止教宗將土地、官職、金錢等利益授予自己的親屬，僅允許資助一位有德行的近親修士或神職人員。是巴洛克時期教廷反裙帶風氣的里程碑文件。`,
  topics: ['nepotism', '教廷改革', '教會職位'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'romanum-decet-pontificem-1692-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文（待補）',
      textKey: 'romanum-decet-pontificem-1692-english',
      placeholder: true,
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org)',
      textKey: 'romanum-decet-pontificem-1692-latin',
      source: 'https://la.wikisource.org/wiki/Romanum_decet_Pontificem',
    },
  ],
  displayMode: 'paragraph-aligned',
}
