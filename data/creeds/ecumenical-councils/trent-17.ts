import type { Creed } from '../types'

export const trent17: Creed = {
  slug: 'trent-17',
  category: 'ecumenical-council',
  councilNo: 19,
  councilDocCode: 'S17',
  councilDocOrder: 17,
  order: 1917,
  nameZh: '第 17 會期 ─ 第三期復會令',
  nameEn: 'Session 17 — Decree of Resumption (Third Period)',
  year: 1562,
  location: '北義特利騰／波隆那（特利騰大公會議第 17 會期）',
  topic: '庇護四世復會特利騰；第三期 (1562-63) 開始；後續快速通過教義令收尾 — 是會議最高效的一段',
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
      textKey: 'trent-17-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《天主教大公會議文獻彙編》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Waterworth 1848 English translation (public domain)',
      text: '',
      textKey: 'trent-17-english',
      source: 'https://www.papalencyclicals.net/councils/trent/',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina（待補；documentacatholicaomnia.eu / Wikisource la 候選）',
      text: '',
      textKey: 'trent-17-latin',
      placeholder: true,
      source: '待補：來源候選 → documentacatholicaomnia.eu / la.wikisource.org / intratext.com LAT0432',
    },
  ],
  summaryZh: `庇護四世 (Pius IV) 即位後重啟會議；第三期 (1562-63) 在 Cardinal Morone 與 Cardinal Borromeo 等改革派主導下高效推進，於不到 2 年內通過剩餘所有重大教義與紀律令，為會議劃下句點。`,
  notes: `- 頒佈日期：1562-01-18
- 會期類別：第 17 會期 / Session 17 (第三期 1562-63)
- 主議題：庇護四世復會特利騰；第三期 (1562-63) 開始；後續快速通過教義令收尾 — 是會議最高效的一段
- 中文版尚未從 vatican.va 取得（Trent 無中文官方版）；中譯需從紙本《天主教大公會議文獻彙編》取材
- 拉丁版待補（papalencyclicals.net 僅提供 Waterworth 1848 英譯；拉丁需另尋 documentacatholicaomnia.eu / Wikisource）`,
  related: [
    'trent-15',
    'trent-16',
    'trent-18',
    'trent-19',
  ],
}
