import type { PapalDocument } from '../types'

export const cumTamDivino1505: PapalDocument = {
  slug: 'cum-tam-divino-1505',
  popeSlug: 'julius-ii',
  category: 'bull',
  titleLat: 'Cum Tam Divino',
  titleEn: 'Against Simony in Papal Elections',
  titleZh: '《既然如此神聖》詔書 — 反 simony 教宗選舉',
  promulgationDate: '1505-01-14',
  century: 16,
  summaryZh: `教宗儒略二世 1505 年頒布的詔書，譴責並宣告「以買賣 simony 方式取得的教宗職位無效」（後任亞歷山大六世被廣泛指控 simony 即背景）。規定即使選舉時收受賄賂的樞機團多數同意，simony 教宗選舉仍為自動無效（ipso jure invalida），任何信徒不必對此「教宗」服從。是中世紀末期教廷自我改革（pre-Trent reform）的關鍵文件。`,
  topics: ['simony', '教宗選舉', 'Conclave 改革', '亞歷山大六世遺緒'],
  versions: [
    {
      lang: 'zh-Hant',
      label: '中文（待補）',
      textKey: 'cum-tam-divino-1505-chinese',
      placeholder: true,
    },
    {
      lang: 'en',
      label: '英文（待補）',
      textKey: 'cum-tam-divino-1505-english',
      placeholder: true,
    },
    {
      lang: 'lat',
      label: '拉丁原文 (la.wikisource.org)',
      textKey: 'cum-tam-divino-1505-latin',
      source: 'https://la.wikisource.org/wiki/Cum_tam_divino',
    },
  ],
  displayMode: 'paragraph-aligned',
}
