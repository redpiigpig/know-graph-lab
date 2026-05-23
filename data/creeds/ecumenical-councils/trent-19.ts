import type { Creed } from '../types'

export const trent19: Creed = {
  slug: 'trent-19',
  category: 'ecumenical-council',
  councilNo: 19,
  councilDocCode: 'S19',
  councilDocOrder: 19,
  order: 1919,
  nameZh: '第 19 會期 ─ 延會令',
  nameEn: 'Session 19 — Decree of Prorogation',
  year: 1562,
  location: '北義特利騰／波隆那（特利騰大公會議第 19 會期）',
  topic: '第三期程序性延會；準備接下來第 21 會期 (Communion under both kinds) 之決議',
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
      textKey: 'trent-19-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《天主教大公會議文獻彙編》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Waterworth 1848 English translation (public domain)',
      text: '',
      textKey: 'trent-19-english',
      source: 'https://www.papalencyclicals.net/councils/trent/',
    },
    {
      lang: 'lat',
      label: '拉丁原文 — Session 19（Documenta Catholica Omnia / Alberigo COD 1973）',
      text: '',
      textKey: 'trent-19-latin',
      source: 'Documenta Catholica Omnia, 1545-1563-,_Concilium_Tridentinum,_Canones_et_Decreta,_LT.pdf — Alberigo, Conciliorum Oecumenicorum Decreta (1973) 批判版；25 sessio 自全集 PDF 按 SESSIO {ROMAN} 標頭切分',
    },
  ],
  summaryZh: `第三期之程序性延會令。`,
  notes: `- 頒佈日期：1562-05-14
- 會期類別：第 19 會期 / Session 19 (第三期 1562-63)
- 主議題：第三期程序性延會；準備接下來第 21 會期 (Communion under both kinds) 之決議
- 中文版尚未從 vatican.va 取得（Trent 無中文官方版）；中譯需從紙本《天主教大公會議文獻彙編》取材
- 拉丁版待補（papalencyclicals.net 僅提供 Waterworth 1848 英譯；拉丁需另尋 documentacatholicaomnia.eu / Wikisource）`,
  related: [
    'trent-17',
    'trent-18',
    'trent-20',
    'trent-21',
  ],
}
