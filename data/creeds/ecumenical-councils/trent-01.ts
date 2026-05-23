import type { Creed } from '../types'

export const trent01: Creed = {
  slug: 'trent-01',
  category: 'ecumenical-council',
  councilNo: 19,
  councilDocCode: 'S01',
  councilDocOrder: 1,
  order: 1901,
  nameZh: '第 1 會期 ─ 開幕會期',
  nameEn: 'Session 1 — Opening of the Council',
  year: 1545,
  location: '北義特利騰／波隆那（特利騰大公會議第 1 會期）',
  topic: '宣告大公會議正式開幕；保祿三世特使主持；確立會議目的：駁斥異端、改革教會、恢復基督教和平',
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
      textKey: 'trent-01-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《天主教大公會議文獻彙編》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Waterworth 1848 English translation (public domain)',
      text: '',
      textKey: 'trent-01-english',
      source: 'https://www.papalencyclicals.net/councils/trent/',
    },
    {
      lang: 'lat',
      label: '拉丁原文 — Session 1（Documenta Catholica Omnia / Alberigo COD 1973）',
      text: '',
      textKey: 'trent-01-latin',
      source: 'Documenta Catholica Omnia, 1545-1563-,_Concilium_Tridentinum,_Canones_et_Decreta,_LT.pdf — Alberigo, Conciliorum Oecumenicorum Decreta (1973) 批判版；25 sessio 自全集 PDF 按 SESSIO {ROMAN} 標頭切分',
    },
  ],
  summaryZh: `特利騰大公會議於 1545 年 12 月 13 日由保祿三世（Paul III）召開於北義特利騰 (Trento)，三位教宗特使 — Del Monte 樞機（後為儒略三世）、Cervini 樞機（後為瑪策祿二世）、Pole 樞機 — 主持開幕禮儀。此會期僅頒佈程序性「開幕令」（Decree touching the opening of the Council），確立會議三大目標：駁斥馬丁路德等改教運動所主張的「異端」、改革教會內部弊端、恢復基督徒和平。出席首日的與會教長僅 25 餘人，遠少於前次大公會議規模，反映 16 世紀中葉天主教世界的政治分裂與信仰危機。`,
  notes: `- 頒佈日期：1545-12-13
- 會期類別：第 1 會期 / Session 1 (第一期 1545-49)
- 主議題：宣告大公會議正式開幕；保祿三世特使主持；確立會議目的：駁斥異端、改革教會、恢復基督教和平
- 中文版尚未從 vatican.va 取得（Trent 無中文官方版）；中譯需從紙本《天主教大公會議文獻彙編》取材
- 拉丁版待補（papalencyclicals.net 僅提供 Waterworth 1848 英譯；拉丁需另尋 documentacatholicaomnia.eu / Wikisource）`,
  related: [
    'trent-02',
    'trent-03',
  ],
}
