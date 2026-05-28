import type { PapalDocument } from '../types'

export const providasRomanorum1751: PapalDocument = {
  slug: 'providas-romanorum-1751',
  popeSlug: 'benedict-xiv',
  category: 'bull',
  titleLat: 'Providas Romanorum',
  titleEn: 'Reaffirming Condemnation of Freemasonry',
  titleZh: '《羅馬教宗的明智》詔書 — 重申譴責共濟會',
  promulgationDate: '1751-05-18',
  century: 18,
  summaryZh: `教宗本篤十四世 1751 年頒布的詔書，重申並擴充 1738 Clement XII *In Eminenti Apostolatus Specula* 對共濟會的譴責。明確列出共濟會被禁的四大理由：宗教大雜燴、秘密結社、宣誓義務、各國法律已禁。是 18 世紀中葉天主教反共濟會立場的正式定型文件，後被 1814 Pius VII / 1846 Pius IX / 1884 Leo XIII *Humanum Genus* 反覆援引。`,
  topics: ['共濟會', 'Freemasonry', '秘密結社', '絕罰'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'providas-romanorum-1751-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文（待補）',
      textKey: 'providas-romanorum-1751-english',
      placeholder: true,
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org)',
      textKey: 'providas-romanorum-1751-latin',
      source: 'https://la.wikisource.org/wiki/Providas_Romanorum',
    },
  ],
  displayMode: 'paragraph-aligned',
}
