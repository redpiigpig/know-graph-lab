import type { Creed } from '../types'

export const trent11: Creed = {
  slug: 'trent-11',
  category: 'ecumenical-council',
  councilNo: 19,
  councilDocCode: 'S11',
  councilDocOrder: 11,
  order: 1911,
  nameZh: '第 11 會期 ─ 復會令',
  nameEn: 'Session 11 — Decree of Resumption',
  year: 1551,
  location: '北義特利騰／波隆那（特利騰大公會議第 11 會期）',
  topic: '儒略三世復會特利騰；新一輪會期開始 — 為第二期 (1551-52)；德意志改教派代表出席要求被討論',
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
      textKey: 'trent-11-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《天主教大公會議文獻彙編》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Waterworth 1848 English translation (public domain)',
      text: '',
      textKey: 'trent-11-english',
      source: 'https://www.papalencyclicals.net/councils/trent/',
    },
    {
      lang: 'lat',
      label: '拉丁原文 — Session 11（Documenta Catholica Omnia / Alberigo COD 1973）',
      text: '',
      textKey: 'trent-11-latin',
      source: 'Documenta Catholica Omnia, 1545-1563-,_Concilium_Tridentinum,_Canones_et_Decreta,_LT.pdf — Alberigo, Conciliorum Oecumenicorum Decreta (1973) 批判版；25 sessio 自全集 PDF 按 SESSIO {ROMAN} 標頭切分',
    },
  ],
  summaryZh: `儒略三世即位後，與皇帝查理五世和解，宣布大公會議於特利騰復會。第十一會期僅頒《復會令》宣告會議重新運作。第二期 (1551-52) 的特色是：德意志改教派代表 (新教 estates) 應皇帝邀請出席，要求重啟成義論辯，但未獲滿足。`,
  notes: `- 頒佈日期：1551-05-01
- 會期類別：第 11 會期 / Session 11 (第二期 1551-52)
- 主議題：儒略三世復會特利騰；新一輪會期開始 — 為第二期 (1551-52)；德意志改教派代表出席要求被討論
- 中文版尚未從 vatican.va 取得（Trent 無中文官方版）；中譯需從紙本《天主教大公會議文獻彙編》取材
- 拉丁版待補（papalencyclicals.net 僅提供 Waterworth 1848 英譯；拉丁需另尋 documentacatholicaomnia.eu / Wikisource）`,
  related: [
    'trent-09',
    'trent-10',
    'trent-12',
    'trent-13',
  ],
}
