import type { Creed } from '../types'

export const trent15: Creed = {
  slug: 'trent-15',
  category: 'ecumenical-council',
  councilNo: 19,
  councilDocCode: 'S15',
  councilDocOrder: 15,
  order: 1915,
  nameZh: '第 15 會期 ─ 延會令（保護新教代表）',
  nameEn: 'Session 15 — Decree of Prorogation + Safe-Conduct',
  year: 1552,
  location: '北義特利騰／波隆那（特利騰大公會議第 15 會期）',
  topic: '頒新教代表「平安通行證」(safe-conduct) 邀請對話；但無實質教義決議；數月後因德意志諸侯起兵會議再度暫停',
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
      textKey: 'trent-15-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《天主教大公會議文獻彙編》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Waterworth 1848 English translation (public domain)',
      text: '',
      textKey: 'trent-15-english',
      source: 'https://www.papalencyclicals.net/councils/trent/',
    },
    {
      lang: 'lat',
      label: '拉丁原文 — Session 15（Documenta Catholica Omnia / Alberigo COD 1973）',
      text: '',
      textKey: 'trent-15-latin',
      source: 'Documenta Catholica Omnia, 1545-1563-,_Concilium_Tridentinum,_Canones_et_Decreta,_LT.pdf — Alberigo, Conciliorum Oecumenicorum Decreta (1973) 批判版；25 sessio 自全集 PDF 按 SESSIO {ROMAN} 標頭切分',
    },
  ],
  summaryZh: `頒新教代表「平安通行證」(salvus conductus) 邀請彼等出席會議陳述立場，但實質對話未成。1552 年春 Maurice of Saxony 領德意志諸侯反叛、進攻 Innsbruck，皇帝查理五世倉皇撤退，會議第二度被迫無限期暫停。1555 年儒略三世去世。`,
  notes: `- 頒佈日期：1552-01-25
- 會期類別：第 15 會期 / Session 15 (第二期 1551-52)
- 主議題：頒新教代表「平安通行證」(safe-conduct) 邀請對話；但無實質教義決議；數月後因德意志諸侯起兵會議再度暫停
- 中文版尚未從 vatican.va 取得（Trent 無中文官方版）；中譯需從紙本《天主教大公會議文獻彙編》取材
- 拉丁版待補（papalencyclicals.net 僅提供 Waterworth 1848 英譯；拉丁需另尋 documentacatholicaomnia.eu / Wikisource）`,
  related: [
    'trent-13',
    'trent-14',
    'trent-16',
    'trent-17',
  ],
}
