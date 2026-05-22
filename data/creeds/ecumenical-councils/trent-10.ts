import type { Creed } from '../types'

export const trent10: Creed = {
  slug: 'trent-10',
  category: 'ecumenical-council',
  councilNo: 19,
  councilDocCode: 'S10',
  councilDocOrder: 10,
  order: 1910,
  nameZh: '第 10 會期 ─ 延會令（波隆那第二）',
  nameEn: 'Session 10 — Decree of Prorogation',
  year: 1547,
  location: '北義特利騰／波隆那（特利騰大公會議第 10 會期）',
  topic: '波隆那期第二場延會；與會教長持續流失；保祿三世於 11 月正式宣告暫停會議',
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
      textKey: 'trent-10-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《天主教大公會議文獻彙編》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Waterworth 1848 English translation (public domain)',
      text: '',
      textKey: 'trent-10-english',
      source: 'https://www.papalencyclicals.net/councils/trent/',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina（待補；documentacatholicaomnia.eu / Wikisource la 候選）',
      text: '',
      textKey: 'trent-10-latin',
      placeholder: true,
      source: '待補：來源候選 → documentacatholicaomnia.eu / la.wikisource.org / intratext.com LAT0432',
    },
  ],
  summaryZh: `波隆那期第二度延會令；會議實質已癱瘓。1547 年 9 月，保祿三世為緩解與皇帝關係，宣布無限期暫停 Bologna 會議。1549 年保祿三世去世；1550 年儒略三世 (Julius III) 即位後重啟特利騰會議。`,
  notes: `- 頒佈日期：1547-06-02
- 會期類別：第 10 會期 / Session 10 (第一期 1545-49)
- 主議題：波隆那期第二場延會；與會教長持續流失；保祿三世於 11 月正式宣告暫停會議
- 中文版尚未從 vatican.va 取得（Trent 無中文官方版）；中譯需從紙本《天主教大公會議文獻彙編》取材
- 拉丁版待補（papalencyclicals.net 僅提供 Waterworth 1848 英譯；拉丁需另尋 documentacatholicaomnia.eu / Wikisource）`,
  related: [
    'trent-08',
    'trent-09',
    'trent-11',
    'trent-12',
  ],
}
