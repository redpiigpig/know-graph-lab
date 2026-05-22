import type { Creed } from '../types'

export const trent14: Creed = {
  slug: 'trent-14',
  category: 'ecumenical-council',
  councilNo: 19,
  councilDocCode: 'S14',
  councilDocOrder: 14,
  order: 1914,
  nameZh: '第 14 會期 ─ 告解與終傅聖事令',
  nameEn: 'Session 14 — Decree on the Sacraments of Penance and Extreme Unction + Decree on Reformation',
  year: 1551,
  location: '北義特利騰／波隆那（特利騰大公會議第 14 會期）',
  topic: '定義告解三要素（痛悔、告明、補贖）+ 神父赦罪之司法權；終傅 (extreme unction) 為基督所立之聖事',
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
      textKey: 'trent-14-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《天主教大公會議文獻彙編》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Waterworth 1848 English translation (public domain)',
      text: '',
      textKey: 'trent-14-english',
      source: 'https://www.papalencyclicals.net/councils/trent/',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina（待補；documentacatholicaomnia.eu / Wikisource la 候選）',
      text: '',
      textKey: 'trent-14-latin',
      placeholder: true,
      source: '待補：來源候選 → documentacatholicaomnia.eu / la.wikisource.org / intratext.com LAT0432',
    },
  ],
  summaryZh: `第十四會期頒兩聖事令：(1)《論告解聖事》9 章 + 15 條 canons：告解 (paenitentia) 為基督所立第二件「重洗」性質的聖事；三要素為痛悔 (contritio)、告明 (confessio)、補贖 (satisfactio)；神父因聖秩擁有「司法性赦罪權」(potestas iudicialis)，非僅宣告而是真實赦免；對重罪 (peccatum mortale) 之告明為神律義務，須年至少一次。(2)《論終傅聖事》3 章 + 4 條 canons：終傅 (extrema unctio, 即病傅之古稱) 為雅各書 5:14-15 所暗示、基督所立、宗徒所傳之聖事，賦予病人罪赦、靈魂安慰、有時甚至身體痊癒之恩寵；唯司鐸 (presbyter) 為其施行者。同會期之《改革令》規範教省會議、主教對神父之裁判權。`,
  notes: `- 頒佈日期：1551-11-25
- 會期類別：第 14 會期 / Session 14 (第二期 1551-52)
- 主議題：定義告解三要素（痛悔、告明、補贖）+ 神父赦罪之司法權；終傅 (extreme unction) 為基督所立之聖事
- 中文版尚未從 vatican.va 取得（Trent 無中文官方版）；中譯需從紙本《天主教大公會議文獻彙編》取材
- 拉丁版待補（papalencyclicals.net 僅提供 Waterworth 1848 英譯；拉丁需另尋 documentacatholicaomnia.eu / Wikisource）`,
  related: [
    'trent-12',
    'trent-13',
    'trent-15',
    'trent-16',
  ],
}
