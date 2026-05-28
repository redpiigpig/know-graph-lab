import type { PapalDocument } from '../types'

export const apostolicaeCurae1896: PapalDocument = {
  slug: 'apostolicae-curae-1896',
  popeSlug: 'leo-xiii',
  category: 'apostolic-letter',
  titleLat: 'Apostolicae Curae',
  titleEn: 'On the Nullity of Anglican Orders',
  titleZh: '《使徒關懷》宗座書信 — 論英國國教聖秩的無效',
  promulgationDate: '1896-09-13',
  century: 19,
  summaryZh: `教宗良十三世 1896 年頒布的宗座書信，正式宣告英國國教（Anglican Church）的聖秩授任（ordinations）「絕對無效」（absolutely null and utterly void），主要理由有二：一是 1552 *Book of Common Prayer* 改革祝聖禮儀時，公認的犧牲性祭司觀（sacerdotium）被刻意刪除（intentio defectus）；二是聖統繼承在 Cranmer 與 Barlow 之間斷裂（forma defectus）。這份宣告影響近 130 年天主教—聖公會合一對話，至 2009 *Anglicanorum Coetibus* 為英國國教人士設立 personal ordinariate 才部分緩解此實際隔閡。`,
  topics: ['聖秩', '聖公會', '聖事神學', '教會合一'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'apostolicae-curae-1896-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文 (en.wikisource.org)',
      textKey: 'apostolicae-curae-1896-english',
      source: 'https://en.wikisource.org/wiki/Apostolicae_Curae',
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org)',
      textKey: 'apostolicae-curae-1896-latin',
      source: 'https://la.wikisource.org/wiki/Apostolicae_curae',
    },
  ],
  displayMode: 'paragraph-aligned',
}
