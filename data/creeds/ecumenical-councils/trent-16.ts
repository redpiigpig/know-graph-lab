import type { Creed } from '../types'

export const trent16: Creed = {
  slug: 'trent-16',
  category: 'ecumenical-council',
  councilNo: 19,
  councilDocCode: 'S16',
  councilDocOrder: 16,
  order: 1916,
  nameZh: '第 16 會期 ─ 暫停會議令',
  nameEn: 'Session 16 — Decree of Suspension',
  year: 1552,
  location: '北義特利騰／波隆那（特利騰大公會議第 16 會期）',
  topic: '因德意志諸侯起兵、皇帝撤退，會議第二度被迫無限期暫停；第二期 (1551-52) 結束',
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
      textKey: 'trent-16-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《天主教大公會議文獻彙編》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Waterworth 1848 English translation (public domain)',
      text: '',
      textKey: 'trent-16-english',
      source: 'https://www.papalencyclicals.net/councils/trent/',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina（待補；documentacatholicaomnia.eu / Wikisource la 候選）',
      text: '',
      textKey: 'trent-16-latin',
      placeholder: true,
      source: '待補：來源候選 → documentacatholicaomnia.eu / la.wikisource.org / intratext.com LAT0432',
    },
  ],
  summaryZh: `因 Maurice of Saxony 起兵與皇帝查理五世撤退，會議第二度被迫無限期暫停。1555 年儒略三世去世；瑪策祿二世在位 22 天便驟逝；繼任的保祿四世 (Paul IV, 1555-59) 反對重啟會議；直至 1559 年其去世、庇護四世 (Pius IV) 即位才於 1562 年 1 月重啟第三期。`,
  notes: `- 頒佈日期：1552-04-28
- 會期類別：第 16 會期 / Session 16 (第二期 1551-52)
- 主議題：因德意志諸侯起兵、皇帝撤退，會議第二度被迫無限期暫停；第二期 (1551-52) 結束
- 中文版尚未從 vatican.va 取得（Trent 無中文官方版）；中譯需從紙本《天主教大公會議文獻彙編》取材
- 拉丁版待補（papalencyclicals.net 僅提供 Waterworth 1848 英譯；拉丁需另尋 documentacatholicaomnia.eu / Wikisource）`,
  related: [
    'trent-14',
    'trent-15',
    'trent-17',
    'trent-18',
  ],
}
