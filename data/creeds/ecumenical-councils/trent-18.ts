import type { Creed } from '../types'

export const trent18: Creed = {
  slug: 'trent-18',
  category: 'ecumenical-council',
  councilNo: 19,
  councilDocCode: 'S18',
  councilDocOrder: 18,
  order: 1918,
  nameZh: '第 18 會期 ─ 禁書目錄令',
  nameEn: 'Session 18 — Decree concerning the Choice of Books + Invitation',
  year: 1562,
  location: '北義特利騰／波隆那（特利騰大公會議第 18 會期）',
  topic: '授權設立《禁書目錄》(Index Librorum Prohibitorum) 編纂委員會；邀請尚未到會之與會者參與會議',
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
      textKey: 'trent-18-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《天主教大公會議文獻彙編》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Waterworth 1848 English translation (public domain)',
      text: '',
      textKey: 'trent-18-english',
      source: 'https://www.papalencyclicals.net/councils/trent/',
    },
    {
      lang: 'lat',
      label: '拉丁原文 — Session 18（Documenta Catholica Omnia / Alberigo COD 1973）',
      text: '',
      textKey: 'trent-18-latin',
      source: 'Documenta Catholica Omnia, 1545-1563-,_Concilium_Tridentinum,_Canones_et_Decreta,_LT.pdf — Alberigo, Conciliorum Oecumenicorum Decreta (1973) 批判版；25 sessio 自全集 PDF 按 SESSIO {ROMAN} 標頭切分',
    },
  ],
  summaryZh: `頒《關於選擇書籍及邀請所有人出席會議令》：授權設立《禁書目錄》(Index Librorum Prohibitorum) 編纂委員會，該目錄於 Session 25 結束後於 1564 年正式發布、由教宗庇護四世以 Dominici gregis 訓令公佈；其延續至 1966 年才被廢止。同令並邀請尚未到會的東方與西方教長盡速赴會。`,
  notes: `- 頒佈日期：1562-02-26
- 會期類別：第 18 會期 / Session 18 (第三期 1562-63)
- 主議題：授權設立《禁書目錄》(Index Librorum Prohibitorum) 編纂委員會；邀請尚未到會之與會者參與會議
- 中文版尚未從 vatican.va 取得（Trent 無中文官方版）；中譯需從紙本《天主教大公會議文獻彙編》取材
- 拉丁版待補（papalencyclicals.net 僅提供 Waterworth 1848 英譯；拉丁需另尋 documentacatholicaomnia.eu / Wikisource）`,
  related: [
    'trent-16',
    'trent-17',
    'trent-19',
    'trent-20',
  ],
}
