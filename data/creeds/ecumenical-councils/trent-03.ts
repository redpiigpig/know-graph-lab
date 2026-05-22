import type { Creed } from '../types'

export const trent03: Creed = {
  slug: 'trent-03',
  category: 'ecumenical-council',
  councilNo: 19,
  councilDocCode: 'S03',
  councilDocOrder: 3,
  order: 1903,
  nameZh: '第 3 會期 ─ 信德象徵令',
  nameEn: 'Session 3 — Decree on the Symbol of Faith',
  year: 1546,
  location: '北義特利騰／波隆那（特利騰大公會議第 3 會期）',
  topic: '重申尼西亞-君士坦丁堡信經為公教信仰之基礎；作為後續各教義令的詮釋框架',
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
      textKey: 'trent-03-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《天主教大公會議文獻彙編》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Waterworth 1848 English translation (public domain)',
      text: '',
      textKey: 'trent-03-english',
      source: 'https://www.papalencyclicals.net/councils/trent/',
    },
    {
      lang: 'lat',
      label: 'Editio Typica Latina（待補；documentacatholicaomnia.eu / Wikisource la 候選）',
      text: '',
      textKey: 'trent-03-latin',
      placeholder: true,
      source: '待補：來源候選 → documentacatholicaomnia.eu / la.wikisource.org / intratext.com LAT0432',
    },
  ],
  summaryZh: `第三會期頒《信德象徵令》(Decree concerning the Symbol of Faith)，正式重申第一次君士坦丁堡大公會議（381）所制定的「尼西亞-君士坦丁堡信經」(含「和子說」filioque 西方版)，作為「全教會所必信、所必宣認」的信仰基礎。此舉並非新訂信經，而是宣告：後續所有教義決議皆以此信經為詮釋起點，重申天主教與東正教在前七次大公會議共識上的延續，同時對改教家提出「重新審視傳統」的挑戰作出嚴正回應。`,
  notes: `- 頒佈日期：1546-02-04
- 會期類別：第 3 會期 / Session 3 (第一期 1545-49)
- 主議題：重申尼西亞-君士坦丁堡信經為公教信仰之基礎；作為後續各教義令的詮釋框架
- 中文版尚未從 vatican.va 取得（Trent 無中文官方版）；中譯需從紙本《天主教大公會議文獻彙編》取材
- 拉丁版待補（papalencyclicals.net 僅提供 Waterworth 1848 英譯；拉丁需另尋 documentacatholicaomnia.eu / Wikisource）`,
  related: [
    'trent-01',
    'trent-02',
    'trent-04',
    'trent-05',
  ],
}
