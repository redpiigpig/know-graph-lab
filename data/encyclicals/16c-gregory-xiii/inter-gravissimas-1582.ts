import type { PapalDocument } from '../types'

export const interGravissimas1582: PapalDocument = {
  slug: 'inter-gravissimas-1582',
  popeSlug: 'gregory-xiii',
  category: 'bull',
  titleLat: 'Inter Gravissimas',
  titleEn: 'Inaugurating the Gregorian Calendar',
  titleZh: '《最重要事務中》詔書 — 公佈額我略曆 ★★★',
  promulgationDate: '1582-02-24',
  century: 16,
  summaryZh: `教宗額我略十三世 1582 年頒布的詔書，是現代「Gregorian Calendar（額我略曆／西曆）」的奠基文件。修正 Julian Calendar 累積的 10 天偏差（1582-10-04 直接跳到 10-15）、改革 leap year 規則（百年不閏，四百年閏）、固定復活節計算。本詔書是教廷對「世俗時間」最深遠的單一影響——所有歐美乃至 20 世紀東亞諸國的官方曆法都建基於此。1923 年（東正教多數採用）／1949 年（中國採用）以後成為近乎全球通行的民用曆。`,
  topics: ['曆法改革', 'Gregorian Calendar', '閏年', '復活節'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'inter-gravissimas-1582-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文（待補）',
      textKey: 'inter-gravissimas-1582-english',
      placeholder: true,
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org)',
      textKey: 'inter-gravissimas-1582-latin',
      source: 'https://la.wikisource.org/wiki/Inter_gravissimas',
    },
  ],
  displayMode: 'paragraph-aligned',
}
