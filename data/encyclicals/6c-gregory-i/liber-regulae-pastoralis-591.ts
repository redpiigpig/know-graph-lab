import type { PapalDocument } from '../types'

export const liberRegulaePastoralis591: PapalDocument = {
  slug: 'liber-regulae-pastoralis-591',
  popeSlug: 'gregory-i',
  category: 'epistola',
  titleLat: 'Liber Regulae Pastoralis',
  titleEn: 'The Book of Pastoral Rule',
  titleZh: '《牧者規範書》★★★',
  promulgationDate: '591-01-01',
  century: 6,
  summaryZh: `教宗額我略一世（大額我略）591 年寫的牧者神學經典——西方教會牧靈神學的奠基文獻。分四部：(I) 進入聖職應有的態度；(II) 牧者的生活應該如何；(III) 牧者按 36 種對象的不同方式講道（最具特色，逐種對象——男女、貧富、健病、智愚——說明牧者該如何訓導）；(IV) 講道後牧者如何回到自己，避免驕傲。本書影響極為深遠：9 世紀英國國王 King Alfred 親譯為古英語、列為「英國國王必讀書」；中世紀整個西方司鐸教育以此為核心；Trent 大公會議後神學院教育依此設計；現代「牧靈神學（Pastoral Theology）」學科之名都源自本書 *Pastoralis*。`,
  topics: ['牧靈神學', '司鐸教育', 'Pastoral Rule', '聖職神學'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'liber-regulae-pastoralis-591-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (Schaff NPNF2 Vol 12)',
      textKey: 'liber-regulae-pastoralis-591-english',
      source: 'CCEL — Schaff NPNF2 Vol 12 (Gregory the Great)',
    },
    {
      lang: 'lat',
      label: '拉丁原文（待補）',
      textKey: 'liber-regulae-pastoralis-591-latin',
      placeholder: true,
    },
  ],
  displayMode: 'paragraph-aligned',
}
