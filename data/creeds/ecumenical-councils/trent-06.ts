import type { Creed } from '../types'

export const trent06: Creed = {
  slug: 'trent-06',
  category: 'ecumenical-council',
  councilNo: 19,
  councilDocCode: 'S06',
  councilDocOrder: 6,
  order: 1906,
  nameZh: '第 6 會期 ─ 成義令',
  nameEn: 'Session 6 — Decree on Justification + Decree on Reformation',
  year: 1547,
  location: '北義特利騰／波隆那（特利騰大公會議第 6 會期）',
  topic: '公教成義論集大成：恩寵先於、伴隨、跟隨人意；信、望、愛三德皆灌注；善功有功德 — 是天主教與信義宗最根本分歧的官方定義',
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
      textKey: 'trent-06-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《天主教大公會議文獻彙編》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Waterworth 1848 English translation (public domain)',
      text: '',
      textKey: 'trent-06-english',
      source: 'https://www.papalencyclicals.net/councils/trent/',
    },
    {
      lang: 'lat',
      label: '拉丁原文 — Session 6（Documenta Catholica Omnia / Alberigo COD 1973）',
      text: '',
      textKey: 'trent-06-latin',
      source: 'Documenta Catholica Omnia, 1545-1563-,_Concilium_Tridentinum,_Canones_et_Decreta,_LT.pdf — Alberigo, Conciliorum Oecumenicorum Decreta (1973) 批判版；25 sessio 自全集 PDF 按 SESSIO {ROMAN} 標頭切分',
    },
  ],
  summaryZh: `第六會期是特利騰最具神學深度的會期，頒《論成義令》(Decree on justification) 16 章 + 33 條 canons，正面定義天主教成義論以回應 1517 以來的改教爭議：(1) 成義是「藉聖事獲得的稱義與內在成聖」(non per solam imputationem, sed interna iustitia)，非僅外在歸算（駁路德 imputed justification）；(2) 恩寵先於人意 (gratia praeveniens)，但人需以自由意志合作 (cooperation)；(3) 信、望、愛三德於受洗時皆由聖神灌注 (infusion)；(4) 受洗後犯死罪可失成義，但可藉告解聖事 (penance) 重獲；(5) 善功在恩寵中具真實功德 (meritum)，能增加成義恩寵；(6) 凡稱「人單藉信即可獲救」者，當受逐出 (anathema sit)。此令與《奧斯堡信條》(1530) 第 4 條「因信稱義」形成 469 年神學鴻溝，直至 1999《路德－天主教合一稱義宣言》(JDDJ) 才達成「實質共識」。`,
  notes: `- 頒佈日期：1547-01-13
- 會期類別：第 6 會期 / Session 6 (第一期 1545-49)
- 主議題：公教成義論集大成：恩寵先於、伴隨、跟隨人意；信、望、愛三德皆灌注；善功有功德 — 是天主教與信義宗最根本分歧的官方定義
- 中文版尚未從 vatican.va 取得（Trent 無中文官方版）；中譯需從紙本《天主教大公會議文獻彙編》取材
- 拉丁版待補（papalencyclicals.net 僅提供 Waterworth 1848 英譯；拉丁需另尋 documentacatholicaomnia.eu / Wikisource）`,
  related: [
    'trent-04',
    'trent-05',
    'trent-07',
    'trent-08',
  ],
}
