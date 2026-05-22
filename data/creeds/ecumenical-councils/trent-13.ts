import type { Creed } from '../types'

export const trent13: Creed = {
  slug: 'trent-13',
  category: 'ecumenical-council',
  councilNo: 19,
  councilDocCode: 'S13',
  councilDocOrder: 13,
  order: 1913,
  nameZh: '第 13 會期 ─ 聖體聖事令',
  nameEn: 'Session 13 — Decree concerning the Most Holy Sacrament of the Eucharist + Decree on Reformation',
  year: 1551,
  location: '北義特利騰／波隆那（特利騰大公會議第 13 會期）',
  topic: '定義變質說 (transubstantiation)：餅酒實體變為基督體血；基督真實、實質、實體地臨在聖體；駁茨溫利、加爾文「象徵」「靈在」說',
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
      textKey: 'trent-13-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《天主教大公會議文獻彙編》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Waterworth 1848 English translation (public domain)',
      text: '',
      textKey: 'trent-13-english',
      source: 'https://www.papalencyclicals.net/councils/trent/',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina（待補；documentacatholicaomnia.eu / Wikisource la 候選）',
      text: '',
      textKey: 'trent-13-latin',
      placeholder: true,
      source: '待補：來源候選 → documentacatholicaomnia.eu / la.wikisource.org / intratext.com LAT0432',
    },
  ],
  summaryZh: `第十三會期頒《論至聖聖體聖事令》8 章 + 11 條 canons，正面定義聖體教義：(1) 變質說 (transubstantiatio) — 餅酒之實體 (substantia) 於祝聖時整個變為基督之體血，唯有附體 (accidentia, 即外在感官特徵) 仍存；(2) 基督真實、實質、實體地臨在聖體 (vere, realiter, substantialiter)，非僅象徵 (駁茨溫利 Zwingli)、亦非僅與餅同在 (駁路德 consubstantiation)、亦非僅靈性同在 (駁加爾文 spiritual presence)；(3) 一旦祝聖，基督即「常存」(permanens) 於聖體中，故合於朝拜與遊行 (Corpus Christi)；(4) 領聖體前需告解，受死罪者領聖體即犯瀆聖罪 (sacrilege)。同會期之《改革令》規範訴訟程序、主教權限。`,
  notes: `- 頒佈日期：1551-10-11
- 會期類別：第 13 會期 / Session 13 (第二期 1551-52)
- 主議題：定義變質說 (transubstantiation)：餅酒實體變為基督體血；基督真實、實質、實體地臨在聖體；駁茨溫利、加爾文「象徵」「靈在」說
- 中文版尚未從 vatican.va 取得（Trent 無中文官方版）；中譯需從紙本《天主教大公會議文獻彙編》取材
- 拉丁版待補（papalencyclicals.net 僅提供 Waterworth 1848 英譯；拉丁需另尋 documentacatholicaomnia.eu / Wikisource）`,
  related: [
    'trent-11',
    'trent-12',
    'trent-14',
    'trent-15',
  ],
}
