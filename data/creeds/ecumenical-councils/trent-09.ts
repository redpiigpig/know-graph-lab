import type { Creed } from '../types'

export const trent09: Creed = {
  slug: 'trent-09',
  category: 'ecumenical-council',
  councilNo: 19,
  councilDocCode: 'S09',
  councilDocOrder: 9,
  order: 1909,
  nameZh: '第 9 會期 ─ 延會令（波隆那第一）',
  nameEn: 'Session 9 — Decree of Prorogation',
  year: 1547,
  location: '北義特利騰／波隆那（特利騰大公會議第 9 會期）',
  topic: '波隆那首場會期；因會議出席率低、政治阻力大，延後實質決議；象徵會議陷入第一段停頓期',
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
      textKey: 'trent-09-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《天主教大公會議文獻彙編》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Waterworth 1848 English translation (public domain)',
      text: '',
      textKey: 'trent-09-english',
      source: 'https://www.papalencyclicals.net/councils/trent/',
    },
    {
      lang: 'lat',
      label: '拉丁原文 — Session 9（Documenta Catholica Omnia / Alberigo COD 1973）',
      text: '',
      textKey: 'trent-09-latin',
      source: 'Documenta Catholica Omnia, 1545-1563-,_Concilium_Tridentinum,_Canones_et_Decreta,_LT.pdf — Alberigo, Conciliorum Oecumenicorum Decreta (1973) 批判版；25 sessio 自全集 PDF 按 SESSIO {ROMAN} 標頭切分',
    },
  ],
  summaryZh: `波隆那期的第一會期 — 因出席教長過少（多為意大利籍）、查理五世持續抗議、教宗保祿三世與皇帝關係緊張，會議無法處理任何實質教義或紀律議題，僅頒延會令。此為大公會議近乎癱瘓的一年標誌。`,
  notes: `- 頒佈日期：1547-04-21
- 會期類別：第 9 會期 / Session 9 (第一期 1545-49)
- 主議題：波隆那首場會期；因會議出席率低、政治阻力大，延後實質決議；象徵會議陷入第一段停頓期
- 中文版尚未從 vatican.va 取得（Trent 無中文官方版）；中譯需從紙本《天主教大公會議文獻彙編》取材
- 拉丁版待補（papalencyclicals.net 僅提供 Waterworth 1848 英譯；拉丁需另尋 documentacatholicaomnia.eu / Wikisource）`,
  related: [
    'trent-07',
    'trent-08',
    'trent-10',
    'trent-11',
  ],
}
