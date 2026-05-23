import type { Creed } from '../types'

export const trent21: Creed = {
  slug: 'trent-21',
  category: 'ecumenical-council',
  councilNo: 19,
  councilDocCode: 'S21',
  councilDocOrder: 21,
  order: 1921,
  nameZh: '第 21 會期 ─ 二形領聖體與兒童領聖體令',
  nameEn: 'Session 21 — Decree on Communion under Both Kinds and on the Communion of Little Children + Decree on Reformation',
  year: 1562,
  location: '北義特利騰／波隆那（特利騰大公會議第 21 會期）',
  topic: '肯定「凡領一形者即領整個基督」之教義；保留聖爵 (chalice) 給平信徒之權柄歸於教會；兒童領聖體非為救恩必需',
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
      textKey: 'trent-21-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《天主教大公會議文獻彙編》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Waterworth 1848 English translation (public domain)',
      text: '',
      textKey: 'trent-21-english',
      source: 'https://www.papalencyclicals.net/councils/trent/',
    },
    {
      lang: 'lat',
      label: '拉丁原文 — Session 21（Documenta Catholica Omnia / Alberigo COD 1973）',
      text: '',
      textKey: 'trent-21-latin',
      source: 'Documenta Catholica Omnia, 1545-1563-,_Concilium_Tridentinum,_Canones_et_Decreta,_LT.pdf — Alberigo, Conciliorum Oecumenicorum Decreta (1973) 批判版；25 sessio 自全集 PDF 按 SESSIO {ROMAN} 標頭切分',
    },
  ],
  summaryZh: `第二十一會期頒《論二形領聖體及兒童領聖體令》4 章 + 4 條 canons：(1) 基督於兩形（餅與酒）任一形下皆完全臨在 — 故領一形者即領整個基督；(2) 領二形非神律必需 (non est iure divino), 教會有權柄因牧靈理由保留聖爵僅給司鐸 (此為西方拉丁禮之長期慣例)；(3) 駁 Hussite 派與後續改教派「平信徒必須領二形」之主張；(4) 兒童（未達理智年齡）領聖體非救恩必需。同會期之改革令規範神品授職、教區管理。`,
  notes: `- 頒佈日期：1562-07-16
- 會期類別：第 21 會期 / Session 21 (第三期 1562-63)
- 主議題：肯定「凡領一形者即領整個基督」之教義；保留聖爵 (chalice) 給平信徒之權柄歸於教會；兒童領聖體非為救恩必需
- 中文版尚未從 vatican.va 取得（Trent 無中文官方版）；中譯需從紙本《天主教大公會議文獻彙編》取材
- 拉丁版待補（papalencyclicals.net 僅提供 Waterworth 1848 英譯；拉丁需另尋 documentacatholicaomnia.eu / Wikisource）`,
  related: [
    'trent-19',
    'trent-20',
    'trent-22',
    'trent-23',
  ],
}
