import type { PapalDocument } from '../types'

export const confidimus376: PapalDocument = {
  slug: 'confidimus-376',
  popeSlug: 'damasus-i',
  category: 'epistola',
  titleLat: 'Confidimus quidem (Epistola ad Acholium)',
  titleEn: 'Letter to Acholius of Thessalonica',
  titleZh: '《我們確信》書信 — 致 Thessalonica 主教 Acholius',
  promulgationDate: '376-01-01',
  century: 4,
  summaryZh: `教宗達瑪穌一世約 376 年致 Thessalonica 主教 Acholius 的書信，譴責 Apollinarian 異端——該派否認基督的人性靈魂（認為道直接取代了人類靈魂的位置）。是「基督有完整人性」教義在西方拉丁世界最早的明確宣示之一，比 Council of Constantinople 381 早 5 年。Apollinaris of Laodicea 本人原本是 Athanasius 的盟友（對抗亞略派），但其基督論偏鋒被達瑪穌與後來 Cappadocian Fathers（特別是 Gregory Nazianzen）系統反駁。書信收 DH 144-148。`,
  topics: ['基督論', '反 Apollinarianism', '基督的人性靈魂', 'Cappadocian 神學前奏'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'confidimus-376-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文（待補）',
      textKey: 'confidimus-376-english',
      placeholder: true,
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org / Damasus Epistolae)',
      textKey: 'confidimus-376-latin',
      source: 'https://la.wikisource.org/wiki/Epistolae_(Damasus_I)',
    },
  ],
  displayMode: 'paragraph-aligned',
}
