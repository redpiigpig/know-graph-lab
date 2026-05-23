import type { Creed } from '../types'

export const trent04: Creed = {
  slug: 'trent-04',
  category: 'ecumenical-council',
  councilNo: 19,
  councilDocCode: 'S04',
  councilDocOrder: 4,
  order: 1904,
  nameZh: '第 4 會期 ─ 正典聖經與聖傳令',
  nameEn: 'Session 4 — Decree concerning the Canonical Scriptures + Decree on the Edition and Use of Sacred Books',
  year: 1546,
  location: '北義特利騰／波隆那（特利騰大公會議第 4 會期）',
  topic: '確立次經（第二正典）為正典之一；定 Vulgate 武加大為公教標準拉丁譯本；聖經與聖傳並列為啟示來源',
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
      textKey: 'trent-04-chinese',
      placeholder: true,
      source: '待補：來源候選 → 中華民國天主教主教團《天主教大公會議文獻彙編》／思高聖經學會《大公會議信條彙編》',
      translator: '待確認',
    },
    {
      lang: 'en',
      label: 'Waterworth 1848 English translation (public domain)',
      text: '',
      textKey: 'trent-04-english',
      source: 'https://www.papalencyclicals.net/councils/trent/',
    },
    {
      lang: 'lat',
      label: '拉丁原文 — Session 4（Documenta Catholica Omnia / Alberigo COD 1973）',
      text: '',
      textKey: 'trent-04-latin',
      source: 'Documenta Catholica Omnia, 1545-1563-,_Concilium_Tridentinum,_Canones_et_Decreta,_LT.pdf — Alberigo, Conciliorum Oecumenicorum Decreta (1973) 批判版；25 sessio 自全集 PDF 按 SESSIO {ROMAN} 標頭切分',
    },
  ],
  summaryZh: `第四會期是特利騰最具決定性的會期之一，頒兩份相關令：(1)《論正典聖經令》(Decree concerning the canonical Scriptures) 列舉 73 卷為正典，包括新教所拒的 7 卷「次經 / 第二正典」(Tobit, Judith, Wisdom, Sirach, Baruch, 1-2 Maccabees + Esther / Daniel 增補)，並宣告聖經與「未成文聖傳」(unwritten traditions) 並列為公教啟示之兩大來源 — 直接駁斥路德「唯獨聖經」(sola Scriptura) 原則。(2)《論聖經版本及使用令》(Decree concerning the edition and the use of the sacred books) 定耶柔米的拉丁武加大譯本 (Vulgate) 為「真實版本」(authentica)，未經教會審查不得擅自詮釋聖經、禁止印行未經許可之聖經譯本。此令確立了天主教在正典範圍、譯本權威、詮釋準則上與新教的根本分歧。`,
  notes: `- 頒佈日期：1546-04-08
- 會期類別：第 4 會期 / Session 4 (第一期 1545-49)
- 主議題：確立次經（第二正典）為正典之一；定 Vulgate 武加大為公教標準拉丁譯本；聖經與聖傳並列為啟示來源
- 中文版尚未從 vatican.va 取得（Trent 無中文官方版）；中譯需從紙本《天主教大公會議文獻彙編》取材
- 拉丁版待補（papalencyclicals.net 僅提供 Waterworth 1848 英譯；拉丁需另尋 documentacatholicaomnia.eu / Wikisource）`,
  related: [
    'trent-02',
    'trent-03',
    'trent-05',
    'trent-06',
  ],
}
