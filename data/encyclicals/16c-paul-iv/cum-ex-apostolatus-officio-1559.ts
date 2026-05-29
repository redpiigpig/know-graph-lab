import type { PapalDocument } from '../types'

export const cumExApostolatusOfficio1559: PapalDocument = {
  slug: 'cum-ex-apostolatus-officio-1559',
  popeSlug: 'paul-iv',
  category: 'bull',
  titleLat: 'Cum Ex Apostolatus Officio',
  titleEn: 'On the Excommunication of Heretical Pontiffs',
  titleZh: '《從使徒職務》詔書 — 異端教宗的當選無效',
  promulgationDate: '1559-02-15',
  century: 16,
  summaryZh: `教宗保祿四世 1559 年頒布的詔書，規定若教宗本人在當選前曾陷異端（haereticus）、分裂（schismaticus）或叛教（apostata），即使後來合法當選並就職，其「當選」自動無效（ipso facto），所有信徒不必服從。背景是宗教改革時期對教廷的神學疑慮（路德派、加爾文派攻擊教宗權威）。本詔書成為 traditionalist Catholic 圈在 Vatican II 後質疑某些教宗合法性的歷史依據。`,
  topics: ['異端', '教宗合法性', 'Sedevacantism', '選舉效力'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'cum-ex-apostolatus-officio-1559-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文（待補）',
      textKey: 'cum-ex-apostolatus-officio-1559-english',
      placeholder: true,
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org)',
      textKey: 'cum-ex-apostolatus-officio-1559-latin',
      source: 'https://la.wikisource.org/wiki/Cum_ex_apostolatus_officio',
    },
  ],
  displayMode: 'paragraph-aligned',
}
