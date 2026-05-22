import type { Creed } from '../types'

export const trent05: Creed = {
  slug: 'trent-05',
  category: 'ecumenical-council',
  councilNo: 19,
  councilDocCode: 'S05',
  councilDocOrder: 5,
  order: 1905,
  nameZh: '第 5 會期 ─ 原罪令',
  nameEn: 'Session 5 — Decree concerning Original Sin + Decree on Reformation',
  year: 1546,
  location: '北義特利騰／波隆那（特利騰大公會議第 5 會期）',
  topic: '定義亞當原罪因受洗得赦；但情慾 (concupiscentia) 仍存於受洗者；正面回應 Pelagius 與改教派對原罪論的不同解釋',
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
      textKey: 'trent-05-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《天主教大公會議文獻彙編》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Waterworth 1848 English translation (public domain)',
      text: '',
      textKey: 'trent-05-english',
      source: 'https://www.papalencyclicals.net/councils/trent/',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina（待補；documentacatholicaomnia.eu / Wikisource la 候選）',
      text: '',
      textKey: 'trent-05-latin',
      placeholder: true,
      source: '待補：來源候選 → documentacatholicaomnia.eu / la.wikisource.org / intratext.com LAT0432',
    },
  ],
  summaryZh: `第五會期頒《論原罪令》(Decree concerning original sin) 五條 canons：肯定亞當因犯罪失去原義並將罪傳給全人類；唯獨基督的功勞能拯救人類；嬰兒受洗的必要性；洗禮確實除去原罪（駁斥路德「罪僅被遮蓋」之說），但「情慾」(concupiscentia, 即犯罪傾向) 仍存於受洗者中 — 此非罪本身、而是罪之促因。此會期同時頒佈第一份《改革令》(Decree on reformation) 規範主教講道義務與聖經教師職位設立，開啟「教義 + 紀律」並行的會議模式。`,
  notes: `- 頒佈日期：1546-06-17
- 會期類別：第 5 會期 / Session 5 (第一期 1545-49)
- 主議題：定義亞當原罪因受洗得赦；但情慾 (concupiscentia) 仍存於受洗者；正面回應 Pelagius 與改教派對原罪論的不同解釋
- 中文版尚未從 vatican.va 取得（Trent 無中文官方版）；中譯需從紙本《天主教大公會議文獻彙編》取材
- 拉丁版待補（papalencyclicals.net 僅提供 Waterworth 1848 英譯；拉丁需另尋 documentacatholicaomnia.eu / Wikisource）`,
  related: [
    'trent-03',
    'trent-04',
    'trent-06',
    'trent-07',
  ],
}
