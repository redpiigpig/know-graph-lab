import type { Creed } from '../types'

export const trent23: Creed = {
  slug: 'trent-23',
  category: 'ecumenical-council',
  councilNo: 19,
  councilDocCode: 'S23',
  councilDocOrder: 23,
  order: 1923,
  nameZh: '第 23 會期 ─ 聖秩令',
  nameEn: 'Session 23 — Doctrine on the Sacrament of Order + Decree on Reformation',
  year: 1563,
  location: '北義特利騰／波隆那（特利騰大公會議第 23 會期）',
  topic: '定義聖秩為基督所立之聖事；主教 / 司鐸 / 執事為神律所立之三級神品；主教按立 ex jure divino 高於司鐸；設立修院制度',
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
      textKey: 'trent-23-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《天主教大公會議文獻彙編》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Waterworth 1848 English translation (public domain)',
      text: '',
      textKey: 'trent-23-english',
      source: 'https://www.papalencyclicals.net/councils/trent/',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina（待補；documentacatholicaomnia.eu / Wikisource la 候選）',
      text: '',
      textKey: 'trent-23-latin',
      placeholder: true,
      source: '待補：來源候選 → documentacatholicaomnia.eu / la.wikisource.org / intratext.com LAT0432',
    },
  ],
  summaryZh: `第二十三會期頒《論聖秩聖事令》4 章 + 8 條 canons：(1) 聖秩 (ordo) 為基督所立之七件聖事之一，賦予不可磨滅之神印 (character indelebilis)；(2) 神品三級 — 主教、司鐸、執事 — 皆為神律所立 (ex jure divino)；(3) 主教於司鐸之上，擁有按立聖秩、堅振之專屬權柄 — 駁路德、加爾文「普世司祭職」之削平主張；(4) 主教為宗徒之繼承人，由聖神所立治理教會。同會期之改革令規範神品授職標準、嚴格規範常駐 (residency)、首創「修院制度」(seminarium) — 規定每教區應設神學院培養神職人員 — 此為日後天主教神職教育最重大的單一改革。`,
  notes: `- 頒佈日期：1563-07-15
- 會期類別：第 23 會期 / Session 23 (第三期 1562-63)
- 主議題：定義聖秩為基督所立之聖事；主教 / 司鐸 / 執事為神律所立之三級神品；主教按立 ex jure divino 高於司鐸；設立修院制度
- 中文版尚未從 vatican.va 取得（Trent 無中文官方版）；中譯需從紙本《天主教大公會議文獻彙編》取材
- 拉丁版待補（papalencyclicals.net 僅提供 Waterworth 1848 英譯；拉丁需另尋 documentacatholicaomnia.eu / Wikisource）`,
  related: [
    'trent-21',
    'trent-22',
    'trent-24',
    'trent-25',
  ],
}
