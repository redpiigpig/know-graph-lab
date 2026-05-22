import type { Creed } from '../types'

export const trent12: Creed = {
  slug: 'trent-12',
  category: 'ecumenical-council',
  councilNo: 19,
  councilDocCode: 'S12',
  councilDocOrder: 12,
  order: 1912,
  nameZh: '第 12 會期 ─ 延會令',
  nameEn: 'Session 12 — Decree of Prorogation',
  year: 1551,
  location: '北義特利騰／波隆那（特利騰大公會議第 12 會期）',
  topic: '第二期程序性延會；準備接下來第 13 會期 (Eucharist) 與第 14 會期 (Penance) 之教義決議',
  authors: [
    '教宗保祿三世／儒略三世／庇護四世（依會期）頒佈',
    '教廷特使主持（Del Monte／Cervini／Pole／Morone 等樞機）',
    '神學委員會審議；與會教長表決通過',
  ],
  acceptedBy: ['catholic'],
  displayMode: 'simple',
  versions: [
    {
      lang: 'zh-Hant-Catholic',
      label: '天主教中文版（待手動填入；vatican.va 對 Trent 無中文官方版）',
      text: '',
      textKey: 'trent-12-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《天主教大公會議文獻彙編》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Waterworth 1848 English translation (public domain)',
      text: '',
      textKey: 'trent-12-english',
      source: 'https://www.papalencyclicals.net/councils/trent/',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina（待補；documentacatholicaomnia.eu / Wikisource la 候選）',
      text: '',
      textKey: 'trent-12-latin',
      placeholder: true,
      source: '待補：來源候選 → documentacatholicaomnia.eu / la.wikisource.org / intratext.com LAT0432',
    },
  ],
  summaryZh: `第二期 (1551-52) 之程序性會期，準備後續第 13、14 會期之教義決議。`,
  notes: `- 頒佈日期：1551-09-01
- 會期類別：第 12 會期 / Session 12 (第二期 1551-52)
- 主議題：第二期程序性延會；準備接下來第 13 會期 (Eucharist) 與第 14 會期 (Penance) 之教義決議
- 中文版尚未從 vatican.va 取得（Trent 無中文官方版）；中譯需從紙本《天主教大公會議文獻彙編》取材
- 拉丁版待補（papalencyclicals.net 僅提供 Waterworth 1848 英譯；拉丁需另尋 documentacatholicaomnia.eu / Wikisource）`,
  related: [
    'trent-10',
    'trent-11',
    'trent-13',
    'trent-14',
  ],
}
